#!/bin/bash
set -e

echo "Building backend Docker image..."
docker build -t skill-adapter-api ./backend

echo "Building frontend Docker image..."
docker build -t skill-adapter-frontend ./frontend

echo "Build complete!"
echo "Images created:"
echo "  - skill-adapter-api"
echo "  - skill-adapter-frontend"
