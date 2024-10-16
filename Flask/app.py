from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import uuid
import datetime

load_dotenv()

app = Flask(__name__)

# Configure server-side session
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# In-memory storage for simplicity (use a database for production)
conversations = {}
summaries = {}

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/set_objective', methods=['POST'])
def set_objective():
    data = request.get_json()
    objective = data.get('objective')
    target_language = data.get('target_language')
    user_language = data.get('user_language')
    country = data.get('country')

    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    conversations[session_id] = []
    summaries[session_id] = ""

    # Initialize conversation with the objective
    conversations[session_id].append({
        'role': 'system',
        'content': f"Objective set to: {objective} | Target Language: {target_language} | User Language: {user_language} | Country: {country}"
    })

    return jsonify({
        'session_id': session_id,
        'message': 'Objective set successfully.'
    })


@app.route('/send_message/<session_id>', methods=['POST'])
def send_message(session_id):
    if session_id not in conversations:
        return jsonify({'error': 'Invalid session ID.'}), 400

    data = request.get_json()
    message = data.get('message')

    # Append user message
    conversations[session_id].append({
        'role': 'user',
        'content': message
    })

    # Here, integrate with your backend AI or processing logic
    # For demonstration, we'll echo the message
    assistant_response = f"[USER] You said: {message}"

    # Append assistant response
    conversations[session_id].append({
        'role': 'assistant',
        'content': assistant_response
    })

    return jsonify({
        'assistant_response': assistant_response,
        'history': conversations[session_id],
        'summary': summaries.get(session_id, "")
    })


@app.route('/process_audio/<session_id>', methods=['POST'])
def process_audio(session_id):
    if session_id not in conversations:
        return jsonify({'error': 'Invalid session ID.'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file part.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Here, integrate with your audio processing (e.g., speech-to-text)
        # For demonstration, we'll assume the audio translates to "Hello World"
        user_text = "Hello World"

        # Append user message
        conversations[session_id].append({
            'role': 'user',
            'content': user_text
        })

        # Generate assistant response
        assistant_response = f"[TARGET] Translated Text: {user_text} in target language."

        # Append assistant response
        conversations[session_id].append({
            'role': 'assistant',
            'content': assistant_response
        })

        return jsonify({
            'user_text': user_text,
            'assistant_response': assistant_response,
            'summary': summaries.get(session_id, "")
        })
    else:
        return jsonify({'error': 'Unsupported file type.'}), 400


@app.route('/history/<session_id>', methods=['GET', 'DELETE'])
def history(session_id):
    if session_id not in conversations:
        return jsonify({'error': 'Invalid session ID.'}), 400

    if request.method == 'GET':
        history_list = []
        for idx, item in enumerate(conversations[session_id]):
            history_list.append({
                'id': idx,
                'role': item['role'],
                'content': item['content'],
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({'history': history_list})

    elif request.method == 'DELETE':
        data = request.get_json()
        message_id = data.get('id')
        if message_id is not None and 0 <= message_id < len(conversations[session_id]):
            del conversations[session_id][message_id]
            return jsonify({'message': 'Message deleted successfully.'})
        else:
            return jsonify({'error': 'Invalid message ID.'}), 400


@app.route('/summary/<session_id>', methods=['GET'])
def get_summary(session_id):
    if session_id not in summaries:
        return jsonify({'error': 'Invalid session ID.'}), 400

    summary = summaries.get(session_id, "No summary available.")
    return jsonify({'summary': summary})


@app.route('/synthesize_text', methods=['POST'])
def synthesize_text():
    data = request.get_json()
    text = data.get('text')
    language = data.get('language')

    # Integrate with a TTS service here
    # For demonstration, we'll return a placeholder URL or binary data
    # In production, return the actual audio file or stream

    # Example response
    return jsonify({
        'audio_url': 'http://example.com/audio.mp3'  # Replace with actual audio URL
    })


@app.route('/translate', methods=['GET'])
def translate():
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('home'))
    return render_template('translate.html', session_id=session_id)


@app.route('/history_page', methods=['GET'])
def history_page():
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('home'))
    return render_template('history.html', session_id=session_id)


if __name__ == '__main__':
    app.run(debug=True)
