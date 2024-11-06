from pyairtable import Api
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class AirtableManager:
    def __init__(self,table_name=None):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.table_name = table_name or os.getenv("AIRTABLE_TABLE_NAME")
        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)
    
    def create_record(self, fields):
        return self.table.create(fields)
    
    def read_records(self):
        return self.table.all()
    
    def update_record(self, record_id, fields):
        return self.table.update(record_id, fields)
    
    def delete_record(self, record_id):
        return self.table.delete(record_id)