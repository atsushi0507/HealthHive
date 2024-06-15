import streamlit as st
from firebase_admin import auth
from data.database import init_db

db = init_db()

def check_user_data():
    try:
        doc_ref = db.collection("users").document(st.session_state.user_id)
        doc = doc_ref.get()
        if doc.exists:
            st.session_state.user_data = doc.to_dict()
        else:
            st.session_state.user_data = None
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
