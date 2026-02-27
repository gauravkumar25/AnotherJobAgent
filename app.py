#!/usr/bin/env python3
"""
Flask backend for Career Agents UI
Securely handles API key from environment variables and proxies requests to xAI
"""

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize xAI client
XAI_API_KEY = os.environ.get("XAI_API_KEY")

if not XAI_API_KEY:
    print("⚠️  WARNING: XAI_API_KEY not found in environment variables!")
    print("   Set it with: export XAI_API_KEY='your-key-here'")

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
) if XAI_API_KEY else None


@app.route('/')
def index():
    """Serve the main HTML UI"""
    return send_file('career_agents_ui.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Proxy endpoint for xAI chat completions
    Keeps the API key secure on the server
    """
    if not client:
        return jsonify({
            'error': {
                'message': 'XAI_API_KEY not configured on server. Please set the environment variable.'
            }
        }), 500

    try:
        data = request.json

        # Extract request parameters
        model = data.get('model', 'grok-beta')
        messages = data.get('messages', [])
        max_tokens = data.get('max_tokens', 2000)
        temperature = data.get('temperature', 0.7)

        # Make request to xAI
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Return response in OpenAI format
        return jsonify({
            'choices': [
                {
                    'message': {
                        'role': 'assistant',
                        'content': response.choices[0].message.content
                    }
                }
            ]
        })

    except Exception as e:
        return jsonify({
            'error': {
                'message': str(e)
            }
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'api_key_configured': bool(XAI_API_KEY)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Career Agents UI Server")
    print(f"   → Running on http://localhost:{port}")
    print(f"   → API Key configured: {bool(XAI_API_KEY)}")
    print(f"\n   Press Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=port, debug=True)
