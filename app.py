import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="💿 Data Cleaner & Converter", layout="wide")

st.markdown("""
    <style>
        /* Global font and background */
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
            color: #1c1c1c;
        }

        /* Header Title */
        .main > div > div > div > div > h1 {
            color: #343a40;
            font-weight: 800;
            font-size: 2.5rem;
        }

        /* File uploader */
        .stFileUploader {
            border: 2px dashed #007bff !important;
            padding: 1.5rem;
            background-color: black;
            border-radius: 10px;
        }

        /* Buttons */
        button[kind="primary"] {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        button[kind="primary"]:hover {
            background-color: #0056b3;
        }

        /* Subheaders */
        .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #212529;
            border-left: 5px solid #007bff;
            padding-left: 10px;
            margin-top: 2rem;
        }

        /* Green success box */
        .stAlert {
            background-color: dark green;
            color: #155724;
            border-left: 5px solid #28a745;
        }

        /* Chart padding */
        .element-container:has(div[data-testid="stBarChart"]) {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💿 Data Cleaner & Converter")
st.markdown("Transform your CSV or Excel files with built-in data cleaning, selection, and visualization tools.")


# File uploader
st.sidebar.header("📁 Upload Files")
upload_files = st.sidebar.file_uploader("Upload your file(s) (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Initialize df outside the if/elif blocks to ensure it's always defined
        df = pd.DataFrame()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            try:
                df = pd.read_excel(file, engine="openpyxl")
            except ImportError:
                st.error("❌ Missing dependency: Please install `openpyxl`.")
                st.stop()
            except Exception as e:
            st.error(f"⚠️ Could not read Excel file: {e}")
            continue
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue # Skip to the next file if type is unsupported

        # Check if DataFrame is empty after reading (e.g., if file was empty or corrupted)
        if df.empty:
            st.warning(f"⚠️ The file '{file.name}' appears to be empty or could not be read.")
            continue # Skip to the next file

        st.divider()
        st.subheader(f"📄 File: {file.name}")
        st.write(f"**File Size:** {round(file.size / 1024, 2)} KB")

        # Show preview
        with st.expander("🔍 Preview First 5 Rows"):
            st.dataframe(df, width='stretch')

        # Data cleaning options
        with st.expander("🧹 Data Cleaning Options"):
            st.markdown("Select cleaning actions for this file:")
            col1, col2 = st.columns(2)

            with col1:
                # Use a unique key for each button to prevent conflicts when multiple files are uploaded
                if st.button(f"🧽 Remove Duplicates – {file.name}", key=f"remove_duplicates_{file.name}"):
                    initial_rows = df.shape[0]
                    df.drop_duplicates(inplace=True)
                    rows_removed = initial_rows - df.shape[0]
                    if rows_removed > 0:
                        st.success(f"✅ Duplicates removed! ({rows_removed} rows removed)")
                    else:
                        st.info("ℹ️ No duplicates found.")

            with col2:
                if st.button(f"🧴 Fill Missing Values – {file.name}", key=f"fill_missing_{file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if not numeric_cols.empty:
                        # Check if there are any missing values before filling
                        missing_count = df[numeric_cols].isnull().sum().sum()
                        if missing_count > 0:
                            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                            st.success(f"✅ Missing numeric values filled with column means. ({missing_count} values filled)")
                        else:
                            st.info("ℹ️ No missing numeric values found.")
                    else:
                        st.info("ℹ️ No numeric columns to fill missing values for.")

        # Column selection
        with st.expander("📌 Select Columns to Keep"):
            # Ensure default selection is based on current df columns
            columns = st.multiselect(f"Select columns for: {file.name}", df.columns.tolist(), default=df.columns.tolist(), key=f"col_select_{file.name}")
            df = df[columns]

        # Visualization
        with st.expander("📊 Data Visualization"):
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if len(numeric_cols) >= 1:
                st.write("Displaying bar chart for numeric columns:")
                
                # Select up to two numeric columns for visualization
                cols_to_plot = []
                if len(numeric_cols) >= 2:
                    cols_to_plot = numeric_cols[:2]
                    st.write(f"Showing '{cols_to_plot[0]}' and '{cols_to_plot[1]}'.")
                    st.bar_chart(df[cols_to_plot])
                elif len(numeric_cols) == 1:
                    col_name = numeric_cols[0]
                    st.write(f"Showing '{col_name}'.")
                    # For a single numeric column, create a temporary DataFrame with an index column
                    # to make Altair happy for bar charts.
                    plot_df = pd.DataFrame({
                        'index': df.index.astype(str), # Convert index to string for categorical x-axis
                        col_name: df[col_name]
                    })
                    st.bar_chart(plot_df, x='index', y=col_name) # Explicitly define x and y
                else:
                    st.info("No suitable numeric columns found for visualization after selection.")
            else:
                st.info("No numeric columns available for visualization.")

        # File conversion
        with st.expander("💾 Convert and Download"):
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], horizontal=True, key=f"conversion_type_{file.name}")

            if st.button(f"🔄 Convert {file.name}", key=f"convert_button_{file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    output_name = file.name.rsplit(".", 1)[0] + ".csv"
                    mime_type = "text/csv"
                else:
                    df.to_excel(buffer, index=False)
                    output_name = file.name.rsplit(".", 1)[0] + ".xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)
                st.download_button(
                    label=f"⬇️ Download {output_name}",
                    data=buffer,
                    file_name=output_name,
                    mime=mime_type,
                    key=f"download_button_{file.name}" # Unique key for download button
                )

    st.sidebar.success("🎉 All files processed successfully!")
else:
    st.sidebar.info("Please upload a CSV or Excel file to get started!")



