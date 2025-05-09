from pydantic import BaseModel

class CancelChatRequest(BaseModel):
    chat_session_id: str
    
    model_config = {
        "json_schema_extra":{
            'examples':{
                'chat_session_id':'123'
            }
        }
    }