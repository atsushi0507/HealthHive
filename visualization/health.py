import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data.database import init_bq
from query.meal_health_query import read_body_log

bq = init_bq()

def read_from_bq():
    query = read_body_log(
        st.session_state.user_id
    )
    df = bq.query(query).to_dataframe()
    st.session_state.body_history = df


def plot_body_metrics():
    df = st.session_state.body_history.copy()
    df["date"] = pd.to_datetime(df.date)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df.date,
        y=df.weight,
        name="体重",
        line={"color": "blue"}
    ))
    fig.add_trace(go.Scatter(
        x=df.date,
        y=df.body_fat,
        name="体脂肪率",
        line={"color": "red", "dash": "dashdot"}
        ),
    secondary_y=True
    )
    fig.update_xaxes(title="日付",showgrid=False)
    fig.update_yaxes(
        title="体重 [kg]", 
        showgrid=False,
        range=[df.weight.min()-5, df.weight.max()*1.05]
        )
    fig.update_yaxes(
        title="体脂肪率 [%]",
        showgrid=False,
        secondary_y=True,
        range=[0, df.body_fat.max()*1.5]
    )
    return fig