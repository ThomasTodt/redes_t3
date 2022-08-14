import socket
import sys
from bitarray import bitarray
from bitarray.util import hex2ba
from tipos import ERRO, INICIA, RESULTADO, FINALIZA, BASTAO

ip = '127.0.0.1'
port = 37880

portRecv = port + ( int(sys.argv[len(sys.argv)-1]) % 4)
portSend = port + ( (int(sys.argv[len(sys.argv)-1]) + 1) % 4)

bastao = False


class mensagem:
    header: bitarray('01111110')
    # tipo: 000
    # jogador: 00
    # dados: 00000000000
    # paridade: 00000000

    def __init__(self, tipo, jogador, dados):
        self.tipo = tipo
        self.jogador = '{0:b}'.format(jogador)
        self.dados = '{0:b}'.format(dados)
        self.paridade = '{0:b}'.format(self.calcParidade(tipo, jogador, dados)) # retornar ja um bitarray?

    def send_msg(self):
        msg = self.header + self.tipo + self.jogador + self.dados + self.paridade
        buff = memoryview(msg)
        sock.sendto(buff, (ip, portSend))



print('recebe: ', portRecv)
print('envia: ', portSend)


if(sys.argv[len(sys.argv)-1] == '0'):
    bastao = True
    print("BASTAO")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))

while True:
    if(bastao):
        TESTE = input('o que eh pra mandar?\n')
        # sock.sendto(bytes(TESTE, "ascii"), (ip, portSend))
        a = bitarray('00')
        f = bitarray('101010')
        a = a + f
        v = memoryview(a)
        # print(v.tobytes())
        sock.sendto(v, (ip, portSend))

    else:
        data, addr = sock.recvfrom(1024)
        if(data):
            # print("RECEBIDO: ", data)
            print("RECEBIDO:", '.'.join(f'{c}' for c in data))
            # print(data)
            recebido = hex2ba(data.hex())
            print(recebido)
            ok = input('de o ok\n')

