// src/api/hubspot.js - COMPLETE FILE WITH ALL FIXES
const express = require('express');
const axios = require('axios');
const router = express.Router();
const { validateApiKey } = require('./auth');
const { HubSpotError } = require('./errors');
const logger = require('../utils/logger');

// Determine the correct base URL based on API key prefix
function getHubSpotBaseUrl() {
  const apiKey = process.env.HUBSPOT_API_KEY;
  if (apiKey?.startsWith('eu')) {
    return 'https://api.hubapi.eu/crm/v3';  // European data center
  }
  return 'https://api.hubapi.com/crm/v3';   // US data center (default)
}

const HUBSPOT_BASE_URL = getHubSpotBaseUrl();
logger.info(`Using HubSpot API endpoint: ${HUBSPOT_BASE_URL}`);

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
      timestamp: new Date().toISOString(),
      region: HUBSPOT_BASE_URL.includes('.eu') ? 'EU' : 'US'
    });
  } catch (error) {
    logger.error('Connection failed:', { 
      status: error.response?.status, 
      message: error.response?.data?.message 
    });
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
    logger.error('Contact operation failed:', { 
      status: error.response?.status, 
      message: error.response?.data?.message 
    });
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
    logger.error('Call logging failed:', { 
      status: error.response?.status, 
      message: error.response?.data?.message 
    });
    next(new HubSpotError('Failed to log call activity', error.response?.status));
  }
});

// Get contact statistics - FIXED VERSION
router.get('/stats', validateApiKey, async (req, res, next) => {
  try {
    let totalContacts = 0;
    let totalCalls = 0;

    // Get contacts count
    try {
      const contactsResponse = await axios.get(`${HUBSPOT_BASE_URL}/objects/contacts`, {
        headers: {
          'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
          'Content-Type': 'application/json'
        },
        params: { limit: 1 }  // Changed from 0 to 1
      });
      totalContacts = contactsResponse.data.total || 0;
    } catch (error) {
      logger.warn('Could not fetch contacts count:', error.response?.status);
    }

    // Get calls count - may not be available in all accounts
    try {
      const callsResponse = await axios.get(`${HUBSPOT_BASE_URL}/objects/calls`, {
        headers: {
          'Authorization': `Bearer ${process.env.HUBSPOT_API_KEY}`,
          'Content-Type': 'application/json'
        },
        params: { limit: 1 }  // Changed from 0 to 1
      });
      totalCalls = callsResponse.data.total || 0;
    } catch (error) {
      // Calls object might not be available - that's okay
      logger.warn('Could not fetch calls count (this is normal if calls are not enabled):', error.response?.status);
    }

    res.json({
      totalContacts,
      totalCalls,
      timestamp: new Date().toISOString(),
      region: HUBSPOT_BASE_URL.includes('.eu') ? 'EU' : 'US'
    });
  } catch (error) {
    logger.error('Stats fetch failed:', { 
      status: error.response?.status, 
      message: error.response?.data?.message 
    });
    next(new HubSpotError('Failed to fetch statistics', error.response?.status));
  }
});

module.exports = router;