from src.RAGs.BaseRAG import BaseRAG
from src.utils.logger import get_logger

logger = get_logger(__name__)

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import Settings
import os
from llama_index.core import PromptTemplate
# from src.utils.contextual_extractor import ChunkContextualExtractor
from src.utils.DocumentParser import PDF4LLMReader

class WildLifeRAG(BaseRAG):
    def __init__(self) -> None:
        self.folder_name = "wlidlife_research_papers"
        self.docs_folder_path = os.path.join("/app/src/docs/", self.folder_name) ## this need to be changed 
        super().__init__(self.docs_folder_path, self.folder_name)
        self.sbert_reranker = self.get_sbert_reranker(top_n=8)
        self.colbert_reranker = self.get_colbert_reranker(top_n=5)

    def ingestion_pipeline(self):
        logger.info(
            f"self.vector_store.collection_name {self.vector_store.collection_name}"
        )
        reader = SimpleDirectoryReader(
            input_dir=self.docs_folder_path, required_exts=[".pdf", ".docx"], file_extractor={".pdf": PDF4LLMReader(), }
        )
        logger.info(f"Loading data from {self.docs_folder_path}")
        docs = reader.load_data()

        pipeline = IngestionPipeline(
            name = f"{self.folder_name}_ingestion_pipeline",
            project_name="WILDLIFE_RESEARCH",
            transformations=[
                SentenceSplitter(chunk_size=350, chunk_overlap=100),
                # ChunkContextualExtractor(metadata_name="chunk_context"),
                self.embed_model
            ],
            docstore=SimpleDocumentStore(),
            vector_store=self.vector_store
        )

        if os.path.exists(self.doc_pipeline_store_path):
            logger.info("Loading existing pipeline...")
            pipeline.load(self.doc_pipeline_store_path, docstore_name=self.folder_name)

        _ = pipeline.run(documents=docs, in_place=False, num_workers=2, show_progress=True)

        pipeline.persist(self.doc_pipeline_store_path, docstore_name=self.folder_name)

    def retrive(self, query: str):
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

        rr = self.index.as_retriever(
            similarity_top_k=20,
            sparse_top_k=20,
            hybrid_top_k = 10,
            vector_store_query_mode="hybrid",
            node_postprocessors=[self.sbert_reranker, self.colbert_reranker],
            llm=self.llm,
        )

        text = ""
        for r in rr.retrieve(query):
            text += r.text + "\n===========================================\n"
        logger.debug(f"Retrieved text: {text}")

        query_engine = self.index.as_query_engine(
            # streaming=True,
            similarity_top_k=20,
            sparse_top_k=20,
            hybrid_top_k = 10,
            vector_store_query_mode="hybrid",
            node_postprocessors=[self.sbert_reranker, self.colbert_reranker],
            llm=self.llm,
        )
        global_template_4 = """You are an expert on the provided documents concerning wildlife conservation, human-wildlife interactions, and ecological research. 
        Your task is to answer the following question using only the information contained within these documents. 
        Provide a comprehensive and insightful response, drawing on specific details and explanations from the text. 
        Do not include any information that is not explicitly mentioned in the provided documents.
        Use the following context to answer the question:
        ----------------------
        {context_str}
        ----------------------

        Given the context information, answer the query: {query_str}"""
        global_template_3 = """
        Respond with only the context provided and not prior knowledge. The context might have jumbled information and some of the information might be irrelevant. Judge the context and provide the answer. 
        ----------------------
        {context_str}
        ----------------------


        Given the context information, answer the query: {query_str}
        """

        text_qa_template = PromptTemplate(global_template_4)

        query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": text_qa_template}
        )
        logger.info(f"Query: {query}")
        # return query_engine
        response = query_engine.query(query)
        logger.debug(f"Query: {query}, Response : {str(response)}")
        
        return response
    

        # Do not provide any extra information strictly other than the answer to the query, Just say Currently this is not part of my knowledge base.
        # Do not answer if what is asked is not in the context, Just say Currently this is not part of my knowledge base.
        # Always answer in polite language of the user's question.
        # Do not mentioning that you obtained the information from the context, Just Currently this is not part of my knowledge base.