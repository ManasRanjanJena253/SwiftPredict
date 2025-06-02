# Importing dependencies
import streamlit as st
from Client.swift_predict import SwiftPredict
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

st.title("SwiftPredict")

X,y = make_regression(random_state = 21)
button = st.button("")