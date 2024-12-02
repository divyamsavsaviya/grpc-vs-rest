#include <httplib.h>
#include <nlohmann/json.hpp>
#include <chrono>
#include <thread>
#include <string>
#include <vector>
#include <mutex>
#include <queue>
#include <sstream>
#include <iomanip>

using json = nlohmann::json;

class RestServer {
private:
    httplib::Server svr;
    std::mutex stream_mutex;

    std::string getCurrentTimeStr() {
        auto now = std::chrono::system_clock::now();
        auto now_c = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&now_c), "%Y-%m-%d %X");
        return ss.str();
    }

public:
    RestServer() {
        // Unary Call
        svr.Post("/unary", [this](const httplib::Request& req, httplib::Response& res) {
            
            auto start_time = std::chrono::system_clock::now();
            json request = json::parse(req.body);
            
            json response;
            response["request_id"] = request["request_id"];
            response["received_at"] = std::chrono::duration_cast<std::chrono::microseconds>(
                start_time.time_since_epoch()).count();

            response["payload"] = json::array();
            for (const auto& data : request["payload"]) {
                json resp;
                resp["key"] = data["key"];
                resp["value"] = data["value"];
                resp["age"] = data["age"]; 
                resp["gradepoint"] = data["gradepoint"];
                response["payload"].push_back(resp);
            }

            auto end_time = std::chrono::system_clock::now();
            response["processed_at"] = std::chrono::duration_cast<std::chrono::microseconds>(
                end_time.time_since_epoch()).count();
            
            response["metrics"]["processing_time_us"] = std::chrono::duration_cast<std::chrono::microseconds>(
                end_time - start_time).count();
            
            res.set_content(response.dump(), "application/json");
        });

        // Client Streaming
        svr.Post("/client-stream", [this](const httplib::Request& req, httplib::Response& res) {
            
            json request = json::parse(req.body);
            json response;
            response["messages_processed"] = request["messages"].size();
            
            res.set_content(response.dump(), "application/json");
        });

        // Bidirectional Streaming
        svr.Post("/bidirectional", [this](const httplib::Request& req, httplib::Response& res) {
            
            json request = json::parse(req.body);
            json response = request;  // Echo back the request
            
            res.set_content(response.dump(), "application/json");
        });

        // Server Streaming
        svr.Get("/stream", [this](const httplib::Request& req, httplib::Response& res) {
            
            res.set_header("Content-Type", "text/event-stream");
            res.set_header("Cache-Control", "no-cache");
            res.set_header("Connection", "keep-alive");
            
            int message_count = std::stoi(req.get_param_value("message_count"));
            int interval_ms = std::stoi(req.get_param_value("interval_ms"));
            int payload_size = std::stoi(req.get_param_value("payload_size"));
            int num_structures = std::stoi(req.get_param_value("num_structures"));

            for (int i = 1; i <= message_count; i++) {
                json response;
                response["sequence_number"] = i;
                response["payload"] = json::array();

                for (int j = 0; j < num_structures; j++) {
                    response["payload"].push_back({
                        {"key", "key_" + std::to_string(j)},
                        {"value", std::string(payload_size, 'x')}
                    });
                }

                std::string message = "data: " + response.dump() + "\n\n";  
                res.set_content(message, "text/event-stream");

                std::this_thread::sleep_for(std::chrono::milliseconds(interval_ms));    
            }
        });

        // Ping-Pong
        svr.Post("/ping", [this](const httplib::Request& req, httplib::Response& res) {
            auto start_time = std::chrono::system_clock::now();
            json request = json::parse(req.body);
            json response;
            response["client_id"] = request["client_id"];
            response["client_timestamp"] = request["send_timestamp"];
            response["server_timestamp"] = std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
            response["payload"] = json::array();

            for (const auto& data : request["payload"]) {
                json resp;
                resp["key"] = data["key"];
                resp["value"] = data["value"];
                resp["age"] = data["age"];
                resp["gradepoint"] = data["gradepoint"];
                response["payload"].push_back(resp);
            }

            auto end_time = std::chrono::system_clock::now();
            response["metrics"]["processing_time_us"] =
                std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
            
            res.set_content(response.dump(), "application/json");
        });

        // Batch Processing
        svr.Post("/batch", [this](const httplib::Request& req, httplib::Response& res) {
            
            auto start_time = std::chrono::system_clock::now();
            json request = json::parse(req.body);
            json response;
            response["responses"] = json::array();
            
            for (const auto& data : request["requests"]) {
                json resp;
                resp["request_id"] = data["request_id"];
                resp["payload"] = json::array();

                for (const auto& item : data["payload"]) {
                    resp["payload"].push_back({
                        {"key", item["key"]},
                        {"value", item["value"]},
                        {"age", item["age"]}, 
                        {"gradepoint", item["gradepoint"]}
                    });
                }

                response["responses"].push_back(resp);
            }

            auto end_time = std::chrono::system_clock::now();
            response["metrics"]["processing_time_us"] =
                std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

            res.set_content(response.dump(), "application/json");
        });
    }

    void run() {
        std::cout << "REST Server starting on port 8080..." << std::endl;
        svr.listen("0.0.0.0", 8080);
    }
};

int main() {
    RestServer server;
    server.run();
    return 0;
}