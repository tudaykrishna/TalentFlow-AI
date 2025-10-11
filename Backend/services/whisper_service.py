"""Local Whisper Service - GPU-Accelerated Transcription"""
import os
import logging
import torch
from faster_whisper import WhisperModel
from typing import Optional, Tuple
import tempfile

logger = logging.getLogger(__name__)


class LocalWhisperService:
    """
    GPU-accelerated local Whisper transcription service
    
    Features:
    - GPU-only mode (fails if GPU not available)
    - Uses medium model for best accuracy/speed balance
    - Thread-safe lazy loading
    - Memory efficient
    """
    
    def __init__(self):
        """Initialize the service (model loaded lazily on first use)"""
        self.model: Optional[WhisperModel] = None
        self.model_size = "medium"
        self.device = "cuda"  # GPU only
        self.compute_type = "float16"  # Optimized for RTX 3060
        
        logger.info("🎙️  LocalWhisperService initialized (lazy loading)")
    
    def _load_model(self):
        """Load the Whisper model onto GPU"""
        if self.model is not None:
            return  # Already loaded
        
        try:
            logger.info(f"📥 Loading Whisper model: {self.model_size}")
            logger.info(f"   Device: {self.device}")
            logger.info(f"   Compute type: {self.compute_type}")
            
            # Check GPU availability
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "GPU not available! LocalWhisperService requires CUDA-enabled GPU. "
                    "Please use Azure API transcription instead."
                )
            
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"   GPU: {gpu_name}")
            
            # Load model on GPU
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None,  # Use default cache directory
                local_files_only=False  # Download if not present
            )
            
            logger.info(f"✅ Whisper model loaded successfully on GPU")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to initialize local Whisper: {e}")
    
    def is_available(self) -> bool:
        """
        Check if local Whisper is available (GPU accessible)
        
        Returns:
            bool: True if GPU is available, False otherwise
        """
        try:
            return torch.cuda.is_available()
        except Exception as e:
            logger.warning(f"GPU check failed: {e}")
            return False
    
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> Tuple[str, dict]:
        """
        Transcribe audio file using local Whisper on GPU
        
        Args:
            audio_file_path: Path to audio file
            language: Optional language code (e.g., 'en'). None for auto-detect.
        
        Returns:
            Tuple of (transcribed_text, metadata)
            
        Raises:
            RuntimeError: If GPU not available or transcription fails
        """
        # Ensure model is loaded
        if self.model is None:
            self._load_model()
        
        try:
            logger.info(f"🎤 Transcribing audio file: {audio_file_path}")
            
            # Get file size for logging
            file_size = os.path.getsize(audio_file_path)
            logger.info(f"   File size: {file_size / 1024:.2f} KB")
            
            # Transcribe
            import time
            start_time = time.time()
            
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )
            
            # Combine all segments into full text
            transcribed_text = " ".join([segment.text for segment in segments])
            
            elapsed_time = time.time() - start_time
            
            # Get GPU memory usage
            if torch.cuda.is_available():
                gpu_memory_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
                torch.cuda.reset_peak_memory_stats()
            else:
                gpu_memory_mb = 0
            
            metadata = {
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "processing_time": round(elapsed_time, 2),
                "gpu_memory_mb": round(gpu_memory_mb, 2),
                "model_size": self.model_size,
                "device": self.device
            }
            
            logger.info(f"✅ Transcription complete:")
            logger.info(f"   Text length: {len(transcribed_text)} chars")
            logger.info(f"   Language: {info.language} ({info.language_probability:.2%})")
            logger.info(f"   Duration: {info.duration:.2f}s")
            logger.info(f"   Processing time: {elapsed_time:.2f}s")
            logger.info(f"   Speed: {info.duration / elapsed_time:.2f}x realtime")
            logger.info(f"   GPU memory: {gpu_memory_mb:.2f} MB")
            
            return transcribed_text.strip(), metadata
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise RuntimeError(f"Local Whisper transcription failed: {e}")
    
    async def transcribe_upload(self, audio_data: bytes, filename: str = "audio.wav") -> Tuple[str, dict]:
        """
        Transcribe audio from uploaded bytes
        
        Args:
            audio_data: Audio file bytes
            filename: Original filename (for logging)
        
        Returns:
            Tuple of (transcribed_text, metadata)
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            logger.info(f"📁 Processing uploaded file: {filename}")
            text, metadata = self.transcribe(temp_path)
            metadata["filename"] = filename
            return text, metadata
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")
    
    def get_status(self) -> dict:
        """
        Get current service status
        
        Returns:
            dict: Status information
        """
        gpu_available = torch.cuda.is_available()
        
        status = {
            "available": gpu_available,
            "model_loaded": self.model is not None,
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type
        }
        
        if gpu_available:
            status["gpu_name"] = torch.cuda.get_device_name(0)
            status["gpu_memory_total_mb"] = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
            status["gpu_memory_used_mb"] = torch.cuda.memory_allocated() / 1024 / 1024
            status["cuda_version"] = torch.version.cuda
        
        return status
    
    def unload_model(self):
        """Unload model from GPU to free memory"""
        if self.model is not None:
            logger.info("🗑️  Unloading Whisper model from GPU")
            del self.model
            self.model = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ Model unloaded, GPU memory freed")


# Global service instance
whisper_service = LocalWhisperService()

