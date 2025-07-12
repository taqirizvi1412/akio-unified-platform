# # unified_platform.py
# import streamlit as st
# import subprocess
# import os
# import json
# import time
# import webbrowser
# from datetime import datetime
# import sys
# import signal
# import atexit

# # Try to import psutil, but don't fail if it's not available
# try:
#     import psutil
#     PSUTIL_AVAILABLE = True
# except ImportError:
#     PSUTIL_AVAILABLE = False

# # Page configuration - MUST BE FIRST STREAMLIT COMMAND
# st.set_page_config(
#     page_title="Akio Unified Platform",
#     page_icon="🎯",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Show warning AFTER page config
# if not PSUTIL_AVAILABLE:
#     st.info("Note: psutil not installed - using fallback port detection method")

# # Custom CSS for professional styling
# st.markdown("""
# <style>
#     .main-header {
#         background: linear-gradient(135deg, #1e3a8a, #3b82f6);
#         padding: 2rem;
#         border-radius: 10px;
#         color: white;
#         margin-bottom: 2rem;
#     }
    
#     .service-card {
#         background: #f8f9fa;
#         border: 1px solid #dee2e6;
#         border-radius: 8px;
#         padding: 1.5rem;
#         margin-bottom: 1rem;
#         transition: all 0.3s ease;
#     }
    
#     .service-card:hover {
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         transform: translateY(-2px);
#     }
    
#     .status-online {
#         color: #28a745;
#         font-weight: bold;
#     }
    
#     .status-offline {
#         color: #dc3545;
#         font-weight: bold;
#     }
    
#     .status-starting {
#         color: #ffc107;
#         font-weight: bold;
#     }
    
#     iframe {
#         border: 1px solid #dee2e6;
#         border-radius: 8px;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
#     }
# </style>
# """, unsafe_allow_html=True)

# # Load configuration
# def load_config():
#     """Load service configuration"""
#     default_config = {
#         "services": {
#             "email_assistant": {
#                 "name": "Email Assistant",
#                 "path": "Email-Assistant",
#                 "command": "python -m streamlit run email_assistant.py",
#                 "port": 8501,
#                 "url": "http://localhost:8501",
#                 "icon": "📧",
#                 "description": "AI-powered email response system with multi-language support"
#             },
#             "call_metrics_api": {
#                 "name": "Call Metrics API",
#                 "path": "Call-System",
#                 "command": "python main.py",
#                 "port": 8000,
#                 "url": "http://localhost:8000",
#                 "icon": "🔌",
#                 "description": "Backend API for call center metrics"
#             },
#             "call_metrics_dashboard": {
#                 "name": "Call Metrics Dashboard",
#                 "path": "Call-System",
#                 "command": "python -m streamlit run dashboard.py --server.port 8502",
#                 "port": 8502,
#                 "url": "http://localhost:8502",
#                 "icon": "📞",
#                 "description": "Real-time call center analytics dashboard",
#                 "depends_on": ["call_metrics_api"]
#             },
#             "crm_integration": {
#                 "name": "CRM Integration",
#                 "path": "crm-integration-prototype",
#                 "command": "npm start",
#                 "port": 3000,
#                 "url": "http://localhost:3000",
#                 "icon": "👥",
#                 "description": "HubSpot CRM integration prototype",
#                 "setup_command": "npm install"
#             }
#         },
#         "platform": {
#             "name": "Akio Unified Call Center Platform",
#             "version": "1.0.0",
#             "author": "Akio Intern",
#             "auto_refresh_interval": 5,
#             "theme": "light"
#         },
#         "startup": {
#             "auto_start_services": [],
#             "start_delay_seconds": 2,
#             "health_check_retries": 3
#         }
#     }
    
#     config_path = "unified_config.json"
#     if os.path.exists(config_path):
#         with open(config_path, 'r') as f:
#             return json.load(f)
#     else:
#         # Save default config
#         with open(config_path, 'w') as f:
#             json.dump(default_config, f, indent=2)
#         return default_config

# # Process management
# class ServiceManager:
#     def __init__(self):
#         self.processes = {}
#         self.config = load_config()
#         # Register cleanup on exit
#         atexit.register(self.cleanup_all)
    
#     def check_port(self, port):
#         """Check if a port is in use"""
#         if PSUTIL_AVAILABLE:
#             for conn in psutil.net_connections():
#                 if conn.laddr.port == port and conn.status == 'LISTEN':
#                     return True
#             return False
#         else:
#             # Fallback method without psutil
#             import socket
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             result = sock.connect_ex(('localhost', port))
#             sock.close()
#             return result == 0
    
#     def get_service_status(self, service_id):
#         """Get the status of a service"""
#         service = self.config['services'][service_id]
#         port = service['port']
        
#         if self.check_port(port):
#             return "online"
#         elif service_id in self.processes and self.processes[service_id].poll() is None:
#             return "starting"
#         else:
#             return "offline"
    
#     def start_service(self, service_id):
#         """Start a service"""
#         if service_id in self.processes and self.processes[service_id].poll() is None:
#             return False, "Service is already running"
        
#         service = self.config['services'][service_id]
        
#         # Check dependencies
#         if 'depends_on' in service:
#             for dep in service['depends_on']:
#                 if self.get_service_status(dep) != "online":
#                     self.start_service(dep)
#                     time.sleep(2)  # Wait for dependency to start
        
#         # Run setup if needed (for Node.js projects)
#         if 'setup_command' in service and not os.path.exists(os.path.join(service['path'], 'node_modules')):
#             st.info(f"Running setup for {service['name']}...")
#             setup_process = subprocess.Popen(
#                 service['setup_command'],
#                 cwd=service['path'],
#                 shell=True
#             )
#             setup_process.wait()
        
#         # Start the service
#         try:
#             # Parse command for better Windows compatibility
#             cmd_parts = service['command'].split()
            
#             if sys.platform == "win32":
#                 # Windows - use CREATE_NEW_CONSOLE for better process management
#                 process = subprocess.Popen(
#                     service['command'],
#                     cwd=os.path.abspath(service['path']),
#                     shell=True,
#                     creationflags=subprocess.CREATE_NEW_CONSOLE
#                 )
#             else:
#                 # Mac/Linux
#                 process = subprocess.Popen(
#                     service['command'],
#                     cwd=os.path.abspath(service['path']),
#                     shell=True,
#                     preexec_fn=os.setsid
#                 )
            
#             self.processes[service_id] = process
#             return True, f"{service['name']} started successfully"
#         except Exception as e:
#             return False, f"Failed to start {service['name']}: {str(e)}"
    
#     def stop_service(self, service_id):
#         """Stop a service"""
#         if service_id not in self.processes:
#             # Try to find and kill by port if process isn't tracked
#             service = self.config['services'][service_id]
#             port = service['port']
#             if self.kill_process_on_port(port):
#                 return True, "Service stopped successfully"
#             return False, "Service is not running"
        
#         process = self.processes[service_id]
#         if process.poll() is None:
#             try:
#                 if sys.platform == "win32":
#                     # Windows: use taskkill for better results
#                     subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
#                                  capture_output=True, check=False)
#                 else:
#                     os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
#                 del self.processes[service_id]
#                 return True, "Service stopped successfully"
#             except Exception as e:
#                 del self.processes[service_id]
#                 return True, f"Service stopped (with warning: {str(e)})"
#         else:
#             del self.processes[service_id]
#             return False, "Service was not running"
    
#     def kill_process_on_port(self, port):
#         """Kill any process using a specific port (Windows)"""
#         if sys.platform == "win32":
#             try:
#                 # Find process using the port
#                 result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
#                 for line in result.stdout.splitlines():
#                     if f':{port}' in line and 'LISTENING' in line:
#                         pid = line.strip().split()[-1]
#                         subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
#                         return True
#             except:
#                 pass
#         return False
    
#     def cleanup_all(self):
#         """Stop all services on exit"""
#         for service_id in list(self.processes.keys()):
#             self.stop_service(service_id)

# # Initialize service manager
# if 'service_manager' not in st.session_state:
#     st.session_state.service_manager = ServiceManager()

# # Header
# st.markdown("""
# <div class="main-header">
#     <h1 style="margin: 0; text-align: center;">🎯 Akio Unified Call Center Platform</h1>
#     <p style="text-align: center; margin-top: 0.5rem; opacity: 0.9;">
#         Integrating Email Management, Call Analytics, and CRM Systems
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # Main interface
# tab1, tab2, tab3 = st.tabs(["🏠 Service Manager", "📊 Unified View", "📚 Documentation"])

# with tab1:
#     st.header("Service Control Panel")
    
#     # Quick actions
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         if st.button("🚀 Start All Services", use_container_width=True):
#             for service_id in st.session_state.service_manager.config['services']:
#                 success, message = st.session_state.service_manager.start_service(service_id)
#                 if success:
#                     st.success(message)
#                 else:
#                     st.error(message)
#             st.rerun()
    
#     with col2:
#         if st.button("🛑 Stop All Services", use_container_width=True):
#             for service_id in st.session_state.service_manager.config['services']:
#                 st.session_state.service_manager.stop_service(service_id)
#             st.rerun()
    
#     with col3:
#         if st.button("🔄 Refresh Status", use_container_width=True):
#             st.rerun()
    
#     with col4:
#         auto_refresh = st.checkbox("Auto-refresh (5s)", key="auto_refresh")
    
#     st.divider()
    
#     # Service cards
#     for service_id, service in st.session_state.service_manager.config['services'].items():
#         status = st.session_state.service_manager.get_service_status(service_id)
        
#         with st.container():
#             col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
#             with col1:
#                 st.markdown(f"### {service['icon']}")
            
#             with col2:
#                 st.markdown(f"### {service['name']}")
#                 st.caption(service['description'])
#                 st.caption(f"Port: {service['port']} | Path: {service['path']}")
            
#             with col3:
#                 if status == "online":
#                     st.markdown('<p class="status-online">● Online</p>', unsafe_allow_html=True)
#                 elif status == "starting":
#                     st.markdown('<p class="status-starting">● Starting...</p>', unsafe_allow_html=True)
#                 else:
#                     st.markdown('<p class="status-offline">● Offline</p>', unsafe_allow_html=True)
            
#             with col4:
#                 col_a, col_b = st.columns(2)
#                 with col_a:
#                     if status == "offline":
#                         if st.button("▶️ Start", key=f"start_{service_id}", use_container_width=True):
#                             success, message = st.session_state.service_manager.start_service(service_id)
#                             if success:
#                                 st.success(message)
#                             else:
#                                 st.error(message)
#                             time.sleep(2)
#                             st.rerun()
#                     else:
#                         if st.button("⏹️ Stop", key=f"stop_{service_id}", use_container_width=True):
#                             success, message = st.session_state.service_manager.stop_service(service_id)
#                             if success:
#                                 st.success(message)
#                             else:
#                                 st.error(message)
#                             st.rerun()
                
#                 with col_b:
#                     if status == "online":
#                         if st.button("🔗 Open", key=f"open_{service_id}", use_container_width=True):
#                             webbrowser.open(service['url'])
        
#         st.divider()

# with tab2:
#     st.header("Unified Platform View")
    
#     # Check which services are online
#     online_services = []
#     for service_id, service in st.session_state.service_manager.config['services'].items():
#         if st.session_state.service_manager.get_service_status(service_id) == "online":
#             online_services.append((service_id, service))
    
#     if not online_services:
#         st.info("No services are currently running. Go to the Service Manager tab to start services.")
#     else:
#         # Service selector
#         service_names = [service['name'] for _, service in online_services]
#         selected_service = st.selectbox(
#             "Select a service to view:",
#             service_names,
#             index=0
#         )
        
#         # Find the selected service
#         for service_id, service in online_services:
#             if service['name'] == selected_service:
#                 st.subheader(f"{service['icon']} {service['name']}")
                
#                 # Embed the service in an iframe
#                 iframe_height = 800
#                 if service_id == "crm_integration":
#                     # CRM needs more height
#                     iframe_height = 900
                
#                 iframe_html = f"""
#                 <iframe 
#                     src="{service['url']}" 
#                     width="100%" 
#                     height="{iframe_height}"
#                     frameborder="0">
#                 </iframe>
#                 """
#                 st.markdown(iframe_html, unsafe_allow_html=True)
                
#                 # Quick links
#                 st.caption(f"🔗 Direct link: {service['url']}")

# with tab3:
#     st.header("📚 Platform Documentation")
    
#     tab_email, tab_call, tab_crm, tab_integration = st.tabs([
#         "📧 Email Assistant",
#         "📞 Call Metrics", 
#         "👥 CRM Integration",
#         "🔗 Integration Guide"
#     ])
    
#     with tab_email:
#         st.markdown("""
#         ## Email Assistant Features
        
#         - **Multi-language Support**: English, French, Spanish, German
#         - **Sentiment Analysis**: Automatic detection of customer mood
#         - **Smart Templates**: Reusable response templates with variables
#         - **Priority Queue**: Intelligent email prioritization
#         - **Search & Analytics**: Historical data analysis
        
#         ### Quick Start:
#         1. Select a test email or paste customer email
#         2. Click "Generate Response"
#         3. Review and customize the response
#         4. Copy to send via your email client
#         """)
    
#     with tab_call:
#         st.markdown("""
#         ## Call Metrics Dashboard
        
#         - **Real-time Analytics**: Live call volume tracking
#         - **Agent Performance**: Individual and team metrics
#         - **Outcome Analysis**: Call resolution statistics
#         - **Trend Visualization**: Hourly and daily patterns
        
#         ### Requirements:
#         - API must be running (port 8000)
#         - Dashboard connects automatically
#         - 7 days of test data included
#         """)
    
#     with tab_crm:
#         st.markdown("""
#         ## CRM Integration Prototype
        
#         - **Contact Management**: Create and search contacts
#         - **Activity Logging**: Track calls and emails
#         - **Mock HubSpot API**: No real API costs
#         - **Visual Workflow**: See integration in action
        
#         ### Features:
#         - Simulated API connections
#         - Local data storage
#         - Full CRUD operations
#         - Integration demonstrations
#         """)
    
#     with tab_integration:
#         st.markdown("""
#         ## Integration Points
        
#         ### Current Integrations:
#         - **Shared Metrics**: View combined analytics
#         - **Unified Interface**: Single control panel
#         - **Process Management**: Start/stop all services
        
#         ### Future Integration Ideas:
#         1. **Email → CRM**: Auto-create contacts from emails
#         2. **Call → Email**: Follow-up email suggestions
#         3. **Unified Search**: Search across all platforms
#         4. **Workflow Automation**: Trigger actions across systems
        
#         ### Architecture Benefits:
#         - **Microservices**: Each component runs independently
#         - **Scalable**: Easy to add new services
#         - **Maintainable**: Clear separation of concerns
#         - **Cost-effective**: No external API costs
#         """)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; color: #666;">
#     <p>Akio Unified Platform v1.0 | Created for Internship Demo | All services run locally (Free)</p>
# </div>
# """, unsafe_allow_html=True)

# # Auto-refresh logic
# if st.session_state.get('auto_refresh', False):
#     time.sleep(5)
#     st.rerun()
# unified_platform_enhanced.py - Key fixes and enhancements

import streamlit as st
import subprocess
import os
import json
import time
import webbrowser
from datetime import datetime
import sys
import signal
import atexit

# Import our new modules
from demo_mode import DemoModeManager
from performance_monitor import PerformanceMonitor

# Page configuration
st.set_page_config(
    page_title="Akio Unified Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with onboarding overlay
st.markdown("""
<style>
    /* Previous CSS remains the same... */
    
    /* Onboarding overlay styles */
    .onboarding-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
        display: none;
    }
    
    .onboarding-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 15px;
        max-width: 600px;
        text-align: center;
    }
    
    .tour-highlight {
        position: relative;
        z-index: 10000;
        box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        animation: pulse 2s infinite;
    }
    
    /* About section */
    .about-section {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# FIXED: Correct service configuration with proper ports
SERVICES = {
    "email": {
        "name": "Email Assistant",
        "description": "AI-powered email response system with multi-language support and smart templates",
        "icon": "✉️",
        "port": 8501,  # FIXED: Email Assistant uses default Streamlit port
        "path": "Email-Assistant",
        "command": ["streamlit", "run", "email_assistant.py"],
        "url": "http://localhost:8501"
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

# Enhanced Service Manager with better error handling
class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.starting_services = set()
        self.service_start_times = {}
        
    def check_port(self, port):
        """Check if a port is in use"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def get_service_uptime(self, service_id):
        """Get service uptime"""
        if service_id in self.service_start_times:
            uptime = datetime.now() - self.service_start_times[service_id]
            return f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        return "N/A"
    
    def start_service(self, service_id):
        """Start a service with enhanced error handling"""
        service = SERVICES[service_id]
        service_path = os.path.abspath(service["path"])
        
        # Check if path exists
        if not os.path.exists(service_path):
            return False, f"Service path not found: {service_path}"
        
        # Mark service as starting
        self.starting_services.add(service_id)
        
        try:
            # For call metrics, start API first
            if service_id == "call" and not self.check_port(service.get("api_port", 0)):
                api_cmd = f'cd /d "{service_path}" && python main.py'
                if sys.platform == "win32":
                    subprocess.Popen(f'start "Call API" cmd /k "{api_cmd}"', shell=True)
                else:
                    subprocess.Popen(api_cmd, shell=True, cwd=service_path)
                time.sleep(3)
            
            # Start main service
            if sys.platform == "win32":
                if service_id == "email":
                    cmd = f'cd /d "{service_path}" && streamlit run email_assistant.py'
                elif service_id == "call":
                    cmd = f'cd /d "{service_path}" && streamlit run dashboard.py --server.port 8502'
                elif service_id == "crm":
                    cmd = f'cd /d "{service_path}" && npm start'
                
                subprocess.Popen(f'start "{service["name"]}" cmd /k "{cmd}"', shell=True)
            else:
                subprocess.Popen(service["command"], cwd=service_path)
            
            # Record start time
            self.service_start_times[service_id] = datetime.now()
            
            # Wait for service to start
            time.sleep(3)
            
            # Remove from starting set
            self.starting_services.discard(service_id)
            
            return True, f"{service['name']} started successfully"
            
        except Exception as e:
            self.starting_services.discard(service_id)
            return False, f"Error starting {service['name']}: {str(e)}"
    
    def stop_service(self, service_id):
        """Stop a service"""
        service = SERVICES[service_id]
        
        # Kill by port for better reliability
        if sys.platform == "win32":
            # Stop main service
            self._kill_process_on_port(service["port"])
            
            # Stop API if it's call service
            if service_id == "call":
                self._kill_process_on_port(service.get("api_port", 0))
            
            # Remove start time
            self.service_start_times.pop(service_id, None)
            
            return True, f"{service['name']} stopped"
        else:
            # Unix/Linux implementation
            os.system(f"lsof -ti:{service['port']} | xargs kill -9")
            return True, f"{service['name']} stopped"
    
    def _kill_process_on_port(self, port):
        """Kill process on specific port (Windows)"""
        if port:
            os.system(f'netstat -ano | findstr :{port} > temp.txt')
            with open('temp.txt', 'r') as f:
                lines = f.readlines()
            os.remove('temp.txt')
            
            for line in lines:
                if 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    os.system(f'taskkill /F /PID {pid} >nul 2>&1')
    
    def get_status(self, service_id):
        """Get service status with more detail"""
        service = SERVICES[service_id]
        
        if service_id in self.starting_services:
            return "starting"
        
        if self.check_port(service["port"]):
            return "online"
            
        return "offline"
    
    def cleanup_all(self):
        """Stop all services on exit"""
        for service_id in SERVICES.keys():
            self.stop_service(service_id)

# Initialize managers
if 'service_manager' not in st.session_state:
    st.session_state.service_manager = ServiceManager()
    atexit.register(st.session_state.service_manager.cleanup_all)

if 'demo_manager' not in st.session_state:
    st.session_state.demo_manager = DemoModeManager()

if 'performance_monitor' not in st.session_state:
    st.session_state.performance_monitor = PerformanceMonitor()

if 'show_tour' not in st.session_state:
    st.session_state.show_tour = True

# Header with enhanced branding
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; text-align: center;">🎯 Akio Unified Call Center Platform</h1>
    <p style="text-align: center; margin-top: 0.5rem; opacity: 0.9;">
        Integrating Email Management, Call Analytics, and CRM Systems
    </p>
    <p style="text-align: center; font-size: 0.9rem; opacity: 0.7;">
        Version 1.0 | Internship Project 2025
    </p>
</div>
""", unsafe_allow_html=True)

# Quick tour button
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("👋 Quick Tour", use_container_width=True):
        st.info("Welcome to the Akio Unified Platform! This integrates three powerful services: Email Assistant for customer communications, Call Metrics for performance tracking, and CRM Integration for customer management. Click 'Start All Services' to begin!")

with col2:
    if st.button("🎭 Demo Mode", use_container_width=True, type="secondary"):
        with st.spinner("Activating Demo Mode..."):
            if st.session_state.demo_manager.activate_demo_mode():
                st.success("Demo Mode activated! Check all services for sample data.")
                time.sleep(2)
                st.rerun()

with col3:
    if st.button("🚀 Start All Services", use_container_width=True, type="primary"):
        with st.spinner("Starting all services..."):
            for service_id in SERVICES.keys():
                if st.session_state.service_manager.get_status(service_id) == "offline":
                    st.session_state.service_manager.start_service(service_id)
                    time.sleep(2)
            st.success("All services are starting!")
            time.sleep(3)
            st.rerun()

with col4:
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()

# Main interface with tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Service Manager", "📊 Unified View", "🔧 Performance", "📚 Documentation"])

with tab1:
    st.header("Service Control Panel")
    
    # Service cards grid
    for idx, (service_id, service) in enumerate(SERVICES.items()):
        status = st.session_state.service_manager.get_status(service_id)
        uptime = st.session_state.service_manager.get_service_uptime(service_id)
        
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                st.markdown(f"### {service['icon']}")
            
            with col2:
                st.markdown(f"### {service['name']}")
                st.caption(service['description'])
                st.caption(f"Port: {service['port']} | Path: {service['path']}")
                if status == "online":
                    st.caption(f"Uptime: {uptime}")
            
            with col3:
                if status == "online":
                    st.markdown('<p class="status-online">● Online</p>', unsafe_allow_html=True)
                elif status == "starting":
                    st.markdown('<p class="status-starting">● Starting...</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="status-offline">● Offline</p>', unsafe_allow_html=True)
            
            with col4:
                col_a, col_b = st.columns(2)
                with col_a:
                    if status == "offline":
                        if st.button("▶️ Start", key=f"start_{service_id}", use_container_width=True):
                            success, message = st.session_state.service_manager.start_service(service_id)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                            time.sleep(2)
                            st.rerun()
                    else:
                        if st.button("⏹️ Stop", key=f"stop_{service_id}", use_container_width=True):
                            success, message = st.session_state.service_manager.stop_service(service_id)
                            st.info(message)
                            st.rerun()
                
                with col_b:
                    if status == "online":
                        if st.button("🔗 Open", key=f"open_{service_id}", use_container_width=True):
                            webbrowser.open(service['url'])
        
        st.divider()

with tab2:
    st.header("Unified Platform View")
    
    # Service selector with better UX
    online_services = [(sid, s) for sid, s in SERVICES.items() 
                       if st.session_state.service_manager.get_status(sid) == "online"]
    
    if not online_services:
        st.info("No services are currently running. Use the Service Manager tab or click 'Start All Services' above.")
    else:
        service_names = [s['name'] for _, s in online_services]
        selected_service = st.selectbox("Select a service to view:", service_names)
        
        for service_id, service in online_services:
            if service['name'] == selected_service:
                st.subheader(f"{service['icon']} {service['name']}")
                
                # Responsive iframe height
                iframe_height = 900 if service_id == "crm" else 800
                
                iframe_html = f"""
                <iframe 
                    src="{service['url']}" 
                    width="100%" 
                    height="{iframe_height}"
                    frameborder="0"
                    style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                </iframe>
                """
                st.markdown(iframe_html, unsafe_allow_html=True)
                
                st.caption(f"🔗 Direct link: {service['url']} | 📍 Port: {service['port']}")

with tab3:
    st.header("🔧 System Performance & Health")
    
    # Performance monitoring
    st.session_state.performance_monitor.display_performance_dashboard()
    
    # System information
    st.subheader("📊 Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        online_count = sum(1 for sid in SERVICES 
                          if st.session_state.service_manager.get_status(sid) == "online")
        st.metric("Services Online", f"{online_count}/{len(SERVICES)}")
    
    with col2:
        st.metric("Platform Version", "1.0.0")
    
    with col3:
        st.metric("Total Services", len(SERVICES))
    
    with col4:
        st.metric("Architecture", "Microservices")

with tab4:
    st.header("📚 Platform Documentation")
    
    # Enhanced documentation with code examples
    doc_tabs = st.tabs(["🏗️ Architecture", "🔌 API Reference", "🚀 Deployment", "💡 Best Practices"])
    
    with doc_tabs[0]:
        st.markdown("""
        ## System Architecture
        
        ### Microservices Design
        ```
        ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
        │ Email Assistant │     │  Call Metrics   │     │ CRM Integration │
        │   Port: 8501    │     │  Port: 8502/8000│     │   Port: 3000    │
        └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
                 │                       │                       │
                 └───────────────────────┴───────────────────────┘
                                         │
                                 ┌───────┴────────┐
                                 │ Unified Portal │
                                 │  Port: 8505    │
                                 └────────────────┘
        ```
        
        ### Data Flow
        - **Email → Call**: Email interactions logged as call activities
        - **Call → CRM**: Call records update customer profiles
        - **CRM → Email**: Customer data enriches email responses
        """)
    
    with doc_tabs[1]:
        st.markdown("""
        ## API Reference
        
        ### Email Assistant API
        ```python
        # Get email analytics
        GET /api/analytics
        
        # Generate response
        POST /api/generate-response
        {
            "email": "customer email content",
            "language": "en"
        }
        ```
        
        ### Call Metrics API
        ```python
        # Create call record
        POST /api/calls
        {
            "agent_id": "AGT001",
            "customer_id": "CUST123",
            "duration": 300,
            "outcome": "resolved"
        }
        
        # Get metrics
        GET /api/metrics?start_date=2025-06-01&end_date=2025-06-30
        ```
        """)
    
    with doc_tabs[2]:
        st.markdown("""
        ## Deployment Guide
        
        ### Production Checklist
        - [ ] Configure environment variables
        - [ ] Set up SSL certificates
        - [ ] Configure reverse proxy (Nginx)
        - [ ] Set up monitoring (Prometheus/Grafana)
        - [ ] Configure backup strategy
        - [ ] Implement rate limiting
        - [ ] Set up logging aggregation
        
        ### Docker Deployment
        ```yaml
        version: '3.8'
        services:
          email-assistant:
            build: ./Email-Assistant
            ports:
              - "8501:8501"
            environment:
              - API_KEY=${API_KEY}
        ```
        """)
    
    with doc_tabs[3]:
        st.markdown("""
        ## Best Practices
        
        ### Security
        - Use environment variables for sensitive data
        - Implement API authentication
        - Regular security audits
        - Data encryption at rest and in transit
        
        ### Performance
        - Implement caching strategies
        - Use connection pooling
        - Optimize database queries
        - Monitor resource usage
        
        ### Maintenance
        - Regular backups
        - Log rotation
        - Performance monitoring
        - Automated testing
        """)

# About section
st.markdown("""
<div class="about-section">
    <p><strong>Akio Unified Call Center Platform v1.0</strong></p>
    <p>Developed during internship at Akio | June 2025</p>
    <p>Created by: [Your Name] | Zero external API costs | 100% local execution</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if st.checkbox("Enable auto-refresh (5s)", value=False):
    time.sleep(5)
    st.rerun()