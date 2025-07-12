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
