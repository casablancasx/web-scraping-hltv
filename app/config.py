from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    furia_hltv_url: str = "https://www.hltv.org/team/8297/furia"
    furia_draft5_url: str = "https://draft5.gg/equipe/330-FURIA"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()