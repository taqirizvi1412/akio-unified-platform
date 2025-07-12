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
