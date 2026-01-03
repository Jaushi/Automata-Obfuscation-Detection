from flask import Blueprint, jsonify, request
from ..services.dictionary_service import cached_dictionaries, DICTIONARY_FILES
from ..utils.search_utils import search_dictionary
from app.services.detection_service import DetectionService


dictionary_bp = Blueprint('dictionary', __name__)

@dictionary_bp.route('/api/dictionaries', methods=['GET'])
def get_all_dictionaries():
    response_data = {}
    for name, model in cached_dictionaries.items():
        if model.error:
            response_data[name] = {"error": model.error}
        else:
            response_data[name] = {"name": model.name, "data": model.data}
    
    return jsonify({
        'success': True,
        'dictionaries': response_data
    })

@dictionary_bp.route('/api/dictionaries/<dictionary_name>', methods=['GET'])
def get_single_dictionary(dictionary_name):
    if dictionary_name not in DICTIONARY_FILES:
        return jsonify({
            'success': False,
            'error': f'Dictionary not found. Available: {list(DICTIONARY_FILES.keys())}'
        }), 404
    
    model = cached_dictionaries.get(dictionary_name)
    if not model or model.error:
        error_msg = model.error if model else "Not loaded"
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    
    return jsonify({
        'success': True,
        'dictionary_name': model.name,
        'data': model.data
    })

@dictionary_bp.route('/api/netspeak', methods=['GET'])
def get_netspeak():
    model = cached_dictionaries.get('netspeak_patterns')
    if not model or model.error:
        error_msg = model.error if model else "Not loaded"
        return jsonify({'success': False, 'error': error_msg}), 500
    
    query = request.args.get('search', '').strip()
    filtered_data = search_dictionary(model.data, query)
    
    return jsonify({
        'success': True,
        'endpoint': 'netspeak',
        'data': filtered_data
    })

@dictionary_bp.route('/api/leetspeak', methods=['GET'])
def get_leetspeak():
    model = cached_dictionaries.get('leetspeak_map')
    if not model or model.error:
        error_msg = model.error if model else "Not loaded"
        return jsonify({'success': False, 'error': error_msg}), 500
    
    query = request.args.get('search', '').strip()
    filtered_data = search_dictionary(model.data, query)
    
    return jsonify({
        'success': True,
        'endpoint': 'leetspeak',
        'data': filtered_data
    })

@dictionary_bp.route('/api/morphology', methods=['GET'])
def get_morphology():
    model = cached_dictionaries.get('morphology_patterns')
    if not model or model.error:
        error_msg = model.error if model else "Not loaded"
        return jsonify({'success': False, 'error': error_msg}), 500
    
    query = request.args.get('search', '').strip()
    filtered_data = search_dictionary(model.data, query)
    
    return jsonify({
        'success': True,
        'endpoint': 'morphology',
        'data': filtered_data
    })

@dictionary_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'status': 'running',
        'service': 'Filipino Netspeak Dictionary API'
    })