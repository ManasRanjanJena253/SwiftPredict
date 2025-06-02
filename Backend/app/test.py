# Importing dependencies
import streamlit as st
from Client.swift_predict import SwiftPredict
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

st.title("SwiftPredict")

X,y = make_classification(random_state = 21)

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify = y, test_size = 0.2, random_state = 21)

button = st.button("")