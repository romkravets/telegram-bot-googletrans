module.exports = {
  apps: [{
    name: "translate-bot",
    script: "bot.py",
    interpreter: "python3",
    restart_delay: 3000,
    max_restarts: 10,
    env: {
      NODE_ENV: "production"
    }
  }]
}
