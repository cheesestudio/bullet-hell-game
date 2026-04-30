// Bullet Hell - WebSocket Relay Server
// Radmin VPN 联机中继服务器
// 运行: node relay.js

const { WebSocketServer } = require('ws');

const WS_PORT = 8007;
const MAX_PLAYERS = 4;

const wss = new WebSocketServer({ port: WS_PORT });
const clients = new Map(); // ws -> { id, ready }

function getNextId() {
  const usedIds = new Set([...clients.values()].map(c => c.id));
  for (let i = 0; i < MAX_PLAYERS; i++) {
    if (!usedIds.has(i)) return i;
  }
  return -1;
}

wss.on('connection', ws => {
  if (clients.size >= MAX_PLAYERS) {
    ws.send(JSON.stringify({ t: 'error', msg: '房间已满 (最多4人)' }));
    ws.close();
    return;
  }

  const id = getNextId();
  const isHost = (clients.size === 0); // First player is host
  clients.set(ws, { id, ready: false });

  // Send welcome to new player
  ws.send(JSON.stringify({
    t: 'welcome',
    id,
    host: isHost,
    players: [...clients.values()].map(c => ({ id: c.id, ready: c.ready }))
  }));

  // Broadcast join to existing players
  broadcast({ t: 'joined', id }, ws);
  console.log(`玩家 ${id} 已连接 (${clients.size}/${MAX_PLAYERS})`);

  ws.on('message', raw => {
    try {
      const msg = JSON.parse(raw);
      const client = clients.get(ws);
      if (!client) return;
      msg.id = client.id; // Stamp sender ID

      if (msg.t === 'ready') {
        client.ready = true;
      }

      // Only host (first connected player) can start the game
      if (msg.t === 'start') {
        const hostClient = [...clients.values()].reduce((a, b) => a.id < b.id ? a : b, { id: Infinity });
        if (client.id !== hostClient.id) return; // ignore non-host start
      }

      // Broadcast to all others
      broadcast(msg, ws);
    } catch (e) {}
  });

  ws.on('close', () => {
    const client = clients.get(ws);
    clients.delete(ws);
    if (client) {
      broadcast({ t: 'left', id: client.id });
      console.log(`玩家 ${client.id} 已断开 (${clients.size}/${MAX_PLAYERS})`);
    }
    // Reset when room is empty
    if (clients.size === 0) {
      console.log('房间已空');
    }
  });
});

function broadcast(msg, except) {
  const data = JSON.stringify(msg);
  for (const [ws] of clients) {
    if (ws !== except && ws.readyState === 1) {
      ws.send(data);
    }
  }
}

console.log(`\u2705 Relay 中继服务器已启动 ws://0.0.0.0:${WS_PORT}`);
console.log('\u2705 在 Radmin VPN 网络中，玩家通过主机IP连接');
console.log(`\u2705 最大支持 ${MAX_PLAYERS} 名玩家`);
