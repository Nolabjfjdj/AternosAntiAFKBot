const mineflayer = require('mineflayer')
const http = require('http')

// ─── CONFIG ───────────────────────────────────────────────
const HOST = 'VRFTYGU.aternos.me'
const PORT = 15822
const USERNAME = 'AternosBot'
const VERSION = '1.20.1'
const RECONNECT_DELAY = 10000 // 10 secondes entre chaque reconnexion
const AFK_INTERVAL = 30000    // mouvement anti-AFK toutes les 30s
// ──────────────────────────────────────────────────────────

let bot = null
let afkTimer = null
let reconnectTimer = null

function createBot() {
  console.log(`[Bot] Connexion à ${HOST}:${PORT}...`)

  bot = mineflayer.createBot({
    host: HOST,
    port: PORT,
    username: USERNAME,
    version: VERSION,
    auth: 'offline',
    hideErrors: false,
  })

  bot.once('spawn', () => {
    console.log(`[Bot] Connecté en tant que ${USERNAME} !`)
    startAntiAFK()
  })

  bot.on('chat', (username, message) => {
    if (username === USERNAME) return
    console.log(`[Chat] <${username}> ${message}`)
  })

  bot.on('kicked', (reason) => {
    console.log(`[Bot] Kické : ${reason}`)
    cleanup()
    scheduleReconnect()
  })

  bot.on('error', (err) => {
    console.log(`[Bot] Erreur : ${err.message}`)
    cleanup()
    scheduleReconnect()
  })

  bot.on('end', (reason) => {
    console.log(`[Bot] Déconnecté : ${reason}`)
    cleanup()
    scheduleReconnect()
  })
}

function startAntiAFK() {
  stopAntiAFK()
  afkTimer = setInterval(() => {
    if (!bot || !bot.entity) return
    // Rotation aléatoire + petit saut pour éviter le kick AFK
    bot.setControlState('jump', true)
    setTimeout(() => {
      if (bot) bot.setControlState('jump', false)
    }, 500)
    bot.look(Math.random() * Math.PI * 2, 0, false)
    console.log('[AFK] Mouvement anti-AFK effectué')
  }, AFK_INTERVAL)
}

function stopAntiAFK() {
  if (afkTimer) {
    clearInterval(afkTimer)
    afkTimer = null
  }
}

function cleanup() {
  stopAntiAFK()
  if (bot) {
    bot.removeAllListeners()
    bot = null
  }
}

function scheduleReconnect() {
  if (reconnectTimer) return
  console.log(`[Bot] Reconnexion dans ${RECONNECT_DELAY / 1000}s...`)
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    createBot()
  }, RECONNECT_DELAY)
}

// ─── Health server pour Railway ───────────────────────────
const PORT_HTTP = process.env.PORT || 3000
http.createServer((req, res) => {
  res.writeHead(200)
  res.end('Bot en ligne')
}).listen(PORT_HTTP, () => {
  console.log(`[Health] Serveur HTTP sur le port ${PORT_HTTP}`)
})

// ─── Démarrage ────────────────────────────────────────────
createBot()
