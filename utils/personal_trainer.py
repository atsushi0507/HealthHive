import openai
from config.settings import OPENAI_API_KEY
from data.database import init_firestore
import yaml
import streamlit as st

openai.api_key = OPENAI_API_KEY
db = init_firestore()

with open("prompt_templates.yaml", "r") as f:
    template = yaml.safe_load(f)["training_template"]

# Suggest training menu
def suggest_training_plan(personal_info):
    # user_id = personal_info["id"]
    # logs = db.collection("workout_logs").where("user_id", "==", user_id).stream()
    logs = []
    workout_history = [log.to_dict() for log in logs]

    personal_input_str = f"""
    身長: {personal_info["height"]:.1f} [cm]
    体重: {personal_info["weight"]:.2f} [kg]
    年齢: {personal_info["age"]:.0f} 歳
    性別: {personal_info["gender"]}
    日々の運動習慣: {personal_info["activity_level"]}
    目的: {personal_info["goal"]}
    """

    prompt_template = template.format(
        personal_info=personal_input_str,
        training_log=workout_history
    )

    client = openai.Client()
    stream_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.3,
        stream=True
    )

    response = st.write_stream(stream_response)
