import streamlit as st
from datetime import date
from query.training_query import update_insert_training_log
from data.database import init_bq

training_options = [
    "筋力トレーニング",
    "屋外ランニング",
    "ウォーキング",
    "屋内ウォーキング",
    "インドアバイク",
    "クロストレーナー",
    "ヨガ",
    "ストレッチ",
    "休養"
]

bq = init_bq()

def add_exercise():
    exercise = st.selectbox(
        label="種目",
        options=training_options,
    )
    time = st.number_input(
        label="運動時間 [分]",
        min_value=0,
        max_value=300,
        step=5,
    )
    training_date = st.date_input(
        label="トレーニング日",
        min_value=date(2020, 1, 1),
    )
    if st.button("登録"):
        st.session_state.exercise_log = {
            "workout": exercise,
            "time": time,
            "training_date": training_date
        }
        save_training_log()


def save_training_log():
    if st.session_state.exercise_log:
        log = st.session_state.exercise_log
        query = update_insert_training_log(
            st.session_state.user_id,
            log["training_date"],
            log["workout"],
            log["time"]
        )
        query_job = bq.query(query)
        st.success("データベースに保存しました")
        st.session_state.exercise_log = None
