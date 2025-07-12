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
