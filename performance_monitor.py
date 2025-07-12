# performance_monitor.py
import time
import psutil
import requests
from datetime import datetime
import streamlit as st

class PerformanceMonitor:
    """Monitor system performance and service health"""
    
    def __init__(self):
        self.services = {
            "Email Assistant": {"url": "http://localhost:8501", "port": 8501},
            "Call Metrics API": {"url": "http://localhost:8000", "port": 8000},
            "Call Dashboard": {"url": "http://localhost:8502", "port": 8502},
            "CRM Integration": {"url": "http://localhost:3000", "port": 3000}
        }
        
    def get_system_metrics(self):
        """Get current system performance metrics"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": self._get_network_stats(),
            "timestamp": datetime.now().isoformat()
        }
        return metrics
    
    def check_service_health(self):
        """Check health status of all services"""
        health_status = {}
        
        for service_name, config in self.services.items():
            start_time = time.time()
            try:
                response = requests.get(config["url"], timeout=2)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": round(response_time, 2),
                    "status_code": response.status_code,
                    "port": config["port"]
                }
            except requests.exceptions.RequestException:
                health_status[service_name] = {
                    "status": "offline",
                    "response_time": None,
                    "status_code": None,
                    "port": config["port"]
                }
        
        return health_status
    
    def _get_network_stats(self):
        """Get network I/O statistics"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    def display_performance_dashboard(self):
        """Display performance metrics in Streamlit"""
        st.subheader("🔧 System Performance Monitor")
        
        # System metrics
        metrics = self.get_system_metrics()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CPU Usage", f"{metrics['cpu_percent']}%", 
                     delta=f"{metrics['cpu_percent']-50:.1f}%" if metrics['cpu_percent'] > 50 else None)
        
        with col2:
            st.metric("Memory Usage", f"{metrics['memory_percent']}%",
                     delta=f"{metrics['memory_percent']-70:.1f}%" if metrics['memory_percent'] > 70 else None)
        
        with col3:
            st.metric("Disk Usage", f"{metrics['disk_usage']}%")
        
        with col4:
            st.metric("Network I/O", f"{metrics['network_io']['bytes_sent']/(1024*1024):.1f} MB sent")
        
        # Service health
        st.subheader("🏥 Service Health Status")
        health_status = self.check_service_health()
        
        for service, status in health_status.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                if status['status'] == 'healthy':
                    st.success(f"✅ {service}")
                elif status['status'] == 'unhealthy':
                    st.warning(f"⚠️ {service}")
                else:
                    st.error(f"❌ {service}")
            
            with col2:
                if status['response_time']:
                    st.text(f"Response: {status['response_time']}ms")
                else:
                    st.text("No response")
            
            with col3:
                st.text(f"Port: {status['port']}")

# Integration with unified_platform.py
def add_performance_monitoring():
    """Add performance monitoring to unified platform"""
    monitor = PerformanceMonitor()
    
    with st.expander("🔧 System Performance", expanded=False):
        monitor.display_performance_dashboard()
        
        # Auto-refresh option
        if st.checkbox("Auto-refresh performance metrics (5s)", key="perf_refresh"):
            time.sleep(5)
            st.rerun()