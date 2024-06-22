import openai
from config.settings import OPENAI_API_KEY, GPT_MODEL
from data.database import init_db, init_bq
import streamlit as st
import streamlit_calendar as st_calendar
import yaml
import json
from datetime import datetime, timedelta
import time
from query.meal_health_query import update_insert_meal_plans
import re

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

    total_calory = st.session_state.dietary["target_calories"]

    prompt_template = template.format(
        personal_info=personal_input_str,
        dietary=dietary_input_str,
        breakfast=f"{total_calory*0.3:.1f}",
        lunch=f"{total_calory*0.4:.1f}",
        dinner=f"{total_calory*0.3:.1f}",
        week_start=week_start,
        week_end=week_end
    )

    openai.api_key = OPENAI_API_KEY
    client = openai.Client()
    stream_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.5,
        response_format={"type": "json_object"},
        stream=True
    )

    response = st.write_stream(stream_response)
    save_meal_plan(response)
    update_counter()
    time.sleep(0.5)
    save_meal_plan_to_bq(response)
    display_meal_plan_by_calendar()
    st.rerun()


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


def update_counter():
    user_doc_ref = db.collection("users").document(
        st.session_state.user_id
    )
    tmp_counter = st.session_state.user_data["meal_plan_requests"] + 1
    user_doc_ref.update({
        "meal_plan_requests": tmp_counter
    })
    st.session_state.user_data["meal_plan_requests"] = tmp_counter


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
        st.subheader(plan["date"])
        meals = plan["meals"]
        meal_types = ["breakfast", "lunch", "dinner"]
        total_calorie = 0
        for meal_type in meal_types:
            if meal_type == "breakfast":
                st.write("**朝食**")
            elif meal_type == "lunch":
                st.write("**昼食**")
            else:
                st.write("**夕食**")
            menu_str = meals[meal_type]["menu"]
            weight_str = meals[meal_type]["weight"]
            cal_str = meals[meal_type]["calorie"]
            list_menu = menu_str.strip("[]").split(",")
            list_weight = weight_str.strip("[]").split(",")
            list_cal = cal_str.strip("[]").split(",")
            for i in range(len(list_menu)):
                st.write(f"{list_menu[i]} ({list_weight[i]} g) | {list_cal[i]} kcal")
                total_calorie += int(list_cal[i])
        st.write(f"総摂取カロリー: {total_calorie} kcal")
        st.write("-----")


def display_meal_plan_by_calendar():
    meal_plans = db.collection("meal_plans").where(
        "user_id", "==", st.session_state.user_id
    ).stream()

    start_suffix = {
        "breakfast": "T06:30:00",
        "lunch": "T12:00:00",
        "dinner": "T18:30:00"
    }
    end_suffix = {
        "breakfast": "T08:00:00",
        "lunch": "T13:30:00",
        "dinner": "T20:00:00"
    }
    eng_jp_convert = {
        "breakfast": "朝食",
        "lunch": "昼食",
        "dinner": "夕食"
    }

    meal_data = []
    i = 0
    for plan in meal_plans:
        data = plan.to_dict().get("data", {})
        for date, meals in data.items():
            for meal_type, detail in meals.items():
                menu_str = detail["menu"]
                weight_str = detail["weight"]
                cal_str = detail["calorie"]
                menu_list = menu_str.strip("[]").strip(" ").split(",")
                weight_list = weight_str.strip("[]").strip(" ").split(",")
                cal_list = cal_str.strip("[]").strip(" ").split(",")
                total_cal = 0
                for cal in cal_list:
                    int_cal = re.sub(r'\D', '', cal) 
                    total_cal += int(int_cal)

                n_list = len(menu_list)
                title = [
                    f"{menu_list[i]} ({weight_list[i]})" for i in range(n_list)
                ]
                title = ",".join(title)
                meal_data.append({
                    "id": i,
                    "title": f"{eng_jp_convert[meal_type]}: {title} | {total_cal} kcal",
                    "start": f"{date}{start_suffix[meal_type]}",
                    "end": f"{date}{end_suffix[meal_type]}"
                })
                i += 1
    options = {
        "initialView": "listWeek",
        "firstDay": 1,
        "height": "auto",
        "editable": False,
        "locale": "ja"
    }
    st_calendar.calendar(
        events=meal_data,
        options=options
    )


def save_meal_plan_to_bq(res):
    meal_plan_data = json.loads(res)
    for date, meals in meal_plan_data.items():
        for meal_type in ["breakfast", "lunch", "dinner"]:
            query = update_insert_meal_plans(
                st.session_state.user_id,
                datetime.strptime(date, "%Y-%m-%d").date(),
                meal_type,
                meals[meal_type]["menu"],
                meals[meal_type]["weight"],
                meals[meal_type]["calorie"]
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
    # Reset the meal_plan_requests counter
    if today > latest_date_in_db:
        st.session_state.user_data["meal_plan_requests"] = 0
        user_doc_ref.update({
            "meal_plan_requests": 0
        })
    else:
        pass
