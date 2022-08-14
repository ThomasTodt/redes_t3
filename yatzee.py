import socket
import sys
from bitarray import bitarray
from bitarray.util import hex2ba
from tipos import ERRO, INICIA, RESULTADO, FINALIZA, BASTAO
from combinacoes_BA import UM_PAR, TRIO, DOIS_PARES, FULL_HOUSE, SEQ_BAIXA, SEQ_ALTA, QUADRA, QUINTETO 

ip = '127.0.0.1'
port = 37880

saldos = [0, 0, 0, 0]
jogadores_BA = [bitarray('00'), bitarray('01'), bitarray('10'), bitarray('11')]

eu = int(sys.argv[len(sys.argv)-1]) # numero do jogador
prox = (eu + 1) % 4

portRecv = port + (eu)
portSend = port + (prox)

bastao = False
rodadas = 0


class mensagem:
    header: bitarray('01111110') # precisa?
    # org: 2
    # dst: 2
    # tipo: 4
    # dados: 8
    # paridade: 8

    def __init__(self, org, dst, tipo, dados):
        self.org = jogadores_BA[org]

        self.dst = jogadores_BA[dst]

        self.tipo = tipo

        self.dados = dados
        if(len(self.dados) < 8): # garante o tamanho de dados
            falta = 8 - len(self.dados)
            a = falta * bitarray('0')
            self.dados = self.dados + a # adiciona o que falta ao fim

        self.paridade = self.calc_paridade(org, dst, tipo, dados) # retornar ja um bitarray?

    def send_msg(self):
        msg = self.header + self.org + self.dst + self.tipo + self.dados + self.paridade
        buff = memoryview(msg)
        sock.sendto(buff, (ip, portSend))

    def recv_msg(self):
        data, addr = sock.recvfrom(1024)
        if(data):
            print("RECEBIDO:", '.'.join(f'{c}' for c in data))
            recebido = hex2ba(data.hex())
            print(recebido)

            rec_head = recebido[8]
            if(rec_head != self.header):
                return -1

            self.org      = recebido[8:9]
            self.dst      = recebido[10:11]
            self.tipo     = recebido[12:15]
            self.dados    = recebido[16:23]
            self.paridade = recebido[24:31]

            return 0

    def calc_paridade(org, dst, tipo, dados): # retornar um bitarray
        ...



print('recebe: ', portRecv)
print('envia: ', portSend)


if(eu == 0): # jogador 0, começa com o bastão
    bastao = True
    print("BASTAO")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))


msg = mensagem()
reserva = mensagem() # guarda a ultima enviada para reenviar em caso de erro // manter uma do bastao?
bst = mensagem(eu, prox, BASTAO) # dados vazio funciona?
while True:
    if(bastao):

        if(rodadas == 0):
            input("escolha a combinação que quer fazer (custo = 1)\n") # implementar
            comb = UM_PAR # sla
            custo = bitarray('001') # garantir sempre os 3 bits
            dados = jogadores_BA[eu] + comb + custo
            msg = mensagem(eu, prox, INICIA, dados)

        msg.send_msg() # vai ter configurado a mensagem no else? (caso nao seja a rodada inicial)
        bst.send_msg()
        bastao = False

    else:
        if(msg.recv_msg() == -1): # nao era uma mensagem com o nosso marcador de inicio
            continue

        if(msg.paridade != msg.calc_paridade()):
            ... # ERRO

        elif(msg.tipo == ERRO):
            ...
        
        elif(msg.tipo == INICIA):
            ...

        elif(msg.tipo == RESULTADO):
            ...

        elif(msg.tipo == FINALIZA):
            ...

        elif(msg.tipo == BASTAO):
            ...
