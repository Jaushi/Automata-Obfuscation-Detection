from flask import Blueprint, jsonify, request
from app.services.detection_service import DetectionService
from app.services.deobfuscation_service import DeobfuscationService

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/detect', methods=['POST'])
def detect_obfuscation():
    # Standard obfuscation detection using finite automata
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400

    text = data['text']
    language = data.get('language', 'unknown')

    try:
        detection_service = DetectionService()
        result = detection_service.analyze(text, language)

        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/deobfuscate', methods=['POST'])
def deobfuscate_text():
    # Deobfuscate text with optional fuzzy matching
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400

    text = data['text']
    use_fuzzy = data.get('use_fuzzy', True)

    try:
        deobfuscation_service = DeobfuscationService()
        deobfuscated = deobfuscation_service.deobfuscate_text(text, use_fuzzy=use_fuzzy)

        return jsonify({
            'success': True,
            'original': text,
            'deobfuscated': deobfuscated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/analyze', methods=['POST'])
def analyze_full():
    # Complete pipeline: detect obfuscation + deobfuscate
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400

    text = data['text']
    language = data.get('language', 'unknown')
    use_fuzzy = data.get('use_fuzzy', True)

    try:
        # Step 1: Detect obfuscation
        detection_service = DetectionService()
        detection_result = detection_service.analyze(text, language)

        # Step 2: Deobfuscate if obfuscation detected
        deobfuscated = text
        if detection_result.get('isObfuscated'):
            deobfuscation_service = DeobfuscationService()
            deobfuscated = deobfuscation_service.deobfuscate_text(text, use_fuzzy=use_fuzzy)

        return jsonify({
            'success': True,
            'original': text,
            'deobfuscated': deobfuscated,
            'detection': detection_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500