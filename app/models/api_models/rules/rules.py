from pydantic import BaseModel


class CreateRule(BaseModel):
    action: str
    user: str
    values: dict
    action_type: str
    expires_at: str
    project: str
    rule_name: str
    workspace: str
    rule_type: str
    rule_values: dict

