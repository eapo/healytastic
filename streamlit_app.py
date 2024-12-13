import altair as alt
import pandas as pd
import streamlit as st
import requests

# # Show the page title and description.
# st.set_page_config(page_title="Movies dataset", page_icon="🎬")
# st.title("🎬 Movies dataset")
# st.write(
#     """
#     This app visualizes data from [The Movie Database (TMDB)](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).
#     It shows which movie genre performed best at the box office over the years. Just 
#     click on the widgets below to explore!
#     """
# )



url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer xai-4slNih4UsLZbFmgGKa8sEAn3IEbH01tWdBotTPS1CCxDIryljhcnl6ak6Kn4ega4bgrLIzkotTapmloC"
}

demo_datasets = {
    "Electoral": [
        {
            "name": "A",
            "age": 25,
        },
        {
            "name": "B",
            "age": 55,
        }
    ],
    "Hospital": [
        {
            "name": "C",
            "age": 25,
            "bmi": 21,
        },
        {
            "name": "D",
            "age": 55,
            "bmi": 32,
        }
    ]
}

# Construct the dataset as a string for the query
query_datasets = "Analyze these datasets for anomalies: "
for category, dataset in demo_datasets.items():
    query_datasets += f"{category}: {dataset} \n"

payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are an AI that detects anomalies in data. Tell me the percentage of probability, create me a markdown table. Explain us why the row is anomalous."
        },
        {
            "role": "user",
            "content": query_datasets
        }
    ],
    "model": "grok-beta",
    "stream": False,
    "temperature": 0
}

# response = requests.post(url, json=payload, headers=headers)

# if response.status_code == 200:
#     print("Response Data:")
#     print(response.json())
# else:
#     print(f"Error: {response.status_code}")
#     print(response.text)


# Streamlit app for interaction
st.title("Anomaly Detection API")

if st.button("Analyze Data"):
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        st.success("Response Received")
        response_data = response.json()

        # Extract and display the markdown tables from the response content
        content = response_data['choices'][0]['message']['content']
        sections = content.split("###")

        for section in sections:
            if section.strip():
                st.markdown(f"### {section.strip()}")
    else:
        st.error(f"Error: {response.status_code}")
        st.text(response.text)

# Placeholder for additional functionality to be preserved
def additional_functionality():
    st.write("Additional functionality can be integrated here.")

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/movies_genres_summary.csv")
    return df


df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
genres = st.multiselect(
    "Genres",
    df.genre.unique(),
    ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
)

# Show a slider widget with the years using `st.slider`.
years = st.slider("Years", 1986, 2006, (2000, 2016))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
df_reshaped = df_filtered.pivot_table(
    index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="year", ascending=False)


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Year")},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:N", title="Year"),
        y=alt.Y("gross:Q", title="Gross earnings ($)"),
        color="genre:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

