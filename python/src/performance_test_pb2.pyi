from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PayloadSize(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EMPTY: _ClassVar[PayloadSize]
    SMALL: _ClassVar[PayloadSize]
    MEDIUM: _ClassVar[PayloadSize]
    LARGE: _ClassVar[PayloadSize]
    XLARGE: _ClassVar[PayloadSize]
EMPTY: PayloadSize
SMALL: PayloadSize
MEDIUM: PayloadSize
LARGE: PayloadSize
XLARGE: PayloadSize

class TestRequest(_message.Message):
    __slots__ = ("request_id", "timestamp", "payload_size_enum", "payload")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_SIZE_ENUM_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    timestamp: _timestamp_pb2.Timestamp
    payload_size_enum: PayloadSize
    payload: _containers.RepeatedCompositeFieldContainer[DataStructure]
    def __init__(self, request_id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., payload_size_enum: _Optional[_Union[PayloadSize, str]] = ..., payload: _Optional[_Iterable[_Union[DataStructure, _Mapping]]] = ...) -> None: ...

class StreamRequest(_message.Message):
    __slots__ = ("message_count", "payload_size_enum", "interval_ms")
    MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_SIZE_ENUM_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    message_count: int
    payload_size_enum: PayloadSize
    interval_ms: int
    def __init__(self, message_count: _Optional[int] = ..., payload_size_enum: _Optional[_Union[PayloadSize, str]] = ..., interval_ms: _Optional[int] = ...) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ("client_id", "send_timestamp")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEND_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    send_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, client_id: _Optional[str] = ..., send_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BatchRequest(_message.Message):
    __slots__ = ("requests", "parallel_process")
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_PROCESS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[TestRequest]
    parallel_process: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[TestRequest, _Mapping]]] = ..., parallel_process: bool = ...) -> None: ...

class ProcessingMetrics(_message.Message):
    __slots__ = ("processing_time_us", "memory_used_bytes", "cpu_usage", "errors")
    PROCESSING_TIME_US_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    CPU_USAGE_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    processing_time_us: int
    memory_used_bytes: int
    cpu_usage: float
    errors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, processing_time_us: _Optional[int] = ..., memory_used_bytes: _Optional[int] = ..., cpu_usage: _Optional[float] = ..., errors: _Optional[_Iterable[str]] = ...) -> None: ...

class TestResponse(_message.Message):
    __slots__ = ("request_id", "received_at", "processed_at", "metrics", "payload")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    received_at: _timestamp_pb2.Timestamp
    processed_at: _timestamp_pb2.Timestamp
    metrics: ProcessingMetrics
    payload: _containers.RepeatedCompositeFieldContainer[DataStructure]
    def __init__(self, request_id: _Optional[str] = ..., received_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., processed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., metrics: _Optional[_Union[ProcessingMetrics, _Mapping]] = ..., payload: _Optional[_Iterable[_Union[DataStructure, _Mapping]]] = ...) -> None: ...

class DataStructure(_message.Message):
    __slots__ = ("key", "value", "age", "gradepoint")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    GRADEPOINT_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    value: str
    age: int
    gradepoint: float
    def __init__(self, key: _Optional[bytes] = ..., value: _Optional[str] = ..., age: _Optional[int] = ..., gradepoint: _Optional[float] = ...) -> None: ...

class StreamResponse(_message.Message):
    __slots__ = ("messages_processed", "aggregate_metrics")
    MESSAGES_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    AGGREGATE_METRICS_FIELD_NUMBER: _ClassVar[int]
    messages_processed: int
    aggregate_metrics: ProcessingMetrics
    def __init__(self, messages_processed: _Optional[int] = ..., aggregate_metrics: _Optional[_Union[ProcessingMetrics, _Mapping]] = ...) -> None: ...

class PongResponse(_message.Message):
    __slots__ = ("client_id", "client_timestamp", "server_timestamp")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SERVER_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    client_timestamp: _timestamp_pb2.Timestamp
    server_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, client_id: _Optional[str] = ..., client_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., server_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BatchResponse(_message.Message):
    __slots__ = ("responses", "batch_metrics")
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    BATCH_METRICS_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[TestResponse]
    batch_metrics: ProcessingMetrics
    def __init__(self, responses: _Optional[_Iterable[_Union[TestResponse, _Mapping]]] = ..., batch_metrics: _Optional[_Union[ProcessingMetrics, _Mapping]] = ...) -> None: ...
