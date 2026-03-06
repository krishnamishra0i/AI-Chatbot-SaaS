/**
 * In-memory support request store (dev mode)
 */

const requests = [];
let idCounter = 1;

const MemorySupportModel = {
  async create(data) {
    const doc = {
      _id: `sup_${Date.now()}_${idCounter++}`,
      user_id: data.user_id || null,
      email: data.email,
      subject: data.subject,
      message: data.message,
      createdAt: new Date()
    };
    requests.push(doc);
    return doc;
  },

  async find(query) {
    if (!query) return [...requests];
    return requests.filter(r => {
      if (query.email && r.email !== query.email) return false;
      if (query.user_id && r.user_id !== query.user_id) return false;
      return true;
    });
  }
};

module.exports = MemorySupportModel;
