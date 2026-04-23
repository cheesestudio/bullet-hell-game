#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DG-Lab 连接二维码生成脚本"""

import asyncio
import qrcode
import sys


def test_connectivity(host: str, port: int):
    """测试端口连通性"""
    import socket
    print(f"[测试] 尝试连接 {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"[测试] 端口 {port} 可达")
            return True
        else:
            print(f"[测试] 端口 {port} 不可达 (code: {result})")
            return False
    except Exception as e:
        print(f"[测试] 连接错误: {e}")
        return False


async def generate_qrcode(
    host: str = "192.168.10.104",
    port: int = 5678,
    output_path: str = "dgcode.png"
) -> str:
    """生成二维码"""
    from pydglab_ws import DGLabWSServer

    print(f"[日志] 启动服务端 0.0.0.0:{port}...")

    async with DGLabWSServer("0.0.0.0", port, 60) as server:
        print(f"[日志] 服务端已启动，等待连接...")

        client = server.new_local_client()
        ws_url = f"ws://{host}:{port}"
        url = client.get_qrcode(ws_url)

        # 生成二维码
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

        print(f"[日志] 二维码已保存")
        print("=" * 40)
        print(f"连接地址: ws://{host}:{port}")
        print(f"请用 DG-Lab App 扫描连接")
        print("=" * 40)

        # 打印已连接的客户端
        import asyncio
        for i in range(30):
            await asyncio.sleep(2)
            clients = list(server.uuid_to_ws.keys())
            if clients:
                print(f"[日志] 检测到连接: {clients}")
                break
            print(f"[日志] 等待中... ({i*2}s)")

        return url


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.10.104"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5678

    print(f"[信息] 目标: {host}:{port}")
    print(f"[信息] 测试网络连通性...")

    # 先测试能否自己连接自己
    test_connectivity(host, port)

    asyncio.run(generate_qrcode(host, port, "dgcode.png"))


if __name__ == "__main__":
    main()