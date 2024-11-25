# rest_comprehensive_test.py

import requests
import time
import uuid
import json
import sseclient
from urllib.parse import urljoin

class RestComprehensiveTester:
    def __init__(self, server_url='http://localhost:8080'):
        self.server_url = server_url

    def test_unary_call(self):
        print("\n=== Testing Unary Call ===")
        request_data = {
            'request_id': str(uuid.uuid4()),
            'payload': 'Hello, Server!'
        }
        
        print("Sending unary request...")
        response = requests.post(urljoin(self.server_url, '/unary'), json=request_data)
        response_data = response.json()
        print(f"Received response with ID: {response_data['request_id']}")

    def test_server_streaming(self):
        print("\n=== Testing Server Streaming ===")
        params = {
            'message_count': 5,
            'interval_ms': 1000
        }
        
        print("Starting server stream...")
        response = requests.get(
            urljoin(self.server_url, '/stream'), 
            params=params, 
            stream=True,
            headers={'Accept': 'text/event-stream'}
        )
        
        client = sseclient.SSEClient(response)
        try:
            for i, event in enumerate(client.events(), 1):
                data = json.loads(event.data)
                print(f"Received stream response {i}")
        except Exception as e:
            print(f"Error processing stream: {e}")
        finally:
            response.close()

    def test_client_streaming(self):
        print("\n=== Testing Client Streaming ===")
        messages = []
        for i in range(1, 6):
            message = {
                'request_id': f'stream-{i}',
                'payload': f'Client stream message {i}'
            }
            print(f"Sending client stream message {i}")
            messages.append(message)
            time.sleep(0.5)
        
        # Send all messages in one batch
        response = requests.post(urljoin(self.server_url, '/client-stream'), json={'messages': messages})
        response_data = response.json()
        print(f"Client streaming complete. Processed {response_data['messages_processed']} messages")

    def test_bidirectional_streaming(self):
        print("\n=== Testing Bidirectional Streaming ===")
        for i in range(1, 6):
            message = {
                'request_id': f'bistream-{i}',
                'payload': f'Bidirectional message {i}'
            }
            print(f"Sending bidirectional message {i}")
            response = requests.post(urljoin(self.server_url, '/bidirectional'), json=message)
            response_data = response.json()
            print(f"Received bidirectional response {i}")
            time.sleep(0.5)

    def test_ping_pong(self):
        print("\n=== Testing PingPong ===")
        request_data = {
            'client_id': str(uuid.uuid4()),
            'send_timestamp': int(time.time() * 1_000_000)
        }
        
        print("Sending ping...")
        response = requests.post(urljoin(self.server_url, '/ping'), json=request_data)
        response_data = response.json()
        print(f"Received pong from client: {response_data['client_id']}")

    def test_batch_processing(self):
        print("\n=== Testing Batch Processing ===")
        
        # Create test requests
        requests_data = []
        for i in range(5):
            requests_data.append({
                'request_id': f"batch-{i}",
                'payload': f"Batch message {i}"
            })
        
        # Test sequential processing
        print("\nTesting sequential batch processing...")
        batch_request = {
            'requests': requests_data,
            'parallel_process': False
        }
        response = requests.post(urljoin(self.server_url, '/batch'), json=batch_request)
        response_data = response.json()
        print(f"Processed {len(response_data['responses'])} requests sequentially")
        
        # Test parallel processing
        print("\nTesting parallel batch processing...")
        batch_request['parallel_process'] = True
        response = requests.post(urljoin(self.server_url, '/batch'), json=batch_request)
        response_data = response.json()
        print(f"Processed {len(response_data['responses'])} requests in parallel")

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
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    tester = RestComprehensiveTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()