#pragma once

#include <sys/types.h>

int rs_socket(char *device);

int rs_set_timeout(int sockfd, uint useconds);

int rs_send(int sockfd, void *data, size_t bytes);

int rs_recv(int sockfd, void *data, size_t bytes);

int rs_close(int sockfd);