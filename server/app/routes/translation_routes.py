from flask import Blueprint, request, jsonify
from ..services.translation_service import process_and_translate

translation_bp = Blueprint('translation', __name__)

@translation_bp.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'No text provided'}), 400
    
    original_text = data['text']
    translated_text = process_and_translate(original_text)
    
    return jsonify({
        'success': True,
        'original': original_text,
        'translated': translated_text
    })