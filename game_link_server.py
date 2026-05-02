#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DG-Lab 游戏联动服务端"""

import asyncio
import qrcode
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

from pydglab_ws import DGLabWSServer
from websockets import serve
import json


async def main():
    host = "192.168.10.104"
    dg_port = 5678
    ws_port = 5679

    print(f"[DG-Lab] Starting server port {dg_port}...")

    server = DGLabWSServer("0.0.0.0", dg_port, 300)
    await server.__aenter__()

    client = server.new_local_client()
    url = client.get_qrcode(f"ws://{host}:{dg_port}")

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save("dgcode.png")

    print("=" * 50)
    print("[DG-Lab] Please scan QR code with DG-Lab App")
    print(f"[DG-Lab] URL: {url}")
    print("=" * 50)

    print(f"[Game] Starting game WebSocket server on port {ws_port}...")
    await serve(handle_game_client, "0.0.0.0", ws_port)
    print(f"[Game] Game server ready!")

    # Wait for DG-Lab
    dg_connected = False
    for i in range(60):
        await asyncio.sleep(1)
        if server.uuid_to_ws:
            dg_connected = True
            print("[DG-Lab] App connected!")
            break
        if i % 10 == 0:
            print(f"[DG-Lab] Waiting... {i}s")

    print("\n" + "=" * 50)
    print("Game link server ready!")
    print(f"WebSocket address: ws://{host}:{ws_port}")
    print("=" * 50)

    # Main loop
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("\n[Exit]")


async def handle_game_client(websocket, path):
    print(f"[Game] Client connected: {id(websocket)}")
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[Game] {data}")
    except Exception as e:
        print(f"[Game] Client error: {e}")


if __name__ == "__main__":
    asyncio.run(main())