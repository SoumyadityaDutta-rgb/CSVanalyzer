# CSV Data Processor & Report Generator

A Streamlit-powered data analysis app that turns any CSV file into a clean, visual, downloadable report. Upload a dataset, clean common issues, explore statistics, generate charts, export a PDF summary, and create a full Insight Lens report from the same interface.

## Highlights

- Upload and preview CSV files instantly.
- Remove duplicate rows, drop missing rows, or fill missing numeric values.
- View dataset KPIs including row count, column count, duplicates, missing values, and quality score.
- Explore numeric summaries, distributions, missing-value charts, categorical breakdowns, and correlation heatmaps.
- Export the cleaned data as CSV.
- Generate a professional PDF summary report.
- Generate an interactive Insight Lens HTML report for automated EDA.

## Tech Stack

- Python 3.11
- Streamlit
- Pandas
- Matplotlib
- Automated EDA engine
- fpdf2

## Project Structure

```text
advancedpython/
|-- app.py              # Main Streamlit application
|-- requirements.txt    # Python dependencies pinned for this app
|-- run.ps1             # Windows PowerShell launcher
|-- README.md           # Project documentation
`-- LICENSE             # MIT license
```

## Getting Started

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
.\run.ps1
```

Or run Streamlit directly:

```powershell
.\venv\Scripts\streamlit.exe run app.py
```

## Deploy To Streamlit Cloud

Push these project files to GitHub:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `README.md`
- `LICENSE`

Do not upload `venv`, `venv2`, `.matplotlib`, or `__pycache__`. They are ignored by `.gitignore` and Streamlit Cloud will rebuild the environment from `requirements.txt`.

In Streamlit Cloud, set the main file path to:

```text
app.py
```

## How To Use

1. Upload a CSV file from the file uploader.
2. Review the dataset overview and first rows.
3. Use the cleaning tools to remove duplicates or handle missing values.
4. Explore statistics and visualizations in the analysis tabs.
5. Export your cleaned CSV or PDF report.
6. Open the Insight Lens tab and generate a full HTML analysis report.

## Insight Lens Notes

Insight Lens powers the app's automated exploratory analysis workflow.

The report is generated with `pool_size=1` so it works reliably on Windows and restricted environments where multiprocessing/thread-pool pipes may be blocked.

For large datasets, use the row slider in the app to profile a smaller sample first.

## OneDrive Warning

This project currently lives inside a OneDrive folder. Virtual environments contain thousands of generated dependency files, so OneDrive may show sync or delete prompts when packages are installed or cleaned up.

Recommended setup:

- Keep `app.py`, `requirements.txt`, `run.ps1`, `README.md`, and `LICENSE` synced if you want.
- Avoid syncing `venv`, `venv2`, `.matplotlib`, and `__pycache__`.
- If the environment breaks, recreate it with `python -m venv venv` and reinstall `requirements.txt`.

## Troubleshooting

If Streamlit is missing:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Insight Lens fails after package changes:

```powershell
.\venv\Scripts\python.exe -m pip check
```

If the virtual environment was deleted by OneDrive:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
