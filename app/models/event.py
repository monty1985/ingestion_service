from pydantic import BaseModel, Field
import time

class EventPayload(BaseModel):
    cpu_usage: int = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: int = Field(..., ge=0, le=100, description="Memory usage percentage")
    battery_status: str = Field(..., regex="^(charging|discharging)$", description="Battery status")
    temperature: int = Field(..., ge=0, description="Device temperature in Celsius")

class DeviceEvent(BaseModel):
    device_id: str
    event_type: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    payload: EventPayload