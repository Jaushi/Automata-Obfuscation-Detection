import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from server.app import app 
    from server.app.services.dictionary_service import load_and_cache_dictionaries, DICTIONARY_FILES
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"Import error: {e}. Ensure you're running from the project root and __init__.py files exist.")
    sys.exit(1)

if __name__ == '__main__':
    os.makedirs('server/app/dictionaries', exist_ok=True)
    load_and_cache_dictionaries()
    
    for name, file_path in DICTIONARY_FILES.items():
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Create this file with your dictionary data.")
    
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', 
            port=int(os.environ.get('PORT', 5000)), 
            host=os.environ.get('HOST', '0.0.0.0'))