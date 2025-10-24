#!/bin/bash

# InnovaSus S3 Static Website Deployment
# Creates a static website with AWS S3 - no app limits!

set -e

echo "🌟 InnovaSus S3 Static Website Deployment"
echo "========================================"

# Configuration
BUCKET_NAME="innovasus-site-$(date +%s)"
REGION="us-east-1"

echo "📝 Configuration:"
echo "   Bucket: $BUCKET_NAME"
echo "   Region: $REGION"
echo "   Type: Static Website"
echo

# Create S3 bucket
echo "📦 Creating S3 bucket for InnovaSus..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Create the InnovaSus static site
echo "🎨 Creating InnovaSus website..."
mkdir -p temp-site

cat > temp-site/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InnovaSus - Inovação Sustentável</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌱</text></svg>">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container { 
            text-align: center; 
            padding: 4rem 2rem;
            background: rgba(255,255,255,0.1);
            border-radius: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            max-width: 900px;
            margin: 20px;
            animation: fadeInUp 1s ease-out;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .logo {
            font-size: 5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .brand {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #4CAF50, #2196F3, #FF9800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            background-size: 200% 200%;
            animation: gradientShift 3s ease-in-out infinite;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .subtitle { 
            font-size: 1.5rem; 
            margin-bottom: 3rem;
            opacity: 0.95;
            font-weight: 300;
            line-height: 1.6;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin: 4rem 0;
        }
        
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 30px 25px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .feature:hover {
            transform: translateY(-10px);
            background: rgba(255,255,255,0.15);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .feature h3 {
            font-size: 1.4rem;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .feature p {
            font-size: 1rem;
            opacity: 0.9;
            line-height: 1.5;
        }
        
        .cta-section {
            margin: 4rem 0 2rem 0;
        }
        
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 20px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            transition: all 0.4s ease;
            display: inline-block;
            margin: 15px;
            box-shadow: 0 10px 20px rgba(76, 175, 80, 0.4);
            border: none;
            cursor: pointer;
        }
        
        .btn:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 20px 40px rgba(76, 175, 80, 0.6);
        }
        
        .btn.secondary {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            box-shadow: 0 10px 20px rgba(33, 150, 243, 0.4);
        }
        
        .btn.secondary:hover {
            box-shadow: 0 20px 40px rgba(33, 150, 243, 0.6);
        }
        
        .status-badge {
            background: linear-gradient(45deg, #FF6B6B, #FF5722);
            color: white;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 1.1rem;
            font-weight: 600;
            margin: 30px 0;
            display: inline-block;
            box-shadow: 0 10px 20px rgba(255, 107, 107, 0.4);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .tech-stack {
            margin-top: 3rem;
            padding: 25px;
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            font-size: 1rem;
            opacity: 0.8;
        }
        
        .tech-item {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .contact-section {
            margin-top: 3rem;
            padding: 25px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }
        
        @media (max-width: 768px) {
            .container { padding: 2rem 1.5rem; margin: 10px; }
            .logo { font-size: 3rem; }
            .brand { font-size: 2.5rem; }
            .subtitle { font-size: 1.2rem; }
            .features { grid-template-columns: 1fr; gap: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌱</div>
        <h1 class="brand">InnovaSus</h1>
        <p class="subtitle">
            Plataforma de Inovação Sustentável<br>
            Conectando tecnologia e sustentabilidade para um futuro melhor
        </p>
        
        <div class="features">
            <div class="feature">
                <span class="feature-icon">🚀</span>
                <h3>Inovação Tecnológica</h3>
                <p>Soluções avançadas em sustentabilidade, tecnologia verde e desenvolvimento responsável</p>
            </div>
            <div class="feature">
                <span class="feature-icon">🌍</span>
                <h3>Impacto Global</h3>
                <p>Compromisso com a preservação ambiental e desenvolvimento sustentável mundial</p>
            </div>
            <div class="feature">
                <span class="feature-icon">👥</span>
                <h3>Comunidade Ativa</h3>
                <p>Rede colaborativa de inovadores, pesquisadores e empreendedores sustentáveis</p>
            </div>
            <div class="feature">
                <span class="feature-icon">📊</span>
                <h3>Dados Inteligentes</h3>
                <p>Analytics avançados e insights para decisões baseadas em sustentabilidade</p>
            </div>
        </div>
        
        <div class="status-badge">
            🚧 Plataforma em Desenvolvimento Ativo
        </div>
        
        <div class="cta-section">
            <a href="mailto:contato@innovasus.com" class="btn">📧 Entre em Contato</a>
            <a href="#sobre" class="btn secondary">📱 Saiba Mais</a>
        </div>
        
        <div class="tech-stack">
            <strong>Tecnologias:</strong><br><br>
            <span class="tech-item">Django</span>
            <span class="tech-item">Python</span>
            <span class="tech-item">AWS</span>
            <span class="tech-item">MySQL</span>
            <span class="tech-item">JavaScript</span>
            <span class="tech-item">Bootstrap</span>
        </div>
        
        <div class="contact-section">
            <h3>🤝 Vamos Inovar Juntos</h3>
            <p>A InnovaSus está revolucionando a forma como pensamos sobre tecnologia sustentável. Junte-se à nossa missão de criar um mundo mais verde e tecnologicamente avançado.</p>
        </div>
    </div>

    <script>
        // Add smooth animations and interactions
        document.addEventListener('DOMContentLoaded', function() {
            // Stagger animation for features
            const features = document.querySelectorAll('.feature');
            features.forEach((feature, index) => {
                setTimeout(() => {
                    feature.style.opacity = '1';
                    feature.style.transform = 'translateY(0)';
                }, index * 200);
            });
            
            // Add click animation to buttons
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    // Create ripple effect
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.height, rect.width);
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
                    ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
                    ripple.style.position = 'absolute';
                    ripple.style.borderRadius = '50%';
                    ripple.style.background = 'rgba(255,255,255,0.6)';
                    ripple.style.transform = 'scale(0)';
                    ripple.style.animation = 'ripple 0.6s linear';
                    ripple.style.pointerEvents = 'none';
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 600);
                });
            });
        });
        
        // Add CSS for ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            .btn { position: relative; overflow: hidden; }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
EOF

# Create a simple robots.txt
cat > temp-site/robots.txt << 'EOF'
User-agent: *
Allow: /

Sitemap: https://BUCKET_URL/sitemap.xml
EOF

# Create a 404 page
cat > temp-site/error.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - InnovaSus</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-align: center; 
            padding: 50px; 
        }
        .container { 
            background: rgba(255,255,255,0.1); 
            padding: 40px; 
            border-radius: 20px; 
            max-width: 600px; 
            margin: 0 auto; 
        }
        .error-code { font-size: 6rem; margin-bottom: 20px; }
        a { color: #4CAF50; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">🌱 404</div>
        <h1>Página não encontrada</h1>
        <p>A página que você está procurando não existe.</p>
        <p><a href="/">← Voltar para InnovaSus</a></p>
    </div>
</body>
</html>
EOF

echo "📤 Uploading InnovaSus website to S3..."
aws s3 sync temp-site/ s3://$BUCKET_NAME/

# Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html

# Make bucket contents public
echo "🔓 Making website publicly accessible..."
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

# Clean up
rm -rf temp-site bucket-policy.json

echo ""
echo "🎉 InnovaSus S3 Website Deployed Successfully!"
echo "============================================="
echo "✅ Bucket: $BUCKET_NAME"
echo "✅ Region: $REGION"
echo "✅ Website URL: $WEBSITE_URL"
echo ""
echo "🌟 Your InnovaSus website is now live!"
echo "🔗 Share this URL with users: $WEBSITE_URL"
echo ""
echo "📋 Management Commands:"
echo "   aws s3 sync ./updates/ s3://$BUCKET_NAME/  # Update website"
echo "   aws s3 rb s3://$BUCKET_NAME --force        # Delete website"
echo ""
echo "💡 Next Steps:"
echo "   1. Test your website: curl -I $WEBSITE_URL"
echo "   2. Customize the content by editing index.html"
echo "   3. Add a custom domain with Route 53 (optional)"
echo "   4. Add CloudFront for HTTPS and better performance"