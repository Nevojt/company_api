from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os


class Settings(BaseSettings):
    users_data_file: str
    default_user: str
    default_room_name: str
    default_room_image: str

    default_user_name: str
    default_user_avatar: str
    default_user_email: str
    default_user_password: str

    company_name: str
    company_subdomain: str
    company_email: str
    company_phone: str
    company_address: str
    company_description: str
    company_logo: str


    model_config = SettingsConfigDict(env_file=".env_start_app", extra="ignore")

    def load_users_data(self):
        if not os.path.exists(self.users_data_file):
            print(f"Warning: File {self.users_data_file} not found. Loading default users data.")
            return []  # Or return a default configuration if appropriate
        with open(self.users_data_file, 'r') as file:
            users_data_json = json.load(file)
        return users_data_json


start_app = Settings()
users_data = start_app.load_users_data()