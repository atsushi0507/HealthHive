import streamlit as st
import pyrebase
from datetime import datetime

firebaseConfig = st.secrets["firebaseConfig"]

# Firebaseの初期化
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

def user_confirm():
    st.title("ユーザー登録")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    confirm_password = st.text_input("パスワード確認", type="password")

    if st.button("登録"):
        if password == confirm_password:
            try:
                # ユーザーを作成
                user = auth.create_user_with_email_and_password(
                    email,
                    password
                )
                st.success("ユーザー登録が完了しました")

                # ユーザーIDを取得
                user_id = user["localId"]

                # Firestoreにユーザー情報を保存 (初期値を設定)
                db.child("users").child(user_id).set({
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
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        else:
            st.error("パスワードが一致しません")