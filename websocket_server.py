"""WebSocket server for Kani TTS with F5-TTS compatible protocol"""

import asyncio
import json
import base64
import io
import struct
import time
import queue
import threading
from typing import Dict, Any, Optional
import numpy as np
from scipy.io.wavfile import write as wav_write
import websockets
from websockets.server import WebSocketServerProtocol
import logging

from audio import LLMAudioPlayer, StreamingAudioWriter
from generation import TTSGenerator
from config import CHUNK_SIZE, LOOKBACK_FRAMES, TEMPERATURE, TOP_P, MAX_TOKENS, SAMPLE_RATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances (initialized on startup)
generator = None
player = None


class TTSConfig:
    """Configuration for TTS generation"""
    def __init__(self, data: Dict[str, Any]):
        self.temperature = data.get("temperature", TEMPERATURE)
        self.max_tokens = data.get("max_tokens", MAX_TOKENS)
        self.top_p = data.get("top_p", TOP_P)
        self.chunk_size = data.get("chunk_size", CHUNK_SIZE)
        self.lookback_frames = data.get("lookback_frames", LOOKBACK_FRAMES)
        self.language = data.get("language", "spanish")
        self.emotion = data.get("emotion", "neutral")
        self.speed = data.get("speed", 1.0)
        self.voice_id = data.get("voice_id", "default")


class WebSocketTTSHandler:
    """Handles TTS requests via WebSocket"""
    
    def __init__(self):
        self.generator = None
        self.player = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize TTS models"""
        if not self.initialized:
            logger.info("🚀 Initializing TTS models...")
            self.generator = TTSGenerator()
            self.player = LLMAudioPlayer(self.generator.tokenizer)
            self.initialized = True
            logger.info("✅ TTS models initialized successfully!")
    
    async def handle_tts_request(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]) -> None:
        """Handle TTS request and send response"""
        try:
            data = message.get("data", {})
            text = data.get("text", "")
            config_data = data.get("config", {})
            reference_audio = data.get("reference_audio")
            
            if not text:
                await self._send_error(websocket, "No text provided")
                return
            
            config = TTSConfig(config_data)
            
            # Initialize models if not already done
            await self.initialize()
            
            # Generate audio
            audio_data = await self._generate_audio(text, config, reference_audio)
            
            # Send response
            response = {
                "type": "tts_response",
                "data": {
                    "audio": base64.b64encode(audio_data).decode('utf-8'),
                    "status": "success",
                    "message": "Audio generated successfully",
                    "metadata": {
                        "duration": len(audio_data) / (SAMPLE_RATE * 2),  # 16-bit audio
                        "sample_rate": SAMPLE_RATE,
                        "channels": 1,
                        "language": config.language,
                        "emotion": config.emotion,
                        "speed": config.speed
                    }
                }
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"✅ Sent audio response: {len(audio_data)} bytes")
            
        except Exception as e:
            logger.error(f"Error handling TTS request: {e}")
            await self._send_error(websocket, str(e))
    
    async def handle_streaming_request(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]) -> None:
        """Handle streaming TTS request"""
        try:
            data = message.get("data", {})
            text = data.get("text", "")
            config_data = data.get("config", {})
            reference_audio = data.get("reference_audio")
            
            if not text:
                await self._send_error(websocket, "No text provided")
                return
            
            config = TTSConfig(config_data)
            
            # Initialize models if not already done
            await self.initialize()
            
            # Start streaming generation
            await self._stream_audio(websocket, text, config, reference_audio)
            
        except Exception as e:
            logger.error(f"Error handling streaming request: {e}")
            await self._send_error(websocket, str(e))
    
    async def _generate_audio(self, text: str, config: TTSConfig, reference_audio: Optional[str] = None) -> bytes:
        """Generate complete audio file"""
        # Create audio writer
        audio_writer = StreamingAudioWriter(
            self.player,
            output_file=None,  # We won't write to file
            chunk_size=config.chunk_size,
            lookback_frames=config.lookback_frames
        )
        audio_writer.start()
        
        # Generate speech
        result = self.generator.generate(
            text,
            audio_writer,
            max_tokens=config.max_tokens
        )
        
        # Finalize and get audio
        audio_writer.finalize()
        
        if not audio_writer.audio_chunks:
            raise Exception("No audio generated")
        
        # Concatenate all chunks
        full_audio = np.concatenate(audio_writer.audio_chunks)
        
        # Convert to WAV bytes
        wav_buffer = io.BytesIO()
        wav_write(wav_buffer, SAMPLE_RATE, full_audio)
        wav_buffer.seek(0)
        
        return wav_buffer.read()
    
    async def _stream_audio(self, websocket: WebSocketServerProtocol, text: str, config: TTSConfig, reference_audio: Optional[str] = None) -> None:
        """Stream audio chunks as they're generated"""
        chunk_queue = queue.Queue()
        
        # Create a custom list wrapper that pushes chunks to queue
        class ChunkList(list):
            def append(self, chunk):
                super().append(chunk)
                chunk_queue.put(("chunk", chunk))
        
        audio_writer = StreamingAudioWriter(
            self.player,
            output_file=None,
            chunk_size=config.chunk_size,
            lookback_frames=config.lookback_frames
        )
        
        # Replace audio_chunks list with our custom one
        audio_writer.audio_chunks = ChunkList()
        
        # Start generation in background thread
        def generate():
            try:
                audio_writer.start()
                self.generator.generate(
                    text,
                    audio_writer,
                    max_tokens=config.max_tokens
                )
                audio_writer.finalize()
                chunk_queue.put(("done", None))  # Signal completion
            except Exception as e:
                logger.error(f"Generation error: {e}")
                chunk_queue.put(("error", str(e)))
        
        gen_thread = threading.Thread(target=generate)
        gen_thread.start()
        
        # Stream chunks as they arrive
        try:
            while True:
                try:
                    msg_type, data = chunk_queue.get(timeout=30)  # 30s timeout
                    
                    if msg_type == "chunk":
                        # Convert numpy array to int16 PCM
                        pcm_data = (data * 32767).astype(np.int16)
                        chunk_bytes = pcm_data.tobytes()
                        
                        # Encode as base64
                        audio_b64 = base64.b64encode(chunk_bytes).decode('utf-8')
                        
                        # Send streaming chunk
                        response = {
                            "type": "tts_stream_chunk",
                            "data": {
                                "audio": audio_b64,
                                "status": "streaming",
                                "metadata": {
                                    "chunk_size": len(chunk_bytes),
                                    "duration": len(data) / SAMPLE_RATE,
                                    "sample_rate": SAMPLE_RATE,
                                    "channels": 1
                                }
                            }
                        }
                        
                        await websocket.send(json.dumps(response))
                        logger.info(f"[STREAM] Sent chunk: {len(chunk_bytes)} bytes ({len(data)/SAMPLE_RATE:.2f}s)")
                        
                    elif msg_type == "done":
                        # Send completion message
                        response = {
                            "type": "tts_stream_complete",
                            "data": {
                                "status": "completed",
                                "message": "Audio streaming completed"
                            }
                        }
                        await websocket.send(json.dumps(response))
                        logger.info("✅ Streaming completed")
                        break
                        
                    elif msg_type == "error":
                        await self._send_error(websocket, f"Generation error: {data}")
                        break
                        
                except queue.Empty:
                    await self._send_error(websocket, "Generation timeout")
                    break
                    
        finally:
            gen_thread.join()
    
    async def _send_error(self, websocket: WebSocketServerProtocol, error_message: str) -> None:
        """Send error response"""
        response = {
            "type": "tts_response",
            "data": {
                "audio": "",
                "status": "error",
                "message": error_message
            }
        }
        await websocket.send(json.dumps(response))
        logger.error(f"Sent error response: {error_message}")


# Global handler instance
tts_handler = WebSocketTTSHandler()


async def handle_client(websocket: WebSocketServerProtocol, path: str) -> None:
    """Handle WebSocket client connections"""
    client_addr = websocket.remote_address
    logger.info(f"🔗 New client connected: {client_addr}")
    
    try:
        async for message in websocket:
            try:
                # Parse JSON message
                data = json.loads(message)
                message_type = data.get("type", "")
                
                logger.info(f"📨 Received message type: {message_type}")
                
                if message_type == "tts_request":
                    await tts_handler.handle_tts_request(websocket, data)
                elif message_type == "tts_stream_request":
                    await tts_handler.handle_streaming_request(websocket, data)
                elif message_type == "ping":
                    # Health check
                    response = {
                        "type": "pong",
                        "data": {
                            "status": "alive",
                            "tts_initialized": tts_handler.initialized
                        }
                    }
                    await websocket.send(json.dumps(response))
                else:
                    await tts_handler._send_error(websocket, f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                await tts_handler._send_error(websocket, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await tts_handler._send_error(websocket, str(e))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Client disconnected: {client_addr}")
    except Exception as e:
        logger.error(f"Connection error: {e}")


async def main():
    """Start WebSocket server"""
    logger.info("🎤 Starting Kani TTS WebSocket Server...")
    
    # Initialize TTS models
    await tts_handler.initialize()
    
    # Start WebSocket server
    server = await websockets.serve(
        handle_client,
        "localhost",
        8001,  # Different port from REST API
        ping_interval=20,
        ping_timeout=10
    )
    
    logger.info("✅ WebSocket server started on ws://localhost:8001")
    logger.info("📋 Supported message types:")
    logger.info("   - tts_request: Generate complete audio")
    logger.info("   - tts_stream_request: Stream audio chunks")
    logger.info("   - ping: Health check")
    
    # Keep server running
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

