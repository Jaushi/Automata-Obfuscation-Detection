from flask import Blueprint, jsonify, request
from app.services.detection_service import DetectionService
from app.services.deobfuscation_service import DeobfuscationService
from app.services.analysis_service import AnalysisService
from app.services.translation_service import translate_to_clean_text

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/detect', methods=['POST'])
def detect_obfuscation():
    # Detect obfuscation patterns using finite automata
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
    # Deobfuscate text with fuzzy matching
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
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        text = data['text']
        language = data.get('language', 'unknown')
        use_fuzzy = data.get('use_fuzzy', True)
        
        # Step 1: Analyze and deobfuscate
        analysis_service = AnalysisService()
        result = analysis_service.analyze(text, language, use_fuzzy)
        
        # Step 2: Translate deobfuscated text to clean final output
        from app.services.translation_service import translate_to_clean_text
        result['deobfuscated'] = translate_to_clean_text(result['deobfuscated'])
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in /api/analyze: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500