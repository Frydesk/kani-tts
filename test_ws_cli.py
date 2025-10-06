"""Interactive CLI to test Kani TTS WebSocket server on Windows.
Prompts user for settings, connects, and performs inference (streaming or full).
"""

import asyncio
import base64
import json
import logging
from typing import Dict, Any

from websocket_client import KaniTTSClient
from websocket_config import DEFAULT_CONFIG, WEBSOCKET_HOST, WEBSOCKET_PORT


def prompt_with_default(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default


def prompt_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("Invalid number, using default.")
        return default


def prompt_int(prompt: str, default: int) -> int:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print("Invalid integer, using default.")
        return default


def prompt_choice(prompt: str, choices: Dict[str, Any], default_key: str) -> Any:
    keys = list(choices.keys())
    print(prompt)
    for i, k in enumerate(keys, start=1):
        print(f"  {i}) {k}")
    raw = input(f"Select 1-{len(keys)} [{default_key}]: ").strip()
    if not raw:
        return choices[default_key]
    try:
        idx = int(raw)
        if 1 <= idx <= len(keys):
            return choices[keys[idx - 1]]
    except ValueError:
        pass
    print("Invalid selection, using default.")
    return choices[default_key]


async def run_cli() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    print("\nKani TTS WebSocket Test CLI\n============================\n")

    # Connection settings
    host = prompt_with_default("Server host", WEBSOCKET_HOST)
    port = prompt_int("Server port", WEBSOCKET_PORT)

    client = KaniTTSClient(host, port)
    if not await client.connect():
        print("Failed to connect to server. Exiting.")
        return

    # Ping
    alive = await client.ping()
    if not alive:
        print("Server did not respond to ping. Exiting.")
        await client.disconnect()
        return

    # Mode
    mode = prompt_choice(
        "Mode:", {"Full (single WAV response)": "full", "Streaming (chunks)": "stream"}, "Full (single WAV response)"
    )

    # Core config
    language = prompt_with_default("Language", str(DEFAULT_CONFIG.get("language", "spanish")))
    emotion = prompt_with_default("Emotion", "friendly")
    speed = prompt_float("Speed (0.5-2.0)", 1.0)
    temperature = prompt_float("Temperature", float(DEFAULT_CONFIG.get("temperature", 0.6)))
    max_tokens = prompt_int("Max tokens", int(DEFAULT_CONFIG.get("max_tokens", 1200)))
    chunk_size = prompt_int("Chunk size (frames)", int(DEFAULT_CONFIG.get("chunk_size", 25)))
    lookback_frames = prompt_int("Lookback frames", int(DEFAULT_CONFIG.get("lookback_frames", 15)))

    print("")
    text = input("Enter text to synthesize: ").strip()
    if not text:
        print("No text provided. Exiting.")
        await client.disconnect()
        return

    # Optional reference audio (base64 input)
    ref_b64 = input("Optional reference audio as base64 (press Enter to skip): ").strip()
    reference_audio_bytes = None
    if ref_b64:
        try:
            reference_audio_bytes = base64.b64decode(ref_b64)
        except Exception:
            print("Invalid base64, ignoring reference audio.")
            reference_audio_bytes = None

    config = {
        "language": language,
        "emotion": emotion,
        "speed": speed,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "chunk_size": chunk_size,
        "lookback_frames": lookback_frames,
    }

    print("")
    print("Starting inference...\n")

    if mode == "full":
        try:
            audio_wav = await client.send_tts_request(text, config=config, reference_audio=reference_audio_bytes)
            if audio_wav:
                out_path = prompt_with_default("Output WAV filename", "tts_output.wav")
                with open(out_path, "wb") as f:
                    f.write(audio_wav)
                print(f"Saved: {out_path}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        total_bytes = 0
        chunk_count = 0

        async def on_chunk_handler(chunk: bytes, metadata: Dict[str, Any]):
            nonlocal total_bytes, chunk_count
            chunk_count += 1
            total_bytes += len(chunk)
            print(f"Chunk {chunk_count}: {len(chunk)} bytes, ~{metadata.get('duration', 0):.2f}s")

        try:
            # Reuse stream_tts_request's async generator by reading from websocket
            ok = await client.stream_tts_request(text, config=config, reference_audio=reference_audio_bytes, chunk_callback=on_chunk_handler)
            if ok:
                print(f"Streaming complete. {chunk_count} chunks, {total_bytes} bytes total.")
        except Exception as e:
            print(f"Error: {e}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run_cli())
