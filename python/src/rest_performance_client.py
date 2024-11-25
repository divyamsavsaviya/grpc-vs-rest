# rest_performance_client.py
import requests
import time
import uuid
import statistics
from datetime import datetime

class RestPerformanceClient:
    def __init__(self, server_url='http://localhost:8080'):
        self.server_url = server_url

    def measure_latency(self, iterations=1000):
        """Measure basic latency using ping-pong"""
        latencies = []
        
        for _ in range(iterations):
            start_time = time.time()
            
            request_data = {
                'client_id': str(uuid.uuid4()),
                'send_timestamp': int(time.time() * 1_000_000)
            }
            
            response = requests.post(f"{self.server_url}/ping", json=request_data)
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
        
        return {
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'avg_latency': statistics.mean(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18],
            'p99_latency': statistics.quantiles(latencies, n=100)[98]
        }

    def measure_throughput(self, payload_size, duration=10):
        """Measure throughput with different payload sizes"""
        messages_sent = 0
        bytes_sent = 0
        start_time = time.time()
        
        while time.time() - start_time < duration:
            request_data = {
                'request_id': str(messages_sent),
                'payload': 'x' * payload_size
            }
            
            response = requests.post(f"{self.server_url}/unary", json=request_data)
            messages_sent += 1
            bytes_sent += len(request_data['payload'])
        
        elapsed_time = time.time() - start_time
        return {
            'messages_per_second': messages_sent / elapsed_time,
            'bytes_per_second': bytes_sent / elapsed_time,
            'total_messages': messages_sent,
            'total_bytes': bytes_sent
        }

def main():
    client = RestPerformanceClient()
    
    print("Testing latency...")
    results = client.measure_latency(iterations=1000)
    print("\nLatency Results:")
    for metric, value in results.items():
        print(f"{metric}: {value:.2f} ms")
    
    print("\nTesting throughput with different payload sizes...")
    payload_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
    
    for size in payload_sizes:
        print(f"\nPayload size: {size} bytes")
        results = client.measure_throughput(size)
        print(f"Messages per second: {results['messages_per_second']:.2f}")
        print(f"Throughput: {results['bytes_per_second']/1024/1024:.2f} MB/s")
        print(f"Total messages: {results['total_messages']}")
        print(f"Total data: {results['total_bytes']/1024/1024:.2f} MB")

if __name__ == "__main__":
    main()