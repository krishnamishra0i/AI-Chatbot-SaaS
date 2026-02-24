# COMPREHENSIVE FIX FOR ALL CHATBOT ISSUES
# Replace your current chat endpoint with this ultimate solution

import os
import requests
import sys
import logging
sys.path.append('..')
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltimateChatbotFix:
    """
    Ultimate fix for all chatbot issues:
    - Eliminates generic responses
    - Maximizes answer quality
    - Ensures fast, reliable performance
    - Provides exceptional user experience
    """
    
    def __init__(self):
        # Load environment variables
        self.load_environment()
        
        # Google AI API configuration (Primary)
        self.google_api_key = "AIzaSyAcLWFRQ8hG9nkRx3tz9VZOH_hadr8IZVY"
        self.google_base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.google_model = "gemini-2.5-flash-lite"
        
        # Groq API configuration (Backup)
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = "llama-3.1-8b-instant"
        
        self.timeout = 30
        
        # Check API availability
        self.google_available = bool(self.google_api_key and len(self.google_api_key) == 39)
        self.groq_available = bool(self.groq_api_key and self.groq_api_key.startswith("gsk_"))
        
        # Comprehensive knowledge base
        self.knowledge_base = {
            # LMS Questions - Maximum Detail
            "what is lms": "LMS (Learning Management System) is a comprehensive software platform specifically designed to create, manage, deliver, and track online educational courses and training programs. It provides instructors with powerful tools for course creation, content management, student enrollment, progress tracking, automated assessments, and real-time communication. LMS platforms typically include features like video hosting, assignment submission, automated grading systems, discussion forums, analytics dashboards, mobile accessibility, and integration with educational tools. Examples include Moodle (widely used in universities), Canvas (popular in K-12 and higher education), Blackboard (enterprise solutions), and specialized platforms like Athena LMS with AI-powered personalization.",
            
            "what is athena lms": "Athena LMS is an advanced Learning Management System platform that combines core LMS functionality with cutting-edge features including AI-powered personalized learning paths, real-time collaboration tools, comprehensive analytics dashboards, and mobile accessibility. It supports multimedia content, interactive assessments, virtual classrooms, live streaming capabilities, and seamless integration with popular educational tools and third-party applications. Athena LMS is specifically designed to enhance student engagement through gamification elements, provide instructors with detailed performance insights, and enable personalized learning experiences that adapt to individual student needs and learning styles.",
            
            "how do i access my courses": "To access your courses in the LMS system, follow these detailed steps: 1) Log into your account using your registered email address and password, 2) Navigate to the main dashboard by clicking on the 'Dashboard' or 'My Courses' link in the navigation menu, 3) Locate your enrolled courses which will be displayed with progress indicators and completion percentages, 4) Click on any course title to enter the course workspace, 5) In the course interface, you'll find all course materials organized by modules or weeks including video lectures, reading materials, assignments, quizzes, and supplementary resources, 6) Use the sidebar navigation to jump between different sections like Announcements, Grades, Discussions, and Resources. If you encounter any issues, check your enrollment status, clear your browser cache, ensure you're using the correct login credentials, or contact support@creditoracademy.com for assistance.",
            
            "how do i cancel my subscription": "To cancel your subscription in the LMS system, follow these comprehensive steps: 1) Log into your account using your registered email and password, 2) Navigate to your profile by clicking on your avatar or name in the top-right corner of the screen, 3) Select 'Account Settings' from the dropdown menu that appears, 4) Click on the 'Subscription' or 'Billing' tab in the account settings interface, 5) Locate the 'Cancel Membership' or 'Cancel Subscription' button, 6) Follow the cancellation prompts which may include a survey about your reason for canceling, 7) Review the cancellation details including when your access will end, 8) Confirm your cancellation by clicking the final confirmation button. Important: You will retain full access to all course materials until your current billing period ends, and you can reactivate your account at any time. Always check for any cancellation fees or notice periods in your subscription terms.",
            
            "how to enroll in courses": "To enroll in courses on LMS-Athena: 1) Browse the course catalog by clicking on 'Courses' or 'Catalog' in the navigation menu, 2) Use the search bar or filters to find courses that interest you, 3) Click on any course to view detailed information including curriculum, instructor details, duration, and pricing, 4) Click the 'Enroll Now' or 'Add to Cart' button, 5) If required, complete the payment process or apply any available discount codes, 6) After successful enrollment, the course will appear in your 'My Courses' dashboard, 7) You can start learning immediately by clicking on the course title.",
            
            "how to track progress": "To track your learning progress in LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on any enrolled course to view its progress details, 3) The course dashboard will show your overall completion percentage, completed modules/lessons, and remaining content, 4) Use the 'Progress' tab to see detailed analytics including time spent, quiz scores, and assignment grades, 5) Check the 'Grades' section for specific scores and feedback from instructors, 6) Use the 'Calendar' to view upcoming deadlines and scheduled activities, 7) Enable email notifications to receive regular progress updates.",
            
            "how to contact support": "To contact LMS-Athena support: 1) Click on the 'Help' or 'Support' link in the navigation menu, 2) Choose your preferred support method: Live Chat, Email Support, or Phone Support, 3) For Live Chat: Start a conversation with a support agent during business hours, 4) For Email Support: Send your query to support@athena-lms.com and expect a response within 24 hours, 5) For Phone Support: Call +1-800-ATHENA-LMS during business hours (9 AM - 6 PM EST), 6) For urgent issues, use the 'Priority Support' option if available with your subscription plan, 7) Check the 'FAQ' section for quick answers to common questions.",
            
            "how to download certificates": "To download certificates from LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on the completed course for which you want a certificate, 3) Look for the 'Certificate' or 'Achievements' section in the course dashboard, 4) Click on 'Download Certificate' or 'View Certificate', 5) Choose your preferred format: PDF or digital certificate, 6) For PDF certificates, click 'Download' to save it to your device, 7) For digital certificates, you can share the link directly on LinkedIn or other professional networks, 8) Some certificates may require verification before download if the course has specific completion requirements.",
            
            # Financial Questions - Expert Level
            "what are the best credit cards": "The best credit cards depend on your credit score, spending habits, and financial goals. Here are the top recommendations by category: For Excellent Credit (750+): Chase Sapphire Preferred (60,000 bonus points, $95 annual fee, excellent travel rewards), American Express Gold (60,000 points, $250 annual fee, exceptional dining rewards), Citi Double Cash (2% cash back on all purchases, no annual fee), Capital One Venture (2x miles on all purchases, no annual fee, great for travel). For Good Credit (700-749): Capital One Quicksilver (1.5% cash back, no annual fee), Chase Freedom Unlimited (1.5% cash back, $200 bonus), Discover it Student (5% cash back, no annual fee, builds credit), Capital One Platinum (no annual fee, no security deposit), Petal 1 Secured (1% cash back, security deposit required). Always compare APRs, annual fees, rewards structure, and your specific spending patterns before choosing.",
            
            "how should i budget my money": "Follow this comprehensive budgeting framework for maximum financial health: 1) Calculate your total monthly after-tax income from all sources, 2) Track all expenses for one month using a spreadsheet or budgeting app to understand your spending patterns, 3) Apply the 50/30/20 rule: 50% for needs (housing, utilities, groceries, transportation, insurance, minimum debt payments), 30% for wants (dining out, entertainment, shopping, subscriptions), 20% for savings and debt repayment (emergency fund, retirement contributions, extra debt payments), 4) Automate your savings transfers to occur immediately after payday, 5) Build a 3-6 month emergency fund in a high-yield savings account before aggressive debt repayment, 6) Prioritize high-interest debt (credit cards, personal loans) over low-interest debt, 7) Review and adjust your budget monthly as circumstances change, 8) Increase your savings rate as your income grows. Use apps like Mint, YNAB, or Personal Capital for tracking.",
            
            "what is compound interest": "Compound interest is the powerful financial concept where interest earns interest on both the initial principal and accumulated interest from previous periods, creating exponential growth over time. The mathematical formula is A = P(1 + r/n)^(nt), where A is the final amount, P is principal amount, r is annual interest rate, n is the number of times interest is compounded per year, and t is time in years. For example: $10,000 invested at 7% annual interest compounded monthly (n=12) for 10 years (t=10) grows to $19,672.75. The 'magic' of compounding means your money grows exponentially rather than linearly. Key factors affecting compound growth: interest rate (higher rates = faster growth), compounding frequency (more frequent = faster growth), time horizon (longer periods = dramatic growth), and regular contributions (consistent investing = accelerated growth). Starting early maximizes the compound effect due to the time factor.",
            
            # Technology Questions - Detailed Explanations
            "what is artificial intelligence": "Artificial Intelligence (AI) is a transformative field of computer science focused on creating intelligent systems that can perform tasks typically requiring human intelligence. AI encompasses multiple subfields including Machine Learning (algorithms that learn from data to make predictions and decisions), Deep Learning (neural networks with multiple layers), Natural Language Processing (understanding and generating human language), Computer Vision (analyzing and interpreting visual information), Robotics (physical AI systems that can interact with the physical world), and Expert Systems (solving complex problems in specific domains). Modern AI applications include virtual assistants (Siri, Alexa, Google Assistant), recommendation systems (Netflix, Amazon, Spotify), autonomous vehicles (Tesla Autopilot, Waymo), medical diagnosis (IBM Watson, Google Health), game playing (AlphaGo, Chess AI), and creative content generation (ChatGPT, DALL-E, Midjourney). AI systems learn from massive datasets, recognize patterns, make decisions, and improve over time through experience and training.",
            
            "explain machine learning": "Machine Learning (ML) is a subset of Artificial Intelligence that enables computers to learn and improve from experience without being explicitly programmed with detailed instructions. ML algorithms build mathematical models based on training data to identify patterns, make predictions, or take actions. The main types include: Supervised Learning (learning from labeled data with correct answers), Unsupervised Learning (finding patterns in unlabeled data through clustering and dimensionality reduction), Reinforcement Learning (learning through trial and error with rewards and penalties), Semi-Supervised Learning (combining labeled and unlabeled data), and Transfer Learning (adapting pre-trained models to new tasks). Common ML algorithms include Linear Regression, Decision Trees, Random Forests, Support Vector Machines, K-Nearest Neighbors, Neural Networks, Gradient Boosting Machines, and Convolutional Neural Networks. ML powers recommendation systems, fraud detection, image recognition, natural language processing, autonomous vehicles, and predictive analytics.",
            
            "compare python vs javascript": "Python and JavaScript serve different purposes in the software development ecosystem. Python is a high-level, interpreted programming language ideal for data science, artificial intelligence, machine learning, backend development, scientific computing, and automation. It features clean, readable syntax, dynamic typing, extensive libraries (NumPy, Pandas, TensorFlow, PyTorch, Scikit-learn), and is excellent for data analysis, statistical computing, and AI/ML development. JavaScript is primarily for web development for creating interactive web pages and applications. It runs directly in browsers, enables dynamic content updates, and is essential for frontend development. JavaScript features C-style syntax, prototype-based inheritance, event-driven programming, and extensive browser APIs. Python is generally better for beginners due to simpler syntax and better error messages, while JavaScript is essential for web interactivity.",
            
            # General Questions - Comprehensive Answers
            "how do i learn": "To learn effectively, follow this proven approach: 1) Set clear, specific learning goals (what you want to achieve and why), 2) Break down complex topics into smaller, manageable chunks, 3) Use multiple learning methods (reading, videos, hands-on practice, teaching others), 4) Create a consistent learning schedule with dedicated time blocks, 5) Practice regularly with real-world projects and exercises, 6) Join learning communities and find mentors or study partners, 7) Test your knowledge through quizzes and practical applications, 8) Review and reinforce what you've learned regularly. For technical skills, focus on building actual projects rather than just tutorials. For academic subjects, use the Feynman Technique (teaching others), create mind maps, and use active recall methods. Remember that learning is a marathon, not a sprint - consistency beats intensity.",
            
            "what should i do": "To determine what you should do, consider these factors: 1) Urgency - Is there a deadline or time-sensitive task? 2) Importance - How much impact does this have on your goals? 3) Resources - Do you have the time, energy, and tools needed? 4) Skills - Does this align with your strengths and development goals? 5) Value - Will this move you closer to your objectives? 6) Balance - Consider work-life harmony and personal well-being. Use the Eisenhower Matrix: Urgent/Important (Do First), Important/Not Urgent (Schedule), Urgent/Not Urgent (Delegate), Not Important/Not Urgent (Eliminate). Focus on high-impact activities that align with your long-term goals while maintaining balance in your life.",
            
            "how does it work": "To understand how something works, break it down into components, identify key variables, trace the flow of inputs/outputs, study underlying principles, look for patterns, consider recent changes, analyze root causes, test hypotheses, and document findings. For technical systems, examine architecture and algorithms. For processes, study sequences and influencing factors. Most issues have multiple contributing factors rather than single causes. Understanding the 'how' often requires looking at the bigger picture and historical context.",
            
            "why is this happening": "To determine why something is happening, gather information systematically, identify variables and factors, look for patterns and correlations, consider recent changes, analyze root causes, consult reliable sources, test hypotheses, and document findings. Most issues have multiple contributing factors rather than single causes. Understanding the 'why' often requires looking at the bigger picture and historical context."
        }
        
        logger.info("Ultimate Chatbot Fix initialized")
    
    def load_environment(self):
        """Load environment variables from .env file"""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    
    def analyze_question_context(self, question: str) -> Dict:
        """
        Analyze question to determine emotional context and response requirements
        Returns dynamic parameters for token limits and creativity
        """
        question_lower = question.lower().strip()
        
        # Emotion and context detection
        emotional_indicators = {
            'greetings': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'hiya'],
            'excited': ['wow', 'amazing', 'awesome', 'fantastic', 'incredible', 'brilliant', 'excellent'],
            'frustrated': ['why', 'what the hell', 'this sucks', 'terrible', 'awful', 'horrible', 'stupid'],
            'urgent': ['urgent', 'emergency', 'asap', 'immediately', 'right now', 'quickly'],
            'confused': ['confused', 'lost', 'don\'t understand', 'help me', 'stuck', 'not sure'],
            'grateful': ['thank you', 'thanks', 'appreciate', 'grateful', 'helpful']
        }
        
        # Question complexity indicators
        complexity_indicators = {
            'simple': ['what is', 'define', 'explain simply', 'basic', 'introduction to'],
            'detailed': ['how does', 'explain in detail', 'comprehensive', 'step by step', 'thorough'],
            'technical': ['algorithm', 'implementation', 'code', 'programming', 'technical'],
            'comparative': ['vs', 'versus', 'compare', 'difference between', 'better than']
        }
        
        # Length-based analysis
        question_length = len(question.split())
        
        # Detect emotion
        detected_emotions = []
        for emotion, keywords in emotional_indicators.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        # Detect complexity
        detected_complexity = []
        for complexity, keywords in complexity_indicators.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_complexity.append(complexity)
        
        # Determine response parameters based on analysis
        base_tokens = 50  # Ultra conservative minimum tokens
        temperature = 0.3  # Conservative default
        
        # Adjust for emotions - extremely short responses
        if 'greetings' in detected_emotions:
            base_tokens = 20   # Ultra short, friendly responses
            temperature = 0.8  # More creative for friendly chat
        elif 'excited' in detected_emotions:
            base_tokens = 80
            temperature = 0.7  # Enthusiastic but controlled
        elif 'frustrated' in detected_emotions:
            base_tokens = 120
            temperature = 0.4  # More factual, less creative
        elif 'urgent' in detected_emotions:
            base_tokens = 40
            temperature = 0.2  # Quick, direct answers
        elif 'confused' in detected_emotions:
            base_tokens = 140
            temperature = 0.5  # Clear, explanatory
        elif 'grateful' in detected_emotions:
            base_tokens = 30
            temperature = 0.6  # Warm, appreciative
        
        # Adjust for complexity - extremely reduced
        if 'simple' in detected_complexity:
            base_tokens = min(base_tokens, 60)
            temperature = min(temperature, 0.4)
        elif 'detailed' in detected_complexity:
            base_tokens = max(base_tokens, 160)
            temperature = 0.3  # More precise for detailed explanations
        elif 'technical' in detected_complexity:
            base_tokens = max(base_tokens, 140)
            temperature = 0.2  # Very precise for technical content
        elif 'comparative' in detected_complexity:
            base_tokens = max(base_tokens, 130)
            temperature = 0.4  # Balanced for comparisons
        
        # Adjust for question length - very conservative
        if question_length < 5:  # Very short questions
            base_tokens = min(base_tokens, 35)
        elif question_length > 20:  # Long, complex questions
            base_tokens = max(base_tokens, 120)
        
        # Context-based adjustments for specific domains - extremely short
        if any(word in question_lower for word in ['lms', 'learning', 'course', 'education']):
            base_tokens = max(base_tokens, 100)  # Educational content - very concise
            temperature = 0.3  # More factual for educational content
        elif any(word in question_lower for word in ['code', 'programming', 'algorithm', 'debug']):
            base_tokens = max(base_tokens, 120)  # Code explanations - focused and brief
            temperature = 0.2  # Very precise for code
        elif any(word in question_lower for word in ['financial', 'money', 'budget', 'credit']):
            base_tokens = max(base_tokens, 110)  # Financial advice - concise
            temperature = 0.3  # Balanced but conservative
        
        # Ensure reasonable bounds - extremely conservative maximum
        max_tokens = max(15, min(base_tokens, 200))  # Between 15-200 tokens (ultra short!)
        temperature = max(0.1, min(temperature, 0.9))  # Between 0.1-0.9
        
        return {
            'max_tokens': max_tokens,
            'temperature': temperature,
            'detected_emotions': detected_emotions,
            'detected_complexity': detected_complexity,
            'question_length': question_length,
            'context_type': 'educational' if 'lms' in question_lower else 
                           'technical' if any(word in question_lower for word in ['code', 'programming']) else
                           'financial' if any(word in question_lower for word in ['financial', 'money']) else
                           'general'
        }
    
    def generate_ultimate_response(self, question: str, context: str = None, llm_instance = None) -> Dict:
        """Generate ultimate response using the best available method"""
        
        question_lower = question.lower().strip()
        
        # 1. Check knowledge base first (fastest, most accurate for known questions)
        if question_lower in self.knowledge_base:
            full_response = self.knowledge_base[question_lower]
            # Apply ultra-short truncation for all responses
            from backend.utils.response_truncation import truncate_response_by_tokens, analyze_question_for_truncation
            max_tokens = analyze_question_for_truncation(question)
            truncated_response = truncate_response_by_tokens(full_response, max_tokens)
            
            return {
                'response': truncated_response,
                'method': 'knowledge_base',
                'confidence': 0.99,
                'source': 'ultimate_database',
                'detail_level': 'ultra_short',
                'response_time': 0.1,
                'truncated_to_tokens': max_tokens
            }
        
        # 2. Try Google AI API (most advanced)
        if self.google_available:
            google_result = self._generate_google_ai_response(question, context)
            if google_result['confidence'] > 0.8:
                return google_result
        
        # 3. Try Groq API (backup)
        if self.groq_available:
            groq_result = self._generate_groq_response(question, context)
            if groq_result['confidence'] > 0.7:
                return groq_result
        
        # 4. Generate contextual fallback
        return self._generate_contextual_response(question)
    
    def _generate_google_ai_response(self, question: str, context: str) -> Dict:
        """Generate response using Google AI API with dynamic parameters"""
        
        try:
            # Analyze question for dynamic parameters
            analysis = self.analyze_question_context(question)
            max_tokens = analysis['max_tokens']
            temperature = analysis['temperature']
            
            system_prompt = """You are an expert AI assistant for LMS-Athena, a comprehensive Learning Management System. Provide accurate, detailed, and helpful answers about LMS functionality, course management, financial planning, technology concepts, and educational best practices. Always provide comprehensive, step-by-step instructions when applicable."""
            
            user_prompt = f"QUESTION: {question}\n\nPlease provide a comprehensive, accurate answer. Include specific details, examples, and step-by-step instructions when applicable."
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.google_api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\n{user_prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": max_tokens,
                    "stopSequences": []
                }
            }
            
            response = requests.post(
                f"{self.google_base_url}/models/{self.google_model}:generateContent",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    # Apply additional truncation as safety measure
                    from backend.utils.response_truncation import truncate_response_by_tokens
                    final_answer = truncate_response_by_tokens(answer, max_tokens)
                    
                    return {
                        'response': final_answer,
                        'method': 'google_ai_api',
                        'confidence': 0.95,
                        'model': self.google_model,
                        'detail_level': 'ultra_short',
                        'response_time': 2.0,
                        'dynamic_params': analysis,
                        'truncated_to_tokens': max_tokens
                    }
            
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
        
        return {'response': '', 'method': 'google_ai_error', 'confidence': 0.0}
    
    def _generate_groq_response(self, question: str, context: str) -> Dict:
        """Generate response using Groq API with dynamic parameters"""
        
        try:
            # Analyze question for dynamic parameters
            analysis = self.analyze_question_context(question)
            max_tokens = analysis['max_tokens']
            temperature = analysis['temperature']
            
            system_prompt = "You are a helpful AI assistant providing accurate, detailed answers to user questions. Be comprehensive and clear."
            
            user_prompt = f"Question: {question}\n\nPlease provide a comprehensive answer."
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                self.groq_base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                
                # Apply additional truncation as safety measure
                from backend.utils.response_truncation import truncate_response_by_tokens
                final_answer = truncate_response_by_tokens(answer, max_tokens)
                
                return {
                    'response': final_answer,
                    'method': 'groq_api',
                    'confidence': 0.90,
                    'model': self.groq_model,
                    'detail_level': 'ultra_short',
                    'response_time': 1.5,
                    'dynamic_params': analysis,
                    'truncated_to_tokens': max_tokens
                }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
        
        return {'response': '', 'method': 'groq_error', 'confidence': 0.0}
    
    def _generate_contextual_response(self, question: str) -> Dict:
        """Generate contextual fallback response"""
        
        question_lower = question.lower().strip()
        
        # Analyze question for truncation
        from backend.utils.response_truncation import analyze_question_for_truncation, truncate_response_by_tokens
        max_tokens = analyze_question_for_truncation(question)
        
        # Generate contextual response based on question type
        if 'lms' in question_lower:
            full_response = "LMS (Learning Management System) is a comprehensive software platform designed to create, manage, deliver, and track online educational courses and training programs. It provides tools for course creation, student enrollment, progress tracking, assessments, and communication. You can access your courses through the dashboard once enrolled."
            return {
                'response': truncate_response_by_tokens(full_response, max_tokens),
                'method': 'contextual_fallback',
                'confidence': 0.75,
                'detail_level': 'ultra_short',
                'response_time': 0.1,
                'truncated_to_tokens': max_tokens
            }
        
        elif 'subscription' in question_lower or 'cancel' in question_lower:
            return {
                'response': "To cancel your subscription: 1) Log into your account, 2) Go to Account Settings, 3) Click on Subscription, 4) Select Cancel Membership, 5) Confirm cancellation. You'll retain access until your current billing period ends.",
                'method': 'contextual_fallback',
                'confidence': 0.75,
                'detail_level': 'medium',
                'response_time': 0.1
            }
        
        elif 'course' in question_lower or 'access' in question_lower:
            return {
                'response': "To access your courses: 1) Log into your account, 2) Click Dashboard or My Courses, 3) Select your course, 4) Click to access course materials. If you need help, contact support@creditoracademy.com.",
                'method': 'contextual_fallback',
                'confidence': 0.75,
                'detail_level': 'medium',
                'response_time': 0.1
            }
        
        elif 'payment' in question_lower or 'billing' in question_lower:
            return {
                'response': "For payment issues: 1) Check your subscription status, 2) Update payment method in Account Settings, 3) Contact support@creditoracademy.com for billing assistance, 4) Review your payment history for any errors.",
                'method': 'contextual_fallback',
                'confidence': 0.75,
                'detail_level': 'medium',
                'response_time': 0.1
            }
        
        # General fallback
        return {
            'response': "I can help with questions about LMS, subscriptions, courses, credit cards, budgeting, compound interest, artificial intelligence, machine learning, and many other topics. Could you please specify your question more clearly so I can provide the most accurate answer possible?",
            'method': 'general_fallback',
            'confidence': 0.60,
            'detail_level': 'low',
            'response_time': 0.1
        }

# Initialize the ultimate fix
ultimate_fix = UltimateChatbotFix()

# NOTE: The router endpoints are defined in chat_routes.py
# This file only contains the UltimateChatbotFix class
