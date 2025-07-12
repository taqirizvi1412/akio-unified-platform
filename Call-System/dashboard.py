# dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Call Metrics Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .plot-container {
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state for auto-refresh
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# Title
st.title("📞 Call Metrics Dashboard")
st.markdown("Real-time monitoring of call center performance")

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=1),
            max_value=datetime.now()
        )
        start_time = st.time_input("Start Time", value=datetime.now().time())
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
        end_time = st.time_input("End Time", value=datetime.now().time())
    
    # Combine date and time
    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)
    
    # Agent filter
    try:
        agents_response = requests.get(f"{API_BASE_URL}/api/agents")
        if agents_response.status_code == 200:
            agents = [agent['agent_id'] for agent in agents_response.json()]
            agent_filter = st.selectbox(
                "Filter by Agent",
                options=["All Agents"] + agents
            )
        else:
            agent_filter = "All Agents"
    except:
        agent_filter = "All Agents"
        st.error("Could not load agents list")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

# Function to fetch metrics from API
@st.cache_data(ttl=30)
def fetch_metrics(start_dt, end_dt):
    try:
        params = {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat()
        }
        response = requests.get(f"{API_BASE_URL}/api/metrics", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return None

# Fetch data
metrics = fetch_metrics(start_datetime, end_datetime)

if metrics:
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📞 Total Calls",
            value=f"{metrics['total_calls']:,}",
            delta=None
        )
    
    with col2:
        avg_duration_minutes = metrics['average_duration'] / 60
        st.metric(
            label="⏱️ Avg Duration",
            value=f"{avg_duration_minutes:.1f} min",
            delta=None
        )
    
    with col3:
        resolved_calls = metrics['calls_by_outcome'].get('resolved', 0)
        resolution_rate = (resolved_calls / metrics['total_calls'] * 100) if metrics['total_calls'] > 0 else 0
        st.metric(
            label="✅ Resolution Rate",
            value=f"{resolution_rate:.1f}%",
            delta=None
        )
    
    with col4:
        # Find peak hour
        if metrics['calls_per_hour']:
            peak_hour_data = max(metrics['calls_per_hour'], key=lambda x: x['count'])
            peak_hour = datetime.fromisoformat(peak_hour_data['hour']).strftime("%I %p")
            st.metric(
                label="📈 Peak Hour",
                value=peak_hour,
                delta=f"{peak_hour_data['count']} calls"
            )
        else:
            st.metric(label="📈 Peak Hour", value="N/A")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Calls Per Hour")
        if metrics['calls_per_hour']:
            # Prepare data for line chart
            df_hourly = pd.DataFrame(metrics['calls_per_hour'])
            df_hourly['hour'] = pd.to_datetime(df_hourly['hour'])
            
            fig = px.line(
                df_hourly, 
                x='hour', 
                y='count',
                title=None,
                labels={'count': 'Number of Calls', 'hour': 'Time'},
                line_shape='spline'
            )
            fig.update_traces(line_color='#00d4ff', line_width=3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_gridcolor='rgba(255,255,255,0.1)',
                yaxis_gridcolor='rgba(255,255,255,0.1)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data available")
    
    with col2:
        st.subheader("🎯 Call Outcomes")
        if metrics['calls_by_outcome']:
            # Prepare data for pie chart
            outcomes_df = pd.DataFrame(
                list(metrics['calls_by_outcome'].items()),
                columns=['Outcome', 'Count']
            )
            
            # Define colors for outcomes
            color_map = {
                'resolved': '#00d4ff',
                'escalated': '#ff6b6b',
                'dropped': '#ffa500',
                'voicemail': '#9370db',
                'callback': '#32cd32'
            }
            colors = [color_map.get(outcome, '#666') for outcome in outcomes_df['Outcome']]
            
            fig = go.Figure(data=[go.Pie(
                labels=outcomes_df['Outcome'],
                values=outcomes_df['Count'],
                hole=0.4,
                marker_colors=colors
            )])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No outcome data available")
    
    # Top Agents Section
    st.subheader("🏆 Top Performing Agents")
    if metrics['top_agents']:
        agents_df = pd.DataFrame(metrics['top_agents'])
        agents_df['avg_duration_min'] = agents_df['avg_duration'] / 60
        agents_df['rank'] = range(1, len(agents_df) + 1)
        
        # Create a more detailed agents table
        for idx, agent in agents_df.iterrows():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                st.markdown(f"### #{agent['rank']}")
            with col2:
                st.markdown(f"**{agent['agent_id']}**")
            with col3:
                st.markdown(f"📞 {agent['call_count']} calls")
            with col4:
                st.markdown(f"⏱️ {agent['avg_duration_min']:.1f} min avg")
        
        # Bar chart for agent performance
        st.subheader("📊 Agent Call Volume")
        fig = px.bar(
            agents_df,
            x='agent_id',
            y='call_count',
            title=None,
            labels={'call_count': 'Number of Calls', 'agent_id': 'Agent'},
            color='call_count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_gridcolor='rgba(255,255,255,0.1)',
            yaxis_gridcolor='rgba(255,255,255,0.1)',
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No agent data available")
    
    # Call Details Table (Optional)
    with st.expander("📋 View Recent Calls"):
        try:
            params = {
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "limit": 50
            }
            if agent_filter != "All Agents":
                params["agent_id"] = agent_filter
            
            calls_response = requests.get(f"{API_BASE_URL}/api/calls", params=params)
            if calls_response.status_code == 200:
                calls_data = calls_response.json()
                if calls_data:
                    calls_df = pd.DataFrame(calls_data)
                    calls_df['start_time'] = pd.to_datetime(calls_df['start_time'])
                    calls_df['duration_min'] = calls_df['duration'] / 60
                    
                    # Display formatted table
                    display_df = calls_df[['call_id', 'agent_id', 'customer_id', 'start_time', 'duration_min', 'call_outcome']]
                    display_df.columns = ['Call ID', 'Agent', 'Customer', 'Start Time', 'Duration (min)', 'Outcome']
                    display_df['Duration (min)'] = display_df['Duration (min)'].round(1)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No calls found for the selected criteria")
        except Exception as e:
            st.error(f"Failed to load call details: {str(e)}")

else:
    st.error("Unable to load metrics. Please check if the API is running at http://localhost:8000")

# Auto-refresh logic
if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Call Metrics Dashboard | Auto-refreshes every 30 seconds | 
        <a href='http://localhost:8000/docs' target='_blank'>API Docs</a>
    </div>
    """,
    unsafe_allow_html=True
)