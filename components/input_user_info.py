import streamlit as st
from data.database import init_db
from datetime import date

db = init_db()

def input_user_info_form():
    st.title("ユーザー情報の登録")
    st.write(help)

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
            st.rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
        
def help():
    """
    運動習慣の目安:
    1. ほとんど運動しない
        デスクワーク中心で座っていることが多い。
        一日の運動は通勤・通学や近所のお買い物程度。
    2. 軽い運動をする
        上記の活動量が低い人 + 1 週間に1, 2 回程度軽い運動や筋トレをする。
    3. 中程度の運動をする。
        営業の外回りや肉体労働で一日中よく動いている。
        または 1 週間に 2, 3 回程度強度の高い運動や筋トレをする。
    4. 活発に運動をする
        上記の標準の人 + 1 週間に 4, 5 回程度強度の高い運動や筋トレをする
    5. 非常に激しい運動をする
        スポーツ選手・アスリート
    """