import streamlit as st
import fastf1
import plotly.graph_objects as go
import os


# Automatically create the cache folder if it doesn't exist
if not os.path.exists('cache'):
    os.makedirs('cache')

# Enable caching to speed up data loading
fastf1.Cache.enable_cache('cache')

# --- UI Setup (The "Stealth" Engineering Aesthetic) ---
st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")
st.title("🏎️ F1 Qualifying Telemetry Comparison")
st.markdown("Compare driver speeds and throttle traces from real F1 sessions.")

# --- Sidebar Controls ---
st.sidebar.header("Select Session")
year = st.sidebar.selectbox("Year", [2023, 2024])
track = st.sidebar.text_input("Track (e.g., Monza, Silverstone, Spa)", "Monza")
driver1 = st.sidebar.text_input("Driver 1 (3-Letter Code)", "VER").upper()
driver2 = st.sidebar.text_input("Driver 2 (3-Letter Code)", "LEC").upper()

if st.sidebar.button("Load Telemetry"):
    with st.spinner('Downloading F1 Data (This takes a moment on first run)...'):
        try:
            # 1. Load the Qualifying Session
            session = fastf1.get_session(year, track, 'Q')
            session.load()
            
            # 2. Extract Fastest Laps for both drivers
            lap_d1 = session.laps.pick_driver(driver1).pick_fastest()
            lap_d2 = session.laps.pick_driver(driver2).pick_fastest()
            
            # 3. Get Telemetry data and add distance synchronization
            tel_d1 = lap_d1.get_car_data().add_distance()
            tel_d2 = lap_d2.get_car_data().add_distance()

            # --- Data Visualization (Plotly) ---
            st.subheader(f"{driver1} vs {driver2} - {track} {year}")
            
            # Create a multi-line interactive chart
            fig = go.Figure()
            
            # Driver 1 Speed Trace
            fig.add_trace(go.Scatter(x=tel_d1['Distance'], y=tel_d1['Speed'], 
                                     mode='lines', name=f"{driver1} Speed", line=dict(color='blue')))
            # Driver 2 Speed Trace
            fig.add_trace(go.Scatter(x=tel_d2['Distance'], y=tel_d2['Speed'], 
                                     mode='lines', name=f"{driver2} Speed", line=dict(color='red')))

            # Format the chart to look professional
            fig.update_layout(
                title="Speed vs Distance",
                xaxis_title="Distance (meters)",
                yaxis_title="Speed (km/h)",
                template="plotly_dark", # Dark mode for the engineering aesthetic
                height=500
            )
            
            # Render chart in the web app
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading data. Check track spelling or driver codes. Details: {e}")