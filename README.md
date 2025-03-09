# WildBot Project Documentation

## Overview

WildBot is a Gen AI-Powered Chat Tool for Research Data Scraping and Interaction on wildlife, biodiversity, and conservation topics. The project integrates:

- **Generative AI:** Uses a Hugging Face model (e.g., `google/flan-t5-xl`) to generate detailed, research-backed responses.
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
│   └── wildbot-frontend/
│       ├── public/
│       │   └── index.html
│       ├── src/
│       │   ├── App.js
│       │   ├── App.css
│       │   └── index.js
│       └── package.json
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

1. **Navigate to the `frontend/wildbot-frontend` folder.**

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

       #!/bin/bash

       # Start Flask backend
       echo "Starting Flask backend..."
       cd backend
       source venv/bin/activate
       python3 app.py &
       BACKEND_PID=$!
       echo "Flask backend started with PID $BACKEND_PID"
       cd ..

       # Start React frontend
       echo "Starting React frontend..."
       cd frontend/wildbot-frontend
       npm start

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
2. Connect your GitHub repository and select the wildbot-frontend project.
3. For Vercel:
   - The default settings work for Create React App (build command: npm run build, output directory: build).
4. For Netlify:
   - Set the Build Command to npm run build and Publish Directory to build.
5. Deploy the frontend.

> **Note:** After deploying, update your React app’s API endpoint (if needed) to point to the deployed backend URL.

---

## Next Steps & Debugging

### Debugging the Model Response Error

- **Check Logs:**  
  In your Flask backend, add print statements in the query_huggingface function to output the status code and response text.
- **Model Warm-Up:**  
  Note that Hugging Face models might take a moment to load on the first call. Consider adding a retry mechanism if needed.
- **Alternative Models:**  
  Test with another model if the current one continues to produce errors.

### UI Enhancements

- **Background & Overlay:**  
  The CSS in index.css or App.css sets a full-page wildlife background. Adjust the URL and styling to suit your theme.
- **Interactive Elements:**  
  Consider using icon libraries (e.g., Font Awesome) and animations (CSS transitions, keyframes, or the AOS library) to further enrich the experience.
- **Custom Components:**  
  Create a header with a wildlife logo or additional cards for research papers to improve layout and interactivity.

---

This documentation provides a comprehensive overview of WildBot, including setup instructions, an automation script, and deployment guidance using free services. Once these steps are in place, you can revisit debugging the Hugging Face model response error if needed.

Happy coding and best of luck with your hackathon demo!
