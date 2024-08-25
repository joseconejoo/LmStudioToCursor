from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI
import json

app = Flask(__name__)
CORS(app)

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

@app.route('/chat/completions', methods=['POST'])
def chat_endpoint():
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', 'lmstudio-ai/gemma-2b-it-GGUF')

    def generate():
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    response = Response(generate(), content_type='text/event-stream')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/models', methods=['GET'])
def get_models():
    # Aquí puedes implementar la lógica para obtener los modelos
    # Por ahora, solo devolveremos una respuesta de ejemplo
    models = ["modelo1", "modelo2", "modelo3"]
    return jsonify(models)

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run_server()