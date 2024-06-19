import streamlit as st
from components.sidebar import sidebar
from utils.personal_trainer import (
    suggest_training_plan,
    reset_train_plan_counter,
    display_train_plan
)
from utils.save_training_history import (
    add_exercise,
)
from visualization.training import (
    read_from_bq,
    make_dashboard
)
from config.settings import TRAIN_SUGGEST_LIMIT

def train_plan_page():
    personal_info = sidebar()
    suggest_column()
    
    col1, col2 = st.columns(2)
    with col1:
        display_train_plan()

    with col2:
        st.subheader("トレーニングログ")
        add_exercise()

    if (
        st.button("データを更新") or 
        st.session_state.training_history is None
    ):
        read_from_bq()
    fig = make_dashboard()
    st.plotly_chart(fig, use_container_width=True)


def suggest_column():
    st.subheader("パーソナルトレーニングプラン")
    reset_train_plan_counter
    train_plan_requests = st.session_state.user_data["training_plan_requests"]
    if train_plan_requests < TRAIN_SUGGEST_LIMIT:
        disable_train_plan = False
    else:
        disable_train_plan = True
        st.error("リクエスト上限に達しました。次の月曜日までお待ちください。")
    
    rest_requests = TRAIN_SUGGEST_LIMIT - train_plan_requests
    st.write(f"今週はあと{rest_requests}回トレーニングプランの提案を受けられます。")
    if st.button("トレーニングメニューの作成", disabled=disable_train_plan):
        suggest_training_plan()
