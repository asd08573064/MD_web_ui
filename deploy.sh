#!/bin/bash

# Medical Deepfake Labeling App Deployment Script
# This script helps deploy the Streamlit app to AWS

echo "🏥 Medical Deepfake Labeling App - Deployment Script"
echo "=================================================="

# Check if required files exist
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p doctor_labels/CXR doctor_labels/MRI doctor_labels/CT
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 app.py
chmod 755 deploy.sh
chmod -R 777 doctor_labels

# Install dependencies (if not in virtual environment)
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if data directories exist; create skeleton if missing
DATA_ROOT="data"
if [ ! -d "$DATA_ROOT" ]; then
    echo "⚠️  Warning: data directory not found. Creating skeleton structure..."
    mkdir -p "$DATA_ROOT"
fi

for MOD in CXR MRI CT; do
    for ROOT in images reports; do
        for DIFF in easy medium hard; do
            mkdir -p "$DATA_ROOT/$MOD/$ROOT/$DIFF"
        done
    done
done

echo "📂 Ensured data structure exists at data/<modality>/{images,reports}/{easy,medium,hard}"

echo "✅ Deployment preparation complete!"
echo ""
echo "🚀 To run the application:"
echo "   streamlit run app.py"
echo ""
echo "🌐 The app will be available at:"
echo "   http://localhost:8501"
echo ""
echo "📋 For AWS deployment:"
echo "   1. Upload all files to your EC2 instance"
echo "   2. Run this script on the instance"
echo "   3. Use 'streamlit run app.py --server.port 8501 --server.address 0.0.0.0'"
echo "   4. Configure security groups to allow port 8501"
echo ""
echo "🔒 Security Notes:"
echo "   - Each doctor's labels are stored separately"
echo "   - Doctor IDs are hashed for privacy"
echo "   - No database required - file-based storage"
