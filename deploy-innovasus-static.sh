#!/bin/bash

# InnovaSus AWS S3 + CloudFront Static Deployment
# Free AWS domain with CloudFront for static sites

set -e

echo "🌟 InnovaSus Static Site with CloudFront"
echo "======================================="
echo "Deploy as a static site with free AWS CloudFront domain"

# Configuration
BUCKET_NAME="innovasus-static-$(date +%s)"
REGION="us-east-1"

echo "📝 Configuration:"
echo "   Bucket: $BUCKET_NAME"
echo "   Region: $REGION"
echo "   Type: Static Site"

# Create S3 bucket
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html

# Create a simple InnovaSus landing page
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InnovaSus - Inovação Sustentável</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            text-align: center; 
            color: white; 
            padding: 2rem;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            max-width: 600px;
        }
        h1 { 
            font-size: 3rem; 
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { 
            font-size: 1.2rem; 
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .btn { 
            background: #4CAF50; 
            color: white; 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 30px; 
            font-size: 1.1rem;
            transition: all 0.3s ease;
            display: inline-block;
            margin: 10px;
        }
        .btn:hover { 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 3rem;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .coming-soon {
            background: #ff6b6b;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 InnovaSus</h1>
        <p class="subtitle">Plataforma de Inovação Sustentável</p>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 Inovação</h3>
                <p>Soluções tecnológicas avançadas</p>
            </div>
            <div class="feature">
                <h3>🌍 Sustentabilidade</h3>
                <p>Compromisso com o meio ambiente</p>
            </div>
            <div class="feature">
                <h3>👥 Comunidade</h3>
                <p>Conectando mentes inovadoras</p>
            </div>
        </div>
        
        <div class="coming-soon">
            🚧 Plataforma completa em desenvolvimento
        </div>
        
        <div style="margin-top: 2rem;">
            <a href="#" class="btn">📱 Em Breve</a>
            <a href="mailto:contato@innovasus.com" class="btn">📧 Contato</a>
        </div>
    </div>
</body>
</html>
EOF

# Upload to S3
echo "📤 Uploading InnovaSus site..."
aws s3 sync . s3://$BUCKET_NAME --exclude "*.sh" --exclude ".git/*"

# Make bucket public
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
        {
            \"Sid\": \"PublicReadGetObject\",
            \"Effect\": \"Allow\",
            \"Principal\": \"*\",
            \"Action\": \"s3:GetObject\",
            \"Resource\": \"arn:aws:s3:::$BUCKET_NAME/*\"
        }
    ]
}"

# Create CloudFront distribution
echo "🌐 Creating CloudFront distribution..."
DISTRIBUTION_CONFIG="{
    \"CallerReference\": \"innovasus-$(date +%s)\",
    \"Comment\": \"InnovaSus Static Site\",
    \"DefaultRootObject\": \"index.html\",
    \"Origins\": {
        \"Quantity\": 1,
        \"Items\": [
            {
                \"Id\": \"S3-$BUCKET_NAME\",
                \"DomainName\": \"$BUCKET_NAME.s3.amazonaws.com\",
                \"S3OriginConfig\": {
                    \"OriginAccessIdentity\": \"\"
                }
            }
        ]
    },
    \"DefaultCacheBehavior\": {
        \"TargetOriginId\": \"S3-$BUCKET_NAME\",
        \"ViewerProtocolPolicy\": \"redirect-to-https\",
        \"MinTTL\": 0,
        \"ForwardedValues\": {
            \"QueryString\": false,
            \"Cookies\": {
                \"Forward\": \"none\"
            }
        }
    },
    \"Enabled\": true,
    \"PriceClass\": \"PriceClass_All\"
}"

DISTRIBUTION_ID=$(aws cloudfront create-distribution --distribution-config "$DISTRIBUTION_CONFIG" --query 'Distribution.Id' --output text)
CLOUDFRONT_URL=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)

echo "🎉 InnovaSus Static Site Deployed!"
echo "================================="
echo "✅ S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "✅ CloudFront URL: https://$CLOUDFRONT_URL"
echo ""
echo "📋 Management:"
echo "   aws s3 sync . s3://$BUCKET_NAME    - Update files"
echo "   aws s3 rb s3://$BUCKET_NAME --force - Delete bucket"