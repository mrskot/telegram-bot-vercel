import requests
import os
import logging
from lib.supabase_client import supabase_client

class TelegramService:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logging.error("❌ Telegram token not set")
            raise ValueError("Telegram token not set")
        
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        logging.info("✅ Telegram service initialized")
    
    def download_and_store_file(self, file_id: str, session_id: str):
        try:
            file_info_url = f"{self.api_url}/getFile"
            response = requests.post(file_info_url, data={"file_id": file_id})
            file_info = response.json()
            
            if not file_info.get('ok'):
                logging.error(f"❌ File info error: {file_info}")
                return None
            
            file_path = file_info['result']['file_path']
            telegram_file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            
            file_response = requests.get(telegram_file_url)
            if file_response.status_code != 200:
                logging.error(f"❌ File download error: {file_response.status_code}")
                return None
            
            file_content = file_response.content
            file_extension = file_path.split('.')[-1] if '.' in file_path else 'jpg'
            supabase_file_path = f"sessions/{session_id}/document.{file_extension}"
            
            upload_result = supabase_client.upload_file(file_content, supabase_file_path)
            
            if upload_result:
                file_url = supabase_client.get_file_url(supabase_file_path)
                logging.info(f"✅ File stored in Supabase: {file_url}")
                return file_url
            else:
                logging.error("❌ Failed to upload file to Supabase")
                return None
            
        except Exception as e:
            logging.error(f"❌ Error downloading and storing file: {e}")
            return None
    
    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': chat_id, 
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            if reply_markup:
                payload['reply_markup'] = reply_markup
                
            response = requests.post(url, json=payload, timeout=10)
            success = response.status_code == 200
            
            if not success:
                logging.error(f"❌ Telegram API error: {response.text}")
            
            return success
            
        except Exception as e:
            logging.error(f"❌ Error sending message: {e}")
            return False
    
    def send_edit_view(self, chat_id, session_id, parsed_data):
        from utils.formatters import format_data_for_edit
        
        text = format_data_for_edit(parsed_data)
        keyboard = self.create_edit_buttons(session_id)
        
        return self.send_message(chat_id, text, keyboard)
    
    def create_verification_buttons(self, session_id):
        return {
            "inline_keyboard": [
                [
                    {"text": "✏️ Скорректировать", "callback_data": f"verify_edit_{session_id}"},
                    {"text": "✅ Всё верно", "callback_data": f"verify_ok_{session_id}"}
                ]
            ]
        }
    
    def create_edit_buttons(self, session_id):
        return {
            "inline_keyboard": [
                [
                    {"text": "🏭 Участок", "callback_data": f"edit_field_{session_id}_Участок"},
                    {"text": "🔧 Изделие", "callback_data": f"edit_field_{session_id}_Изделие"}
                ],
                [
                    {"text": "📐 Номер чертежа", "callback_data": f"edit_field_{session_id}_Номер чертежа"},
                    {"text": "🔢 Номер изделия", "callback_data": f"edit_field_{session_id}_Номер изделия"}
                ],
                [
                    {"text": "✅ Завершить", "callback_data": f"edit_done_{session_id}"}
                ]
            ]
        }
    
    def create_ok_button(self, session_id):
        return {
            "inline_keyboard": [
                [{"text": "✅ ОК", "callback_data": f"edit_ok_{session_id}"}]
            ]
        }
