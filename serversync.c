#include "serversync.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>

extern ClientData* waitingClients[10];
extern Session* sessions[5];
extern int waitingCount;
extern int sessionCount;
FILE* logFile;

void logMessage(char* message) {
    if (logFile) {
        fprintf(logFile, "%s\n", message);
        fflush(logFile);
    }
}

void initLogFile(const char* logName) {
    logFile = fopen(logName, "w");
    if (logFile == NULL) {
        perror("Could not create file");
    }
}

int startServer(int port) {
    int listenSocket;
    struct sockaddr_in server;

    listenSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (listenSocket == -1) {
        perror("Could not create socket");
        logMessage("Could not create socket");
        return -1;
    }
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(port);

    if (bind(listenSocket, (struct sockaddr*)&server, sizeof(server)) == -1) {
        perror("Bind failed");
        logMessage("bind failed");
        return -1;
    }

    listen(listenSocket, 3);
    return listenSocket;
}

ClientData* acceptClient(int serverSocket) {
    ClientData* newClient = (ClientData*) malloc(sizeof(ClientData));
    socklen_t c = sizeof(struct sockaddr_in);

    newClient->socket = accept(serverSocket, (struct sockaddr*) & newClient->address, &c);
    if (newClient->socket == -1) {
        free(newClient);
        return NULL;
    }

    return newClient;
}

bool isClientInSession(ClientData* client) {
    for(int i = 0; i < sessionCount; i++) {
        if(sessions[i]->client1 == client || sessions[i]->client2 == client) {
            return true;
        }
    }
    return false;
}

void* ClientHandler(void* clientData) {
    ClientData* data = (ClientData*)clientData;
    int socket = data->socket;
    struct sockaddr_in clientAddress = data->address;
    char message[100];

    while (!isClientInSession(data)) {
        usleep(100000); // Espera 100 ms
    }

    for (int i = 0; i < sessionCount; i++) {
        if (sessions[i]->client1 == data || sessions[i]->client2 == data) {
            // Encontramos la sesión, averigua quién es el otro cliente
            int id = (sessions[i]->client1 == data) ? 1 : 2;
            // Ahora puedes enviar el mensaje al otro cliente
            if(id == 1){
                char idMessage[] = "Eres jugador 1\n";
                send(socket, idMessage, strlen(idMessage), 0);
            } else {
                char idMessage[] = "Eres jugador 2\n";
                send(socket, idMessage, strlen(idMessage), 0);
            }

            break;
        }
    }

    int bytesRead;
    while ((bytesRead = recv(socket, message, sizeof(message) - 1, 0)) > 0) {
        message[bytesRead] = '\0';
        char tempMessage[50];
        strcpy(tempMessage, message);
        char AccionLogger[256];
        snprintf(AccionLogger, sizeof(AccionLogger), "Received from %s:%d: %s", inet_ntoa(clientAddress.sin_addr), ntohs(clientAddress.sin_port), message);
        logMessage(AccionLogger);
        printf("Received from %s:%d: %s\n", inet_ntoa(clientAddress.sin_addr), ntohs(clientAddress.sin_port), message);
        char * comando;
        comando = strtok (message," ");
        if (strcmp("Movement", comando) == 0) {
            for (int i = 0; i < sessionCount; i++) {
                if (sessions[i]->client1 == data || sessions[i]->client2 == data) {
                    // Encontramos la sesión, averigua quién es el otro cliente
                    ClientData* otherClient = (sessions[i]->client1 == data) ? sessions[i]->client2 : sessions[i]->client1;

                    send(otherClient->socket, tempMessage, strlen(tempMessage), 0);
                    send(socket, tempMessage, strlen(tempMessage), 0);
                    break;
                }
            }
        }
    }

    if (bytesRead == 0) {
        printf("Client disconnected.\n");
        logMessage("Client disconnected.\n");
    } else {
        perror("Receive failed");
        logMessage("Receive failed");
    }
    close(socket);
    free(clientData);
}

void createNewSession(ClientData* waitingClients[], Session* sessions[], int* waitingCount, int* sessionCount) {
    Session* newSession = (Session*) malloc(sizeof(Session));
    newSession->client1 = waitingClients[--(*waitingCount)];
    newSession->client2 = waitingClients[--(*waitingCount)];
    sessions[*sessionCount] = newSession;

    printf("Nueva sesion creada con ID %d entre %s y %s\n", 
        *sessionCount,
        inet_ntoa(newSession->client1->address.sin_addr),
        inet_ntoa(newSession->client2->address.sin_addr));

    char sesionLogger[256];
    snprintf(sesionLogger, sizeof(sesionLogger), "Nueva sesion creada con ID %d entre %s y %s\n",
         *sessionCount,
         inet_ntoa(newSession->client1->address.sin_addr),
         inet_ntoa(newSession->client2->address.sin_addr));
    
    logMessage(sesionLogger);



    char sessionResponse[] = "Eres jugador 2\n";
    send(sessions[*sessionCount]->client1->socket, sessionResponse, strlen(sessionResponse), 0);
    send(sessions[*sessionCount]->client2->socket, sessionResponse, strlen(sessionResponse), 0);
    (*sessionCount)++;
}

void iniciarJuego(ClientData* newClient) {
    char* message = "Waiting...\n";
    send(waitingClients[0]->socket, message, strlen(message), 0);  // Enviar al primer cliente
    send(newClient->socket, message, strlen(message), 0);           // Enviar al segundo cliente (nuevo cliente)
}