import streamlit as st
from datetime import date
from query.meal_health_query import (
    update_insert_health_log,
    update_insert_meal_log
)
from data.database import init_bq

bq = init_bq()

def add_health_log():
    st.subheader("体重・体脂肪率の記録")
    weight = st.number_input(
        label="体重 [kg]",
        value=st.session_state.user_data["weight"],
        min_value=30.0,
        max_value=200.0,
        step=0.1
    )
    body_fat = st.number_input(
        label="体脂肪率 %",
        value=15.0,
        min_value=0.,
        max_value=40.,
        step=0.1
    )
    input_date = st.date_input(
        label="記録する日",
        min_value=date(2020, 1, 1),
        key="date_health_log"
    )
    if st.button("登録", key="weight_log"):
        st.session_state.health_log = {
            "weight": weight,
            "body_fat": body_fat,
            "date": input_date
        }
        save_health_log()


def save_health_log():
    if st.session_state.health_log:
        log = st.session_state.health_log
        query = update_insert_health_log(
            st.session_state.user_id,
            log["date"],
            log["weight"],
            log["body_fat"]
        )
        query_job = bq.query(query)
        st.success("データベースに保存しました")
        st.session_state.health_log = None
    else:
        st.error("登録するデータがありません")


def add_meal_log():
    st.subheader("食事履歴の登録")
    meal_type = st.selectbox(
        label="食事タイプ",
        options=["朝食", "昼食", "夕食", "間食"]
    )
    menu = st.text_input(
        label="メニュー",
        value="",
        placeholder="例) なすと大葉の肉巻きロール、小松菜とシラスの炒めもの、切り干し大根とかぼちゃの味噌汁"
    )
    input_date = st.date_input(
        label="記録する日",
        min_value=date(2020, 1, 1),
        key="date_meal_log"
    )
    if menu is not None and st.button("登録", key="menu_log"):
        st.session_state.meal_log = {
            "date": input_date,
            "meal_type": meal_type,
            "menu": menu
        }
        save_meal_log()

    
def save_meal_log():
    if st.session_state.meal_log:
        log = st.session_state.meal_log
        query = update_insert_meal_log(
            st.session_state.user_id,
            log["date"],
            log["meal_type"],
            log["menu"]
        )
        _ = bq.query(query)
        st.success("データベースに保存しました")
        st.session_state.meal_log = None
    else:
        st.error("登録するデータがありません")