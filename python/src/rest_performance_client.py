# rest_performance_client.py

import requests
import time
import uuid
import statistics
import json
from enum import Enum
import random

class PayloadSize(Enum):
    SMALL = 1024      # 1KB
    MEDIUM = 10240    # 10KB
    LARGE = 102400    # 100KB

class RestPerformanceClient:
    def __init__(self, server_address='http://localhost:8080'):
        self.server_address = server_address

    def generate_payload(self, num_structures, size_per_structure):
        """Generate an array of data structures."""
        return [{'key': f'key_{i}',
                  'value': 'x' * size_per_structure,
                  'age': random.randint(18, 30),
                  'gradepoint': round(random.uniform(2.0, 4.0), 2)
                } for i in range(num_structures)]
    
    def measure_latency(self, num_structures, size_per_structure, iterations=10):
        """Measure basic latency using ping-pong"""
        latencies = []
        payload = self.generate_payload(num_structures, size_per_structure)
        
        for _ in range(iterations):
            start_time = time.perf_counter_ns()
            
            request_data = {
                'client_id': str(uuid.uuid4()),
                'timestamp': int(time.time() * 1_000_000),
                'payload': payload
            }

            # print("Request Data:", json.dumps(request_data, indent=4))

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

    def measure_throughput(self, num_structures, size_per_structure, duration=10):
        """Measure throughput with different payload sizes"""
        payload = self.generate_payload(num_structures, size_per_structure)
        messages_sent = 0
        bytes_sent = 0
        start_time = time.time()
        
        # size_name = payload_size.name
        # size_bytes = payload_size.value
        # payload = 'x' * size_byt  es
        
        # print(f"\nPayload size: {size_name}")
        
        while time.time() - start_time < duration:
            request_data = {
                'request_id': str(messages_sent),
                'payload': payload
            }

            # print("Request Data:", json.dumps(request_data, indent=4)) 

            response = requests.post(f"{self.server_address}/unary", json=request_data)
            messages_sent += 1
            for data in payload:
                bytes_sent += len(data['key'])  # Key size (bytes)
                bytes_sent += len(data['value'].encode('utf-8'))  # Value size
                bytes_sent += 4  # Age
                bytes_sent += 4  # Gradepoint

            # bytes_sent += num_structures * size_per_structure
        
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

    def test_streaming(self, message_count=1000, interval_ms=100, num_structures=10, size_per_structure=10):
        """Test server streaming performance"""
        print("\nTesting server streaming...")
        print(f"Testing server streaming with {message_count} messages...")
        
        start_time = time.time()
        
        response = requests.get(
            f"{self.server_address}/stream",
            params={
                'message_count': message_count,
                'interval_ms': interval_ms, 
                'num_structures': num_structures, 
                'payload_size': size_per_structure
            },
            stream=True
        )
        
        messages_received = sum(1 for _ in response.iter_lines() if _)
        
        elapsed_time = time.time() - start_time
        throughput = messages_received / elapsed_time
        
        print(f"Received {messages_received} messages in {elapsed_time:.2f} seconds")
        print(f"Average throughput: {throughput:.2f} messages/second")
        
        return {
            'messages_received': messages_received,
            'elapsed_time': elapsed_time,
            'throughput': throughput
        }

    def test_batch_processing(self, batch_sizes=[10, 50, 100], num_structures=5, size_per_structure=10, parallel_options=[False, True]):
        """Test batch processing performance"""
        print("\nTesting batch processing...")
        
        results = {}
        
        for parallel in parallel_options:
            mode = "Parallel" if parallel else "Sequential"
            print(f"\n{mode} Processing:")
            
            for batch_size in batch_sizes:
                requests_data = [
                    {'request_id': f'batch_{i}', 'payload': self.generate_payload(num_structures, size_per_structure)}
                    for i in range(batch_size)
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
    client.measure_latency(10, 256)
    
    print("\nTesting throughput with different payload sizes...")
    payload_configs = [
        {"label": "SMALL", "num_structures": 20, "size_per_structure": 1024}, 
        {"label": "MEDIUM", "num_structures": 10000, "size_per_structure": 2048}, 
        {"label": "LARGE", "num_structures": 300000, "size_per_structure": 4096}, 
    ]

    for config in payload_configs:
        print(f"\nTesting throughput with payload size: {config['label']}")
        client.measure_throughput(config["num_structures"], config["size_per_structure"])
    
    # print("\nTesting streaming performance...")
    # client.test_streaming()
    
    # print("\nTesting batch processing...")
    # client.test_batch_processing()

if __name__ == "__main__":
    main()