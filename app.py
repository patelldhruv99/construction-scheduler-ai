import streamlit as st
import pandas as pd
from parser import extract_tasks_from_text
from io import StringIO
import datetime
import plotly.express as px

# Set up Streamlit UI
st.set_page_config(page_title="Construction Planner AI", layout="centered")
st.title("🏗️ AI Construction Planner")

# File upload or manual text input
uploaded_file = st.file_uploader("📁 Upload a .txt project description", type=["txt"])
manual_input = st.text_area("📝 Or paste your meeting notes / scope here", height=200)

input_text = ""

if uploaded_file:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    input_text = stringio.read()
elif manual_input:
    input_text = manual_input

# Continue only if we have text
if input_text:
    tasks = extract_tasks_from_text(input_text)
    df = pd.DataFrame(tasks)

    st.subheader("📋 Extracted Task List")

    def parse_date(text):
        try:
            return datetime.datetime.strptime(text, "%B %d")
        except:
            return None

    def parse_duration(text):
        try:
            number = int(''.join(filter(str.isdigit, text)))
            return datetime.timedelta(days=number)
        except:
            return datetime.timedelta(days=0)

    # Auto-infer start & end dates with safety check
    start_dates = []
    end_dates = []

    for i, row in df.iterrows():
        start_dt = parse_date(row["start_date"]) if row["start_date"] else None
        duration = parse_duration(row["duration"]) if row["duration"] else datetime.timedelta(days=0)

        if not start_dt and row["depends_on"] == "Previous task" and i > 0:
            prev_end = end_dates[i - 1]
            if prev_end:  # Only infer if previous task has valid end date
                start_dt = prev_end + datetime.timedelta(days=1)

        end_dt = start_dt + duration if start_dt else None
        start_dates.append(start_dt)
        end_dates.append(end_dt)

    df["Auto Start"] = [dt.strftime("%b %d") if dt else "" for dt in start_dates]
    df["Auto End"] = [dt.strftime("%b %d") if dt else "" for dt in end_dates]
    st.dataframe(df)

    # ⚠️ Conflict Detector
    st.subheader("⚠️ Conflict Detector")
    issues = []

    for i in range(1, len(df)):
        curr_start = start_dates[i]
        prev_end = end_dates[i - 1]

        if curr_start and prev_end and curr_start < prev_end:
            issues.append(
                f"🚨 '{df.iloc[i]['task']}' starts on {curr_start.strftime('%b %d')}, "
                f"but previous task '{df.iloc[i-1]['task']}' ends on {prev_end.strftime('%b %d')}"
            )

    if issues:
        for issue in issues:
            st.error(issue)
    else:
        st.success("✅ No conflicts detected!")

    # 📊 Gantt Chart View
    st.subheader("📊 Visual Gantt Chart")

    gantt_data = []
    for i, row in df.iterrows():
        start_dt = start_dates[i]
        end_dt = end_dates[i]
        if start_dt and end_dt:
            gantt_data.append({
                "Task": row["task"],
                "Start": start_dt,
                "Finish": end_dt
            })

    if gantt_data:
        gantt_df = pd.DataFrame(gantt_data)
        fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task", color="Task")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to display Gantt chart.")

    # 📤 Excel Export
    st.subheader("📤 Export")
    if st.button("Download Excel File"):
        export_df = df.copy()
        export_df["Auto Start Date"] = [dt.strftime("%B %d") if dt else "" for dt in start_dates]
        export_df["Auto End Date"] = [dt.strftime("%B %d") if dt else "" for dt in end_dates]
        export_df.to_excel("project_schedule.xlsx", index=False)
        st.success("✅ Excel file saved as project_schedule.xlsx")
