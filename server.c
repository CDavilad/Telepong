#include "serversync.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>



ClientData* waitingClients[100];
Session* sessions[50];
int waitingCount = 0;
int sessionCount = 0;

int main(int argc, char *argv[]) {
    int serverPort = 80;
    if (argc > 1) {
        serverPort = atoi(argv[1]); 
    }
    char *logName = argv[2];
    initLogFile(logName);
    
    int serverSocket = startServer(serverPort);
    if (serverSocket == -1) {
        return 1;
    }
    printf("Waiting for incoming connections...\n");

    while (1) {
        ClientData* newClient = acceptClient(serverSocket);
        if (newClient) {
            
            
            waitingClients[waitingCount++] = newClient;
            if (waitingCount == 1) {
                printf("Esperando al otro cliente...\n");
                pthread_t clientThread;
                int threadStatus = pthread_create(&clientThread, NULL, ClientHandler, (void*)newClient);

                if (threadStatus != 0) {
                    perror("Could not create client thread");
                    close(newClient->socket);
                    free(newClient);
                } else {
                    pthread_detach(clientThread);
                }

            }  else if (waitingCount == 2) {
                createNewSession(waitingClients, sessions, &waitingCount, &sessionCount);
                pthread_t clientThread;
                int threadStatus = pthread_create(&clientThread, NULL, ClientHandler, (void*)newClient);

                if (threadStatus != 0) {
                    perror("Could not create client thread");
                    close(newClient->socket);
                    free(newClient);
                } else {
                    pthread_detach(clientThread);
                }
                usleep(3000000);
                iniciarJuego(newClient);
            }


        }
    }
    close(serverSocket);
    return 0;
}
