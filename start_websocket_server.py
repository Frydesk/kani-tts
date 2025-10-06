#!/usr/bin/env python3
"""Startup script for Kani TTS WebSocket server"""

import asyncio
import sys
import logging
from websocket_server import main

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('websocket_server.log')
        ]
    )

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Kani TTS WebSocket Server                ║
║                                                              ║
║  🎤 High-quality Text-to-Speech with WebSocket Support      ║
║  🌍 Multi-language support (Spanish optimized)              ║
║  ⚡ Real-time streaming audio generation                     ║
║  🔗 F5-TTS compatible protocol                               ║
║                                                              ║
║  Server will start on: ws://localhost:8001                  ║
║  Use Ctrl+C to stop the server                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

if __name__ == "__main__":
    setup_logging()
    print_banner()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

