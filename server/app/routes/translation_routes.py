from flask import Blueprint, request, jsonify
from ..services.analysis_service import AnalysisService
from ..services.translation_service import translate_to_clean_text

translation_bp = Blueprint('translation', __name__)

# Singleton instance to avoid recreating on every request
_analysis_service = None

def get_analysis_service():
    """Get or create analysis service."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


@translation_bp.route('/api/translate', methods=['POST'])
def translate():
    """
    Translate/deobfuscate text.
    
    Request:
        {
            "text": "k_m_s_t_a p@ss",
            "use_fuzzy": true
        }
    
    Response:
        {
            "success": true,
            "original": "k_m_s_t_a p@ss",
            "translated": "kumusta pass"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        original_text = data['text'].strip()
        if not original_text:
            return jsonify({'success': False, 'error': 'Text is empty'}), 400
        
        use_fuzzy = data.get('use_fuzzy', True)
        
        # Use analysis service for full pipeline
        service = get_analysis_service()
        result = service.analyze(original_text, use_fuzzy=use_fuzzy)
        
        return jsonify({
            'success': True,
            'original': result['original'],
            'translated': result['deobfuscated']
        }), 200
    
    except Exception as e:
        print(f"[ERROR] /api/translate: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500