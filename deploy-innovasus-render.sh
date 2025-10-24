#!/bin/bash

# InnovaSus Render.com Deployment
# Full Django backend support

echo "🌟 Setting up Render.com deployment for InnovaSus"
echo "================================================="

# Create render.yaml for full Django deployment
cat > render.yaml << 'EOF'
databases:
  - name: innovasus-db
    databaseName: innovasus
    user: innovasus_user

services:
  - type: web
    name: innovasus-backend
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn setup.wsgi:application"
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: setup.settings_production
      - key: DATABASE_URL
        fromDatabase:
          name: innovasus-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
    autoDeploy: false
EOF

echo "✅ Render.com configuration created!"
echo ""
echo "📋 Deployment Steps:"
echo "1. Go to: https://render.com"
echo "2. Sign up with GitHub"
echo "3. Import repository: Grupo-TCC/django-app" 
echo "4. Render will detect render.yaml automatically"
echo "5. Deploy with PostgreSQL database included"
echo ""
echo "🎯 You'll get:"
echo "✅ Full Django backend: https://innovasus-backend.onrender.com"
echo "✅ PostgreSQL database (free tier)"
echo "✅ Automatic HTTPS"
echo "✅ All Django features working"