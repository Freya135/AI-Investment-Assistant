import json
import streamlit as st 
import google.generativeai as genai
import os
import time
import threading
from datetime import datetime

# Add a semaphore to limit concurrent requests
request_semaphore = threading.Semaphore(1)  # Allow only 1 request at a time

# Session state for rate limiting
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'error_count' not in st.session_state:
    st.session_state.error_count = 0

st.set_page_config(
    page_title="Investment Planner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with 3D elements and visual appeal
st.markdown("""
<style>
    /* Modern 3D UI Elements */
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #3b82f6, #ff4d4d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        letter-spacing: 2px;
        transform: perspective(500px) translateZ(0);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: perspective(500px) translateZ(0); }
        50% { transform: perspective(500px) translateZ(20px); }
        100% { transform: perspective(500px) translateZ(0); }
    }
    
    /* 3D Card Effect */
    .results-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2.5rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8.5px);
        -webkit-backdrop-filter: blur(8.5px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transform: perspective(1000px) rotateX(2deg);
        transition: all 0.3s ease;
    }
    
    .results-container:hover {
        transform: perspective(1000px) rotateX(0deg);
        box-shadow: 0 15px 35px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Enhanced Input Fields */
    .stSelectbox, .stNumberInput, .stSlider {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox:hover, .stNumberInput:hover, .stSlider:hover {
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Button 3D Effect */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.5) !important;
        transition: all 0.3s ease !important;
        transform: translateY(0) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #4f46e5, #3b82f6) !important;
        box-shadow: 0 7px 15px rgba(79, 70, 229, 0.7) !important;
        transform: translateY(-3px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 3px 8px rgba(79, 70, 229, 0.4) !important;
    }
    
    .results-header {
        font-size: 1.7rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        color: #f0f0f0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .glow-text {
        color: #ff4d4d;
        text-shadow: 0 0 10px rgba(255, 77, 77, 0.7);
    }
    
    .disclaimer {
        font-size: 0.8rem;
        color: #cccccc;
        margin-top: 2rem;
        font-style: italic;
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .footer {
        text-align: center;
        margin-top: 4rem;
        padding: 1rem;
        border-top: 1px solid rgba(59, 130, 246, 0.2);
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(30, 60, 114, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Input label enhancement */
    label.css-qrbaxs {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #a3bffa !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    }
    
    /* 3D Section dividers */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 2rem 0;
    }
    
    /* Animated background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1e3c72, #2a5298, #3a1c71);
        background-size: 400% 400%;
        z-index: -1;
        animation: gradientBG 15s ease infinite;
    }
    
    /* Info message styling */
    .stAlert {
        background: rgba(59, 130, 246, 0.2) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(5px) !important;
    }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <h1 class="main-title">INVESTMENT PLANNER</h1>
    """, unsafe_allow_html=True)

# Improved API key handling
try:
    # Try to get from Streamlit secrets (for deployed app)
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Try to get from environment variables (for local development)
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    
    if not GOOGLE_API_KEY:
        st.error("API key not found. Please set up your API key using Streamlit secrets.")
        st.info("For local development: Create a .streamlit/secrets.toml file with your GOOGLE_API_KEY.")
        st.info("For deployment: Add your API key in the app's settings under 'Advanced Settings'.")
        st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Cache model information to avoid repeated API calls
@st.cache_resource(ttl=3600)
def get_model_info():
    try:
        available_models = [model.name.split('/')[-1] for model in genai.list_models()]
        
        if 'gemini-1.5-pro' in available_models:
            model_name = 'gemini-1.5-pro'  
        elif 'gemini-pro' in available_models:
            model_name = 'gemini-pro'
        elif available_models:
            model_name = available_models[0]
        else:
            model_name = None
            
        return model_name, available_models
    except Exception as e:
        return 'gemini-1.5-pro', []

model_name, available_models = get_model_info()

if not model_name:
    st.error("No models available. Please check your API key.")
    st.stop()

with st.sidebar:
    st.markdown("### 📊 Model Information")
    if available_models:
        st.write("Available models:", available_models)
    st.success(f"Using model: {model_name}")
    
    st.markdown("---")
    
    # Add rate limit information in sidebar
    st.markdown("### 🔄 Rate Limit Info")
    st.write(f"Requests today: {st.session_state.request_count}")
    st.write(f"Errors encountered: {st.session_state.error_count}")
    
    # Reset counters button
    if st.button("Reset Counters"):
        st.session_state.request_count = 0
        st.session_state.error_count = 0
        st.session_state.last_request_time = 0
        st.success("Counters reset!")
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.info("If you encounter rate limit errors, wait a few minutes before trying again.")
    st.info("Your investment plan is cached for faster access when you return.")

model = genai.GenerativeModel(model_name)

# Main input form with 3D card effect
st.markdown("""
<div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 2rem; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2); backdrop-filter: blur(4px); border: 1px solid rgba(255, 255, 255, 0.1); transform: perspective(1000px) rotateX(1deg);">
    <h3 style="text-align: center; margin-bottom: 1.5rem; color: #a3bffa; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">Tell Us About Your Financial Goals</h3>
</div>
""", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        goal = st.selectbox('What is your primary financial goal? 🎯', 
                           ('Saving for retirement', 'Building an emergency fund', 'Buying a house', 
                            'Paying for a child\'s education', 'Taking a dream vacation'))
        
        income = st.number_input('What is your current income? (in Rupees) 💰', 
                                min_value=0, 
                                value=40000,
                                step=5000)
        
    with col2:
        time_horizon = st.selectbox('What is your investment time horizon? ⏳', 
                           ('Short-term (Less than 5 years)', 'Medium-term (5-10 years)', 'Long-term (10+ years)'))
        
        debt = st.selectbox('Do you have any existing debt? 💳', 
                           ('Yes', 'No'))
        
    invest = st.number_input('How much investable money do you have available? (in Rupees) 💵', 
                            min_value=0, 
                            step=1000)

    st.write("On a scale of 1-10, where 1 is very conservative and 10 is highly aggressive:")
    scale = st.slider("How comfortable are you with risk? 📊", 
                     min_value=1, 
                     max_value=10, 
                     value=5,
                     step=1)

user_data = f"""
- Primary financial goal is {goal}
- My current income level is {income} Rupees
- My investment time horizon is {time_horizon}
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

# Create a cache key based on user inputs
def create_cache_key(user_data):
    return f"{goal}_{income}_{time_horizon}_{debt}_{invest}_{scale}"

# Cache investment plans to avoid redundant API calls
@st.cache_data(ttl=3600)
def cached_investment_plan(cache_key, prompt):
    return generate_investment_plan(prompt)

def generate_investment_plan(prompt):
    # Use the semaphore to limit concurrent requests
    with request_semaphore:
        try:
            # Check if we need to wait before making another request
            current_time = time.time()
            time_since_last_request = current_time - st.session_state.last_request_time
            
            # Implement adaptive delay based on error count
            min_delay = 2 + (st.session_state.error_count * 5)  # Increase delay as errors increase
            
            if time_since_last_request < min_delay:
                wait_time = min_delay - time_since_last_request
                with st.spinner(f"Rate limiting in effect. Waiting {wait_time:.1f} seconds..."):
                    time.sleep(wait_time)
            
            # Update request tracking
            st.session_state.last_request_time = time.time()
            st.session_state.request_count += 1
            
            # Make the API call
            response = model.generate_content(prompt)
            
            # Add a small delay after successful request to prevent rapid successive calls
            time.sleep(1)
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            st.session_state.error_count += 1
            
            # Handle rate limit errors specifically
            if "429" in error_msg:
                # Extract retry delay if available
                retry_delay = 60  # Default to 60 seconds
                if "retry_delay" in error_msg and "seconds" in error_msg:
                    try:
                        retry_delay_str = error_msg.split("retry_delay")[1].split("seconds")[0]
                        retry_delay_str = ''.join(filter(str.isdigit, retry_delay_str))
                        retry_delay = int(retry_delay_str) if retry_delay_str else 60
                    except:
                        pass
                
                return f"Error: Rate limit exceeded. The API is currently overloaded. Please try again in {retry_delay} seconds."
            
            if "404" in error_msg and "model" in error_msg.lower():
                return f"Error: The model '{model_name}' is not available. Please check your API key permissions or try a different model."
            
            return f"Error generating investment plan: {error_msg}"

# Create a 3D button effect
st.markdown("""
<style>
    .generate-button {
        background: linear-gradient(45deg, #3b82f6, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.5);
        transition: all 0.3s ease;
        transform: translateY(0);
        width: 100%;
        text-align: center;
        cursor: pointer;
        margin-top: 20px;
        font-size: 1.1rem;
    }
    
    .generate-button:hover {
        background: linear-gradient(45deg, #4f46e5, #3b82f6);
        box-shadow: 0 7px 15px rgba(79, 70, 229, 0.7);
        transform: translateY(-3px);
    }
</style>
""", unsafe_allow_html=True)

# Custom button with 3D effect
if st.button("✨ Generate Your Investment Plan! ✨", key="generate_plan"):
    # Check if we already have this plan cached in session state
    cache_key = create_cache_key(user_data)
    
    if 'investment_plans' not in st.session_state:
        st.session_state.investment_plans = {}
    
    # Use the cached plan if available
    if cache_key in st.session_state.investment_plans:
        response_text = st.session_state.investment_plans[cache_key]
        st.info("Using cached investment plan")
    else:
        with st.spinner('Creating your personalized investment plan... '):
            response_text = cached_investment_plan(cache_key, prompt)
            # Store in session state for even faster retrieval
            st.session_state.investment_plans[cache_key] = response_text
    
    if response_text.startswith("Error:"):
        st.error(response_text)
    else:
        try:
            # Extract JSON content from response
            if "```json" in response_text:
                json_content = response_text.split("``````")[0]
            elif "```
                json_content = response_text.split("```")[1].split("```
            else:
                json_content = response_text

                
            investment_plan = json.loads(json_content)
            
            # Display results with 3D effects
            with st.container():
                st.markdown("""
                <div class="results-container">
                    <h2 style="text-align: center; margin-bottom: 1.5rem; background: linear-gradient(45deg, #3b82f6, #ff4d4d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; text-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                        ✨ Your Investment Plan ✨
                    </h2>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<p class="results-header">🔍 Understanding Your Situation</p>', unsafe_allow_html=True)
                    st.write(investment_plan["Understanding Your Situation"])
                    
                    st.markdown('<p class="results-header">💼 Investment Options & Potential Allocation</p>', unsafe_allow_html=True)
                    st.write(investment_plan["Investment Options & Potential Allocation"])
                
                with col2:
                    st.markdown('<p class="results-header glow-text">⚠️ Important Considerations</p>', unsafe_allow_html=True)
                    st.write(investment_plan["Important Considerations"])
                    
                    st.markdown('<p class="disclaimer">'+investment_plan["Disclaimer"]+'</p>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
        except json.JSONDecodeError:
            st.error("Could not parse the response as JSON. Raw response:")
            st.text(response_text)

# 3D floating footer
with st.container():
    st.markdown("""
    <div class="footer" style="transform: perspective(1000px) rotateX(-1deg); animation: float 6s ease-in-out infinite alternate;">
        <p>Investment Planner | Chart Your Financial Future! | Made with ❤️</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">© 2025 Investment Planner</p>
    </div>
    """, unsafe_allow_html=True)
