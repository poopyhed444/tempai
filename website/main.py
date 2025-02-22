import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="E-Bike Battery Risk Dashboard",
    layout="wide"
)

# Add title and description
st.title("E-Bike Battery Risk Dashboard")
st.markdown("""
This dashboard visualizes the concentration of delivery e-bikes and their associated battery fire risks.
Risk factors include battery age, charging cycles, and temperature exposure.
""")

# Function to generate sample data (replace this with real data)
def generate_sample_data(n_points=100):
    # New York City coordinates (example)
    NYC_CENTER = (40.7128, -74.0060)
    
    data = {
        'latitude': np.random.normal(NYC_CENTER[0], 0.02, n_points),
        'longitude': np.random.normal(NYC_CENTER[1], 0.02, n_points),
        'battery_age_months': np.random.randint(1, 36, n_points),
        'charging_cycles': np.random.randint(50, 1000, n_points),
        'last_inspection_date': [
            datetime.now().date() - pd.Timedelta(days=np.random.randint(0, 365))
            for _ in range(n_points)
        ],
        'delivery_service': np.random.choice(
            ['UberEats', 'GrubHub', 'DoorDash', 'Independent'],
            n_points
        )
    }
    
    # Calculate risk score (0-100)
    data['risk_score'] = np.clip(
        data['battery_age_months'] * 1.5 +
        data['charging_cycles'] * 0.05,
        0, 100
    )
    
    return pd.DataFrame(data)

# Sidebar controls
st.sidebar.header("Filter Options")
selected_service = st.sidebar.multiselect(
    "Delivery Service",
    ["All", "UberEats", "GrubHub", "DoorDash", "Independent"],
    default="All"
)

risk_threshold = st.sidebar.slider(
    "Risk Score Threshold",
    0, 100, 50,
    help="Show e-bikes with risk score above this threshold"
)

# Generate or load data
df = generate_sample_data()

# Filter data based on selections
if "All" not in selected_service:
    df = df[df['delivery_service'].isin(selected_service)]
df = df[df['risk_score'] >= risk_threshold]

# Create the main map
m = folium.Map(
    location=[df['latitude'].mean(), df['longitude'].mean()],
    zoom_start=12
)

# Add heatmap layer
from folium.plugins import HeatMap
heat_data = [[row['latitude'], row['longitude'], row['risk_score']] for idx, row in df.iterrows()]
HeatMap(heat_data, radius=15, blur=10).add_to(m)

# Create two columns for the layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("E-Bike Risk Heatmap")
    folium_static(m)

with col2:
    st.subheader("Risk Statistics")
    
    # Display key metrics
    st.metric(
        "Average Risk Score",
        f"{df['risk_score'].mean():.1f}",
        delta=f"{df['risk_score'].mean() - 50:.1f} from baseline"
    )
    
    st.metric(
        "High Risk Vehicles",
        len(df[df['risk_score'] > 75]),
        help="Number of e-bikes with risk score > 75"
    )
    
    # Add a bar chart of risk distribution by delivery service
    st.subheader("Risk Distribution by Service")
    risk_by_service = df.groupby('delivery_service')['risk_score'].mean()
    st.bar_chart(risk_by_service)
    
    # Add table of highest risk vehicles
    st.subheader("Highest Risk Vehicles")
    high_risk = df.nlargest(10, 'risk_score')[
        ['delivery_service', 'risk_score', 'battery_age_months', 'charging_cycles']
    ]
    st.dataframe(high_risk)

# Footer with additional information
st.markdown("""
---
### Risk Score Calculation
The risk score is calculated based on:
- Battery age (months)
- Number of charging cycles
- Time since last inspection

A score above 75 indicates high risk and requires immediate attention.
""")