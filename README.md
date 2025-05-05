# Investment Planner using Google Gemini & Streamlit

This is an AI-powered Investment Planner built using **Google Gemini** (Generative AI API) and **Streamlit** for the UI. It helps users build a customized investment plan based on their financial goals, risk tolerance, income, and investment horizon.


## Features

- Personalized investment plans based on user input
- Secure API key input (supports `.streamlit/secrets.toml` or manual entry)
- Uses Gemini (`gemini-pro` or `gemini-1.5-pro`) for generating financial advice
- Stylish and responsive dark UI
- Investment allocation, important considerations, and disclaimers
- Safe error handling for API, JSON parsing, and model selection


## Technologies Used

- [Streamlit](https://streamlit.io/) - for the frontend
- [Google Generative AI API](https://ai.google.dev/) - for generating investment advice
- [Python 3.8+](https://www.python.org/)
- HTML/CSS for custom styling inside Streamlit


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Freya135/AI-investment-Assistant.git
```
### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Add Your Google API Key
You have two options:

Option A: Add to secrets.toml (recommended) <br>
Create a file .streamlit/secrets.toml with:

```toml
GOOGLE_API_KEY = "your_google_api_key"
```
Option B: Enter it manually in the app when prompted.

Running the App
```bash
streamlit run investment_planner.py
```
Then open http://localhost:8501 in your browser.

### How It Works
- You enter your financial details (goal, income, debt, risk appetite, etc.)
- The app formats this into a structured prompt.
- The Gemini API generates a JSON-formatted investment plan.
- The app parses the JSON and displays it beautifully using Streamlit components.

Example Output
```json
{
  "Understanding Your Situation": "...",
  "Investment Options & Potential Allocation": "...",
  "Important Considerations": "...",
  "Disclaimer": "I'm an AI chatbot, not a financial advisor..."
}
```
## Disclaimer
This tool is intended for educational purposes only. It does not replace professional financial advice. Always consult a certified financial planner for real investment decision
