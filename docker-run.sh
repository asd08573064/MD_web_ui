#!/bin/bash

# Medical Deepfake Labeling App - Docker Run Script
# This script helps run the application using Docker

echo "🏥 Medical Deepfake Labeling App - Docker Setup"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if required data directories exist
if [ ! -d "out_scm_tts" ]; then
    echo "⚠️  Warning: out_scm_tts directory not found!"
    echo "   Please ensure your image data is in the correct location."
fi

if [ ! -d "out_scm_tts_ehr" ]; then
    echo "⚠️  Warning: out_scm_tts_ehr directory not found!"
    echo "   Please ensure your EHR data is in the correct location."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p doctor_labels logs

# Build and run with Docker Compose
echo "🐳 Building and starting the application..."
docker-compose up --build -d

# Wait a moment for the container to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Application is running!"
    echo ""
    echo "🌐 Access the application at:"
    echo "   http://localhost:8501"
    echo ""
    echo "📋 To view authorized doctor IDs:"
    echo "   docker-compose exec medical-labeling-app python show_doctor_ids.py"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop the application:"
    echo "   docker-compose down"
    echo ""
    echo "🔄 To restart:"
    echo "   docker-compose restart"
else
    echo "❌ Failed to start the application!"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
