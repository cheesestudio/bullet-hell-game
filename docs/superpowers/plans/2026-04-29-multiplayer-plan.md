# Multiplayer Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强游戏多人联机功能，包括双人同屏双打和网络对战连接入口

**Architecture:** 在现有bullet-hell.html中添加菜单选项和双人模式处理

**Tech Stack:** HTML5 Canvas + Vanilla JavaScript + WebSocket

---

## File Structure

| 文件 | 修改内容 |
|------|---------|
| bullet-hell.html | 添加双人对战菜单、处理、渲染 |
| relay.js | 保持现有功能（可选增强） |

---

### Task 1: 主菜单添加选项

**Files:**
- Modify: `bullet-hell.html` (renderMenu函数)

- [ ] **Step 1: 添加gameMode和STATE**

在文件顶部变量区添加：
```javascript
let gameMode = 'single'; // 'single' | 'coop' | 'network'
let networkRole = 'offline'; // 'host' | 'client' | 'offline'
const STATE = { MENU: 0, PLAYING: 1, TRANSITION: 2, GAMEOVER: 3, PAUSED: 4, SETTINGS: 5, LOBBY: 6, NETWORK: 7 };
```

- [ ] **Step 2: 添加菜单选项变量**

```javascript
let menuOptions = ['单人游戏', '双人同屏', '网络对战'];
let menuSelection = 0;
```

- [ ] **Step 3: 修改renderMenu渲染选项**

在现有菜单渲染代码后添加：
```javascript
// Menu options
ctx.font = '14px "Courier New", monospace';
for (let i = 0; i < menuOptions.length; i++) {
  ctx.fillStyle = i === menuSelection ? '#00ffff' : '#666666';
  ctx.textAlign = 'center';
  const label = menuOptions[i];
  ctx.fillText(label, canvas.width / 2, 280 + i * 30);
}
```

- [ ] **Step 4: 修改updateMenu检测选择**

```javascript
function updateMenu(dt) {
  if (keys['ArrowUp'] && !keys['ArrowUp_pressed']) {
    keys['ArrowUp_pressed'] = true;
    menuSelection = (menuSelection - 1 + menuOptions.length) % menuOptions.length;
  }
  if (keys['ArrowDown'] && !keys['ArrowDown_pressed']) {
    keys['ArrowDown_pressed'] = true;
    menuSelection = (menuSelection + 1) % menuOptions.length;
  }
  if ((keys['Enter'] || keys[' ']) && !keys['Enter_pressed']) {
    keys['Enter_pressed'] = true;
    // 根据menuSelection执行
  }
}
```

- [ ] **Step 5: 根据选择设置gameMode**

```javascript
if (menuSelection === 0) { // 单人游戏
  gameMode = 'single';
  startGame();
} else if (menuSelection === 1) { // 双人同屏
  gameMode = 'coop';
  startGame();
} else if (menuSelection === 2) { // 网络对战
  gameMode = 'network';
  gameState = STATE.LOBBY;
}
```

---

### Task 2: 双人同屏模式

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 修改player对象为数组**

```javascript
const players = [
  {
    x: canvas.width / 2,
    y: canvas.height - 80,
    r: 8,
    speed: 250,
    lives: 3,
    power: 0,
    maxPower: 4,
    score: 0,
    invincible: 0,
    shootCooldown: 0,
    bombReady: true,
    bombCooldown: 0
  },
  // Player 2 (初始隐藏)
  {
    x: canvas.width / 2,
    y: canvas.height - 80,
    r: 8,
    speed: 250,
    lives: 3,
    power: 0,
    maxPower: 4,
    score: 0,
    invincible: 0,
    shootCooldown: 0,
    bombReady: true,
    bombCooldown: 0,
    active: false
  }
];
```

- [ ] **Step 2: 检测玩家2键盘输入**

在updatePlayer函数开头添加：
```javascript
function updatePlayer(dt) {
  // Player 1 - WASD
  const p1 = players[0];
  if (isDown('ArrowLeft') || isDown('a')) p1.x -= p1.speed * dt;
  if (isDown('ArrowRight') || isDown('d')) p1.x += p1.speed * dt;
  if (isDown('ArrowUp') || isDown('w')) p1.y -= p1.speed * dt;
  if (isDown('ArrowDown') || isDown('s')) p1.y += p1.speed * dt;
  
  // 边界限制
  p1.x = Math.max(p1.r, Math.min(canvas.width - p1.r, p1.x));
  p1.y = Math.max(p1.r, Math.min(canvas.height - p1.r, p1.y));
  
  // 自动射击
  p1.shootCooldown -= dt;
  if (p1.shootCooldown <= 0) {
    shootBullet(p1.x, p1.y - 10, -400, 'player');
    p1.shootCooldown = 0.15;
  }
  
  // 双人模式 - Player 2 (方向键)
  if (gameMode === 'coop' && players[1].active) {
    const p2 = players[1];
    if (isDown('ArrowLeft')) p2.x -= p2.speed * dt;
    if (isDown('ArrowRight')) p2.x += p2.speed * dt;
    if (isDown('ArrowUp')) p2.y -= p2.speed * dt;
    if (isDown('ArrowDown')) p2.y += p2.speed * dt;
    
    p2.x = Math.max(p2.r, Math.min(canvas.width - p2.r, p2.x));
    p2.y = Math.max(p2.r, Math.min(canvas.height - p2.r, p2.y));
    
    p2.shootCooldown -= dt;
    if (p2.shootCooldown <= 0) {
      shootBullet(p2.x, p2.y - 10, -400, 'player');
      p2.shootCooldown = 0.15;
    }
  }
  // ...
}
```

- [ ] **Step 3: 修改渲染两个玩家**

```javascript
function renderPlayer() {
  for (const p of players) {
    if (p.invincible > 0 && Math.floor(p.invincible * 10) % 2 === 0) continue;
    
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#00ffff';
    
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.moveTo(0, -p.r * 2);
    ctx.lineTo(-p.r, p.r);
    ctx.lineTo(p.r, p.r);
    ctx.closePath();
    ctx.fill();
    
    ctx.restore();
  }
}
```

- [ ] **Step 4: 激活玩家的处理**

在游戏开始时：
```javascript
function startGame() {
  if (gameMode === 'coop') {
    players[1].active = true;
    players[1].x = canvas.width / 2 + 30;
  }
  // ...
}
```

- [ ] **Step 5: 敌人分配逻辑**

修改弹幕生成，敌人根据区域生成：
```javascript
// 在fireBossPattern中根据玩家区域生成
if (gameMode === 'coop' && players[1].active) {
  // 上半部分敌人攻击players[0]
  // 下半部分敌人攻击players[1]
}
```

---

### Task 3: 生命值显示

**Files:**
- Modify: `bullet-hell.html` (renderUI函数)

- [ ] **Step 1: 双人生命显示**

```javascript
function renderUI() {
  // Player 1 lives (左上)
  for (let i = 0; i < players[0].lives; i++) {
    ctx.fillStyle = '#ff4444';
    ctx.fillText('❤', 20 + i * 20, 30);
  }
  
  // Player 2 lives (右上，仅双人模式显示)
  if (gameMode === 'coop' && players[1].active) {
    for (let i = 0; i < players[1].lives; i++) {
      ctx.fillStyle = '#ff8800';
      ctx.fillText('❤', canvas.width - 20 - i * 20, 30);
    }
  }
}
```

---

### Task 4: 网络对战大厅

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加NETWORK状态处理**

```javascript
function updateNetwork(dt) {
  // 显示等待连接界面
}

function renderNetwork() {
  ctx.fillStyle = '#00ffff';
  ctx.font = '24px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('网络对战', canvas.width / 2, 100);
  
  ctx.font = '14px monospace';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('选择模式:', canvas.width / 2, 180);
  
  // Host / Client 选项
  ctx.textAlign = 'center';
  ctx.fillText('[1] 创建主机', canvas.width / 2, 250);
  ctx.fillText('[2] 加入游戏', canvas.width / 2, 300);
  
  ctx.fillStyle = '#888888';
  ctx.fillText('[ESC] 返回', canvas.width / 2, 400);
}
```

- [ ] **Step 2: 添加网络连接逻辑**

```javascript
// 显示本机IP地址（通过WebSocket或UDP获取）
function getLocalIP() {
  // 尝试通过连接获取
  return '192.168.x.x';
}

// 显示房间代码
function generateRoomCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}
```

- [ ] **Step 3: 连接输入UI**

```javascript
let connectingIP = '';
function renderConnectInput() {
  ctx.fillStyle = '#000000';
  ctx.fillRect(canvas.width/2 - 150, canvas.height/2 - 30, 300, 60);
  ctx.strokeStyle = '#00ffff';
  ctx.strokeRect(canvas.width/2 - 150, canvas.height/2 - 30, 300, 60);
  
  ctx.fillStyle = '#ffffff';
  ctx.font = '16px monospace';
  ctx.fillText('输入主机IP: ' + connectingIP, canvas.width/2, canvas.height/2 + 5);
}
```

- [ ] **Step 4: WebSocket连接（可选简化版）**

如果relay.js已运行，直接提示用户运行命令。

```javascript
function renderHostWaiting() {
  ctx.fillStyle = '#00ffff';
  ctx.font = '20px monospace';
  ctx.fillText('等待连接...', canvas.width/2, 200);
  
  ctx.font = '14px monospace';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('请运行以下命令启动主机:', canvas.width/2, 280);
  
  ctx.font = '12px monospace';
  ctx.fillStyle = '#888888';
  ctx.fillText('node relay.js', canvas.width/2, 320);
  
  // 显示本机IP
  ctx.fillStyle = '#ffff00';
  ctx.fillText('IP: ' + getLocalIP(), canvas.width/2, 380);
}
```

---

### Task 5: 测试与调试

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 本地测试**

1. 打开游戏，确认主菜单显示3个选项
2. 选择"双人同屏"，测试双键盘控制
3. 验证两个玩家都能移动和射击
4. 选择"网络对战"，验证菜单显示

- [ ] **Step 2: 验证现有功能未破坏**

确保单人游戏仍然正常工作

---

## 实现顺序

1. Task 1: 主菜单添加选项
2. Task 2: 双人同屏模式
3. Task 3: 生命值显示
4. Task 4: 网络对战大厅
5. Task 5: 测试与调试

---

## Acceptance Criteria 验证清单

- [ ] 主菜单显示3个选项（单人游戏/双人同屏/网络对战）
- [ ] 可以用方向键选择菜单选项
- [ ] 回车键确认选择
- [ ] 双人同屏模式启动
- [ ] 玩家1用WASD控制
- [ ] 玩家2用方向键控制
- [ ] 两个玩家都能射击
- [ ] 各自生命值独立显示
- [ ] 网络对战菜单显示
- [ ] 60 FPS性能保持