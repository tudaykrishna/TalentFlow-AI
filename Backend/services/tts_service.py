"""Text-to-Speech Service using gTTS (Google Text-to-Speech)"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech Service using Google TTS"""
    
    def __init__(self):
        """Initialize the TTS Service"""
        logger.info("TTS Service initialized")
    
    def is_available(self) -> bool:
        """Check if TTS service is available (dynamic check)"""
        try:
            import gtts
            return True
        except ImportError:
            return False
    
    async def text_to_speech(self, text: str, output_path: str = None) -> str:
        """
        Convert text to speech using Google TTS
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Import gTTS (will fail if not installed)
            from gtts import gTTS
            
            # Create output path if not provided
            if output_path is None:
                temp_dir = "uploads/tts"
                os.makedirs(temp_dir, exist_ok=True)
                output_path = os.path.join(temp_dir, f"tts_{os.urandom(8).hex()}.mp3")
            
            logger.info(f"🔊 Generating speech with gTTS: {text[:50]}...")
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
            logger.info(f"✅ Speech generated: {output_path}")
            return output_path
            
        except ImportError as e:
            error_msg = "gTTS not installed. Run: pip install gTTS"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"❌ Error generating speech: {e}")
            raise RuntimeError(f"Failed to generate speech: {str(e)}") from e
    
    def get_status(self) -> dict:
        """Get TTS service status"""
        available = self.is_available()
        return {
            "available": available,
            "service": "Google TTS (gTTS)",
            "language": "en"
        }


# Global service instance
tts_service = TTSService()

