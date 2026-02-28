# Athena AI Avatar Frontend

A React-based frontend for the Athena AI Avatar platform, inspired by Soul Machines and D-ID, featuring AI avatar interactions with animated responses.

## Features

- **AI Avatar Interface**: Animated avatar that responds with visual and audio feedback
- **Voice Input**: Speech-to-text microphone for hands-free interaction
- **Text-to-Speech**: Bot responses are spoken aloud
- **Real-time Chat**: Live conversation with typing indicators
- **Dual-Panel Layout**: Avatar display alongside chat interface
- **Responsive Design**: Works on all devices
- **Backend Integration**: Connects to Flask API for chat functionality
- **Modern UI**: Clean, professional design with smooth animations

## Technologies Used

- React 18 with Hooks
- Vite for fast development
- Axios for API communication
- CSS3 with animations
- Responsive design principles

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open `http://localhost:5173` in your browser

## Backend Requirements

Ensure your Flask backend is running on `http://localhost:5000` with the `/api/chat` endpoint.

## Project Structure

```
src/
├── App.jsx          # Main application with chat and avatar
├── main.jsx         # React entry point
├── index.css        # Global styles and animations
└── assets/          # Static assets
```

## Future Enhancements

- Voice input/output integration
- Video avatar support (D-ID style)
- Emotional avatar expressions (Soul Machines style)
- Multi-language support
- Advanced conversation flows
