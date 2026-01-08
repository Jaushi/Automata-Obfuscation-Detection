from flask import Blueprint, jsonify, request
from app.services.analysis_service import AnalysisService

api_bp = Blueprint('api', __name__)

# Initialize service once to avoid recreating on every request
_analysis_service = None

def get_analysis_service():
    """Get or create analysis service (lazy initialization)."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'success': True, 'status': 'healthy'}), 200


@api_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Full analysis: detect obfuscation and deobfuscate text. 
    Request:
        {
            "text": "k_m_s_t_a p@ss",
            "language": "unknown",
            "use_fuzzy": true
        }
    
    Response:
        {
            "success": true,
            "original": "k_m_s_t_a p@ss",
            "deobfuscated": "kumusta pass",
            "is_obfuscated": true,
            "confidence": 0.85,
            "obfuscation_types": ["symbol_separation", "leetspeak"],
            "transformations": [...],
            "status": "obfuscated"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'success': False, 'error': 'Text is empty'}), 400
        
        language = data.get('language', 'unknown')
        use_fuzzy = data.get('use_fuzzy', True)
        
        service = get_analysis_service()
        result = service.analyze(text, language, use_fuzzy)
        
        return jsonify({
            'success': True,
            'original': result['original'],
            'deobfuscated': result['deobfuscated'],
            'is_obfuscated': result['detection'].get('isObfuscated', False),
            'confidence': result['detection'].get('confidence', 0.0),
            'obfuscation_types': result['obfuscation_types'],
            'transformations': result.get('transformations', []),
            'status': result['detection'].get('status', 'unknown')
        }), 200
    
    except Exception as e:
        import traceback
        print(f"[ERROR] /api/analyze: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/detect', methods=['POST'])
def detect():
    """
    Detect obfuscation patterns only (no deobfuscation).
    
    Request:
        {
            "text": "k_m_s_t_a p@ss",
            "language": "unknown"
        }
    
    Response:
        {
            "success": true,
            "is_obfuscated": true,
            "confidence": 0.85,
            "patterns": ["symbol_separation", "leetspeak"],
            "signals": {...},
            "status": "obfuscated"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'success': False, 'error': 'Text is empty'}), 400
        
        language = data.get('language', 'unknown')
        
        service = get_analysis_service()
        detection_result = service.detector.analyze(text, language)
        
        return jsonify({
            'success': True,
            'is_obfuscated': detection_result.get('isObfuscated', False),
            'confidence': detection_result.get('confidence', 0.0),
            'patterns': detection_result.get('patterns', []),
            'signals': detection_result.get('detected_signals', {}),
            'status': detection_result.get('status', 'unknown')
        }), 200
    
    except Exception as e:
        print(f"[ERROR] /api/detect: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/deobfuscate', methods=['POST'])
def deobfuscate():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'success': False, 'error': 'Text is empty'}), 400
        
        use_fuzzy = data.get('use_fuzzy', True)
        
        service = get_analysis_service()
        deobfuscated, transformations = service._deobfuscate(text, use_fuzzy)
        
        return jsonify({
            'success': True,
            'original': text,
            'deobfuscated': deobfuscated,
            'transformations': transformations
        }), 200
    
    except Exception as e:
        print(f"[ERROR] /api/deobfuscate: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500