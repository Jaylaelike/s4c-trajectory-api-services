import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="GPS Scintillation Analyzer",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
FASTAPI_URL = "http://backend:8000"

# --- Helper Functions ---
@st.cache_data
def convert_df_to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode('utf-8')

def fetch_data_from_api(endpoint):
    """Fetches data from a FastAPI endpoint."""
    try:
        response = requests.get(f"{FASTAPI_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to API: {e}")
        return None

def fetch_html_from_api(endpoint):
    """Fetches HTML content from a FastAPI endpoint."""
    try:
        response = requests.get(f"{FASTAPI_URL}/{endpoint}")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to API: {e}")
        return None

# --- UI Sidebar ---
with st.sidebar:
    st.header("📡 GPS Scintillation Analyzer")
    st.write("Upload your GPS data files to begin. You can select all files at once.")
    
    # Use a single multi-file uploader
    uploaded_files = st.file_uploader(
        "Upload S4C, Latitude, and Longitude CSV files",
        type="csv",
        accept_multiple_files=True
    )

    # Initialize file holders
    s4c_file = None
    lat_file = None
    lon_file = None

    # Automatically identify uploaded files
    if uploaded_files:
        for file in uploaded_files:
            # More specific checks can be added if filenames are ambiguous
            if "S4C" in file.name:
                s4c_file = file
            elif "Lat" in file.name:
                lat_file = file
            elif "Lon" in file.name:
                lon_file = file
    
    # Display file recognition status
    with st.expander("File Status", expanded=True):
        st.markdown(f"**S4C Data:** {'✅ Found' if s4c_file else '❌ Missing'}")
        st.markdown(f"**Latitude Data:** {'✅ Found' if lat_file else '❌ Missing'}")
        st.markdown(f"**Longitude Data:** {'✅ Found' if lon_file else '❌ Missing'}")

    analyze_button = st.button("🚀 Analyze Data", type="primary", use_container_width=True)

# --- Main Page ---
st.title("GPS Scintillation Analysis Dashboard")

if analyze_button:
    # Check if all files were identified before proceeding
    if s4c_file and lat_file and lon_file:
        with st.spinner("🛰️ Processing data... This may take a moment."):
            files_to_send = {
                "s4c_file": (s4c_file.name, s4c_file.getvalue(), "text/csv"),
                "lat_file": (lat_file.name, lat_file.getvalue(), "text/csv"),
                "lon_file": (lon_file.name, lon_file.getvalue(), "text/csv"),
            }
            try:
                response = requests.post(f"{FASTAPI_URL}/analyze/", files=files_to_send, timeout=60)
                response.raise_for_status()
                st.session_state["analysis_complete"] = True
                st.success("✅ Analysis complete! Results are shown below.")
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e}")
                st.session_state["analysis_complete"] = False
    else:
        st.warning("⚠️ Please ensure one of each required file type (S4C, Lat, Lon) is uploaded and recognized.")

if st.session_state.get("analysis_complete", False):
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Interactive Dashboard", "🗺️ Geographic Map", "📈 Statistics", "💾 Data Tables"])

    with tab1:
        st.header("Interactive Analysis Dashboard")
        plotly_json = fetch_data_from_api("plots/plotly")
        if plotly_json:
            fig = go.Figure(plotly_json)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Geographic Scintillation Map")
        map_html = fetch_html_from_api("plots/folium")
        if map_html:
            st.components.v1.html(map_html, height=600, scrolling=False)

    with tab3:
        st.header("Statistical Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("By Satellite")
            sat_stats = fetch_data_from_api("stats/satellite")
            if sat_stats:
                st.dataframe(pd.DataFrame(sat_stats), use_container_width=True)
        with col2:
            st.subheader("By Time (per minute)")
            temp_stats = fetch_data_from_api("stats/temporal")
            if temp_stats:
                st.dataframe(pd.DataFrame(temp_stats), use_container_width=True)

    with tab4:
        st.header("Processed Data")
        
        st.subheader("Transformed Data")
        transformed_data_json = fetch_data_from_api("data/transformed")
        if transformed_data_json:
            df_transformed = pd.DataFrame(transformed_data_json)
            st.dataframe(df_transformed)
            st.download_button(
                label="📥 Download Transformed Data as CSV",
                data=convert_df_to_csv(df_transformed),
                file_name="transformed_scintillation_data.csv",
                mime="text/csv",
            )
        
        st.subheader("Combined Raw Data")
        combined_data_json = fetch_data_from_api("data/combined")
        if combined_data_json:
            df_combined = pd.DataFrame(combined_data_json)
            st.dataframe(df_combined)
            st.download_button(
                label="📥 Download Combined Data as CSV",
                data=convert_df_to_csv(df_combined),
                file_name="combined_scintillation_data.csv",
                mime="text/csv",
            )
else:
    st.info("Please upload your data files and click 'Analyze Data' to see the results.")