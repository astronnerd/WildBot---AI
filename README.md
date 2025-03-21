# WildBot Project Documentation

## Overview

WildBot is a Gen AI-Powered Chat Tool for Research Data Scraping and Interaction on wildlife, biodiversity, and conservation topics. The project integrates:

- **Generative AI:** Uses a BGE-Large and Gemma3-IT to generate detailed, research-backed responses.
- **Themed UI:** A React-based frontend with a custom wildlife-themed design.

---

## Architecture & Tools

### Backend

- **Language:** Python 3.x
- **Framework:** FastAPI
- **Key Libraries:**
  - FastAPI==2.2.2
  - Werkzeug==2.2.2 (or 2.2.3 as needed)
  - requests==2.28.1
  - Pytorch
  
- **Models Used**
  - **BGE-Large**
    - The BGE-Large model is a powerful embedding model designed for semantic understanding of text.
    - It converts sentences into high-dimensional vectors that capture their meaning, enabling advanced applications like semantic search, question answering, and document retrieval.
    - Unlike traditional keyword-based methods, BGE-Large retrieves results based on contextual similarity, making it ideal for building intelligent search systems, chatbots, and recommendation engines.
  - **Gemma3-IT**
    - Gemma-3B-IT is an instruction-tuned language model developed by Google, designed to follow human instructions and generate helpful, context-aware responses
    - With 3 billion parameters, it balances performance and efficiency, making it ideal for tasks like conversational AI, code generation, summarization, and question answering. 
    - Fine-tuned for alignment with user intent, Gemma-3B-IT excels in real-world applications where understanding and following instructions is key.
      
- Backend Code Explanation      
  -> Request Flow
    1. Receive Query: When a POST request is made to /api/chat, the JSON payload is parsed to extract the user’s query.
    2. Generate AI Response:
        * A detailed prompt is constructed that instructs the model to provide a multi-paragraph, evidence-based answer.
        * The prompt is sent to the Gemma3-IT.
    3. Data Scraping (Research Papers):
        * If the query contains wildlife-related keywords (e.g., "wildlife", "animals", "flora", "fauna", etc.), the backend makes a GET request to the Semantic Scholar API.
        * It requests the top 3 relevant research papers including the title, abstract, and URL.
        * The resulting papers provide scientific backing for the generated answer.
    4. Response Construction: The final JSON response includes:
        * "answer": The generated AI response.
        * "research": A list of research papers (if any).
        * "images": A list of image URLs.
        * "image_url": The first image URL, typically used for display.

### Frontend
- **Framework:** React (via Create React App)
- **Styling:** Custom CSS (using App.css) with a full-page wildlife background, semi-transparent overlay, and interactive elements.
- **Key Dependencies:** react, react-dom, react-scripts
- **Proxy Setup:** Configured in package.json to route API calls to the Flask backend.

### Development Tools
- **IDE:** Visual Studio Code (or any preferred editor)
- **Node.js & npm:** For managing the React project
- **Python Virtual Environment:** For isolating backend dependencies

---

## Project Structure

WildBot/
├── backend/
|   ├──src/
│   ├── app.py
│   ├── requirements.txt
│   └── venv/           # Python virtual environment folder
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
└── start.sh            # Automation script to run backend and frontend

---

## Setup Instructions

### 1. Backend Setup

1. **Navigate to the `backend` folder.**

2. **Create and Activate the Virtual Environment:**

   Run:
   
       python3 -m venv venv
       source venv/bin/activate

3. **Install Dependencies:**

       pip install -r requirements.txt
       Install Ollama

       Run:

           - ollama pull gemma3:4b-it-q8_0
           - ollama pull bge-large:latest
          

4. **Deploy LLM:**
   - In the root folder:

      Run:

         docker compose up --build


### 2. Frontend Setup

1. **Navigate to the frontend` folder.**

2. **Install Dependencies:**

       npm install

3. **Verify package.json:**

   Ensure it includes a "proxy": "http://localhost:5000" key and a "browserslist" configuration similar to:

       "browserslist": {
         "production": [
           ">0.2%",
           "not dead",
           "not op_mini all"
         ],
         "development": [
           "last 1 chrome version",
           "last 1 firefox version",
           "last 1 safari version"
         ]
       }

---

## Deployment Instructions

### Deploying the Backend (Flask)

**Option: Render (Free Tier)**
1. Sign up at https://render.com/.
2. Create a new Web Service and link your GitHub repository.
3. Set the Build Command to:
       
       pip install -r requirements.txt
4. Set the Start Command to:
       
       python3 app.py
5. In the Render dashboard, add environment variables:
   - HUGGINGFACE_API_KEY
   - PIXABAY_API_KEY
6. Deploy the service.

### Deploying the Frontend (React)

**Option: Vercel or Netlify (Free Tier)**
1. Sign up at https://vercel.com/ or https://www.netlify.com/.
2. Connect your GitHub repository and select the frontend project.
3. For Vercel:
   - The default settings work for Create React App (build command: npm run build, output directory: build).
4. For Netlify:
   - Set the Build Command to npm run build and Publish Directory to build.
5. Deploy the frontend.

> **Note:** After deploying, update your React app’s API endpoint (if needed) to point to the deployed backend URL.

---
