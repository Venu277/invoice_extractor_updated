from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.gst.rules import is_valid_gstin_format


class PartyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    gstin: str | None = Field(None, max_length=15)
    state_code: str | None = Field(None, max_length=2)
    type: str = Field("vendor", pattern="^(vendor|customer|both)$")
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)
    shipping_address: str | None = Field(None, max_length=500)
    gst_registration_type: str = Field("unregistered", pattern="^(regular|composition|sez|unregistered|consumer)$")
    notes: str | None = Field(None, max_length=4000)
    payment_terms_days: int | None = 30
    credit_limit_paise: int = Field(0, ge=0)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Party name is required.")
        return value

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return "vendor" if value == "supplier" else value

    @field_validator("gstin")
    @classmethod
    def normalize_gstin(cls, value: str | None) -> str | None:
        if value:
            value = value.strip().upper()
        return value or None

    @model_validator(mode="after")
    def require_gstin_for_registered_party(self):
        if self.gst_registration_type not in {"unregistered", "consumer"} and not self.gstin:
            raise ValueError("GSTIN is required for this registration type.")
        return self

    @field_validator("gst_registration_type")
    @classmethod
    def validate_registration_type(cls, value: str) -> str:
        allowed = {"regular", "composition", "sez", "unregistered", "consumer"}
        if value not in allowed:
            raise ValueError("Choose a valid GST registration type.")
        return value

    @field_validator("payment_terms_days")
    @classmethod
    def validate_payment_terms(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 365:
            raise ValueError("Payment terms must be between 0 and 365 days.")
        return value


class PartyCreate(PartyBase):
    @field_validator("gstin")
    @classmethod
    def validate_create_gstin(cls, value: str | None) -> str | None:
        if value and not is_valid_gstin_format(value):
            raise ValueError("Enter a valid 15-character GSTIN.")
        return value


class PartyUpdate(BaseModel):
    name: str | None = None
    gstin: str | None = None
    state_code: str | None = None
    type: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    shipping_address: str | None = None
    gst_registration_type: str | None = None
    notes: str | None = None
    payment_terms_days: int | None = None
    credit_limit_paise: int | None = None


class PartyResponse(PartyBase):
    id: int
    business_id: int
    auto_created: bool
    is_archived: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
