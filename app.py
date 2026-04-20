import streamlit as st
import pandas as pd
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib"))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server rendering

import matplotlib.pyplot as plt
import io
import streamlit.components.v1 as components
from fpdf import FPDF

try:
    from ydata_profiling import ProfileReport
    PROFILE_IMPORT_ERROR = None
except ImportError as exc:
    ProfileReport = None
    PROFILE_IMPORT_ERROR = str(exc)

st.set_page_config(page_title="CSV Data Processor & Report Generator", layout="wide")

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-card { background: #1e2130; border-radius: 10px; padding: 1rem; }
    h1 { color: #4fc3f7; }
    h3 { color: #90caf9; }
</style>
""", unsafe_allow_html=True)

st.title("📊 CSV Data Processor & Report Generator")
st.markdown("Upload any CSV file — clean it, analyze it deeply, and export a professional PDF report.")

uploaded_file = st.file_uploader("⬆️ Upload your CSV file", type=["csv"])

# ─── Helpers ───────────────────────────────────────────────────────────────────
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    return buf.read()

# ─── Main App ──────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)

    # Reset cleaned df when a new file is uploaded
    if st.session_state.get("last_file") != uploaded_file.name:
        st.session_state["cleaned_df"] = df_raw.copy()
        st.session_state["last_file"] = uploaded_file.name

    curr_df = st.session_state["cleaned_df"]

    # ── KPI Overview ────────────────────────────────────────────────────────────
    st.subheader("📋 Dataset Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Rows", f"{curr_df.shape[0]:,}")
    c2.metric("Total Columns", curr_df.shape[1])
    c3.metric("Duplicate Rows", int(curr_df.duplicated().sum()))
    c4.metric("Missing Values", int(curr_df.isnull().sum().sum()))
    missing_pct = round(curr_df.isnull().sum().sum() / curr_df.size * 100, 1)
    c5.metric("Data Quality", f"{100 - missing_pct}%", delta=f"-{missing_pct}% missing")

    st.dataframe(curr_df.head(10), use_container_width=True)

    num_cols = curr_df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = curr_df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ── TABS ────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧹 Clean & Analyze",
        "📈 Deep Profile",
        "📄 Export Report"
        , "Insight Lens",
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1: CLEAN & BASIC ANALYSIS
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🧹 Data Cleaning Tools")
        cl1, cl2, cl3 = st.columns(3)
        with cl1:
            if st.button("🗑️ Remove Duplicate Rows"):
                before = len(curr_df)
                st.session_state["cleaned_df"] = curr_df.drop_duplicates()
                after = len(st.session_state["cleaned_df"])
                st.success(f"Removed {before - after} duplicate rows.")
                st.rerun()
        with cl2:
            if st.button("🚫 Drop Rows with Missing Values"):
                before = len(curr_df)
                st.session_state["cleaned_df"] = curr_df.dropna()
                after = len(st.session_state["cleaned_df"])
                st.success(f"Dropped {before - after} rows with missing values.")
                st.rerun()
        with cl3:
            if st.button("🔢 Fill Missing Numbers with 0"):
                st.session_state["cleaned_df"] = curr_df.fillna({c: 0 for c in num_cols})
                st.success("Filled missing numeric values with 0.")
                st.rerun()

        st.divider()
        st.markdown("### 📊 Statistical Summary")
        if num_cols:
            st.dataframe(curr_df[num_cols].describe().round(2).T, use_container_width=True)
        else:
            st.info("No numeric columns found.")

        st.markdown("### 📉 Distribution Visualizer")
        if num_cols:
            sel_col = st.selectbox("Select a numeric column", num_cols, key="dist_col")
            fig, ax = plt.subplots(figsize=(10, 3))
            curr_df[sel_col].dropna().hist(bins=25, ax=ax, color="#4fc3f7", edgecolor="white")
            ax.set_title(f"Distribution of '{sel_col}'", fontsize=13)
            ax.set_facecolor("#1e2130")
            fig.patch.set_facecolor("#0e1117")
            ax.tick_params(colors="white")
            ax.title.set_color("white")
            st.pyplot(fig)
        else:
            st.info("No numeric columns available for visualization.")

    # ════════════════════════════════════════════════════════
    # TAB 2: CUSTOM DEEP PROFILING
    # ════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📈 Deep Data Profile")
        st.caption("Auto-generated column-by-column analysis — built with pandas & matplotlib.")

        # Missing values heatmap
        if curr_df.isnull().sum().sum() > 0:
            st.markdown("#### 🔍 Missing Values Per Column")
            miss = curr_df.isnull().sum().reset_index()
            miss.columns = ["Column", "Missing Count"]
            miss = miss[miss["Missing Count"] > 0].sort_values("Missing Count", ascending=False)
            st.dataframe(miss, use_container_width=True)

            fig_miss, ax_miss = plt.subplots(figsize=(10, max(2, len(miss) * 0.4)))
            ax_miss.barh(miss["Column"], miss["Missing Count"], color="#ef5350")
            ax_miss.set_facecolor("#1e2130")
            fig_miss.patch.set_facecolor("#0e1117")
            ax_miss.tick_params(colors="white")
            ax_miss.set_title("Missing Values Count", color="white")
            st.pyplot(fig_miss)
        else:
            st.success("✅ No missing values detected in the dataset!")

        # Numeric column deep dive
        if num_cols:
            st.markdown("#### 🔢 Numeric Columns — Full Stats")
            desc = curr_df[num_cols].describe().T
            desc["skewness"] = curr_df[num_cols].skew().round(3)
            desc["kurtosis"] = curr_df[num_cols].kurt().round(3)
            desc["% missing"] = (curr_df[num_cols].isnull().sum() / len(curr_df) * 100).round(1)
            st.dataframe(desc.round(3), use_container_width=True)

            st.markdown("#### 📊 Correlation Heatmap")
            if len(num_cols) >= 2:
                corr = curr_df[num_cols].corr()
                fig_corr, ax_corr = plt.subplots(figsize=(min(12, len(num_cols) + 2), min(10, len(num_cols) + 1)))
                im = ax_corr.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
                ax_corr.set_xticks(range(len(corr.columns)))
                ax_corr.set_yticks(range(len(corr.columns)))
                ax_corr.set_xticklabels(corr.columns, rotation=45, ha="right", color="white", fontsize=8)
                ax_corr.set_yticklabels(corr.columns, color="white", fontsize=8)
                for i in range(len(corr)):
                    for j in range(len(corr.columns)):
                        ax_corr.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7, color="white")
                fig_corr.colorbar(im, ax=ax_corr)
                fig_corr.patch.set_facecolor("#0e1117")
                ax_corr.set_facecolor("#1e2130")
                ax_corr.set_title("Correlation Matrix", color="white")
                st.pyplot(fig_corr)
            else:
                st.info("Need at least 2 numeric columns for correlation heatmap.")

        # Categorical columns analysis
        if cat_cols:
            st.markdown("#### 🔤 Categorical Columns — Value Counts")
            for col in cat_cols[:5]:  # Limit to 5 to avoid UI overload
                with st.expander(f"Column: **{col}** ({curr_df[col].nunique()} unique values)"):
                    top_vals = curr_df[col].value_counts().head(10)
                    fig_cat, ax_cat = plt.subplots(figsize=(8, 3))
                    top_vals.plot(kind="barh", ax=ax_cat, color="#7e57c2")
                    ax_cat.set_facecolor("#1e2130")
                    fig_cat.patch.set_facecolor("#0e1117")
                    ax_cat.tick_params(colors="white")
                    ax_cat.set_title(f"Top values in '{col}'", color="white")
                    st.pyplot(fig_cat)
                    st.caption(f"Most frequent: **{top_vals.index[0]}** ({top_vals.iloc[0]} times)")

    # ════════════════════════════════════════════════════════
    # =========================================================================
    # TAB 4: INSIGHT LENS
    # =========================================================================
    with tab4:
        st.markdown("### Insight Lens Report")
        st.caption(
            "Generates a full automated EDA report with column summaries, "
            "missing-value checks, correlations, alerts, and downloadable HTML."
        )

        if ProfileReport is None:
            st.error(
                "Insight Lens is not installed in this virtual environment. "
                "Run: python -m pip install -r requirements.txt"
            )
            st.info(
                "On Streamlit Cloud, confirm that requirements.txt in GitHub "
                "contains ydata-profiling==4.6.4 and that the app is deployed "
                "with Python 3.11."
            )
            if PROFILE_IMPORT_ERROR:
                with st.expander("Import details"):
                    st.code(PROFILE_IMPORT_ERROR)
        else:
            max_rows = st.slider(
                "Rows to analyze",
                min_value=100,
                max_value=max(100, min(len(curr_df), 10000)),
                value=min(len(curr_df), 1000),
                step=100,
                help="Large CSV files can take time, so the report profiles a sample by default."
            )
            profile_df = curr_df.head(max_rows)

            minimal_report = st.checkbox(
                "Use faster minimal report",
                value=True,
                help="Keeps the library working smoothly for larger datasets."
            )

            if st.button("Generate Insight Lens Report"):
                with st.spinner("Building the Insight Lens report..."):
                    profile = ProfileReport(
                        profile_df,
                        title=f"Insight Lens Report - {uploaded_file.name}",
                        explorative=True,
                        minimal=minimal_report,
                        pool_size=1,
                    )

                    html_bytes = profile.to_html().encode("utf-8")
                    components.html(html_bytes.decode("utf-8"), height=900, scrolling=True)
                    st.download_button(
                        "Download Insight Lens HTML",
                        data=html_bytes,
                        file_name="insight_lens_report.html",
                        mime="text/html",
                    )

    # TAB 3: EXPORT
    # ════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📄 Export Processed Data")

        # ── Cleaned CSV ────────────────────────────────────
        csv_bytes = curr_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Cleaned CSV", data=csv_bytes,
                           file_name="cleaned_data.csv", mime="text/csv")

        st.divider()

        # ── PDF Report ─────────────────────────────────────
        st.markdown("### 📑 Generate PDF Summary Report")
        st.caption("The report includes file info, statistical summary, and per-column analysis.")

        if st.button("⚙️ Generate & Download PDF Report"):
            with st.spinner("Building your PDF report..."):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                # Title
                pdf.set_font("Helvetica", "B", 20)
                pdf.set_text_color(30, 100, 200)
                pdf.cell(0, 12, "Automated Data Analysis Report", new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.ln(4)

                # File Meta
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 8, f"File: {uploaded_file.name}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 8, f"Rows: {curr_df.shape[0]:,}    Columns: {curr_df.shape[1]}    Missing Values: {int(curr_df.isnull().sum().sum())}    Duplicates: {int(curr_df.duplicated().sum())}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(6)

                # Column Summary Table
                pdf.set_font("Helvetica", "B", 13)
                pdf.set_text_color(30, 100, 200)
                pdf.cell(0, 10, "Column Overview", new_x="LMARGIN", new_y="NEXT")

                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(220, 230, 255)
                pdf.set_text_color(0, 0, 0)
                col_widths = [60, 30, 30, 30, 35]
                headers = ["Column Name", "Type", "Unique", "Missing", "Missing %"]
                for i, h in enumerate(headers):
                    pdf.cell(col_widths[i], 8, h, border=1, fill=True)
                pdf.ln()

                pdf.set_font("Helvetica", "", 9)
                for col in curr_df.columns:
                    miss_n = int(curr_df[col].isnull().sum())
                    miss_p = f"{miss_n / len(curr_df) * 100:.1f}%"
                    row = [col[:28], str(curr_df[col].dtype), str(curr_df[col].nunique()), str(miss_n), miss_p]
                    for i, val in enumerate(row):
                        pdf.cell(col_widths[i], 7, val, border=1)
                    pdf.ln()

                # Numeric Stats
                if num_cols:
                    pdf.ln(6)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 100, 200)
                    pdf.cell(0, 10, "Numeric Column Statistics", new_x="LMARGIN", new_y="NEXT")

                    desc = curr_df[num_cols].describe().round(2)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.set_fill_color(220, 230, 255)
                    pdf.set_text_color(0, 0, 0)
                    stat_widths = [50, 25, 25, 25, 25, 25, 20]
                    stat_headers = ["Column", "Mean", "Std", "Min", "25%", "75%", "Max"]
                    for i, h in enumerate(stat_headers):
                        pdf.cell(stat_widths[i], 8, h, border=1, fill=True)
                    pdf.ln()

                    pdf.set_font("Helvetica", "", 9)
                    for col in num_cols:
                        row_vals = [
                            col[:22],
                            str(desc.loc["mean", col]),
                            str(desc.loc["std", col]),
                            str(desc.loc["min", col]),
                            str(desc.loc["25%", col]),
                            str(desc.loc["75%", col]),
                            str(desc.loc["max", col]),
                        ]
                        for i, val in enumerate(row_vals):
                            pdf.cell(stat_widths[i], 7, val, border=1)
                        pdf.ln()

                # Categorical Summary
                if cat_cols:
                    pdf.ln(6)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 100, 200)
                    pdf.cell(0, 10, "Categorical Column Summary", new_x="LMARGIN", new_y="NEXT")

                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(0, 0, 0)
                    for col in cat_cols:
                        top = curr_df[col].value_counts().iloc[0]
                        top_val = curr_df[col].value_counts().index[0]
                        unique_count = curr_df[col].nunique()
                        pdf.cell(0, 7, f"{col}: {unique_count} unique values. Most frequent: '{top_val}' ({top}x)", new_x="LMARGIN", new_y="NEXT")

                pdf_bytes = bytes(pdf.output())

            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )
            st.success("✅ PDF report is ready!")

else:
    st.info("👆 Upload a CSV file above to get started.")
    st.markdown("""
    **What this tool does:**
    - 🧹 Cleans your CSV (duplicates, missing values)
    - 📊 Shows statistical summaries for all numeric columns
    - 📈 Deep profile: correlation heatmap, skewness, categorical breakdowns
    - 📄 Exports a professional PDF report
    """)
