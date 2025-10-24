#!/bin/bash

# InnovaSus Railway Region Troubleshooter
echo "🚀 Railway Deployment Troubleshooter"
echo "==================================="

echo "🔍 Railway Status Check:"
echo "1. Railway Status: https://railway.app/status"
echo "2. Try different times (off-peak hours)"
echo "3. Clear browser cache and retry"
echo ""

echo "⚡ Quick Alternative Solutions:"
echo ""
echo "🥇 Render.com (MOST RELIABLE):"
echo "   1. Go to: https://render.com"
echo "   2. Sign up with GitHub"
echo "   3. Import: Grupo-TCC/django-app"
echo "   4. Render auto-detects render.yaml"
echo "   5. Deploy with free PostgreSQL"
echo ""
echo "🥈 Fly.io (Fast Alternative):"
echo "   1. Go to: https://fly.io"
echo "   2. Sign up and install flyctl"
echo "   3. Use our fly.toml configuration"
echo ""
echo "🥉 Back4App (Simple):"
echo "   1. Go to: https://back4app.com"
echo "   2. Connect GitHub repo"
echo "   3. One-click Django deployment"
echo ""

echo "💡 Railway Retry Tips:"
echo "• Wait 10-15 minutes for Railway servers to recover"
echo "• Try deploying during off-peak hours (late night/early morning)"
echo "• Delete any failed deployments first"
echo "• Use a different browser/incognito mode"

echo ""
read -p "Which platform would you like to try? (render/fly/railway-retry): " choice

case $choice in
    "render"|"1")
        echo "🎯 Opening Render.com..."
        open https://render.com
        echo "✅ render.yaml is already configured in your repo!"
        ;;
    "fly"|"2") 
        echo "🎯 Opening Fly.io..."
        open https://fly.io
        echo "✅ fly.toml is already configured in your repo!"
        ;;
    "railway-retry"|"3")
        echo "🎯 Opening Railway (retry)..."
        open https://railway.app
        echo "💡 Clear cache, try incognito, or wait 15 minutes"
        ;;
    *)
        echo "🌐 Opening all platforms:"
        open https://render.com
        open https://railway.app
        open https://fly.io
        ;;
esac

echo ""
echo "🎉 InnovaSus is ready to deploy on any platform!"