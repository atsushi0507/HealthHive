import streamlit as st
from data.database import init_db
from datetime import date

db = init_db()

def input_user_info_form():
    st.title("ユーザー情報の登録")

    height = st.number_input("身長 [cm]", min_value=100.0, max_value=250.0, step=0.1)
    weight = st.number_input("体重 [kg]", min_value=30.0, max_value=200.0, step=0.1)
    birth_date = st.date_input("生年月日", min_value=date(1900, 1, 1))
    gender = st.selectbox("性別", ["男性", "女性"])
    activity_level = st.selectbox("運動習慣", [
        "ほとんど運動しない",
        "軽い運動をする",
        "中程度の運動をする",
        "活発に運動をする",
        "非常に激しい運動をする"
    ])
    goal = st.selectbox("目的", ["減量", "現状維持", "増量"])

    if st.button("登録"):
        try:
            user_data = {
                "height": height,
                "weight": weight,
                "birthday": birth_date.isoformat(),
                "gender": gender,
                "activity_level": activity_level,
                "goal": goal,
                "meal_plan_requests": 0,
                "training_plan_requests": 0
            }
            db.collection("users").document(st.session_state.user_id).update(user_data)
            st.session_state.user_data = user_data
            st.success("ユーザー情報が更新されました")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
        