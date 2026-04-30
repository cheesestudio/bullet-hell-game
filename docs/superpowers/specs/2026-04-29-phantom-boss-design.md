# PHANTOM BOSS Design

**Date**: 2026-04-29
**Project**: Bullet Hell Boss Rush - PHANTOM BOSS
**Status**: Design approved

---

## Overview

PHANTOM是游戏的第4个BOSS，采用幽灵/虚体风格设计，具有独特的分身机制和干扰屏幕的特殊能力。

---

## PHANTOM Phases

| 形态 | 生命值 | 视觉 | 弹幕 | 特殊能力 |
|------|--------|------|------|----------|
| Phase 1 | 150 | 半透明幽灵轮廓 | 幻影追踪弹（3发一组） | 幽魂冲刺 + 虚影重重 |
| Phase 2 | 200 | 分裂成3个分身 | 包围弹幕（环形） | 鬼影追踪 + 分身 |
| Phase 3 | 300 | 完整巨大鬼魂 | 螺旋聚集（从四周向中心） | 旋转屏幕(360°) + 虚影重重 |

---

## Special Abilities

### 1. 幽魂冲刺 (Ghost Dash)
- **触发**: HP < 80%
- **持续时间**: 1秒
- **效果**: BOSS快速闪现到玩家附近位置
- **冷却**: 15秒

### 2. 虚影重重 (Shadow Realm)
- **触发**: HP < 70%
- **持续时间**: 5秒
- **效果**: 留下3个残影幻影，幻影会同步射击
- **冷却**: 25秒

### 3. 鬼影追踪 (Phantom Trail)
- **触发**: HP < 50%
- **持续时间**: 4秒
- **效果**: 发射半透明子弹缓慢追踪玩家
- **冷却**: 20秒

### 4. 分身 (Phase Split)
- **触发**: HP < 40%
- **持续时间**: 6秒
- **效果**: 分裂成3个分身，每个都有独立HP
- **冷却**: 30秒

### 5. 旋转屏幕 (Screen Rotate)
- **触发**: HP < 30% 或 HP < 20%
- **持续时间**: 3秒旋转 + 3秒恢复 = 6秒
- **效果**: 游戏画面缓慢旋转360°再转回来
- **冷却**: 25秒

**旋转屏幕实现：**
```javascript
function updateScreenRotation(dt) {
  if (screenRotationActive) {
    rotationAngle += rotationSpeed * dt; // 缓慢旋转
    if (rotationAngle >= 360) {
      // 开始恢复
      rotationAngle -= rotationSpeed * dt;
      if (rotationAngle <= 0) rotationAngle = 0;
    }
    // 应用画布旋转
    ctx.rotate(rotationAngle * Math.PI / 180);
  }
}
```

---

## Bullet Patterns

### Phase 1: Phantom Trail
```javascript
// 3发一组的追踪弹
for (let i = 0; i < 3; i++) {
  const angle = Math.atan2(player.y - boss.y, player.x - boss.x);
  bullets.push({
    x: boss.x,
    y: boss.y,
    vx: Math.cos(angle + i * 0.2) * 80,
    vy: Math.sin(angle + i * 0.2) * 80,
    tracking: true, // 追踪弹
    r: 5,
    owner: 'boss',
    color: '#8844ff',
    alpha: 0.6 // 半透明
  });
}
```

### Phase 2: Encircle
```javascript
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
```

### Phase 3: Spiral Convergence (螺旋聚集)
```javascript
// 从画布四角向中心螺旋
const corners = [
  {x: 0, y: 0},
  {x: canvas.width, y: 0},
  {x: canvas.width, y: canvas.height},
  {x: 0, y: canvas.height}
];

for (let c = 0; c < corners.length; c++) {
  for (let i = 0; i < 8; i++) {
    const t = i / 8;
    const startX = corners[c].x;
    const startY = corners[c].y;
    // 螺旋路径向中心移动
    const angle = Date.now() / 500 + i;
    bullets.push({
      x: startX * (1-t) + boss.x * t,
      y: startY * (1-t) + boss.y * t,
      vx: Math.cos(angle) * 20,
      vy: Math.sin(angle) * 20,
      r: 4,
      owner: 'boss',
      color: '#aa66ff'
    });
  }
}
```

---

## Visual Design

### Colors
- **主色调**: `#8844ff` (幽灵紫)
- **虚体色**: `#aa66ff` (浅紫光晕)
- **追踪弹**: `#6644ff` (半透明蓝紫)
- **Phase 3**: `#ff44ff` (品红边缘发光)

### Visual Effects
- Phase 1: 半透明轮廓 + 飘忽效果
- Phase 2: 3个分身实体 + 切换位置
- Phase 3: 巨大鬼魂形态 + 屏幕旋转干扰

---

## Drops (掉落物)

| 形态 | 能量数量 | 说明 |
|------|---------|------|
| Phase 1 | 1 | 击杀掉落 |
| Phase 2 | 2 | 击杀掉落 |
| Phase 3 | 4 | 击杀掉落更多 |

```javascript
// Phase 3 额外掉落
if (boss.phase === 2) { // Phase 3
  // 额外掉落2个能量
  for (let i = 0; i < 2; i++) {
    spawnPowerup(boss.x + (Math.random()-0.5)*50, boss.y, {name: 'POWER', color: '#ff0066'});
  }
}
```

---

## Implementation Architecture

```
bullet-hell.html
├── BOSS_PHASES        // 添加PHANTOM配置
├── BOSS_PATTERNS     // 添加新弹幕模式
│   ├── phantom_trail  // Phase 1 追踪弹
│   ├── encircle      // Phase 2 包围
│   └── spiral       // Phase 3 螺旋聚集
├── BOSS_ABILITIES   // 添加PHANTOM能力
│   ├── GHOST_DASH
│   ├── SHADOW_REALM
│   ├── PHANTOM_TRAIL
│   ├── PHASE_SPLIT
│   └── SCREEN_ROTATE
├── triggerScreenRotate() // 新能力函数
├── updateScreenRotation() // 旋转逻辑
└── renderBossPhantom() // PHANTOM渲染
```

---

## Acceptance Criteria

- [ ] PHANTOM作为第4个BOSS添加到游戏
- [ ] 3个形态都有独特视觉
- [ ] 3种新弹幕模式实现
- [ ] 5个特殊能力实现
- [ ] 旋转屏幕360°平滑过渡
- [ ] Phase 3掉落更多能量
- [ ] 保持60 FPS性能
- [ ] 赛博朋克视觉风格

---

## Difficulty Balancing

- Phase 1: 基础难度，学习模式
- Phase 2: 中等难度，需要移动技巧
- Phase 3: 高难度，屏幕干扰

**总HP**: 150 + 200 + 300 = 650 (比CORE更难)