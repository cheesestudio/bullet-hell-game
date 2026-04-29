# PHANTOM BOSS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 添加第4个BOSS PHANTOM到弹幕游戏，包含3个形态、5个特殊能力、新弹幕模式和屏幕旋转效果

**Architecture:** 在现有bullet-hell.html中添加PHANTOM配置和新函数，保持单文件结构

**Tech Stack:** HTML5 Canvas + Vanilla JavaScript

---

## File Structure

| 文件 | 修改内容 |
|------|---------|
| bullet-hell.html | 添加PHANTOM的BOSS配置、新弹幕模式、能力函数、渲染逻辑 |

---

### Task 1: 添加PHANTOM到BOSS配置

**Files:**
- Modify: `bullet-hell.html:890-930`

- [ ] **Step 1: 添加PHANTOM到BOSS_PHASES**

在BOSS_PHASES数组末尾添加：
```javascript
// PHANTOM - Phase 1
{ name: 'PHANTOM', hp: 150, color: '#8844ff', pattern: 'phantom_trail' },
// PHANTOM - Phase 2  
{ name: 'PHANTOM', hp: 200, color: '#8844ff', pattern: 'encircle' },
// PHANTOM - Phase 3
{ name: 'PHANTOM', hp: 300, color: '#8844ff', pattern: 'spiral' }
```

- [ ] **Step 2: 添加新弹幕模式到BOSS_PATTERNS**

在BOSS_PATTERNS数组中添加：
```javascript
'phantom_trail', 'encircle', 'spiral'
```

- [ ] **Step 3: 添加PHANTOM能力配置**

在BOSS_ABILITIES对象中添加：
```javascript
GHOST_DASH: { cooldown: 15, triggerHp: 0.8, name: 'GHOST_DASH' },
SHADOW_REALM: { cooldown: 25, triggerHp: 0.7, name: 'SHADOW_REALM' },
PHANTOM_TRAIL: { cooldown: 20, triggerHp: 0.5, name: 'PHANTOM_TRAIL' },
PHASE_SPLIT: { cooldown: 30, triggerHp: 0.4, name: 'PHASE_SPLIT' },
SCREEN_ROTATE: { cooldown: 25, triggerHp: 0.3, name: 'SCREEN_ROTATE' }
```

---

### Task 2: 添加屏幕旋转功能

**Files:**
- Modify: `bullet-hell.html` (在全局变量区添加)

- [ ] **Step 1: 添加屏幕旋转全局变量**

在文件顶部变量区添加：
```javascript
let screenRotation = 0;
let screenRotationTarget = 0;
let screenRotationActive = false;
const screenRotationSpeed = 60; // 每秒旋转60度
```

- [ ] **Step 2: 添加updateScreenRotation函数**

在游戏循环函数区域添加：
```javascript
function updateScreenRotation(dt) {
  if (screenRotationActive) {
    if (screenRotation < 360) {
      screenRotation += screenRotationSpeed * dt;
      if (screenRotation >= 360) {
        screenRotation = 360;
        screenRotationTarget = 0;
      }
    } else if (screenRotationTarget === 0 && screenRotation > 0) {
      screenRotation -= screenRotationSpeed * dt;
      if (screenRotation < 0) screenRotation = 0;
    }
    if (screenRotation === 0) screenRotationActive = false;
  }
}
```

- [ ] **Step 3: 在gameLoop中调用更新函数**

在gameLoop的update部分添加：
```javascript
case STATE.PLAYING: 
  update(clampedDt);
  updateScreenRotation(clampedDt);
  network.tick++;
  break;
```

- [ ] **Step 4: 在render函数中应用旋转**

在render函数开头添加画布旋转：
```javascript
function render() {
  ctx.save();
  if (screenRotation > 0) {
    ctx.translate(canvas.width/2, canvas.height/2);
    ctx.rotate(screenRotation * Math.PI / 180);
    ctx.translate(-canvas.width/2, -canvas.height/2);
  }
  // ... 原有的render代码
  ctx.restore();
}
```

- [ ] **Step 5: 在render结束前恢复旋转**

在ctx.restore()之前添加：
```javascript
if (screenRotation > 0) {
  ctx.translate(canvas.width/2, canvas.height/2);
  ctx.rotate(-screenRotation * Math.PI / 180);
  ctx.translate(-canvas.width/2, -canvas.height/2);
}
```

---

### Task 3: 添加triggerScreenRotate函数

**Files:**
- Modify: `bullet-hell.html` (在triggerPhantomTank函数附近)

- [ ] **Step 1: 添加triggerScreenRotate函数**

```javascript
function triggerScreenRotate() {
  if (screenRotationActive) return;
  screenRotationActive = true;
  screenRotation = 0;
  screenRotationTarget = 360;
  triggerScreenShake(5, 0.3);
}
```

- [ ] **Step 2: 在checkBossAbilities中添加触发逻辑**

在BOSS能力检查函数中添加：
```javascript
if (hpPercent < 0.3 && boss.abilityCooldowns.SCREEN_ROTATE <= 0) {
  triggerScreenRotate();
  boss.abilityCooldowns.SCREEN_ROTATE = BOSS_ABILITIES.SCREEN_ROTATE.cooldown;
}
```

---

### Task 4: 实现新弹幕模式

**Files:**
- Modify: `bullet-hell.html` (在fireBossPattern函数中添加)

- [ ] **Step 1: phantom_trail模式 (Phase 1)**

在fireBossPattern函数中添加：
```javascript
else if (pattern === 'phantom_trail') {
  // 3发一组的追踪弹
  for (let i = 0; i < 3; i++) {
    const angle = Math.atan2(player.y - boss.y, player.x - boss.x) + (i - 1) * 0.15;
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: Math.cos(angle) * 80,
      vy: Math.sin(angle) * 80,
      r: 5,
      owner: 'boss',
      color: '#8844ff',
      alpha: 0.6,
      tracking: true
    });
  }
}
```

- [ ] **Step 2: encircle模式 (Phase 2)**

```javascript
else if (pattern === 'encircle') {
  // 环形包围弹幕
  for (let i = 0; i < 16; i++) {
    const angle = (i / 16) * Math.PI * 2;
    bullets.push({
      x: boss.x + Math.cos(angle) * 50,
      y: boss.y + Math.sin(angle) * 50,
      vx: Math.cos(angle) * 100,
      vy: Math.sin(angle) * 100,
      r: 5,
      owner: 'boss',
      color: '#8844ff'
    });
  }
}
```

- [ ] **Step 3: spiral模式 (Phase 3)**

```javascript
else if (pattern === 'spiral') {
  // 螺旋聚集 - 从四角向中心
  const corners = [
    {x: -20, y: -20},
    {x: canvas.width + 20, y: -20},
    {x: canvas.width + 20, y: canvas.height + 20},
    {x: -20, y: canvas.height + 20}
  ];
  const i = Math.floor(Date.now() / 100) % 4;
  const corner = corners[i];
  for (let j = 0; j < 3; j++) {
    const angle = Date.now() / 300 + j;
    const targetX = boss.x + Math.cos(angle) * 20;
    const targetY = boss.y + Math.sin(angle) * 20;
    bullets.push({
      x: corner.x,
      y: corner.y,
      vx: (targetX - corner.x) * 2,
      vy: (targetY - corner.y) * 2,
      r: 4,
      owner: 'boss',
      color: '#aa66ff'
    });
  }
}
```

---

### Task 5: 添加虚影重重能力

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加shadowRealms数组**

```javascript
const shadowRealms = [];
```

- [ ] **Step 2: 添加triggerShadowRealm函数**

```javascript
function triggerShadowRealm() {
  if (shadowRealms.length >= 3) return;
  // 创建3个虚影
  for (let i = 0; i < 3; i++) {
    shadowRealms.push({
      x: boss.x + (Math.random() - 0.5) * 100,
      y: boss.y + (Math.random() - 0.5) * 50,
      life: 5,
      maxLife: 5
    });
  }
}
```

- [ ] **Step 3: 添加renderShadowRealms函数**

```javascript
function renderShadowRealms() {
  for (const s of shadowRealms) {
    ctx.save();
    ctx.globalAlpha = 0.4 * (s.life / s.maxLife);
    ctx.shadowBlur = 20;
    ctx.shadowColor = boss.color;
    ctx.fillStyle = boss.color;
    ctx.beginPath();
    ctx.arc(s.x, s.y, boss.r * 0.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}
```

- [ ] **Step 4: 在updateBoss中添加虚影更新**

```javascript
for (let i = shadowRealms.length - 1; i >= 0; i--) {
  shadowRealms[i].life -= dt;
  if (shadowRealms[i].life <= 0) shadowRealms.splice(i, 1);
}
```

- [ ] **Step 5: 在checkBossAbilities中添加触发**

```javascript
if (hpPercent < 0.7 && boss.abilityCooldowns.SHADOW_REALM <= 0) {
  triggerShadowRealm();
  boss.abilityCooldowns.SHADOW_REALM = BOSS_ABILITIES.SHADOW_REALM.cooldown;
}
```

---

### Task 6: 添加幽魂冲刺能力

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加triggerGhostDash函数**

```javascript
function triggerGhostDash() {
  boss.x = player.x + (Math.random() - 0.5) * 100;
  boss.y = Math.min(player.y + 50, canvas.height - 100);
  triggerScreenShake(3, 0.1);
}
```

- [ ] **Step 2: 在checkBossAbilities中添加触发**

```javascript
if (hpPercent < 0.8 && boss.abilityCooldowns.GHOST_DASH <= 0) {
  triggerGhostDash();
  boss.abilityCooldowns.GHOST_DASH = BOSS_ABILITIES.GHOST_DASH.cooldown;
}
```

---

### Task 7: 添加鬼影追踪能力

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 鬼影追踪在phantom_trail模式中已包含**
（此能力通过弹幕模式实现，无需额外函数）

---

### Task 8: 添加分身能力

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加phaseSplits数组**

```javascript
const phaseSplits = [];
```

- [ ] **Step 2: 添加triggerPhaseSplit函数**

```javascript
function triggerPhaseSplit() {
  if (phaseSplits.length >= 3) return;
  clearAllTimers();
  // 创建3个分身
  for (let i = 0; i < 3; i++) {
    phaseSplits.push({
      x: boss.x + (i - 1) * 80,
      y: boss.y,
      targetX: boss.x + (i - 1) * 100,
      life: 6,
      maxLife: 6,
      color: boss.color
    });
  }
  safeTimeout(() => {
    phaseSplits.length = 0;
  }, 6000);
}
```

- [ ] **Step 3: 添加renderPhaseSplits函数**

```javascript
function renderPhaseSplits() {
  for (const p of phaseSplits) {
    ctx.save();
    ctx.globalAlpha = 0.7 * (p.life / p.maxLife);
    ctx.shadowBlur = 15;
    ctx.shadowColor = p.color;
    ctx.fillStyle = p.color;
    // 绘制分身形状
    ctx.beginPath();
    const sides = 5 + Math.floor(Date.now() / 500) % 3;
    for (let i = 0; i < sides; i++) {
      const angle = (i / sides) * Math.PI * 2 - Math.PI / 2;
      const px = p.x + Math.cos(angle) * boss.r;
      const py = p.y + Math.sin(angle) * boss.r;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
}
```

- [ ] **Step 4: 在checkBossAbilities中添加触发**

```javascript
if (hpPercent < 0.4 && boss.abilityCooldowns.PHASE_SPLIT <= 0) {
  triggerPhaseSplit();
  boss.abilityCooldowns.PHASE_SPLIT = BOSS_ABILITIES.PHASE_SPLIT.cooldown;
}
```

---

### Task 9: Phase 3额外掉落

**Files:**
- Modify: `bullet-hell.html` (在checkBossHit函数中)

- [ ] **Step 1: 修改掉落逻辑**

在BOSS击败检测处修改：
```javascript
if (boss.hp <= 0) {
  // 基础掉落
  for (let i = 0; i < 2; i++) {
    spawnPowerup(boss.x + (Math.random()-0.5)*50, boss.y, {name: 'POWER', color: '#ff0066'});
  }
  // Phase 3额外掉落
  if (boss.phase === 2) { // Phase 3
    for (let i = 0; i < 2; i++) {
      spawnPowerup(boss.x + (Math.random()-0.5)*80, boss.y, {name: 'POWER', color: '#ff0066'});
    }
  }
  // ... 后续代码
}
```

---

### Task 10: 渲染PHANTOM视觉效果

**Files:**
- Modify: `bullet-hell.html` (在renderBoss函数后添加)

- [ ] **Step 1: 添加renderBossPhantom函数**

根据Phase显示不同视觉效果：
```javascript
function renderBossPhantom(time, phase) {
  ctx.save();
  ctx.shadowBlur = 25;
  ctx.shadowColor = boss.color;
  
  if (phase === 0) {
    // Phase 1: 半透明幽灵轮廓
    ctx.globalAlpha = 0.6;
    ctx.fillStyle = boss.color;
    ctx.beginPath();
    // 飘忽的鬼魂形状
    const flicker = Math.sin(time * 5) * 3;
    ctx.arc(boss.x, boss.y, boss.r + flicker, 0, Math.PI * 2);
    ctx.fill();
  } else if (phase === 1) {
    // Phase 2: 分裂效果在renderPhaseSplits中处理
    ctx.globalAlpha = 0.8;
  } else {
    // Phase 3: 巨大鬼魂形态
    ctx.globalAlpha = 0.7;
    ctx.fillStyle = boss.color;
    ctx.beginPath();
    // 更大的鬼魂形态
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2 + time * 2;
      const r = boss.r * 1.5 + Math.sin(angle * 2) * 10;
      const px = boss.x + Math.cos(angle) * r;
      const py = boss.y + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();
}
```

---

### Task 11: 测试与调试

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 将新渲染函数加入render循环**

在render函数的BOSS渲染部分添加调用：
```javascript
if (boss.active) {
  renderBoss();
  renderBossAbilities();
  if (boss.name === 'PHANTOM') {
    renderBossPhantom(time, boss.phase);
    renderShadowRealms();
    renderPhaseSplits();
  }
}
```

- [ ] **Step 2: 本地测试**

- 打开浏览器访问 `bullet-hell.html`
- 开始游戏，确认PHANTOM作为第4个BOSS出现
- 测试3个形态的弹幕模式
- 测试屏幕旋转效果
- 测试掉落物数量

---

## 实现顺序

1. Task 1: 添加配置
2. Task 2: 屏幕旋转基础
3. Task 3: 旋转触发
4. Task 4: 弹幕模式
5. Task 5: 虚影能力
6. Task 6: 幽魂冲刺
7. Task 7: 鬼影追踪（已包含）
8. Task 8: 分身能力
9. Task 9: 额外掉落
10. Task 10: 视觉效果
11. Task 11: 测试

---

## Acceptance Criteria 验证清单

- [ ] PHANTOM作为第4个BOSS出现
- [ ] 3个形态都有独特视觉
- [ ] phantom_trail弹幕模式正常
- [ ] encircle弹幕模式正常
- [ ] spiral弹幕模式正常
- [ ] 幽魂冲刺能力正常
- [ ] 虚影重重能力正常
- [ ] 鬼影追踪能力正常
- [ ] 分身能力正常
- [ ] 旋转屏幕360°正常
- [ ] Phase 3额外掉落
- [ ] 60 FPS性能