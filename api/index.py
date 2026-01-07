"""
Vercel Serverless Function Entry Point
This wraps the Flask app for Vercel deployment
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

# Vercel expects a handler function
def handler(request, context):
    return app(request, context)

# For Vercel
app = app
