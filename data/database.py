from google.cloud import firestore, bigquery
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime
import streamlit as st
import json

# Firestoreの初期化
def init_firestore():
    return firestore.Client()

# Firebase Admin
def init_db():
    firebase_secrets = dict(st.secrets["firebase"])
    if not  firebase_admin._apps:
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    return db

# Bigquery
def init_bq():
    return bigquery.Client()