import streamlit as st
from firebase_admin import auth
from data.database import init_db
from datetime import datetime

db = init_db()

def sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "show_login" not in st.session_state:
        st.session_state.show_login = False

    st.sidebar.button("ログイン/サインアップ", on_click=lambda: setattr(st.session_state, "show_login", True))


    st.sidebar.header("Personal Setting")
    height = st.sidebar.number_input("身長 (cm)")
    weight = st.sidebar.number_input("体重 (kg)")
    age = st.sidebar.number_input("年齢")
    gender = st.sidebar.selectbox("性別", ["男性", "女性"])
    activity_level = st.sidebar.selectbox("運動週間", ["ほとんど運動しない", "軽い運動をする", "中程度の運動をする", "活発に運動をする", "非常に激しい運動をする"])
    goal = st.sidebar.selectbox("目的", ["減量", "維持", "増量"])

    return {
        "height": height,
        "weight": weight,
        "age": age,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal
    }

def show_login_signup_form():
    st.title("ログイン/サインアップ")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    confirm_password = st.text_input("パスワード確認用", type="password")

    if st.button("登録"):
        if password == confirm_password:
            try:
                user = auth.create_user(
                    email=email,
                    password=password
                )
                st.success("ユーザー登録が完了しました")

                user_id = user.uid

                db.collection("users").document(user_id).set({
                    "email": email,
                    "height": None,
                    "weight": None,
                    "birthday": None,
                    "gender": None,
                    "activity_level": None,
                    "goal": None,
                    "meal_plan_requests": 0,
                    "training_plan_requests": 0,
                    "registration_timestamp": datetime.now().isoformat()
                })

                st.session_state.logged_in = True
                st.session_state.show_login = False
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        else:
            st.error("パスワードが一致しません")

    return (st.session_state.logged_in, st.session_state.show_login)