#!/bin/bash

# Oda Bot Status Check Script
# Checks the status of the bot across different deployment methods

echo "🤖 Oda Bot Status Check"
echo "======================="

# Check Docker deployment
if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Docker Status:"
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "oda-discord-bot\|oda-bot"; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -1
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "oda-discord-bot|oda-bot"
        echo "📊 Docker logs (last 10 lines):"
        docker logs --tail 10 oda-discord-bot 2>/dev/null || docker logs --tail 10 oda-bot 2>/dev/null || echo "   No logs available"
    else
        echo "   ❌ Bot container not running"
    fi
else
    echo ""
    echo "🐳 Docker: Not installed"
fi

# Check systemd service
if command -v systemctl &> /dev/null; then
    echo ""
    echo "⚙️  Systemd Service Status:"
    if systemctl is-enabled oda-bot &>/dev/null; then
        systemctl status oda-bot --no-pager --lines=3 2>/dev/null || echo "   Service not found"
    else
        echo "   ❌ oda-bot service not enabled or found"
    fi
else
    echo ""
    echo "⚙️  Systemd: Not available"
fi

# Check if bot process is running
echo ""
echo "🔍 Process Check:"
if pgrep -f "bot.py" > /dev/null; then
    echo "   ✅ Bot process found:"
    ps aux | grep "bot.py" | grep -v grep | awk '{print "      PID:", $2, "CPU:", $3"%", "MEM:", $4"%", "CMD:", $11, $12, $13}'
else
    echo "   ❌ No bot process found"
fi

# Check logs if available
echo ""
echo "📋 Recent Logs:"
if [ -f "/opt/oda-bot/logs/bot.log" ]; then
    echo "   System logs (last 5 lines):"
    tail -n 5 /opt/oda-bot/logs/bot.log 2>/dev/null | sed 's/^/      /'
elif [ -f "./logs/bot.log" ]; then
    echo "   Local logs (last 5 lines):"
    tail -n 5 ./logs/bot.log 2>/dev/null | sed 's/^/      /'
elif command -v journalctl &> /dev/null && systemctl is-enabled oda-bot &>/dev/null; then
    echo "   Journal logs (last 5 lines):"
    journalctl -u oda-bot --no-pager -n 5 2>/dev/null | sed 's/^/      /' || echo "      No journal logs available"
else
    echo "   ❌ No log files found"
fi

# Check network connectivity (optional)
echo ""
echo "🌐 Network Check:"
if command -v ping &> /dev/null; then
    if ping -c 1 discord.com &> /dev/null; then
        echo "   ✅ Can reach Discord servers"
    else
        echo "   ❌ Cannot reach Discord servers"
    fi
else
    echo "   ❓ Ping not available"
fi

echo ""
echo "💡 Quick Actions:"
echo "   • Restart Docker: docker-compose restart oda-bot"
echo "   • Restart Service: sudo systemctl restart oda-bot"
echo "   • View Docker logs: docker logs -f oda-discord-bot"
echo "   • View Service logs: journalctl -u oda-bot -f"