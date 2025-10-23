#!/bin/bash

# AWS Deployment Automation Script
# This script automates the AWS infrastructure setup

set -e

echo "🚀 AWS Deployment Automation for Django + MariaDB"
echo "=================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get user inputs
read -p "Enter your desired AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

read -p "Enter database password (must be strong): " -s DB_PASSWORD
echo
if [ ${#DB_PASSWORD} -lt 8 ]; then
    echo "❌ Password must be at least 8 characters long"
    exit 1
fi

read -p "Enter your domain name (optional, press enter to skip): " DOMAIN_NAME

read -p "Enter your GitHub repository URL: " REPO_URL

echo "🔧 Setting up AWS infrastructure..."

# Set default region
export AWS_DEFAULT_REGION=$AWS_REGION

# Create key pair if it doesn't exist
KEY_NAME="django-app-key"
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &>/dev/null; then
    echo "📋 Creating SSH key pair..."
    
    # Generate key pair locally
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/$KEY_NAME -N ""
    
    # Import to AWS
    aws ec2 import-key-pair \
        --key-name $KEY_NAME \
        --public-key-material fileb://~/.ssh/${KEY_NAME}.pub
    
    echo "✅ SSH key pair created: ~/.ssh/$KEY_NAME"
else
    echo "✅ SSH key pair already exists"
fi

# Get default VPC and subnets
DEFAULT_VPC=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --query "Vpcs[0].VpcId" \
    --output text)

SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$DEFAULT_VPC" \
    --query "Subnets[].SubnetId" \
    --output text)

SUBNET_ARRAY=($SUBNETS)

echo "🌐 Using VPC: $DEFAULT_VPC"
echo "🌐 Using Subnets: ${SUBNET_ARRAY[@]}"

# Create security group for database
echo "🔒 Creating database security group..."
DB_SG_ID=$(aws ec2 create-security-group \
    --group-name django-db-sg \
    --description "Security group for Django MariaDB database" \
    --vpc-id $DEFAULT_VPC \
    --query "GroupId" \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names django-db-sg \
    --query "SecurityGroups[0].GroupId" \
    --output text)

echo "✅ Database security group: $DB_SG_ID"

# Create security group for web server
echo "🔒 Creating web server security group..."
WEB_SG_ID=$(aws ec2 create-security-group \
    --group-name django-web-sg \
    --description "Security group for Django web server" \
    --vpc-id $DEFAULT_VPC \
    --query "GroupId" \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names django-web-sg \
    --query "SecurityGroups[0].GroupId" \
    --output text)

echo "✅ Web server security group: $WEB_SG_ID"

# Configure security group rules
echo "🔒 Configuring security group rules..."

# Web server rules
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 2>/dev/null || true

# Database rules (allow access from web server)
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG_ID \
    --protocol tcp \
    --port 3306 \
    --source-group $WEB_SG_ID 2>/dev/null || true

# Create DB subnet group
echo "🗄️ Creating RDS subnet group..."
aws rds create-db-subnet-group \
    --db-subnet-group-name django-db-subnet-group \
    --db-subnet-group-description "Subnet group for Django MariaDB" \
    --subnet-ids ${SUBNET_ARRAY[0]} ${SUBNET_ARRAY[1]} 2>/dev/null || \
    echo "✅ DB subnet group already exists"

# Create RDS instance
echo "🗄️ Creating RDS MariaDB instance (this may take 10-15 minutes)..."
RDS_ENDPOINT=$(aws rds create-db-instance \
    --db-instance-identifier django-mariadb \
    --db-instance-class db.t2.micro \
    --engine mariadb \
    --engine-version 10.11.8 \
    --master-username admin \
    --master-user-password "$DB_PASSWORD" \
    --allocated-storage 20 \
    --storage-type gp2 \
    --db-name django_db \
    --vpc-security-group-ids $DB_SG_ID \
    --db-subnet-group-name django-db-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted \
    --no-deletion-protection \
    --query "DBInstance.Endpoint.Address" \
    --output text 2>/dev/null || \
    aws rds describe-db-instances \
    --db-instance-identifier django-mariadb \
    --query "DBInstances[0].Endpoint.Address" \
    --output text)

echo "⏳ Waiting for RDS instance to be available..."
aws rds wait db-instance-available --db-instance-identifier django-mariadb

# Get the latest Ubuntu AMI
echo "🖥️ Getting latest Ubuntu AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
    --output text)

echo "✅ Using AMI: $AMI_ID"

# Launch EC2 instance
echo "🖥️ Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $WEB_SG_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=django-web-server}]' \
    --query "Instances[0].InstanceId" \
    --output text)

echo "⏳ Waiting for EC2 instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query "Reservations[0].Instances[0].PublicIpAddress" \
    --output text)

echo "✅ EC2 Instance launched: $INSTANCE_ID"
echo "✅ Public IP: $PUBLIC_IP"

# Create deployment summary
cat > deployment-info.txt << EOF
🚀 AWS Deployment Information
============================

EC2 Instance:
- Instance ID: $INSTANCE_ID
- Public IP: $PUBLIC_IP
- SSH Key: ~/.ssh/$KEY_NAME
- SSH Command: ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP

RDS Database:
- Endpoint: $RDS_ENDPOINT
- Database: django_db
- Username: admin
- Password: [provided during setup]

Security Groups:
- Web Server: $WEB_SG_ID
- Database: $DB_SG_ID

Next Steps:
1. Wait for RDS to be fully available (check AWS Console)
2. Connect to EC2: ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP
3. Run the deployment script on EC2
4. Configure your domain DNS to point to $PUBLIC_IP

Repository: $REPO_URL
Region: $AWS_REGION
EOF

echo ""
echo "🎉 AWS Infrastructure Setup Complete!"
echo "======================================"
echo ""
echo "📋 Summary saved to: deployment-info.txt"
echo ""
echo "🔗 Next Steps:"
echo "1. Connect to your EC2 instance:"
echo "   ssh -i ~/.ssh/$KEY_NAME ubuntu@$PUBLIC_IP"
echo ""
echo "2. Run the server setup script on EC2:"
echo "   curl -fsSL https://raw.githubusercontent.com/Grupo-TCC/django-app/master/deploy-aws.sh | bash"
echo ""
echo "3. Configure your application with:"
echo "   DB_HOST=$RDS_ENDPOINT"
echo "   DB_PASSWORD=[your-password]"
echo "   AWS_EC2_PUBLIC_IP=$PUBLIC_IP"
echo ""
echo "📞 If you need help, check the AWS_DEPLOYMENT_GUIDE.md file"

# Save RDS endpoint for later use
echo "export RDS_ENDPOINT=$RDS_ENDPOINT" > .aws-deployment-vars
echo "export EC2_PUBLIC_IP=$PUBLIC_IP" >> .aws-deployment-vars
echo "export INSTANCE_ID=$INSTANCE_ID" >> .aws-deployment-vars

echo ""
echo "💾 AWS variables saved to .aws-deployment-vars"
echo "   Source this file later: source .aws-deployment-vars"