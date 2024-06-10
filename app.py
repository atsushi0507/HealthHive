import streamlit as st
from streamlit import secrets
from components.sidebar import sidebar, show_login_signup_form
from utils.calc_pfc import calc_pfc
from utils.menu_suggestion import suggest_meal_plan
from utils.personal_trainer import suggest_training_plan

st.set_page_config(
    page_title="Health Hive",
    page_icon=":training"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False

personal_info = sidebar()
personal_info["id"] = "0001" # Dummy data: should be deleted.

dietary_info = calc_pfc(personal_info)
st.subheader("マクロ栄養素")
st.write(f"一日に必要なカロリ-: {dietary_info["target_calories"]:.1f} kcal")
st.write(f"タンパク質: {dietary_info["p_grams"]:.1f} [g]")
st.write(f"脂質: {dietary_info["f_grams"]:.1f} [g]")
st.write(f"炭水化物: {dietary_info["c_grams"]:.1f} [g]")

if st.button("食事の提案を受ける"):
    suggest_meal_plan(personal_info, dietary_info)

if st.button("今週のトレーニングメニューの作成"):
    suggest_training_plan(personal_info)



# # データ入力
# def input_data():
#     st.header("データ入力")
#     weight = st.number_input("体重 (kg)")
#     body_fat = st.number_input("体脂肪率 (%)")
#     exercise = st.text_area("運動内容")
#     if st.button("保存"):
#         # firestore への保存を実装
#         st.success("データを保存しました")

# # データ可視化
# def visualize_data():
#     st.header("データ可視化")
#     # Firestore から取得
#     records = []
#     # データを可視化する