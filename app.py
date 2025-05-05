import json
import streamlit as st 
import google.generativeai as genai
import os
import time

st.set_page_config(
    page_title="Investment Planner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    :root {
        --bg-color: #0e1117;
        --text-color: #f8f8f8;
        --blue-accent: #4dabf7;
        --blue-hover: #1e90ff;
        --card-bg: #1e2130;
        --input-bg: #1a1d2a;
        --red-accent: #ff6b6b;
        --red-hover: #fa5252;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    .main-title {
        font-family: 'Helvetica Neue', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        text-align: center !important;
        background: linear-gradient(90deg, var(--blue-accent), var(--red-accent), var(--blue-accent));
        background-size: 200% auto;
        color: transparent !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        animation: shine 6s linear infinite;
        margin-bottom: 2rem !important;
        padding: 1rem 0 !important;
        text-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
    }

    @keyframes shine {
        to {
            background-position: 200% center;
        }
    }

    h1, label, .stTextInput label, .stSelectbox label, .stSlider label {
        color: var(--text-color) !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: var(--input-bg) !important;
        border: 1px solid rgba(77, 171, 247, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        color: white !important;
    }

    .stButton > button {
        background: linear-gradient(45deg, var(--blue-accent), var(--red-accent)) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 25px !important;
        padding: 0.6rem 2.5rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button:hover {
        box-shadow: 0 7px 20px rgba(59, 130, 246, 0.4) !important;
    }

    .results-container {
        background-color: var(--card-bg);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid rgba(77, 171, 247, 0.2);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3), 0 0 20px rgba(77, 171, 247, 0.1);
        color: var(--text-color);
    }

    .results-header {
        color: var(--blue-accent) !important;
        font-size: 1.4rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.7rem;
        margin-bottom: 1.2rem;
    }

    .disclaimer {
        background-color: rgba(77, 171, 247, 0.1);
        border-left: 3px solid var(--red-accent);
        padding: 1.2rem;
        margin-top: 1.5rem;
        font-style: italic;
        border-radius: 6px;
    }
            /* Hide Streamlit's default white main block */
        .stApp {
            background-color: #000000;
        }

        /* Remove white box backgrounds from widgets */
        .stTextInput > div > div,
        .stSelectbox > div > div,
        .stSlider > div,
        .stNumberInput > div,
        .stDownloadButton,
        .stButton > button,
        .stTextArea > div,
        .stDataFrame,
        .stMarkdown,
        .stContainer,
        .block-container {
            background-color: transparent !important;
            color: white !important;
        }

        /* General text color */
        html, body, [class*="css"] {
            color: white !important;
            background-color: #000000 !important;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #111111 !important;
        }

        /* Button hover effect */
        button:hover {
            background-color: #333333 !important;
        }

        /* Remove shadows */
        .stButton > button,
        .stDownloadButton > button {
            box-shadow: none !important;
        }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <h1 class="main-title">INVESTMENT PLANNER</h1>
    """, unsafe_allow_html=True)

if 'init_timestamp' not in st.session_state:
    st.session_state.init_timestamp = int(time.time())

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    
    if not GOOGLE_API_KEY:
        with st.container():
            
            GOOGLE_API_KEY = st.text_input("Enter your Google API Key:", type="password")
            st.markdown('</div>', unsafe_allow_html=True)
            if not GOOGLE_API_KEY:
                st.warning("Please enter a Google API Key to continue.")
                st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

try:
    available_models = [model.name.split('/')[-1] for model in genai.list_models()]
    with st.sidebar:
        st.write("Available models:", available_models)
    
    if 'gemini-1.5-pro' in available_models:
        model_name = 'gemini-1.5-pro'  
    elif 'gemini-pro' in available_models:
        model_name = 'gemini-pro'
    elif available_models:
        model_name = available_models[0]
    else:
        st.error("No models available. Please check your API key.")
        st.stop()
        
    model = genai.GenerativeModel(model_name)
    with st.sidebar:
        st.success(f"Using model: {model_name}")
    
except Exception as e:
    with st.sidebar:
        st.error(f"Error listing models: {str(e)}")
    model_name = 'gemini-1.5-pro'  
    model = genai.GenerativeModel(model_name)
    with st.sidebar:
        st.info(f"Attempting to use model: {model_name}")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        goal = st.selectbox('What is your primary financial goal? ', 
                           ('Saving for retirement', 'Building an emergency fund', 'Buying a house', 
                            'Paying for a child\'s education', 'Taking a dream vacation'))
        
        income = st.number_input('What is your current income? (in Rupees) ', 
                                min_value=0, 
                                value=40000,
                                step=5000)
        
    with col2:
        time = st.selectbox('What is your investment time horizon? ', 
                           ('Short-term (Less than 5 years)', 'Medium-term (5-10 years)', 'Long-term (10+ years)'))
        
        debt = st.selectbox('Do you have any existing debt? ', 
                           ('Yes', 'No'))

    invest = st.number_input('How much investable money do you have available? (in Rupees) ', 
                            min_value=0, 
                            step=1000)

    st.write("On a scale of 1-10, where 1 is very conservative and 10 is highly aggressive:")
    scale = st.slider("How comfortable are you with risk? ", 
                     min_value=1, 
                     max_value=10, 
                     value=5,
                     step=1)

user_data = f"""
- Primary financial goal is {goal}
- My current income level is {income} Rupees
- My investment time horizon is {time}
- My debt status is {debt}
- Investable money available is {invest} Rupees
- Risk comfort level is {scale} out of 10
"""

output_format = """
{
    "Understanding Your Situation": "A concise assessment of the user's financial situation, goals, and constraints",
    "Investment Options & Potential Allocation": "Detailed breakdown of recommended investment vehicles with percentage allocations",
    "Important Considerations": "Key factors and warnings specific to the user's situation",
    "Disclaimer": "I'm an AI chatbot, not a financial advisor. This information is for educational purposes only and should not replace professional advice."
}
"""

prompt = f"{user_data}\n\nBased on the above details, suggest an investment plan. Return the response in JSON format with the following structure: {output_format}. Give me a paragraph for each subsection."

def generate_investment_plan(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        if "404" in str(e) and "model" in str(e).lower():
            return f"Error: The model '{model_name}' is not available. Please check your API key permissions or try a different model."
        return f"Error generating investment plan: {str(e)}"

if st.button(" Generate Your Investment Plan! "):
    with st.spinner('Creating your personalized investment plan... '):
        try:
            response_text = generate_investment_plan(prompt)
            
            if response_text.startswith("Error:"):
                st.error(response_text)
            else:
                try:
                    if "```json" in response_text:
                        json_content = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        json_content = response_text.split("```")[1].strip()
                    else:
                        json_content = response_text
                        
                    investment_plan = json.loads(json_content)
                    
                    with st.container():
                        st.markdown("""
                        <div class="results-container">
                            <h2 style="text-align: center; margin-bottom: 1.5rem; background: linear-gradient(45deg, #3b82f6, #ff4d4d); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                 Your Investment Plan 
                            </h2>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown('<p class="results-header"> Understanding Your Situation</p>', unsafe_allow_html=True)
                            st.write(investment_plan["Understanding Your Situation"])
                            
                            st.markdown('<p class="results-header"> Investment Options & Potential Allocation</p>', unsafe_allow_html=True)
                            st.write(investment_plan["Investment Options & Potential Allocation"])
                        
                        with col2:
                            st.markdown('<p class="results-header glow-text"> Important Considerations</p>', unsafe_allow_html=True)
                            st.write(investment_plan["Important Considerations"])
                            
                            st.markdown('<p class="disclaimer">'+investment_plan["Disclaimer"]+'</p>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                except json.JSONDecodeError:
                    st.error("Could not parse the response as JSON. Raw response:")
                    st.text(response_text)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please try again with different parameters.")

with st.container():
    st.markdown("""
    <div style="text-align: center; margin-top: 4rem; padding: 1rem; border-top: 1px solid rgba(59, 130, 246, 0.2);">
        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
            Investment Planner. Chart Your Financial Future!
        </p>
    </div>
    """, unsafe_allow_html=True)