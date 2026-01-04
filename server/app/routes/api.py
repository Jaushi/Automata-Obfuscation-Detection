from flask import Blueprint, jsonify, request
from app.services.detection_service import DetectionService
from app.services.deobfuscation_service import DeobfuscationService
from app.services.translation_service import translate_to_clean_text
from app.services.preprocessing_service import word_tokenize, normalize_input

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
        
        # Step 1: Detect obfuscation signals
        detector = DetectionService()
        analysis = detector.analyze(text, language)
        
        print(f"\n[DEBUG] Input: {text[:50]}...")
        print(f"[DEBUG] Detected Signals: {analysis['detected_signals']}")
        print(f"[DEBUG] Is Obfuscated: {analysis['isObfuscated']}")
        
        # DEBUG: Check abbreviation detection
        print(f"\n[DEBUG ABBREV]")
        print(f"  Abbreviation map size: {len(detector.abbreviation.single_abbrevs)}")
        print(f"  'btw' in abbrevs: {'btw' in detector.abbreviation.single_abbrevs}")
        print(f"  'hbd' in abbrevs: {'hbd' in detector.abbreviation.single_abbrevs}")
        print(f"  'omg' in abbrevs: {'omg' in detector.abbreviation.single_abbrevs}")

        # Tokenize to see what tokens are being checked
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        print(f"  First 10 tokens: {tokens[:10]}")

        for token in tokens[:10]:
            cleaned = token.lower().strip('.,!?;:()[]{}"\'-')
            is_abbrev = detector.abbreviation.detect_single(cleaned)
            print(f"    '{token}' -> '{cleaned}': {is_abbrev}")
        
        # Step 2: Deobfuscate with signals
        deobfuscator = DeobfuscationService()
        
        # Tokenize and deobfuscate each token with its signals
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        
        deobfuscated_tokens = []
        for token in tokens:
            corrected = deobfuscator.deobfuscate(token, use_fuzzy=use_fuzzy, signals=analysis['detected_signals'])
            deobfuscated_tokens.append(corrected)
        
        deobfuscated = " ".join(deobfuscated_tokens)
        
        print(f"[DEBUG] Deobfuscated: {deobfuscated[:50]}...\n")
        
        # Step 3: Translate to clean output
        final_output = translate_to_clean_text(deobfuscated)
        
        return jsonify({
            'success': True,
            'original': text,
            'deobfuscated': deobfuscated,
            'final': final_output,
            'analysis': analysis
        })
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in /api/analyze: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500