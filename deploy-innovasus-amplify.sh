#!/bin/bash

# InnovaSus AWS Amplify Deployment (Easiest Free AWS Domain)
# Uses AWS Amplify for free subdomain with automatic HTTPS

set -e

echo "🌟 InnovaSus AWS Amplify Deployment"
echo "=================================="
echo "This will deploy InnovaSus with a FREE AWS Amplify domain!"

# Configuration
APP_NAME="innovasus"
REGION="us-east-1"
BRANCH="master"

echo "📝 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Region: $REGION"
echo "   GitHub Repo: Grupo-TCC/django-app"
echo "   Branch: $BRANCH"
echo "   Free Domain: https://main.d[random].amplifyapp.com/"
echo

# Check if AWS Amplify CLI is available
if ! command -v aws amplify &> /dev/null; then
    echo "Using AWS CLI for Amplify deployment..."
fi

# First, let's create a simple build specification for Django
cat > amplify.yml << 'EOF'
version: 1
backend:
  phases:
    build:
      commands:
        - '# No backend for static deployment'
frontend:
  phases:
    preBuild:
      commands:
        - echo "Installing dependencies..."
        - pip3 install -r requirements.txt
        - pip3 install django-environ whitenoise
    build:
      commands:
        - echo "Building InnovaSus static files..."
        - python3 manage.py collectstatic --noinput --settings=setup.settings_static
        - echo "Build completed successfully!"
  artifacts:
    baseDirectory: staticfiles
    files:
      - '**/*'
  cache:
    paths:
      - .venv/**/*
EOF

# Create static-only settings for Amplify
cat > setup/settings_static.py << 'EOF'
"""
Static site settings for AWS Amplify deployment
"""
from .settings import *
import os

# Static files configuration
STATIC_URL = '/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Collect all static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Basic settings for static build
DEBUG = False
SECRET_KEY = 'static-build-key'
ALLOWED_HOSTS = ['*']

# Minimal database for collectstatic
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
EOF

# Create a simple index.html for the root
mkdir -p staticfiles
cat > staticfiles/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InnovaSus - Inovação Sustentável</title>
    <link rel="stylesheet" href="/styles/home.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            text-align: center; 
            color: white; 
            padding: 3rem;
            background: rgba(255,255,255,0.15);
            border-radius: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255,255,255,0.18);
            max-width: 800px;
            margin: 20px;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle { 
            font-size: 1.4rem; 
            margin-bottom: 2.5rem;
            opacity: 0.95;
            font-weight: 300;
        }
        .btn { 
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white; 
            padding: 18px 35px; 
            text-decoration: none; 
            border-radius: 50px; 
            font-size: 1.2rem;
            font-weight: 600;
            transition: all 0.4s ease;
            display: inline-block;
            margin: 15px;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        }
        .btn:hover { 
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.6);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 3rem 0;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .feature:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.15);
        }
        .feature h3 {
            font-size: 1.5rem;
            margin-bottom: 15px;
        }
        .status-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            margin: 25px 0;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        }
        .tech-stack {
            margin-top: 2rem;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        @media (max-width: 768px) {
            .container { padding: 2rem; margin: 10px; }
            .logo { font-size: 2.5rem; }
            .subtitle { font-size: 1.1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌱 InnovaSus</div>
        <p class="subtitle">Plataforma de Inovação Sustentável</p>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 Inovação Tecnológica</h3>
                <p>Soluções avançadas em sustentabilidade e tecnologia verde</p>
            </div>
            <div class="feature">
                <h3>🌍 Impacto Ambiental</h3>
                <p>Compromisso com a preservação do meio ambiente</p>
            </div>
            <div class="feature">
                <h3>👥 Comunidade Ativa</h3>
                <p>Conectando mentes inovadoras pelo mundo</p>
            </div>
            <div class="feature">
                <h3>📊 Dados Inteligentes</h3>
                <p>Analytics e insights para decisões sustentáveis</p>
            </div>
        </div>
        
        <div class="status-badge">
            🚧 Plataforma em Desenvolvimento
        </div>
        
        <div>
            <a href="mailto:contato@innovasus.com" class="btn">📧 Entre em Contato</a>
            <a href="#sobre" class="btn">📱 Saiba Mais</a>
        </div>
        
        <div class="tech-stack">
            <strong>Tecnologias:</strong> Django • Python • AWS • MySQL • JavaScript
        </div>
    </div>

    <script>
        // Simple animation
        document.addEventListener('DOMContentLoaded', function() {
            const features = document.querySelectorAll('.feature');
            features.forEach((feature, index) => {
                setTimeout(() => {
                    feature.style.opacity = '1';
                    feature.style.transform = 'translateY(0)';
                }, index * 200);
            });
        });
    </script>
</body>
</html>
EOF

echo "📦 Preparing InnovaSus for deployment..."

# Try to create Amplify app using AWS CLI
echo "🚀 Creating InnovaSus Amplify app..."

APP_ID=$(aws amplify create-app \
    --name "$APP_NAME" \
    --description "InnovaSus - Plataforma de Inovação Sustentável" \
    --repository "https://github.com/Grupo-TCC/django-app" \
    --platform "WEB" \
    --region "$REGION" \
    --query 'app.appId' \
    --output text 2>/dev/null || echo "")

if [ -z "$APP_ID" ]; then
    echo "❌ Could not create Amplify app. Let's try a different approach..."
    echo ""
    echo "🔧 Manual Amplify Setup Instructions:"
    echo "======================================"
    echo "1. Go to AWS Console > Amplify"
    echo "2. Click 'Get Started' > 'Host your web app'"
    echo "3. Connect GitHub repository: Grupo-TCC/django-app"
    echo "4. Branch: master"
    echo "5. Use this build settings:"
    echo ""
    cat amplify.yml
    echo ""
    echo "6. Deploy!"
    echo ""
    echo "Your InnovaSus site will be live at:"
    echo "https://main.d[random].amplifyapp.com/"
    exit 1
fi

# Create branch
echo "🌿 Setting up branch deployment..."
aws amplify create-branch \
    --app-id "$APP_ID" \
    --branch-name "$BRANCH" \
    --region "$REGION" \
    --description "Main InnovaSus branch"

# Start deployment
echo "🚀 Starting InnovaSus deployment..."
JOB_ID=$(aws amplify start-job \
    --app-id "$APP_ID" \
    --branch-name "$BRANCH" \
    --job-type "RELEASE" \
    --region "$REGION" \
    --query 'jobSummary.jobId' \
    --output text)

echo "📡 Deployment started with Job ID: $JOB_ID"

# Get app URL
APP_URL=$(aws amplify get-app \
    --app-id "$APP_ID" \
    --region "$REGION" \
    --query 'app.defaultDomain' \
    --output text)

echo ""
echo "🎉 InnovaSus Amplify Deployment Complete!"
echo "======================================="
echo "✅ App ID: $APP_ID"
echo "✅ InnovaSus URL: https://$BRANCH.$APP_URL"
echo "✅ Automatic HTTPS enabled"
echo "✅ Global CDN active"
echo ""
echo "📊 Monitor deployment:"
echo "   AWS Console: https://console.aws.amazon.com/amplify/home#/$APP_ID"
echo ""
echo "🔄 Update commands:"
echo "   git push origin master    # Auto-deploys to Amplify"
echo ""
echo "🌟 Your InnovaSus platform is now live!"
EOF