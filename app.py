import streamlit as st
from components.sidebar import sidebar
from components.signup_login import show_login_signup_form
from components.input_user_info import input_user_info_form
from utils.calc_pfc import calc_pfc
from utils.menu_suggestion import suggest_meal_plan, display_meal_plan, reset_meal_plan_counter
from utils.personal_trainer import suggest_training_plan, reset_train_plan_counter
from utils.check_user_data import check_user_data
from datetime import datetime, timedelta
from config.settings import MEAL_SUGGEST_LIMIT, TRAIN_SUGGEST_LIMIT

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

if st.session_state.show_login:
    show_login_signup_form()
elif st.session_state.logged_in:
    check_user_data()
    if (st.session_state.user_data
        and all(value is not None for key, value in st.session_state.user_data.items()
                if key not in ["meal_plan_requests", "training_plan_requests"])
        ): # ユーザー登録されていて、基本情報も入っていたらメイン機能を表示
        personal_info = sidebar()
    
        personal_info["id"] = st.session_state.user_id

        st.session_state.dietary = calc_pfc(personal_info)
        st.subheader("マクロ栄養素")
        st.write(f"一日に必要なカロリ-: {st.session_state.dietary["target_calories"]:.1f} kcal")
        st.write(f"タンパク質: {st.session_state.dietary["p_grams"]:.1f} [g]")
        st.write(f"脂質: {st.session_state.dietary["f_grams"]:.1f} [g]")
        st.write(f"炭水化物: {st.session_state.dietary["c_grams"]:.1f} [g]")

        reset_meal_plan_counter()

        meal_plan_requests = st.session_state.user_data["meal_plan_requests"]
        if meal_plan_requests < MEAL_SUGGEST_LIMIT:
            disable_meal_plan = False
        else:
            disable_meal_plan = True

        # reset_train_plan_counter()
        training_plan_requests = st.session_state.user_data["training_plan_requests"]
        if training_plan_requests < TRAIN_SUGGEST_LIMIT:
            disable_training_plan = False
        else:
            disable_training_plan = True
            st.error("リクエスト上限に達しました。次の週までお待ちください。")

        if st.session_state.user_data["meal_plan_requests"] >= 0:
            display_meal_plan()

        can_meal_plan_requests = MEAL_SUGGEST_LIMIT - st.session_state.user_data["meal_plan_requests"]
        st.write(f"今週はあと{can_meal_plan_requests}回リクエストできます")
        if st.button("食事の提案を受ける", disabled=disable_meal_plan):
            suggest_meal_plan()

        can_training_plan_requests = TRAIN_SUGGEST_LIMIT - st.session_state.user_data["training_plan_requests"]
        st.write(f"今週はあと{can_training_plan_requests}回リクエストできます")
        if st.button("今週のトレーニングメニューの作成", disabled=disable_training_plan):
            suggest_training_plan()
    else:
        input_user_info_form()
