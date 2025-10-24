#!/bin/bash

# InnovaSus Free Hosting Deployment
# Deploy to free platforms while AWS account verifies

echo "🌟 InnovaSus Free Hosting Deployment"
echo "===================================="
echo "Deploy InnovaSus while waiting for AWS verification"

echo ""
echo "📋 Available Free Hosting Options:"
echo ""
echo "1. 🚀 Vercel (Recommended)"
echo "   - Free domain: https://innovasus.vercel.app"
echo "   - Automatic HTTPS"
echo "   - GitHub integration"
echo ""
echo "2. 🌐 Netlify"
echo "   - Free domain: https://innovasus.netlify.app"
echo "   - Instant deploys"
echo "   - Form handling"
echo ""
echo "3. 🐙 GitHub Pages"
echo "   - Free domain: https://grupo-tcc.github.io/django-app"
echo "   - Direct from GitHub"
echo ""
echo "4. 🔄 Railway"
echo "   - Full Django support"
echo "   - Free PostgreSQL database"
echo ""

read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "🚀 Setting up Vercel deployment..."
        
        # Install Vercel CLI
        if ! command -v vercel &> /dev/null; then
            echo "📦 Installing Vercel CLI..."
            npm i -g vercel
        fi
        
        # Create vercel.json configuration
        cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "setup/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.9" }
    },
    {
      "src": "build.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "staticfiles"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "src": "/(.*)",
      "dest": "setup/wsgi.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "setup.settings_production"
  }
}
EOF

        # Create build script
        cat > build.sh << 'EOF'
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
EOF
        
        chmod +x build.sh
        
        echo "✅ Vercel configuration created!"
        echo "📋 Next steps:"
        echo "1. Run: vercel --prod"
        echo "2. Follow the setup prompts"
        echo "3. Your site will be live at: https://innovasus.vercel.app"
        ;;
        
    2)
        echo "🌐 Setting up Netlify deployment..."
        
        # Create netlify.toml
        cat > netlify.toml << 'EOF'
[build]
  publish = "staticfiles"
  command = "python manage.py collectstatic --noinput"

[build.environment]
  PYTHON_VERSION = "3.9"
  DJANGO_SETTINGS_MODULE = "setup.settings_static"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF
        
        echo "✅ Netlify configuration created!"
        echo "📋 Next steps:"
        echo "1. Go to: https://netlify.com"
        echo "2. Connect GitHub repository: Grupo-TCC/django-app"
        echo "3. Your site will be live at: https://innovasus.netlify.app"
        ;;
        
    3)
        echo "🐙 Setting up GitHub Pages..."
        
        # Create GitHub Actions workflow
        mkdir -p .github/workflows
        cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy InnovaSus to GitHub Pages

on:
  push:
    branches: [ master ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install whitenoise
    
    - name: Build static files
      run: |
        python manage.py collectstatic --noinput --settings=setup.settings_static
        cp staticfiles/index.html staticfiles/404.html
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./staticfiles
EOF
        
        echo "✅ GitHub Pages workflow created!"
        echo "📋 Next steps:"
        echo "1. Commit and push changes"
        echo "2. Enable Pages in GitHub repo settings"
        echo "3. Your site will be live at: https://grupo-tcc.github.io/django-app"
        ;;
        
    4)
        echo "🔄 Setting up Railway deployment..."
        
        # Create railway.toml
        cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && gunicorn setup.wsgi:application"
healthcheckPath = "/"
restartPolicyType = "ON_FAILURE"

[env]
DJANGO_SETTINGS_MODULE = "setup.settings_production"
EOF
        
        # Create Procfile
        cat > Procfile << 'EOF'
web: gunicorn setup.wsgi:application
release: python manage.py migrate
EOF
        
        echo "✅ Railway configuration created!"
        echo "📋 Next steps:"
        echo "1. Go to: https://railway.app"
        echo "2. Connect GitHub repository: Grupo-TCC/django-app"
        echo "3. Deploy with one click"
        echo "4. Get free PostgreSQL database"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 InnovaSus deployment configured!"
echo ""
echo "💡 While you wait for AWS verification:"
echo "✅ Use free hosting to get InnovaSus online immediately"
echo "✅ Get a working URL to share with users"
echo "✅ Test your application functionality"
echo ""
echo "🔄 Once AWS is verified (24-48 hours):"
echo "✅ You can migrate to AWS for more features"
echo "✅ Use the AWS scripts we prepared"
echo "✅ Get professional AWS domain"