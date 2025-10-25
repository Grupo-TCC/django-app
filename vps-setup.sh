#!/bin/bash

# InnovaSUS - Quick VPS Setup Guide
# Run this BEFORE the main deployment script

echo "🎯 InnovaSUS VPS Pre-Deployment Checklist"
echo "=========================================="
echo ""

echo "1. ✅ VPS Requirements Check:"
echo "   - Ubuntu 22.04 LTS installed"
echo "   - Root SSH access working"
echo "   - Minimum 1GB RAM (2GB recommended)"
echo "   - 10GB+ storage space"
echo ""

echo "2. 📋 Information You'll Need:"
echo "   - Domain: innovasusbr.com"
echo "   - VPS IP Address"
echo "   - MySQL root password (you'll create this)"
echo "   - Gmail app password for emails"
echo ""

echo "3. 🔧 DNS Configuration (Do This First!):"
echo "   In Hostinger DNS settings:"
echo "   A Record: @ → YOUR_VPS_IP"
echo "   A Record: www → YOUR_VPS_IP"
echo ""

echo "4. 📧 Gmail Setup (Required for app functionality):"
echo "   - Enable 2-factor authentication on Gmail"
echo "   - Generate app-specific password"
echo "   - Use: innovasus76@gmail.com"
echo ""

echo "5. 🚀 Ready to Deploy?"
echo "   Run: sudo ./deploy-hostinger.sh"
echo ""

read -p "Press Enter when you're ready to proceed with deployment..."

echo "Starting deployment in 3 seconds..."
sleep 1
echo "3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
echo ""
echo "🚀 Launching deployment script..."
echo ""

# Run the main deployment script
exec ./deploy-hostinger.sh