# ECS Timetable By AK

A lightweight student timetable website. Students enter their roll number, choose a starting weekday, and view the next day with classes plus their full weekly schedule. It includes a saved dark/light theme and remembers the last roll number in the browser.

## Project structure

```text
ECS-Timetable-By-AK/
├── index.html
├── styles.css
├── script.js
├── timetable.json
├── requirements.txt
├── scripts/
│   └── generate_timetable.py
└── README.md
```

## 1. Add your original Excel files

Put these files in the project root (beside `index.html`):

- `5th Semester Time Table - REVISED-2025-07-31.xlsx`
- `5th sem group.xlsx`
- `m_group.xlsx` (optional; used to add PE-1 and PE-2 elective slots)

The elective workbook is expected to have roll numbers in `Roll No.` and elective group names in columns `Z` (PE-1) and `AA` (PE-2). The regular group workbook is expected to have `Roll No.` and `Group` columns. The timetable workbook is expected to contain a sheet named `Table 9` with `GROUP` and `Day` columns.

If your Excel headings differ, edit the column settings near the top of `scripts/generate_timetable.py`.

## 2. Generate the student JSON data

Open a terminal in the project folder:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_timetable.py
```

This creates `timetable.json`, which the website reads. Keep this file in the same folder as `index.html`.

## 3. Run the website

The browser may block `fetch()` when you open the HTML directly using `file://`. Start a local server instead.

Using Python:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

Alternatively, use the VS Code **Live Server** extension.

## Data format

`timetable.json` must be an object keyed by each student's roll number:

```json
{
  "2300000000": {
    "MON": {
      "09:00-10:00": "Subject name",
      "10:00-11:00": "No class"
    },
    "TUE": {
      "09:00-10:00": "Another subject"
    }
  }
}
```

Use `"No class"` or `"X"` for empty slots. The page hides those slots from the displayed class list.

## Important

The supplied code did not include the actual Excel timetable/group workbooks or the final student timetable JSON. Therefore this project contains an empty `timetable.json` starter file. The website is ready, but it will not find real student roll numbers until you add the original Excel files and run the generator (or provide an already-generated JSON file).
