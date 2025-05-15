from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TrackerMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTO: _ClassVar[TrackerMode]
    OFF: _ClassVar[TrackerMode]
AUTO: TrackerMode
OFF: TrackerMode

class TelemetryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Telemetry(_message.Message):
    __slots__ = ("mac", "current_position", "target_position", "battery_soc", "charging", "mode")
    MAC_FIELD_NUMBER: _ClassVar[int]
    CURRENT_POSITION_FIELD_NUMBER: _ClassVar[int]
    TARGET_POSITION_FIELD_NUMBER: _ClassVar[int]
    BATTERY_SOC_FIELD_NUMBER: _ClassVar[int]
    CHARGING_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    mac: str
    current_position: float
    target_position: float
    battery_soc: float
    charging: bool
    mode: TrackerMode
    def __init__(self, mac: _Optional[str] = ..., current_position: _Optional[float] = ..., target_position: _Optional[float] = ..., battery_soc: _Optional[float] = ..., charging: bool = ..., mode: _Optional[_Union[TrackerMode, str]] = ...) -> None: ...
