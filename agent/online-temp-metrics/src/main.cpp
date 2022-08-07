// Copyright (c)  2021 Juan Rodriguez Hortala
// Apache License Version 2.0, see https://github.com/juanrh/TemperatureMetrics/blob/master/LICENSE
#include <iostream>
#include "./sensors.h"

// FIXME for raw sockets
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>

// FIXME for boost sockets
#include <boost/asio.hpp>


extern "C" {
    #include "sht31_sensor.h"
}

void failWithMsg(int status_code, const std::string & msg) {
    std::cout << msg << ", error code=["
              << status_code<< "]\n";
    exit(status_code);
}

void failIfNotOk(int status_code, const std::string & msg) {
    if (status_code != SHT31_STATUS_OK) {
        failWithMsg(status_code, msg);
    }
}

int main(int argc, char *argv[]) {
    std::string hostname = argv[1]; // FIXME: useless?
    int port = argc >= 3 ? std::stoi(argv[2]) : 8080;
    std::cout << "Using hostname=[" << hostname << "], port=[" << port << "]\n";

     // Creating socket file descriptor
    int socket_fd;
    // AF_INET for IPv4 socket, SOCK_STREAM for TCP
    if ((socket_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        std::cout << "Error creating socket\n";
        exit(1); //FIXME
    }
    std::cout << "Socket created ok\n";
    int setsockopt_opt = 1;
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                  &setsockopt_opt, sizeof(setsockopt_opt)) < 0) {
        std::cout << "Error with setsockopt\n";
        exit(1); //FIXME
    }
    // bind
    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(hostname.c_str());// INADDR_ANY; any message
    address.sin_port = htons(port);
    int addrlen = sizeof(address);
    if (bind(socket_fd, (struct sockaddr *)&address, 
                                 sizeof(address)) < 0) {
        std::cout << "Bind error\n";
        exit(1); //FIXME
    }
    std::cout << "Socket bind ok" << std::endl;

    // wait for connections: only accept a single connection
    if (listen(socket_fd, 1) < 0){
        std::cout << "listen error\n";
        exit(1); //FIXME
    }
    std::cout << "Socket listen ok" << std::endl;
    int socket_conn;
    if (socket_conn = accept(socket_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen) < 0){
        std::cout << "accept error\n";
        exit(1); //FIXME
    }
    std::cout << "Socket accept ok" << std::endl;

    char buffer[1024] = {0};
    int valread = read( socket_conn , buffer, 1024);
    printf("%s\n",buffer );
    send(socket_conn , buffer ,valread , 0 );
    printf("Hello message sent\n");

    Sht31Sensor sensor{1};

/**
    for (int i=0; i < 3; i++) {
        auto measurementOpt = sensor.measure();
        Measurement* measurement = std::get_if<Measurement>(& measurementOpt);
        if  (measurement != nullptr) {
            std::cout << "Measurement: " << *measurement << "\n";
        } else {
            std::string errorMsg = std::get<std::string>(measurementOpt);
            std::cout << "Measurement error: " << errorMsg << "\n";
        }
    }
*/
    return 0;
}
