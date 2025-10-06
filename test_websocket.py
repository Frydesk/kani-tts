"""Test script for WebSocket TTS integration"""

import asyncio
import logging
import os
from websocket_client import KaniTTSClient, SpanishAITTSIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_basic_client():
    """Test basic WebSocket client functionality"""
    logger.info("🧪 Testing basic WebSocket client...")
    
    client = KaniTTSClient()
    
    try:
        # Connect
        if not await client.connect():
            logger.error("❌ Failed to connect to server")
            return False
        
        # Test ping
        if not await client.ping():
            logger.error("❌ Ping test failed")
            return False
        
        # Test simple TTS request
        test_text = "Hello, this is a test of the WebSocket TTS system."
        audio_data = await client.send_tts_request(test_text)
        
        if audio_data:
            # Save test audio
            with open("test_basic.wav", "wb") as f:
                f.write(audio_data)
            logger.info(f"✅ Basic test successful - saved {len(audio_data)} bytes to test_basic.wav")
            return True
        else:
            logger.error("❌ No audio data received")
            return False
            
    except Exception as e:
        logger.error(f"❌ Basic test failed: {e}")
        return False
    finally:
        await client.disconnect()


async def test_spanish_integration():
    """Test Spanish AI integration"""
    logger.info("🧪 Testing Spanish AI integration...")
    
    integration = SpanishAITTSIntegration()
    
    try:
        # Initialize
        if not await integration.initialize():
            logger.error("❌ Failed to initialize Spanish AI integration")
            return False
        
        # Test Spanish text generation
        spanish_texts = [
            "¡Hola! ¿Cómo estás hoy?",
            "Buenos días, espero que tengas un día maravilloso.",
            "¿Puedes ayudarme con alguna pregunta en particular?",
            "Gracias por usar nuestro asistente de inteligencia artificial."
        ]
        
        for i, text in enumerate(spanish_texts):
            logger.info(f"🎤 Generating speech for: {text}")
            
            # Test with different emotions
            emotions = ["friendly", "professional", "excited", "calm"]
            emotion = emotions[i % len(emotions)]
            
            voice_config = {
                "emotion": emotion,
                "speed": 1.0 + (i * 0.1)  # Vary speed slightly
            }
            
            audio_data = await integration.generate_speech(text, voice_config)
            
            if audio_data:
                filename = f"test_spanish_{i+1}_{emotion}.wav"
                with open(filename, "wb") as f:
                    f.write(audio_data)
                logger.info(f"✅ Saved {filename} ({len(audio_data)} bytes)")
            else:
                logger.error(f"❌ Failed to generate audio for text {i+1}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Spanish integration test failed: {e}")
        return False
    finally:
        await integration.disconnect()


async def test_streaming():
    """Test streaming functionality"""
    logger.info("🧪 Testing streaming functionality...")
    
    integration = SpanishAITTSIntegration()
    
    try:
        # Initialize
        if not await integration.initialize():
            logger.error("❌ Failed to initialize for streaming test")
            return False
        
        # Test streaming
        long_text = """
        Este es un texto más largo para probar la funcionalidad de streaming.
        El sistema debería enviar chunks de audio en tiempo real mientras genera el contenido.
        Esto es especialmente útil para conversaciones en tiempo real donde necesitamos
        una respuesta rápida y fluida del asistente de inteligencia artificial.
        """
        
        chunk_count = 0
        total_bytes = 0
        
        def on_chunk(audio_bytes, metadata):
            nonlocal chunk_count, total_bytes
            chunk_count += 1
            total_bytes += len(audio_bytes)
            logger.info(f"📦 Chunk {chunk_count}: {len(audio_bytes)} bytes, {metadata['duration']:.2f}s")
        
        logger.info("🎤 Starting streaming generation...")
        success = await integration.stream_speech(long_text, chunk_callback=on_chunk)
        
        if success:
            logger.info(f"✅ Streaming test successful - {chunk_count} chunks, {total_bytes} total bytes")
            return True
        else:
            logger.error("❌ Streaming test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Streaming test failed: {e}")
        return False
    finally:
        await integration.disconnect()


async def main():
    """Run all tests"""
    logger.info("🚀 Starting WebSocket TTS tests...")
    
    tests = [
        ("Basic Client", test_basic_client),
        ("Spanish Integration", test_spanish_integration),
        ("Streaming", test_streaming)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! WebSocket integration is working correctly.")
    else:
        logger.error("⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())

