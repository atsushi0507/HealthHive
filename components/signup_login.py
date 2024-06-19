import streamlit as st
from firebase_admin import auth
from data.database import init_db
from datetime import datetime

db = init_db()

def show_login_signup_form():
    col1, col2 = st.columns(2)

    with col1:
        st.title("ログイン")
        email = st.text_input("メールアドレス", key="login_email")
        password = st.text_input("パスワード", key="login_pw", type="password")

        if st.button("ログイン"):
            try:
                # メールアドレスとパスワードでユーザー認証
                user = auth.get_user_by_email(email)
                user_token = auth.create_custom_token(user.uid)
                if user_token:
                    st.success("ログインに成功しました")
                    st.session_state.logged_in = True
                    st.session_state.show_login = False
                    st.session_state.user_id  = user.uid
                    st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

    with col2:
        st.title("サインアップ")
        email = st.text_input("メールアドレス", key="signup_email")
        password = st.text_input("パスワード", key="signup_pw", type="password")
        confirm_password = st.text_input("パスワード確認用", key="signup_pw_confirm", type="password")

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
                    st.session_state.user_id = user_id
                    st.rerun()

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
            else:
                st.error("パスワードが一致しません")

    return (st.session_state.logged_in, st.session_state.show_login)
