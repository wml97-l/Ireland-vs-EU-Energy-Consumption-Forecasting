# Energy Consumption, Crude Oil Demand, and Sentiment Analysis (Ireland & EU)

## Project Overview

This project investigates the relationship between crude oil consumption and electricity consumption in Ireland and the European Union. In addition to traditional energy forecasting, the study incorporates sentiment analysis on energy-related discussions to explore how public opinion reflects or relates to energy consumption trends.

The project combines time-series forecasting, supervised machine learning, and natural language processing to provide a multi-dimensional view of energy dynamics. The study uses World Bank datasets for macroeconomic indicators and Reddit API data for sentiment extraction.

---

## Research Questions

* Does crude oil consumption influence electricity consumption in Ireland and the EU?
* Can machine learning models accurately predict energy consumption trends?
* How does public sentiment around energy topics relate to consumption patterns?
* Can ARIMA improve forecasting of crude oil consumption over time?

---

## Datasets

### Economic & Energy Data

* World Bank Open Data
* Crude oil consumption (Ireland & EU)
* Electricity consumption (Ireland & EU)

### Text Data

* Reddit API (energy-related discussions)

---

## Methodology

### 1. Data Processing

* Data collection from World Bank API and Reddit API
* Cleaning and normalization of time-series data
* Feature engineering for regression models

### 2. Supervised Learning Models

* Random Forest Regressor
* XGBoost Regressor
* Evaluation using:

  * Mean Squared Error (MSE)
  * Root Mean Squared Error (RMSE)
  * R² Score

### 3. Time Series Forecasting

* ARIMA model applied to crude oil consumption
* Trend and seasonality analysis

### 4. Sentiment Analysis (NLP)

* Text preprocessing using NLP techniques
* Sentiment scoring using VADER (Valence Aware Dictionary and Sentiment Reasoner)
* Sentiment trend analysis over time

### 5. Text Classification

* Multinomial Naive Bayes classifier
* Classification of energy-related sentiment
* Evaluation using classification report (precision, recall, F1-score)

### 6. Unsupervised Learning

* Clustering of text data
* Evaluation using Silhouette Score

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn
* XGBoost
* Statsmodels (ARIMA)
* NLTK (VADER)
* Reddit API (PRAW)
* Matplotlib / Seaborn
* Jupyter Notebook

---

## Key Findings

* A measurable relationship exists between crude oil consumption and electricity consumption trends.
* Machine learning models (Random Forest, XGBoost) effectively capture energy consumption patterns.
* ARIMA provides useful short-term forecasting capability for crude oil usage.
* Public sentiment around energy topics shows measurable trends that can complement economic indicators.
* Combining structured and unstructured data improves analytical depth.

---

## Future Improvements

* Use Transformer-based NLP models (BERT) for sentiment analysis.
* Incorporate real-time energy market data.
* Extend analysis to renewable energy consumption.
* Deploy an interactive dashboard for policymakers.
