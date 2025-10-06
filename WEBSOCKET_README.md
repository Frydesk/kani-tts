# 🎤 Kani TTS WebSocket Integration

This document describes the WebSocket integration for Kani TTS, designed to replace F5-TTS servers while maintaining compatibility with Spanish AI Assistant communication patterns.

## 🚀 Quick Start

### 1. Start the WebSocket Server

```bash
# Start the WebSocket server
python start_websocket_server.py
```

The server will start on `ws://localhost:8001` and initialize the TTS models.

### 2. Test the Integration

```bash
# Run the test suite
python test_websocket.py
```

This will test basic functionality, Spanish integration, and streaming capabilities.

### 3. Use in Your Spanish AI Assistant

```python
from websocket_client import SpanishAITTSIntegration

# Initialize the integration
integration = SpanishAITTSIntegration()

# Generate speech
audio_data = await integration.generate_speech("¡Hola! ¿Cómo estás?")

# Stream speech for real-time playback
await integration.stream_speech("Texto largo aquí...", on_chunk=your_callback)
```

## 📋 Features

### ✅ Implemented Features

- **WebSocket Server**: Real-time communication with F5-TTS compatible protocol
- **Spanish Language Support**: Optimized for Spanish text-to-speech
- **Streaming Audio**: Real-time audio chunk streaming for immediate playback
- **Multiple Emotions**: Support for friendly, professional, excited, calm, etc.
- **Voice Cloning Ready**: Framework ready for reference audio input
- **Error Handling**: Robust error handling and connection management
- **Health Checks**: Ping/pong mechanism for connection monitoring

### 🔄 F5-TTS Compatibility

The WebSocket server implements the F5-TTS message protocol:

#### Client to Server Messages

```json
{
    "type": "tts_request",
    "data": {
        "text": "Text to synthesize",
        "reference_audio": "base64_encoded_audio",  // Optional
        "config": {
            "language": "spanish",
            "emotion": "friendly",
            "speed": 1.0,
            "temperature": 0.6,
            "max_tokens": 1200
        }
    }
}
```

#### Server to Client Messages

```json
{
    "type": "tts_response",
    "data": {
        "audio": "base64_encoded_audio",
        "status": "success",
        "message": "Audio generated successfully",
        "metadata": {
            "duration": 3.5,
            "sample_rate": 22050,
            "channels": 1,
            "language": "spanish",
            "emotion": "friendly"
        }
    }
}
```

## 🏗️ Architecture

```
┌─────────────────────┐    WebSocket     ┌─────────────────────┐
│  Spanish AI         │ ◄─────────────► │  Kani TTS           │
│  Assistant          │                 │  WebSocket Server   │
│                     │                 │                     │
│ • Chat Interface    │                 │ • WebSocket Handler │
│ • Voice Requests    │                 │ • TTS Generator     │
│ • Audio Playback    │                 │ • Streaming Writer  │
│ • Voice Cloning     │                 │ • Audio Processing  │
└─────────────────────┘                 └─────────────────────┘
```

## 📁 File Structure

```
kani-tts/
├── websocket_server.py          # Main WebSocket server
├── websocket_client.py          # Client for Spanish AI Assistant
├── websocket_config.py          # WebSocket configuration
├── test_websocket.py           # Test suite
├── start_websocket_server.py   # Server startup script
├── WEBSOCKET_README.md         # This documentation
├── server.py                   # Original REST API server
├── audio/                      # Audio processing modules
├── generation/                 # TTS generation modules
└── config.py                   # Core configuration
```

## 🔧 Configuration

### WebSocket Server Settings

Edit `websocket_config.py` to customize:

```python
# Server settings
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8001

# Default TTS configuration
DEFAULT_CONFIG = {
    "temperature": 0.6,
    "max_tokens": 1200,
    "language": "spanish",
    "emotion": "friendly",
    "speed": 1.0
}

# Supported languages
SUPPORTED_LANGUAGES = ["spanish", "english", "french", "german", "italian", "portuguese"]

# Supported emotions
SUPPORTED_EMOTIONS = ["neutral", "happy", "sad", "angry", "excited", "calm", "friendly", "professional"]
```

## 📡 Message Types

### Request Messages

- `tts_request`: Generate complete audio file
- `tts_stream_request`: Stream audio chunks in real-time
- `ping`: Health check

### Response Messages

- `tts_response`: Complete audio response or error
- `tts_stream_chunk`: Streaming audio chunk
- `tts_stream_complete`: End of streaming
- `pong`: Health check response

## 🌍 Spanish Language Optimization

The system is specifically optimized for Spanish language synthesis:

- **Pronunciation**: Accurate Spanish phoneme generation
- **Intonation**: Natural Spanish speech patterns
- **Emotions**: Spanish-appropriate emotional expressions
- **Speed Control**: Optimized for conversational Spanish

## ⚡ Streaming Architecture

The streaming system uses a sliding window decoder:

1. **Chunk Size**: 25 frames (~2.0 seconds) per iteration
2. **Lookback Frames**: 15 frames (~1.2 seconds) for context
3. **Real-time Processing**: Audio chunks sent as they're generated
4. **Low Latency**: Minimal delay for conversational AI

## 🧪 Testing

### Run All Tests

```bash
python test_websocket.py
```

### Test Individual Components

```python
# Test basic client
from websocket_client import KaniTTSClient
client = KaniTTSClient()
await client.connect()
audio = await client.send_tts_request("Hello world")

# Test Spanish integration
from websocket_client import SpanishAITTSIntegration
integration = SpanishAITTSIntegration()
await integration.initialize()
audio = await integration.generate_speech("¡Hola! ¿Cómo estás?")
```

## 🔌 Integration with Spanish AI Assistant

### Basic Integration

```python
from websocket_client import SpanishAITTSIntegration

class SpanishAI:
    def __init__(self):
        self.tts = SpanishAITTSIntegration()
    
    async def start(self):
        await self.tts.initialize()
    
    async def speak(self, text: str, emotion: str = "friendly"):
        voice_config = {"emotion": emotion}
        audio_data = await self.tts.generate_speech(text, voice_config)
        # Play audio_data using your audio player
        return audio_data
    
    async def stream_speak(self, text: str, on_chunk):
        await self.tts.stream_speech(text, chunk_callback=on_chunk)
```

### Advanced Integration with Voice Cloning

```python
async def speak_with_voice(self, text: str, reference_audio: bytes):
    # Load reference audio for voice cloning
    voice_config = {
        "emotion": "friendly",
        "voice_id": "user_voice"
    }
    
    # Generate speech with voice cloning
    audio_data = await self.tts.generate_speech(
        text, 
        voice_config, 
        reference_audio=reference_audio
    )
    
    return audio_data
```

## 🚨 Error Handling

The system includes comprehensive error handling:

- **Connection Errors**: Automatic reconnection attempts
- **Generation Errors**: Graceful fallback to default settings
- **Timeout Handling**: Configurable timeouts for long operations
- **Validation**: Input validation and sanitization

## 📊 Performance

### Benchmarks

- **Model Loading**: ~5-10 seconds on first startup
- **Audio Generation**: ~1 second for 15 seconds of audio
- **Memory Usage**: ~2GB GPU VRAM
- **Latency**: <100ms for streaming chunks

### Optimization Tips

1. **Keep Connection Alive**: Use ping/pong to maintain connection
2. **Batch Requests**: Combine multiple TTS requests when possible
3. **Streaming**: Use streaming for long texts to reduce perceived latency
4. **Voice Caching**: Cache voice profiles for repeated use

## 🔮 Future Enhancements

### Planned Features

- [ ] **Voice Cloning**: Full voice cloning with reference audio
- [ ] **Multi-Voice Support**: Multiple voice profiles per user
- [ ] **Emotion Blending**: Smooth transitions between emotions
- [ ] **Language Detection**: Automatic language detection and switching
- [ ] **Custom Models**: Support for custom trained models
- [ ] **Cloud Deployment**: Docker and cloud deployment options

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure WebSocket server is running on port 8001
2. **Model Loading Errors**: Check GPU memory and CUDA installation
3. **Audio Quality Issues**: Verify sample rate and bit depth settings
4. **Streaming Interruptions**: Check network stability and timeout settings

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This WebSocket integration follows the same license as the main Kani TTS project.

## 🤝 Contributing

Contributions are welcome! Please focus on:

- Spanish language optimization
- Voice cloning capabilities
- Performance improvements
- Error handling enhancements
- Documentation improvements

---

**Ready to integrate?** Start with `python start_websocket_server.py` and then use the client examples in `websocket_client.py` to integrate with your Spanish AI Assistant!

