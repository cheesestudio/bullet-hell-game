# Bullet Hell

赛博朋克弹幕射击游戏 | 支持 Radmin 1~4 人联机 | 支持 DG-LAB 郊狼脉冲反馈

✅ 在线玩: https://cheesestudio.github.io/bullet-hell.html

> ⚠️ 在线版本不包含DG-Lab联动功能，下载完整包才能获得完整体验！

---

## 🎮 操作
| 按键 | 功能 |
|------|------|
| 方向键 ↑ ↓ ← → | 移动 |
| 空格 | 炸弹 清屏 |
| ESC | 暂停 / 设置 |

✅ 自动射击，不需要按空格射击
✅ 已移除 R 重新开始、Shift减速、B炸弹按键

---

## 👥 Radmin 联机
**零配置，不需要端口映射**

```bash
# 主机只需要运行这两行
npm install ws
node relay.js
```

运行成功后其他人输入主机 Radmin IP 即可连接，最多4人。

---

## 🐺 DG-Lab 联动（需要启动服务）

### 一键启动
```
双击 DGGameLink.exe
```

会自动：
1. 检测局域网IP
2. 启动DG-Lab服务（端口5678）
3. 启动游戏WebSocket服务（端口5679）
4. 启动HTTP服务并打开游戏
5. 生成连接二维码

### 连接步骤
1. 扫描 [dgcode.png](dgcode.png) 连接DG-Lab App
2. 在浏览器打开 http://192.168.10.104:8888/bullet-hell.html
3. 开始游戏，受伤时双通道会收到波形

### 震动事件
| 事件 | 震动 |
|------|------|
| 玩家受击 | A+B双通道波形 |
| 击中Boss | 轻微震动 |
| Boss死亡 | 强力震动 |

---

## 🔧 本地运行（不含DG-Lab联动）
直接浏览器打开 `bullet-hell.html` 即可游玩，不需要服务器。
