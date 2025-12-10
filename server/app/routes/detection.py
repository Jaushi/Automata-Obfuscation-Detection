from flask import request, jsonify
from app.routes import api_bp
from app.services.detection_service import DetectionService

detection_service = DetectionService()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Automata Obfuscation Detection API is running'
    }), 200

@api_bp.route('/detect', methods=['POST'])
def detect_obfuscation():
    """Detect obfuscation in provided code"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'error': 'Code is required'
            }), 400
        
        code = data['code']
        language = data.get('language', 'unknown')
        
        result = detection_service.analyze(code, language)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
