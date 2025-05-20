from flask import Flask, request, jsonify
import requests 
from utils import utils
from utils import vectordb
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

@app.route('/chat', methods=['POST'])
def chat():
    conversation_history = request.json.get('messages')

    db = vectordb.VectorDB()
    util = utils.Utils()
    conversation_with_context = conversation_history

    try:
        last_message = conversation_history[-1]
        last_message_content = last_message["content"]
        query_embedding = util.basic_embedding_generator(last_message_content)
        print("QUERY EMBEDDING")
        retrieved_context = db.get_embedding_from_postgres(query_embedding)
        print("RETRIEVED CONTEXT", retrieved_context)

        if retrieved_context:
            conversation_with_context.append({'role': 'system', 'content': f"Here is some additional context that may help: {retrieved_context}"})
    except Exception as e:
        print(f"Error during context retrieval: {e}")
        return jsonify({'error': str(e)}), 500

    try:
        bot_response = util.basic_chat_completion(conversation_with_context)
        return jsonify({'response': bot_response})
    except Exception as e:
        print(f"Error during chat completion: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
