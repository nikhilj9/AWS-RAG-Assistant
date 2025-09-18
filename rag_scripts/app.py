import argparse
import uuid
from flask import Flask, request, jsonify
from rag import RAGPipeline

app = Flask(__name__)
rag_pipeline = None  # Global variable to store the pipeline instance

@app.route("/question", methods=["POST"])
def handle_question():
    data = request.json
    question = data["question"]

    if not question:
        return jsonify({"error": "No question provided"}), 400

    conversation_id = str(uuid.uuid4())
    answer = rag_pipeline.rag(question)  # Use the instance, not the class

    result = {
        "conversation_id": conversation_id,
        "question": question,
        "answer": answer,
    }

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    return jsonify(result)

@app.route("/feedback", methods=["POST"])
def handle_feedback():
    data = request.json
    conversation_id = data["conversation_id"]
    feedback = data["feedback"]

    if not conversation_id or feedback not in [1, -1]:
        return jsonify({"error": "Invalid input"}), 400

    result = {
        "message": f"Feedback received for conversation {conversation_id}: {feedback}"
    }
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "provider": rag_pipeline.provider})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RAG Pipeline Server')
    parser.add_argument('--provider', choices=['bedrock', 'openai'], required=True,
                       help='LLM provider to use (bedrock or openai)')
    args = parser.parse_args()
    
    rag_pipeline = RAGPipeline(provider=args.provider)  # Create instance
    app.run(debug=False, host='0.0.0.0', port=5000)  # Changed for Docker