# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import json
from contextlib import contextmanager, asynccontextmanager
import random
import uvicorn

# Database configuration
DB_NAME = "call_metrics.db"

# Pydantic models
class CallRecord(BaseModel):
    agent_id: str = Field(..., example="AGT001")
    customer_id: str = Field(..., example="CUST123")
    start_time: datetime
    end_time: datetime
    call_outcome: str = Field(..., example="resolved")
    
class CallResponse(BaseModel):
    call_id: int
    agent_id: str
    customer_id: str
    start_time: datetime
    end_time: datetime
    duration: int  # in seconds
    call_outcome: str

class MetricsResponse(BaseModel):
    total_calls: int
    average_duration: float
    calls_by_outcome: dict
    calls_per_hour: List[dict]
    top_agents: List[dict]

# Database context manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                duration INTEGER NOT NULL,
                call_outcome TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_start_time ON calls(start_time);
        ''')
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_id ON calls(agent_id);
        ''')
        conn.commit()

# Generate fake data
def generate_fake_data():
    agents = [f"AGT{str(i).zfill(3)}" for i in range(1, 11)]
    outcomes = ["resolved", "escalated", "dropped", "voicemail", "callback"]
    
    with get_db() as conn:
        # Check if data already exists
        cursor = conn.execute("SELECT COUNT(*) FROM calls")
        if cursor.fetchone()[0] > 0:
            return
        
        # Generate calls for the last 7 days
        base_date = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            current_date = base_date + timedelta(days=day)
            # More calls during business hours (9 AM - 6 PM)
            for hour in range(24):
                if 9 <= hour <= 18:
                    num_calls = random.randint(20, 40)
                else:
                    num_calls = random.randint(0, 10)
                
                for _ in range(num_calls):
                    start_time = current_date.replace(
                        hour=hour, 
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    # Call duration between 30 seconds and 20 minutes
                    duration = random.randint(30, 1200)
                    end_time = start_time + timedelta(seconds=duration)
                    
                    conn.execute('''
                        INSERT INTO calls (agent_id, customer_id, start_time, end_time, duration, call_outcome)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        random.choice(agents),
                        f"CUST{random.randint(1000, 9999)}",
                        start_time.isoformat(),
                        end_time.isoformat(),
                        duration,
                        random.choice(outcomes)
                    ))
        
        conn.commit()

# Initialize FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    generate_fake_data()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Call Metrics API", version="1.0.0", lifespan=lifespan)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Call Metrics API", "version": "1.0.0"}

@app.post("/api/calls", response_model=CallResponse)
async def create_call(call: CallRecord):
    """Record a new call"""
    duration = int((call.end_time - call.start_time).total_seconds())
    
    if duration <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO calls (agent_id, customer_id, start_time, end_time, duration, call_outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            call.agent_id,
            call.customer_id,
            call.start_time.isoformat(),
            call.end_time.isoformat(),
            duration,
            call.call_outcome
        ))
        conn.commit()
        
        # Fetch the created record
        cursor = conn.execute(
            "SELECT * FROM calls WHERE call_id = ?", 
            (cursor.lastrowid,)
        )
        row = cursor.fetchone()
        
        return CallResponse(
            call_id=row['call_id'],
            agent_id=row['agent_id'],
            customer_id=row['customer_id'],
            start_time=datetime.fromisoformat(row['start_time']),
            end_time=datetime.fromisoformat(row['end_time']),
            duration=row['duration'],
            call_outcome=row['call_outcome']
        )

@app.get("/api/calls", response_model=List[CallResponse])
async def get_calls(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    agent_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Retrieve call records with optional filtering"""
    query = "SELECT * FROM calls WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND start_time >= ?"
        params.append(start_date.isoformat())
    
    if end_date:
        query += " AND start_time <= ?"
        params.append(end_date.isoformat())
    
    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)
    
    query += " ORDER BY start_time DESC LIMIT ?"
    params.append(limit)
    
    with get_db() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            CallResponse(
                call_id=row['call_id'],
                agent_id=row['agent_id'],
                customer_id=row['customer_id'],
                start_time=datetime.fromisoformat(row['start_time']),
                end_time=datetime.fromisoformat(row['end_time']),
                duration=row['duration'],
                call_outcome=row['call_outcome']
            )
            for row in rows
        ]

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get aggregated call metrics"""
    # Default to last 24 hours if no dates provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(hours=24)
    
    with get_db() as conn:
        # Total calls and average duration
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_calls,
                AVG(duration) as avg_duration
            FROM calls
            WHERE start_time >= ? AND start_time <= ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        row = cursor.fetchone()
        total_calls = row['total_calls'] or 0
        avg_duration = row['avg_duration'] or 0
        
        # Calls by outcome
        cursor = conn.execute('''
            SELECT call_outcome, COUNT(*) as count
            FROM calls
            WHERE start_time >= ? AND start_time <= ?
            GROUP BY call_outcome
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        calls_by_outcome = {row['call_outcome']: row['count'] for row in cursor.fetchall()}
        
        # Calls per hour
        cursor = conn.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', start_time) as hour,
                COUNT(*) as count
            FROM calls
            WHERE start_time >= ? AND start_time <= ?
            GROUP BY hour
            ORDER BY hour
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        calls_per_hour = [
            {"hour": row['hour'], "count": row['count']} 
            for row in cursor.fetchall()
        ]
        
        # Top agents by call count
        cursor = conn.execute('''
            SELECT 
                agent_id,
                COUNT(*) as call_count,
                AVG(duration) as avg_duration
            FROM calls
            WHERE start_time >= ? AND start_time <= ?
            GROUP BY agent_id
            ORDER BY call_count DESC
            LIMIT 5
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        top_agents = [
            {
                "agent_id": row['agent_id'],
                "call_count": row['call_count'],
                "avg_duration": round(row['avg_duration'], 2)
            }
            for row in cursor.fetchall()
        ]
        
        return MetricsResponse(
            total_calls=total_calls,
            average_duration=round(avg_duration, 2),
            calls_by_outcome=calls_by_outcome,
            calls_per_hour=calls_per_hour,
            top_agents=top_agents
        )

@app.get("/api/agents")
async def get_agents():
    """Get list of all agents"""
    with get_db() as conn:
        cursor = conn.execute("SELECT DISTINCT agent_id FROM calls ORDER BY agent_id")
        return [{"agent_id": row['agent_id']} for row in cursor.fetchall()]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)