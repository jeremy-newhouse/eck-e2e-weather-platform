#!/bin/bash
set -euo pipefail

# Weather Platform -- ECS Fargate Deployment Script
# Usage: ./infra/deploy.sh [REGION] [ACCOUNT_ID]

REGION=${1:-us-east-1}
ACCOUNT_ID=${2:-$(aws sts get-caller-identity --query Account --output text)}
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
BACKEND_REPO="weather-platform-backend"
FRONTEND_REPO="weather-platform-frontend"

echo "Deploying to: ${ECR_REGISTRY}"

# Authenticate to ECR
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Build and push backend
docker build -t "$BACKEND_REPO" ./backend
docker tag "$BACKEND_REPO:latest" "$ECR_REGISTRY/$BACKEND_REPO:latest"
docker push "$ECR_REGISTRY/$BACKEND_REPO:latest"

# Build and push frontend
docker build -t "$FRONTEND_REPO" ./frontend
docker tag "$FRONTEND_REPO:latest" "$ECR_REGISTRY/$FRONTEND_REPO:latest"
docker push "$ECR_REGISTRY/$FRONTEND_REPO:latest"

# Update ECS services
aws ecs update-service \
  --cluster weather-platform \
  --service backend \
  --force-new-deployment \
  --region "$REGION"

aws ecs update-service \
  --cluster weather-platform \
  --service frontend \
  --force-new-deployment \
  --region "$REGION"

echo "Deployment complete. Waiting for stability..."
aws ecs wait services-stable \
  --cluster weather-platform \
  --services backend frontend \
  --region "$REGION"

echo "Services stable. Deployment successful."
