from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    if file and file.filename != "":
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("students.csv")

    df.columns = df.columns.str.strip()

    subjects = ["Maths", "Science", "English", "Computer", "Statistics"]

    # Data Cleaning
    for col in subjects:
        df[col] = df[col].apply(lambda x: x if 0 <= x <= 100 else np.nan)
        df[col] = df[col].fillna(df[col].mean())

    # Feature Engineering
    df["Total"] = df[subjects].sum(axis=1)

    def grade(total):
        if total >= 400:
            return "A"
        elif total >= 300:
            return "B"
        elif total >= 200:
            return "C"
        else:
            return "Fail"

    df["Grade"] = df["Total"].apply(grade)

    # Filter
    selected_class = request.form.get("class_filter")
    if selected_class and selected_class != "All":
        df = df[df["Class"] == selected_class]

    # Analysis
    if df.empty:
        avg_marks = {}
        median_marks = {}
        grade_counts = {}
        total_marks = []
        pass_percentage = 0
        topper = {}
    else:
        avg_marks = df[subjects].mean().to_dict()
        median_marks = df[subjects].median().to_dict()
        grade_counts = df["Grade"].value_counts().to_dict()
        total_marks = df["Total"].tolist()

        pass_students = df[df["Total"]/5 >= 40]
        pass_percentage = round((len(pass_students) / len(df)) * 100, 2)

        topper = df.loc[df["Total"].idxmax()].to_dict()

    # Search
    search_name = request.form.get("search")
    filtered_data = None

    if search_name:
        filtered = df[df["Name"].str.lower() == search_name.lower()]
        if not filtered.empty:
            filtered_data = filtered.to_dict(orient="records")[0]

    return render_template("dashboard.html",
                           avg=avg_marks,
                           median=median_marks,
                           grade_data=grade_counts,
                           total_data=total_marks,
                           pass_perc=pass_percentage,
                           topper=topper,
                           student=filtered_data,
                           selected_class=selected_class)

if __name__ == "__main__":
    app.run(debug=True)