import streamlit as st
from components.sidebar import sidebar
from utils.calc_pfc import calc_pfc
from utils.menu_suggestion import (
    suggest_meal_plan, 
    display_meal_plan_by_calendar,
    reset_meal_plan_counter
)
from utils.save_health_history import (
    add_health_log,
    add_meal_log
)
from visualization.health import (
    read_from_bq,
    plot_body_metrics
)
from config.settings import MEAL_SUGGEST_LIMIT

def meal_plan_page():
    personal_info = sidebar()

    st.session_state.dietary = calc_pfc(personal_info)
    st.header("マクロ栄養素")
    st.write(
        f"一日に必要なカロリー: {st.session_state.dietary['target_calories']:.1f} kcal"
    )
    st.write(f"タンパク質: {st.session_state.dietary['p_grams']:.1f} g")
    st.write(f"脂質: {st.session_state.dietary['f_grams']:.1f} g")
    st.write(f"炭水化物: {st.session_state.dietary['c_grams']:.1f} g")

    suggest_column()

    col1, col2 = st.columns(2)
    with col1:
        add_meal_log()

    with col2:
        add_health_log()

    if (
        st.button("データを更新") or
        st.session_state.body_history is None
    ):
        read_from_bq()
    fig = plot_body_metrics()
    st.plotly_chart(fig)


def suggest_column():
    reset_meal_plan_counter()

    meal_plan_requests = st.session_state.user_data["meal_plan_requests"]
    if meal_plan_requests < MEAL_SUGGEST_LIMIT:
        disable_meal_plan = False
    else:
        disable_meal_plan = True
        st.error("リクエスト上限に達しました。次の月曜日までお待ちください。")

    rest_requests = MEAL_SUGGEST_LIMIT - meal_plan_requests
    st.write(f"今週はあと{rest_requests}回食事の提案を受けられます")
    if st.button("食事の提案を受ける", disabled=disable_meal_plan):
        suggest_meal_plan()
    display_meal_plan_by_calendar()