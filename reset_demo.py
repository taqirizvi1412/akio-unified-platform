# reset_demo.py
import os
import shutil
import sqlite3
import json
from datetime import datetime, timedelta
import random

def reset_email_assistant():
    """Reset Email Assistant to fresh state with sample data"""
    print("🔄 Resetting Email Assistant...")
    
    # Remove existing data files
    files_to_remove = ['email_responses.json', 'email_analytics.json', 'templates.json']
    for file in files_to_remove:
        path = os.path.join('Email-Assistant', file)
        if os.path.exists(path):
            os.remove(path)
            print(f"  ✅ Removed {file}")
    
    # Create sample templates
    templates = {
        "templates": [
            {
                "id": "welcome_001",
                "name": "Welcome Email",
                "language": "en",
                "template": "Dear {customer_name},\n\nWelcome to Akio! We're thrilled to have you as our customer.\n\nBest regards,\nThe Akio Team",
                "category": "onboarding"
            },
            {
                "id": "followup_001",
                "name": "Call Follow-up",
                "language": "en",
                "template": "Hi {customer_name},\n\nThank you for your call today. As discussed, {action_items}.\n\nPlease don't hesitate to reach out if you need anything else.\n\nBest regards,\n{agent_name}",
                "category": "followup"
            },
            {
                "id": "apology_001",
                "name": "Service Apology",
                "language": "en",
                "template": "Dear {customer_name},\n\nWe sincerely apologize for {issue}. We value your business and are taking immediate steps to resolve this.\n\nAs a gesture of goodwill, {compensation}.\n\nSincerely,\nThe Akio Team",
                "category": "apology"
            }
        ]
    }
    
    with open(os.path.join('Email-Assistant', 'templates.json'), 'w') as f:
        json.dump(templates, f, indent=2)
    print("  ✅ Created sample templates")

def reset_call_metrics():
    """Reset Call Metrics with fresh demo data"""
    print("🔄 Resetting Call Metrics...")
    
    db_path = os.path.join('Call-System', 'call_metrics.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("  ✅ Removed old database")
    
    # Create new database with demo data
    conn = sqlite3.connect(db_path)
    
    # Create table
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
    
    # Generate demo data for today
    agents = ['AGT001', 'AGT002', 'AGT003', 'AGT004', 'AGT005']
    outcomes = ['resolved', 'escalated', 'callback', 'voicemail']
    
    now = datetime.now()
    today_start = now.replace(hour=9, minute=0, second=0)
    
    # Add some calls for today
    for i in range(15):
        start_time = today_start + timedelta(minutes=random.randint(0, 480))
        duration = random.randint(120, 900)  # 2-15 minutes
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
    conn.close()
    print("  ✅ Created demo call data")

def reset_crm_integration():
    """Reset CRM Integration data"""
    print("🔄 Resetting CRM Integration...")
    
    # Remove data directory
    data_path = os.path.join('crm-integration-prototype', 'data')
    if os.path.exists(data_path):
        shutil.rmtree(data_path)
        print("  ✅ Removed CRM data")
    
    # Create fresh data directory
    os.makedirs(data_path, exist_ok=True)
    
    # Create sample contacts
    contacts = {
        "contacts": [
            {
                "id": "contact_001",
                "email": "john.doe@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "phone": "+1234567890",
                "company": "Acme Corp",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "contact_002",
                "email": "jane.smith@example.com",
                "firstname": "Jane",
                "lastname": "Smith",
                "phone": "+0987654321",
                "company": "Tech Solutions",
                "created_at": datetime.now().isoformat()
            }
        ]
    }
    
    with open(os.path.join(data_path, 'contacts.json'), 'w') as f:
        json.dump(contacts, f, indent=2)
    print("  ✅ Created sample CRM data")

def main():
    print("🧹 Akio Platform Demo Reset Tool")
    print("================================")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('unified_platform.py'):
        print("❌ Error: Please run this script from the Akio-stage directory")
        return
    
    # Reset each component
    try:
        reset_email_assistant()
        reset_call_metrics()
        reset_crm_integration()
        
        print()
        print("✅ All demo data has been reset successfully!")
        print("📌 Your platform is ready for a fresh demonstration")
        
    except Exception as e:
        print(f"❌ Error during reset: {str(e)}")

if __name__ == "__main__":
    main()