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
