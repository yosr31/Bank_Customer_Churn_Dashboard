# Bank Customer Churn Dashboard

An interactive Streamlit dashboard built from the supplied `Churn_Modelling(1).csv` dataset and the completed `Churn_EDA.ipynb`.

## Run locally

1. Install Python 3.10 or newer.
2. Extract the project ZIP and open a terminal in the extracted folder.
3. (Recommended) Create and activate a virtual environment:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
6. Streamlit opens the dashboard in your browser (usually `http://localhost:8501`).

## Files

- `app.py` — dashboard application.
- `requirements.txt` — Python dependencies.
- `Churn_Modelling(1).csv` — the original supplied dataset, bundled so the app works immediately.

You can also upload another compatible CSV from the sidebar. The app validates the columns it needs and does not create or augment records with synthetic data.

## Dashboard features

- KPI cards for customer count, churn, retention, average age, and average balance.
- Dynamic filters for geography, gender, age, membership, product count, and customer status.
- Interactive Plotly charts for churn composition, age, geography, segments, and numeric relationships.
- Searchable customer table with CSV export.
- Dataset quality checks and correlation-to-churn view.
- Insight statements calculated from the currently selected real records.

**Note:** This is a descriptive analytics dashboard, not a churn prediction model. Correlation and segment differences should not be interpreted as proof of causation.
