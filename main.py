from flask import Flask, request, jsonify
from service.pairwise_ai import process_evaluation
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/ai', methods=['POST'])
def evaluate_pairwise():
    """
    Enhanced endpoint supporting multiple AI providers and model types
    post request parameters:
                            task_id
                            ai_model
                            model_type
    
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        task_id = data.get('task_id')
        ai_model = data.get('ai_model', 'openai').lower()
        model_type = data.get('model_type', 'text').lower()

        # Validate input
        if not isinstance(task_id, int):
            return jsonify({"error": "Valid integer Task ID required"}), 400
            
        valid_models = ['openai', 'gemini']
        if ai_model not in valid_models:
            return jsonify({"error": f"Supported models: {', '.join(valid_models)}"}), 400

        # Process evaluation
        result = process_evaluation(
            task_id=task_id,
            provider=ai_model,
            model_type=model_type
        )

        return jsonify(result) if 'error' not in result else jsonify(result), 500

    except Exception as e:
        app.logger.error(f"Request processing error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=app.config['DEBUG'])