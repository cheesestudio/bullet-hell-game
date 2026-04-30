# 武器切换系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 玩家每击杀5个BOSS自动切换下一把武器，共10把独特武器，全部自动攻击无需按键

**Architecture:** 在现有 bullet-hell.html 中扩展，新增武器状态管理、切换逻辑、各武器独立发射函数

**Tech Stack:** 纯JavaScript + Canvas，无外部依赖

---

## 文件结构

- Modify: `bullet-hell.html` - 主游戏文件，添加武器系统

---

### Task 1: 添加武器系统全局变量

**Files:**
- Modify: `bullet-hell.html:45-60` (在现有变量声明区域后添加)

- [ ] **Step 1: 添加武器系统变量**

在 `let menuPhase = 'title'` 后（约第45行）添加：

```javascript
// ==================== Weapon System ====================
const WEAPON_COUNT = 10;
const KILLS_PER_WEAPON = 5;
let currentWeapon = 0;
let killCount = 0;
let weaponSwitchTimer = 0;
const WEAPON_SWITCH_DISPLAY_TIME = 1.5;

// Weapon name list
const WEAPON_NAMES = [
  '散弹三连', '追踪火箭', '回旋镖', '能量脉冲', '螺旋弹幕',
  '闪电环', '波动炮', '冰晶刺', '黑洞弹', '时间钟摆'
];

// Weapon cooldowns (seconds)
const WEAPON_CDS = [
  0,      // 散弹三连 - 无CD
  2,       // 追踪火箭
  1.5,     // 回旋镖
  2,        // 能量脉冲
  0,        // 螺旋弹幕 - 无CD
  3,        // 闪电环
  4,        // 波动炮
  2,        // 冰晶刺
  3,        // 黑洞弹
  2         // 时间钟摆
];

// Last fire time for each weapon
let lastWeaponFire = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
```

- [ ] **Step 2: 保存并继续**

---

### Task 2: 添加武器切换逻辑

**Files:**
- Modify: `bullet-hell.html` 在游戏状态更新函数中添加切换检测

- [ ] **Step 1: 在游戏主循环中找到死亡检测位置**

搜索 `boss.hp <= 0` 或 `if (boss.hp <= 0` 模式，约在3200-3500行附近

- [ ] **Step 2: 添加武器切换触发代码**

在BOSS死亡后将 `killCount++`，添加：

```javascript
// Weapon switching - after boss death
if (boss.hp <= 0 && !boss.dead) {
  boss.dead = true;
  killCount++;
  if (killCount >= KILLS_PER_WEAPON) {
    killCount = 0;
    currentWeapon = (currentWeapon + 1) % WEAPON_COUNT;
    weaponSwitchTimer = WEAPON_SWITCH_DISPLAY_TIME;
    // Reset all weapon cooldowns
    for (let i = 0; i < WEAPON_COUNT; i++) {
      lastWeaponFire[i] = 0;
    }
  }
}
```

- [ ] **Step 3: 保存并继续**

---

### Task 3: 添加武器切换动画效果

**Files:**
- Modify: `bullet-hell.html` 在绘制UI函数中添加切换提示

- [ ] **Step 1: 在 HUD 绘制函数中添加切换动画**

找到 `function drawHUD()` 或绘制UI的函数位置（约2900行），在函数开始处添加：

```javascript
// Weapon switch animation
if (weaponSwitchTimer > 0) {
  const alpha = Math.min(1, weaponSwitchTimer / 0.3);
  // Flash effect
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.3})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Weapon name display
  ctx.save();
  ctx.font = 'bold 48px "Courier New"';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const scale = 1 + (weaponSwitchTimer > WEAPON_SWITCH_DISPLAY_TIME - 0.3 ? 
    (WEAPON_SWITCH_DISPLAY_TIME - weaponSwitchTimer) * 3 : 0);
  
  // Glow effect
  ctx.shadowColor = '#00ffff';
  ctx.shadowBlur = 20;
  ctx.fillStyle = '#00ffff';
  ctx.fillText(WEAPON_NAMES[currentWeapon], canvas.width / 2, canvas.height / 2);
  ctx.restore();
}
```

- [ ] **Step 2: 保存并继续**

---

### Task 4: 修改玩家射击逻辑 - 引入武器系统

**Files:**
- Modify: `bullet-hell.html` 找到玩家射击函数并重写

- [ ] **Step 1: 找到玩家射击函数**

搜索包含 `player.power` 和 `fireRate` 的射击逻辑，约在2700-2900行

- [ ] **Step 2: 替换为武器分发逻辑**

将现有射击代码替换为：

```javascript
// Player shooting - weapon based
if (player.shootCooldown > 0) {
  player.shootCooldown -= dt;
}

// Fire based on current weapon
if (gameState === STATE.PLAYING && player.alive) {
  const now = gameTime;
  const weaponCD = WEAPON_CDS[currentWeapon];
  
  // Continuous fire weapons (no CD)
  if (weaponCD === 0 && player.shootCooldown <= 0) {
    fireWeapon(currentWeapon);
    player.shootCooldown = 0.08;
  }
  // CD-based weapons
  else if (weaponCD > 0 && now - lastWeaponFire[currentWeapon] >= weaponCD) {
    fireWeapon(currentWeapon);
    lastWeaponFire[currentWeapon] = now;
  }
}

function fireWeapon(weaponIndex) {
  const p = player;
  switch(weaponIndex) {
    case 0: fireSpreadShot(p); break;
    case 1: fireHomingRocket(p); break;
    case 2: fireBoomerang(p); break;
    case 3: fireEnergyPulse(p); break;
    case 4: fireSpiralShot(p); break;
    case 5: fireLightningRing(p); break;
    case 6: fireWaveCannon(p); break;
    case 7: fireIceSpike(p); break;
    case 8: fireBlackHole(p); break;
    case 9: fireTimePendulum(p); break;
  }
}
```

- [ ] **Step 3: 保存并继续**

---

### Task 5: 实现武器1 - 散弹三连

**Files:**
- Modify: `bullet-hell.html` 在 fireWeapon 函数后添加

- [ ] **Step 1: 添加散弹三连函数**

```javascript
// Weapon 1: 散弹三连 - 扇形散射
function fireSpreadShot(p) {
  const baseSpeed = -400 - p.power * 30;
  const spreadAngles = p.power >= 2 ? [-30, -15, 0, 15, 30] : [-15, 0, 15];
  const color = p.power >= 2 ? '#00ffff' : '#00aaff';
  
  for (const angle of spreadAngles) {
    const rad = angle * Math.PI / 180;
    bullets.push({
      x: p.x,
      y: p.y - 20,
      vx: Math.sin(rad) * baseSpeed * 0.3,
      vy: Math.cos(rad) * baseSpeed,
      r: 5,
      owner: 'player',
      type: 'spread',
      color: color
    });
  }
}
```

- [ ] **Step 2: 保存并继续**

---

### Task 6: 实现武器2 - 追踪火箭 and 武器3 - 回旋镖

**Files:**
- Modify: `bullet-hell.html` 在散弹函数后添加

- [ ] **Step 1: 添加追踪火箭函数**

```javascript
// Weapon 2: 追踪火箭 - 曲线寻敌
function fireHomingRocket(p) {
  const target = findNearestBoss(p.x, p.y);
  const speed = 250 + p.power * 20;
  let vx = 0, vy = -speed;
  
  if (target) {
    const dx = target.x - p.x;
    const dy = target.y - p.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    vx = (dx / dist) * speed;
    vy = (dy / dist) * speed;
  }
  
  bullets.push({
    x: p.x,
    y: p.y - 20,
    vx: vx,
    vy: vy,
    r: 8,
    owner: 'player',
    type: 'homing',
    color: '#ff4444',
    trail: []
  });
}

// Find nearest boss
function findNearestBoss(x, y) {
  let nearest = null;
  let minDist = Infinity;
  if (boss.active) {
    const dx = boss.x - x;
    const dy = boss.y - y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist < minDist) {
      minDist = dist;
      nearest = boss;
    }
  }
  return nearest;
}
```

- [ ] **Step 2: 添加回旋镖函数**

```javascript
// Weapon 3: 回旋镖 - 绕场一圈
function fireBoomerang(p) {
  bullets.push({
    x: p.x,
    y: p.y - 30,
    vx: -100,
    vy: -150,
    r: 10,
    owner: 'player',
    type: 'boomerang',
    color: '#ffff00',
    phase: 0,      // 0=left-top, 1=center, 2=right-bottom, 3=return
    originX: p.x,
    originY: p.y,
    time: 0,
    duration: 2.0   // 2 seconds for full loop
  });
}
```

- [ ] **Step 3: 在 updateBullets 中添加追踪火箭和回旋镖的更新逻辑**

找到 `function updateBullets(dt)` 添加：

```javascript
// Homing rocket update
if (b.type === 'homing') {
  const target = findNearestBoss(b.x, b.y);
  if (target) {
    const dx = target.x - b.x;
    const dy = target.y - b.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > 0) {
      const turnRate = 3;
      b.vx += (dx / dist * 300 - b.vx) * turnRate * dt;
      b.vy += (dy / dist * 300 - b.vy) * turnRate * dt;
    }
  }
  // Trail
  b.trail.push({ x: b.x, y: b.y, alpha: 1 });
  if (b.trail.length > 10) b.trail.shift();
  for (const t of b.trail) t.alpha -= dt * 3;
}
```

- [ ] **Step 4: 在绘制子弹函数中添加火箭拖尾和回旋镖绘制**

找到绘制子弹位置，添加：

```javascript
// Homing rocket trail
if (b.type === 'homing' && b.trail) {
  for (let i = 0; i < b.trail.length; i++) {
    const t = b.trail[i];
    if (t.alpha <= 0) continue;
    ctx.fillStyle = `rgba(255, 100, 50, ${t.alpha})`;
    ctx.beginPath();
    ctx.arc(t.x, t.y, 3 * (i / b.trail.length), 0, Math.PI * 2);
    ctx.fill();
  }
}

// Boomerang rotation
if (b.type === 'boomerang') {
  b.time += dt;
  const progress = b.time / b.duration;
  if (progress >= 1) {
    bullets.splice(i, 1);
    continue;
  }
  // Figure-8 path
  const t = progress * Math.PI * 2;
  b.x = b.originX + Math.sin(t) * 200;
  b.y = b.originY + Math.sin(t * 2) * 100 - progress * 200;
}
```

- [ ] **Step 5: 保存并继续**

---

### Task 7: 实现武器4 - 能量脉冲 and 武器5 - 螺旋弹幕

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加能量脉冲函数**

```javascript
// Weapon 4: 能量脉冲 - 环形能量波
function fireEnergyPulse(p) {
  const rings = p.power >= 2 ? 3 : 2;
  for (let r = 0; r < rings; r++) {
    setTimeout(() => {
      bullets.push({
        x: p.x,
        y: p.y,
        vx: 0,
        vy: 0,
        r: 10,
        owner: 'player',
        type: 'pulse',
        color: '#00ff88',
        radius: 10,
        maxRadius: 500 + p.power * 50,
        expanding: true,
        alpha: 1
      });
    }, r * 100);
  }
}
```

- [ ] **Step 2: 添加螺旋弹幕函数**

```javascript
// Weapon 5: 螺旋弹幕 - 螺旋排列
let spiralAngle = 0;
function fireSpiralShot(p) {
  spiralAngle += 25 + p.power * 3;
  const arms = p.power >= 2 ? 2 : 1;
  const speed = -350 - p.power * 20;
  const baseAngle = spiralAngle * Math.PI / 180;
  
  for (let arm = 0; arm < arms; arm++) {
    const offset = (arm * Math.PI * 2 / arms);
    bullets.push({
      x: p.x,
      y: p.y - 15,
      vx: Math.sin(baseAngle + offset) * 80,
      vy: speed,
      r: 4,
      owner: 'player',
      type: 'spiral',
      color: `hsl${(spiralAngle + arm * 30) % 360}, 100%, 60%`,
      angle: baseAngle + offset
    });
  }
}
```

- [ ] **Step 3: 在 updateBullets 中添加脉冲和螺旋更新**

```javascript
// Energy pulse expansion
if (b.type === 'pulse') {
  if (b.expanding) {
    b.radius += 400 * dt;
    b.alpha = 1 - (b.radius / b.maxRadius);
    if (b.radius >= b.maxRadius) {
      bullets.splice(i, 1);
    }
  }
}

// Spiral spin (visual only, handled in draw)
```

- [ ] **Step 4: 修改子弹绘制添加螺旋颜色**

```javascript
// Spiral color
if (b.type === 'spiral') {
  ctx.fillStyle = b.color;
}
```

- [ ] **Step 5: 保存并继续**

---

### Task 8: 实现武器6 - 闪电环 and 武器7 - 波动炮

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加闪电环函数**

```javascript
// Weapon 6: 闪电环 - 电弧扩散
function fireLightningRing(p) {
  bullets.push({
    x: p.x,
    y: p.y,
    vx: 0,
    vy: 0,
    r: 15,
    owner: 'player',
    type: 'lightning',
    color: '#ffffff',
    radius: 20,
    maxRadius: 500,
    expanding: true,
    alpha: 1,
    bolts: [],
    boltTimer: 0
  });
}
```

- [ ] **Step 2: 添加波动炮函数**

```javascript
// Weapon 7: 波动炮 - 蓄力后冲击波
function fireWaveCannon(p) {
  // Charged state on player
  p.charging = true;
  p.chargeTime = 0;
  p.chargeTimer = p.chargeTimer || 0;
  p.chargeTimer += dt;
  
  if (p.chargeTimer >= 0.5) {
    // Release!
    p.charging = false;
    p.chargeTimer = 0;
    
    bullets.push({
      x: p.x,
      y: p.y,
      vx: 0,
      vy: 0,
      r: 20,
      owner: 'player',
      type: 'wave',
      color: '#ff00ff',
      radius: 30,
      maxRadius: 600 + p.power * 60,
      expanding: true,
      alpha: 1
    });
  }
}
```

- [ ] **Step 3: 在 updateBullets 中添加闪电和波动更新**

```javascript
// Lightning ring
if (b.type === 'lightning') {
  b.radius += 350 * dt;
  b.alpha = 1 - (b.radius / b.maxRadius);
  b.boltTimer += dt;
  if (b.boltTimer > 0.05) {
    b.boltTimer = 0;
    // Spawn lightning bolt
    const angle = Math.random() * Math.PI * 2;
    b.bolts.push({
      x: b.x + Math.cos(angle) * b.radius,
      y: b.y + Math.sin(angle) * b.radius,
      life: 0.1
    });
  }
  // Update bolts
  for (let j = b.bolts.length - 1; j >= 0; j--) {
    b.bolts[j].life -= dt;
    if (b.bolts[j].life <= 0) b.bolts.splice(j, 1);
  }
  if (b.radius >= b.maxRadius) {
    bullets.splice(i, 1);
  }
}

// Wave cannon
if (b.type === 'wave') {
  b.radius += 500 * dt;
  b.alpha = 1 - (b.radius / b.maxRadius);
  if (b.radius >= b.maxRadius) {
    bullets.splice(i, 1);
  }
}
```

- [ ] **Step 4: 在绘制中添加闪电bolt效果**

```javascript
// Lightning bolts
if (b.type === 'lightning' && b.bolts) {
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  for (const bolt of b.bolts) {
    ctx.beginPath();
    ctx.moveTo(b.x, b.y);
    ctx.lineTo(bolt.x, bolt.y);
    ctx.stroke();
  }
}
```

- [ ] **Step 5: 添加玩家蓄力显示**

在玩家绘制处添加：

```javascript
// Charge indicator
if (p.charging) {
  p.chargeTime += dt;
  ctx.strokeStyle = `rgba(255, 0, 255, ${0.5 + Math.sin(p.chargeTime * 20) * 0.5})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(p.x, p.y, 25 + p.chargeTime * 20, 0, Math.PI * 2);
  ctx.stroke();
}
```

- [ ] **Step 6: 保存并继续**

---

### Task 9: 实现武器8 - 冰晶刺 and 武器9 - 黑洞弹

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加冰晶刺函数**

```javascript
// Weapon 8: 冰晶刺 - 冰冻控制
let bossFreezeTimer = 0;
let bossFrozen = false;
function fireIceSpike(p) {
  const angle = -Math.PI / 2;
  bullets.push({
    x: p.x,
    y: p.y - 20,
    vx: Math.sin(angle) * 100,
    vy: Math.cos(angle) * -450,
    r: 6,
    owner: 'player',
    type: 'ice',
    color: '#00ddff',
    frozen: false
  });
}
```

- [ ] **Step 2: 添加黑洞弹函数**

```javascript
// Weapon 9: 黑洞弹 - 引力吸引
function fireBlackHole(p) {
  bullets.push({
    x: p.x,
    y: p.y - 50,
    vx: 0,
    vy: 0,
    r: 15,
    owner: 'player',
    type: 'blackhole',
    color: '#6600ff',
    radius: 20,
    maxRadius: 100,
    gravityRadius: 120,
    active: true,
    time: 0,
    duration: 2.0 + p.power * 0.3,
    exploding: false,
    explosionRadius: 150
  });
}
```

- [ ] **Step 3: 在 updateBullets 中添加冰晶和黑洞更新**

```javascript
// Ice spike - freeze boss on hit
if (b.type === 'ice' && !b.frozen) {
  if (boss.active) {
    const dx = b.x - boss.x;
    const dy = b.y - boss.y;
    if (Math.sqrt(dx*dx + dy*dy) < boss.r + 10) {
      b.frozen = true;
      if (!bossFrozen || bossFreezeTimer <= 0) {
        bossFrozen = true;
        bossFreezeTimer = 0.5 + player.power * 0.1;
      }
    }
  }
}

// Black hole
if (b.type === 'blackhole') {
  b.time += dt;
  if (b.time >= b.duration) {
    if (!b.exploding) {
      b.exploding = true;
      b.vx = 0;
      b.vy = 0;
    }
    // Explosion
    b.radius += (b.explosionRadius - b.radius) * dt * 5;
    if (b.radius >= b.explosionRadius * 0.9) {
      bullets.splice(i, 1);
    }
  } else {
    // Gravity pull on enemy bullets
    for (let j = bullets.length - 1; j >= 0; j--) {
      const e = bullets[j];
      if (e.owner === 'boss') {
        const dx = b.x - e.x;
        const dy = b.y - e.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < b.gravityRadius && dist > 0) {
          e.vx += (dx / dist) * 300 * dt;
          e.vy += (dy / dist) * 300 * dt;
        }
      }
    }
  }
}
```

- [ ] **Step 4: 在 BOSS 更新中添加冻结逻辑**

找到BOSS更新函数，添加：

```javascript
// Ice freeze
if (bossFrozen) {
  bossFreezeTimer -= dt;
  if (bossFreezeTimer <= 0) {
    bossFrozen = false;
    bossFreezeTimer = 0;
  }
} else {
  // Normal boss update
}
```

- [ ] **Step 5: 添加冻结视觉**

在BOSS绘制处添加：

```javascript
// Frozen effect
if (bossFrozen) {
  ctx.fillStyle = 'rgba(100, 200, 255, 0.4)';
  ctx.beginPath();
  ctx.arc(boss.x, boss.y, boss.r + 10, 0, Math.PI * 2);
  ctx.fill();
}
```

- [ ] **Step 6: 保存并继续**

---

### Task 10: 实现武器10 - 时间钟摆 and HUD显示

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加时间钟摆函数**

```javascript
// Weapon 10: 时间钟摆 - 摆动穿越
let pendulumAngle = 0;
function fireTimePendulum(p) {
  const amplitude = 30 + player.power * 3;
  bullets.push({
    x: p.x,
    y: p.y - 20,
    vx: 0,
    vy: -300,
    r: 8,
    owner: 'player',
    type: 'pendulum',
    color: '#ffdd00',
    originY: p.y - 20,
    amplitude: amplitude,
    pendulumAngle: pendulumAngle,
    time: 0,
    duration: 1.5
  });
  pendulumAngle += 20;
}
```

- [ ] **Step 2: 在 updateBullets 中添加钟摆更新**

```javascript
// Time pendulum
if (b.type === 'pendulum') {
  b.time += dt;
  b.pendulumAngle += dt * 250;
  const xOffset = Math.sin(b.pendulumAngle * Math.PI / 180) * b.amplitude;
  b.x += xOffset * dt * 3;
  if (b.time >= b.duration) {
    bullets.splice(i, 1);
  }
}
```

- [ ] **Step 3: 添加Weapon HUD显示**

找到 drawHUD 函数，添加：

```javascript
// Weapon indicator
ctx.font = '14px "Courier New"';
ctx.fillStyle = '#aaaaaa';
ctx.textAlign = 'left';
ctx.fillText(`WEAPON: ${WEAPON_NAMES[currentWeapon]}`, 10, 60);
ctx.fillText(`KILLS: ${killCount}/${KILLS_PER_WEAPON}`, 10, 80);

// Weapon CD indicator
const cd = WEAPON_CDS[currentWeapon];
if (cd > 0) {
  const now = gameTime;
  const elapsed = now - lastWeaponFire[currentWeapon];
  const progress = Math.min(1, elapsed / cd);
  const cdY = 95;
  ctx.fillStyle = '#333';
  ctx.fillRect(10, cdY, 60, 6);
  ctx.fillStyle = progress >= 1 ? '#00ffff' : '#ff4444';
  ctx.fillRect(10, cdY, 60 * progress, 6);
}
```

- [ ] **Step 4: 保存并继续**

---

### Task 11: 测试与验证

**Files:**
- Modify: `bullet-hell.html` 无需修改，用于验证

- [ ] **Step 1: 打开游戏测试**

在浏览器中打开 bullet-hell.html，确认：
1. 游戏正常启动
2. 玩家可以射击
3. 击杀5个BOSS后武器切换
4. 切换时有动画提示

- [ ] **Step 2: 测试各武器**

验证每把武器都能正常发射：
1. 散弹三连 - 扇形散射
2. 追踪火箭 - 寻找BOSS
3. 回旋镖 - 绕圈返回
4. 能量脉冲 - 扩散环
5. 螺旋弹幕 - 螺旋排列
6. 闪电环 - 电弧闪电
7. 波动炮 - 蓄力释放
8. 冰晶刺 - 冻结BOSS
9. 黑洞弹 - 吸引敌弹
10. 时间钟摆 - 摆动穿越

- [ ] **Step 3: 测试Power加成**

验证Power加成对各武器的影响

- [ ] **Step 4: 保存并提交**

---

## 实现计划完成

10把武器全部实现，武器切换机制和HUD显示完成。建议使用 subagent-driven-development 执行。