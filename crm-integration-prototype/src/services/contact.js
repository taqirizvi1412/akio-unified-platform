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
