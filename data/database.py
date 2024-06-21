from google.cloud import firestore, bigquery
import firebase_admin
from google.oauth2 import service_account
from firebase_admin import credentials, firestore
import streamlit as st

# Firestoreの初期化
def init_firestore():
    return firestore.Client()

# Firebase Admin
def init_db():
    firebase_secrets = dict(st.secrets["firebase"])
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    return db

# Bigquery
def init_bq():
    bq_secrets = service_account.Credentials.from_service_account_info(
        st.secrets["bigquery"]
    )

    return bigquery.Client(
        credentials=bq_secrets,
        project=bq_secrets.project_id
    )