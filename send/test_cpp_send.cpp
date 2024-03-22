#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>


const int MESSAGE_SIZE = 50 * 1024; // 64KB

int main() {
    // Create a UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    // Server address information
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(12345); // Port number
    serverAddr.sin_addr.s_addr = inet_addr("192.168.0.6"); // IP address of the server

    // Message to send
    char* message = new char[MESSAGE_SIZE];
    memset(message, 'A', MESSAGE_SIZE); // Fill the message with 'A's
    for(int i=0; i< 100; i++) {
    // Measure time before sending
    auto start = std::chrono::high_resolution_clock::now();

    // Send the message
    ssize_t bytesSent = sendto(sockfd, message, strlen(message), 0,
                                (struct sockaddr *)&serverAddr, sizeof(serverAddr));
    if (bytesSent < 0) {
        std::cerr << "Error sending message\n";
        close(sockfd);
        return 1;
    }

    // Measure time after sending
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "Time taken for send operation: " << duration.count() << " microseconds\n";
    }
    // Close the socket
    close(sockfd);

    return 0;
}
