/**
 * Model resolver – returns Mongoose models when MongoDB is connected,
 * otherwise falls back to in-memory stores for local dev/testing.
 */

function getUser() {
  if (global.USE_MEMORY_STORE) {
    return require('./MemoryUser');
  }
  return require('./User');
}

function getSupportRequest() {
  if (global.USE_MEMORY_STORE) {
    return require('./MemorySupport');
  }
  return require('./SupportRequest');
}

module.exports = { getUser, getSupportRequest };
