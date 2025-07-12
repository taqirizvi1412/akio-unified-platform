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
