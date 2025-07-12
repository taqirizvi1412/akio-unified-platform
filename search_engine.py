# search_engine.py
import json
import sqlite3
import os
import requests
from datetime import datetime
from typing import List, Dict, Any

class UnifiedSearchEngine:
    """Cross-system search engine for the Akio platform"""
    
    def __init__(self):
        self.email_path = "Email-Assistant"
        self.call_db_path = os.path.join("Call-System", "call_metrics.db")
        self.crm_data_path = os.path.join("crm-integration-prototype", "data")
        
    def search_all_systems(self, query: str) -> Dict[str, Any]:
        """Search across all systems for a given query"""
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "email_results": self._search_emails(query),
            "call_results": self._search_calls(query),
            "crm_results": self._search_crm(query),
            "timeline": []
        }
        
        # Build unified timeline
        results["timeline"] = self._build_timeline(results)
        
        return results
    
    def _search_emails(self, query: str) -> List[Dict[str, Any]]:
        """Search email system"""
        results = []
        query_lower = query.lower()
        
        # Search in email responses
        responses_file = os.path.join(self.email_path, "email_responses.json")
        if os.path.exists(responses_file):
            try:
                with open(responses_file, 'r') as f:
                    data = json.load(f)
                    
                for response in data.get("responses", []):
                    # Search in email content and metadata
                    if (query_lower in response.get("customer_email", "").lower() or
                        query_lower in response.get("original_email", "").lower() or
                        query_lower in response.get("generated_response", "").lower()):
                        
                        results.append({
                            "type": "email_response",
                            "timestamp": response.get("timestamp"),
                            "customer_email": response.get("customer_email"),
                            "subject": self._extract_subject(response.get("original_email", "")),
                            "sentiment": response.get("sentiment"),
                            "language": response.get("language")
                        })
            except Exception as e:
                print(f"Error searching emails: {e}")
        
        # Search in templates
        templates_file = os.path.join(self.email_path, "templates.json")
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    data = json.load(f)
                    
                for template in data.get("templates", []):
                    if query_lower in template.get("template", "").lower():
                        results.append({
                            "type": "email_template",
                            "name": template.get("name"),
                            "category": template.get("category")
                        })
            except Exception as e:
                print(f"Error searching templates: {e}")
        
        return results
    
    def _search_calls(self, query: str) -> List[Dict[str, Any]]:
        """Search call system database"""
        results = []
        
        if not os.path.exists(self.call_db_path):
            return results
        
        try:
            conn = sqlite3.connect(self.call_db_path)
            conn.row_factory = sqlite3.Row
            
            # Search by customer ID, agent ID, or phone number
            cursor = conn.execute("""
                SELECT * FROM calls 
                WHERE customer_id LIKE ? OR agent_id LIKE ?
                ORDER BY start_time DESC
                LIMIT 20
            """, (f"%{query}%", f"%{query}%"))
            
            for row in cursor:
                results.append({
                    "type": "call_record",
                    "call_id": row["call_id"],
                    "agent_id": row["agent_id"],
                    "customer_id": row["customer_id"],
                    "start_time": row["start_time"],
                    "duration": row["duration"],
                    "outcome": row["call_outcome"]
                })
            
            conn.close()
        except Exception as e:
            print(f"Error searching calls: {e}")
        
        return results
    
    def _search_crm(self, query: str) -> List[Dict[str, Any]]:
        """Search CRM data"""
        results = []
        query_lower = query.lower()
        
        contacts_file = os.path.join(self.crm_data_path, "contacts.json")
        if os.path.exists(contacts_file):
            try:
                with open(contacts_file, 'r') as f:
                    data = json.load(f)
                    
                for contact in data.get("contacts", []):
                    # Search in all contact fields
                    if (query_lower in contact.get("email", "").lower() or
                        query_lower in contact.get("firstname", "").lower() or
                        query_lower in contact.get("lastname", "").lower() or
                        query_lower in contact.get("phone", "").lower() or
                        query_lower in contact.get("company", "").lower()):
                        
                        results.append({
                            "type": "crm_contact",
                            "id": contact.get("id"),
                            "email": contact.get("email"),
                            "name": f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
                            "phone": contact.get("phone"),
                            "company": contact.get("company"),
                            "created_at": contact.get("created_at")
                        })
            except Exception as e:
                print(f"Error searching CRM: {e}")
        
        return results
    
    def _extract_subject(self, email_text: str) -> str:
        """Extract subject from email text"""
        lines = email_text.split('\n')
        for line in lines:
            if line.startswith("Subject:"):
                return line.replace("Subject:", "").strip()
        return "No subject"
    
    def _build_timeline(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build a unified timeline from all results"""
        timeline_events = []
        
        # Add email events
        for email in results["email_results"]:
            if email.get("timestamp"):
                timeline_events.append({
                    "timestamp": email["timestamp"],
                    "system": "📧 Email",
                    "event": f"Email {email.get('type', 'interaction')} - {email.get('subject', 'No subject')}",
                    "details": email
                })
        
        # Add call events
        for call in results["call_results"]:
            if call.get("start_time"):
                timeline_events.append({
                    "timestamp": call["start_time"],
                    "system": "📞 Call",
                    "event": f"Call with {call['agent_id']} - {call['outcome']}",
                    "details": call
                })
        
        # Add CRM events
        for contact in results["crm_results"]:
            if contact.get("created_at"):
                timeline_events.append({
                    "timestamp": contact["created_at"],
                    "system": "👥 CRM",
                    "event": f"Contact created: {contact['name']}",
                    "details": contact
                })
        
        # Sort by timestamp (newest first)
        timeline_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return timeline_events[:20]  # Return top 20 most recent events

# API endpoint for the search (to be added to a FastAPI app)
def create_search_api():
    """Create FastAPI endpoints for search"""
    from fastapi import FastAPI, Query
    
    app = FastAPI(title="Unified Search API")
    search_engine = UnifiedSearchEngine()
    
    @app.get("/api/search")
    async def search(q: str = Query(..., description="Search query")):
        """Search across all systems"""
        results = search_engine.search_all_systems(q)
        return results
    
    @app.get("/api/search/emails")
    async def search_emails(q: str = Query(..., description="Search query")):
        """Search only in email system"""
        results = search_engine._search_emails(q)
        return {"query": q, "results": results}
    
    @app.get("/api/search/calls")
    async def search_calls(q: str = Query(..., description="Search query")):
        """Search only in call system"""
        results = search_engine._search_calls(q)
        return {"query": q, "results": results}
    
    @app.get("/api/search/crm")
    async def search_crm(q: str = Query(..., description="Search query")):
        """Search only in CRM system"""
        results = search_engine._search_crm(q)
        return {"query": q, "results": results}
    
    return app

if __name__ == "__main__":
    # Test the search engine
    engine = UnifiedSearchEngine()
    
    # Example searches
    print("Testing search engine...")
    
    # Search for a customer
    results = engine.search_all_systems("john")
    print(f"\nSearch results for 'john': {len(results['timeline'])} events found")
    
    # Search for an email
    results = engine.search_all_systems("@example.com")
    print(f"\nSearch results for '@example.com': {len(results['timeline'])} events found")
    
    # To run as API:
    # import uvicorn
    # app = create_search_api()
    # uvicorn.run(app, host="0.0.0.0", port=8003)