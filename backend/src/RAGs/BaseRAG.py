from abc import abstractmethod
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from llama_index.llms.ollama import Ollama
from llama_index.core.postprocessor import SentenceTransformerRerank
# from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.postprocessor.colbert_rerank import ColbertRerank
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker

## this need to be updated
from src.utils.logger import get_logger
logger = get_logger(__name__)


class BaseRAG:
    def __init__(self, docs_folder_path, folder_name) -> None:
        self.docs_folder_path = docs_folder_path
        self.folder_name = folder_name
        self.doc_pipeline_store_path = "/app/data/pipeline_storage"

        self.embed_model = self.get_embedding_model()
        self.llm = self.get_llm()
        self.vector_store = self.get_vector_store()
        # self.ingestion_pipeline()  # to be run once to populate the data in qdrant
        self.index = self.get_v_index()
        # self.reranker = self.get_sbert_reranker()

        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

    def get_embedding_model(self, model_name="BAAI/bge-small-en-v1.5"):
        # embed_model = FastEmbedEmbedding(
        #     model_name=model_name, cache_dir="./data/fastembeded/"
        # )
        embed_model = OllamaEmbedding(
            model_name="bge-large:latest",
            base_url="http://host.docker.internal:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )
        return embed_model

    def get_llm(
        self,
        model="gemma3:4b-it-q8_0",
        request_timeout=3000,
        temperature=0.0,
        stream=False,
    ):
        llm = Ollama(
            base_url="http://host.docker.internal:11434",
            model=model,
            request_timeout=request_timeout,
            temperature=temperature,
            additional_kwargs={"seed": 42, "num_ctx": 32768},
            stream=stream,
        )
        return llm

    def get_sbert_reranker(
        self,
        name="cross-encoder/ms-marco-MiniLM-L-2-v2",
        top_n=5,
        keep_retrieval_score=True,
    ):
        sbert_rerank = SentenceTransformerRerank(
            model=name,
            top_n=top_n,
            keep_retrieval_score=keep_retrieval_score,
        )
        return sbert_rerank
    
    def get_colbert_reranker(
        self,
        top_n=5,
        keep_retrieval_score=True,
    ):
        colbert_reranker = ColbertRerank(
            top_n=top_n,
            model="colbert-ir/colbertv2.0",
            tokenizer="colbert-ir/colbertv2.0",
            keep_retrieval_score=keep_retrieval_score,
        )
        return colbert_reranker
    
    def get_flag_reranker(
        self,
        top_n=5,
    ):
        flag_reranker = FlagEmbeddingReranker(model="BAAI/bge-reranker-large", top_n=top_n, use_fp16=True)

        return flag_reranker

    @abstractmethod
    def ingestion_pipeline(self):
        pass

    def get_vector_store(self):
        client = QdrantClient(host="qdrant", port=6333)
        # aclient = AsyncQdrantClient(host="qdrant", port=6333)

        # create our vector store with hybrid indexing enabled
        # batch_size controls how many nodes are encoded with sparse vectors at once
        vector_store = QdrantVectorStore(
            self.folder_name,
            client=client,
            enable_hybrid=True,
            batch_size=4,
        )
        return vector_store

    def get_v_index(self):
        index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embed_model,
        )
        return index

    @abstractmethod
    def retrieve(self, query: str):
        pass
