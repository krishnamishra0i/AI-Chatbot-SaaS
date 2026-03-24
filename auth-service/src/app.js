require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const mongoose = require('mongoose');
const passport = require('passport');
const session = require('express-session');

const app = express();

// Basic middleware
app.use(helmet());
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Passport (Google OAuth)
app.use(session({ secret: process.env.SESSION_SECRET || 'session_secret', resave: false, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());

// Global flag: are we using MongoDB or in-memory?
global.USE_MEMORY_STORE = false;

const PORT = process.env.PORT || 3001;

function buildMongoUri() {
  if (process.env.MONGODB_URI) return process.env.MONGODB_URI;
  const user = encodeURIComponent(process.env.MONGODB_USER || '');
  const pass = encodeURIComponent(process.env.MONGODB_PASS || '');
  const cluster = process.env.MONGODB_CLUSTER || '';
  const db = process.env.MONGODB_DB || 'athena_auth';
  if (!user || !pass || !cluster) return null;
  return `mongodb://localhost:27017/${process.env.MONGODB_DB || 'athena_auth'}`;
}

// const connection = mongoose.connection(`mongodb://localhost:27017/${process.env.MONGODB_DB || 'athena_auth'}`);
// connection.on('error', (err) => {
//   console.warn(`MongoDB connection error: ${err.message}`);
//   console.warn('Falling back to in-memory storage (dev mode)');
//   global.USE_MEMORY_STORE = true;
// });


async function start() {
  const mongoUri = buildMongoUri();

  if (mongoUri) {
    try {
      console.log(`Connecting to MongoDB (cluster: ${process.env.MONGODB_CLUSTER || 'from URI'})...`);
      await mongoose.connect(mongoUri, { connectTimeoutMS: 10000 });
      console.log('✅ Connected to MongoDB');
    } catch (err) {
      console.warn(`⚠️  MongoDB connection failed: ${err.message}`);
      console.warn('   Falling back to in-memory storage (dev mode)');
      global.USE_MEMORY_STORE = true;
    }
  } else {
    console.warn('⚠️  No MongoDB config found — running in dev mode (in-memory storage)');
    global.USE_MEMORY_STORE = true;
  }

  // Load passport config (only if NOT in memory mode — Google OAuth needs Mongo)
  try { require('./config/passport'); } catch (e) { /* ignore in dev */ }

  // Routes (loaded after db decision so models resolve correctly)
  const authRoutes = require('./routes/auth');
  const supportRoutes = require('./routes/support');
  app.use('/api/auth', authRoutes);
  app.use('/support', supportRoutes);

  app.get('/health', (req, res) => res.json({
    status: 'healthy',
    storage: global.USE_MEMORY_STORE ? 'in-memory' : 'mongodb',
    uptime: process.uptime()
  }));

  app.listen(PORT, () => {
    console.log(`\n🚀 Auth service running on http://localhost:${PORT}`);
    console.log(`   Storage: ${global.USE_MEMORY_STORE ? 'In-Memory (dev)' : 'MongoDB'}`);
    console.log(`   Endpoints: /auth/signup | /auth/verify-otp | /auth/login | /auth/me\n`);
  });
}

start().catch(err => {
  console.error('Failed to start auth service', err);
  process.exit(1);
});
