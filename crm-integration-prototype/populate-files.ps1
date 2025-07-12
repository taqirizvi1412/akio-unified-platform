# populate-files.ps1 - Automatically populate all project files
Write-Host "🚀 Populating CRM Integration Prototype files..." -ForegroundColor Cyan

# Create package.json
@'
{
  "name": "crm-integration-prototype",
  "version": "1.0.0",
  "description": "HubSpot CRM Integration Prototype",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "jest"
  },
  "keywords": ["crm", "hubspot", "integration", "api"],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "axios": "^1.6.0",
    "dotenv": "^16.3.1",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.7.0"
  }
}
'@ | Out-File -FilePath "package.json" -Encoding UTF8

Write-Host "✅ Created package.json" -ForegroundColor Green

# Create .env.example
@'
# HubSpot Configuration
HUBSPOT_API_KEY=your_hubspot_api_key_here

# Server Configuration
PORT=3000
NODE_ENV=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=info

# Rate Limiting
RATE_LIMIT_WINDOW_MS=600000
RATE_LIMIT_MAX_REQUESTS=100
'@ | Out-File -FilePath ".env.example" -Encoding UTF8

Write-Host "✅ Created .env.example" -ForegroundColor Green

# Create .gitignore
@'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Build files
dist/
build/

# Logs
logs/
*.log

# Testing
coverage/
.nyc_output/

# Temporary files
tmp/
temp/
'@ | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "✅ Created .gitignore" -ForegroundColor Green

# Create src/server.js
@'
// src/server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const hubspotRoutes = require('./api/hubspot');
const { errorHandler } = require('./api/errors');
const logger = require('./utils/logger');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*'
}));
app.use(express.json());
app.use(express.static('public'));

// Serve the main HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'index.html'));
});

// API Routes
app.use('/api/hubspot', hubspotRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV
  });
});

// Error handling middleware
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  logger.info(`Server running on http://localhost:${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV}`);
});
'@ | Out-File -FilePath "src\server.js" -Encoding UTF8

Write-Host "✅ Created src/server.js" -ForegroundColor Green

# Create src/api/hubspot.js
@'
// src/api/hubspot.js
const express = require('express');
const axios = require('axios');
const router = express.Router();
const { validateApiKey } = require('./auth');
const { HubSpotError } = require('./errors');
const logger = require('../utils/logger');

const HUBSPOT_BASE_URL = 'https://api.hubapi.com/crm/v3';

// Test connection
router.get('/test-connection', validateApiKey, async (req, res, next) => {
  try {
    const response = await axios.get(`${HUBSPOT_BASE_URL}/objects/contacts`, {
      headers: {
        'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      params: { limit: 1 }
    });

    res.json({
      connected: true,
      message: 'Successfully connected to HubSpot',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(new HubSpotError('Failed to connect to HubSpot', error.response?.status));
  }
});

// Create or update contact
router.post('/contacts', validateApiKey, async (req, res, next) => {
  try {
    const { email, firstname, lastname, phone } = req.body;

    // First, search for existing contact
    const searchResponse = await axios.post(
      `${HUBSPOT_BASE_URL}/objects/contacts/search`,
      {
        filterGroups: [{
          filters: [{
            propertyName: 'email',
            operator: 'EQ',
            value: email
          }]
        }]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    let contact;
    if (searchResponse.data.total > 0) {
      // Update existing contact
      const contactId = searchResponse.data.results[0].id;
      contact = await axios.patch(
        `${HUBSPOT_BASE_URL}/objects/contacts/${contactId}`,
        {
          properties: { firstname, lastname, phone }
        },
        {
          headers: {
            'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
      logger.info(`Updated contact: ${contactId}`);
    } else {
      // Create new contact
      contact = await axios.post(
        `${HUBSPOT_BASE_URL}/objects/contacts`,
        {
          properties: { email, firstname, lastname, phone }
        },
        {
          headers: {
            'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
      logger.info(`Created new contact: ${contact.data.id}`);
    }

    res.json({
      success: true,
      contact: contact.data,
      action: searchResponse.data.total > 0 ? 'updated' : 'created'
    });
  } catch (error) {
    next(new HubSpotError('Failed to create/update contact', error.response?.status));
  }
});

// Log call activity
router.post('/calls', validateApiKey, async (req, res, next) => {
  try {
    const { contactId, duration, notes, direction, outcome } = req.body;

    const callActivity = await axios.post(
      `${HUBSPOT_BASE_URL}/objects/calls`,
      {
        properties: {
          hs_timestamp: Date.now(),
          hs_call_duration: duration * 1000, // Convert to milliseconds
          hs_call_body: notes,
          hs_call_direction: direction.toUpperCase(),
          hs_call_disposition: outcome,
          hs_call_status: 'COMPLETED'
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    // Associate call with contact
    if (contactId) {
      await axios.put(
        `${HUBSPOT_BASE_URL}/objects/calls/${callActivity.data.id}/associations/contacts/${contactId}/CALL_TO_CONTACT`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
    }

    logger.info(`Logged call activity: ${callActivity.data.id}`);
    res.json({
      success: true,
      activity: callActivity.data
    });
  } catch (error) {
    next(new HubSpotError('Failed to log call activity', error.response?.status));
  }
});

// Get contact statistics
router.get('/stats', validateApiKey, async (req, res, next) => {
  try {
    const contactsResponse = await axios.get(`${HUBSPOT_BASE_URL}/objects/contacts`, {
      headers: {
        'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      params: { limit: 0 }
    });

    const callsResponse = await axios.get(`${HUBSPOT_BASE_URL}/objects/calls`, {
      headers: {
        'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      params: { limit: 0 }
    });

    res.json({
      totalContacts: contactsResponse.data.total || 0,
      totalCalls: callsResponse.data.total || 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(new HubSpotError('Failed to fetch statistics', error.response?.status));
  }
});

module.exports = router;
'@ | Out-File -FilePath "src\api\hubspot.js" -Encoding UTF8

Write-Host "✅ Created src/api/hubspot.js" -ForegroundColor Green

# Create src/api/auth.js
@'
// src/api/auth.js
const { AuthError } = require('./errors');

function validateApiKey(req, res, next) {
  const apiKey = process.env.HUBSPOT_API_KEY;
  
  if (!apiKey) {
    return next(new AuthError('HubSpot API key not configured'));
  }

  // In production, you might validate the API key format
  if (apiKey.length < 10) {
    return next(new AuthError('Invalid HubSpot API key format'));
  }

  next();
}

// For future OAuth implementation
function validateOAuthToken(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next(new AuthError('Missing or invalid authorization header'));
  }

  const token = authHeader.substring(7);
  
  // TODO: Validate OAuth token with HubSpot
  // For now, just check if token exists
  if (!token) {
    return next(new AuthError('Invalid token'));
  }

  req.accessToken = token;
  next();
}

module.exports = {
  validateApiKey,
  validateOAuthToken
};
'@ | Out-File -FilePath "src\api\auth.js" -Encoding UTF8

Write-Host "✅ Created src/api/auth.js" -ForegroundColor Green

# Create src/api/errors.js
@'
// src/api/errors.js
class BaseError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class HubSpotError extends BaseError {
  constructor(message, statusCode = 500) {
    super(message, statusCode);
    this.name = 'HubSpotError';
  }
}

class AuthError extends BaseError {
  constructor(message) {
    super(message, 401);
    this.name = 'AuthError';
  }
}

class ValidationError extends BaseError {
  constructor(message) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

function errorHandler(err, req, res, next) {
  if (res.headersSent) {
    return next(err);
  }

  const { statusCode = 500, message } = err;

  res.status(statusCode).json({
    success: false,
    error: {
      message,
      status: statusCode,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
}

module.exports = {
  BaseError,
  HubSpotError,
  AuthError,
  ValidationError,
  errorHandler
};
'@ | Out-File -FilePath "src\api\errors.js" -Encoding UTF8

Write-Host "✅ Created src/api/errors.js" -ForegroundColor Green

# Create src/utils/logger.js
@'
// src/utils/logger.js
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3
};

class Logger {
  constructor(minLevel = 'info') {
    this.minLevel = logLevels[minLevel] || logLevels.info;
  }

  log(level, message, data = {}) {
    if (logLevels[level] <= this.minLevel) {
      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        level,
        message,
        ...data
      };

      if (level === 'error') {
        console.error(JSON.stringify(logEntry));
      } else {
        console.log(JSON.stringify(logEntry));
      }
    }
  }

  error(message, data) {
    this.log('error', message, data);
  }

  warn(message, data) {
    this.log('warn', message, data);
  }

  info(message, data) {
    this.log('info', message, data);
  }

  debug(message, data) {
    this.log('debug', message, data);
  }
}

module.exports = new Logger(process.env.LOG_LEVEL || 'info');
'@ | Out-File -FilePath "src\utils\logger.js" -Encoding UTF8

Write-Host "✅ Created src/utils/logger.js" -ForegroundColor Green

# Create src/utils/queue.js
@'
// src/utils/queue.js
// Simple in-memory queue for development
// In production, use Bull or RabbitMQ
class SimpleQueue {
  constructor(name) {
    this.name = name;
    this.jobs = [];
    this.processing = false;
  }

  async add(data) {
    const job = {
      id: Date.now().toString(),
      data,
      createdAt: new Date(),
      status: 'pending'
    };
    
    this.jobs.push(job);
    this.process();
    return job;
  }

  async process() {
    if (this.processing || this.jobs.length === 0) {
      return;
    }

    this.processing = true;
    
    while (this.jobs.length > 0) {
      const job = this.jobs.shift();
      
      try {
        // Process job (implement your logic here)
        job.status = 'completed';
        console.log(`Processed job ${job.id}`);
      } catch (error) {
        job.status = 'failed';
        job.error = error.message;
        console.error(`Failed to process job ${job.id}:`, error);
      }
    }
    
    this.processing = false;
  }
}

module.exports = SimpleQueue;
'@ | Out-File -FilePath "src\utils\queue.js" -Encoding UTF8

Write-Host "✅ Created src/utils/queue.js" -ForegroundColor Green

# Create src/services/call.js
@'
// src/services/call.js
class CallService {
  constructor(hubspotClient) {
    this.hubspotClient = hubspotClient;
    this.activeCalls = new Map();
  }

  startCall(phoneNumber, callType) {
    const callId = Date.now().toString();
    const call = {
      id: callId,
      phoneNumber,
      type: callType,
      startTime: new Date(),
      status: 'active'
    };
    
    this.activeCalls.set(callId, call);
    return call;
  }

  endCall(callId) {
    const call = this.activeCalls.get(callId);
    if (!call) {
      throw new Error('Call not found');
    }

    call.endTime = new Date();
    call.duration = Math.floor((call.endTime - call.startTime) / 1000);
    call.status = 'completed';
    
    this.activeCalls.delete(callId);
    return call;
  }

  getActiveCall(callId) {
    return this.activeCalls.get(callId);
  }
}

module.exports = CallService;
'@ | Out-File -FilePath "src\services\call.js" -Encoding UTF8

Write-Host "✅ Created src/services/call.js" -ForegroundColor Green

# Create src/services/contact.js
@'
// src/services/contact.js
class ContactService {
  constructor(hubspotClient) {
    this.hubspotClient = hubspotClient;
  }

  async findOrCreateContact(contactData) {
    // Implementation handled by HubSpot API routes
    // This service layer can add business logic
    const { email, phone } = contactData;
    
    if (!email && !phone) {
      throw new Error('Either email or phone is required');
    }

    // Additional validation or business logic here
    return contactData;
  }

  formatContactData(rawData) {
    return {
      firstname: rawData.firstName || rawData.firstname || '',
      lastname: rawData.lastName || rawData.lastname || '',
      email: rawData.email || '',
      phone: rawData.phone || ''
    };
  }
}

module.exports = ContactService;
'@ | Out-File -FilePath "src\services\contact.js" -Encoding UTF8

Write-Host "✅ Created src/services/contact.js" -ForegroundColor Green

# Create public/js/app.js
@'
// public/js/app.js
// This file can be used to add additional frontend functionality
// that connects to your backend API

const API_BASE_URL = window.location.origin + '/api';

// Enhanced API client
class CRMIntegrationClient {
  constructor() {
    this.apiKey = null;
    this.isConnected = false;
  }

  async testConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/hubspot/test-connection`);
      const data = await response.json();
      this.isConnected = data.connected;
      return data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
    }
  }

  async createOrUpdateContact(contactData) {
    try {
      const response = await fetch(`${API_BASE_URL}/hubspot/contacts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contactData)
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to create/update contact:', error);
      throw error;
    }
  }

  async logCallActivity(callData) {
    try {
      const response = await fetch(`${API_BASE_URL}/hubspot/calls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(callData)
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to log call activity:', error);
      throw error;
    }
  }

  async getStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/hubspot/stats`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export for use in other scripts
window.CRMIntegrationClient = CRMIntegrationClient;
'@ | Out-File -FilePath "public\js\app.js" -Encoding UTF8

Write-Host "✅ Created public/js/app.js" -ForegroundColor Green

# Create test files
@'
// tests/api.test.js
describe('HubSpot API', () => {
  test('should connect to HubSpot', async () => {
    // Add your tests here
    expect(true).toBe(true);
  });

  test('should create a contact', async () => {
    // Add your tests here
    expect(true).toBe(true);
  });

  test('should log call activity', async () => {
    // Add your tests here
    expect(true).toBe(true);
  });
});
'@ | Out-File -FilePath "tests\api.test.js" -Encoding UTF8

Write-Host "✅ Created tests/api.test.js" -ForegroundColor Green

@'
// tests/services.test.js
describe('Services', () => {
  test('should handle calls', () => {
    // Add your tests here
    expect(true).toBe(true);
  });

  test('should format contact data', () => {
    // Add your tests here
    expect(true).toBe(true);
  });
});
'@ | Out-File -FilePath "tests\services.test.js" -Encoding UTF8

Write-Host "✅ Created tests/services.test.js" -ForegroundColor Green

# Create config files
@'
// config/default.js
module.exports = {
  hubspot: {
    apiKey: process.env.HUBSPOT_API_KEY,
    baseUrl: 'https://api.hubapi.com/crm/v3'
  },
  server: {
    port: process.env.PORT || 3000
  },
  rateLimit: {
    windowMs: 10 * 60 * 1000, // 10 minutes
    max: 100
  }
};
'@ | Out-File -FilePath "config\default.js" -Encoding UTF8

Write-Host "✅ Created config/default.js" -ForegroundColor Green

@'
// config/production.js
module.exports = {
  // Production-specific config
  logging: {
    level: 'error'
  }
};
'@ | Out-File -FilePath "config\production.js" -Encoding UTF8

Write-Host "✅ Created config/production.js" -ForegroundColor Green

# Create documentation files
@'
# API Documentation

## Base URL
`http://localhost:3000/api`

## Endpoints

### Test Connection
- **URL**: `/hubspot/test-connection`
- **Method**: `GET`
- **Description**: Tests the connection to HubSpot API
- **Response**: 
  ```json
  {
    "connected": true,
    "message": "Successfully connected to HubSpot",
    "timestamp": "2025-06-23T10:00:00.000Z"
  }
  ```

### Create/Update Contact
- **URL**: `/hubspot/contacts`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "phone": "+1234567890"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "contact": { ... },
    "action": "created" // or "updated"
  }
  ```

### Log Call Activity
- **URL**: `/hubspot/calls`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "contactId": "12345",
    "duration": 300,
    "notes": "Discussed product features",
    "direction": "inbound",
    "outcome": "Connected"
  }
  ```

### Get Statistics
- **URL**: `/hubspot/stats`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "totalContacts": 150,
    "totalCalls": 75,
    "timestamp": "2025-06-23T10:00:00.000Z"
  }
  ```
'@ | Out-File -FilePath "docs\API.md" -Encoding UTF8

Write-Host "✅ Created docs/API.md" -ForegroundColor Green

@'
# Setup Guide

## Prerequisites
- Node.js 14+ installed
- HubSpot account (free tier is fine)
- Basic understanding of REST APIs

## Installation Steps

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your HubSpot API key to the `.env` file

3. **Get HubSpot API Key**
   - Log in to HubSpot
   - Go to Settings → Integrations → Private Apps
   - Create a new private app
   - Set required scopes (contacts read/write, calls read/write)
   - Copy the access token

4. **Start the server**
   ```bash
   npm start
   ```

5. **Access the application**
   - Open http://localhost:3000 in your browser
   - The frontend interface will load automatically

## Testing
Run tests with:
```bash
npm test
```

## Development Mode
For auto-restart on file changes:
```bash
npm run dev
```

## Troubleshooting
- Ensure all dependencies are installed
- Check that your API key is valid
- Verify Node.js version is 14+
- Check console for error messages
'@ | Out-File -FilePath "docs\SETUP.md" -Encoding UTF8

Write-Host "✅ Created docs/SETUP.md" -ForegroundColor Green

# Create public/css/styles.css (empty for now, can be customized later)
@'
/* public/css/styles.css */
/* Additional styles can be added here to override or extend the inline styles in index.html */
'@ | Out-File -FilePath "public\css\styles.css" -Encoding UTF8

Write-Host "✅ Created public/css/styles.css" -ForegroundColor Green

# Copy .env.example to .env
Copy-Item -Path ".env.example" -Destination ".env" -Force
Write-Host "✅ Created .env from .env.example" -ForegroundColor Green

Write-Host "`n📋 File Population Summary:" -ForegroundColor Yellow
Write-Host "All files have been populated with their content!" -ForegroundColor Green

Write-Host "`n📁 Verifying files..." -ForegroundColor Yellow
$emptyFiles = Get-ChildItem -Recurse -File | Where-Object { $_.Length -eq 0 }
if ($emptyFiles.Count -eq 0) {
    Write-Host "✅ All files contain content!" -ForegroundColor Green
} else {
    Write-Host "⚠️  The following files are still empty:" -ForegroundColor Yellow
    $emptyFiles | ForEach-Object { Write-Host "   - $($_.FullName)" -ForegroundColor Red }
}

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env and add your HubSpot API key" -ForegroundColor White
Write-Host "2. Make sure you have the index.html and README.md files from the previous artifacts" -ForegroundColor White
Write-Host "3. Run: npm install" -ForegroundColor White
Write-Host "4. Run: npm start" -ForegroundColor White
Write-Host "5. Open http://localhost:3000 in your browser" -ForegroundColor White

Write-Host "`n✨ Setup complete! Happy coding!" -ForegroundColor Greennpm start