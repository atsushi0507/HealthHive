import openai
from config.settings import OPENAI_API_KEY
import streamlit as st
import yaml

openai.api_key = OPENAI_API_KEY
with open("prompt_templates.yaml", "r") as f:
    template = yaml.safe_load(f)["meal_suggestion_template"]

def suggest_meal_plan(personal_info, dietary_info):
    personal_input_str = f"""
    身長: {personal_info["height"]:.1f} [cm]
    体重: {personal_info["weight"]:.2f} [kg]
    年齢: {personal_info["age"]:.0f} 歳
    性別: {personal_info["gender"]}
    日々の運動習慣: {personal_info["activity_level"]}
    目的: {personal_info["goal"]}
    """

    dietary_input_str = f"""
    総摂取カロリー: {dietary_info["target_calories"]:.1f} [kcal]
    たんぱく質: {dietary_info["p_grams"]:.1f} [g]
    脂質: {dietary_info["f_grams"]:.1f} [g]
    炭水化物: {dietary_info["c_grams"]:.1f} [g]
    """

    prompt_template = template.format(
        personal_info=personal_input_str,
        dietary=dietary_input_str
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
