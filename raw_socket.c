#include <linux/if.h>
#include <linux/if_packet.h>
#include <net/ethernet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include "raw_socket.h"
#include "debug.h"
#include "error.h"

int rs_socket(char *device)
{
    int soquete;
    struct ifreq ir;
    struct sockaddr_ll endereco;
    struct packet_mreq mr;

    TRY(soquete = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))); /*cria socket*/

    memset(&ir, 0, sizeof(struct ifreq)); /*dispositivo eth0*/
    memcpy(ir.ifr_name, device, strlen(device) + 1);
    TRY(ioctl(soquete, SIOCGIFINDEX, &ir));

    memset(&endereco, 0, sizeof(endereco)); /*IP do dispositivo*/
    endereco.sll_family = AF_PACKET;
    endereco.sll_protocol = htons(ETH_P_ALL);
    endereco.sll_ifindex = ir.ifr_ifindex;
    TRY(bind(soquete, (struct sockaddr *)&endereco, sizeof(endereco)));

    memset(&mr, 0, sizeof(mr)); /*Modo Promiscuo*/
    mr.mr_ifindex = ir.ifr_ifindex;
    mr.mr_type = PACKET_MR_PROMISC;
    TRY(setsockopt(soquete, SOL_PACKET, PACKET_ADD_MEMBERSHIP, &mr, sizeof(mr)));

    return soquete;
}

int rs_set_timeout(int sockfd, uint useconds)
{
    struct timeval timeout;
    timeout.tv_sec = useconds / (uint)1e6;
    timeout.tv_usec = useconds % (uint)1e6;

    TRY(setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)));

    return 0;
}

int rs_send(int sockfd, void *data, size_t bytes)
{
    TRY(write(sockfd, data, bytes));
    return 0;
}

int rs_recv(int sockfd, void *data, size_t bytes)
{
    TRY(read(sockfd, data, bytes));
    return 0;
}

int rs_close(int sockfd)
{
    TRY(close(sockfd));
    return 0;
}