import os
import json
import openai
import google.generativeai as genai
from snowflake.connector import DictCursor
from snowflake_connection import create_snowflake_connector_connection
from config import MODEL_CONFIG

def get_model_config(provider, model_type):
    """Get optimized model parameters based on provider and type"""
    config = MODEL_CONFIG.get(provider, {}).get(model_type)
    if not config:
        raise ValueError(f"Unsupported provider/type: {provider}/{model_type}")
    return config

def call_ai_api(provider, formatted_prompt, config):
    """Generic API caller with provider-specific handling"""
    try:
        if provider == 'openai':
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=config['model_name'],
                messages=[{
                    "role": "system", 
                    "content": "You are an expert at comparative analysis."
                }, {
                    "role": "user", 
                    "content": formatted_prompt
                }],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                top_p=config.get('top_p', 1.0)
            )
            return response.choices[0].message.content.strip()
            
        elif provider == 'gemini':
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(config['model_name'])
            response = model.generate_content(
                formatted_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config['temperature'],
                    max_output_tokens=config['max_tokens'],
                    top_p=config.get('top_p', 1.0)
                )
            )
            return response.text.strip()
            
    except Exception as e:
        raise RuntimeError(f"{provider.upper()} API error: {str(e)}")

def process_evaluation(task_id, provider, model_type):
    """Main processing function with multi-provider support"""
    conn = None
    try:
        # Get model configuration
        config = get_model_config(provider, model_type)
        
        # Snowflake setup
        # conn = get_snowflake_connection()
        conn = create_snowflake_connector_connection()
        with conn.cursor(DictCursor) as cursor:
            # Fetch task data
            cursor.execute(f"""
                SELECT LEFT_RESPONSE, RIGHT_RESPONSE, FINAL_USER_QUESTION, PROJECT_ID
                FROM {os.getenv('PAIRWISE_EVALUATION_TABLE')}
                WHERE TASK_ID = %s
            """, (task_id,))
            
            task_data = cursor.fetchone()
            if not task_data:
                return {"error": f"Task {task_id} not found"}
                
            # Validate and format data
            final_question = task_data['FINAL_USER_QUESTION']
            if isinstance(final_question, dict):
                final_question = json.dumps(final_question)
                
            # Get prompt template
            cursor.execute(f"""
                SELECT TEMPLATE_CONTENT
                FROM {os.getenv('PROMPT_TEMPLATES_TABLE')}
                WHERE PROJECT_ID = %s AND IS_ACTIVE = TRUE
                LIMIT 1
            """, (task_data['PROJECT_ID'],))
            
            template = cursor.fetchone()
            if not template:
                return {"error": "No active template found"}
                
            # Format prompt
            formatted_prompt = template['TEMPLATE_CONTENT'].format(
                left_response=task_data['LEFT_RESPONSE'],
                right_response=task_data['RIGHT_RESPONSE'],
                user_question=final_question
            )
            
            # Get AI response
            ai_response = call_ai_api(provider, formatted_prompt, config)
            
            # Update database
            cursor.execute(f"""
                UPDATE {os.getenv('PAIRWISE_EVALUATION_TABLE')}
                SET {provider.upper()}_RESPONSE = %s
                WHERE TASK_ID = %s
            """, (ai_response, task_id))
            
            conn.commit()
            return {"status": "success", "response": ai_response}

    except KeyError as e:
        return {"error": f"Template formatting error: {str(e)}"}
    except Exception as e:
        conn.rollback() if conn else None
        return {"error": str(e)}
    finally:
        if conn: conn.close()