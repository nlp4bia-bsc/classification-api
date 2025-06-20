from flask import Flask, request, jsonify
from flasgger import Swagger

from app.config.model_config import ModelConfig
from app.models.classifier_baseline import BinaryBERT, PredictionPipeline

app = Flask(__name__)
swagger = Swagger(app)

def get_model():
    config = ModelConfig()
    config.__init__()
    model = BinaryBERT(config)
    pipeline = PredictionPipeline(model, config)
    return pipeline

model = get_model()

@app.route('/process_text', methods=['POST'])
def process_text():
    """
    Process text using the trained classification model
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: text_input
          required:
            - text
          properties:
            text:
              type: string
              description: The text to process
    responses:
      200:
        description: Processed text with classification results
    """
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Input must be a dictionary with 'content' key"}), 400

    if not "content" in data.keys():
        return jsonify({"error": "Input must be a dictionary with 'content' key"}), 400

    data = data["content"]

    text = data.get('text')

    if not text:
        return jsonify({"error": "'text' is required"}), 400

    result = model.predict(text, data.get('footer'))
    return jsonify(result)

@app.route('/process_bulk', methods=['POST'])
def process_bulk():
    """
    Process multiple texts using the trained classification model
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: bulk_input
          type: array
          items:
            type: object
            required:
              - text
            properties:
              text:
                type: string
                description: The text to process
    responses:
      200:
        description: Processed texts with NER annotations
    """
    data = request.json

    if not isinstance(data, dict):
        return jsonify({"error": "Input must be a dictionary with 'content' key"}), 400

    if not "content" in data.keys():
        return jsonify({"error": "Input must be a dictionary with 'content' key"}), 400

    data = data["content"]

    if not isinstance(data, list):
        return jsonify({"error": "Input must be a list of objects"}), 400

    results = []
    for item in data:
        text = item.get('text')

        if not text:
            return jsonify({"error": "Each item must contain 'text'"}), 400

        result = model.predict(text, item.get('footer'))
        results.append(result)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
