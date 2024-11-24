import grpc
import loop_pb2
import loop_pb2_grpc

def run():
    try:
       channel = grpc.insecure_channel('localhost:50051')
       stub = loop_pb2_grpc.LoopServiceStub(channel)
       argIn = loop_pb2.Route()
       argIn.id = 1
       argIn.num_loops = 100
       response = stub.doLoop(argIn)
       dir(response)
       print("Done:", (1==response.id), ", collisions =", response.num_loops)
    except:
       print("failed to connect/send to service")
       raise


if __name__ == '__main__':
    run()
