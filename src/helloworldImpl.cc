#include <iostream>
#include <memory>
#include <string>
#include <chrono>
#include <thread>
#include <vector>
#include <sys/resource.h>
#include <thread>
#include <future>

#include <grpcpp/grpcpp.h>
#include "helloworld.pb.h"
#include "helloworld.grpc.pb.h"
#include "performance_test.pb.h"
#include "performance_test.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using grpc::ServerReader;
using grpc::ServerWriter;
using grpc::ServerReaderWriter;

// Helper functions for metrics
class MetricsCollector {
public:
    static google::protobuf::Timestamp getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto seconds = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
        auto nanos = std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count() % 1000000000;
        
        google::protobuf::Timestamp timestamp;
        timestamp.set_seconds(seconds);
        timestamp.set_nanos(nanos);
        return timestamp;
    }

    static perftest::ProcessingMetrics collectMetrics(
        const std::chrono::system_clock::time_point& start_time,
        const std::chrono::system_clock::time_point& end_time) {
        
        perftest::ProcessingMetrics metrics;
        
        // Processing time
        auto processing_time = std::chrono::duration_cast<std::chrono::microseconds>(
            end_time - start_time).count();
        metrics.set_processing_time_us(processing_time);
        
        // Memory usage
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        metrics.set_memory_used_bytes(usage.ru_maxrss * 1024); // Convert to bytes
        
        // CPU usage (simplified)
        metrics.set_cpu_usage(0.0); // Would need more complex implementation for accurate CPU usage
        
        return metrics;
    }

    static size_t getPayloadSize(perftest::PayloadSize size) {
        switch (size) {
            case perftest::PayloadSize::EMPTY: return 0;
            case perftest::PayloadSize::SMALL: return 1024;
            case perftest::PayloadSize::MEDIUM: return 10 * 1024;
            case perftest::PayloadSize::LARGE: return 100 * 1024;
            case perftest::PayloadSize::XLARGE: return 1024 * 1024;
            default: return 0;
        }
    }
};

// Original Greeter service remains unchanged
class GreeterServiceImpl final : public helloworld::Greeter::Service {
    Status SayHello(ServerContext* context, const helloworld::HelloRequest* request,
                    helloworld::HelloReply* reply) override {
        std::string prefix("Hello MF ");
        reply->set_message(prefix + request->name());
        return Status::OK;
    }
};

// Performance Test service implementation
class PerformanceTestServiceImpl final : public perftest::PerformanceTest::Service {
public:
    Status UnaryCall(ServerContext* context, const perftest::TestRequest* request,
                    perftest::TestResponse* response) override {
        auto start_time = std::chrono::system_clock::now();
        
        response->set_request_id(request->request_id());
        *response->mutable_received_at() = MetricsCollector::getCurrentTimestamp();
        
        // Process request
        for (int i = 0; i < 5; i++) { // Example: Add 5 data structures
        auto* data = response->add_payload();
        data->set_key("key" + std::to_string(i));
        data->set_value("value" + std::to_string(i));
    }
        
        auto end_time = std::chrono::system_clock::now();
        *response->mutable_processed_at() = MetricsCollector::getCurrentTimestamp();
        
        *response->mutable_metrics() = MetricsCollector::collectMetrics(start_time, end_time);
        return Status::OK;
    }

    Status ServerStreaming(ServerContext* context, const perftest::StreamRequest* request,
                         ServerWriter<perftest::TestResponse>* writer) override {
        auto start_time = std::chrono::system_clock::now();
        
        for (int i = 0; i < request->message_count(); i++) {
            perftest::TestResponse response;
            response.set_request_id(std::to_string(i));
            
            // Generate payload based on requested size
            // std::string payload(MetricsCollector::getPayloadSize(request->payload_size()), 'x');
            // response.set_payload(payload);
            
            *response.mutable_received_at() = MetricsCollector::getCurrentTimestamp();

            for (int j = 0; j < 3; j++) { // Example: Add 3 data structures per message
                auto* data = response.add_payload();
                data->set_key("stream_key" + std::to_string(j));
                data->set_value("stream_value" + std::to_string(j));
            }

            *response.mutable_processed_at() = MetricsCollector::getCurrentTimestamp();
            
            writer->Write(response);
            
            if (request->interval_ms() > 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(request->interval_ms()));
            }
        }
        
        auto end_time = std::chrono::system_clock::now();
        return Status::OK;
    }

    Status ClientStreaming(ServerContext* context, ServerReader<perftest::TestRequest>* reader,
                         perftest::StreamResponse* response) override {
        auto start_time = std::chrono::system_clock::now();
        
        perftest::TestRequest request;
        int count = 0;
        while (reader->Read(&request)) {
            count++;
        }
        
        auto end_time = std::chrono::system_clock::now();
        
        response->set_messages_processed(count);
        *response->mutable_aggregate_metrics() = MetricsCollector::collectMetrics(start_time, end_time);
        
        return Status::OK;
    }

    Status BidirectionalStreaming(ServerContext* context,
                                ServerReaderWriter<perftest::TestResponse, perftest::TestRequest>* stream) override {
        perftest::TestRequest request;
        while (stream->Read(&request)) {
            auto start_time = std::chrono::system_clock::now();
            
            perftest::TestResponse response;
            response.set_request_id(request.request_id());
            // response.set_payload(request.payload());
            *response.mutable_received_at() = MetricsCollector::getCurrentTimestamp();

            for (int i = 0; i < 2; i++) { // Adding 2 data structures per request
                auto* data = response.add_payload();
                data->set_key("bi_key" + std::to_string(i));
                data->set_value("bi_value" + std::to_string(i));
            }

            *response.mutable_processed_at() = MetricsCollector::getCurrentTimestamp();
            
            auto end_time = std::chrono::system_clock::now();
            *response.mutable_metrics() = MetricsCollector::collectMetrics(start_time, end_time);
            
            stream->Write(response);
        }
        return Status::OK;
    }

    Status PingPong(ServerContext* context, const perftest::PingRequest* request,
                   perftest::PongResponse* response) override {
        response->set_client_id(request->client_id());
        *response->mutable_client_timestamp() = request->send_timestamp();
        *response->mutable_server_timestamp() = MetricsCollector::getCurrentTimestamp();
        return Status::OK;
    }

    Status BatchProcess(ServerContext* context, const perftest::BatchRequest* request,
                       perftest::BatchResponse* response) override {
        auto start_time = std::chrono::system_clock::now();
        
        if (request->parallel_process()) {
            // Parallel processing
            std::vector<std::future<perftest::TestResponse>> futures;
            for (const auto& req : request->requests()) {
                futures.push_back(std::async(std::launch::async, [this, &req]() {
                    perftest::TestResponse resp;
                    auto start = std::chrono::system_clock::now();
                    
                    resp.set_request_id(req.request_id());
                    for (const auto& data : req.payload()) {
                        auto* new_payload = resp.add_payload();  
                        new_payload->CopyFrom(data);            
                    }
                    *resp.mutable_received_at() = MetricsCollector::getCurrentTimestamp();
                    *resp.mutable_processed_at() = MetricsCollector::getCurrentTimestamp();
                    
                    auto end = std::chrono::system_clock::now();
                    *resp.mutable_metrics() = MetricsCollector::collectMetrics(start, end);
                    
                    return resp;
                }));
            }

            for (auto& future : futures) {
                *response->add_responses() = future.get();
            }
        } else {
            // Sequential processing
            for (const auto& req : request->requests()) {
                auto* resp = response->add_responses();
                auto start = std::chrono::system_clock::now();
                
                resp->set_request_id(req.request_id());
                for (const auto& data : req.payload()) {
                    auto* new_payload = resp->add_payload();
                    new_payload->CopyFrom(data);
                }
                *resp->mutable_received_at() = MetricsCollector::getCurrentTimestamp();
                *resp->mutable_processed_at() = MetricsCollector::getCurrentTimestamp();
                
                auto end = std::chrono::system_clock::now();
                *resp->mutable_metrics() = MetricsCollector::collectMetrics(start, end);
            }
        }
        
        auto end_time = std::chrono::system_clock::now();
        *response->mutable_batch_metrics() = MetricsCollector::collectMetrics(start_time, end_time);
        
        return Status::OK;
    }
};

void RunServer() {
    try{
        std::string server_address("0.0.0.0:50051");
        
        GreeterServiceImpl greeter_service;
        PerformanceTestServiceImpl perf_service;

        ServerBuilder builder;
        builder.SetMaxReceiveMessageSize(1024 * 1024 * 10);  // 10MB
        builder.SetMaxSendMessageSize(1024 * 1024 * 10);     // 10MB
        builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
        builder.RegisterService(&greeter_service);
        builder.RegisterService(&perf_service);

        std::cout << "Initializing gRPC server..." << std::endl;

        std::unique_ptr<Server> server(builder.BuildAndStart());
        std::cout << "Server listening on " << server_address << std::endl;
        server->Wait();
    }catch(const std::exception& e) {
        std::cerr << "Server failed to start: " << e.what() << std::endl;
    }
}

int main(int argc, char** argv) {
    RunServer();
    return 0;
}