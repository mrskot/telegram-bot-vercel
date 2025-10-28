import os
from supabase import create_client, Client
import logging

class SupabaseService:
    def __init__(self):
        self.url: str = os.getenv('SUPABASE_URL')
        self.key: str = os.getenv('SUPABASE_SERVICE_KEY')
        if not self.url or not self.key:
            logging.error("❌ Supabase credentials not set")
            raise ValueError("Supabase credentials not set")
        
        self.supabase: Client = create_client(self.url, self.key)
        logging.info("✅ Supabase client initialized")
    
    def create_session(self, chat_id: int, extracted_data: str = None):
        try:
            data = {
                'chat_id': chat_id,
                'extracted_data': extracted_data,
                'parsed_data': {
                    'Участок': 'не указано',
                    'Изделие': 'не указано',
                    'Номер чертежа': 'не указано', 
                    'Номер изделия': 'не указано'
                },
                'status': 'pending_verification'
            }
            
            result = self.supabase.table('sessions').insert(data).execute()
            if result.data:
                logging.info(f"✅ Session created: {result.data[0]['id']}")
                return result.data[0]
            return None
            
        except Exception as e:
            logging.error(f"❌ Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str):
        try:
            result = self.supabase.table('sessions').select('*').eq('id', session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"❌ Error getting session: {e}")
            return None
    
    def update_session(self, session_id: str, updates: dict):
        try:
            updates['updated_at'] = 'now()'
            result = self.supabase.table('sessions').update(updates).eq('id', session_id).execute()
            if result.data:
                logging.info(f"✅ Session updated: {session_id}")
                return result.data[0]
            return None
        except Exception as e:
            logging.error(f"❌ Error updating session: {e}")
            return None
    
    def delete_session(self, session_id: str):
        try:
            result = self.supabase.table('sessions').delete().eq('id', session_id).execute()
            logging.info(f"✅ Session deleted: {session_id}")
            return True
        except Exception as e:
            logging.error(f"❌ Error deleting session: {e}")
            return False
    
    def upload_file(self, file_content: bytes, file_path: str, bucket: str = 'documents'):
        try:
            result = self.supabase.storage.from_(bucket).upload(file_path, file_content)
            return result if not result.get('error') else None
        except Exception as e:
            logging.error(f"❌ Error uploading file: {e}")
            return None
    
    def get_file_url(self, file_path: str, bucket: str = 'documents'):
        try:
            result = self.supabase.storage.from_(bucket).get_public_url(file_path)
            return result
        except Exception as e:
            logging.error(f"❌ Error getting file URL: {e}")
            return None

supabase_client = SupabaseService()
