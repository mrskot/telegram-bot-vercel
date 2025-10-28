import requests
import logging
import json
import os
from lib.supabase_client import supabase_client

class BitrixService:
    def __init__(self):
        self.webhook_url = os.getenv('BITRIX24_WEBHOOK_URL')
        self.entity_type_id = os.getenv('BITRIX24_ENTITY_TYPE_ID', '1086')
        
        if not self.webhook_url:
            logging.error("❌ Bitrix24 webhook URL not set")
            raise ValueError("Bitrix24 webhook URL not set")
        
        logging.info("✅ Bitrix service initialized")
    
    def send_data(self, parsed_data: dict, chat_id: int, username: str = "unknown"):
        try:
            bitrix_data = {
                "entityTypeId": int(self.entity_type_id),
                "fields": {
                    "ufCrm28_1737543613": parsed_data.get('Номер чертежа', 'не указано'),
                    "ufCrm28_1753194216": parsed_data.get('Участок', 'не указано'),
                    "ufCrm28_1753194194": parsed_data.get('Изделие', 'не указано'),
                    "ufCrm28_1736772873": parsed_data.get('Номер изделия', 'не указано')
                }
            }
            
            logging.info(f"🔄 Sending to Bitrix24: {json.dumps(bitrix_data, ensure_ascii=False)}")
            
            response = requests.post(
                self.webhook_url,
                json=bitrix_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            logging.info(f"📨 Bitrix24 response: {response.status_code}")
            
            result_data = response.json()
            
            supabase_client.supabase.table('bitrix_logs').insert({
                'request_data': bitrix_data,
                'response_data': result_data,
                'status': 'success' if response.status_code == 200 else 'error'
            }).execute()
            
            if response.status_code == 200:
                if 'result' in result_data:
                    return result_data['result']
                else:
                    error = result_data.get('error', 'Unknown error')
                    logging.error(f"❌ Bitrix24 error: {error}")
                    return False
            else:
                logging.error(f"❌ HTTP error Bitrix24: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error sending to Bitrix24: {e}")
            
            try:
                supabase_client.supabase.table('bitrix_logs').insert({
                    'request_data': {'error': str(e)},
                    'response_data': {},
                    'status': 'exception'
                }).execute()
            except:
                pass
            
            return False
    
    def extract_bitrix_id(self, item_id):
        try:
            if isinstance(item_id, dict):
                if 'item' in item_id and 'id' in item_id['item']:
                    return item_id['item']['id']
                elif 'id' in item_id:
                    return item_id['id']
            elif isinstance(item_id, (int, str)):
                return str(item_id)
            
            logging.warning(f"⚠️ Непонятный формат ответа от Битрикс24: {item_id}")
            return None
            
        except Exception as e:
            logging.error(f"❌ Ошибка извлечения ID из ответа Битрикс24: {e}")
            return None
