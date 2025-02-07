import os

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
# Model configuration with optimized parameters
MODEL_CONFIG = {
    'openai': {
        'text': {
            'model_name': 'gpt-3.5-turbo',
            'temperature': 0.3,
            'max_tokens': 512,
            'top_p': 0.9
        },
        'reasoning': {
            'model_name': 'gpt-4-turbo',
            'temperature': 0.7,
            'max_tokens': 1024,
            'top_p': 1.0
        }
    },
    'gemini': {
        'text': {
            'model_name': 'gemini-2.0-flash',
            'temperature': 0.3,
            'max_tokens': 2048
        },
        'reasoning': {
            'model_name': 'gemini-pro',
            'temperature': 0.7,
            'max_tokens': 4096
        }
    }
}