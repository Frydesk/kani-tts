"""WebSocket client for Kani TTS - Example implementation for Spanish AI Assistant"""

import asyncio
import json
import base64
import io
import logging
from typing import Optional, Callable, Dict, Any
import websockets
from websockets.client import WebSocketClientProtocol

from websocket_config import (
    WEBSOCKET_HOST, WEBSOCKET_PORT, MESSAGE_TYPES, 
    DEFAULT_CONFIG, ERROR_MESSAGES
)

logger = logging.getLogger(__name__)


class KaniTTSClient:
    """WebSocket client for Kani TTS server"""
    
    def __init__(self, host: str = WEBSOCKET_HOST, port: int = WEBSOCKET_PORT):
        self.host = host
        self.port = port
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.websocket = await websockets.connect(uri)
            self.connected = True
            logger.info(f"✅ Connected to Kani TTS server at {uri}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("🔌 Disconnected from server")
    
    async def send_tts_request(self, text: str, config: Optional[Dict[str, Any]] = None, 
                             reference_audio: Optional[bytes] = None) -> Optional[bytes]:
        """Send TTS request and get complete audio"""
        if not self.connected or not self.websocket:
            raise ConnectionError("Not connected to server")
        
        # Prepare request
        request_data = {
            "type": MESSAGE_TYPES["TTS_REQUEST"],
            "data": {
                "text": text,
                "config": config or DEFAULT_CONFIG
            }
        }
        
        # Add reference audio if provided
        if reference_audio:
            request_data["data"]["reference_audio"] = base64.b64encode(reference_audio).decode('utf-8')
        
        # Send request
        await self.websocket.send(json.dumps(request_data))
        logger.info(f"📤 Sent TTS request: {len(text)} characters")
        
        # Wait for response
        response = await self.websocket.recv()
        data = json.loads(response)
        
        if data["type"] == MESSAGE_TYPES["TTS_RESPONSE"]:
            response_data = data["data"]
            if response_data["status"] == "success":
                # Decode audio
                audio_b64 = response_data["audio"]
                audio_bytes = base64.b64decode(audio_b64)
                logger.info(f"✅ Received audio: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                raise Exception(f"TTS error: {response_data['message']}")
        else:
            raise Exception(f"Unexpected response type: {data['type']}")
    
    async def stream_tts_request(self, text: str, config: Optional[Dict[str, Any]] = None,
                                reference_audio: Optional[bytes] = None,
                                chunk_callback: Optional[Callable[[bytes, Dict[str, Any]], None]] = None) -> bool:
        """Send streaming TTS request and handle chunks"""
        if not self.connected or not self.websocket:
            raise ConnectionError("Not connected to server")
        
        # Prepare request
        request_data = {
            "type": MESSAGE_TYPES["TTS_STREAM_REQUEST"],
            "data": {
                "text": text,
                "config": config or DEFAULT_CONFIG
            }
        }
        
        # Add reference audio if provided
        if reference_audio:
            request_data["data"]["reference_audio"] = base64.b64encode(reference_audio).decode('utf-8')
        
        # Send request
        await self.websocket.send(json.dumps(request_data))
        logger.info(f"📤 Sent streaming TTS request: {len(text)} characters")
        
        # Handle streaming responses
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data["type"] == MESSAGE_TYPES["TTS_STREAM_CHUNK"]:
                    # Handle audio chunk
                    chunk_data = data["data"]
                    if chunk_data["status"] == "streaming":
                        # Decode audio chunk
                        audio_b64 = chunk_data["audio"]
                        audio_bytes = base64.b64decode(audio_b64)
                        metadata = chunk_data["metadata"]
                        
                        logger.info(f"📦 Received chunk: {len(audio_bytes)} bytes ({metadata['duration']:.2f}s)")
                        
                        # Call callback if provided
                        if chunk_callback:
                            chunk_callback(audio_bytes, metadata)
                
                elif data["type"] == MESSAGE_TYPES["TTS_STREAM_COMPLETE"]:
                    # Streaming completed
                    logger.info("✅ Streaming completed")
                    return True
                
                elif data["type"] == MESSAGE_TYPES["TTS_RESPONSE"]:
                    # Error response
                    response_data = data["data"]
                    if response_data["status"] == "error":
                        raise Exception(f"Streaming error: {response_data['message']}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.error("❌ Connection closed during streaming")
            return False
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            return False
    
    async def ping(self) -> bool:
        """Send ping to check server health"""
        if not self.connected or not self.websocket:
            return False
        
        try:
            ping_data = {
                "type": MESSAGE_TYPES["PING"],
                "data": {}
            }
            await self.websocket.send(json.dumps(ping_data))
            
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data["type"] == MESSAGE_TYPES["PONG"]:
                logger.info("🏓 Server is alive")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"❌ Ping failed: {e}")
            return False


class SpanishAITTSIntegration:
    """Integration class for Spanish AI Assistant"""
    
    def __init__(self, tts_host: str = WEBSOCKET_HOST, tts_port: int = WEBSOCKET_PORT):
        self.tts_client = KaniTTSClient(tts_host, tts_port)
        self.connected = False
        
    async def initialize(self) -> bool:
        """Initialize TTS connection"""
        self.connected = await self.tts_client.connect()
        if self.connected:
            # Test connection
            health_check = await self.tts_client.ping()
            return health_check
        return False
    
    async def generate_speech(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
        """Generate speech for Spanish text"""
        if not self.connected:
            await self.initialize()
        
        # Spanish-optimized configuration
        spanish_config = {
            **DEFAULT_CONFIG,
            "language": "spanish",
            "emotion": voice_config.get("emotion", "friendly") if voice_config else "friendly",
            "speed": voice_config.get("speed", 1.0) if voice_config else 1.0,
            **voice_config or {}
        }
        
        try:
            audio_data = await self.tts_client.send_tts_request(text, spanish_config)
            return audio_data
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return None
    
    async def stream_speech(self, text: str, voice_config: Optional[Dict[str, Any]] = None,
                          on_chunk: Optional[Callable[[bytes, Dict[str, Any]], None]] = None) -> bool:
        """Stream speech generation for real-time playback"""
        if not self.connected:
            await self.initialize()
        
        # Spanish-optimized configuration
        spanish_config = {
            **DEFAULT_CONFIG,
            "language": "spanish",
            "emotion": voice_config.get("emotion", "friendly") if voice_config else "friendly",
            "speed": voice_config.get("speed", 1.0) if voice_config else 1.0,
            **voice_config or {}
        }
        
        try:
            success = await self.tts_client.stream_tts_request(text, spanish_config, chunk_callback=on_chunk)
            return success
        except Exception as e:
            logger.error(f"Speech streaming failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from TTS server"""
        if self.connected:
            await self.tts_client.disconnect()
            self.connected = False


# Example usage for testing
async def test_client():
    """Test the WebSocket client"""
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    client = KaniTTSClient()
    
    try:
        # Connect
        if await client.connect():
            # Test ping
            await client.ping()
            
            # Test TTS request
            spanish_text = "¡Hola! Soy tu asistente de inteligencia artificial. ¿Cómo puedo ayudarte hoy?"
            audio_data = await client.send_tts_request(spanish_text)
            
            if audio_data:
                # Save audio to file
                with open("test_output.wav", "wb") as f:
                    f.write(audio_data)
                print("✅ Audio saved to test_output.wav")
            
            # Test streaming
            def on_chunk(audio_bytes, metadata):
                print(f"📦 Chunk received: {len(audio_bytes)} bytes, {metadata['duration']:.2f}s")
            
            await client.stream_tts_request(spanish_text, chunk_callback=on_chunk)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_client())

