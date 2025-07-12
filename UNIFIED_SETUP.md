# 🎯 Akio Unified Platform - Quick Setup Guide

## 🚀 One-Click Setup

### Windows:
```bash
# Double-click start_platform.bat
# OR run in terminal:
./start_platform.bat
```

### Mac/Linux:
```bash
# Make script executable (first time only)
chmod +x start_platform.sh

# Run the platform
./start_platform.sh
```

## 📋 What Happens:

1. **Checks Prerequisites**: Python 3.7+ and Node.js
2. **Installs Dependencies**: All Python packages
3. **Sets Up CRM**: Installs Node modules if needed
4. **Launches Dashboard**: Opens at http://localhost:8501

## 🎮 Using the Platform:

### Service Manager Tab:
- **Start All**: Launches all services with one click
- **Individual Control**: Start/stop services separately
- **Status Monitor**: See what's running
- **Direct Access**: Open services in new tabs

### Unified View Tab:
- **Embedded View**: Use services without switching tabs
- **Quick Switch**: Dropdown to change between services
- **Integrated Experience**: Everything in one place

## 🛠️ Manual Start (if needed):

### 1. Email Assistant:
```bash
cd Akio-stage
streamlit run email_assistant.py
```

### 2. Call Metrics API:
```bash
cd Call-Metrics-Dashboard
python main.py
```

### 3. Call Metrics Dashboard:
```bash
cd Call-Metrics-Dashboard
streamlit run dashboard.py --server.port 8502
```

### 4. CRM Integration:
```bash
cd crm-integration-prototype
npm start
```

## 📍 Service URLs:

- **Unified Platform**: http://localhost:8501
- **Email Assistant**: http://localhost:8501 (same port)
- **Call API**: http://localhost:8000
- **Call Dashboard**: http://localhost:8502
- **CRM**: http://localhost:3000

## ⚠️ Troubleshooting:

### "Port already in use":
- Another service is using that port
- Stop all services and restart

### "Module not found":
- Run: `pip install -r requirements_unified.txt`

### "Cannot find Node modules":
- Run: `cd crm-integration-prototype && npm install`

### Services not starting:
- Check the terminal for error messages
- Ensure all dependencies are installed

## 💡 Tips:

1. **First Time**: Let everything install (may take 2-3 minutes)
2. **Demo Mode**: Start all services for full experience
3. **Development**: Start only what you need
4. **Shutdown**: Ctrl+C in terminal stops everything

## 🎯 For Your Presentation:

1. Start with the Unified Platform
2. Show how all services integrate
3. Demonstrate individual features
4. Highlight the cost-free architecture

---

**Remember**: Everything runs locally = $0 cost! 🎉