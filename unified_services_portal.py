# unified_services_portal_fixed.py
import streamlit as st
import subprocess
import os
import time
import socket
import sys
import webbrowser
from datetime import datetime
import threading

# Page configuration
st.set_page_config(
    page_title="Unified Services",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced modern CSS (keeping your UI exactly the same)
st.markdown("""
<style>
    /* Reset and base styles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        padding: 0;
        overflow-x: hidden;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0f0f1e, #1a1a2e, #16213e, #0f3460);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Container with glass morphism */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 3rem 2rem;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Header section */
    .header-section {
        text-align: center;
        margin-bottom: 4rem;
        animation: slideDown 0.8s ease-out;
    }
    
    .main-title {
        font-size: 4.5rem;
        font-weight: 200;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: 0.15em;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
    }
    
    .subtitle {
        font-size: 1.8rem;
        color: #94a3b8;
        font-weight: 300;
        margin-bottom: 3rem;
    }
    
    /* Service cards container */
    .services-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2.5rem;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
    
    /* Glass morphism card */
    .service-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 30px;
        padding: 3rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .service-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .service-card:hover {
        transform: translateY(-15px) scale(1.02);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }
    
    .service-card:hover::before {
        opacity: 1;
    }
    
    /* Service content */
    .service-icon-wrapper {
        font-size: 3.5rem;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .email-service .service-icon-wrapper {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
    }
    
    .call-service .service-icon-wrapper {
        background: linear-gradient(135deg, #10b981, #34d399);
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
    }
    
    .crm-service .service-icon-wrapper {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3);
    }
    
    .service-name {
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .service-description {
        font-size: 1.1rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Status badge */
    .status-badge {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-offline {
        background: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
        border: 1px solid rgba(107, 114, 128, 0.3);
    }
    
    .status-starting {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    .status-online .status-dot {
        background: #10b981;
    }
    
    .status-offline .status-dot {
        background: #6b7280;
        animation: none;
    }
    
    .status-starting .status-dot {
        background: #f59e0b;
        animation: pulse 1s infinite;
    }
    
    /* Animations */
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 3rem;
        }
        .services-container {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
    }
    
    /* Action buttons */
    .action-button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .action-button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Service configuration - FIXED PORTS
SERVICES = {
    "email": {
        "name": "Email Assistant",
        "description": "AI-powered email response system with multi-language support and smart templates",
        "icon": "✉️",
        "port": 8501,  # FIXED: Changed from 8503 to 8501
        "path": "Email-Assistant",
        "command": ["streamlit", "run", "email_assistant.py"],  # Default port 8501
        "url": "http://localhost:8501"  # FIXED URL
    },
    "call": {
        "name": "Call Metrics",
        "description": "Real-time analytics dashboard for call center performance monitoring",
        "icon": "📊",
        "port": 8502,
        "api_port": 8000,
        "path": "Call-System",
        "command": ["streamlit", "run", "dashboard.py", "--server.port", "8502"],
        "api_command": ["python", "main.py"],
        "url": "http://localhost:8502"
    },
    "crm": {
        "name": "CRM Integration",
        "description": "Customer relationship management system with HubSpot integration",
        "icon": "🤝",
        "port": 3000,
        "path": "crm-integration-prototype",
        "command": ["npm", "start"],
        "url": "http://localhost:3000"
    }
}

# Service manager class
class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.starting_services = set()  # Track services that are starting
        
    def check_port(self, port):
        """Check if a port is in use"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def start_service(self, service_id):
        """Start a service"""
        service = SERVICES[service_id]
        service_path = os.path.abspath(service["path"])
        
        # Mark service as starting
        self.starting_services.add(service_id)
        
        try:
            # For call metrics, start API first
            if service_id == "call" and not self.check_port(service.get("api_port", 0)):
                if sys.platform == "win32":
                    # Option 1: Open in new window (visible)
                    subprocess.Popen(
                        f'start cmd /k "cd /d {service_path} && python main.py"',
                        shell=True
                    )
                    
                    # Option 2: Run hidden (uncomment to use)
                    # subprocess.Popen(
                    #     ["python", "main.py"],
                    #     cwd=service_path,
                    #     creationflags=subprocess.CREATE_NO_WINDOW
                    # )
                time.sleep(3)
            
            # Start main service
            if sys.platform == "win32":
                # Option 1: Open in new window (visible - good for debugging)
                if service_id == "email":
                    subprocess.Popen(
                        f'start cmd /k "cd /d {service_path} && streamlit run email_assistant.py"',
                        shell=True
                    )
                elif service_id == "call":
                    subprocess.Popen(
                        f'start cmd /k "cd /d {service_path} && streamlit run dashboard.py --server.port 8502"',
                        shell=True
                    )
                elif service_id == "crm":
                    subprocess.Popen(
                        f'start cmd /k "cd /d {service_path} && npm start"',
                        shell=True
                    )
                
                # Option 2: Run hidden (uncomment to use)
                # if service_id == "email":
                #     subprocess.Popen(
                #         ["streamlit", "run", "email_assistant.py"],
                #         cwd=service_path,
                #         creationflags=subprocess.CREATE_NO_WINDOW
                #     )
                # elif service_id == "call":
                #     subprocess.Popen(
                #         ["streamlit", "run", "dashboard.py", "--server.port", "8502"],
                #         cwd=service_path,
                #         creationflags=subprocess.CREATE_NO_WINDOW
                #     )
                # elif service_id == "crm":
                #     subprocess.Popen(
                #         ["npm", "start"],
                #         cwd=service_path,
                #         creationflags=subprocess.CREATE_NO_WINDOW
                #     )
            
            # Wait a bit for service to start
            time.sleep(3)
            
            # Remove from starting set after a delay
            def remove_starting_flag():
                time.sleep(10)
                self.starting_services.discard(service_id)
            
            threading.Thread(target=remove_starting_flag, daemon=True).start()
            
            return True
        except Exception as e:
            self.starting_services.discard(service_id)
            st.error(f"Error starting service: {str(e)}")
            return False
        
    def get_status(self, service_id):
        """Get service status"""
        service = SERVICES[service_id]
        
        # Check if service is starting
        if service_id in self.starting_services:
            return "starting"
        
        # Check main port
        if self.check_port(service["port"]):
            return "online"
            
        return "offline"
    
    def start_all_services(self):
        """Start all services"""
        for service_id in SERVICES.keys():
            if self.get_status(service_id) == "offline":
                self.start_service(service_id)
                time.sleep(2)  # Wait between starting services

# Initialize service manager
if 'service_manager' not in st.session_state:
    st.session_state.service_manager = ServiceManager()

# Initialize auto-start flag
if 'auto_started' not in st.session_state:
    st.session_state.auto_started = False

# Main UI
st.markdown("""
<div class="main-container">
    <div class="header-section">
        <h1 class="main-title">Unified Services</h1>
        <p class="subtitle">Choose your service</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Add control buttons at the top
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🚀 Start All Services", use_container_width=True, type="primary"):
        with st.spinner("Starting all services..."):
            st.session_state.service_manager.start_all_services()
            st.success("All services are starting!")
            time.sleep(5)
            st.rerun()

with col2:
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()

# Auto-start services on first load (optional)
if not st.session_state.auto_started:
    auto_start = st.checkbox("Auto-start all services on load", value=False)
    if auto_start:
        st.session_state.service_manager.start_all_services()
        st.session_state.auto_started = True
        st.rerun()

st.markdown("---")

# Create service cards
cols = st.columns(3)

for idx, (service_id, service) in enumerate(SERVICES.items()):
    with cols[idx]:
        status = st.session_state.service_manager.get_status(service_id)
        
        # Service card HTML
        card_class = f"{service_id}-service"
        status_class = f"status-{status}"
        status_text = status.replace("_", " ").title()
        
        # Create card
        st.markdown(f"""
        <div class="service-card {card_class}">
            <div class="status-badge {status_class}">
                <span class="status-dot"></span>
                <span>{status_text}</span>
            </div>
            <div class="service-icon-wrapper">
                {service['icon']}
            </div>
            <h3 class="service-name">{service['name']}</h3>
            <p class="service-description">{service['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        if status == "online":
            if st.button(f"🔗 Open {service['name']}", key=f"open_{service_id}", 
                        use_container_width=True, type="primary"):
                webbrowser.open_new_tab(service["url"])
        elif status == "starting":
            st.info("Service is starting... Please wait")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"▶️ Start", key=f"start_{service_id}", 
                           use_container_width=True):
                    if st.session_state.service_manager.start_service(service_id):
                        st.success(f"Starting {service['name']}...")
                        time.sleep(2)
                        st.rerun()
            with col2:
                if st.button(f"🔗 Open Anyway", key=f"force_open_{service_id}",
                           use_container_width=True):
                    webbrowser.open_new_tab(service["url"])

# Help section
with st.expander("ℹ️ About the PowerShell Windows"):
    st.markdown("""
    ### Why do PowerShell/Command windows open?
    
    When you start a service, a PowerShell/Command window opens to run the service. This is **normal and expected behavior**.
    
    **Benefits of visible windows:**
    - You can see if services are running properly
    - Error messages are visible for debugging
    - You can manually stop services by closing the window
    
    **To hide the windows (advanced users only):**
    - Edit the `unified_services_portal.py` file
    - Uncomment the "Option 2" sections in the `start_service` method
    - Comment out the "Option 1" sections
    - This will run services in the background
    
    **Important:** Keep the windows open while using the services. Closing them will stop the services.
    
    ### Quick Start Guide:
    
    1. Click "🚀 Start All Services" to start everything at once
    2. Wait for all services to show "Online" status (10-15 seconds)
    3. Click "🔗 Open" buttons to access each service
    
    ### Direct URLs:
    - Email Assistant: `http://localhost:8501`
    - Call Metrics: `http://localhost:8502`
    - CRM Integration: `http://localhost:3000`
    """)

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()