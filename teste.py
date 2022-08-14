import socket
import sys
from bitfield import binary
import tipos

ip = '127.0.0.1'
port = 37880


class mensagem:
    header: Binary(01111110)
    tipo: 000
    jogador: 00
    dados: 00000000000
    paridade: 00000000

    def __init__(self, tipo, jogador, dados):
        self.tipo = tipo
        self.jogador = B(jogador)
        self.dados = dados
        self.paridade = self.calcParidade(tipo, jogador, dados)



# TESTE = 'TESTANDO'

# TESTE = sys.argv[len(sys.argv)-1]

portRecv = port + ( int(sys.argv[len(sys.argv)-1]) % 4)
portSend = port + ( (int(sys.argv[len(sys.argv)-1]) + 1) % 4)
print('recebe: ', portRecv)
print('envia: ', portSend)

bastao = False
if(sys.argv[len(sys.argv)-1] == '0'):
    bastao = True
    print("BASTAO")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))

while True:
    if(bastao):
        TESTE = input('o que eh pra mandar?\n')
        sock.sendto(bytes(TESTE, "ascii"), (ip, portSend))

    else:
        data, addr = sock.recvfrom(1024)
        if(data):
            print("RECEBIDO: ", data)

