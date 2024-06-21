import streamlit as st
from firebase_admin import auth
from data.database import init_db
from datetime import datetime
import time
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(message)
                else:
                    register_user(email, password)
                # try:
                #     user = auth.create_user(
                #         email=email,
                #         password=password
                #     )
                #     st.success("ユーザー登録が完了しました")

                #     user_id = user.uid

                #     db.collection("users").document(user_id).set({
                #         "email": email,
                #         "height": None,
                #         "weight": None,
                #         "birthday": None,
                #         "gender": None,
                #         "activity_level": None,
                #         "goal": None,
                #         "meal_plan_requests": 0,
                #         "training_plan_requests": 0,
                #         "registration_timestamp": datetime.now().isoformat()
                #     })

                #     st.session_state.logged_in = True
                #     st.session_state.show_login = False
                #     st.session_state.user_id = user_id
                #     st.rerun()

                # except Exception as e:
                #     st.error(f"エラーが発生しました: {e}")
            else:
                st.error("パスワードが一致しません")

    return (st.session_state.logged_in, st.session_state.show_login)


def register_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )

        link = auth.generate_email_verification_link(email)
        if send_verification_email(email, link):
            st.success(f"{email} 宛に確認メールを送りました。\n10分以内に本登録を完了してください。")
        else:
            st.error("確認メールの送信に失敗しました")

        timeout = time.time() + 600
        while True:
            user = auth.get_user(user.uid)
            if user.email_verified:
                st.success("登録完了です")
                break
            if time.time() > timeout:
                st.warining("有効期限が切れました。再度登録手続きを行ってください。")
            time.sleep(5)

        # Firestore に登録
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


def validate_password(password):
    if len(password) < 6:
        return False, "パスワードは最低6文字必要です"
    if not re.match("^[A-Za-z0-9@#$%^&+=!]+$", password):
        return False, "パスワードは英数字および記号(@, #, $, %, ^, &, +, =, !)のみ使用可能です"
    
    return True, ""


def send_verification_email(to_email, verification_link):
    from_email = st.secrets["mail"]["address"]
    password = st.secrets["mail"]["password"]

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = "[Health Hive] メールアドレス登録URL通知"

    body = f"""引き続き、下記URLから登録を行ってください。
    本メールを受信したメールアドレスが、アカウントとして登録されます。
    {verification_link}
    （URLの有効期限：10分間）

    ※このメールにお心当たりがない場合は、お手数ですがメールの破棄をお願いします。
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        # server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        st.warning(e)
        return False