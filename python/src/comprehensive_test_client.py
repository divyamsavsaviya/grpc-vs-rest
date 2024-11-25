import grpc
import performance_test_pb2
import performance_test_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import time
import uuid
import threading

class ComprehensiveGrpcTester:
    def __init__(self, server_address='localhost:50051'):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = performance_test_pb2_grpc.PerformanceTestStub(self.channel)

    def _create_timestamp(self):
        now = time.time()
        timestamp = Timestamp()
        timestamp.seconds = int(now)
        timestamp.nanos = int((now - int(now)) * 1e9)
        return timestamp

    def test_unary_call(self):
        """Test simple unary call"""
        print("\n=== Testing Unary Call ===")
        request = performance_test_pb2.TestRequest(
            request_id=str(uuid.uuid4()),
            timestamp=self._create_timestamp(),
            payload=b'Hello, Server!'
        )
        
        print("Sending unary request...")
        response = self.stub.UnaryCall(request)
        print(f"Received response with ID: {response.request_id}")

    def test_server_streaming(self):
        """Test server streaming"""
        print("\n=== Testing Server Streaming ===")
        request = performance_test_pb2.StreamRequest(
            message_count=5,  # Request 5 messages
            payload_size=performance_test_pb2.SMALL,
            interval_ms=1000  # 1 second between messages
        )
        
        print("Starting server stream...")
        responses = self.stub.ServerStreaming(request)
        for i, response in enumerate(responses, 1):
            print(f"Received stream response {i}")
            time.sleep(0.5)  # Small delay to make it easier to follow

    def test_client_streaming(self):
        """Test client streaming"""
        print("\n=== Testing Client Streaming ===")
        
        def request_generator():
            for i in range(5):  # Send 5 messages
                request = performance_test_pb2.TestRequest(
                    request_id=f"stream-{i}",
                    timestamp=self._create_timestamp(),
                    payload=f"Stream message {i}".encode()
                )
                print(f"Sending client stream message {i+1}")
                yield request
                time.sleep(0.5)  # Small delay between messages
        
        response = self.stub.ClientStreaming(request_generator())
        print(f"Client streaming complete. Processed {response.messages_processed} messages")

    def test_bidirectional_streaming(self):
        """Test bidirectional streaming"""
        print("\n=== Testing Bidirectional Streaming ===")
        
        def request_generator():
            for i in range(5):  # Send 5 messages
                request = performance_test_pb2.TestRequest(
                    request_id=f"bistream-{i}",
                    timestamp=self._create_timestamp(),
                    payload=f"Bidirectional message {i}".encode()
                )
                print(f"Sending bidirectional message {i+1}")
                yield request
                time.sleep(0.5)
        
        responses = self.stub.BidirectionalStreaming(request_generator())
        for i, response in enumerate(responses, 1):
            print(f"Received bidirectional response {i}")

    def test_ping_pong(self):
        """Test ping pong"""
        print("\n=== Testing PingPong ===")
        request = performance_test_pb2.PingRequest(
            client_id=str(uuid.uuid4()),
            send_timestamp=self._create_timestamp()
        )
        
        print("Sending ping...")
        response = self.stub.PingPong(request)
        print(f"Received pong from client: {response.client_id}")

    def test_batch_processing(self):
        """Test batch processing"""
        print("\n=== Testing Batch Processing ===")
        
        # Create a batch of requests
        requests = []
        for i in range(5):
            request = performance_test_pb2.TestRequest(
                request_id=f"batch-{i}",
                timestamp=self._create_timestamp(),
                payload=f"Batch message {i}".encode()
            )
            requests.append(request)
        
        # Test sequential processing
        print("\nTesting sequential batch processing...")
        batch_request = performance_test_pb2.BatchRequest(
            requests=requests,
            parallel_process=False
        )
        response = self.stub.BatchProcess(batch_request)
        print(f"Processed {len(response.responses)} requests sequentially")
        
        # Test parallel processing
        print("\nTesting parallel batch processing...")
        batch_request.parallel_process = True
        response = self.stub.BatchProcess(batch_request)
        print(f"Processed {len(response.responses)} requests in parallel")

    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            self.test_unary_call()
            time.sleep(1)
            
            self.test_server_streaming()
            time.sleep(1)
            
            self.test_client_streaming()
            time.sleep(1)
            
            self.test_bidirectional_streaming()
            time.sleep(1)
            
            self.test_ping_pong()
            time.sleep(1)
            
            self.test_batch_processing()
            
        except grpc.RpcError as e:
            print(f"RPC error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    tester = ComprehensiveGrpcTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()