# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import performance_test_pb2 as performance__test__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in performance_test_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class PerformanceTestStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UnaryCall = channel.unary_unary(
                '/perftest.PerformanceTest/UnaryCall',
                request_serializer=performance__test__pb2.TestRequest.SerializeToString,
                response_deserializer=performance__test__pb2.TestResponse.FromString,
                _registered_method=True)
        self.ServerStreaming = channel.unary_stream(
                '/perftest.PerformanceTest/ServerStreaming',
                request_serializer=performance__test__pb2.StreamRequest.SerializeToString,
                response_deserializer=performance__test__pb2.TestResponse.FromString,
                _registered_method=True)
        self.ClientStreaming = channel.stream_unary(
                '/perftest.PerformanceTest/ClientStreaming',
                request_serializer=performance__test__pb2.TestRequest.SerializeToString,
                response_deserializer=performance__test__pb2.StreamResponse.FromString,
                _registered_method=True)
        self.BidirectionalStreaming = channel.stream_stream(
                '/perftest.PerformanceTest/BidirectionalStreaming',
                request_serializer=performance__test__pb2.TestRequest.SerializeToString,
                response_deserializer=performance__test__pb2.TestResponse.FromString,
                _registered_method=True)
        self.PingPong = channel.unary_unary(
                '/perftest.PerformanceTest/PingPong',
                request_serializer=performance__test__pb2.PingRequest.SerializeToString,
                response_deserializer=performance__test__pb2.PongResponse.FromString,
                _registered_method=True)
        self.BatchProcess = channel.unary_unary(
                '/perftest.PerformanceTest/BatchProcess',
                request_serializer=performance__test__pb2.BatchRequest.SerializeToString,
                response_deserializer=performance__test__pb2.BatchResponse.FromString,
                _registered_method=True)


class PerformanceTestServicer(object):
    """Missing associated documentation comment in .proto file."""

    def UnaryCall(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ServerStreaming(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClientStreaming(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BidirectionalStreaming(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PingPong(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BatchProcess(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PerformanceTestServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UnaryCall': grpc.unary_unary_rpc_method_handler(
                    servicer.UnaryCall,
                    request_deserializer=performance__test__pb2.TestRequest.FromString,
                    response_serializer=performance__test__pb2.TestResponse.SerializeToString,
            ),
            'ServerStreaming': grpc.unary_stream_rpc_method_handler(
                    servicer.ServerStreaming,
                    request_deserializer=performance__test__pb2.StreamRequest.FromString,
                    response_serializer=performance__test__pb2.TestResponse.SerializeToString,
            ),
            'ClientStreaming': grpc.stream_unary_rpc_method_handler(
                    servicer.ClientStreaming,
                    request_deserializer=performance__test__pb2.TestRequest.FromString,
                    response_serializer=performance__test__pb2.StreamResponse.SerializeToString,
            ),
            'BidirectionalStreaming': grpc.stream_stream_rpc_method_handler(
                    servicer.BidirectionalStreaming,
                    request_deserializer=performance__test__pb2.TestRequest.FromString,
                    response_serializer=performance__test__pb2.TestResponse.SerializeToString,
            ),
            'PingPong': grpc.unary_unary_rpc_method_handler(
                    servicer.PingPong,
                    request_deserializer=performance__test__pb2.PingRequest.FromString,
                    response_serializer=performance__test__pb2.PongResponse.SerializeToString,
            ),
            'BatchProcess': grpc.unary_unary_rpc_method_handler(
                    servicer.BatchProcess,
                    request_deserializer=performance__test__pb2.BatchRequest.FromString,
                    response_serializer=performance__test__pb2.BatchResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'perftest.PerformanceTest', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('perftest.PerformanceTest', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PerformanceTest(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def UnaryCall(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/perftest.PerformanceTest/UnaryCall',
            performance__test__pb2.TestRequest.SerializeToString,
            performance__test__pb2.TestResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ServerStreaming(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/perftest.PerformanceTest/ServerStreaming',
            performance__test__pb2.StreamRequest.SerializeToString,
            performance__test__pb2.TestResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ClientStreaming(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            '/perftest.PerformanceTest/ClientStreaming',
            performance__test__pb2.TestRequest.SerializeToString,
            performance__test__pb2.StreamResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def BidirectionalStreaming(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/perftest.PerformanceTest/BidirectionalStreaming',
            performance__test__pb2.TestRequest.SerializeToString,
            performance__test__pb2.TestResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def PingPong(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/perftest.PerformanceTest/PingPong',
            performance__test__pb2.PingRequest.SerializeToString,
            performance__test__pb2.PongResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def BatchProcess(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/perftest.PerformanceTest/BatchProcess',
            performance__test__pb2.BatchRequest.SerializeToString,
            performance__test__pb2.BatchResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
