#!/bin/bash

echo "📁 Switching to script directory..."
cd "$(dirname "$0")" || exit 1

echo "🧹 Cleaning any existing virtual environment..."
rm -rf venv

echo "🌱 Creating new virtual environment..."
python3 -m venv venv || { echo "❌ Failed to create virtual environment."; exit 1; }

echo "✅ Virtual environment created."

echo "📦 Activating virtual environment and installing requirements..."
source venv/bin/activate

# Upgrade pip and install packages
pip install --upgrade pip
pip install requests beautifulsoup4 pandas

echo "✅ All dependencies installed."

echo ""
echo "🚀 To run the downloader, use:"
echo "source venv/bin/activate && python pdf_downloader.py"
