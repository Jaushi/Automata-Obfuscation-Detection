from flask import Blueprint, jsonify, request
from app.services.detection_service import DetectionService

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/detect/fuzzy', methods=['POST'])
def detect_with_fuzzy():
    """Enhanced detection with fuzzy matching"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
    
    text = data['text']
    threshold = data.get('threshold', 75)
    
    detection_service = DetectionService()
    detection_service.fuzzy_matching_service.threshold = threshold
    
    result = detection_service.detect_with_fuzzy(text)
    
    return jsonify({
        'success': True,
        **result
    })

@api_bp.route('/api/detect', methods=['POST'])
def detect_obfuscation():
    """Standard code obfuscation detection"""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({
            'success': False,
            'error': 'No code provided'
        }), 400
    
    code = data['code']
    language = data.get('language', 'unknown')
    
    detection_service = DetectionService()
    result = detection_service.analyze(code, language)
    
    return jsonify({
        'success': True,
        **result
    })
