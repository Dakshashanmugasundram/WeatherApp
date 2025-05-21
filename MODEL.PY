import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

def list_models():
    try:
        models = genai.list_models()
        st.write("Available Gemini AI models:")
        for model in models:
            st.write(f"- {model.name} (Supports: {model.supported_generation_methods})")
    except Exception as e:
        st.error(f"Error listing models: {e}")

def main():
    st.title("Gemini AI Available Models")
    if gemini_api_key is None:
        st.error("Please set your GEMINI_API_KEY in the .env file")
        return
    list_models()

if __name__ == "__main__":
    main()
