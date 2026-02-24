"""
Avatar controller module for lip-sync and animation
"""
import numpy as np
from typing import List, Tuple, Optional
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AvatarLipSync:
    """Synchronize avatar lip-sync with audio"""
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize lip-sync controller
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.frame_duration = 0.033  # ~30 FPS
        self.samples_per_frame = int(sample_rate * self.frame_duration)
        
    def extract_mouth_shapes(self, audio: np.ndarray) -> List[str]:
        """
        Extract mouth shapes from audio for lip-sync
        
        Args:
            audio: Audio array (mono, PCM)
            
        Returns:
            List of mouth shape names: ['A', 'E', 'I', 'O', 'U', 'closed']
        """
        try:
            mouth_shapes = []
            num_frames = len(audio) // self.samples_per_frame
            
            for i in range(num_frames):
                frame = audio[i * self.samples_per_frame:(i + 1) * self.samples_per_frame]
                
                if len(frame) == 0:
                    mouth_shapes.append('closed')
                    continue
                
                # Analyze frame energy and frequency to determine mouth shape
                rms_energy = np.sqrt(np.mean(frame ** 2))
                
                if rms_energy < 0.01:
                    mouth_shapes.append('closed')
                elif rms_energy < 0.05:
                    mouth_shapes.append('O')
                elif rms_energy < 0.1:
                    mouth_shapes.append('A')
                else:
                    # Simple frequency analysis
                    try:
                        fft = np.abs(np.fft.fft(frame))
                        dominant_freq = np.argmax(fft) * self.sample_rate / len(frame)
                        
                        if dominant_freq < 1000:
                            mouth_shapes.append('O')
                        elif dominant_freq < 2000:
                            mouth_shapes.append('A')
                        elif dominant_freq < 3000:
                            mouth_shapes.append('E')
                        else:
                            mouth_shapes.append('I')
                    except:
                        mouth_shapes.append('A')
            
            return mouth_shapes
        except Exception as e:
            logger.error(f"Error extracting mouth shapes: {e}")
            return ['closed'] * (len(audio) // self.samples_per_frame)
    
    def get_mouth_position(self, mouth_shape: str) -> Tuple[float, float]:
        """
        Get mouth position for rendering
        
        Args:
            mouth_shape: Mouth shape name
            
        Returns:
            Tuple of (openness, width) where 0-1 represents percentage
        """
        positions = {
            'closed': (0.0, 0.5),
            'O': (0.7, 0.4),
            'A': (0.8, 0.6),
            'E': (0.5, 0.7),
            'I': (0.3, 0.3),
            'U': (0.6, 0.5),
        }
        return positions.get(mouth_shape, (0.0, 0.5))


class AvatarExpression:
    """Manage avatar expressions and emotions"""
    
    def __init__(self):
        """Initialize expression controller"""
        self.current_emotion = "neutral"
        self.expressions = {
            'neutral': {'eyebrows': 0, 'mouth': 'closed', 'eyes': 'open'},
            'happy': {'eyebrows': 0.3, 'mouth': 'smile', 'eyes': 'open'},
            'sad': {'eyebrows': -0.3, 'mouth': 'sad', 'eyes': 'sad'},
            'surprised': {'eyebrows': 0.5, 'mouth': 'O', 'eyes': 'wide'},
            'thinking': {'eyebrows': 0.2, 'mouth': 'closed', 'eyes': 'thinking'},
            'confused': {'eyebrows': -0.2, 'mouth': 'uncertain', 'eyes': 'confused'},
        }
    
    def set_emotion(self, emotion: str) -> dict:
        """
        Set avatar emotion
        
        Args:
            emotion: Emotion name
            
        Returns:
            Expression parameters
        """
        if emotion in self.expressions:
            self.current_emotion = emotion
            return self.expressions[emotion]
        return self.expressions['neutral']
    
    def get_emotion_for_text(self, text: str) -> str:
        """
        Detect emotion from text
        
        Args:
            text: Input text
            
        Returns:
            Emotion name
        """
        text_lower = text.lower()
        
        happy_words = ['happy', 'great', 'excellent', 'love', 'awesome', 'wonderful']
        sad_words = ['sad', 'sorry', 'bad', 'terrible', 'worst', 'unhappy']
        surprised_words = ['wow', 'amazing', 'incredible', 'shocked', 'surprised']
        thinking_words = ['think', 'hmm', 'maybe', 'considering', 'perhaps']
        confused_words = ['confused', 'not sure', 'unclear', 'confusing']
        
        if any(word in text_lower for word in happy_words):
            return 'happy'
        elif any(word in text_lower for word in sad_words):
            return 'sad'
        elif any(word in text_lower for word in surprised_words):
            return 'surprised'
        elif any(word in text_lower for word in thinking_words):
            return 'thinking'
        elif any(word in text_lower for word in confused_words):
            return 'confused'
        
        return 'neutral'


class AvatarAnimation:
    """Handle avatar animations and movements"""
    
    def __init__(self):
        """Initialize animation controller"""
        self.animations = {
            'nod': {'duration': 0.5, 'frames': ['neutral', 'nod_down', 'nod_up', 'neutral']},
            'shake': {'duration': 0.6, 'frames': ['neutral', 'shake_left', 'shake_right', 'neutral']},
            'blink': {'duration': 0.2, 'frames': ['open', 'half', 'closed', 'half', 'open']},
            'wave': {'duration': 1.0, 'frames': ['wave_start', 'wave_1', 'wave_2', 'wave_end']},
            'listen': {'duration': 2.0, 'frames': ['listen_1', 'listen_2', 'listen_1']},
            'thinking': {'duration': 1.5, 'frames': ['thinking_1', 'thinking_2', 'thinking_3']},
        }
    
    def get_animation(self, animation_name: str) -> Optional[dict]:
        """
        Get animation frames
        
        Args:
            animation_name: Name of animation
            
        Returns:
            Animation data or None
        """
        return self.animations.get(animation_name)
    
    def trigger_animation(self, animation_name: str, user_input: str = "") -> dict:
        """
        Trigger animation based on context
        
        Args:
            animation_name: Animation to trigger
            user_input: Optional user input for context
            
        Returns:
            Animation data
        """
        animation = self.get_animation(animation_name)
        if not animation:
            animation = self.get_animation('neutral')
        
        if animation is None:
            animation = {}
        
        return {
            'name': animation_name,
            'duration': animation.get('duration', 1.0),
            'frames': animation.get('frames', []),
            'loop': False
        }


class Avatar:
    """Main avatar controller"""
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize avatar
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        self.lip_sync = AvatarLipSync(sample_rate)
        self.expression = AvatarExpression()
        self.animation = AvatarAnimation()
        self.is_speaking = False
        
    def prepare_for_speech(self, text: str) -> dict:
        """
        Prepare avatar for speech
        
        Args:
            text: Text that will be spoken
            
        Returns:
            Avatar state
        """
        emotion = self.expression.get_emotion_for_text(text)
        
        return {
            'emotion': emotion,
            'expression': self.expression.set_emotion(emotion),
            'animation': self.animation.trigger_animation('listening'),
            'ready': True
        }
    
    def process_audio_for_lipsync(self, audio: np.ndarray) -> List[dict]:
        """
        Process audio and generate lip-sync data
        
        Args:
            audio: Audio array
            
        Returns:
            List of lip-sync frames with timing
        """
        mouth_shapes = self.lip_sync.extract_mouth_shapes(audio)
        
        frame_time = self.lip_sync.frame_duration
        lip_sync_data = []
        
        for i, shape in enumerate(mouth_shapes):
            timestamp = i * frame_time
            mouth_pos = self.lip_sync.get_mouth_position(shape)
            
            lip_sync_data.append({
                'timestamp': timestamp,
                'shape': shape,
                'mouth_openness': mouth_pos[0],
                'mouth_width': mouth_pos[1],
            })
        
        self.is_speaking = True
        return lip_sync_data
    
    def finish_speech(self) -> dict:
        """
        Finalize speech and return to neutral state
        
        Returns:
            Avatar state
        """
        self.is_speaking = False
        return {
            'emotion': 'neutral',
            'expression': self.expression.set_emotion('neutral'),
            'animation': self.animation.trigger_animation('thinking'),
        }
    
    def get_state(self) -> dict:
        """
        Get current avatar state
        
        Returns:
            Current state
        """
        return {
            'emotion': self.expression.current_emotion,
            'expression': self.expression.expressions[self.expression.current_emotion],
            'is_speaking': self.is_speaking,
        }
