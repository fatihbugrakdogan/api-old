from pydantic import BaseModel


class SubscriptionBase(BaseModel):

    type: "Pro" | "Free"
