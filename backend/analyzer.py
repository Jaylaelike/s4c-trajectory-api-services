# backend/analyzer.py

import pandas as pd
import numpy as np
import folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class GPSScintillationAnalyzer:
    def __init__(self):
        self.lat_data = None
        self.lon_data = None
        self.s4c_data = None
        self.combined_data = None
        self.active_satellites = []

    def load_data(self, lat_file, lon_file, s4c_file):
        """Load the three CSV files from file-like objects"""
        self.lat_data = pd.read_csv(lat_file, index_col=0)
        self.lon_data = pd.read_csv(lon_file, index_col=0)
        self.s4c_data = pd.read_csv(s4c_file, index_col=0)

        # Convert index to datetime
        for df in [self.lat_data, self.lon_data, self.s4c_data]:
            df.index = pd.to_datetime(df.index)

        # Find active satellites
        self.active_satellites = [col for col in self.lat_data.columns if self.lat_data[col].notna().any()]

    def merge_data(self):
        """Merge latitude, longitude, and S4C data into a single DataFrame"""
        merged_records = []
        for timestamp in self.lat_data.index:
            for satellite in self.active_satellites:
                lat = self.lat_data.loc[timestamp, satellite]
                lon = self.lon_data.loc[timestamp, satellite]
                s4c = self.s4c_data.loc[timestamp, satellite]

                if pd.notna(lat) and pd.notna(lon) and pd.notna(s4c):
                    merged_records.append({
                        'timestamp': timestamp,
                        'satellite': satellite,
                        'latitude': lat,
                        'longitude': lon,
                        's4c': s4c,
                    })
        self.combined_data = pd.DataFrame(merged_records)
        return self.combined_data
    
    def transform_to_new_format(self):
        """Transforms the combined DataFrame into the specified format with validation."""
        if self.combined_data is None or self.combined_data.empty:
            return pd.DataFrame(columns=['Satellite', 'Time', 'S4C', 'Lat', 'Lon'])
        
        # Create a copy and validate required columns exist
        required_columns = ['satellite', 'timestamp', 's4c', 'latitude', 'longitude']
        if not all(col in self.combined_data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in self.combined_data.columns]
            raise ValueError(f"Missing required columns: {missing}")
        
        new_df = self.combined_data[required_columns].copy()
        
        # Remove any rows with NaN values in critical columns
        new_df = new_df.dropna()
        
        # Rename columns to the specified format
        new_df.rename(columns={
            'satellite': 'Satellite',
            'timestamp': 'Time',
            's4c': 'S4C',
            'latitude': 'Lat',
            'longitude': 'Lon'
        }, inplace=True)
        
        # Format timestamp and round numeric values
        new_df['Time'] = new_df['Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        new_df['S4C'] = new_df['S4C'].round(6)
        new_df['Lat'] = new_df['Lat'].round(6)
        new_df['Lon'] = new_df['Lon'].round(6)
        
        return new_df

    def analyze_statistics(self):
        """Perform statistical analysis and return as DataFrames"""
        if self.combined_data is None:
            return None, None
            
        sat_stats = self.combined_data.groupby('satellite')['s4c'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(6).reset_index()

        temporal_stats = self.combined_data.set_index('timestamp').groupby(pd.Grouper(freq='1min'))['s4c'].agg([
            'count', 'mean', 'std'
        ]).round(6).reset_index()
        
        return sat_stats, temporal_stats

    def create_interactive_map(self):
        """Create and return interactive Folium map HTML"""
        if self.combined_data is None or self.combined_data.empty:
            return "<h3>No data to display on map.</h3>"

        center_lat = self.combined_data['latitude'].mean()
        center_lon = self.combined_data['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles='CartoDB positron')

        s4c_min, s4c_max = self.combined_data['s4c'].min(), self.combined_data['s4c'].max()

        def get_color(s4c_value):
            norm_value = (s4c_value - s4c_min) / (s4c_max - s4c_min) if (s4c_max - s4c_min) > 0 else 0
            if norm_value < 0.25: return '#440154'
            elif norm_value < 0.5: return '#31688e'
            elif norm_value < 0.75: return '#35b779'
            else: return '#fde725'

        for _, row in self.combined_data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=f"Sat: {row['satellite']}<br>S4C: {row['s4c']:.4f}",
                color=get_color(row['s4c']),
                fill=True,
                fill_opacity=0.7
            ).add_to(m)
        
        return m._repr_html_()

    def create_plotly_dashboard(self):
        """Create and return interactive Plotly dashboard figure"""
        if self.combined_data is None or self.combined_data.empty:
            return go.Figure()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('S4C Time Series', 'Geographic Distribution', 'S4C Distribution', 'Satellite Comparison'),
            specs=[[{}, {"type": "scattergeo"}], [{"type": "histogram"}, {"type": "box"}]]
        )

        for satellite in self.active_satellites:
            sat_data = self.combined_data[self.combined_data['satellite'] == satellite]
            fig.add_trace(go.Scatter(x=sat_data['timestamp'], y=sat_data['s4c'], mode='lines+markers', name=satellite), row=1, col=1)

        fig.add_trace(go.Scattergeo(
            lon=self.combined_data['longitude'], lat=self.combined_data['latitude'], mode='markers',
            marker=dict(size=5, color=self.combined_data['s4c'], colorscale='Plasma', colorbar=dict(title="S4C")),
            text=self.combined_data.apply(lambda r: f"Sat: {r['satellite']}<br>S4C: {r['s4c']:.4f}", axis=1),
            hoverinfo='text', showlegend=False
        ), row=1, col=2)

        fig.add_trace(go.Histogram(x=self.combined_data['s4c'], name='S4C Dist', showlegend=False), row=2, col=1)
        
        for satellite in self.active_satellites:
            fig.add_trace(go.Box(y=self.combined_data[self.combined_data['satellite'] == satellite]['s4c'], name=satellite, showlegend=False), row=2, col=2)

        fig.update_layout(title_text="GPS Scintillation Analysis Dashboard", height=800, margin=dict(l=20, r=20, t=60, b=20))
        fig.update_geos(projection_type="mercator", showland=True, landcolor="lightgray", showocean=True, oceancolor="lightblue")
        
        return fig
    
    def create_transformed_data_response(self):
        """Create a comprehensive response structure for transformed data results"""
        if self.combined_data is None:
            return {
                "status": "error",
                "message": "No data available. Please load and merge data first.",
                "data": None,
                "metadata": None
            }
        
        # Get transformed data
        transformed_df = self.transform_to_new_format()
        
        # Calculate metadata and summary statistics
        metadata = {
            "total_records": len(transformed_df),
            "unique_satellites": transformed_df['Satellite'].nunique(),
            "satellite_list": sorted(transformed_df['Satellite'].unique().tolist()),
            "time_range": {
                "start": transformed_df['Time'].min() if not transformed_df.empty else None,
                "end": transformed_df['Time'].max() if not transformed_df.empty else None
            },
            "s4c_statistics": {
                "min": float(transformed_df['S4C'].min()) if not transformed_df.empty else None,
                "max": float(transformed_df['S4C'].max()) if not transformed_df.empty else None,
                "mean": float(transformed_df['S4C'].mean()) if not transformed_df.empty else None,
                "std": float(transformed_df['S4C'].std()) if not transformed_df.empty else None
            },
            "geographic_bounds": {
                "lat_min": float(transformed_df['Lat'].min()) if not transformed_df.empty else None,
                "lat_max": float(transformed_df['Lat'].max()) if not transformed_df.empty else None,
                "lon_min": float(transformed_df['Lon'].min()) if not transformed_df.empty else None,
                "lon_max": float(transformed_df['Lon'].max()) if not transformed_df.empty else None
            }
        }
        
        # Create response structure
        response = {
            "status": "success",
            "message": "Data transformation completed successfully",
            "data": {
                "records": transformed_df.to_dict(orient='records'),
                "format": {
                    "columns": ["Satellite", "Time", "S4C", "Lat", "Lon"],
                    "column_descriptions": {
                        "Satellite": "Satellite identifier",
                        "Time": "Timestamp in YYYY-MM-DD HH:MM:SS format",
                        "S4C": "Scintillation index value",
                        "Lat": "Latitude coordinate",
                        "Lon": "Longitude coordinate"
                    }
                }
            },
            "metadata": metadata,
            "processing_info": {
                "transformation_applied": "GPS scintillation data merged and reformatted",
                "processing_timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                "data_quality": {
                    "complete_records": len(transformed_df),
                    "data_coverage": f"{len(transformed_df) / (len(self.active_satellites) * len(self.lat_data)) * 100:.2f}%" if self.active_satellites and not self.lat_data.empty else "0%"
                }
            }
        }
        
        return response

    def get_processing_summary(self):
        """Get a summary of the data processing results"""
        if self.combined_data is None:
            return {
                "status": "no_data",
                "message": "No data has been processed yet"
            }
        
        transformed_df = self.transform_to_new_format()
        
        # Calculate data quality metrics
        total_possible_records = len(self.active_satellites) * len(self.lat_data) if self.active_satellites and not self.lat_data.empty else 0
        actual_records = len(transformed_df)
        data_completeness = (actual_records / total_possible_records * 100) if total_possible_records > 0 else 0
        
        # Analyze S4C value ranges
        s4c_ranges = {
            "low": len(transformed_df[transformed_df['S4C'] < 0.2]) if not transformed_df.empty else 0,
            "moderate": len(transformed_df[(transformed_df['S4C'] >= 0.2) & (transformed_df['S4C'] < 0.5)]) if not transformed_df.empty else 0,
            "high": len(transformed_df[transformed_df['S4C'] >= 0.5]) if not transformed_df.empty else 0
        }
        
        summary = {
            "processing_status": "completed",
            "data_overview": {
                "total_records": actual_records,
                "unique_satellites": len(self.active_satellites),
                "data_completeness_percentage": round(data_completeness, 2),
                "time_span_minutes": self._calculate_time_span_minutes(transformed_df) if not transformed_df.empty else 0
            },
            "scintillation_analysis": {
                "s4c_value_distribution": s4c_ranges,
                "dominant_activity_level": self._get_dominant_activity_level(s4c_ranges),
                "average_s4c": round(float(transformed_df['S4C'].mean()), 6) if not transformed_df.empty else 0
            },
            "spatial_coverage": {
                "latitude_range": round(float(transformed_df['Lat'].max() - transformed_df['Lat'].min()), 4) if not transformed_df.empty else 0,
                "longitude_range": round(float(transformed_df['Lon'].max() - transformed_df['Lon'].min()), 4) if not transformed_df.empty else 0
            }
        }
        
        return summary
    
    def _calculate_time_span_minutes(self, df):
        """Calculate time span in minutes"""
        if df.empty:
            return 0
        time_series = pd.to_datetime(df['Time'])
        return round((time_series.max() - time_series.min()).total_seconds() / 60, 2)
    
    def _get_dominant_activity_level(self, s4c_ranges):
        """Determine the dominant scintillation activity level"""
        max_count = max(s4c_ranges.values())
        for level, count in s4c_ranges.items():
            if count == max_count:
                return level
        return "unknown"