import openai
from config.settings import OPENAI_API_KEY, GPT_MODEL
from data.database import init_db, init_bq
import yaml
import json
from datetime import datetime, timedelta
from query.training_query import update_insert_training_plan
import time
import streamlit as st
import streamlit_calendar as st_calendar

db = init_db()
bq = init_bq()

with open("prompt_templates.yaml", "r") as f:
    template = yaml.safe_load(f)["training_template"]

# Suggest training menu
def suggest_training_plan():
    # user_id = personal_info["id"]
    # logs = db.collection("workout_logs").where("user_id", "==", user_id).stream()
    logs = []
    workout_history = [log.to_dict() for log in logs]

    personal_info = st.session_state.user_data
    personal_input_str = f"""
    身長: {personal_info["height"]:.1f} [cm]
    体重: {personal_info["weight"]:.2f} [kg]
    年齢: {personal_info["age"]:.0f} 歳
    性別: {personal_info["gender"]}
    日々の運動習慣: {personal_info["activity_level"]}
    目的: {personal_info["goal"]}
    """

    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    prompt_template = template.format(
        personal_info=personal_input_str,
        training_log=workout_history,
        week_start=week_start,
        week_end=week_end
    )

    openai.api_key = OPENAI_API_KEY
    client = openai.Client()
    stream_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.3,
        response_format={"type": "json_object"},
        stream=True
    )

    response = st.write_stream(stream_response)
    save_training_plan(response)
    update_counter()
    time.sleep(0.5)
    # save_training_plan_to_bq(response)
    # display_train_plan()
    st.rerun()


def update_counter():
    user_doc_ref = db.collection("users").document(
        st.session_state.user_id
    )
    tmp_counter = st.session_state.user_data["training_plan_requests"] + 1
    user_doc_ref.update({
        "training_plan_requests": tmp_counter
    })
    st.session_state.user_data["training_plan_requests"] = tmp_counter


def save_training_plan(res):
    train_plan_data = json.loads(res)
    train_entry = {
        "user_id": st.session_state.user_id,
    }
    train_plan_dict = {}

    doc_ref = db.collection("training_plans").document(
        f"{st.session_state.user_id}"
    )
    doc = doc_ref.get()

    for date, train in train_plan_data.items():
        train_plan_dict[date] = train
    train_entry["data"] = train_plan_dict

    if doc.exists:
        doc_ref.update({
            "data": train_entry["data"]
        })
    else:
        doc_ref.set(train_entry)


def save_training_plan_to_bq(res):
    train_plan_data = json.loads(res)
    for date, plans in train_plan_data.items():
        query = update_insert_training_plan(
            st.session_state.user_id,
            datetime.strptime(date, "%Y-%m-%d").date(),
            plans
        )
        query_job = bq.query(query)


def reset_train_plan_counter():
    train_plans = db.collection("training_plans").where(
        "user_id", "==", st.session_state.user_id
    ).stream()
    dates = []
    for plan in train_plans:
        data = plan.to_dict().get("data", {})
        for date, _ in data.items():
            dates.append(date)
    if len(dates) == 0:
        return
    latest_date_in_db = datetime.strptime(
        sorted(dates)[-1],
        "%Y-%m-%d"
    ).date()
    today = datetime.today().date()
    user_doc_ref = db.collection("users").document(
        st.session_state.user_id
    )

    if today > latest_date_in_db:
        st.session_state.user_data["training_plan_requests"] = 0
        user_doc_ref.update({
            "training_plan_requests": 0
        })
    else:
        pass


def display_train_plan():
    train_plans = db.collection("training_plans").where(
        "user_id", "==", st.session_state.user_id
    ).stream()
    train_data = []
    i = 0
    for plan in train_plans:
        data = plan.to_dict().get("data", {})
        for date, trains in data.items():
            menu_str = trains["menu"]
            set_str = trains["set"]
            list_menu = menu_str.strip("[]").split(",")
            list_set = set_str.strip("[]").split(",")

            menu = [
                f"{list_menu[i]} {list_set[i]}" for i in range(len(list_menu))
            ]
            menu = ",".join(menu)
            train_data.append({
                "id": i,
                "title": menu,
                "start": date
            })
            i += 1

    st.header("今週のトレーニング")

    options = {
        "initialView": "listWeek",
        "firstDay": 1,
        "height": "auto",
        "editable": False,
        "locale": "ja"
    }
    st_calendar.calendar(
        events=train_data,
        options=options
    )
