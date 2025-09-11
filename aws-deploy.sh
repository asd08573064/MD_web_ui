#!/bin/bash

# Medical Deepfake Labeling App - AWS Deployment Script
# This script helps deploy the Docker application to AWS EC2

echo "🏥 Medical Deepfake Labeling App - AWS Deployment"
echo "==============================================="

# Check if required files exist
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found!"
    exit 1
fi

if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found!"
    exit 1
fi

# Check if data directories exist
if [ ! -d "out_scm_tts" ]; then
    echo "⚠️  Warning: out_scm_tts directory not found!"
    echo "   Please ensure your image data is uploaded to the EC2 instance."
fi

if [ ! -d "out_scm_tts_ehr" ]; then
    echo "⚠️  Warning: out_scm_tts_ehr directory not found!"
    echo "   Please ensure your EHR data is uploaded to the EC2 instance."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p doctor_labels logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 doctor_labels
chmod 755 logs

# Build and run with production Docker Compose
echo "🐳 Building and starting the production application..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for the container to start
echo "⏳ Waiting for application to start..."
sleep 15

# Check if container is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Application is running in production mode!"
    echo ""
    echo "🌐 Application should be accessible at:"
    echo "   http://YOUR_EC2_PUBLIC_IP:8501"
    echo ""
    echo "📋 To view authorized doctor IDs:"
    echo "   docker-compose -f docker-compose.prod.yml exec medical-labeling-app python show_doctor_ids.py"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "🛑 To stop the application:"
    echo "   docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "🔒 Security Notes:"
    echo "   - Ensure EC2 security group allows port 8501"
    echo "   - Consider using HTTPS with a reverse proxy"
    echo "   - Monitor logs regularly"
    echo "   - Backup doctor_labels directory regularly"
else
    echo "❌ Failed to start the application!"
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi
