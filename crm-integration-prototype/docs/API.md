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
