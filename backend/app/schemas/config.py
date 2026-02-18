from pydantic import BaseModel

class ConfigResponse(BaseModel):
    """Public configuration response"""
    telegram_bot_name: str

    class Config:
        from_attributes = True
