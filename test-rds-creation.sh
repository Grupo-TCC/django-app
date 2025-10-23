#!/bin/bash

# Simple RDS creation test script
echo "Testing RDS creation..."

aws rds create-db-instance \
    --db-instance-identifier django-test-db \
    --db-instance-class db.t2.micro \
    --engine mariadb \
    --master-username admin \
    --master-user-password 'DjangoPass123!' \
    --allocated-storage 20 \
    --storage-type gp2 \
    --no-deletion-protection

echo "RDS creation command sent. Checking status..."
aws rds describe-db-instances --db-instance-identifier django-test-db --query "DBInstances[0].DBInstanceStatus"