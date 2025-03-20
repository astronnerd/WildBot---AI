from typing import Any, Callable, Dict, List, Optional, Sequence, cast

from llama_index.core.async_utils import DEFAULT_NUM_WORKERS, run_jobs
from llama_index.core.bridge.pydantic import (
    Field,
    PrivateAttr,
    SerializeAsAny,
)
from llama_index.core.extractors.interface import BaseExtractor
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.settings import Settings
from llama_index.core.types import BasePydanticProgram
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama

llm = Ollama(base_url="http://host.docker.internal:11434", model="gemma3:4b-it-q8_0", 
             request_timeout=3000.0, 
             temperature=0.0,
             additional_kwargs={"seed": 42, "num_ctx": 32768})
Settings.llm = llm

from llama_index.embeddings.ollama import OllamaEmbedding

ollama_embedding = OllamaEmbedding(
    model_name="bge-large:latest",
    base_url="http://host.docker.internal:11434",
    ollama_additional_kwargs={"mirostat": 0},
)
Settings.embed_model = ollama_embedding

DEFAULT_KEYWORD_EXTRACT_TEMPLATE = """\
<document> 
{document} 
</document>
Here is the chunk we want to situate within the whole document: 
<chunk> 
{chunk_text} 
</chunk> 
Please give a short succinct context to situate this chunk within 
the overall document for the purposes of improving search retrieval of the chunk. 
Answer only with the succinct context and nothing else."""

class ChunkContextualExtractor(BaseExtractor):
    """
    ChunkContextualExtractor is a class that extracts contextual information for chunks of text within a document using a language model (LLM).
    Attributes:
        llm (SerializeAsAny[LLM]): The language model to use for generation.
        metadata_name (str): Name of the metadata context. Default is "node_context".
    Methods:
        __init__(llm: Optional[LLM] = None or Settings.llm, metadata_name: Optional[str] = None, num_workers: int = DEFAULT_NUM_WORKERS, **kwargs: Any) -> None:
            Initializes the ChunkContextualExtractor with the given parameters.
        class_name(cls) -> str:
            Returns the class name "PageLevelContextExtractor".
        aextract(nodes: Sequence[BaseNode]) -> List[Dict]:
            Asynchronously extracts contextual information for the given nodes.
        separate_nodes_by_parent_ref_doc_id(nodes: Sequence[BaseNode]) -> Dict:
            Separates nodes by their parent reference document ID.
        combined_text_by_parent_ref_doc_id(nodes: Sequence[BaseNode]) -> Dict:
            Combines text of nodes by their parent reference document ID.
        extract_page_level_context(combined_texts: Dict, nodes_by_parent_ref_doc_id: Sequence[BaseNode]) -> List:
            Asynchronously extracts page-level context for the combined texts and nodes.
        get_node_level_contexts(combined_text: str, nodes: List[BaseNode]) -> List[str]:
            Asynchronously gets node-level contexts for the given combined text and nodes.
    """

    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    metadata_name: str = Field(description="Name of metadata of context", default="node_context")
    def __init__(
        self,
        llm: Optional[LLM] = None or Settings.llm,
        metadata_name: Optional[str] = None,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:


        super().__init__(
            llm= llm,
            num_workers=num_workers,
            **kwargs,
        )
        self.metadata_name = metadata_name
        self.llm = llm

    @classmethod
    def class_name(cls) -> str:
        return "PageLevelContextExtractor"

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        combined_texts = self.combined_text_by_parent_ref_doc_id(nodes)
        separate_nodes = self.separate_nodes_by_parent_ref_doc_id(nodes)
        llm_responses = await self.extract_page_level_context(combined_texts, separate_nodes)
        # add to check if returned response in correct order of the nodes.
        return [{self.metadata_name: llm_response.message.content} for llm_response in llm_responses]
    
    def separate_nodes_by_parent_ref_doc_id(self, nodes: Sequence[BaseNode]) -> Dict:
        separated_items: Dict[Optional[str], List[BaseNode]] = {}

        for node in nodes:
            key = node.metadata["parent_ref_doc_id"]
            if key not in separated_items:
                separated_items[key] = []
            separated_items[key].append(node)

        return separated_items
    
    def combined_text_by_parent_ref_doc_id(self, nodes: Sequence[BaseNode]) -> Dict:
        combined_texts: Dict[Optional[str], str] = {}

        for node in nodes:
            key = node.metadata["parent_ref_doc_id"]
            if key not in combined_texts:
                combined_texts[key] = ""
            combined_texts[key] += node.text                

        return combined_texts
# seperate page level node by parent doc id
    async def extract_page_level_context(self, combined_texts: Dict, nodes_by_parent_ref_doc_id: Sequence[BaseNode]) -> List:
        llm_responses = []
        for key, combined_text in combined_texts.items():
            llm_responses.extend(await self.get_node_level_contexts(combined_text, nodes_by_parent_ref_doc_id[key]))
        return llm_responses

    async def get_node_level_contexts(self, combined_text: str, nodes: List[BaseNode]) -> List[str]:
        contextualization_jobs = [
            self.llm.achat([
            ChatMessage(role="user", 
                        content=f"""<document> 
                        {combined_text} 
                    </document> """),

            ChatMessage(role="user", 
                        content=f"""
                    Here is the chunk we want to situate within the whole document: 
                    <chunk> 
                        {node.text} 
                    </chunk> 
                    Please give a short succinct context to situate this chunk within 
                    the overall document for the purposes of improving search retrieval of the chunk. 
                    Answer only with the succinct context and nothing else.
                    """),
            ]
            )
            for node in nodes
        ]
        return await run_jobs(
            contextualization_jobs, show_progress=self.show_progress, workers=self.num_workers
        )

