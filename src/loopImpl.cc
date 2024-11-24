#include <cmath>
#include <iostream>
#include <memory>
#include <string>

#include "omp.h"

#include <grpc/grpc.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/security/server_credentials.h>

// generated code
#include "loop.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReader;
using grpc::ServerReaderWriter;
using grpc::ServerWriter;
using grpc::Status;

using loop::LoopService;

// print test results
//#define VERBOSE
#define SHOWRESULTS

// number of iterations
#define N 100000

class LoopImpl final : public LoopService::Service {
 public:
  explicit LoopImpl() {
  }

  /**
   * service implementation
   */
  Status doLoop(::grpc::ServerContext* context, const ::loop::Route* request, ::loop::Route* response) override {

    // --------------------------------------------

    int baseValue = 1; 
    int* a = new int[N];
    int* b = new int[N];

    // initialize comparison
    for (int i = 0; i < N; i++) {
        a[i] = baseValue;
        b[i] = i;
    }

#ifdef VERBOSE
    printf("-------------------------------\n");
    printf(" T,  i)    A   B   tmp\n");
#endif

    int tcnt = 0;
    #pragma omp parallel
    {
#if defined(_OPENMP)
        int id = omp_get_thread_num();
        int nt = omp_get_num_threads();
        printf("---> %02d) %2d threads available\n", id,nt);
#else
        int id = -1; 
#endif
        int cnt = 0;

        //#pragma omp for schedule(dynamic)
        #pragma omp for schedule(static)
        for (int i = 0; i < N; i++) {
          try{
            a[i] = baseValue;
            a[i+1] = b[i+1];
            baseValue = a[i];

            /* no verbose option, and no critical, we want to see interleaving 
               of thread execution */
            //#pragma omp critical 
            {
               printf("%2d ", id);
            }

            // on a single socket we see more collisions
            if ( baseValue != 1 ) {
                cnt++;
#ifdef VERBOSE 
                printf("%2d, %4d) %3d %3d %3d\n", id,i,a[i],b[i],baseValue);
#endif
             }
          } catch (...) {
              printf("caught exception\n");
          }
        }

       #pragma omp critical
       { 
#ifdef SHOWRESULTS 
          printf("T%02d collisions:   %5d\n", id,cnt);
#endif
          tcnt += cnt; 
       }
    }

    // --------------------------------------------

    delete[] a;
    delete[] b;

#ifdef SHOWRESULTS
    printf("Total Collisions: %5d\n", tcnt);
#endif

    response->set_id(request->id());
    response->set_collisions(tcnt);

    return Status::OK;
  }

};

void RunServer() {
  // TODO retrieve from a configuration
  std::string server_address("0.0.0.0:50051");

  LoopImpl service;

  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);
  std::unique_ptr<Server> server(builder.BuildAndStart());

#if defined(_OPENMP)
  std::cout << "Server using openmp" << std::endl;
#else
  std::cout << "Server is not threaded" << std::endl;
#endif

  std::cout << "Server listening on " << server_address << std::endl;
  server->Wait();
}

int main(int argc, char** argv) {
  RunServer();

  return 0;
}
