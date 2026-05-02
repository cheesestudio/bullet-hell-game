#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DG-Lab 游戏联动控制"""

import asyncio
from pydglab_ws import DGLabWSServer
from pydglab_ws import LocalClient
import qrcode


class GameLink:
    """游戏联动控制器"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server = None
        self.client = None
        self.target_id = None

    async def start(self):
        """启动服务并等待连接"""
        print(f"[联动] 启动 DG-Lab 服务 {self.host}:{self.port}")

        self.server = DGLabWSServer("0.0.0.0", self.port, 300)
        await self.server.__aenter__()

        self.client = self.server.new_local_client()
        url = self.client.get_qrcode(f"ws://{self.host}:{self.port}")

        # 生成二维码
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save("dgcode.png")

        print("[联动] 请用 DG-Lab App 扫描二维码连接")
        print("[联动] 地址:", url)

        # 等待连接
        for i in range(60):
            await asyncio.sleep(1)
            if self.server.uuid_to_ws:
                self.target_id = list(self.server.uuid_to_ws.keys())[0]
                print(f"[联动] ✅ 已连接: {self.target_id}")
                return True
            if i % 10 == 0:
                print(f"[联动] 等待连接... {i}s")

        print("[联动] 连接超时")
        return False

    def set_intensity(self, channel: str, intensity: int):
        """
        设置震动强度

        Args:
            channel: 'A' 或 'B'
            intensity: 0-100
        """
        if self.client:
            self.client.set_intensity(channel, intensity)
            print(f"[控制] 通道{channel}: {intensity}%")

    def increase(self, channel: str, amount: int = 10):
        """增加强度"""
        if self.client:
            self.client.increase_intensity(channel, amount)
            print(f"[控制] 通道{channel} +{amount}%")

    def decrease(self, channel: str, amount: int = 10):
        """减少强度"""
        if self.client:
            self.client.decrease_intensity(channel, amount)
            print(f"[控制] 通道{channel} -{amount}%")

    def clear(self, channel: str):
        """清空震动"""
        if self.client:
            self.client.clear(channel)
            print(f"[控制] 通道{channel} 清空")

    async def listen(self, callback):
        """监听App数据并触发回调"""
        async for data in self.client.data_generator():
            # 获取当前强度
            a = getattr(data, 'channel_a', None)
            b = getattr(data, 'channel_b', None)
            print(f"[监听] A:{a} B:{b}")

            # 调用回调函数
            if callback:
                callback(data)


# ==========================================
# 示例游戏事件处理函数
# ==========================================

def on_shoot():
    """射击时触发 - 单次震动"""
    print("💥 射击!")
    gl.set_intensity('A', 80)
    gl.set_intensity('B', 80)

def on_hit():
    """命中时触发 - 强力震动"""
    print("💢 命中!")
    gl.set_intensity('A', 100)
    gl.set_intensity('B', 100)

def on_game_over():
    """游戏结束"""
    print("💀 游戏结束")
    gl.clear('A')
    gl.clear('B')


# ==========================================
# 使用示例
# ==========================================

if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.10.104"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5678

    gl = GameLink(host, port)

    async def main():
        # 启动并等待连接
        if not await gl.start():
            return

        print("\n" + "=" * 40)
        print("🎮 游戏联动已就绪")
        print("=" * 40)
        print("测试命令:")
        print("  on_shoot()    - 射击震动")
        print("  on_hit()     - 命中震动")
        print("  on_game_over() - 游戏结束")
        print("=" * 40)

        # 示例：监听时模拟游戏事件
        # 你可以把这些函数绑定到游戏的按键事件上

        # 保持运行
        try:
            while True:
                await asyncio.sleep(10)
                print("[运行中] 等待游戏事件...")
        except KeyboardInterrupt:
            print("\n[退出] 关闭服务")
            gl.clear('A')
            gl.clear('B')

    asyncio.run(main())