#!/bin/bash

# InnovaSus AWS Infrastructure Setup with HTTPS Support
# Creates EC2 instance, RDS database, and security groups for SSL

set -e

echo "🌟 InnovaSus AWS Infrastructure Setup"
echo "====================================="

# Configuration
REGION="us-east-1"
PROJECT_NAME="innovasus"
KEY_NAME="innovasus-key"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📝 InnovaSus Infrastructure Configuration${NC}"
read -p "Enter your domain name (e.g., innovasus.com): " DOMAIN_NAME
read -p "Enter your email for notifications: " EMAIL
echo

# Create key pair
echo -e "${BLUE}🔑 Creating SSH key pair for InnovaSus...${NC}"
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION &>/dev/null; then
    aws ec2 create-key-pair --key-name $KEY_NAME --region $REGION --query 'KeyMaterial' --output text > ~/.ssh/${KEY_NAME}.pem
    chmod 400 ~/.ssh/${KEY_NAME}.pem
    echo -e "${GREEN}✅ Created new key pair: ~/.ssh/${KEY_NAME}.pem${NC}"
else
    echo -e "${YELLOW}⚠️  Key pair already exists${NC}"
fi

# Create security group for web server with HTTPS
echo -e "${BLUE}🔒 Creating security group for InnovaSus...${NC}"
SG_WEB=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-web-sg \
    --description "InnovaSus web server security group with HTTPS" \
    --region $REGION \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names ${PROJECT_NAME}-web-sg \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' --output text)

# Add rules for web access
aws ec2 authorize-security-group-ingress \
    --group-id $SG_WEB \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SG_WEB \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SG_WEB \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || true

# Create database security group
echo -e "${BLUE}🗄️  Creating database security group...${NC}"
SG_DB=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-db-sg \
    --description "InnovaSus database security group" \
    --region $REGION \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names ${PROJECT_NAME}-db-sg \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' --output text)

# Allow database access from web server
aws ec2 authorize-security-group-ingress \
    --group-id $SG_DB \
    --protocol tcp \
    --port 3306 \
    --source-group $SG_WEB \
    --region $REGION 2>/dev/null || true

# Create DB subnet group
echo -e "${BLUE}🌐 Creating database subnet group...${NC}"
SUBNETS=$(aws ec2 describe-subnets --region $REGION --query 'Subnets[?AvailabilityZone!=`us-east-1e`].SubnetId' --output text | tr '\t' ' ')
aws rds create-db-subnet-group \
    --db-subnet-group-name ${PROJECT_NAME}-subnet-group \
    --db-subnet-group-description "InnovaSus database subnet group" \
    --subnet-ids $SUBNETS \
    --region $REGION 2>/dev/null || true

# Create RDS instance
echo -e "${BLUE}💾 Creating MariaDB database for InnovaSus...${NC}"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
aws rds create-db-instance \
    --db-instance-identifier ${PROJECT_NAME}-mariadb \
    --db-instance-class db.t3.micro \
    --engine mariadb \
    --master-username admin \
    --master-user-password "$DB_PASSWORD" \
    --allocated-storage 20 \
    --vpc-security-group-ids $SG_DB \
    --db-subnet-group-name ${PROJECT_NAME}-subnet-group \
    --backup-retention-period 7 \
    --region $REGION \
    --no-multi-az \
    --no-publicly-accessible \
    --storage-type gp2 \
    --engine-version 10.11.8 2>/dev/null || echo -e "${YELLOW}⚠️  Database may already exist${NC}"

# Launch EC2 instance
echo -e "${BLUE}🖥️  Launching EC2 instance for InnovaSus...${NC}"
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0e86e20dae90224f1 \
    --count 1 \
    --instance-type t3.micro \
    --key-name $KEY_NAME \
    --security-group-ids $SG_WEB \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}-server},{Key=Project,Value=InnovaSus}]" \
    --user-data '#!/bin/bash
apt-get update
apt-get install -y awscli' \
    --query 'Instances[0].InstanceId' --output text)

echo -e "${GREEN}✅ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo -e "${BLUE}⏳ Waiting for instance to be ready...${NC}"
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get instance details
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# Get RDS endpoint
echo -e "${BLUE}⏳ Waiting for database to be available...${NC}"
aws rds wait db-instance-available --db-instance-identifier ${PROJECT_NAME}-mariadb --region $REGION

DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier ${PROJECT_NAME}-mariadb \
    --region $REGION \
    --query 'DBInstances[0].Endpoint.Address' --output text)

# Save configuration
cat > innovasus-deployment-vars << EOF
export EC2_INSTANCE_ID="$INSTANCE_ID"
export EC2_PUBLIC_IP="$PUBLIC_IP"
export RDS_IDENTIFIER="${PROJECT_NAME}-mariadb"
export RDS_ENDPOINT="$DB_ENDPOINT"
export DB_USERNAME="admin"
export DB_PASSWORD="$DB_PASSWORD"
export DB_NAME="django_db"
export AWS_REGION="$REGION"
export SSH_KEY="~/.ssh/${KEY_NAME}.pem"
export DOMAIN_NAME="$DOMAIN_NAME"
export EMAIL="$EMAIL"
export PROJECT_NAME="$PROJECT_NAME"
EOF

echo -e "${GREEN}🎉 InnovaSus Infrastructure Ready!${NC}"
echo "=================================="
echo -e "${GREEN}✅ Resources Created:${NC}"
echo "   EC2 Instance: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   Database: $DB_ENDPOINT"
echo "   SSH Key: ~/.ssh/${KEY_NAME}.pem"
echo
echo -e "${BLUE}📋 Configuration saved to: innovasus-deployment-vars${NC}"
echo
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo "1. Point your domain '$DOMAIN_NAME' to IP: $PUBLIC_IP"
echo "2. Wait 5-10 minutes for DNS propagation"
echo "3. Run the deployment script:"
echo "   scp -i ~/.ssh/${KEY_NAME}.pem deploy-innovasus-https.sh ubuntu@$PUBLIC_IP:~/"
echo "   ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo "   ./deploy-innovasus-https.sh"
echo
echo -e "${GREEN}🌟 InnovaSus will be live at: https://$DOMAIN_NAME${NC}"