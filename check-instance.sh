#!/bin/bash

# Quick script to check AWS EC2 instance status and get current IP
# Usage: ./check-instance.sh

source .aws-deployment-vars

echo "🔍 Checking InnovaSus deployment status..."
echo "Instance ID: $EC2_INSTANCE_ID"
echo "Last known IP: $EC2_PUBLIC_IP"
echo ""

echo "📡 Checking instance status..."
aws ec2 describe-instances \
    --region $AWS_REGION \
    --instance-ids $EC2_INSTANCE_ID \
    --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,PrivateIpAddress]' \
    --output table

echo ""
echo "🔧 Getting current public IP..."
CURRENT_IP=$(aws ec2 describe-instances \
    --region $AWS_REGION \
    --instance-ids $EC2_INSTANCE_ID \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text)

if [ "$CURRENT_IP" != "None" ] && [ ! -z "$CURRENT_IP" ]; then
    echo "✅ Current IP: $CURRENT_IP"
    
    if [ "$CURRENT_IP" != "$EC2_PUBLIC_IP" ]; then
        echo "⚠️  IP has changed! Updating deployment vars..."
        sed -i.bak "s/EC2_PUBLIC_IP=\".*\"/EC2_PUBLIC_IP=\"$CURRENT_IP\"/" .aws-deployment-vars
        echo "Updated .aws-deployment-vars with new IP: $CURRENT_IP"
    fi
    
    echo ""
    echo "🌐 Testing InnovaSus site connectivity..."
    if curl -s --connect-timeout 10 "http://$CURRENT_IP/" > /dev/null; then
        echo "✅ InnovaSus site is accessible at: http://$CURRENT_IP/"
    else
        echo "❌ Site not responding. May need to start services."
    fi
else
    echo "❌ Instance appears to be stopped or terminated"
    echo "💡 Would you like to start it or create a new deployment?"
fi