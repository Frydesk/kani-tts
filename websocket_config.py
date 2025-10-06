"""WebSocket server configuration for Kani TTS"""

# WebSocket server settings
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8001
WEBSOCKET_PING_INTERVAL = 20
WEBSOCKET_PING_TIMEOUT = 10

# Message types
MESSAGE_TYPES = {
    "TTS_REQUEST": "tts_request",
    "TTS_STREAM_REQUEST": "tts_stream_request", 
    "TTS_RESPONSE": "tts_response",
    "TTS_STREAM_CHUNK": "tts_stream_chunk",
    "TTS_STREAM_COMPLETE": "tts_stream_complete",
    "PING": "ping",
    "PONG": "pong"
}

# Default TTS configuration
DEFAULT_CONFIG = {
    "temperature": 0.6,
    "max_tokens": 1200,
    "top_p": 0.95,
    "chunk_size": 25,
    "lookback_frames": 15,
    "language": "spanish",
    "emotion": "neutral",
    "speed": 1.0,
    "voice_id": "default"
}

# Supported languages
SUPPORTED_LANGUAGES = [
    "spanish",
    "english", 
    "french",
    "german",
    "italian",
    "portuguese"
]

# Supported emotions
SUPPORTED_EMOTIONS = [
    "neutral",
    "happy",
    "sad",
    "angry",
    "excited",
    "calm",
    "friendly",
    "professional"
]

# Audio format settings
AUDIO_FORMAT = {
    "sample_rate": 22050,
    "channels": 1,
    "bit_depth": 16,
    "format": "wav"
}

# Streaming settings
STREAMING_CONFIG = {
    "chunk_timeout": 30,  # seconds
    "max_chunk_size": 1024 * 1024,  # 1MB
    "compression": False
}

# Error messages
ERROR_MESSAGES = {
    "INVALID_JSON": "Invalid JSON format",
    "MISSING_TEXT": "No text provided",
    "UNKNOWN_MESSAGE_TYPE": "Unknown message type",
    "GENERATION_ERROR": "Audio generation failed",
    "STREAMING_ERROR": "Audio streaming failed",
    "TIMEOUT_ERROR": "Request timeout",
    "MODEL_NOT_INITIALIZED": "TTS models not initialized"
}

