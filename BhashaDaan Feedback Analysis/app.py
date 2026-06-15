import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Bhashini Feedback Analytics",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(
        r"C:\Users\sneha\Downloads\BHASHHINI\FEEDBACK_PROJECT\master_feedback_raw.csv"
    )

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Filters")

service_options = ["All"] + sorted(
    df["service_id"].dropna().astype(str).unique().tolist()
)

task_options = ["All"] + sorted(
    df["task_type"].dropna().astype(str).unique().tolist()
)

lang_options = ["All"] + sorted(
    df["source_language"].dropna().astype(str).unique().tolist()
)

selected_service = st.sidebar.selectbox(
    "Service",
    service_options
)

selected_task = st.sidebar.selectbox(
    "Task Type",
    task_options
)

selected_lang = st.sidebar.selectbox(
    "Language",
    lang_options
)

filtered_df = df.copy()

if selected_service != "All":
    filtered_df = filtered_df[
        filtered_df["service_id"].astype(str)
        == selected_service
    ]

if selected_task != "All":
    filtered_df = filtered_df[
        filtered_df["task_type"].astype(str)
        == selected_task
    ]

if selected_lang != "All":
    filtered_df = filtered_df[
        filtered_df["source_language"].astype(str)
        == selected_lang
    ]

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 Bhashini Feedback Analytics Dashboard")

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Feedback",
    len(filtered_df)
)

col2.metric(
    "Models",
    filtered_df["service_id"].nunique()
)

col3.metric(
    "Languages",
    filtered_df["source_language"].nunique()
)

col4.metric(
    "Tasks",
    filtered_df["task_type"].nunique()
)

avg_rating = pd.to_numeric(
    filtered_df["pipeline_rating"],
    errors="coerce"
).mean()

col5.metric(
    "Avg Rating",
    round(avg_rating, 2)
)

st.divider()

# -----------------------------
# MODEL LEADERBOARD
# -----------------------------
st.subheader("🏆 Model Leaderboard")

leaderboard = (
    filtered_df.groupby("service_id")
    .agg(
        Total_Feedback=("service_id", "count"),
        Avg_Rating=("pipeline_rating", "mean")
    )
    .sort_values(
        "Total_Feedback",
        ascending=False
    )
)

st.dataframe(
    leaderboard,
    use_container_width=True
)

st.bar_chart(
    leaderboard["Total_Feedback"]
)

st.divider()

# -----------------------------
# LANGUAGE ANALYSIS
# -----------------------------
st.subheader("🌐 Language Distribution")

lang_dist = (
    filtered_df["source_language"]
    .value_counts()
)

st.bar_chart(lang_dist)

if len(lang_dist) > 0:

    dominant_lang_pct = (
        lang_dist.iloc[0]
        / len(filtered_df)
    )

    if dominant_lang_pct > 0.8:
        st.warning(
            "Dataset is highly dominated by one language."
        )

st.divider()

# -----------------------------
# TASK DISTRIBUTION
# -----------------------------
st.subheader("📊 Task Distribution")

task_dist = (
    filtered_df["task_type"]
    .value_counts()
)

st.bar_chart(task_dist)

st.divider()

# -----------------------------
# RATING DISTRIBUTION
# -----------------------------
st.subheader("⭐ Pipeline Rating Distribution")

rating_dist = (
    filtered_df["pipeline_rating"]
    .value_counts()
    .sort_index()
)

st.bar_chart(rating_dist)

# anomaly detection
if len(rating_dist) > 0:

    max_pct = (
        rating_dist.max()
        / rating_dist.sum()
    )

    if max_pct > 0.95:
        st.error(
            "Anomaly Detected: Nearly all ratings have the same value."
        )

st.divider()

# -----------------------------
# BENCHMARK QUALITY
# -----------------------------
st.subheader("📈 Benchmark Dataset Quality")

source_count = filtered_df[
    "source_text"
].notna().sum()

output_count = filtered_df[
    "model_output"
].notna().sum()

suggested_count = filtered_df[
    "suggested_output"
].notna().sum()

q1, q2, q3 = st.columns(3)

q1.metric(
    "Source Text Available",
    source_count
)

q2.metric(
    "Model Output Available",
    output_count
)

q3.metric(
    "Suggested Output Available",
    suggested_count
)

st.divider()

# -----------------------------
# HUMAN CORRECTION ANALYSIS
# -----------------------------
st.subheader("🧠 Human Correction Analysis")

benchmark = filtered_df[
    filtered_df["suggested_output"].notna()
].copy()

if len(benchmark) > 0:

    benchmark["exact_match"] = (
        benchmark["model_output"]
        .astype(str)
        .str.strip()
        ==
        benchmark["suggested_output"]
        .astype(str)
        .str.strip()
    )

    exact_match_rate = (
        benchmark["exact_match"]
        .mean()
        * 100
    )

    st.metric(
        "Exact Match %",
        round(exact_match_rate, 2)
    )

    st.metric(
        "Rows With Human Corrections",
        len(benchmark)
    )

else:

    st.info(
        "No suggested outputs available."
    )

st.divider()

# -----------------------------
# AUTO INSIGHTS
# -----------------------------
st.subheader("🔍 Dataset Insights")

if len(filtered_df) > 0:

    st.success(
        f"""
        • Most Used Model: {filtered_df['service_id'].mode().iloc[0]}

        • Dominant Language: {filtered_df['source_language'].mode().iloc[0]}

        • Dominant Task: {filtered_df['task_type'].mode().iloc[0]}

        • Human Corrections Available: {suggested_count}

        • Average Rating: {round(avg_rating,2)}
        """
    )

st.divider()
# -----------------------------
# RATING CONSISTENCY ANALYSIS
# -----------------------------

st.divider()

st.subheader("🎯 Rating Consistency Analysis")

if "task_rating" in filtered_df.columns:

    rating_df = filtered_df[
        filtered_df["pipeline_rating"].notna() &
        filtered_df["task_rating"].notna()
    ].copy()

    if len(rating_df) > 0:

        rating_df["ratings_match"] = (
            pd.to_numeric(
                rating_df["pipeline_rating"],
                errors="coerce"
            )
            ==
            pd.to_numeric(
                rating_df["task_rating"],
                errors="coerce"
            )
        )

        match_count = (
            rating_df["ratings_match"]
            .sum()
        )

        mismatch_count = (
            len(rating_df)
            - match_count
        )

        match_pct = (
            match_count
            / len(rating_df)
            * 100
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Rows With Both Ratings",
            len(rating_df)
        )

        c2.metric(
            "Matching Ratings",
            match_count
        )

        c3.metric(
            "Match %",
            f"{match_pct:.2f}%"
        )

        match_chart = pd.DataFrame({
            "Count": [
                match_count,
                mismatch_count
            ]
        },
        index=[
            "Match",
            "Mismatch"
        ])

        st.bar_chart(match_chart)

        st.dataframe(
            rating_df[
                rating_df["ratings_match"] == False
            ][[
                "_id",
                "service_id",
                "pipeline_rating",
                "task_rating"
            ]],
            use_container_width=True
        )

    else:

        st.warning(
            "No records contain both pipeline_rating and task_rating."
        )
        

# -----------------------------
# DATA EXPLORER
# -----------------------------
st.subheader("📄 Feedback Explorer")

st.dataframe(
    filtered_df,
    use_container_width=True
)
# -----------------------------
# TASK-WISE LANGUAGE ANALYSIS
# -----------------------------
st.subheader("🗂️ Task-wise Source Language Distribution")

# Group by task_type and source_language
task_lang_dist = (
    filtered_df.groupby(["task_type", "source_language"])
    .size()
    .reset_index(name="count")
)

if len(task_lang_dist) > 0:
    # Show full table
    st.dataframe(task_lang_dist, use_container_width=True)

    # Separate by task type
    for task in task_lang_dist["task_type"].unique():
        st.markdown(f"### 📌 {task}")
        subset = task_lang_dist[task_lang_dist["task_type"] == task]

        # Bar chart for each task
        st.bar_chart(
            subset.set_index("source_language")["count"]
        )
else:
    st.info("No task-language distribution available.")
