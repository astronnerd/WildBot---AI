from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.RAGs.WildLifeRAG import WildLifeRAG
from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

wildlife_rag = WildLifeRAG()

tracer_provider = register(
  project_name="WILDLIFE_RESEARCH",
  endpoint="http://phoenix:6006/v1/traces",
)


LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

@app.get("/")
def root():
    return {"STATUS": "RAG IS WORKING"}

@app.post("/ask_wildlife/")
def read_item(query: str):
    response = wildlife_rag.retrive(query)
    return {"result": str(response)}


wildlife_keywords_set = {
    "wildlife", "biodiversity", "conservation", "bird", "climate", "change", "endangered", "animals",
    "trees", "rain", "flora", "fauna", "ecosystem", "habitat", "nature", "forest", "jungle",
    "savanna", "marine", "ocean", "reptile", "mammal", "amphibian", "earth", "india", "globe",
    "species", "extinct", "environment", "protection", "sustainability", "ecology", "pollution",
    "deforestation", "global", "warming", "temperature", "development", "laws",
    "research", "studies", "analysis", "trends", "challenges", "prospects", "solutions", "NGO",
    "government", "policy", "institutions", "carbon", "footprint", "impact", "human",
    "population", "hunting", "poaching", "fishing", "agriculture", "urbanization", "waste",
    "plastic", "recycling", "renewable", "energy", "services", "air", "soil", "preservation", "restoration",
    "migration"
}

@app.post('/api/chat')
def chat(data: dict):
    query = data.get("query", "")
    

    if not query:
        return {"error": "No query provided"}, 400
    
    # Extract relevant context from chat history
    # context = extract_relevant_context(query, chat_history)

    # Get structured response with the relevant context
    # hf_answer = get_structured_response(query, context)
    hf_answer = wildlife_rag.retrive(query)
    research_results = None
    images = None
    first_image = None

    result = {
        "answer": str(hf_answer),
        "research": research_results,
        "images": images,
        "image_url": first_image
    }
    return result