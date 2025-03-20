from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.RAGs.WildLifeRAG import WildLifeRAG



wildlife_rag = WildLifeRAG()


from phoenix.otel import register

tracer_provider = register(
  project_name="WILDLIFE_RESEARCH",
  endpoint="http://phoenix:6006/v1/traces",
)
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

@app.get("/")
def root():
    return {"STATUS": "RAG IS WORKING"}

@app.post("/ask_wildlife/")
def read_item(query: str):
    response = wildlife_rag.retrive(query)
    return {"result": str(response)}