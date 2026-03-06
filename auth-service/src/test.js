const mongoose = require('mongoose');
const User = require('../models/User');

// Quick test script - run with: node src/test.js
async function runTests() {
  console.log('🧪 Starting auth flow tests...\n');

  const testEmail = `test_${Date.now()}@athena.local`;
  const testPassword = 'Test@12345';
  let testOtp = '';
  let accessToken = '';

  try {
    // Build connection URI (handles special chars in password)
    let mongoUri = process.env.MONGODB_URI;
    if (!mongoUri) {
      const user = encodeURIComponent(process.env.MONGODB_USER || '');
      const pass = encodeURIComponent(process.env.MONGODB_PASS || '');
      const cluster = process.env.MONGODB_CLUSTER || '';
      const db = process.env.MONGODB_DB || 'athena_auth';
      mongoUri = `mongodb+srv://${user}:${pass}@${cluster}/${db}?retryWrites=true&w=majority`;
    }
    if (!mongoUri) throw new Error('MongoDB config not set');
    
    await mongoose.connect(mongoUri);
    console.log('✅ Connected to MongoDB\n');

    // 1. CLEANUP (remove test user if exists)
    console.log(`1️⃣ Cleaning up test user...`);
    await User.deleteOne({ email: testEmail });
    console.log('✅ Cleanup complete\n');

    // 2. CREATE TEST USER (Signup)
    console.log(`2️⃣ Testing signup with email: ${testEmail}`);
    const bcrypt = require('bcrypt');
    const { generateOtp } = require('./utils/otp');
    
    const otp = generateOtp(6);
    const hashed = await bcrypt.hash(testPassword, 12);
    const user = await User.create({
      name: 'Test User',
      email: testEmail,
      password: hashed,
      otp,
      otpExpiry: new Date(Date.now() + 10 * 60 * 1000),
      isVerified: false
    });
    testOtp = otp;
    console.log(`✅ User created: ${user._id}`);
    console.log(`   OTP: ${testOtp}\n`);

    // 3. VERIFY OTP
    console.log(`3️⃣ Testing OTP verification (OTP: ${testOtp})`);
    const verified = await User.findByIdAndUpdate(user._id, {
      isVerified: true,
      otp: undefined,
      otpExpiry: undefined,
      otpAttempts: 0
    }, { new: true });
    console.log(`✅ User verified\n`);

    // 4. LOGIN
    console.log(`4️⃣ Testing login`);
    const jwt = require('jsonwebtoken');
    accessToken = jwt.sign(
      { sub: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRY || '1h' }
    );
    console.log(`✅ Login successful`);
    console.log(`   Access Token: ${accessToken}\n`);

    // 5. VALIDATE TOKEN
    console.log(`5️⃣ Testing JWT validation`);
    const decoded = jwt.verify(accessToken, process.env.JWT_SECRET);
    console.log(`✅ Token valid`);
    console.log(`   Decoded: ${JSON.stringify(decoded)}\n`);

    // 6. GET USER PROFILE
    console.log(`6️⃣ Testing profile fetch`);
    const profile = await User.findById(decoded.sub).select('-password -otp -otpExpiry -otpAttempts -lockedUntil');
    console.log(`✅ Profile fetched:`);
    console.log(`   Name: ${profile.name}`);
    console.log(`   Email: ${profile.email}`);
    console.log(`   Verified: ${profile.isVerified}\n`);

    // 7. CLEANUP
    await User.deleteOne({ email: testEmail });
    console.log(`✅ Test user cleaned up\n`);

    console.log('🎉 All tests passed!\n');
  } catch (err) {
    console.error('❌ Test failed:', err.message);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('Disconnected from MongoDB');
  }
}

runTests();
