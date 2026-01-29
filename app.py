from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# ---------------- CONFIGURAÇÃO ----------------
openai.api_key = os.environ.get("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente!")

# ---------------- FLASK API ----------------
app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Armazena históricos por sessão (em produção, use Redis ou banco de dados)
sessions = {}

def generate_chatgpt_response(prompt, conversation_history=None):
    system_prompt = """
    You are an experienced, patient, and motivating English teacher.
    Your goal is to help the student practice English conversation about any topic they choose,
    including hobbies, studies, work, and daily life.

    Rules:
    1. Always respond in English. Do not use Portuguese or any other language.
    2. Encourage the student to write or speak short sentences.
    3. Ask open-ended questions so the student can choose the topic of conversation.
    4. Correct mistakes ONLY if the student explicitly asks for correction (e.g., "Can you correct me?").
    5. Be patient, encouraging, and praise the student's progress.
    6. Introduce new vocabulary and expressions naturally during the conversation.
    7. use answers between 5 and 10 words.
    8. start the conversation with a question related to daily life: hobbies, studies, work, and daily routines.
    """

    if conversation_history is None:
        conversation_history = []

    messages = [{"role": "system", "content": system_prompt}]
    messages += conversation_history
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

# ---------------- ENDPOINTS DA API ----------------

@app.route("/", methods=["GET"])
def index():
    """Servir o frontend estático"""
    return send_from_directory(".", "frontend.html")

@app.route("/api/health", methods=["GET"])
def health():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({"status": "ok", "message": "API is running"})

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint principal para chat
    Body: {
        "message": "Hello",
        "session_id": "user123" (opcional)
    }
    """
    try:
        data = request.json
        user_input = data.get("message")
        session_id = data.get("session_id", "default")
        
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
        
        # Recupera ou cria histórico da sessão
        if session_id not in sessions:
            sessions[session_id] = []
        
        conversation_history = sessions[session_id]
        
        # Gera resposta
        reply = generate_chatgpt_response(user_input, conversation_history)
        
        # Atualiza histórico
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": reply})
        sessions[session_id] = conversation_history
        
        return jsonify({
            "reply": reply,
            "session_id": session_id,
            "history_length": len(conversation_history)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def reset():
    """
    Reinicia o histórico de conversa
    Body: {"session_id": "user123"}
    """
    data = request.json
    session_id = data.get("session_id", "default")
    
    if session_id in sessions:
        sessions[session_id] = []
    
    return jsonify({"message": "Session reset", "session_id": session_id})

@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Retorna o histórico de conversa
    Query: ?session_id=user123
    """
    session_id = request.args.get("session_id", "default")
    history = sessions.get(session_id, [])
    
    return jsonify({
        "session_id": session_id,
        "history": history,
        "message_count": len(history)
    })

if __name__ == "__main__":
    # Configuração para desenvolvimento
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
