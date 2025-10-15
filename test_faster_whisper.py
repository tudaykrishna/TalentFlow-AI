"""
Test script for faster-whisper GPU transcription

This script:
1. Records audio from your microphone (5 seconds)
2. Transcribes using faster-whisper with GPU (CUDA)
3. Prints the transcription

Requirements:
- faster-whisper
- sounddevice
- numpy
- scipy
- CUDA-capable GPU

Usage:
    python test_faster_whisper.py
"""

import os
import sys
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
from pathlib import Path

# Check if faster-whisper is installed
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("❌ faster-whisper is not installed.")
    print("Install it with: pip install faster-whisper")
    sys.exit(1)

def record_audio(duration=5, samplerate=16000):
    """
    Record audio from microphone
    
    Args:
        duration: Recording duration in seconds
        samplerate: Sample rate (16000 Hz recommended for Whisper)
    
    Returns:
        numpy array of audio data
    """
    print(f"🎙️  Recording for {duration} seconds... Speak now!")
    print("(Make sure your microphone is connected and working)")
    
    try:
        # Record audio
        audio_data = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        print("✅ Recording complete!")
        return audio_data, samplerate
        
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        print("Make sure your microphone is connected and accessible.")
        sys.exit(1)

def save_audio(audio_data, samplerate, filepath="test_audio.wav"):
    """Save audio to WAV file"""
    try:
        # Convert float32 to int16 for WAV file
        audio_int16 = (audio_data * 32767).astype(np.int16)
        write_wav(filepath, samplerate, audio_int16)
        print(f"💾 Audio saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        sys.exit(1)

def transcribe_with_faster_whisper(audio_file, model_size="medium", device="cuda", compute_type="float16"):
    """
    Transcribe audio using faster-whisper with GPU
    
    Args:
        audio_file: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
        device: Device to use (cuda for GPU, cpu for CPU)
        compute_type: Computation type (float16, int8_float16, int8)
    
    Returns:
        Transcription text
    """
    print("\n" + "="*60)
    print("Initializing faster-whisper model...")
    print(f"Model: {model_size}")
    print(f"Device: {device}")
    print(f"Compute type: {compute_type}")
    print("="*60)
    
    try:
        # Initialize the model
        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        print("✅ Model loaded successfully!")
        
        # Transcribe
        print("\n🔄 Transcribing audio...")
        start_time = time.time()
        
        segments, info = model.transcribe(
            audio_file,
            beam_size=5,
            language="en",  # Force English (or set to None for auto-detection)
            vad_filter=True,  # Enable voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Collect all segments
        transcription = ""
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            transcription += segment.text + " "
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("✅ Transcription complete!")
        print(f"⏱️  Processing time: {elapsed_time:.2f} seconds")
        print(f"🌐 Detected language: {info.language} (probability: {info.language_probability:.2f})")
        print("="*60)
        
        return transcription.strip()
        
    except Exception as e:
        print(f"\n❌ Error during transcription: {e}")
        
        # Check common issues
        if "CUDA" in str(e) or "cuda" in str(e):
            print("\n💡 GPU Error detected. Trying with CPU instead...")
            try:
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                segments, info = model.transcribe(audio_file, beam_size=5)
                transcription = " ".join([segment.text for segment in segments])
                print("✅ Transcription succeeded on CPU")
                return transcription.strip()
            except Exception as cpu_error:
                print(f"❌ CPU fallback also failed: {cpu_error}")
                sys.exit(1)
        else:
            sys.exit(1)

def main():
    print("\n" + "="*60)
    print("🎤 Faster-Whisper GPU Transcription Test")
    print("="*60 + "\n")
    
    # Configuration
    MODEL_SIZE = "medium"  # Options: tiny, base, small, medium, large-v2, large-v3
    DEVICE = "cuda"  # Use GPU
    COMPUTE_TYPE = "float16"  # GPU computation type
    
    # Audio file path
    AUDIO_FILE = r"C:\Users\udayt\Downloads\(Audio) Demo - Made with Clipchamp (1).m4a"
    
    # Check if file exists
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Audio file not found: {AUDIO_FILE}")
        print("Please check the file path and try again.")
        sys.exit(1)
    
    print(f"📂 Audio file: {AUDIO_FILE}")
    print(f"📊 File size: {os.path.getsize(AUDIO_FILE) / 1024:.2f} KB\n")
    
    # Transcribe
    transcription = transcribe_with_faster_whisper(
        AUDIO_FILE,
        model_size=MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE
    )
    
    # Display results
    print("\n" + "="*60)
    print("📝 FINAL TRANSCRIPTION:")
    print("="*60)
    print(transcription)
    print("="*60 + "\n")
    
    print("\n✅ Test complete!\n")

if __name__ == "__main__":
    main()
