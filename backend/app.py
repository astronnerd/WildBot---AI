import requests
import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your API keys here or via environment variables
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "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")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "49250214-ddbd8555d4f9b7ad81a28b8b0")
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Wildlife-related keywords as a Python set for fast lookup.
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

def is_query_relevant(query, keywords_set):
    """Return True if any keyword (or its singular form) from the set appears in the query."""
    query_lower = query.lower()
    for keyword in keywords_set:
        if keyword in query_lower:
            return True
        if keyword.endswith('s') and keyword[:-1] in query_lower:
            return True
    return False

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    chat_history = data.get("chatHistory", [])
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Combine chat history into a single context string
    context = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history])

    prompt = (
        "You are an AI assistant trained in advanced scientific research, specializing in wildlife, biodiversity, and conservation science in India. "
        "Your task is to provide well-structured, evidence-based, and scientifically rigorous answers focused specifically on India's ecological and environmental landscape. "
        "Your response must include:\n"
        "1. A clear and concise summary of the topic with relevance to India.\n"
        "2. Detailed explanations supported by scientific studies, government policies, or conservation initiatives in India.\n"
        "3. A discussion of historical trends, current developments, and future challenges specific to India’s biodiversity and ecosystems.\n"
        "4. Citations of reputable sources, such as research from the Wildlife Institute of India (WII), National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change (MoEFCC), and peer-reviewed journals.\n"
        "5. Actionable recommendations aligned with India's legal frameworks, conservation programs, and global commitments like the Paris Agreement and CBD.\n\n"
        "Avoid vague statements or unsupported claims. If uncertainty exists, clarify the limitations of available data.\n"
        "Ensure the response is written in a formal, scientific tone, yet remains accessible to an educated audience.\n\n"
        "Context (chat history):\n" + context + "\n\n"
        "Query: \"" + query + "\""
    )
    hf_answer = query_huggingface(prompt)

    if is_query_relevant(query, wildlife_keywords_set):
        research_results = query_semantic_scholar(query)
        images = query_pixabay(query)
        first_image = images[0] if images else "https://cdn.pixabay.com/photo/2017/06/06/22/08/bird-2376974_1280.jpg"
    else:
        research_results = None
        images = None
        first_image = None

    result = {
        "answer": hf_answer,
        "research": research_results,
        "images": images,
        "image_url": first_image
    }
    return jsonify(result)

def query_huggingface(prompt, retries=3, delay=5):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "do_sample": True,
            "temperature": 0.8
        }
    }
    primary_model_url = "https://api-inference.huggingface.co/models/google/flan-ul2"
    for attempt in range(retries):
        response = requests.post(primary_model_url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "No answer generated.")
            return result.get("generated_text", "No answer generated.")
        elif response.status_code == 503:
            print("Primary model (FLAN-UL2) returned 503. Retrying in", delay, "seconds...")
            time.sleep(delay)
        elif response.status_code == 500 and "CUDA out of memory" in response.text:
            print("CUDA out of memory error encountered. Falling back to FLAN-T5-Large...")
            fallback_model_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            fallback_response = requests.post(fallback_model_url, headers=headers, json=payload)
            if fallback_response.status_code == 200:
                result = fallback_response.json()
                if isinstance(result, list) and result:
                    return result[0].get("generated_text", "No answer generated.")
                return result.get("generated_text", "No answer generated.")
            else:
                print("Fallback model (FLAN-T5-Large) error:", fallback_response.status_code, fallback_response.text)
                print("Falling back further to FLAN-T5-Base...")
                second_fallback_model_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
                second_fallback_response = requests.post(second_fallback_model_url, headers=headers, json=payload)
                if second_fallback_response.status_code == 200:
                    result = second_fallback_response.json()
                    if isinstance(result, list) and result:
                        return result[0].get("generated_text", "No answer generated.")
                    return result.get("generated_text", "No answer generated.")
                else:
                    print("Second fallback model (FLAN-T5-Base) error:", second_fallback_response.status_code, second_fallback_response.text)
                    break
        else:
            print("Hugging Face API Error:", response.status_code, response.text)
            break
    return "Error generating response from AI model."

def query_semantic_scholar(query):
    params = {
        "query": query,
        "limit": 3,
        "fields": "title,abstract,url"
    }
    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "data" not in data:
            print("Semantic Scholar API response missing 'data' key. Full response:", data)
        papers = []
        for paper in data.get("data", []):
            papers.append({
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "url": paper.get("url")
            })
        return papers
    else:
        print("Semantic Scholar API Error:", response.status_code, response.text)
        return []

def query_pixabay(query):
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "per_page": 3
    }
    url = "https://pixabay.com/api/"
    response = requests.get(url, params=params)
    try:
        data = response.json()
    except ValueError:
        print("Error parsing JSON from Pixabay response:", response.text)
        data = {}
    if response.status_code == 200 and data:
        hits = data.get("hits", [])
        if hits:
            image_urls = [hit.get("webformatURL") for hit in hits if hit.get("webformatURL")]
            return image_urls
    return ["https://cdn.pixabay.com/photo/2017/06/06/22/08/bird-2376974_1280.jpg"]

if __name__ == '__main__':
    app.run(debug=True)