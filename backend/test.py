# Importing dependencies
import streamlit as st
import requests
from app.client.swift_predict import SwiftPredict
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
import pandas as pd
from io import BytesIO
from PIL import Image

X,y = make_classification(n_samples = 1000, random_state = 21)
model = LogisticRegression(max_iter = 500, penalty = 'l2', random_state = 21)

scores = cross_val_score(estimator = model, X = X, y = y, cv = 10, scoring = "accuracy")

def main():
    if "logger" not in st.session_state:
        st.session_state.logger = SwiftPredict(project_name = "Testing Classification Model")
    logger = st.session_state.logger
    logger.log_params({"model": "LogisticRegression", "penalty": "l2", "max_iter": 500})
    for step, value in enumerate(scores):
        logger.log_metric(step = step, value = value, key = "accuracy")

main()
base_url = "http://127.0.0.1:9000"

st.markdown(
    "<p style='font-size:40px; font-weight:bold;'>SwiftPredict: Your compass from data to discovery</p>",
    unsafe_allow_html=True
)

# Creating buttons
fetch_runs = st.button("Fetch Runs")
get_projects = st.button("Get All Created Projects")
visualize_run = st.button("Visualize Run Metrics")
add_notes = st.button("Add Notes")

if fetch_runs:
    project_name = st.text_input("Enter the project name")
    run_id = st.text_input("Enter the run id")
    search = st.button("Search")

    if search:
        response = requests.get(base_url + f"{project_name}/runs/{run_id}")
        data = response.json()

        df = pd.DataFrame(data, columns = ["Run Id"])
        st.dataframe(df)

elif get_projects:
    response = requests.get(base_url + "/projects")

    data = response.json()
    df = pd.DataFrame(data, columns = ["Projects"])
    st.dataframe(df)

elif visualize_run:
    project_name = st.text_input("Enter the project name")
    param = {"metric": "accuracy"}
    show = st.button("Show")
    if show:
        response = requests.get(base_url + f"/{project_name}/plots", params = param)

        img = Image.open(BytesIO(response.content))
        st.image(img)

elif add_notes:
    project_name = st.text_input("Enter the project name")
    run_id = st.text_input("Enter the run id")
    response = requests.get(base_url + f"/{project_name}/runs/{run_id}/add_notes")
    data = response.json()

    df = pd.DataFrame(data)
    st.dataframe(df)
