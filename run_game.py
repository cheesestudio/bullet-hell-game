#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DG-Lab 游戏联动服务端"""

import asyncio
import qrcode
import sys
import os

from pydglab_ws import DGLabWSServer, Channel, StrengthOperationType
from websockets import serve
import json

# 波形数据
HIT_PULSE = [
    ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
    ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 92, 84, 67)),
    ((10, 10, 10, 10), (67, 58, 50, 33)), ((10, 10, 10, 10), (0, 0, 0, 0)),
    ((10, 10, 10, 10), (0, 0, 0, 1)), ((10, 10, 10, 10), (2, 2, 2, 2))
]


def get_local_ip():
    try:
        import subprocess
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('IPv4') and ':' in line:
                ip = line.split(':')[-1].strip()
                if ip.startswith('192.168.'):
                    return ip
        return "192.168.10.104"
    except:
        return "192.168.10.104"


def update_html_ip(ip):
    html_file = "bullet-hell.html"
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        pattern = r"ws://[\d.]+:5679"
        new_url = f"ws://{ip}:5679"
        if re.search(pattern, content):
            content = re.sub(pattern, new_url, content)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)


game_clients = set()
dg_client = None
dg_server = None


async def handle_game_client(websocket, path):
    global game_clients, dg_client
    print(f"[Game] Client connected", flush=True)
    game_clients.add(websocket)

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"[Game] {data}", flush=True)

                if data.get('type') == 'hit':
                    # 玩家受击 - 发送波形
                    if dg_client:
                        try:
                            ch = Channel.A if data.get('channel', 'A') == 'A' else Channel.B
                            # 发送波形 - 复制3份延长播放时间
                            await dg_client.add_pulses(ch, *HIT_PULSE, *HIT_PULSE, *HIT_PULSE)
                            print(f"[DG-Lab] Hit pulse sent!", flush=True)
                        except Exception as e:
                            print(f"[DG-Lab] Error: {e}", flush=True)

                elif data.get('type') == 'vibrate':
                    channel = data.get('channel', 'A')
                    intensity = data.get('intensity', 0)

                    if dg_client:
                        try:
                            ch = Channel.A if channel == 'A' else Channel.B
                            # set_strength(channel, operation_type, value)
                            await dg_client.set_strength(ch, StrengthOperationType.SET_TO, intensity)
                            print(f"[DG-Lab] {channel}={intensity}%", flush=True)
                        except Exception as e:
                            print(f"[DG-Lab] Error: {e}", flush=True)

            except json.JSONDecodeError as e:
                print(f"[Game] JSON error: {e}", flush=True)

    except Exception as e:
        print(f"[Game] Error: {e}", flush=True)
    finally:
        game_clients.remove(websocket)


async def main():
    global dg_client, dg_server

    host = get_local_ip()
    dg_port = 5678
    ws_port = 5679

    print("=" * 50, flush=True)
    print(f"DG-Lab Game Link", flush=True)
    print(f"IP: {host}", flush=True)
    print("=" * 50, flush=True)

    # 启动DG-Lab服务
    print(f"[DG-Lab] Port {dg_port}...", flush=True)
    dg_server = DGLabWSServer("0.0.0.0", dg_port, 300)
    await dg_server.__aenter__()

    client = dg_server.new_local_client()
    dg_client = client
    url = client.get_qrcode(f"ws://{host}:{dg_port}")

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save("dgcode.png")

    print("=" * 50, flush=True)
    print(f"[二维码] 已保存到 dgcode.png", flush=True)
    print(f"[连接地址] {url}", flush=True)
    print("=" * 50, flush=True)

    # 游戏WebSocket
    print(f"[Game] Port {ws_port}...", flush=True)
    await serve(handle_game_client, "0.0.0.0", ws_port)
    print("[Game] Ready!", flush=True)

    # 更新HTML
    update_html_ip(host)

    # HTTP服务
    import threading
    import http.server
    import socketserver

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    HTTP_PORT = 8080
    httpd = None

    try:
        httpd = socketserver.TCPServer(("", HTTP_PORT), Handler)
        httpd_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        httpd_thread.start()
    except:
        HTTP_PORT = 8000
        try:
            httpd = socketserver.TCPServer(("", HTTP_PORT), Handler)
            httpd_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            httpd_thread.start()
        except:
            HTTP_PORT = 8888
            httpd = socketserver.TCPServer(("", HTTP_PORT), Handler)
            httpd_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            httpd_thread.start()

    game_url = f"http://{host}:{HTTP_PORT}/bullet-hell.html"
    print(f"[HTTP] {game_url}", flush=True)

    import webbrowser
    webbrowser.open(game_url)

    print(f"\n[Ready] WS: ws://{host}:{ws_port}", flush=True)
    print("[Info] Scan QR then play game\n", flush=True)

    # 等待DG-Lab连接
    for i in range(120):
        await asyncio.sleep(1)
        if dg_server.uuid_to_ws:
            print(f"[DG-Lab] App connected!", flush=True)
            break
        if i % 20 == 0:
            print(f"[DG-Lab] Waiting... {i}s", flush=True)

    try:
        while True:
            await asyncio.sleep(30)
            print(f"[Status] DG: {'OK' if dg_server.uuid_to_ws else 'WAIT'}", flush=True)
    except KeyboardInterrupt:
        print("\n[Exit]", flush=True)


if __name__ == "__main__":
    asyncio.run(main())