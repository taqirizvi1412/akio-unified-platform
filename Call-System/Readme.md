# Call Metrics API with Visualization Dashboard

A real-time call center performance monitoring system featuring a FastAPI backend and Streamlit visualization dashboard for tracking, analyzing, and optimizing call center operations.

## 🎯 Overview

This application provides a complete call center analytics solution with:
- RESTful API for call data management
- Real-time performance dashboards
- Automatic test data generation
- Interactive visualizations with 30-second auto-refresh
- Agent performance tracking
- Call outcome analysis

## 🏗️ Architecture

```
┌─────────────────┐     HTTP Requests    ┌──────────────────┐
│                 │ ◄──────────────────► │                  │
│  FastAPI Backend│                      │Streamlit Frontend│
│   (Port 8000)   │                      │  (Port 8501)     │
│                 │                      │                  │
└────────┬────────┘                      └──────────────────┘
         │
         ▼
   ┌──────────┐
   │  SQLite  │
   │ Database │
   └──────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd call-metrics-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn streamlit pandas plotly requests
   ```

3. **Start the backend API**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

4. **Start the dashboard** (in a new terminal)
   ```bash
   streamlit run dashboard.py
   ```
   The dashboard will open at `http://localhost:8501`

## 📊 Features

### Backend API Features

- **Automatic Database Setup**: Creates SQLite database with optimized indexes
- **Test Data Generation**: Populates 7 days of realistic call center data
- **RESTful Endpoints**: Full CRUD operations for call management
- **Aggregated Metrics**: Pre-calculated KPIs for dashboard performance
- **Flexible Filtering**: Date range and agent-specific queries

### Dashboard Features

- **Real-time Metrics**: 4 key performance indicators updated every 30 seconds
- **Interactive Charts**: 
  - Hourly call volume trends
  - Call outcome distribution
  - Agent performance rankings
- **Flexible Filtering**: Date/time range and agent selection
- **Auto-refresh Toggle**: Choose between automatic and manual updates
- **Detailed Call Records**: Expandable table view of individual calls

## 🔧 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Create Call
```http
POST /api/calls
Content-Type: application/json

{
  "agent_id": "agent_001",
  "customer_id": "cust_123",
  "start_time": "2024-03-15T10:30:00",
  "end_time": "2024-03-15T10:45:00",
  "outcome": "resolved"
}
```

#### 2. Get Calls
```http
GET /api/calls?start_date=2024-03-15&end_date=2024-03-16&agent_id=agent_001&limit=100
```

#### 3. Get Metrics
```http
GET /api/metrics?start_date=2024-03-15&end_date=2024-03-16&agent_id=agent_001
```

Response includes:
- Summary statistics (total calls, average duration, resolution rate)
- Hourly call distribution
- Outcome breakdown
- Agent performance metrics

#### 4. Get Agents
```http
GET /api/agents
```

## 📈 Dashboard Components

### 1. Key Performance Indicators (KPIs)
- **Total Calls**: Volume of customer interactions
- **Average Duration**: Mean call handling time
- **Resolution Rate**: Percentage of successfully resolved calls
- **Peak Hour**: Busiest hour of the day

### 2. Visualizations

#### Calls Per Hour (Line Chart)
- Shows call volume trends throughout the day
- Smooth spline interpolation for better readability
- Identifies peak and off-peak hours

#### Call Outcomes (Donut Chart)
- Visual breakdown of call results:
  - ✅ Resolved
  - ⚡ Escalated
  - 📞 Dropped
  - 📮 Voicemail
  - 🔄 Callback

#### Agent Performance (Bar Chart)
- Ranks agents by call volume
- Color gradient highlighting top performers
- Helps identify training needs

### 3. Filters & Controls
- **Date Range**: Select start and end dates
- **Time Range**: Specific hour selection
- **Agent Filter**: Focus on individual performance
- **Auto-refresh**: Toggle 30-second updates
- **Manual Refresh**: Instant data update button

## 💾 Database Schema

### Calls Table
```sql
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    outcome TEXT NOT NULL
);

CREATE INDEX idx_calls_start_time ON calls(start_time);
CREATE INDEX idx_calls_agent_id ON calls(agent_id);
```

## 🛠️ Configuration

### Backend Configuration (main.py)
```python
# Server settings
HOST = "localhost"
PORT = 8000

# Database
DATABASE_URL = "calls.db"

# Test data generation
NUM_AGENTS = 10
DAYS_OF_DATA = 7
CALLS_PER_DAY = 200-500
```

### Frontend Configuration (dashboard.py)
```python
# API endpoint
API_BASE_URL = "http://localhost:8000"

# Refresh settings
AUTO_REFRESH_INTERVAL = 30  # seconds

# Display settings
PAGE_LAYOUT = "wide"
THEME = "dark"
```

## 📦 Data Flow

1. **Phone System** → Call completion triggers API
2. **FastAPI** → Validates and stores call record
3. **SQLite** → Persists data with indexes
4. **API Endpoints** → Aggregate and serve metrics
5. **Streamlit** → Fetch and visualize data
6. **Dashboard** → Display insights to managers

## 🚦 Development Guide

### Adding New Metrics
1. Update the `/api/metrics` endpoint in `main.py`
2. Add calculation logic to the SQL queries
3. Update the dashboard to display new metrics

### Customizing Visualizations
1. Modify Plotly chart configurations in `dashboard.py`
2. Adjust color schemes, layouts, and interactivity
3. Add new chart types as needed

### Extending the API
1. Add new endpoints to `main.py`
2. Update database schema if needed
3. Document new endpoints in this README

## 🐛 Troubleshooting

### Common Issues

1. **"Connection refused" error**
   - Ensure the backend is running on port 8000
   - Check firewall settings

2. **Empty dashboard**
   - Verify database has been initialized
   - Check date filters aren't excluding all data

3. **Slow performance**
   - Ensure database indexes are created
   - Consider implementing pagination for large datasets

### Debug Mode
```bash
# Run FastAPI with debug logging
uvicorn main:app --reload --log-level debug

# Run Streamlit with debug info
streamlit run dashboard.py --logger.level debug
```

## 🚀 Production Deployment

### Backend Deployment
1. Use production ASGI server:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. Configure environment variables:
   ```bash
   export DATABASE_URL="postgresql://user:pass@host/db"
   export API_KEY="your-secret-key"
   ```

3. Set up reverse proxy (Nginx/Apache)

### Frontend Deployment
1. Configure Streamlit for production:
   ```toml
   # .streamlit/config.toml
   [server]
   headless = true
   port = 8501
   enableCORS = false
   ```

2. Use process manager (PM2/systemd)

### Database Migration
For production, migrate from SQLite to PostgreSQL:
```python
# Update connection string
DATABASE_URL = "postgresql://user:password@localhost/callcenter"
```

## 📋 Best Practices

1. **Regular Backups**: Schedule daily database backups
2. **Performance Monitoring**: Track API response times
3. **Data Retention**: Implement archival for old call records
4. **Security**: Add authentication to both API and dashboard
5. **Scalability**: Consider caching frequently accessed metrics

## 🔒 Security Considerations

- Add API authentication (JWT tokens)
- Implement role-based access control
- Use HTTPS in production
- Sanitize all user inputs
- Log access for audit trails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for rapid dashboard development
- Plotly for interactive visualizations
- SQLite for lightweight database management

---

**Version**: 1.0.0  
**Last Updated**: June 2025  
**Documentation**: [API Docs](http://localhost:8000/docs) | [Support](mailto:support@example.com)