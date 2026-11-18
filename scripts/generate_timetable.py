"""
Generate timetable.json from the Excel files used by the original project.

Expected files in the project root:
  - 5th Semester Time Table - REVISED-2025-07-31.xlsx
  - 5th sem group.xlsx
  - m_group.xlsx (optional, for PE-1 / PE-2 elective groups)

Run:
  pip install -r requirements.txt
  python scripts/generate_timetable.py

The script builds the regular group timetable and then overlays PE-1 / PE-2
rows when m_group.xlsx is present. Excel column names are validated below;
adjust COLUMN settings if your workbook uses different headings.
"""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TIMETABLE_FILE = ROOT / "5th Semester Time Table - REVISED-2025-07-31.xlsx"
GROUP_FILE = ROOT / "5th sem group.xlsx"
ELECTIVE_FILE = ROOT / "m_group.xlsx"
OUTPUT_FILE = ROOT / "timetable.json"

TIMETABLE_SHEET = "Table 9"
GROUP_SHEET = "Sheet1"
ROLL_COLUMN_GROUPS = "Roll No."
ROLL_COLUMN_ELECTIVES = "Roll No."
ELECTIVE_PE1_COLUMN = "Z"
ELECTIVE_PE2_COLUMN = "AA"


def clean_group(value):
    value = re.sub(r"[\s-]+", "", str(value)).lower()
    if value.startswith("ecsgroup"):
        number = value.replace("ecsgroup", "", 1)
        if number.isdigit():
            return f"ecsc{int(number)}"
    return value


def clean_roll(value):
    if pd.isna(value):
        return ""
    # Avoid converting Excel numeric roll numbers such as 2205... to "... .0".
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip().upper()


def clean_subject(value):
    if pd.isna(value) or str(value).strip() == "":
        return "No class"
    return str(value).strip()


def main():
    for path in (TIMETABLE_FILE, GROUP_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Missing required file: {path.name}. Put it in the project root."
            )

    timetable = pd.read_excel(TIMETABLE_FILE, sheet_name=TIMETABLE_SHEET)
    groups = pd.read_excel(GROUP_FILE, sheet_name=GROUP_SHEET)

    required_timetable = {"GROUP", "Day"}
    if not required_timetable.issubset(timetable.columns):
        raise ValueError(f"Timetable sheet must contain columns: {sorted(required_timetable)}")
    if ROLL_COLUMN_GROUPS not in groups.columns or "Group" not in groups.columns:
        raise ValueError("Group sheet must contain 'Roll No.' and 'Group' columns.")

    timetable["GROUP_clean"] = timetable["GROUP"].map(clean_group)
    timetable["Day"] = timetable["Day"].ffill().astype(str).str.strip().str.upper()
    subject_columns = [
        col for col in timetable.columns if col not in {"Day", "GROUP", "GROUP_clean"}
    ]

    # Build one weekly timetable per roll number.
    result = {}
    for _, student in groups.iterrows():
        roll = clean_roll(student[ROLL_COLUMN_GROUPS])
        group = clean_group(student["Group"])
        if not roll:
            continue
        matched = timetable[timetable["GROUP_clean"] == group]
        if matched.empty:
            print(f"Warning: no timetable rows found for group {group} (roll {roll})")
            continue
        result.setdefault(roll, {})
        for _, row in matched.iterrows():
            day = str(row["Day"]).strip().upper()[:3]
            if day not in {"MON", "TUE", "WED", "THU", "FRI"}:
                continue
            result[roll][day] = {
                str(col): clean_subject(row[col]) for col in subject_columns
            }

    # Overlay elective rows for students listed in m_group.xlsx, if supplied.
    if ELECTIVE_FILE.exists():
        electives = pd.read_excel(ELECTIVE_FILE, sheet_name=GROUP_SHEET)
        needed = {ROLL_COLUMN_ELECTIVES, ELECTIVE_PE1_COLUMN, ELECTIVE_PE2_COLUMN}
        if not needed.issubset(electives.columns):
            raise ValueError(
                f"Elective sheet must contain columns: {sorted(needed)}"
            )
        for _, student in electives.iterrows():
            roll = clean_roll(student[ROLL_COLUMN_ELECTIVES])
            if not roll:
                continue
            result.setdefault(roll, {})
            for elective_name, column in (
                ("PE-1", ELECTIVE_PE1_COLUMN),
                ("PE-2", ELECTIVE_PE2_COLUMN),
            ):
                group = clean_group(student[column])
                matched = timetable[timetable["GROUP_clean"] == group]
                if matched.empty:
                    print(f"Warning: no {elective_name} rows for group {group} (roll {roll})")
                    continue
                for _, row in matched.iterrows():
                    day = str(row["Day"]).strip().upper()[:3]
                    if day not in {"MON", "TUE", "WED", "THU", "FRI"}:
                        continue
                    result.setdefault(roll, {}).setdefault(day, {})
                    for col in subject_columns:
                        subject = clean_subject(row[col])
                        if subject.lower() != "no class":
                            result[roll][day][f"{col} ({elective_name})"] = subject

    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Created {OUTPUT_FILE.name} with {len(result)} student records.")


if __name__ == "__main__":
    main()
