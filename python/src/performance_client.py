import grpc
import performance_test_pb2
import performance_test_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import time
import uuid
import statistics
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class PerformanceTestClient:
    def __init__(self, server_address='localhost:50051'):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = performance_test_pb2_grpc.PerformanceTestStub(self.channel)

    def create_timestamp(self):
        now = time.time()
        timestamp = Timestamp()
        timestamp.seconds = int(now)
        timestamp.nanos = int((now - int(now)) * 1e9)
        return timestamp

    def generate_payload(self, size):
        sizes = {
            performance_test_pb2.EMPTY: 0,
            performance_test_pb2.SMALL: 1024,
            performance_test_pb2.MEDIUM: 10240,
            performance_test_pb2.LARGE: 102400,
            performance_test_pb2.XLARGE: 1048576
        }
        return os.urandom(sizes[size])

    def measure_latency(self, iterations=1000):
        latencies = []
        
        for _ in range(iterations):
            start_time = time.time()
            
            request = performance_test_pb2.PingRequest(
                client_id=str(uuid.uuid4()),
                send_timestamp=self.create_timestamp()
            )
            
            response = self.stub.PingPong(request)
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            latencies.append(latency)
        
        return {
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'avg_latency': statistics.mean(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18],
            'p99_latency': statistics.quantiles(latencies, n=100)[98]
        }

    def measure_throughput(self, payload_size, duration_seconds=10):
        messages_sent = 0
        bytes_sent = 0
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            request = performance_test_pb2.TestRequest(
                request_id=str(uuid.uuid4()),
                timestamp=self.create_timestamp(),
                payload_size=payload_size,
                payload=self.generate_payload(payload_size)
            )
            
            response = self.stub.UnaryCall(request)
            messages_sent += 1
            bytes_sent += len(request.payload)
        
        elapsed_time = time.time() - start_time
        return {
            'messages_per_second': messages_sent / elapsed_time,
            'bytes_per_second': bytes_sent / elapsed_time,
            'total_messages': messages_sent,
            'total_bytes': bytes_sent
        }

    def test_streaming(self, message_count=100, payload_size=performance_test_pb2.SMALL, interval_ms=100):
        request = performance_test_pb2.StreamRequest(
            message_count=message_count,
            payload_size=payload_size,
            interval_ms=interval_ms
        )
        
        print(f"\nTesting server streaming with {message_count} messages...")
        messages_received = 0
        start_time = time.time()
        
        for response in self.stub.ServerStreaming(request):
            messages_received += 1
            
        elapsed_time = time.time() - start_time
        print(f"Received {messages_received} messages in {elapsed_time:.2f} seconds")
        print(f"Average throughput: {messages_received/elapsed_time:.2f} messages/second")

    def test_batch_processing(self, batch_size=10, parallel=True):
        requests = []
        for _ in range(batch_size):
            request = performance_test_pb2.TestRequest(
                request_id=str(uuid.uuid4()),
                timestamp=self.create_timestamp(),
                payload_size=performance_test_pb2.SMALL,
                payload=self.generate_payload(performance_test_pb2.SMALL)
            )
            requests.append(request)
        
        batch_request = performance_test_pb2.BatchRequest(
            requests=requests,
            parallel_process=parallel
        )
        
        start_time = time.time()
        response = self.stub.BatchProcess(batch_request)
        elapsed_time = time.time() - start_time
        
        return {
            'batch_size': batch_size,
            'parallel': parallel,
            'processing_time': elapsed_time,
            'avg_time_per_request': elapsed_time / batch_size
        }

def main():
    client = PerformanceTestClient()
    
    # 1 Test latency
    print("Testing latency...")
    latency_results = client.measure_latency(iterations=1000)
    print("\nLatency Results:")
    for metric, value in latency_results.items():
        print(f"{metric}: {value:.2f} ms")

    # 2 Test throughput with different payload sizes
    print("\nTesting throughput with different payload sizes...")
    payload_sizes = [
        performance_test_pb2.SMALL,
        performance_test_pb2.MEDIUM,
        performance_test_pb2.LARGE
    ]
    
    for size in payload_sizes:
        print(f"\nPayload size: {performance_test_pb2.PayloadSize.Name(size)}")
        results = client.measure_throughput(size, duration_seconds=10)
        print(f"Messages per second: {results['messages_per_second']:.2f}")
        print(f"Throughput: {results['bytes_per_second']/1024/1024:.2f} MB/s")
        print(f"Total messages: {results['total_messages']}")
        print(f"Total data: {results['total_bytes']/1024/1024:.2f} MB")

    # 3 Test streaming (kind of optional but good to have for the grpc)
    print("\nTesting streaming performance...")
    client.test_streaming(message_count=1000, 
                         payload_size=performance_test_pb2.SMALL,
                         interval_ms=10)

    # 4 Test batch processing (kind of optional but good to have for the grpc)
    print("\nTesting batch processing...")
    batch_sizes = [10, 50, 100]
    for parallel in [False, True]:
        mode = "Parallel" if parallel else "Sequential"
        print(f"\n{mode} Processing:")
        for batch_size in batch_sizes:
            results = client.test_batch_processing(batch_size, parallel)
            print(f"\nBatch size: {results['batch_size']}")
            print(f"Total processing time: {results['processing_time']:.3f} seconds")
            print(f"Average time per request: {results['avg_time_per_request']*1000:.2f} ms")

if __name__ == '__main__':
    main()