import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './index.css'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I\'m Athena, your AI assistant. How can I help you today?', sender: 'bot' }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [showFloatingChat, setShowFloatingChat] = useState(false)
  const floatingMessagesRef = useRef(null)
  const floatingInputRef = useRef(null)
  const [expandedFaq, setExpandedFaq] = useState(null)
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const [authMode, setAuthMode] = useState('login')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authUser, setAuthUser] = useState(null)
  const [authToken, setAuthToken] = useState(null)

  const templates = [
    { id: 1, name: 'Customer Service Agent', color: '#10b981', avatar: '/images/customer.png', description: 'Handle customer inquiries with intelligence and empathy' },
    { id: 2, name: 'Operations Coach', color: '#ef4444', avatar: '/images/operations.png', description: 'Enterprise talent strategy and optimization' },
    { id: 3, name: 'HR Benefits Agent', color: '#3b82f6', avatar: '/images/hr.png', description: 'Guide employees through benefits and policies' },
    { id: 4, name: 'Clinical Onboarding', color: '#06b6d4', avatar: '/images/clinical.png', description: 'Medical protocol and trial support' }
  ];

  const features = [
    { icon: '📊', title: 'Precision Reporting', description: 'Get precise analytics and detailed reporting with actionable insights' },
    { icon: '⚡', title: 'Lightning Fast', description: 'Sub-millisecond response times for seamless conversations' },
    { icon: '🌍', title: 'Global Scale', description: 'Support for customers worldwide with multi-regional deployment' },
    { icon: '🎤', title: 'Real-Time Voice Input', description: 'Crystal-clear voice recognition in any environment' },
    { icon: '🔊', title: 'Natural Voice Output', description: 'Human-like voice synthesis with emotional nuance' },
    { icon: '🎭', title: 'Photorealistic Avatars', description: 'Engage customers with stunning visual presence' },
    { icon: '🌐', title: 'Multi-Language Support', description: 'Communicate seamlessly in 50+ languages' },
    { icon: '🔒', title: 'Enterprise Security', description: 'Bank-level encryption and compliance with all standards' },
    { icon: '⚙️', title: 'Sub-second Latency', description: 'Experience instant, natural conversations' }
  ]

  const integrations = [
    { name: 'Salesforce', icon: '☁️' },
    { name: 'Slack', icon: '💬' },
    { name: 'Google Cloud', icon: '🔷' },
    { name: 'AWS', icon: '📦' },
    { name: 'Microsoft Teams', icon: '👥' },
    { name: 'Custom APIs', icon: '🔌' }
  ]

  const testimonials = [
    { name: 'Sarah Chen', company: 'TechCorp', text: 'Athena has transformed how we handle customer support. The AI is incredibly smart and natural.' },
    { name: 'Marcus Johnson', company: 'Global Solutions', text: 'The implementation was seamless and ROI was immediate. Highly recommended!' },
    { name: 'Emma Davis', company: 'Innovation Labs', text: 'The avatar quality and conversation flow are industry-leading. Worth every penny!' }
  ]

  const faqs = [
    { q: 'What is Athena AI Platform?', a: 'Athena AI Platform enables enterprises to deploy intelligent digital workers with photorealistic avatars and natural language understanding.' },
    { q: 'Can I deploy it myself or do I need help?', a: 'Both options are available. We offer self-service deployment or managed implementation by our expert team.' },
    { q: 'What integrations are supported?', a: 'We support 50+ integrations including Salesforce, Slack, Microsoft Teams, Google Cloud, AWS, and custom APIs.' },
    { q: 'How long is the onboarding?', a: 'Standard onboarding takes 2-4 weeks. Express deployment is available for enterprise clients.' },
    { q: 'What are the pricing options?', a: 'We offer flexible plans based on usage, features, and scale. Contact our sales team for a custom quote.' },
    { q: 'What security standards do you meet?', a: 'We comply with SOC 2 Type II, GDPR, HIPAA (healthcare), and industry-specific regulations.' }
  ]

  const products = [
    { name: 'Marketing', icon: '📱' },
    { name: 'Content Insights', icon: '📊' },
    { name: 'Learning & Development', icon: '📚' },
    { name: 'Recruiting', icon: '👔' }
  ]

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser.')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognitionRef.current = new SpeechRecognition()
    recognitionRef.current.continuous = false
    recognitionRef.current.interimResults = false
    recognitionRef.current.lang = 'en-US'

    recognitionRef.current.onstart = () => {
      setIsListening(true)
    }

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInput(transcript)
    }

    recognitionRef.current.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current.start()
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'en-US'
      utterance.rate = 0.9
      utterance.pitch = 1
      window.speechSynthesis.speak(utterance)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { id: Date.now(), text: input, sender: 'user' }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      const headers = authToken ? { Authorization: `Bearer ${authToken}` } : {}
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: input
      }, { headers })
      const botMessage = { id: Date.now() + 1, text: response.data.message, sender: 'bot' }
      setMessages(prev => [...prev, botMessage])
      setIsSpeaking(true)
      speakText(response.data.message)
      setTimeout(() => setIsSpeaking(false), 3000) // Simulate speaking duration
    } catch {
      const errorMessage = { id: Date.now() + 1, text: 'Sorry, I\'m having trouble connecting. Please try again.', sender: 'bot' }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    setCurrentPage('chat')
  }

  const toggleFloatingChat = () => setShowFloatingChat(v => !v)

  useEffect(() => {
    if (showFloatingChat) {
      // scroll messages to bottom and focus input when opened
      setTimeout(() => {
        floatingMessagesRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
        floatingInputRef.current?.focus()
      }, 120)
    }
  }, [showFloatingChat, messages])

  useEffect(() => {
    // try to restore a simple client-side auth user
    try {
      const raw = localStorage.getItem('ai_auth_user')
      if (raw) setAuthUser(JSON.parse(raw))
    } catch {}
  }, [])

  useEffect(() => {
    try {
      const t = localStorage.getItem('ai_auth_token')
      if (t) setAuthToken(t)
    } catch {}
  }, [])

  useEffect(() => {
    if (currentPage === 'chat' && !authUser) {
      setCurrentPage('auth')
    }
  }, [currentPage, authUser])

  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    if (!authEmail.trim() || !authPassword.trim()) return alert('Please enter email and password')

    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register'
      const resp = await axios.post(`http://localhost:5000${endpoint}`, {
        email: authEmail,
        password: authPassword
      })

      if (resp.data && resp.data.user) {
        setAuthUser(resp.data.user)
        setAuthToken(resp.data.token || null)
        localStorage.setItem('ai_auth_user', JSON.stringify(resp.data.user))
        if (resp.data.token) localStorage.setItem('ai_auth_token', resp.data.token)
        setCurrentPage('chat')
      } else {
        alert('Authentication failed')
      }
    } catch (err) {
      console.error(err)
      alert('Auth error — check backend or network')
    }
  }

  const socialAuth = async (provider) => {
    try {
      const resp = await axios.get(`http://localhost:5000/api/auth/oauth/${provider}`)
      if (resp.data && resp.data.user) {
        setAuthUser(resp.data.user)
        if (resp.data.token) {
          setAuthToken(resp.data.token)
          localStorage.setItem('ai_auth_token', resp.data.token)
        }
        localStorage.setItem('ai_auth_user', JSON.stringify(resp.data.user))
        setCurrentPage('chat')
      }
    } catch (e) { console.error(e); alert('Social auth failed') }
  }

  const logout = () => {
    setAuthUser(null)
    setAuthToken(null)
    localStorage.removeItem('ai_auth_user')
    localStorage.removeItem('ai_auth_token')
    setCurrentPage('auth')
  }

  // Floating Chat widget included on every page
  const FloatingChatWidget = () => (
    <div className={`floating-chat ${showFloatingChat ? 'open' : ''}`}>
      <button className="floating-btn" onClick={toggleFloatingChat} aria-label="Open chat">💬</button>

      <div className="floating-panel" role="dialog" aria-hidden={!showFloatingChat}>
        <div className="floating-avatar-header">
          <img src="/images/operations.png" alt="Athena Avatar" className="floating-avatar-large" />
          <div className="floating-header-info">
            <strong>Athena</strong>
            <div className="floating-sub">AI Assistant</div>
          </div>
          <button className="floating-close" onClick={toggleFloatingChat} aria-label="Close chat">✕</button>
        </div>

        <div className="floating-messages">
          <div className="floating-messages-list">
            {messages.map(m => (
              <div key={m.id} className={`message ${m.sender}`}>
                <div className="message-bubble">{m.text}</div>
              </div>
            ))}
            {isTyping && (
              <div className="message bot">
                <div className="message-bubble typing"><span></span><span></span><span></span></div>
              </div>
            )}
            <div ref={floatingMessagesRef} />
          </div>
        </div>

        <div className="floating-input">
          <input
            ref={floatingInputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Athena..."
            disabled={isTyping}
          />
          <button onClick={isListening ? stopListening : startListening} className={`mic-btn ${isListening ? 'listening' : ''}`}>🎤</button>
          <button onClick={() => { sendMessage(); }} disabled={isTyping || !input.trim()} className="send-btn">→</button>
        </div>
      </div>
    </div>
  )

  // Auth / Login Page
  if (currentPage === 'auth') {
    return (
      <div className="auth-page">
        <nav className="landing-navbar">
          <div className="nav-container">
            <div className="logo">🤖 ATHENA AI</div>
            <div className="nav-actions">
              <button className="nav-cta-btn" onClick={() => setCurrentPage('home')}>Back Home</button>
            </div>
          </div>
        </nav>

        <section className="auth-section">
          <div className="auth-card">
            <div className="auth-tabs">
              <button className={authMode === 'login' ? 'active' : ''} onClick={() => setAuthMode('login')}>Login</button>
              <button className={authMode === 'register' ? 'active' : ''} onClick={() => setAuthMode('register')}>Register</button>
            </div>

            <div className="social-row">
              <button type="button" className="social-btn" onClick={() => socialAuth('google')}>Continue with Google</button>
              <button type="button" className="social-btn" onClick={() => socialAuth('facebook')}>Continue with Facebook</button>
            </div>

            <form className="auth-form" onSubmit={handleAuthSubmit}>
              <label>Email</label>
              <input type="email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} placeholder="you@company.com" required />

              <label>Password</label>
              <input type="password" value={authPassword} onChange={(e) => setAuthPassword(e.target.value)} placeholder="••••••••" required />

              <div className="auth-actions">
                <button type="submit" className="btn-primary">{authMode === 'login' ? 'Sign In' : 'Create Account'}</button>
                <button type="button" className="btn-outline" onClick={async () => { setAuthEmail('demo@demo.com'); setAuthPassword('password'); try { const resp = await axios.post('http://localhost:5000/api/auth/login', { email: 'demo@demo.com', password: 'password' }); setAuthUser(resp.data.user); localStorage.setItem('ai_auth_user', JSON.stringify(resp.data.user)); setCurrentPage('chat'); } catch (e) { alert('Demo login failed') } }}>Demo Login</button>
              </div>
            </form>

            <div className="auth-footer">By continuing you agree to our Terms and Privacy Policy.</div>
          </div>

          <aside className="auth-side">
            <h2>Chat with Athena</h2>
            <p>Access your chatbot from here — quick onboarding and instantaneous replies.</p>
            <div className="auth-side-actions">
              <button className="btn-primary" onClick={() => { setCurrentPage('chat') }}>Open Chat</button>
              <button className="btn-outline" onClick={() => { setShowFloatingChat(true) }}>Open Floating Chat</button>
            </div>
          </aside>
        </section>

        <FloatingChatWidget />
      </div>
    )
  }

  // Home Page
  if (currentPage === 'home') {
    return (
      <div className="landing-page">
        {/* Navbar */}
        <nav className="landing-navbar">
          <div className="nav-container">
            <div className="logo">🤖 ATHENA AI</div>
            <div className="nav-actions">
              {authUser ? (
                <>
                  <span className="nav-user">{authUser.email}</span>
                  <button className="nav-login" onClick={logout}>Logout</button>
                </>
              ) : (
                <>
                  <button className="nav-login" onClick={() => setCurrentPage('auth')}>Login / Register</button>
                  <a href="#/" className="nav-cta-btn">Get Started</a>
                </>
              )}
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="landing-hero">
          <div className="hero-grid">
            <div className="hero-left">
              <div className="hero-badge">Experience the future</div>
              <h1>Athena AI Platform</h1>
              <p>Transform your communications with photorealistic AI avatars. Deploy intelligent agents that understand context, respond naturally, and engage customers worldwide.</p>
              <div className="hero-buttons">
                <button className="btn-large btn-primary" onClick={() => setCurrentPage('chat')}>Start Free Trial</button>
                <button className="btn-large btn-outline">Schedule Demo</button>
              </div>
            </div>

            <div className="hero-right">
              <div className="hero-avatar-card" aria-hidden="true">
                <img src="/images/paul-sir-image.png" alt="Athena Avatar" />
              </div>
              <div className="showcase-panel" aria-hidden="true">
                <div className="showcase-features-wrapper">
                  <div className="showcase-inner">
                    <div className="showcase-card center">
                      <img src="/images/operations.png" alt="Ai-Avatar Chatbot" />
                    </div>
                  </div>
                  
                  <div className="feature-badge badge-top-left">
                    <span className="badge-icon">🤖</span>
                    <span className="badge-label">AI-Powered</span>
                  </div>
                  
                  <div className="feature-badge badge-top-right">
                    <span className="badge-icon">💬</span>
                    <span className="badge-label">Real-Time Chat</span>
                  </div>
                  
                  <div className="feature-badge badge-bottom-left">
                    <span className="badge-icon">⚡</span>
                    <span className="badge-label">Lightning Fast</span>
                  </div>
                  
                  <div className="feature-badge badge-bottom-right">
                    <span className="badge-icon">🔒</span>
                    <span className="badge-label">Secure & Safe</span>
                  </div>
                </div>
                <div className="showcase-caption">Ai-Avatar Chatbot</div>
              </div>
            </div>
          </div>
        </section>

        {/* Experience Section */}
        <section className="experience-section">
          <h2>Experience the Future</h2>
          <p>Get how AI transforms your communication with photorealistic digital worker solutions</p>
          <div className="experience-grid">
            {features.map((feature, idx) => (
              <div key={idx} className="experience-card">
                <span className="experience-icon">{feature.icon}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Used By Teams Section */}
        <section className="used-by-section">
          <h2>Used by Leading Teams</h2>
          <p>Trusted by enterprises worldwide to transform customer communications</p>
          <div className="companies-grid">
            {products.map((product, idx) => (
              <div key={idx} className="company-card">
                <span className="company-icon">{product.icon}</span>
                <h4>{product.name}</h4>
                <p>Trusted by leading teams</p>
              </div>
            ))}
          </div>
          <button className="btn-primary">View Case Studies</button>
        </section>

        {/* Integrations Section */}
        <section className="integrations-section">
          <h2>Seamless Integrations</h2>
          <p>Connect Athena with your favorite tools and platforms</p>
          <div className="integrations-grid">
            {integrations.map((integration, idx) => (
              <div key={idx} className="integration-card">
                <span className="integration-icon">{integration.icon}</span>
                <p>{integration.name}</p>
              </div>
            ))}
          </div>
          <button className="btn-primary">View All Integrations</button>
        </section>

        {/* Enterprise Ready Section */}
        <section className="enterprise-section">
          <h2>Enterprise-Ready</h2>
          <div className="enterprise-grid">
            <div className="enterprise-card">
              <span className="enterprise-icon">🔒</span>
              <h3>Privacy First</h3>
              <p>Your data stays secure with end-to-end encryption</p>
            </div>
            <div className="enterprise-card">
              <span className="enterprise-icon">✅</span>
              <h3>Security Certified</h3>
              <p>SOC 2 Type II and compliant with GDPR & HIPAA</p>
            </div>
            <div className="enterprise-card">
              <span className="enterprise-icon">🤖</span>
              <h3>Ethical AI</h3>
              <p>Transparent and responsible AI deployment</p>
            </div>
            <div className="enterprise-card">
              <span className="enterprise-icon">🚀</span>
              <h3>24/7 Support</h3>
              <p>Premium support available round the clock</p>
            </div>
            <div className="enterprise-card">
              <span className="enterprise-icon">📊</span>
              <h3>99.99% Uptime</h3>
              <p>Industry-leading reliability guarantees</p>
            </div>
            <div className="enterprise-card">
              <span className="enterprise-icon">🔧</span>
              <h3>Scalable Architecture</h3>
              <p>Grow from startup to enterprise effortlessly</p>
            </div>
          </div>
        </section>

        {/* Video Showcase Section */}
        <section className="video-showcase-section">
          <div className="video-showcase-content">
            <div className="video-showcase-header">
              <h2>See Athena in Action</h2>
              <p>Experience the power of our AI avatar platform</p>
            </div>

            <div className="video-container-3d">
              <div className="video-wrapper">
                <video
                  className="showcase-video"
                  controls
                  autoPlay
                  muted
                  loop
                  playsInline
                  onError={(e) => console.error('Video error:', e)}
                >
                  <source src="/video01_converted.mp4" type="video/mp4" />
                  <source src="/video01.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="video-glow"></div>
                <div className="video-border-effect"></div>
              </div>

              <div className="video-stats">
                <div className="stat-item">
                  <span className="stat-number">4K</span>
                  <span className="stat-label">Resolution</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">60fps</span>
                  <span className="stat-label">Smooth Playback</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">Live</span>
                  <span className="stat-label">Real-time Interaction</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="testimonials-section">
          <h2>What Our Customers Say</h2>
          <div className="testimonials-grid">
            {testimonials.map((testimonial, idx) => (
              <div key={idx} className="testimonial-card">
                <p className="testimonial-text">"{testimonial.text}"</p>
                <div className="testimonial-author">
                  <div className="author-avatar">👤</div>
                  <div>
                    <h4>{testimonial.name}</h4>
                    <p>{testimonial.company}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-container">
            {faqs.map((faq, idx) => (
              <div key={idx} className="faq-item">
                <button 
                  className="faq-question"
                  onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                >
                  {faq.q}
                  <span className={`faq-toggle ${expandedFaq === idx ? 'open' : ''}`}>▼</span>
                </button>
                {expandedFaq === idx && (
                  <div className="faq-answer">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <h2>Ready to Transform Your Communications?</h2>
          <p>Join hundreds of enterprises using Athena AI for real human-like interactions at scale</p>
          <button className="btn-large btn-primary" onClick={() => setCurrentPage('chat')}>Start Free Trial</button>
        </section>

        {/* Footer */}
        <footer className="site-footer">
          <div className="site-footer-top">
            <div className="footer-left">
              <h3>ai-chatbot-avatar</h3>
              <p>Your gateway to a world of knowledge. Discover, read, and explore thousands of digital books at your fingertips.</p>
              <div className="social-icons">
                <a href="#/" className="social-circle">🔵</a>
                <a href="#/" className="social-circle">🔷</a>
                <a href="#/" className="social-circle">🟣</a>
                <a href="#/" className="social-circle">🔹</a>
              </div>
            </div>

            <div className="footer-links">
              <h4>Quick Links</h4>
              <a href="#/">Browse Books</a>
              <a href="#/">My Profile</a>
              <a href="#/">Shopping Cart</a>
              <a href="#/">My Wishlist</a>
            </div>

            <div className="footer-contact">
              <h4>Contact Us</h4>
              <p>📧 support@ebookathena.com</p>
              <p>📞 +1 (555) 123-4567</p>
              <p>📍 123 Book Street, Knowledge City, KC 12345</p>
            </div>
          </div>

          <div className="site-footer-bottom">
            <hr />
            <p>© 2026 ai-chatbot-avatar. All rights reserved.</p>
            <p className="muted">Crafted for curious minds. Explore the world of digital reading.</p>
          </div>
        </footer>
        <FloatingChatWidget />
      </div>
    )
  }



  // Templates page removed per user request.

  // Chat Page
  return (
    <div className="app-chat">
      <header className="chat-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>← Back</button>
        <div className="header-content">
          <h1>Athena AI</h1>
          {selectedTemplate && <p>{selectedTemplate.name}</p>}
        </div>
        <div className="status">
          <div className="status-dot"></div>
          {isSpeaking ? 'Speaking...' : 'Online'}
        </div>
      </header>

      <div className="chat-main">
        <div className="avatar-panel">
          <div className="avatar-box">
            <div className={`avatar-circle ${isSpeaking ? 'speaking' : ''}`}>
              <img src="/images/paul-sir-image.png" alt="Athena Avatar" />
            </div>
            <h2>Athena</h2>
            <p>AI Assistant</p>
            <div className="avatar-stats">
              <div className="stat">
                <span className="stat-label">Status</span>
                <span className="stat-value">Online</span>
              </div>
            </div>
          </div>
        </div>

        <div className="chat-panel">
          <div className="messages-area">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  {message.text}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message bot">
                <div className="message-bubble typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isTyping}
            />
            <button
              onClick={isListening ? stopListening : startListening}
              className={`mic-btn ${isListening ? 'listening' : ''}`}
            >
              🎤
            </button>
            <button onClick={sendMessage} disabled={isTyping || !input.trim()} className="send-btn">
              →
            </button>
          </div>
        </div>
      </div>
        <FloatingChatWidget />
      </div>
  )
}

export default App
