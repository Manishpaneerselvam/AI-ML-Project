# AI/ML-Project
Live AI Football Commentator

An AI-powered football commentary generator that produces real-time match commentary using live football data and a Large Language Model (LLaMA 3.2).

This project integrates:
  API-Football (Live Match Data)
  LLaMA 3.2 via Ollama (AI Commentary Generation)
  Streamlit (Web Interface)

Features:
  Fetches live football matches
  Displays real-time score and match minute
  Generates AI-based live commentary for match events
  Avoids duplicate commentary using event tracking
  Clean and interactive web interface
  
Tech Stack:
  Python
  Streamlit
  REST API (API-Football)
  Ollama
  LLaMA 3.2
  Requests

Installation & Setup:
1.Clone the Repository:
  git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2.Install Required Libraries:
  pip install streamlit requests ollama

3.Install and Start Ollama:
  ollama server
  
4.Pull the LLaMA 3.2 model:
  ollama pull llama3.2

5.Add Your API Key:
  Inside the Python file, replace:
  API_KEY = "YOUR_API_KEY"

6.Run the Application:
  streamlit run live_commentary_app.py
