import streamlit as st
import pandas as pd
import os 
from io import BytesIO

# setup app
st.set_page_config(page_title="💿 Data Cleaner & Converter", layout="wide")
st.title("💿 Data Cleaner & Converter")
st.write("transform your file between CSV and Excel format with buit-in data cleaning and visualization")
upload_files = st.file_uploader("upload your file (CSV OR Excel):", type={"csv","xlsx"},accept_multiple_files=True)
if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext==".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else: 
            st.error(f"unsupported file type: {file_ext}")
            continue
        # display info about the file
        st. write(f"**fileName:**{file.name}")
        st.write(f"**FileSize:**{file.size/1024}")

        # show 5 rows of our df
        st.write("Preview The Head Of The dataframe")
        st.dataframe(df.head())

        # options for data cleaning
        st.subheader("🛠️data cleaning option")
        if st.checkbox(f"clean data for {file.name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"remove dupliacte from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("duplicates Removed!")
            
            with col2:
                if st.button(f"file missing values for{file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been filled!")

        # choose specific colun to keep or convert
        st.subheader("select columns to convert")  
        columns = st.multiselect(f"choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns] 

        # create some visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"show visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include="number").iloc[:,:2])

        # conver the file --> CSV to Excel
        st.subheader("💿 conversion options")
        conversion_type = st.radio(f"convert {file.name} to :", ["CSV", "Excel"], key=file.name)
        if st.button (f"convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer,index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer,index=False)
                file_name = file.name.replace(file_ext,".xlsx")
                mime_type = "applicatin/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # download button
            st.download_button(
                label=f"download ⬇️ {file.name} as {conversion_type}",
                data=buffer,
            file_name= file_name,
                mime=mime_type,
            ) 

st.success("🥳 All Files Processed")