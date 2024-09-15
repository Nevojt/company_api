from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_from_name_company: str
    database_hostname_company: str
    database_hostname: str
    database_port: str
    database_password_company: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    supabase_url: str
    supabase_key: str
    backblaze_id: str
    backblaze_key: str
    url_address_dns: str
    url_address_dns_company: str
    key_crypto: str
    rout_image: str
    bucket_name_user_avatar: str
    bucket_name_room_image: str
    openai_api_key: str
    users_data_file: str

    
    model_config = SettingsConfigDict(env_file = ".env")
    
    def load_users_data(self):
        if not os.path.exists(self.users_data_file):
            print(f"Warning: File {self.users_data_file} not found. Loading default users data.")
            return []  # Or return a default configuration if appropriate
        with open(self.users_data_file, 'r') as file:
            users_data = json.load(file)
        return users_data



settings = Settings()
users_data = settings.load_users_data()