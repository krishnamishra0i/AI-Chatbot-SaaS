const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const validator = require('validator');

const { getUser } = require('../models');
const { verifyJWT } = require('../middleware/auth');
const { generateOtp } = require('../utils/otp');
const { sendOtpEmail } = require('../utils/email');

const router = express.Router();

const otpLimiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
  max: parseInt(process.env.RATE_LIMIT_MAX || '5', 10),
  message: { error: 'Too many OTP requests, please try later' }
});

// Signup
router.post('/signup', otpLimiter, async (req, res) => {
  try {
    const { name, email, password } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    if (!password || password.length < 8) return res.status(400).json({ error: 'Password must be at least 8 chars' });

    const User = getUser();
    // const existing = await User.findOne({ email: email.toLowerCase() });
    // if (existing) return res.status(409).json({ error: 'Email already registered' });

    const hashed = await bcrypt.hash(password, 12);
    const otp = generateOtp(parseInt(process.env.OTP_LENGTH || '6', 10));
    console.log('OTP:', otp);
    
    const otpExpiry = new Date(Date.now() + (parseInt(process.env.OTP_TTL_MINUTES || '10', 10) * 60 * 1000));

    const user = await User.create({ name, email: email.toLowerCase(), password: hashed, otp, otpExpiry });
    await sendOtpEmail(user.email, otp);
    // console.log(res);
    // if (process.env.DISABLE_EMAIL !== 'true') await sendOtpEmail(user.email, otp);

    return res.status(201).json({ message: 'User created, OTP sent', user_id: user._id });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Verify OTP
router.post('/verify-otp', async (req, res) => {
  try {
    const { email, otp } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    const User = getUser();
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Check locked
    if (user.lockedUntil && user.lockedUntil > new Date()) {
      return res.status(429).json({ error: 'Too many attempts, try later' });
    }

    if (user.otp !== otp) {
      user.otpAttempts = (user.otpAttempts || 0) + 1;
      if (user.otpAttempts >= parseInt(process.env.OTP_MAX_ATTEMPTS || '5', 10)) {
        user.lockedUntil = new Date(Date.now() + (parseInt(process.env.OTP_LOCK_MINUTES || '15', 10) * 60 * 1000));
      }
      await user.save();
      return res.status(400).json({ error: 'Invalid OTP' });
    }

    if (!user.otpExpiry || user.otpExpiry < new Date()) return res.status(400).json({ error: 'OTP expired' });

    user.isVerified = true;
    user.otp = undefined;
    user.otpExpiry = undefined;
    user.otpAttempts = 0;
    user.lockedUntil = undefined;
    await user.save();

    // Generate JWT tokens
    const accessToken = jwt.sign({ sub: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
    const refreshToken = jwt.sign({ sub: user._id }, process.env.JWT_REFRESH_SECRET, { expiresIn: process.env.JWT_REFRESH_EXPIRY || '7d' });
    
    // Store refresh token in http-only cookie
    res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict' });
    
    return res.json({ accessToken, refreshToken, user: { _id: user._id, name: user.name, email: user.email } });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Resend OTP
router.post('/resend-otp', otpLimiter, async (req, res) => {
  try {
    const { email } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    const User = getUser();
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return res.status(404).json({ error: 'User not found' });

    if (user.lockedUntil && user.lockedUntil > new Date()) {
      return res.status(429).json({ error: 'Too many attempts, try later' });
    }

    const otp = generateOtp(parseInt(process.env.OTP_LENGTH || '6', 10));
    user.otp = otp;
    user.otpExpiry = new Date(Date.now() + (parseInt(process.env.OTP_TTL_MINUTES || '10', 10) * 60 * 1000));
    user.otpAttempts = 0;
    await user.save();

    if (process.env.DISABLE_EMAIL !== 'true') await sendOtpEmail(user.email, otp);
    return res.json({ message: 'OTP resent' });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    const User = getUser();
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return res.status(404).json({ error: 'Invalid credentials' });

    if (!user.isVerified) return res.status(403).json({ error: 'Email not verified' });

    const ok = await bcrypt.compare(password, user.password || '');
    if (!ok) return res.status(401).json({ error: 'Invalid credentials' });

    const accessToken = jwt.sign({ sub: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
    const refreshToken = jwt.sign({ sub: user._id }, process.env.JWT_REFRESH_SECRET, { expiresIn: process.env.JWT_REFRESH_EXPIRY || '7d' });
    
    // Store refresh token in http-only cookie
    res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict' });
    
    return res.json({ accessToken, refreshToken });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Send OTP for Login (alternative to password)
router.post('/send-login-otp', otpLimiter, async (req, res) => {
  try {
    const { email } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    const User = getUser();
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return res.status(404).json({ error: 'User not found' });

    if (!user.isVerified) return res.status(403).json({ error: 'Email not verified' });

    // Check if account is locked
    if (user.lockedUntil && user.lockedUntil > new Date()) {
      return res.status(429).json({ error: 'Too many attempts, try later' });
    }

    // Generate and send OTP
    const otp = generateOtp(parseInt(process.env.OTP_LENGTH || '6', 10));
    user.otp = otp;
    user.otpExpiry = new Date(Date.now() + (parseInt(process.env.OTP_TTL_MINUTES || '10', 10) * 60 * 1000));
    user.otpAttempts = 0;
    await user.save();

    if (process.env.DISABLE_EMAIL !== 'true') await sendOtpEmail(user.email, otp);
    console.log('Login OTP:', otp);

    return res.json({ message: 'OTP sent to email' });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Verify OTP for Login
router.post('/verify-login-otp', async (req, res) => {
  try {
    const { email, otp } = req.body;
    if (!email || !validator.isEmail(email)) return res.status(400).json({ error: 'Invalid email' });
    const User = getUser();
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Check locked
    if (user.lockedUntil && user.lockedUntil > new Date()) {
      return res.status(429).json({ error: 'Too many attempts, try later' });
    }

    if (user.otp !== otp) {
      user.otpAttempts = (user.otpAttempts || 0) + 1;
      if (user.otpAttempts >= parseInt(process.env.OTP_MAX_ATTEMPTS || '5', 10)) {
        user.lockedUntil = new Date(Date.now() + (parseInt(process.env.OTP_LOCK_MINUTES || '15', 10) * 60 * 1000));
      }
      await user.save();
      return res.status(400).json({ error: 'Invalid OTP' });
    }

    if (!user.otpExpiry || user.otpExpiry < new Date()) return res.status(400).json({ error: 'OTP expired' });

    // Clear OTP fields
    user.otp = undefined;
    user.otpExpiry = undefined;
    user.otpAttempts = 0;
    user.lockedUntil = undefined;
    await user.save();

    // Generate JWT tokens
    const accessToken = jwt.sign({ sub: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
    const refreshToken = jwt.sign({ sub: user._id }, process.env.JWT_REFRESH_SECRET, { expiresIn: process.env.JWT_REFRESH_EXPIRY || '7d' });
    
    // Store refresh token in http-only cookie
    res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict' });
    
    return res.json({ accessToken, refreshToken, user: { _id: user._id, name: user.name, email: user.email } });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Refresh token endpoint
router.post('/refresh', (req, res) => {
  try {
    const { refreshToken } = req.body;
    if (!refreshToken) {
      // Try from cookie
      const cookieToken = req.cookies.refreshToken;
      if (!cookieToken) return res.status(401).json({ error: 'Refresh token missing' });
      
      const decoded = jwt.verify(cookieToken, process.env.JWT_REFRESH_SECRET);
      const accessToken = jwt.sign({ sub: decoded.sub }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
      return res.json({ accessToken });
    }
    
    const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    const accessToken = jwt.sign({ sub: decoded.sub }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
    return res.json({ accessToken });
  } catch (err) {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Logout (invalidate refresh token)
router.post('/logout', (req, res) => {
  res.clearCookie('refreshToken');
  return res.json({ message: 'Logged out' });
});

// Get current user profile (requires valid JWT)
router.get('/me', verifyJWT, async (req, res) => {
  try {
    const User = getUser();
    const user = await User.findById(req.user.sub).select('-password -otp -otpExpiry -otpAttempts -lockedUntil');
    if (!user) return res.status(404).json({ error: 'User not found' });
    return res.json(user);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Google OAuth entry
router.get('/google', (req, res, next) => {
  const passport = require('passport');
  passport.authenticate('google', { scope: ['profile', 'email'] })(req, res, next);
});

router.get('/google/callback', (req, res, next) => {
  const passport = require('passport');
  passport.authenticate('google', (err, user) => {
    if (err || !user) return res.status(401).json({ error: 'Google authentication failed' });
    // generate JWT
    const token = jwt.sign({ sub: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRY || '1h' });
    // redirect with token
    res.redirect(`/auth/success?token=${token}`);
  })(req, res, next);
});

// DEV-ONLY: Retrieve OTP for testing (only available when DISABLE_EMAIL=true)
if (process.env.DISABLE_EMAIL === 'true') {
  router.get('/dev/otp/:email', async (req, res) => {
    try {
      const User = getUser();
      const user = await User.findOne({ email: req.params.email.toLowerCase() });
      if (!user) return res.status(404).json({ error: 'User not found' });
      return res.json({ otp: user.otp, otpExpiry: user.otpExpiry });
    } catch (err) {
      return res.status(500).json({ error: 'Server error' });
    }
  });
}

module.exports = router;
