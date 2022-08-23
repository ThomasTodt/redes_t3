# TODO
# Implementar varias rodadas
# Implementar funcoes com logica do jogo

import socket
import sys
from bitarray import bitarray
from bitarray.util import hex2ba, ba2int, int2ba, parity
from random import randint
from tipos import ERRO, INICIA, JOGA, RESULTADO, FINALIZA, BASTAO
from combinacoes_BA import UM_PAR, TRIO, DOIS_PARES, FULL_HOUSE, SEQ_BAIXA, SEQ_ALTA, QUADRA, QUINTETO 

ip = '127.0.0.1'
port = 37880

saldos = [0, 0, 0, 0]
jogadores_BA = [bitarray('00'), bitarray('01'), bitarray('10'), bitarray('11')]

eu = int(sys.argv[len(sys.argv)-1]) # numero do jogador
prox = (eu + 1) % 4
jogador_inicial = 0

portRecv = port + (eu)
portSend = port + (prox)

bastao = False
rodada = 0

combinacoes_BA = [UM_PAR, TRIO, DOIS_PARES, FULL_HOUSE, 
                    SEQ_BAIXA, SEQ_ALTA, QUADRA, QUINTETO]

class mensagem:
    header = bitarray('01111110') # precisa?
    # org: 2
    # dst: 2
    # tipo: 4
    # dados: 8
    # paridade: 8

    def __init__(self, org, dst, tipo, dados=bitarray('')):
        self.org = jogadores_BA[org]

        self.dst = jogadores_BA[dst]

        self.tipo = tipo

        self.dados = dados
        if(len(self.dados) < 8): # garante o tamanho de dados
            falta = 8 - len(self.dados)
            a = falta * bitarray('0')
            self.dados = self.dados + a # adiciona o que falta ao fim

        self.paridade = self.calc_paridade() # retornar ja um bitarray?

    def send_msg(self):
        msg = mensagem.header + self.org + self.dst + self.tipo + self.dados + self.paridade
        buff = memoryview(msg)
        sock.sendto(buff, (ip, portSend))

    def recv_msg(self):
        data, addr = sock.recvfrom(1024)
        if(data):
            print("RECEBIDO:", '.'.join(f'{c}' for c in data))
            recebido = hex2ba(data.hex())
            print(recebido)

            rec_head = recebido[0:8]
            if(rec_head != self.header):
                return -1

            self.org      = recebido[8:10]
            self.dst      = recebido[10:12]
            self.tipo     = recebido[12:16]
            self.dados    = recebido[16:24]
            self.paridade = recebido[24:32]

            # print(f"org: {self.org} | dst: {self.dst} | tipo: {self.tipo} | dados: {self.dados} | paridade: {self.paridade}")

            return 0

    def calc_paridade(self): # retornar um bitarray
        return int2ba(parity(self.org + self.dst + self.tipo + self.dados), length=8)


def jogar_dados():
    return [randint(1,6), randint(1,6), randint(1,6), randint(1,6), randint(1,6)]

def checar_comb(dadinhos, comb):
    dadinhos.sort()
    return True

def pontos_comb(comb):
    return 0

print('recebe: ', portRecv)
print('envia: ', portSend)


if(eu == 0): # jogador 0, começa com o bastão
    bastao = True
    print("BASTAO")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))


msg: mensagem
reserva: mensagem # guarda a ultima enviada para reenviar em caso de erro // manter uma do bastao?
bst = mensagem(eu, prox, BASTAO) # dados vazio funciona?
msg = mensagem(eu, prox, BASTAO)
reserva = mensagem(eu, prox, BASTAO)
nova_rodada = True
nao_envia = False

while True:
    if(bastao):

        if(eu == jogador_inicial and nova_rodada == True):
            print(f"====== Yatzee | Jogador {eu} | Rodada {rodadas} ======")
            print("1 - Um Par")
            print("2 - Um Trio")
            print("3 - Dois Pares")
            print("4 - Full House")
            print("5 - Sequência Baixa")
            print("6 - Sequência Alta")
            print("7 - Quadra")
            print("8 - Quinteto")
            userinput = int(input("\nQual combinação quer fazer? (custo = 1) [1-8]: "))
            comb = int2ba(userinput - 1, length=3)
            custo = bitarray('001') # garantir sempre os 3 bits
            dados = jogadores_BA[eu] + comb + custo
            msg = mensagem(eu, prox, INICIA, dados)
            nova_rodada = False

        if not nao_envia:
            msg.send_msg() # vai ter configurado a mensagem no else? (caso nao seja a rodada inicial)
        else:
            nao_envia = True

        bst.send_msg()
        bastao = False

    else:
        if(msg.recv_msg() == -1): # nao era uma mensagem com o nosso marcador de inicio
            continue

        if(msg.paridade != msg.calc_paridade()):
            print(f"ERRO PARIDADE: {msg.paridade} vs {msg.calc_paridade()}")
            anterior = (eu + 3) % 4
            msg = mensagem(eu, anterior, ERRO)

        elif(msg.tipo == ERRO):
            if ba2int(msg.dst) == eu:
                msg = reserva
            else:
                msg.prox = prox # cursed.
        
        elif(msg.tipo == INICIA):
            apostador = ba2int(msg.dados[0:2])
            comb = ba2int(msg.dados[2:5])
            custo = ba2int(msg.dados[5:8])

            if jogador_inicial == eu:
                print(f"apostador: {apostador}")
                msg = mensagem(eu, apostador, JOGA, msg.dados)
                input("qqr tecla...")
            else:
                print(f"====== Yatzee - Jogador {eu} - {rodadas}a rodada ======")
                print("1 - Um Par")
                print("2 - Um Trio")
                print("3 - Dois Pares")
                print("4 - Full House")
                print("5 - Sequência Baixa")
                print("6 - Sequência Alta")
                print("7 - Quadra")
                print("8 - Quinteto")
                print(f"\nJogador {apostador} aposta {custo} na opcao {comb+1}.")
                entrada = input(f"Deseja aumentar a aposta? [s/n]: ")

                comb = msg.dados[2:5]
                
                if entrada == "s":
                    custo += 1
                    apostador = eu

                custo = int2ba(custo, length=3) # garantir sempre os 3 bits
                dados = jogadores_BA[apostador] + comb + custo
                msg = mensagem(eu, prox, INICIA, dados)

        elif(msg.tipo == JOGA):
            print(f"dst: {ba2int(msg.dst)}")
            input("Qqr tecla...")
            if(ba2int(msg.dst) == eu):
                print("Voce deu a maior aposta e jogou os dados.")
                comb = msg.dados[2:5]
                dadinhos = jogar_dados()
                ganhei = checar_comb(dadinhos, comb)
                ganhei = int2ba(int(ganhei), length=1)
                pontos = int2ba(pontos_comb(comb), length=4)
                input()
                print(f"Voce ganhou {pontos} pontos")
                dados =  ganhei + pontos
                msg = msg(eu, prox, RESULTADO, dados)

        elif(msg.tipo == RESULTADO):
            if eu == jogador_inicial:
                msg.dados[5:7] = int2ba(eu, length=2) # FINALIZA tem os bytes iniciais igual a RESULTADO
            else:
                msg.prox = prox # nao precisa

        elif(msg.tipo == FINALIZA):
            afetado = ba2int(msg.dados[5:7])
            sinal = (-1) if msg.dados[0] == 1 else 1
            pontos = sinal * ba2int(msg.dados[1:5])

            if afetado == eu:
                saldos[eu] += sinal * ba2int(msg.dados[1:5])
            else:
                print("Jogador {afetado} ganhou {pontos} pontos.")

            if jogador_inicial == eu:
                jogador_inicial = prox
                nova_rodada = True
                nao_envia = True
            else:
                msg.prox = prox

        elif(msg.tipo == BASTAO):
            bastao = True
            msg = reserva # mensagem criada no estado anterior em msg é sobrescrita pelo bastao

        reserva.org      = msg.org[:]   # copia objeto ao invés de manter mesmo ponteiro
        reserva.dst      = msg.dst[:]
        reserva.tipo     = msg.tipo[:]
        reserva.dados    = msg.dados[:]
        reserva.paridade = msg.paridade[:]

        print(f"reserva.org: {reserva.org}\nreserva.dst: {reserva.dst}\nreserva.tipo: {reserva.tipo}")
        print(f"reserva.dados: {reserva.dados}\nreserva.paridade: {reserva.paridade}")
        input("shesh")