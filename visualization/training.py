import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data.database import init_bq
from query.training_query import read_train_log

bq = init_bq()

def read_from_bq():
    query = read_train_log(
        st.session_state.user_id
    )
    df = bq.query(query).to_dataframe()
    st.session_state.training_history = df


def make_dashboard():
    fig = make_subplots(
        rows=3, cols=2,
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "domain"}, {"type": "domain"}],
               [{"colspan": 2, "type": "heatmap"}, None]
            ],
            subplot_titles=(
                "日ごとの運動時間",
                "週ごとの運動時間",
                "週ごとのワークアウト比率",
                "月ごとのワークアウト比率",
                "運動頻度と休息日のバランス"
            )
    )

    daily_fig = plot_daily_exercise()
    for trace in daily_fig["data"]:
        fig.add_trace(trace, row=1, col=1)

    weekly_fig = plot_weekly_exercise()
    for trace in weekly_fig["data"]:
        fig.add_trace(trace, row=1, col=2)

    weekly_dist_fig =plot_workout_components(period="weekly")
    for trace in weekly_dist_fig["data"]:
        fig.add_trace(trace, row=2, col=1)

    monthly_dist_fig = plot_workout_components(period="monthly")
    for trace in monthly_dist_fig["data"]:
        fig.add_trace(trace, row=2, col=2)

    heatmap_fig = plot_heatmap()
    for trace in heatmap_fig["data"]:
        fig.add_trace(trace, row=3, col=1)

    fig.update_layout(height=900, showlegend=False, title_text="運動記録ダッシュボード")
    return fig


def plot_workout_components(period="total"):
    df = st.session_state.training_history.copy()
    if period == "weekly":
        df["week"] = pd.to_datetime(df.date).dt.isocalendar().week
        summary = df.groupby(["week", "workout"]).agg({"duration": "sum"}).reset_index()
    elif period == "monthly":
        df["month"] = pd.to_datetime(df.date).dt.month
        summary = df.groupby(["month", "workout"]).agg({"duration": "sum"}).reset_index()
    else:
        summary = df.groupby("workout").agg({"duration": "sum"}).reset_index()

    pie_fig = px.pie(
        summary,
        values="duration",
        names="workout",
        title=f"種目ごとの割合: {period}"
    )
    return pie_fig


def plot_daily_exercise():
    df = st.session_state.training_history.copy()
    summary = df.groupby("date").agg({"duration": "sum"}).reset_index()
    fig = px.line(summary, x="date", y="duration", title="日毎の運動時間")
    return fig


def plot_heatmap():
    df = st.session_state.training_history.copy()
    df["day_of_week"] = pd.to_datetime(df.date).dt.day_name()
    df["week"] = pd.to_datetime(df.date).dt.isocalendar().week

    heatmap_data = df.pivot_table(
        values="duration",
        index="week",
        columns="day_of_week",
        aggfunc="sum",
        fill_value=0
    )
    day_order =  day_order = [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday'
    ]
    heatmap_data = heatmap_data.reindex(columns=day_order, fill_value=0)
    heatmap_data = heatmap_data[[
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale="Viridis",
            colorbar=dict(
                len=0.35,  # カラースケールの高さを調整するための長さ
                yanchor='middle',  # カラースケールを中央に配置
                y=0.1  # カラースケールのY位置を中央に設定
        )
        )
    )

    fig.update_layout(
        title="運動頻度と休息日のバランス",
        xaxis_nticks=7
    )
    return fig


def plot_weekly_exercise():
    df = st.session_state.training_history.copy()
    df["week"] = pd.to_datetime(df.date).dt.isocalendar().week
    summary = df.groupby("week").agg({"duration": "sum"}).reset_index()
    fig = px.bar(
        summary,
        x="week",
        y="duration",
        title="週ごとの運動時間"
    )
    return fig