import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Speech configuration
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

def text_to_audio(text, output_file="output_audio.wav"):
    try:
        # Configure the Azure Speech SDK
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )

        # Set the voice (optional)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

        # Create audio configuration
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

        # Initialize speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Convert text to speech
        print("🎙️ Generating speech...")
        result = synthesizer.speak_text_async(text).get()

        # Handle success or failure
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"✅ Audio generated successfully! Saved as: {output_file}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"❌ Speech synthesis canceled: {cancellation.reason}")
            if cancellation.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation.error_details}")

    except Exception as e:
        print("❌ Exception:", e)

# Example usage
if __name__ == "__main__":
    text = "Hello! This is a test of Azure Speech Services converting text into audio."
    text_to_audio(text)
