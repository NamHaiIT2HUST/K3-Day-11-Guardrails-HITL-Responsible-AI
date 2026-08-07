import asyncio
import os
from flask import Flask, render_template, request, jsonify

# Import the existing agents from the project
from agents.agent import create_unsafe_agent
from agents.guards_agent import create_guards_agent
from core.utils import chat_with_agent

app = Flask(__name__)

# Initialize agents globally
unsafe_agent, unsafe_runner = create_unsafe_agent()
guards_agent, guards_runner = create_guards_agent()

# Load API key if not loaded
if "GOOGLE_API_KEY" not in os.environ:
    # Use a dummy or instruct user to set it
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    mode = data.get('mode', 'guarded') # 'unsafe' or 'guarded'
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Run async function in a sync route using asyncio.run
        if mode == 'unsafe':
            response, _ = asyncio.run(chat_with_agent(unsafe_agent, unsafe_runner, user_message))
        else:
            response, _ = asyncio.run(chat_with_agent(guards_agent, guards_runner, user_message))
        
        return jsonify({"response": response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Handle Rate limits or model refusals elegantly
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({
                "response": "⚠️ **Lỗi 429 RESOURCE_EXHAUSTED**\n\nGoogle API đã hết hạn mức (Quota exceeded). Vui lòng thử lại sau hoặc chuyển sang API Key khác."
            })
        return jsonify({
            "response": f"⚠️ **Lỗi Hệ Thống**\n\n{error_msg}"
        })

if __name__ == '__main__':
    # Add src to python path so imports work
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    app.run(debug=True, port=5000)
