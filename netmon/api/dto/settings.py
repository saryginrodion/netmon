from pydantic import BaseModel


class SetCollectorSettingsBody(BaseModel):
    is_active: bool
