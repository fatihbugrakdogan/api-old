from pydantic import BaseModel,validator
import json
from typing import List

class DiscordRuleConfig(BaseModel):
    action_type: str              
    expires_at: str
    project: str
    workspace: str
    user: str

class DiscordRuleValues(BaseModel):
    discord_link: str
    content: str

class DiscordRuleOnSubmitData(BaseModel):
    action: str
    user: str
    values: DiscordRuleValues
    action_type: str
    expires_at: str
    project: str
    rule_name: str
    workspace: str

class DiscordRuleOnSubmit(BaseModel):
    
    data:DiscordRuleOnSubmitData
    
    @validator('data', pre=True)
    def parse_data(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


class DiscordRuleTriggerData(BaseModel):
    workspace: str
    project: str
    target_object: str
    action_type: str
    action: str
    user: str
    app_configuration_json: str
    idempotency_key: str
    expires_at: str

class DiscordRuleTrigger(BaseModel):
    data: DiscordRuleTriggerData

    @validator('data', pre=True)
    def parse_data(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value









    






