import pandas as pd


def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format.")

        if df.empty:
            raise ValueError("The uploaded file is empty.")

        return df, None

    except Exception as e:
        return None, str(e)