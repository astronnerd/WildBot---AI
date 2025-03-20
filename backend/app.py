import requests
import os
import time
from flask import Flask, request, jsonify
import logging
from collections import Counter
import re
import json

logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

def analyze_query_type(query):
    """Analyze the query to determine its type and required information."""
    query_lower = query.lower()
    
    # Define query patterns
    patterns = {
        'latest_news': r'latest|recent|new|updates|news',
        'historical': r'history|historical|past|evolution|timeline',
        'statistics': r'statistics|numbers|data|figures|count',
        'causes_effects': r'causes|effects|impact|influence|affect',
        'solutions': r'solutions|measures|steps|actions|how to|prevent',
        'comparison': r'compare|difference|versus|vs|better',
        'definition': r'what is|define|meaning|explain|description',
        'location': r'where|location|place|area|region|habitat',
        'process': r'how does|process|mechanism|way|method',
        'status': r'status|condition|state|situation|current'
    }
    
    # Check which patterns match the query
    query_types = []
    for qtype, pattern in patterns.items():
        if re.search(pattern, query_lower):
            query_types.append(qtype)
    
    # If no specific type is detected, treat as a general query
    if not query_types:
        query_types = ['general']
    
    return query_types

def get_task_templates():
    """Define templates for different types of tasks."""
    return {
        'general': {
            "task": "general_info",
            "prompt": "Provide a comprehensive overview of '{query}' with specific relevance to India's context."
        },
        'latest_news': {
            "task": "recent_developments",
            "prompt": "Describe the most recent developments, news, and updates about '{query}' in India."
        },
        'historical': {
            "task": "historical_context",
            "prompt": "Explain the historical background and evolution of '{query}' in India."
        },
        'statistics': {
            "task": "statistics",
            "prompt": "Provide key statistics, data, and figures related to '{query}' in India."
        },
        'causes_effects': {
            "task": "impact_analysis",
            "prompt": "Analyze the causes and effects of '{query}' on India's biodiversity and environment."
        },
        'solutions': {
            "task": "solutions",
            "prompt": "Outline specific solutions and conservation measures for '{query}' in India."
        },
        'status': {
            "task": "current_status",
            "prompt": "Describe the current status and conditions related to '{query}' in India."
        },
        'summary': {
            "task": "summary",
            "prompt": "Provide a clear and concise summary of '{query}' focusing on India."
        },
        'recommendations': {
            "task": "recommendations",
            "prompt": "Suggest practical recommendations for addressing '{query}' in India."
        }
    }

def get_structured_prompt(query, context):
    """Select and return relevant prompts based on query type."""
    query_types = analyze_query_type(query)
    templates = get_task_templates()
    prompts = []
    
    # Always include summary for context
    prompts.append(templates['summary'])
    
    # Add specific prompts based on query type
    for qtype in query_types:
        if qtype in templates:
            prompts.append(templates[qtype])
    
    # Add status if not already included for latest news queries
    if 'latest_news' in query_types and 'status' not in query_types:
        prompts.append(templates['status'])
    
    # Always include recommendations for actionable insights
    if 'recommendations' not in [p['task'] for p in prompts]:
        prompts.append(templates['recommendations'])
    
    # Remove duplicates while preserving order
    seen_tasks = set()
    unique_prompts = []
    for p in prompts:
        if p['task'] not in seen_tasks:
            seen_tasks.add(p['task'])
            unique_prompts.append(p)
    
    return unique_prompts

def get_structured_response(query, context):
    responses = {}
    prompts = get_structured_prompt(query, context)
    query_types = analyze_query_type(query)
    
    logging.debug(f"Query types detected: {query_types}")
    logging.debug(f"Generated prompts: {json.dumps(prompts, indent=2)}")
    
    # Get responses for each prompt
    for prompt_info in prompts:
        task = prompt_info["task"]
        full_prompt = (
            "You are an AI assistant specializing in Indian wildlife and conservation science. "
            "Provide a focused, evidence-based response. "
            f"{prompt_info['prompt']}\n\n"
            f"Context: {context}"
        )
        logging.debug(f"Sending prompt for task '{task}':\n{full_prompt}")
        
        response = query_huggingface(full_prompt)
        responses[task] = response.strip()
        logging.debug(f"Response received for task '{task}':\n{response}")

    # Define section order based on query type
    section_orders = {
        'latest_news': ['summary', 'recent_developments', 'current_status', 'recommendations'],
        'historical': ['summary', 'historical_context', 'current_status', 'recommendations'],
        'statistics': ['summary', 'statistics', 'impact_analysis', 'recommendations'],
        'causes_effects': ['summary', 'impact_analysis', 'current_status', 'solutions', 'recommendations'],
        'solutions': ['summary', 'current_status', 'solutions', 'recommendations'],
        'definition': ['summary', 'general_info', 'current_status', 'recommendations'],
        'location': ['summary', 'general_info', 'current_status', 'recommendations'],
        'process': ['summary', 'general_info', 'current_status', 'recommendations'],
        'status': ['summary', 'current_status', 'impact_analysis', 'recommendations'],
        'general': ['summary', 'general_info', 'current_status', 'recommendations']
    }

    # Map task names to display headers
    header_map = {
        'summary': '📋 Summary',
        'general_info': '📚 Overview',
        'recent_developments': '🔄 Latest Developments',
        'historical_context': '📜 Historical Background',
        'statistics': '📊 Key Statistics',
        'impact_analysis': '🎯 Impact Analysis',
        'solutions': '💡 Solutions',
        'current_status': '📌 Current Status',
        'recommendations': '✨ Recommendations'
    }

    # Get the appropriate section order based on query type
    primary_type = query_types[0] if query_types else 'general'
    section_order = section_orders.get(primary_type, section_orders['general'])

    # Build the response sections
    formatted_sections = []
    
    # Add sections in the determined order if they exist in responses
    for task in section_order:
        if task in responses:
            header = header_map.get(task, task.replace('_', ' ').title())
            content = responses[task]
            if content:  # Only add section if there's content
                formatted_sections.append(f"{header}:\n{content}")
    
    # Add any remaining sections that weren't in the order but exist in responses
    for task, content in responses.items():
        if task not in section_order and content:
            header = header_map.get(task, task.replace('_', ' ').title())
            formatted_sections.append(f"{header}:\n{content}")
    
    # Join all sections with double line breaks
    final_response = "\n\n".join(formatted_sections)
    
    return final_response

def get_tokens(text):
    """Convert text to lowercase tokens."""
    return re.findall(r'\w+', text.lower())

def calculate_similarity(text1, text2):
    """Calculate similarity between two texts using token overlap."""
    tokens1 = set(get_tokens(text1))
    tokens2 = set(get_tokens(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    
    return len(intersection) / len(union)

def split_message_into_lines(message):
    """Split a message into lines while preserving sender information."""
    text = message['text']
    sender = message['sender']
    # Split text into lines and remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return [(sender, line) for line in lines]

def extract_relevant_context(query, chat_history, max_lines=10, similarity_threshold=0.1):
    """Extract relevant context from chat history based on line-level similarity."""
    if not chat_history:
        return ""
    
    # Extract all lines from chat history
    all_lines = []
    for msg in chat_history:
        all_lines.extend(split_message_into_lines(msg))
    
    # Calculate similarity scores for each line
    lines_with_scores = []
    for sender, line in all_lines:
        score = calculate_similarity(query, line)
        lines_with_scores.append((score, sender, line))
    
    # Sort by similarity score and filter by threshold
    lines_with_scores = x(lines_with_scores, key=lambda x: x[0], reverse=True)
    relevant_lines = [(sender, line) for score, sender, line in lines_with_scores if score > similarity_threshold][:max_lines]
    
    # Sort the selected lines by their original order
    relevant_lines.sort(
        key=lambda x: next(
            i for i, msg in enumerate(chat_history) 
            if x[1] in msg['text']
        )
    )
    
    # Format the context string with line breaks between different messages
    context_parts = []
    current_sender = None
    
    for sender, line in relevant_lines:
        if sender != current_sender:
            if context_parts:  # Add extra line break between different senders
                context_parts.append("")
            current_sender = sender
        context_parts.append(f"{sender}: {line}")
    
    return "\n".join(context_parts)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    chat_history = data.get("chatHistory", [])
    
    logging.info(f"Received chat request with query: {query}")
    logging.debug(f"Chat history length: {len(chat_history)}")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Extract relevant context from chat history
    context = extract_relevant_context(query, chat_history)
    logging.debug(f"Extracted context:\n{context}")

    # Get structured response with the relevant context
    hf_answer = get_structured_response(query, context)
    logging.debug(f"Generated response:\n{hf_answer}")

    # if is_query_relevant(query, wildlife_keywords_set):
    #     research_results = None#query_semantic_scholar(query)
    #     images = None#query_pixabay(query)
    #     first_image = None#images[0] if images else "https://cdn.pixabay.com/photo/2017/06/06/22/08/bird-2376974_1280.jpg"
    # else:
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
    
    logging.debug(f"Sending request to Hugging Face API with payload:\n{json.dumps(payload, indent=2)}")
    
    def get_response_text(result):
        """Helper function to extract text from API response"""
        if isinstance(result, list) and result:
            text = result[0].get("generated_text", "").strip()
        else:
            text = result.get("generated_text", "").strip()
        return text if text else None

    primary_model_url = "https://api-inference.huggingface.co/models/google/flan-ul2"
    for attempt in range(retries):
        response = requests.post(primary_model_url, headers=headers, json=payload)
        logging.debug(f"Response from API (attempt {attempt + 1}):\nStatus: {response.status_code}\nHeaders: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            logging.debug(f"Successful response content:\n{json.dumps(result, indent=2)}")
            
            # Try to get response text
            text = get_response_text(result)
            if text:
                return text
            
            # If response is empty, log and retry once
            if attempt < retries - 1:
                logging.warning("Received empty response from API. Retrying...")
                time.sleep(delay)
                continue
            else:
                return f"No answer generated for task. Please try rephrasing your question."
                
        elif response.status_code == 503:
            logging.warning(f"Primary model (FLAN-UL2) returned 503. Retrying in {delay} seconds...")
            time.sleep(delay)
        elif response.status_code == 500 and "CUDA out of memory" in response.text:
            logging.warning("CUDA out of memory error encountered. Falling back to FLAN-T5-Large...")
            fallback_model_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            fallback_response = requests.post(fallback_model_url, headers=headers, json=payload)
            
            if fallback_response.status_code == 200:
                result = fallback_response.json()
                logging.debug(f"Successful response content from fallback model:\n{json.dumps(result, indent=2)}")
                
                # Try to get response text from fallback
                text = get_response_text(result)
                if text:
                    return text
                    
                # If fallback response is empty, try second fallback
                logging.warning("Received empty response from fallback model. Trying second fallback...")
            
            logging.error(f"Fallback model (FLAN-T5-Large) error: {fallback_response.status_code} {fallback_response.text}")
            logging.info("Falling back further to FLAN-T5-Base...")
            second_fallback_model_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
            second_fallback_response = requests.post(second_fallback_model_url, headers=headers, json=payload)
            
            if second_fallback_response.status_code == 200:
                result = second_fallback_response.json()
                logging.debug(f"Successful response content from second fallback model:\n{json.dumps(result, indent=2)}")
                
                # Try to get response text from second fallback
                text = get_response_text(result)
                if text:
                    return text
                return f"No answer generated for task. Please try rephrasing your question."
            else:
                logging.error(f"Second fallback model (FLAN-T5-Base) error: {second_fallback_response.status_code} {second_fallback_response.text}")
        else:
            logging.error(f"Hugging Face API Error: {response.status_code} {response.text}")
            
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
            logging.error(f"Semantic Scholar API response missing 'data' key. Full response: {data}")
        papers = []
        for paper in data.get("data", []):
            papers.append({
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "url": paper.get("url")
            })
        return papers
    else:
        logging.error(f"Semantic Scholar API Error: {response.status_code} {response.text}")
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
        logging.error(f"Error parsing JSON from Pixabay response: {response.text}")
        data = {}
    if response.status_code == 200 and data:
        hits = data.get("hits", [])
        if hits:
            image_urls = [hit.get("webformatURL") for hit in hits if hit.get("webformatURL")]
            return image_urls
    return ["https://cdn.pixabay.com/photo/2017/06/06/22/08/bird-2376974_1280.jpg"]

if __name__ == '__main__':
    app.run(debug=True)