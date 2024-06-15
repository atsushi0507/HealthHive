import openai
from config.settings import OPENAI_API_KEY, GPT_MODEL
from data.database import init_db, init_bq
import streamlit as st
import yaml
import json
from datetime import datetime, timedelta
import time
from query.update_insert_meal_plan import update_insert_meal_plans

openai.api_key = OPENAI_API_KEY
with open("prompt_templates.yaml", "r") as f:
    template = yaml.safe_load(f)["meal_suggestion_template"]

db = init_db()
bq = init_bq()

def suggest_meal_plan():
    personal_info = st.session_state.user_data
    personal_input_str = f"""
    身長: {personal_info["height"]:.1f} [cm]
    体重: {personal_info["weight"]:.2f} [kg]
    年齢: {personal_info["age"]:.0f} 歳
    性別: {personal_info["gender"]}
    日々の運動習慣: {personal_info["activity_level"]}
    目的: {personal_info["goal"]}
    """

    dietary_input_str = f"""
    総摂取カロリー: {st.session_state.dietary["target_calories"]:.1f} [kcal]
    たんぱく質: {st.session_state.dietary["p_grams"]:.1f} [g]
    脂質: {st.session_state.dietary["f_grams"]:.1f} [g]
    炭水化物: {st.session_state.dietary["c_grams"]:.1f} [g]
    """

    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    prompt_template = template.format(
        personal_info=personal_input_str,
        dietary=dietary_input_str,
        week_start=week_start,
        week_end=week_end
    )

    client = openai.Client()
    stream_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
        response_format={"type": "json_object"},
        stream=True
    )

    response = st.write_stream(stream_response)
    save_meal_plan(response)
    time.sleep(0.5)
    save_meal_plan_to_bq(response)
    display_meal_plan()
    st.session_state.user_data["meal_plan_requests"] += 1
    st.experimental_rerun()


def save_meal_plan(res):
    meal_plan_data = json.loads(res)
    meal_entry = {
        "user_id": st.session_state.user_id,
    }
    meal_plan_dict = {}

    doc_ref = db.collection("meal_plans").document(
        f"{st.session_state.user_id}"
    )
    doc = doc_ref.get()

    for date, meals in meal_plan_data.items():
        meal_plan_dict[date] = meals
    meal_entry["data"] = meal_plan_dict

    if doc.exists:
        doc_ref.update({
            "data": meal_entry["data"]
        })
    else:
        doc_ref.set(meal_entry)


def display_meal_plan():
    meal_plans = db.collection("meal_plans").where(
        "user_id", "==", st.session_state.user_id
        ).stream()
    meal_data = []
    for plan in meal_plans:
        data = plan.to_dict().get("data", {})
        for date, meals in data.items():
            meal_data.append({"date": date, "meals": meals})
    meal_data.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))

    st.header("今週の献立")
    for plan in meal_data:
        st.write(plan["date"])
        st.write("朝食:　", plan["meals"].get("朝食", "なし"))
        st.write("昼食:　", plan["meals"].get("昼食", "なし"))
        st.write("夕食:　", plan["meals"].get("夕食", "なし"))
        st.write("-----")


def save_meal_plan_to_bq(res):
    meal_plan_data = json.loads(res)
    for date, meals in meal_plan_data.items():
        query = update_insert_meal_plans(
            st.session_state.user_id,
            datetime.strptime(date, "%Y-%m-%d").date(),
            meals["朝食"],
            meals["昼食"],
            meals["夕食"]
        )
        query_job = bq.query(query)


def reset_meal_plan_counter():
    meal_plans = db.collection("meal_plans").where(
        "user_id", "==", st.session_state.user_id
    ).stream()
    dates = []
    for plan in meal_plans:
        data = plan.to_dict().get("data", {})
        for date, _ in data.items():
            dates.append(date)
    latest_date_in_db = datetime.strptime(
        sorted(dates)[-1],
        "%Y-%m-%d"
    ).date()
    today = datetime.today().date()
    # Reset the meal_plan_requests counter
    if today > latest_date_in_db:
        st.session_state.user_data["meal_plan_requests"] = 0
        meal_plans.update({
            "meal_plan_requests": 0
        })
        st.experimental_rerun()
    else:
        pass
