# rest_performance_client.py

import requests
import time
import uuid
import statistics
import json
from enum import Enum

class PayloadSize(Enum):
    SMALL = 1024      # 1KB
    MEDIUM = 10240    # 10KB
    LARGE = 102400    # 100KB

class RestPerformanceClient:
    def __init__(self, server_address='http://localhost:8080'):
        self.server_address = server_address

    def measure_latency(self, iterations=1000):
        """Measure basic latency using ping-pong"""
        latencies = []
        
        for _ in range(iterations):
            start_time = time.perf_counter_ns()
            
            request_data = {
                'client_id': str(uuid.uuid4()),
                'timestamp': int(time.time() * 1_000_000)
            }
            
            response = requests.post(f"{self.server_address}/ping", json=request_data)
            
            end_time = time.perf_counter_ns()
            latency = (end_time - start_time) / 1_000_000  # Convert to milliseconds
            latencies.append(latency)
        
        results = {
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'avg_latency': statistics.mean(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18],
            'p99_latency': statistics.quantiles(latencies, n=100)[98]
        }

        print("\nLatency Results:")
        for metric, value in results.items():
            print(f"{metric}: {value:.2f} ms")
        
        return results

    def measure_throughput(self, payload_size: PayloadSize, duration=10):
        """Measure throughput with different payload sizes"""
        messages_sent = 0
        bytes_sent = 0
        start_time = time.time()
        
        size_name = payload_size.name
        size_bytes = payload_size.value
        payload = 'x' * size_bytes
        
        print(f"\nPayload size: {size_name}")
        
        while time.time() - start_time < duration:
            request_data = {
                'request_id': str(messages_sent),
                'payload': payload
            }
            
            response = requests.post(f"{self.server_address}/unary", json=request_data)
            messages_sent += 1
            bytes_sent += len(payload)
        
        elapsed_time = time.time() - start_time
        messages_per_second = messages_sent / elapsed_time
        throughput_mb = (bytes_sent / elapsed_time) / (1024 * 1024)
        
        print(f"Messages per second: {messages_per_second:.2f}")
        print(f"Throughput: {throughput_mb:.2f} MB/s")
        print(f"Total messages: {messages_sent}")
        print(f"Total data: {bytes_sent / (1024 * 1024):.2f} MB")
        
        return {
            'messages_per_second': messages_per_second,
            'throughput_mb_s': throughput_mb,
            'total_messages': messages_sent,
            'total_bytes': bytes_sent
        }

    def test_streaming(self, message_count=1000, interval_ms=100):
        """Test server streaming performance"""
        print("\nTesting server streaming...")
        print(f"Testing server streaming with {message_count} messages...")
        
        start_time = time.time()
        
        response = requests.get(
            f"{self.server_address}/stream",
            params={
                'message_count': message_count,
                'interval_ms': interval_ms
            },
            stream=True
        )
        
        messages_received = 0
        for line in response.iter_lines():
            if line:
                messages_received += 1
        
        elapsed_time = time.time() - start_time
        throughput = messages_received / elapsed_time
        
        print(f"Received {messages_received} messages in {elapsed_time:.2f} seconds")
        print(f"Average throughput: {throughput:.2f} messages/second")
        
        return {
            'messages_received': messages_received,
            'elapsed_time': elapsed_time,
            'throughput': throughput
        }

    def test_batch_processing(self, batch_sizes=[10, 50, 100], parallel_options=[False, True]):
        """Test batch processing performance"""
        print("\nTesting batch processing...")
        
        results = {}
        
        for parallel in parallel_options:
            mode = "Parallel" if parallel else "Sequential"
            print(f"\n{mode} Processing:")
            
            for batch_size in batch_sizes:
                requests_data = [
                    {
                        'request_id': f"batch-{i}",
                        'payload': f"Batch message {i}"
                    } for i in range(batch_size)
                ]
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.server_address}/batch",
                    json={
                        'requests': requests_data,
                        'parallel_process': parallel
                    }
                )
                
                end_time = time.time()
                total_time = end_time - start_time
                avg_time = (total_time * 1000) / batch_size  # Convert to ms
                
                print(f"\nBatch size: {batch_size}")
                print(f"Total processing time: {total_time:.3f} seconds")
                print(f"Average time per request: {avg_time:.2f} ms")
                
                results[f"{'parallel' if parallel else 'sequential'}_{batch_size}"] = {
                    'batch_size': batch_size,
                    'total_time': total_time,
                    'avg_time_ms': avg_time
                }
        
        return results

def main():
    client = RestPerformanceClient()
    
    print("Testing latency...")
    client.measure_latency()
    
    print("\nTesting throughput with different payload sizes...")
    for size in PayloadSize:
        client.measure_throughput(size)
    
    print("\nTesting streaming performance...")
    client.test_streaming()
    
    print("\nTesting batch processing...")
    client.test_batch_processing()

if __name__ == "__main__":
    main()