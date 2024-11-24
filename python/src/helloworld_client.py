import grpc
import helloworld_pb2
import helloworld_pb2_grpc

def run():
    # Connect to the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        
        # Create a request message
        request = helloworld_pb2.HelloRequest(name="Divyam")
        
        # Call the SayHello method on the server
        response = stub.SayHello(request)
        
        print(f"Greeter server responded with: {response.message}")

if __name__ == "__main__":
    run()
