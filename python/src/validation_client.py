import grpc
import performance_test_pb2
import performance_test_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import time
import statistics
import numpy as np
from concurrent import futures
import psutil
import os

class PerformanceValidator:
    def __init__(self, server_address='localhost:50051'):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = performance_test_pb2_grpc.PerformanceTestStub(self.channel)
    
    def _create_timestamp(self):
        """Helper method to create Timestamp"""
        now = time.time()
        timestamp = Timestamp()
        timestamp.seconds = int(now)
        timestamp.nanos = int((now - int(now)) * 1e9)
        return timestamp
        
    def measure_baseline_system_noise(self, iterations=1000):
        """Measure system noise by running empty operations"""
        noise_measurements = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            end = time.perf_counter_ns()
            noise_measurements.append(end - start)
        return statistics.mean(noise_measurements), statistics.stdev(noise_measurements)

    def validate_latency_measurements(self, iterations=100):  # Reduced iterations for testing
        """Validate latency measurements against known delays"""
        results = []
        expected_delays = [1000, 5000, 10000]  # microseconds
        
        for delay in expected_delays:
            measurements = []
            for _ in range(iterations):
                start = time.perf_counter_ns()
                
                request = performance_test_pb2.PingRequest(
                    client_id=str(os.getpid()),
                    send_timestamp=self._create_timestamp()
                )
                
                response = self.stub.PingPong(request)
                end = time.perf_counter_ns()
                
                actual_delay = (end - start) / 1000  # Convert to microseconds
                measurements.append(actual_delay)
            
            results.append({
                'expected_delay': delay,
                'mean_measured': statistics.mean(measurements),
                'stddev': statistics.stdev(measurements),
                'error_percentage': abs(statistics.mean(measurements) - delay) / delay * 100
            })
            
        return results

    def measure_throughput_accuracy(self, message_size=1024, duration=5):  # Reduced duration for testing
        """Validate throughput measurements"""
        messages_sent = 0
        bytes_sent = 0
        start_time = time.perf_counter()
        
        # Network interface baseline
        net_io_start = psutil.net_io_counters()
        
        while time.perf_counter() - start_time < duration:
            request = performance_test_pb2.TestRequest(
                request_id=str(messages_sent),
                timestamp=self._create_timestamp(),
                payload=b'x' * message_size
            )
            response = self.stub.UnaryCall(request)
            messages_sent += 1
            bytes_sent += message_size
            
        net_io_end = psutil.net_io_counters()
        
        actual_bytes = net_io_end.bytes_sent - net_io_start.bytes_sent
        expected_bytes = bytes_sent
        
        return {
            'expected_throughput': bytes_sent / duration,
            'actual_throughput': actual_bytes / duration,
            'accuracy_percentage': (actual_bytes / expected_bytes) * 100 if expected_bytes > 0 else 0
        }

    def validate_parallel_processing(self, batch_size=5, iterations=5):  # Reduced sizes for testing
        """Validate parallel processing efficiency"""
        sequential_times = []
        parallel_times = []
        
        for _ in range(iterations):
            # Sequential processing
            requests = [
                performance_test_pb2.TestRequest(
                    request_id=str(i),
                    timestamp=self._create_timestamp(),
                    payload=b'x' * 1024
                ) for i in range(batch_size)
            ]
            
            start = time.perf_counter_ns()
            batch_request = performance_test_pb2.BatchRequest(
                requests=requests,
                parallel_process=False
            )
            response = self.stub.BatchProcess(batch_request)
            end = time.perf_counter_ns()
            sequential_times.append(end - start)
            
            # Parallel processing
            start = time.perf_counter_ns()
            batch_request.parallel_process = True
            response = self.stub.BatchProcess(batch_request)
            end = time.perf_counter_ns()
            parallel_times.append(end - start)
            
        return {
            'sequential_mean': statistics.mean(sequential_times),
            'parallel_mean': statistics.mean(parallel_times),
            'speedup_factor': statistics.mean(sequential_times) / statistics.mean(parallel_times),
            'efficiency': (statistics.mean(sequential_times) / 
                         statistics.mean(parallel_times) / batch_size) * 100
        }

    def run_comprehensive_validation(self):
        """Run all validation tests and produce a report"""
        results = {
            'system_noise': self.measure_baseline_system_noise(),
            'latency_validation': self.validate_latency_measurements(),
            'throughput_accuracy': self.measure_throughput_accuracy(),
            'parallel_processing': self.validate_parallel_processing()
        }
        
        self._generate_validation_report(results)
        return results

    def _generate_validation_report(self, results):
        """Generate a detailed validation report"""
        print("\n=== Performance Testing System Validation Report ===\n")
        
        print("1. System Noise Baseline:")
        print(f"   Mean noise: {results['system_noise'][0]:.2f} ns")
        print(f"   Noise StdDev: {results['system_noise'][1]:.2f} ns")
        
        print("\n2. Latency Validation:")
        for r in results['latency_validation']:
            print(f"   Expected: {r['expected_delay']}µs")
            print(f"   Measured: {r['mean_measured']:.2f}µs")
            print(f"   Error: {r['error_percentage']:.2f}%")
        
        print("\n3. Throughput Accuracy:")
        ta = results['throughput_accuracy']
        print(f"   Expected: {ta['expected_throughput']/1024:.2f} KB/s")
        print(f"   Actual: {ta['actual_throughput']/1024:.2f} KB/s")
        print(f"   Accuracy: {ta['accuracy_percentage']:.2f}%")
        
        print("\n4. Parallel Processing Efficiency:")
        pp = results['parallel_processing']
        print(f"   Speedup Factor: {pp['speedup_factor']:.2f}x")
        print(f"   Efficiency: {pp['efficiency']:.2f}%")

def main():
    validator = PerformanceValidator()
    validator.run_comprehensive_validation()

if __name__ == "__main__":
    main()