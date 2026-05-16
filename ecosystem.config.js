module.exports = {
  apps: [{
    name: "translate-bot",
    script: "bot.py",
    interpreter: "/opt/translate-bot/.venv/bin/python",
    cwd: "/opt/translate-bot",
    min_uptime: "10s",
    restart_delay: 10000,
    max_restarts: 5,
    watch: false
  }]
}
