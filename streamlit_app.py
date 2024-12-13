import altair as alt
import pandas as pd
import streamlit as st
import requests

# Streamlit app configuration and title
st.set_page_config(page_title="Anomaly Detection", page_icon="📊")
st.title("Anomaly Detection API")

# Demo datasets as DataFrames
demo_datasets = {
    "Electoral": pd.DataFrame([
        {"name": "A", "age": 25},
        {"name": "B", "age": 55},
    ]),
    "Hospital": pd.DataFrame([
        {"name": "C", "age": 25, "bmi": 21},
        {"name": "D", "age": 55, "bmi": 32},
    ]),
}

# File upload for custom CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    try:
        # Read uploaded CSV into a DataFrame
        uploaded_df = pd.read_csv(uploaded_file)
        uploaded_filename = uploaded_file.name  # Get the filename
        demo_datasets[uploaded_filename] = uploaded_df  # Use filename as the key
        st.success(f"CSV file '{uploaded_filename}' uploaded successfully!")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")

# Dropdown to select a dataset
dataset_options = list(demo_datasets.keys())
selected_dataset = st.selectbox("Select a dataset to analyze:", dataset_options)

# Display the selected dataset
st.write("### Selected Dataset:")
st.dataframe(demo_datasets[selected_dataset])

# API configuration
url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer xai-4slNih4UsLZbFmgGKa8sEAn3IEbH01tWdBotTPS1CCxDIryljhcnl6ak6Kn4ega4bgrLIzkotTapmloC",
}

# Convert the selected DataFrame to a JSON-like structure for the query
query_dataset = demo_datasets[selected_dataset].to_dict(orient="records")

payload = {
    "messages": [
        {
            "role": "system",
            "content": f"Analyze the dataset below for anomalies in {selected_dataset}. Detect issues, if present (and not limited to) such as: - Duplicate records. - Mismatched patient information (e.g., between NPI, claims, and insurance data). - Fraudulent billing patterns. - Resource mismanagement (e.g., unused allocations). - Cross-state compliance violations.",
        },
        {
            "role": "user",
            "content": f"Analyze this dataset for anomalies: {selected_dataset}: {query_dataset}",
        },
    ],
    "model": "grok-beta",
    "stream": False,
    "temperature": 0,
}

# Anomaly detection button
if st.button("Analyze Data"):
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        st.success("Response Received")
        response_data = response.json()

        # Extract and display the markdown tables from the response content
        content = response_data["choices"][0]["message"]["content"]
        sections = content.split("###")

        for section in sections:
            if section.strip():
                st.markdown(f"### {section.strip()}")
    else:
        st.error(f"Error: {response.status_code}")
        st.text(response.text)

# Placeholder for additional functionality
def additional_functionality():
    st.write("Additional functionality can be integrated here.")
