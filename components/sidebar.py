import streamlit as st
from data.database import init_db
from datetime import date, datetime

def sidebar():
    udata = st.session_state.user_data
    init_gender = 0 if udata["gender"] == "男性" else 1

    st.sidebar.header("Personal Setting")
    height = st.sidebar.number_input("身長 (cm)", value=udata["height"])
    weight = st.sidebar.number_input("体重 (kg)", value=udata["weight"])
    birthday = st.sidebar.date_input("生年月日", min_value=date(1900, 1, 1), value=date.fromisoformat(udata["birthday"]))
    gender = st.sidebar.selectbox("性別", ["男性", "女性"],index=init_gender)
    activity_level = st.sidebar.selectbox("運動週間", ["ほとんど運動しない", "軽い運動をする", "中程度の運動をする", "活発に運動をする", "非常に激しい運動をする"], index=init_act_level(udata["activity_level"]))
    goal = st.sidebar.selectbox("目的", ["減量", "維持", "増量"], index=init_goal(udata["goal"]))

    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    st.session_state.user_data["age"] = age

    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.show_login = True
        st.session_state.user_id = None
        st.session_state.user_data = None
        st.experimental_rerun()

    return {
        "height": height,
        "weight": weight,
        "age": age,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal
    }

def init_act_level(act_level):
    if act_level == "ほとんど運動しない":
        return 0
    elif act_level == "軽い運動をする":
        return 1
    elif act_level == "中程度の運動をする":
        return 2
    elif act_level == "活発に運動をする":
        return 3
    elif act_level == "非常に激しい運動をする":
        return 4
    else:
        return -1
    
def init_goal(goal):
    if goal == "減量":
        return 0
    elif goal == "現状維持":
        return 1
    elif goal == "増量":
        return 2
    else:
        -1