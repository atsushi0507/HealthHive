import streamlit as st
from components.signup_login import show_login_signup_form
from components.input_user_info import input_user_info_form
from components.meal_health_manage import meal_plan_page
from components.training_manage import train_plan_page
from utils.check_user_data import check_user_data

st.set_page_config(
    page_title="Health Hive",
    page_icon=":training"
)

# アプリ内で扱う情報の初期化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = True
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "dietary" not in st.session_state:
    st.session_state.dietary = None
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = None
if "exercise_log" not in st.session_state:
    st.session_state.exercise_log = None
if "health_log" not in st.session_state:
    st.session_state.health_log = None
if "meal_log" not in st.session_state:
    st.session_state.meal_log = None
if "body_history" not in st.session_state:
    st.session_state.body_history = None
if "training_history" not in st.session_state:
    st.session_state.training_history = None

if st.session_state.show_login:
    show_login_signup_form()
elif st.session_state.logged_in:
    check_user_data()
    if (st.session_state.user_data
        and all(value is not None for key, value in st.session_state.user_data.items()
                if key not in ["meal_plan_requests", "training_plan_requests"])
        ): # ユーザー登録されていて、基本情報も入っていたらメイン機能を表示
        page = st.radio("ページ", ["食事・健康管理", "運動管理"])

        if page == "食事・健康管理":
            meal_plan_page()
        else:
            train_plan_page()

    else:
        input_user_info_form()
