import altair as alt
import pandas as pd
import streamlit as st
import requests
import firebase_admin
import json
from firebase_admin import credentials, db, auth

# Streamlit app configuration and title
st.set_page_config(page_title="Anomaly Detection", page_icon="📊")
st.title("Anomaly Detection API")

firebase_key = st.secrets["SERVICE_ACCOUNT_KEY"]
firebase_key_dict = json.loads(json.dumps(firebase_key))

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://data-vision-4b7ba-default-rtdb.firebaseio.com"
    })

# Firebase Authentication Helper Functions
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return {"status": "success", "message": f"User {email} registered successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(email, password):
    ref = db.reference(f"users/{email.replace('.', ',')}")
    user_data = ref.get()
    if user_data and user_data["password"] == password:
        return {"status": "success", "message": "Login successful!"}
    return {"status": "error", "message": "Invalid credentials."}

def save_user_to_db(email, password):
    ref = db.reference(f"users/{email.replace('.', ',')}")
    ref.set({"email": email, "password": password})

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["email"] = ""

# Login and registration workflow
if not st.session_state["logged_in"]:
    st.subheader("Login")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Login"):
        result = login_user(login_email, login_password)
        if result["status"] == "success":
            st.session_state["logged_in"] = True
            st.session_state["email"] = login_email
            st.success(result["message"])
            st.rerun()  # Re-render the page
        else:
            st.error(result["message"])

    st.subheader("Register")
    reg_email = st.text_input("New Email")
    reg_password = st.text_input("New Password", type="password")
    if st.button("Register"):
        result = register_user(reg_email, reg_password)
        if result["status"] == "success":
            save_user_to_db(reg_email, reg_password)
            st.success(result["message"])
        else:
            st.error(result["message"])
else:
    # Main app functionality after login
    st.success(f"Welcome, {st.session_state['email']}!")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["email"] = ""
        st.rerun()  # Re-render the page

    # Demo datasets
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
            uploaded_df = pd.read_csv(uploaded_file)
            uploaded_filename = uploaded_file.name
            demo_datasets[uploaded_filename] = uploaded_df
            st.success(f"CSV file '{uploaded_filename}' uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")

    # Dropdown to select a dataset
    dataset_options = list(demo_datasets.keys())
    selected_dataset = st.selectbox("Select a dataset to analyze:", dataset_options)

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
