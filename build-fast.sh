#!/bin/bash

# Fast Docker build script with BuildKit
# Usage: ./build-fast.sh [--multi-stage] [--no-cache]

set -e

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Parse arguments
MULTI_STAGE=false
NO_CACHE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --multi-stage)
            MULTI_STAGE=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--multi-stage] [--no-cache]"
            exit 1
            ;;
    esac
done

echo "🚀 Starting fast Docker build..."
echo "BuildKit enabled: $DOCKER_BUILDKIT"
echo "Multi-stage build: $MULTI_STAGE"
echo "No cache: $NO_CACHE"

# Choose Dockerfile based on arguments
if [ "$MULTI_STAGE" = true ]; then
    echo "📦 Using multi-stage Dockerfile.backend.optimized"
    cp Dockerfile.backend.optimized Dockerfile.backend.temp
else
    echo "📦 Using optimized single-stage Dockerfile.backend"
fi

# Build with BuildKit
echo "🔨 Building containers..."
docker-compose build $NO_CACHE --parallel

# Clean up temp file if used
if [ "$MULTI_STAGE" = true ]; then
    rm -f Dockerfile.backend.temp
fi

echo "✅ Build completed successfully!"
echo "🚀 Starting containers..."
docker-compose up -d

echo "🎉 All done! Your Bug Bounty Platform is running."
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🌺 Flower (Celery): http://localhost:5555" 