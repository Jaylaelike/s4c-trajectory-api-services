# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

from analyzer import GPSScintillationAnalyzer

app = FastAPI(
    title="GPS Scintillation Analysis API",
    description="Processes GPS data files to analyze scintillation.",
    version="1.0.0"
)

# Define the origins that are allowed to connect to this backend.
# This includes the Streamlit app running on the host machine.
origins = [
    "http://localhost",
    "http://localhost:8501",
]

# Allow CORS for the Streamlit app to connect
# Add the CORS middleware to the FastAPI application.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)
# A simple in-memory cache to store the results of the last analysis
cache = {}

@app.post("/analyze/", tags=["Analysis"])
async def analyze_files(
    s4c_file: UploadFile = File(..., description="S4C data CSV file"),
    lat_file: UploadFile = File(..., description="Latitude data CSV file"),
    lon_file: UploadFile = File(..., description="Longitude data CSV file"),
):
    """
    Upload three CSV files, run the full analysis, and cache the results.
    """
    try:
        analyzer = GPSScintillationAnalyzer()
        
        # The .file attribute is a file-like object
        analyzer.load_data(lat_file.file, lon_file.file, s4c_file.file)
        
        # Store results in the cache
        cache["combined_data"] = analyzer.merge_data()
        cache["transformed_data"] = analyzer.transform_to_new_format()
        cache["sat_stats"], cache["temporal_stats"] = analyzer.analyze_statistics()
        cache["plotly_fig"] = analyzer.create_plotly_dashboard()
        cache["folium_map_html"] = analyzer.create_interactive_map()
        cache["analyzer_instance"] = analyzer  # Cache the analyzer instance for later use
        
        # Get the transformed data response
        transformed_response = analyzer.create_transformed_data_response()
        
        return {
            "message": "Files processed successfully. Results are now available via GET endpoints.",
            "analysis_complete": True,
            "transformed_data_result": transformed_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")


def get_cached_item(key: str):
    """Helper to get an item from cache or raise 404."""
    if key not in cache:
        raise HTTPException(status_code=404, detail=f"No data found. Please run the analysis first by POSTing to /analyze/.")
    return cache[key]

@app.get("/data/combined", tags=["Data"])
async def get_combined_data():
    """Returns the main combined dataset as JSON."""
    df = get_cached_item("combined_data")
    return JSONResponse(content=df.to_dict(orient='records'))

@app.get("/data/transformed", tags=["Data"])
async def get_transformed_data():
    """Returns the data in the 'Satellite, Time, S4C, Lat, Lon' format."""
    df = get_cached_item("transformed_data")
    return JSONResponse(content=df.to_dict(orient='records'))

@app.get("/data/transformed-response", tags=["Data"])
async def get_transformed_data_response():
    """Returns the transformed data with comprehensive response structure including metadata and processing info."""
    # Check if we have cached analyzer instance or need to recreate it
    if "analyzer_instance" not in cache:
        raise HTTPException(status_code=404, detail="No analysis results found. Please run the analysis first by POSTing to /analyze/.")
    
    analyzer = cache["analyzer_instance"]
    response = analyzer.create_transformed_data_response()
    return JSONResponse(content=response)

@app.get("/stats/satellite", tags=["Statistics"])
async def get_satellite_stats():
    """Returns S4C statistics grouped by satellite."""
    df = get_cached_item("sat_stats")
    return JSONResponse(content=df.to_dict(orient='records'))

@app.get("/stats/temporal", tags=["Statistics"])
async def get_temporal_stats():
    """Returns S4C statistics grouped by time."""
    df = get_cached_item("temporal_stats")
    return JSONResponse(content=df.to_dict(orient='records'))

@app.get("/plots/plotly", tags=["Plots"])
async def get_plotly_dashboard():
    """Returns the Plotly dashboard figure as a JSON object."""
    fig = get_cached_item("plotly_fig")
    return JSONResponse(content=json.loads(fig.to_json()))

@app.get("/plots/folium", response_class=HTMLResponse, tags=["Plots"])
async def get_folium_map():
    """Returns the Folium map as an HTML response."""
    html_content = get_cached_item("folium_map_html")
    return HTMLResponse(content=html_content)

@app.get("/analysis/summary", tags=["Analysis"])
async def get_processing_summary():
    """Returns a summary of the data processing and analysis results."""
    if "analyzer_instance" not in cache:
        raise HTTPException(status_code=404, detail="No analysis results found. Please run the analysis first by POSTing to /analyze/.")
    
    analyzer = cache["analyzer_instance"]
    summary = analyzer.get_processing_summary()
    return JSONResponse(content=summary)

@app.get("/analysis/complete-report", tags=["Analysis"])
async def get_complete_analysis_report():
    """Returns a comprehensive analysis report with all processed data and insights."""
    if "analyzer_instance" not in cache:
        raise HTTPException(status_code=404, detail="No analysis results found. Please run the analysis first by POSTing to /analyze/.")
    
    analyzer = cache["analyzer_instance"]
    
    # Get all components
    transformed_response = analyzer.create_transformed_data_response()
    processing_summary = analyzer.get_processing_summary()
    
    # Get statistics
    sat_stats = get_cached_item("sat_stats")
    temporal_stats = get_cached_item("temporal_stats")
    
    # Create comprehensive report
    report = {
        "report_metadata": {
            "generated_at": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "report_type": "GPS Scintillation Analysis Complete Report",
            "version": "1.0"
        },
        "processing_summary": processing_summary,
        "transformed_data": transformed_response,
        "statistical_analysis": {
            "satellite_statistics": sat_stats.to_dict(orient='records'),
            "temporal_statistics": temporal_stats.to_dict(orient='records')
        },
        "endpoints_available": {
            "transformed_data": "/data/transformed-response",
            "processing_summary": "/analysis/summary",
            "satellite_stats": "/stats/satellite",
            "temporal_stats": "/stats/temporal",
            "plotly_dashboard": "/plots/plotly",
            "folium_map": "/plots/folium"
        }
    }
    
    return JSONResponse(content=report)