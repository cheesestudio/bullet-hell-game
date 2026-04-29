# Multiplayer Enhancement Design

**Date**: 2026-04-29
**Project**: Bullet Hell Boss Rush - Multiplayer Enhancement
**Status**: Design approved

---

## Overview

增强游戏的多人联机功能，包括双人同屏双打和网络对战支持。

---

## UI Structure

### Main Menu

```
┌─────────────────┐
│   BULLET HELL   │
│   BOSS RUSH     │
│                │
│  [单人游戏]      │ → 开始游戏
│  [双人同屏]     │ → 2人键盘双打
│  [网络对战]     │ → 主机/客户端选择
│                │
│ HIGH SCORE: xxx │
└─────────────────┘
```

### Network Lobby

```
┌─────────────────┐
│   网络对战      │
│                │
│ [创建主机]     │ → 显示本机IP/房间码
│ [加入游戏]     │ → 输入IP/房间码
│                │
│ [返回]         │
└─────────────────┘
```

### Settings → Network

```
┌─────────────────┐
│   设置         │
│ ...            │
│ [连接]        │ → 输入IP连接
│                │
└─────────────────┘
```

---

## Implementation

### 1. 双人同屏模式

**Controls:**
- Player 1: WASD + 自动射击
- Player 2: 方向键 + 自动射击

**Enemy Distribution:**
- Player 1: 左侧敌人 / 屏幕上半部分
- Player 2: 右侧敌人 / 屏幕下半部分

**Separate State:**
```javascript
const players = [
  { x, y, lives, power, score, invincible, ... },
  { x, y, lives, power, score, invincible, ... }
];
```

**Rendering:**
- 屏幕分为两个区域
- 各自的生命显示
- 独立的得分统计

---

### 2. 网络对战模式 (Radmin)

**Host:**
```javascript
// 显示本机IP地址
const hostIP = getLocalIP(); // 或从relay.js获取
// 显示房间代码
const roomCode = Math.random().toString(36).substring(2, 8).toUpperCase();
```

**Join:**
```javascript
// 输入框
const inputIP = prompt('输入主机IP:'); // 或房间码
```

**Connection Flow:**
```
[创建主机]
  ↓
启动 relay.js (或内置WebSocket)
  ↓
显示 IP + 房间码
  ↓
等待连接

[加入游戏]
  ↓
输入 IP/房间码
  ↓
连接主机
  ↓
同步游戏状态
```

---

## Technical Implementation

### Changes to bullet-hell.html

1. **主菜单增加选项**
```javascript
function renderMenu() {
  // ...
  // [单人游戏] - 开始单机
  // [双人同屏] - 2人模式
  // [网络对战] - 联机模式
}
```

2. **STATE增加模式**
```javascript
const STATE = {
  MENU: 0,
  PLAYING: 1,
  TRANSITION: 2,
  GAMEOVER: 3,
  PAUSED: 4,
  SETTINGS: 5,
  LOBBY: 6,
  NETWORK: 7    // 新增
};
```

3. **双人模式选择**
```javascript
let gameMode = 'single'; // 'single' | 'coop' | 'network'
let player2Active = false;

// 检测玩家2键盘
function detectPlayer2() {
  if (keys['ArrowUp'] || keys['ArrowDown'] || 
      keys['ArrowLeft'] || keys['ArrowRight']) {
    player2Active = true;
  }
}
```

4. **网络连接UI**
```javascript
// 显示本机IP
function getLocalIP() {
  // 通过WebSocket连接获取
}
```

---

## File Changes

| File | Change |
|------|--------|
| bullet-hell.html | 添加菜单选项、处理函数、渲染 |
| relay.js | 保持现有功能 |

---

## Acceptance Criteria

- [ ] 主菜单显示3个选项
- [ ] 双人同屏模式正常游戏
- [ ] 玩家1用WASD，玩家2用方向键
- [ ] 敌���分开攻击两个玩家
- [ ] 网络对战显示本机IP
- [ ] 网络对战可输入IP连接
- [ ] 连接状态显示
- [ ] 60 FPS性能保持

---

## Difficulty Design

**双人同屏难度：**
- 敌人分开攻击各自区域
- 伤害不叠加
- 各自独立生命

**网络对战难度：**
- 同步所有状态到客户端
- 延迟补偿（如需要）