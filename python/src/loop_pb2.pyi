from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Route(_message.Message):
    __slots__ = ("id", "num_loops", "collisions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NUM_LOOPS_FIELD_NUMBER: _ClassVar[int]
    COLLISIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    num_loops: int
    collisions: int
    def __init__(self, id: _Optional[int] = ..., num_loops: _Optional[int] = ..., collisions: _Optional[int] = ...) -> None: ...
