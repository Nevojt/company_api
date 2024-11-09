from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    mail_from_name: str
    mail_from_name_company: str

    database_name: str
    database_username: str
    database_hostname: str
    database_port: str
    database_password: str

    database_hostname_company: str
    database_password_company: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    backblaze_id: str
    backblaze_key: str

    database_name_company: str
    database_username_company: str
    url_address_dns: str
    url_address_dns_company: str

    key_crypto: str
    rout_image: str
    bucket_name_user_avatar: str
    bucket_name_room_image: str
    openai_api_key: str

    sentry_url: str

    redis_url: str


    model_config = SettingsConfigDict(env_file = ".env", extra="ignore")
    

settings = Settings()
