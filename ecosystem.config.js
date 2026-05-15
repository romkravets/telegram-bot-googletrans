module.exports = {
  apps: [{
    name: "translate-bot",
    script: "bot.py",
    interpreter: "python3",
    min_uptime: "10s",
    restart_delay: 3000,
    max_restarts: 10,
    watch: false
  }]
}
