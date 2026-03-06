/**
 * In-memory user store for development mode (no MongoDB required)
 * Implements the same interface as Mongoose User model
 */
const bcrypt = require('bcrypt');

const users = new Map(); // email -> user object
let idCounter = 1;

function genId() {
  return `mem_${Date.now()}_${idCounter++}`;
}

class MemoryUser {
  constructor(data) {
    this._id = data._id || genId();
    this.name = data.name || '';
    this.email = (data.email || '').toLowerCase();
    this.password = data.password || '';
    this.isVerified = data.isVerified || false;
    this.otp = data.otp || null;
    this.otpExpiry = data.otpExpiry || null;
    this.otpAttempts = data.otpAttempts || 0;
    this.lockedUntil = data.lockedUntil || null;
    this.provider = data.provider || 'local';
    this.googleId = data.googleId || null;
    this.createdAt = data.createdAt || new Date();
  }

  async save() {
    users.set(this.email, this);
    return this;
  }

  toJSON() {
    const obj = { ...this };
    delete obj.password;
    delete obj.otp;
    delete obj.otpExpiry;
    delete obj.otpAttempts;
    delete obj.lockedUntil;
    return obj;
  }
}

// Static query methods (mimic Mongoose)
const MemoryUserModel = {
  async create(data) {
    if (users.has((data.email || '').toLowerCase())) {
      const err = new Error('Duplicate key');
      err.code = 11000;
      throw err;
    }
    const user = new MemoryUser(data);
    users.set(user.email, user);
    return user;
  },

  async findOne(query) {
    if (query.email) return users.get(query.email.toLowerCase()) || null;
    if (query.googleId) {
      for (const u of users.values()) {
        if (u.googleId === query.googleId) return u;
      }
    }
    return null;
  },

  async findById(id) {
    for (const u of users.values()) {
      if (u._id === id) return u;
    }
    return null;
  },

  async findByIdAndUpdate(id, update, opts) {
    const user = await this.findById(id);
    if (!user) return null;
    Object.assign(user, update);
    return user;
  },

  async deleteOne(query) {
    if (query.email) users.delete(query.email.toLowerCase());
    return { deletedCount: 1 };
  },

  // Support chaining (select)
  findByIdChain(id) {
    const self = this;
    return {
      select() { return self.findById(id); }
    };
  }
};

// Patch findById to support .select() chain
const origFindById = MemoryUserModel.findById.bind(MemoryUserModel);
MemoryUserModel.findById = function(id) {
  const promise = origFindById(id);
  promise.select = function() { return this; };
  return promise;
};

module.exports = MemoryUserModel;
