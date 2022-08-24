from functools import reduce
from nis import match
import socket
import sys
from bitarray import bitarray
from bitarray.util import hex2ba, ba2int, int2ba, parity
from random import randint
from tipos import *
from combinacoes_BA import *

ip = '127.0.0.1'
port = 37880

saldos = [10, 10, 10, 10]
jogadores_BA = [bitarray('00'), bitarray('01'), bitarray('10'), bitarray('11')]

eu = int(sys.argv[len(sys.argv)-1])  # numero do jogador
prox = (eu + 1) % 4

portRecv = port + (eu)
portSend = port + (prox)

# print('recebe: ', portRecv)
# print('envia: ', portSend)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))


class Mensagem:
    header = bitarray('01111110')  # precisa?
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

        if (len(self.dados) < 8):  # garante o tamanho de dados
            falta = 8 - len(self.dados)
            a = falta * bitarray('0')
            self.dados = self.dados + a  # adiciona o que falta ao fim

        self.paridade = self.calc_paridade()  # retornar ja um bitarray?

    def send_msg(self):
        msg = Mensagem.header + self.org + self.dst + \
            self.tipo + self.dados + self.paridade
        buff = memoryview(msg)
        sock.sendto(buff, (ip, portSend))

    def recv_msg(self):
        data, addr = sock.recvfrom(1024)
        if (data):
            # print("RECEBIDO:", '.'.join(f'{c}' for c in data))
            recebido = hex2ba(data.hex())
            # print(recebido)

            rec_head = recebido[0:8]
            if (rec_head != self.header):
                return -1

            self.org = recebido[8:10]
            self.dst = recebido[10:12]
            self.tipo = recebido[12:16]
            self.dados = recebido[16:24]
            self.paridade = recebido[24:32]

            # print(f"org: {self.org} | dst: {self.dst} | tipo: {self.tipo} | dados: {self.dados} | paridade: {self.paridade}")

            return 0

    def calc_paridade(self):  # retornar um bitarray
        return int2ba(parity(self.org + self.dst + self.tipo + self.dados), length=8)


bst = Mensagem(eu, prox, BASTAO)    # bastao
buf = Mensagem(eu, prox, BASTAO)    # buffer para leitura de mensagens
msg: Mensagem                       # mensagem a ser enviada para o proximo jogador

jogador_inicial = 0
rodada = 0


def escolher_comb():
    # Pergunta ao usuário qual combinação deseja
    # Retorna bitarray da combinação escolhida
    print(f"====== Yatzee | Jogador {eu} | Rodada {rodada} ======")
    print("1 - Um Par")
    print("2 - Um Trio")
    print("3 - Dois Pares")
    print("4 - Full House")
    print("5 - Sequência Baixa")
    print("6 - Sequência Alta")
    print("7 - Quadra")
    print("8 - Quinteto")

    entrada = int(input("\nQual combinação quer fazer? (custo = 1) [1-8]: "))
    return int2ba(entrada - 1, length=3)


def aumentar_aposta(apostador, comb, custo):
    # Pergunta ao usuário se quer aumentar aposta
    # Retorna bool
    comb = ba2int(comb)

    print(f"====== Yatzee | Jogador {eu} | Rodada {rodada} ======")
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
    return True if entrada == "s" else False


def jogar_dadinhos():
    # Interage com o usuário para jogada dos dados
    # Retorna lista com estado final dos dados
    dados = [randint(1, 6), randint(1, 6), randint(
        1, 6), randint(1, 6), randint(1, 6)]
    fixados = []

    for chance in range(1, 3):

        print(f"Você rolou {5 - len(fixados)} dados:")
        print(f"1 -> {dados[0]}")
        print(f"2 -> {dados[1]}")
        print(f"3 -> {dados[2]}")
        print(f"4 -> {dados[3]}")
        print(f"5 -> {dados[4]}")

        fixados = []

        entrada = int(
            input(f"\nQuantos dados deseja fixar? ({chance}a chance) [0-5]: "))

        if entrada >= 5:
            continue

        for i in range(0, entrada):
            fixado = int(
                input(f"Digite a opção do {i+1}o dado a ser fixado: [1-5]: "))
            fixados.append(fixado - 1)

        for i in range(0, 5):
            if i not in fixados:
                dados[i] = randint(1, 6)

    print(f"Dados finais:")
    print(f"1 -> {dados[0]}")
    print(f"2 -> {dados[1]}")
    print(f"3 -> {dados[2]}")
    print(f"4 -> {dados[3]}")
    print(f"5 -> {dados[4]}")

    return dados


def checar_comb(dadinhos, comb):
    # Checa se deu a combinação nos dados
    # Retorna bool

    dadinhos.sort()  # util para sequencias

    def count_num(num):
        # Conta quantos dados deram o numero num
        return reduce(lambda acc, x: acc + 1 if x == num else acc, dadinhos, 0)

    # Gera mapa de frequencia dos dados
    frequencias = {}
    for num in range(1, 7):
        count = count_num(num)
        frequencias.setdefault(count, []).append(num)

    if comb == UM_PAR:
        return True if 2 in frequencias else False

    elif comb == TRIO:
        return True if 3 in frequencias else False

    elif comb == DOIS_PARES:
        return True if len(frequencias.get(2, [])) >= 2 else False

    elif comb == FULL_HOUSE:
        return True if 2 in frequencias and 3 in frequencias else False

    elif comb == SEQ_BAIXA:
        return True if dadinhos == [5, 4, 3, 2, 1] or dadinhos == [6, 5, 4, 3, 2] else False

    elif comb == SEQ_ALTA:
        return True if dadinhos == [1, 2, 3, 4, 5] or dadinhos == [2, 3, 4, 5, 6] else False

    elif comb == QUADRA:
        return True if 4 in frequencias else False

    elif comb == QUINTETO:
        return True if 5 in frequencias else False

    return False


def calcular_pontos(comb):
    comb = frozenbitarray(comb)
    # Calcula quantos pontos vale a combinação
    tabela = {
        UM_PAR: 2,
        TRIO: 3,
        DOIS_PARES: 4,
        FULL_HOUSE: 5,
        SEQ_BAIXA: 7,
        SEQ_ALTA: 7,
        QUADRA: 10,
        QUINTETO: 15
    }
    return tabela[comb]


def alguem_faliu():
    # Verifica se algum jogador possui saldo <= 0
    return reduce(lambda acc, x: x <= 0 if acc == False else True, saldos, False)


if eu == jogador_inicial:
    comb = escolher_comb()
    custo = bitarray('001')  # custo inicial
    dados = jogadores_BA[eu] + comb + custo
    msg = Mensagem(eu, prox, INICIA, dados)

    msg.send_msg()
    bst.send_msg()


while True:

    if buf.recv_msg() == -1:  # nao era uma mensagem com o nosso marcador de inicio
        continue

    if buf.paridade != buf.calc_paridade():
        # print(f"ERRO PARIDADE: {msg.paridade} vs {msg.calc_paridade()}")
        anterior = (eu + 3) % 4
        msg = Mensagem(eu, anterior, ERRO)

    elif buf.tipo == ERRO:
        if buf.dst != jogadores_BA[eu]:
            # se não for o destinatário repassa a mensagem lida adiante
            msg = Mensagem(eu, ba2int(buf.dst), buf.tipo[:], buf.dados[:])

    elif buf.tipo == INICIA:
        apostador = ba2int(buf.dados[0:2])
        comb = buf.dados[2:5]
        custo = ba2int(buf.dados[5:8])

        if eu != jogador_inicial:
            if (aumentar_aposta(apostador, comb, custo)):
                apostador = eu
                custo += 1

            custo = int2ba(custo, length=3)
            dados = jogadores_BA[apostador] + comb + custo
            msg = Mensagem(eu, prox, INICIA, dados)

        else:
            msg = Mensagem(eu, apostador, JOGA, buf.dados)

    elif buf.tipo == JOGA:
        if buf.dst != jogadores_BA[eu]:
            msg = Mensagem(eu, ba2int(buf.dst), buf.tipo[:], buf.dados[:])

        else:
            comb = buf.dados[2:5]
            custo = ba2int(buf.dados[5:8])

            dadinhos = jogar_dadinhos()
            ganhei = checar_comb(dadinhos, comb)
            pontos = calcular_pontos(comb) if ganhei else custo

            ganhei = int2ba(int(ganhei), length=1)
            pontos = int2ba(pontos, length=4)
            dados = ganhei + pontos + jogadores_BA[eu]
            msg = Mensagem(eu, prox, RESULTADO, dados)

    elif buf.tipo == RESULTADO:
        if eu == jogador_inicial:
            dados = buf.dados[:]
            msg = Mensagem(eu, prox, FINALIZA, dados)
        else:
            msg = Mensagem(eu, ba2int(buf.dst), buf.tipo[:], buf.dados[:])

    elif buf.tipo == FINALIZA:
        afetado = ba2int(buf.dados[5:7])
        sinal = (-1) if buf.dados[0] == 0 else 1
        pontos = sinal * ba2int(msg.dados[1:5])

        if afetado == eu:
            print(f"\nVocê ganhou {pontos} pontos.")
        else:
            print(f"\nJogador {afetado} ganhou {pontos} pontos")

        if eu == jogador_inicial:
            msg = Mensagem(eu, prox, RECOMECA)
        else:
            msg = Mensagem(eu, ba2int(buf.dst), buf.tipo[:], buf.dados[:])

        saldos[afetado] += pontos
        jogador_inicial = (jogador_inicial + 1) % 4
        rodada += 1

        print("\nPlacar atual")
        print(f"- Jogador 0: {saldos[0]}")
        print(f"- Jogador 1: {saldos[1]}")
        print(f"- Jogador 2: {saldos[2]}")
        print(f"- Jogador 3: {saldos[3]}")

    elif buf.tipo == RECOMECA:
        comb = escolher_comb()
        custo = bitarray('001')  # custo inicial
        dados = jogadores_BA[eu] + comb + custo
        msg = Mensagem(eu, prox, INICIA, dados)

    elif buf.tipo == BASTAO:
        msg.send_msg()
        bst.send_msg()
        if alguem_faliu():
            break

print(f"========== Yatzee | Placar Final ==========")
print(f"- Jogador 0: {saldos[0]}")
print(f"- Jogador 1: {saldos[1]}")
print(f"- Jogador 2: {saldos[2]}")
print(f"- Jogador 3: {saldos[3]}")
