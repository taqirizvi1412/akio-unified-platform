# demo_mode.py
import json
import sqlite3
import os
from datetime import datetime, timedelta
import random
import streamlit as st
import time

class DemoModeManager:
    """Manages demo mode for presentations with interconnected data"""
    
    def __init__(self):
        self.email_path = "Email-Assistant"
        self.call_db_path = os.path.join("Call-System", "call_metrics.db")
        self.crm_data_path = os.path.join("crm-integration-prototype", "data")
        
        # Shared customer data for consistency across services
        self.demo_customers = [
            {
                "id": "CUST001",
                "email": "sarah.johnson@techcorp.com",
                "name": "Sarah Johnson",
                "phone": "+1-555-0123",
                "company": "TechCorp Solutions",
                "type": "VIP"
            },
            {
                "id": "CUST002",
                "email": "miguel.rodriguez@globalimports.com",
                "name": "Miguel Rodriguez",
                "phone": "+1-555-0124",
                "company": "Global Imports LLC",
                "type": "Regular"
            },
            {
                "id": "CUST003",
                "email": "emma.chen@innovate.io",
                "name": "Emma Chen",
                "phone": "+1-555-0125",
                "company": "Innovate.io",
                "type": "VIP"
            }
        ]
        
        self.demo_scenarios = [
            {
                "customer_id": 0,
                "email_subject": "Urgent: Order #12345 Delayed - Need Update",
                "email_body": "I placed an order 5 days ago and it still hasn't shipped. This is unacceptable for a VIP customer. I need immediate resolution.",
                "sentiment": "negative",
                "priority": "high",
                "call_outcome": "escalated",
                "call_duration": 720
            },
            {
                "customer_id": 1,
                "email_subject": "Request for Bulk Discount",
                "email_body": "We're interested in placing a large order of 500 units. Can you provide bulk pricing? We've been happy with your service.",
                "sentiment": "positive",
                "priority": "medium",
                "call_outcome": "resolved",
                "call_duration": 480
            },
            {
                "customer_id": 2,
                "email_subject": "Technical Issue with API Integration",
                "email_body": "We're experiencing intermittent failures with the API. Error code 503. This is affecting our production environment.",
                "sentiment": "neutral",
                "priority": "high",
                "call_outcome": "resolved",
                "call_duration": 1200
            }
        ]
    
    def activate_demo_mode(self):
        """Populate all services with interconnected demo data"""
        print("🎭 Activating Demo Mode...")
        
        # Clear existing data
        self._clear_existing_data()
        
        # Populate services with interconnected data
        self._populate_emails()
        self._populate_calls()
        self._populate_crm()
        
        print("✅ Demo Mode activated! All services populated with sample data.")
        return True
    
    def _clear_existing_data(self):
        """Clear existing data from all services"""
        # Clear email data
        for file in ['email_responses.json', 'email_analytics.json']:
            path = os.path.join(self.email_path, file)
            if os.path.exists(path):
                os.remove(path)
        
        # Clear call database
        if os.path.exists(self.call_db_path):
            conn = sqlite3.connect(self.call_db_path)
            conn.execute("DELETE FROM calls")
            conn.commit()
            conn.close()
        
        # Clear CRM data
        contacts_path = os.path.join(self.crm_data_path, "contacts.json")
        if os.path.exists(contacts_path):
            os.remove(contacts_path)
    
    def _populate_emails(self):
        """Populate email system with demo emails"""
        responses = {"responses": []}
        
        for idx, scenario in enumerate(self.demo_scenarios):
            customer = self.demo_customers[scenario["customer_id"]]
            
            response = {
                "id": f"email_{idx+1:03d}",
                "timestamp": (datetime.now() - timedelta(hours=idx*2)).isoformat(),
                "customer_email": customer["email"],
                "customer_name": customer["name"],
                "original_email": f"Subject: {scenario['email_subject']}\n\n{scenario['email_body']}",
                "sentiment": scenario["sentiment"],
                "priority": scenario["priority"],
                "language": "en",
                "category": "customer_service",
                "generated_response": self._generate_demo_response(scenario),
                "customer_id": customer["id"]
            }
            responses["responses"].append(response)
        
        # Save email data
        with open(os.path.join(self.email_path, "email_responses.json"), 'w') as f:
            json.dump(responses, f, indent=2)
    
    def _populate_calls(self):
        """Populate call system with demo calls"""
        conn = sqlite3.connect(self.call_db_path)
        
        # Create table if not exists
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
        
        agents = ['AGT_SMITH', 'AGT_JONES', 'AGT_DAVIS']
        
        for idx, scenario in enumerate(self.demo_scenarios):
            customer = self.demo_customers[scenario["customer_id"]]
            start_time = datetime.now() - timedelta(hours=idx*3)
            duration = scenario["call_duration"]
            end_time = start_time + timedelta(seconds=duration)
            
            conn.execute('''
                INSERT INTO calls (agent_id, customer_id, start_time, end_time, duration, call_outcome)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                agents[idx % len(agents)],
                customer["id"],
                start_time.isoformat(),
                end_time.isoformat(),
                duration,
                scenario["call_outcome"]
            ))
        
        conn.commit()
        conn.close()
    
    def _populate_crm(self):
        """Populate CRM with demo contacts"""
        contacts = {"contacts": []}
        
        for customer in self.demo_customers:
            contact = {
                "id": f"contact_{customer['id']}",
                "email": customer["email"],
                "firstname": customer["name"].split()[0],
                "lastname": customer["name"].split()[1],
                "phone": customer["phone"],
                "company": customer["company"],
                "customer_type": customer["type"],
                "created_at": datetime.now().isoformat(),
                "last_interaction": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            }
            contacts["contacts"].append(contact)
        
        # Ensure directory exists
        os.makedirs(self.crm_data_path, exist_ok=True)
        
        # Save CRM data
        with open(os.path.join(self.crm_data_path, "contacts.json"), 'w') as f:
            json.dump(contacts, f, indent=2)
    
    def _generate_demo_response(self, scenario):
        """Generate appropriate response based on scenario"""
        if scenario["sentiment"] == "negative":
            return f"Dear Customer,\n\nI sincerely apologize for the inconvenience. I've escalated your issue to our priority team. A senior specialist will contact you within 2 hours.\n\nYour satisfaction is our top priority.\n\nBest regards,\nAkio Support Team"
        elif scenario["sentiment"] == "positive":
            return f"Dear Customer,\n\nThank you for your interest! I'm delighted to offer you our bulk discount of 15% for orders over 500 units. I've attached our bulk pricing sheet.\n\nLooking forward to your business!\n\nBest regards,\nAkio Sales Team"
        else:
            return f"Dear Customer,\n\nThank you for reporting this issue. Our technical team has identified the problem and is implementing a fix. The API should be stable within the next hour.\n\nWe appreciate your patience.\n\nBest regards,\nAkio Technical Support"

# Add to unified_platform.py
def add_demo_mode_button():
    """Add demo mode button to the unified platform"""
    if st.button("🎭 Activate Demo Mode", key="demo_mode", type="secondary"):
        demo_manager = DemoModeManager()
        with st.spinner("Populating all services with demo data..."):
            if demo_manager.activate_demo_mode():
                st.success("Demo Mode activated! All services now have interconnected sample data.")
                time.sleep(2)
                st.rerun()