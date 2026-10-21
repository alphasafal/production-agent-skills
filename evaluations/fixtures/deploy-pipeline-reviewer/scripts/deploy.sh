#!/usr/bin/env bash
# Usage: ./scripts/deploy.sh <image-tag>

TAG="$1"
IMAGE="${ECR_REGISTRY}/orders-api:${TAG}"

echo "Deploying ${IMAGE} to orders-prod"

aws ecs update-service \
  --cluster orders-prod \
  --service orders-api \
  --force-new-deployment \
  --task-definition "$(shipctl render-task --image "${IMAGE}")"

echo "Deploy submitted"
