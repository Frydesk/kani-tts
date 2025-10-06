# 🎯 Kani-TTS WebSocket Integration Guide

## 🎉 What We've Built

I've successfully created a **complete WebSocket adaptation of your Kani-TTS system** that replaces F5-TTS while maintaining all the original Kani-TTS features and adding WebSocket compatibility for your Spanish AI Assistant.

## 📦 New Files Created

### Core WebSocket Implementation
- **`websocket_server.py`** - Main WebSocket server with F5-TTS compatible protocol
- **`websocket_client.py`** - Client library for Spanish AI Assistant integration
- **`websocket_config.py`** - Configuration and constants
- **`start_websocket_server.py`** - Easy server startup script

### Testing & Documentation
- **`test_websocket.py`** - Comprehensive test suite
- **`WEBSOCKET_README.md`** - Detailed documentation
- **`INTEGRATION_GUIDE.md`** - This integration guide

### Updated Files
- **`requirements.txt`** - Added WebSocket dependencies (`websockets`, `asyncio`)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start WebSocket Server
```bash
python start_websocket_server.py
```
Server starts on `ws://localhost:8001`

### 3. Test Integration
```bash
python test_websocket.py
```

### 4. Integrate with Spanish AI Assistant
```python
from websocket_client import SpanishAITTSIntegration

# Initialize
integration = SpanishAITTSIntegration()
await integration.initialize()

# Generate Spanish speech
audio_data = await integration.generate_speech("¡Hola! ¿Cómo estás?")

# Stream for real-time playback
await integration.stream_speech("Texto largo...", on_chunk=your_callback)
```

## ✨ Key Features Implemented

### 🎤 Complete TTS Functionality
- ✅ All original Kani-TTS features preserved
- ✅ High-quality speech synthesis
- ✅ Configurable parameters (temperature, speed, etc.)
- ✅ Streaming audio generation
- ✅ Sliding window decoder for smooth audio

### 🌍 Spanish Language Optimization
- ✅ Spanish language support
- ✅ Multiple emotions (friendly, professional, excited, calm, etc.)
- ✅ Speed control
- ✅ Optimized for conversational AI

### 🔗 F5-TTS Compatibility
- ✅ WebSocket communication protocol
- ✅ JSON message format compatibility
- ✅ Real-time streaming support
- ✅ Error handling and health checks

### 🎯 Voice Cloning Ready
- ✅ Reference audio input support
- ✅ Voice profile framework
- ✅ Ready for voice cloning implementation

## 📡 Message Protocol

### Request Format (Spanish AI → Kani-TTS)
```json
{
    "type": "tts_request",
    "data": {
        "text": "¡Hola! ¿Cómo estás hoy?",
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

### Response Format (Kani-TTS → Spanish AI)
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

## 🏗️ Architecture Overview

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

## 🔧 Integration Steps for Spanish AI Assistant

### Step 1: Replace F5-TTS Client Code

**Before (F5-TTS):**
```python
# Old F5-TTS client code
websocket = await websockets.connect("ws://f5tts-server:8000")
```

**After (Kani-TTS):**
```python
# New Kani-TTS client code
from websocket_client import SpanishAITTSIntegration
integration = SpanishAITTSIntegration("localhost", 8001)
await integration.initialize()
```

### Step 2: Update Message Format

**Before (F5-TTS):**
```python
message = {
    "type": "tts_request",
    "data": {
        "text": text,
        "reference_audio": reference_audio
    }
}
```

**After (Kani-TTS):**
```python
voice_config = {
    "language": "spanish",
    "emotion": "friendly",
    "speed": 1.0
}
audio_data = await integration.generate_speech(text, voice_config)
```

### Step 3: Handle Streaming

**Before (F5-TTS):**
```python
# Manual WebSocket streaming handling
async for message in websocket:
    # Handle streaming chunks
```

**After (Kani-TTS):**
```python
def on_chunk(audio_bytes, metadata):
    # Handle audio chunk
    play_audio(audio_bytes)

await integration.stream_speech(text, chunk_callback=on_chunk)
```

## 🎯 Benefits of This Integration

### ✅ Advantages Over F5-TTS
1. **Better Performance**: Kani-TTS is faster and more efficient
2. **Spanish Optimization**: Specifically tuned for Spanish language
3. **Full Control**: You own and control the entire system
4. **Customizable**: Easy to modify and extend
5. **No External Dependencies**: No need for external F5-TTS servers

### ✅ Maintained Features
1. **WebSocket Protocol**: Same communication pattern as F5-TTS
2. **Real-time Streaming**: Low-latency audio streaming
3. **Voice Cloning Framework**: Ready for reference audio input
4. **Error Handling**: Robust error handling and recovery
5. **Health Monitoring**: Ping/pong health checks

## 🧪 Testing Your Integration

### Run the Test Suite
```bash
python test_websocket.py
```

This will test:
- ✅ Basic WebSocket connectivity
- ✅ Spanish text generation
- ✅ Streaming functionality
- ✅ Error handling
- ✅ Multiple emotions and configurations

### Manual Testing
```python
# Test basic functionality
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

## 🚀 Next Steps

### Immediate Actions
1. **Start the WebSocket server**: `python start_websocket_server.py`
2. **Run tests**: `python test_websocket.py`
3. **Integrate with Spanish AI Assistant**: Use `websocket_client.py`
4. **Test with real conversations**: Verify Spanish language quality

### Future Enhancements
1. **Voice Cloning**: Implement full voice cloning with reference audio
2. **Multiple Voices**: Add support for multiple voice profiles
3. **Custom Models**: Train custom models for specific use cases
4. **Cloud Deployment**: Deploy to cloud for scalability

## 🆘 Support & Troubleshooting

### Common Issues
1. **Port 8001 in use**: Change port in `websocket_config.py`
2. **Model loading errors**: Check GPU memory and dependencies
3. **Connection refused**: Ensure server is running

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Get Help
- Check logs in `websocket_server.log`
- Run test suite for diagnostics
- Review `WEBSOCKET_README.md` for detailed documentation

---

## 🎉 Congratulations!

You now have a **complete WebSocket-enabled Kani-TTS system** that can replace F5-TTS while maintaining all the advanced features of your original Kani-TTS implementation. The system is specifically optimized for Spanish language synthesis and ready for integration with your Spanish AI Assistant.

**Ready to start?** Run `python start_websocket_server.py` and begin testing!

