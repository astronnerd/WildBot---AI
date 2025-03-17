# WildBot Project Documentation

## Overview

WildBot is a Gen AI-Powered Chat Tool for Research Data Scraping and Interaction on wildlife, biodiversity, and conservation topics. The project integrates:

- **Generative AI:** Uses a Hugging Face model (`google/flan-ul2`) to generate detailed, research-backed responses.
- **Data Scraping:** Fetches research papers via the Semantic Scholar API.
- **Visual Enhancements:** Retrieves relevant wildlife images using the Pixabay API.
- **Themed UI:** A React-based frontend with a custom wildlife-themed design.

---

## Architecture & Tools

### Backend

- **Language:** Python 3.x
- **Framework:** Flask
- **Key Libraries:**
  - Flask==2.2.2
  - Werkzeug==2.2.2 (or 2.2.3 as needed)
  - requests==2.28.1
- **APIs Integrated:**
  - **Hugging Face API:** For AI-generated responses.
  - **Semantic Scholar API:** For research paper data.
  - **Pixabay API:** For wildlife images.
- **Models Used**
  - **Primary Model: FLAN-UL2**
    - What It Is: FLAN-UL2 is an instruction-tuned language model by Google. It is designed to follow detailed instructions and provide nuanced, in-depth responses.
    - Why We Use It: It is capable of generating comprehensive, multi-paragraph answers with evidence-based analysis, which is essential for a professional research chatbot.
    - Limitations: FLAN-UL2 can be memory intensive. On free Hugging Face endpoints, it may encounter CUDA out-of-memory errors if resource limits are exceeded.
  - **Fallback Models: FLAN-T5-LARGE, FLAN-T5-BASE**
    - What It Is: FLAN-T5-Base is a smaller, less resource-intensive version of the FLAN family. Although it may not be as detailed as FLAN-UL2, it is more likely to run successfully under constrained resources.
    - Fallback Usage: If FLAN-UL2 fails due to memory limitations (e.g., CUDA out-of-memory), the backend falls back to using FLAN-T5-Base with adjusted generation parameters.
      
- Backend Code Explanation
  -> Framework and Setup
    * Flask: The backend is built using Flask, a lightweight Python web framework. Flask handles incoming HTTP POST requests on the /api/chat endpoint.
    * Environment Variables: API keys for Hugging Face, Pixabay, and the Semantic Scholar base URL are set via environment variables or directly in the code.
      
  -> Request Flow
    1. Receive Query: When a POST request is made to /api/chat, the JSON payload is parsed to extract the user’s query.
    2. Generate AI Response:
        * A detailed prompt is constructed that instructs the model to provide a multi-paragraph, evidence-based answer.
        * The prompt is sent to the Hugging Face Inference API.
        * Primary Call: Uses FLAN-UL2 with parameters (e.g., max_new_tokens: 250, temperature: 0.8).
        * Fallback Mechanism: If a 500 error due to CUDA out-of-memory occurs, the backend switches to FLAN-T5-Base with reduced token limits (e.g., 200 tokens) to try and generate a response.
    3. Data Scraping (Research Papers):
        * If the query contains wildlife-related keywords (e.g., "wildlife", "animals", "flora", "fauna", etc.), the backend makes a GET request to the Semantic Scholar API.
        * It requests the top 3 relevant research papers including the title, abstract, and URL.
        * The resulting papers provide scientific backing for the generated answer.
    4. Image Retrieval:
        * The backend calls the Pixabay API to search for relevant images using the query.
        * It returns up to 3 image URLs, with a fallback default image if no results are found.
    5. Response Construction: The final JSON response includes:
        * "answer": The generated AI response.
        * "research": A list of research papers (if any).
        * "images": A list of image URLs.
        * "image_url": The first image URL, typically used for display.
  
    **Data Scraping of Research Papers**
    -> Semantic Scholar Integration
      * Endpoint: The code uses the Semantic Scholar API (via https://api.semanticscholar.org/graph/v1/paper/search) to search for research papers.
      * Parameters:
          * query: The user's query.
          * limit: Set to 3 to retrieve the top three papers.
          * fields: Specifies which details to retrieve (e.g., title, abstract, URL).
      * Processing: The JSON response is parsed, and a list of research papers is constructed. Each paper in the list includes the title, abstract, and a link to the full document.
      * Usage: These research papers are included in the final response to provide users with scientific sources that back up the chatbot's answer.

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

4. **Configure API Keys:**

   - Open app.py and replace the placeholders:
     
         HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "your_huggingface_api_key_here")
         PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "your_pixabay_api_key_here")
     
   - Alternatively, set them as environment variables:
     
         export HUGGINGFACE_API_KEY=your_actual_huggingface_api_key
         export PIXABAY_API_KEY=your_actual_pixabay_api_key

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

## Running the Project

### Automated Run Script

A script (start.sh) is provided to start both the backend and frontend. Save this file at the root of your project.

#### start.sh

### How to Run

1. **Make the script executable:**

       chmod +x start.sh

2. **Run the script from the project root:**

       ./start.sh

This will launch the Flask backend (listening on port 5000) and the React app (usually on port 3000).

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
