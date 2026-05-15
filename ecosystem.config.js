module.exports = {
  apps: [{
    name: "translate-bot",
    script: "bot.py",
    interpreter: "/opt/translate-bot/.venv/bin/python",
    min_uptime: "10s",
    restart_delay: 3000,
    max_restarts: 10,
    watch: false
  }]
}
