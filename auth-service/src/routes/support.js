const express = require('express');
const validator = require('validator');
const { getSupportRequest } = require('../models');

const router = express.Router();

router.post('/', async (req, res) => {
  try {
    const { user_id, email, subject, message } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    if (!subject || !message) return res.status(400).json({ error: 'Missing fields' });

    const SupportRequest = getSupportRequest();
    const doc = await SupportRequest.create({ user_id, email, subject, message });
    return res.status(201).json({ message: 'Support request received', id: doc._id });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
