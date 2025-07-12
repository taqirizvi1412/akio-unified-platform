# HubSpot CRM Integration Prototype

A demonstration prototype showing how to integrate call center operations with HubSpot CRM, featuring automatic contact management and call activity logging.

## 🚀 Overview

This prototype demonstrates key concepts for building production-ready CRM integrations:
- API authentication and connection management
- Real-time contact creation/updates
- Automatic call activity logging
- Visual integration flow monitoring
- Comprehensive error handling

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Integration](#api-integration)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **API Connection Management**: Secure connection to HubSpot using API keys
- **Contact Management**: Automatic creation and updates of customer records
- **Call Logging**: Detailed activity tracking with duration and outcomes
- **Real-time Monitoring**: Live activity feed and statistics dashboard
- **Error Handling**: Comprehensive error management and retry logic

### User Interface
- **Visual Integration Flow**: Step-by-step process visualization
- **Call Simulator**: Test the integration with mock calls
- **Activity Log**: Real-time event tracking with timestamps
- **Statistics Dashboard**: Key metrics at a glance
- **Setup Guide**: Built-in documentation for getting started

## 🔧 Prerequisites

### For the Prototype
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No installation required - runs entirely in browser

### For Production Implementation
- Node.js 14+ or Python 3.8+
- HubSpot account (free tier available)
- Basic understanding of REST APIs
- OAuth 2.0 knowledge (for production auth)

## 🏃 Quick Start

### Using the Prototype

1. **Open the HTML file** in your web browser
2. **Get a HubSpot API Key**:
   - Sign up for free at [HubSpot](https://app.hubspot.com/signup)
   - Navigate to Settings → Integrations → API Key
   - Generate and copy your API key
3. **Connect to HubSpot**:
   - Paste your API key in the connection field
   - Click "Connect to HubSpot"
4. **Simulate a Call**:
   - Enter customer details
   - Click "Start Call"
   - Click "End Call" to log the activity

### Setting Up for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/crm-integration-prototype.git
cd crm-integration-prototype

# For Node.js backend
npm init -y
npm install express axios dotenv

# For Python backend
pip install flask requests python-dotenv
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Call System   │────▶│  Integration    │────▶│   HubSpot CRM   │
│   (Frontend)    │     │    Service      │     │      API        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Call Triggers  │     │  Data Mapping   │     │  CRM Records    │
│  - Start Call   │     │  - Contacts     │     │  - Contacts     │
│  - End Call     │     │  - Activities   │     │  - Call Logs    │
│  - Call Details │     │  - Properties   │     │  - Properties   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Data Flow

1. **Call Initiation** → Trigger integration
2. **Contact Lookup** → Search existing records
3. **Create/Update** → Manage contact data
4. **Log Activity** → Record call details
5. **Update UI** → Show confirmation

## 🔌 API Integration

### Authentication

#### Development (API Key)
```javascript
const headers = {
  'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
  'Content-Type': 'application/json'
};
```

#### Production (OAuth 2.0)
```javascript
// Authorization URL
const authUrl = `https://app.hubspot.com/oauth/authorize?
  client_id=${CLIENT_ID}&
  redirect_uri=${REDIRECT_URI}&
  scope=crm.objects.contacts.write`;

// Token exchange
const tokenResponse = await axios.post(
  'https://api.hubapi.com/oauth/v1/token',
  {
    grant_type: 'authorization_code',
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    redirect_uri: REDIRECT_URI,
    code: authorizationCode
  }
);
```

### Core API Endpoints

#### Create Contact
```javascript
POST /crm/v3/objects/contacts
{
  "properties": {
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "phone": "+1234567890"
  }
}
```

#### Search Contacts
```javascript
POST /crm/v3/objects/contacts/search
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "email",
      "operator": "EQ",
      "value": "john@example.com"
    }]
  }]
}
```

#### Log Call Activity
```javascript
POST /crm/v3/objects/calls
{
  "properties": {
    "hs_timestamp": "1640995200000",
    "hs_call_duration": "300000",
    "hs_call_direction": "INBOUND",
    "hs_call_status": "COMPLETED"
  }
}
```

## 📖 Usage Guide

### Basic Workflow

1. **Setup Connection**
   ```javascript
   const client = new HubSpotClient(apiKey);
   await client.testConnection();
   ```

2. **Handle Incoming Call**
   ```javascript
   async function handleIncomingCall(phoneNumber) {
     // Search for existing contact
     const contact = await client.searchContactByPhone(phoneNumber);
     
     if (!contact) {
       // Create new contact
       contact = await client.createContact({
         phone: phoneNumber,
         lifecyclestage: 'lead'
       });
     }
     
     return contact;
   }
   ```

3. **Log Call Activity**
   ```javascript
   async function logCallActivity(contactId, callData) {
     const activity = await client.createCallActivity({
       contactId,
       duration: callData.duration,
       notes: callData.notes,
       outcome: callData.outcome
     });
     
     return activity;
   }
   ```

### Advanced Features

#### Batch Operations
```javascript
// Create multiple contacts
const contacts = await client.batchCreateContacts([
  { email: 'user1@example.com', firstname: 'User1' },
  { email: 'user2@example.com', firstname: 'User2' }
]);
```

#### Custom Properties
```javascript
// Define custom property
await client.createProperty('contacts', {
  name: 'call_preference',
  label: 'Preferred Call Time',
  type: 'enumeration',
  options: ['morning', 'afternoon', 'evening']
});
```

#### Webhooks
```javascript
// Subscribe to contact updates
await client.createWebhookSubscription({
  eventType: 'contact.propertyChange',
  propertyName: 'lifecyclestage',
  callbackUrl: 'https://your-app.com/webhooks/hubspot'
});
```

## 💻 Development

### Project Structure
```
crm-integration-prototype/
├── index.html           # Frontend prototype
├── README.md           # This file
├── src/
│   ├── api/           # API integration modules
│   │   ├── hubspot.js # HubSpot client
│   │   ├── auth.js    # Authentication logic
│   │   └── errors.js  # Error handling
│   ├── services/      # Business logic
│   │   ├── call.js    # Call management
│   │   └── contact.js # Contact management
│   └── utils/         # Utilities
│       ├── logger.js  # Logging
│       └── queue.js   # Job queue
├── tests/             # Test files
├── config/            # Configuration
└── docs/             # Documentation
```

### Environment Variables
```bash
# .env file
HUBSPOT_API_KEY=your_api_key_here
HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_client_secret
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
NODE_ENV=development
```

### Testing

```javascript
// Unit test example
describe('HubSpot Integration', () => {
  it('should create a contact', async () => {
    const contact = await client.createContact({
      email: 'test@example.com',
      firstname: 'Test'
    });
    
    expect(contact.properties.email).toBe('test@example.com');
  });
  
  it('should handle rate limits', async () => {
    // Test rate limit handling
    const promises = Array(150).fill().map(() => 
      client.getContact('123')
    );
    
    await expect(Promise.all(promises)).resolves.toBeDefined();
  });
});
```

## 🚀 Production Deployment

### Security Considerations

1. **API Key Storage**
   - Never commit API keys to version control
   - Use environment variables or secrets management
   - Rotate keys regularly

2. **OAuth Implementation**
   - Implement proper token refresh logic
   - Store tokens securely (encrypted)
   - Handle token expiration gracefully

3. **Data Protection**
   - Encrypt sensitive data in transit and at rest
   - Implement proper access controls
   - Follow GDPR/CCPA compliance

### Performance Optimization

1. **Caching**
   ```javascript
   const cache = new Redis();
   
   async function getContact(id) {
     const cached = await cache.get(`contact:${id}`);
     if (cached) return JSON.parse(cached);
     
     const contact = await hubspot.getContact(id);
     await cache.setex(`contact:${id}`, 3600, JSON.stringify(contact));
     
     return contact;
   }
   ```

2. **Rate Limiting**
   ```javascript
   const limiter = rateLimit({
     windowMs: 10 * 1000, // 10 seconds
     max: 100 // HubSpot limit
   });
   ```

3. **Queue Processing**
   ```javascript
   const queue = new Bull('hubspot-sync');
   
   queue.process(async (job) => {
     const { action, data } = job.data;
     
     switch (action) {
       case 'createContact':
         return await createContact(data);
       case 'logCall':
         return await logCallActivity(data);
     }
   });
   ```

### Monitoring

```javascript
// Health check endpoint
app.get('/health', async (req, res) => {
  const checks = {
    api: await checkHubSpotConnection(),
    database: await checkDatabaseConnection(),
    queue: await checkQueueHealth()
  };
  
  const healthy = Object.values(checks).every(check => check);
  res.status(healthy ? 200 : 503).json({ checks });
});
```

## 🔧 Troubleshooting

### Common Issues

#### Connection Failed
- Verify API key is correct
- Check network connectivity
- Ensure HubSpot services are operational

#### Rate Limit Errors
- Implement exponential backoff
- Use batch operations where possible
- Cache frequently accessed data

#### Data Sync Issues
- Verify field mappings
- Check for required fields
- Validate data formats

### Debug Mode

```javascript
// Enable debug logging
process.env.DEBUG = 'hubspot:*';

// Detailed request logging
client.on('request', (config) => {
  console.log('Request:', config);
});

client.on('response', (response) => {
  console.log('Response:', response.status, response.data);
});
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Use ESLint configuration
- Follow naming conventions
- Write comprehensive tests
- Document all functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- HubSpot for their excellent API documentation
- The open-source community for inspiration
- Contributors who help improve this project

---

For questions or support, please open an issue or contact [taqirizvi1412@gmail.com]