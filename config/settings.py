import streamlit as st

OPENAI_API_KEY = st.secrets["openai"]["apiKey"]
MEAL_SUGGEST_LIMIT = 2
TRAIN_SUGGEST_LIMIT = 2
GPT_MODEL = "gpt-3.5-turbo"