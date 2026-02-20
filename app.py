from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import pdfkit
from io import BytesIO
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH_DEFAULT = os.path.join(BASE_DIR, "2ITsTiM_Raspisanie_2_polugodie_25-26_bak__pechat2.xlsx")
UPLOAD_PATH = os.path.join(BASE_DIR, "uploaded_timetable.xlsx")
CURRENT_EXCEL_PATH = EXCEL_PATH_DEFAULT
current_file_name = os.path.basename(EXCEL_PATH_DEFAULT)

DAY_ORDER = {
    "ПОНЕДЕЛЬНИК": 0,
    "ВТОРНИК": 1,
    "СРЕДА": 2,
    "ЧЕТВЕРГ": 3,
    "ПЯТНИЦА": 4,
    "СУББОТА": 5,
    "ВОСКРЕСЕНЬЕ": 6,
}


def load_dataframe(path):
    excel = pd.ExcelFile(path)
    preferred = ["for_app", "For_app", "FOR_APP"]
    df = None
    for name in preferred:
        if name in excel.sheet_names:
            df = excel.parse(name)
            break
    if df is None:
        for sheet in excel.sheet_names:
            df_candidate = excel.parse(sheet)
            cols = set(df_candidate.columns.astype(str))
            if "Day" in cols and "Time" in cols:
                df = df_candidate
                break
    if df is None:
        raise ValueError("在 Excel 中没有找到同时包含 'Day' 和 'Time' 列的工作表，请检查 Power Query 输出。")
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    return df


def normalize_weekday(value):
    text = str(value).strip().upper()
    text = text.replace(" ", "")
    return text


def time_order_value(value):
    text = str(value)
    if "1-2" in text:
        return 0
    if "3-4" in text:
        return 1
    if "5-6" in text:
        return 2
    if "7-8" in text:
        return 3
    if "9-10" in text:
        return 4
    if "11-12" in text:
        return 5
    return 999


def sort_labels_for_dropdown(values):
    def sort_key(v):
        norm = normalize_weekday(v)
        if norm in DAY_ORDER:
            return (0, DAY_ORDER[norm])
        return (1, str(v))

    return sorted(values, key=sort_key)


def refresh_data(path):
    global df, days, groups, CURRENT_EXCEL_PATH, current_file_name
    df = load_dataframe(path)
    df["Day"] = df["Day"].astype(str)
    unique_days = df["Day"].dropna().unique()
    days = sort_labels_for_dropdown(unique_days)
    base_cols = [c for c in df.columns if c not in ["Day", "Time"]]
    cleaned_groups = []
    for c in base_cols:
        name = str(c).strip()
        if not name:
            continue
        if name.startswith("列") or name.startswith("Unnamed"):
            continue
        series = df[c]
        non_na = series.dropna()
        if non_na.empty:
            continue
        non_blank = non_na[non_na.astype(str).str.strip() != ""]
        if non_blank.empty:
            continue
        cleaned_groups.append(c)
    groups = cleaned_groups
    CURRENT_EXCEL_PATH = path
    current_file_name = os.path.basename(path)


def build_day_rows(day_value):
    target = normalize_weekday(day_value)
    day_rows = df[df["Day"].apply(lambda v: normalize_weekday(v) == target)]
    result = []
    if day_rows.empty:
        return result
    day_rows = day_rows.copy()
    day_rows["__order"] = day_rows["Time"].apply(time_order_value)
    day_rows = day_rows.sort_values(["__order", "Time"])
    grouped_rows = day_rows.groupby("Time", sort=False)
    for time_label, group_df in grouped_rows:
        courses = []
        for g in groups:
            series = group_df[g]
            value = ""
            for v in series:
                if isinstance(v, float) and pd.isna(v):
                    continue
                text = str(v).strip()
                if not text:
                    continue
                value = v
                break
            courses.append(value)
        result.append({"time": time_label, "courses": courses})
    return result


def build_tables_for_day(day_value, chunk_size=8):
    rows = build_day_rows(day_value)
    tables = []
    if not rows:
        return tables
    total_groups = len(groups)
    for start in range(0, total_groups, chunk_size):
        group_slice = groups[start : start + chunk_size]
        table_rows = []
        for r in rows:
            courses_slice = r["courses"][start : start + chunk_size]
            table_rows.append({"time": r["time"], "courses": courses_slice})
        tables.append({"groups": group_slice, "rows": table_rows})
    return tables


refresh_data(EXCEL_PATH_DEFAULT)


@app.route("/")
def index():
    return render_template("index.html", teachers=days, current_file_name=current_file_name)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect(url_for("index", error="1"))
    file.save(UPLOAD_PATH)
    try:
        refresh_data(UPLOAD_PATH)
    except Exception:
        refresh_data(CURRENT_EXCEL_PATH)
        return redirect(url_for("index", error="1"))
    return redirect(url_for("index", uploaded="1"))


@app.route("/teacher")
def teacher_schedule():
    name = request.args.get("teacher")
    if not name:
        return "Не выбран день недели", 400
    tables = build_tables_for_day(name)
    if not tables:
        return "没有找到该教师的课程", 404
    return render_template("schedule.html", teacher=name, tables=tables)


@app.route("/teacher/pdf")
def teacher_schedule_pdf():
    name = request.args.get("teacher")
    if not name:
        return "Не выбран день недели", 400
    tables = build_tables_for_day(name)
    if not tables:
        return "没有找到该教师的课程", 404
    html = render_template("schedule.html", teacher=name, tables=tables)

    wkhtml_path = os.environ.get("WKHTMLTOPDF_PATH")
    try:
        if wkhtml_path:
            config = pdfkit.configuration(wkhtmltopdf=wkhtml_path)
        else:
            config = pdfkit.configuration()
        options = {
            "page-size": "A3",
            "orientation": "Landscape",
            "encoding": "UTF-8",
            "margin-top": "5mm",
            "margin-right": "5mm",
            "margin-bottom": "5mm",
            "margin-left": "5mm",
        }
        pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)
    except Exception:
        return "На сервере не установлен wkhtmltopdf, экспорт PDF недоступен.", 500

    pdf_file = BytesIO(pdf_bytes)
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"{name}_raspisanie.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

