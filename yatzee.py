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

portRecv = port + (eu)
portSend = port + (prox)

print('recebe: ', portRecv)
print('envia: ', portSend)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, portRecv))

class Mensagem:
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
        msg = Mensagem.header + self.org + self.dst + self.tipo + self.dados + self.paridade
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


msg: Mensagem                   # mensagem a ser enviada para o proximo jogador
buf: Mensagem                   # buffer para leitura de mensagens
bst: Mensagem(eu, prox, BASTAO) # bastao

jogador_inicial = 0
rodada = 0

# Pergunta ao usuário qual combinação deseja
# Retorna bitarray da combinação escolhida
def escolher_comb():
    pass

# Pergunta ao usuário se quer aumentar aposta
# Retorna bool
def aumentar_aposta():
    pass

# Interage com o usuário para jogada dos dados
# Retorna lista com estado final dos dados
def jogar_dadinhos():
    pass

# Checa se deu a combinação nos dados
# Retorna bool
def checar_comb(dadinhos, comb):
    pass

# Calcula quantos pontos vale a combinação
def calcular_pontos(comb):
    pass

if eu == jogador_inicial:
    bastao = True
    comb = escolher_comb()
    custo = bitarray('001') # custo inicial
    dados = jogadores_BA[eu] + comb + custo
    msg = Mensagem(eu, prox, INICIA, dados)

    msg.send_msg()
    bst.send_msg()


while True:
    
    if buf.recv_msg() == -1: # nao era uma mensagem com o nosso marcador de inicio
        continue

    if buf.paridade != buf.calc_paridade():
        # print(f"ERRO PARIDADE: {msg.paridade} vs {msg.calc_paridade()}")
        anterior = (eu + 3) % 4
        msg = Mensagem(eu, anterior, ERRO)

    elif buf.tipo == ERRO:
        if buf.dst != jogadores_BA[eu]:
            msg = buf # se não for o destinatário repassa a mensagem lida adiante

    elif buf.tipo == INICIA:
        apostador = ba2int(buf.dados[0:2])
        comb = buf.dados[2:5]
        custo = ba2int(buf.dados[5:8])

        if eu != jogador_inicial:
            if(aumentar_aposta()):
                apostador = eu
                custo += 1

        apostador = jogadores_BA[apostador]
        custo = int2ba(custo, length=3)
        dados = jogadores_BA[apostador] + comb + custo
        msg = Mensagem(eu, prox, INICIA, dados)
        
    elif buf.tipo == JOGA:
        if buf.dst != jogadores_BA[eu]:
            msg = buf

        else:
            comb = buf.dados[2:5]
            
            dadinhos = jogar_dadinhos()
            ganhei = checar_comb(dadinhos, comb)
            
            ganhei = int2ba(int(ganhei), length=1) 
            pontos = int2ba(calcular_pontos(comb), length=4)
            dados =  ganhei + pontos + jogadores_BA[eu]
            msg = Mensagem(eu, prox, RESULTADO, dados)
            
    elif buf.tipo == RESULTADO:
        if eu == jogador_inicial:
            dados = buf.dados
            msg = Mensagem(eu, prox, FINALIZA, dados)
        else:
            msg = buf
            
    elif buf.tipo == FINALIZA:
        afetado = ba2int(buf.dados[5:7])
        sinal = (-1) if buf.dados[0] == 0 else 1
        pontos = sinal * ba2int(msg.dados[1:5])
        
        if afetado == eu:
            print(f"Você ganhou {pontos} pontos.")
        else:
            print(f"Jogador {afetado} ganhou {pontos} pontos
        
        if eu == jogador_inicial:
            msg = Mensagem(eu, prox, RECOMECA)
        else:
            msg = buf

        saldos[afetados] += pontos
        jogador_inicial = (jogador_inicial + 1) % 4
        rodada += 1
        
    elif buf.tipo == RECOMECA:
        comb = escolher_comb()
        custo = bitarray('001') # custo inicial
        dados = jogadores_BA[eu] + comb + custo
        msg = Mensagem(eu, prox, INICIA, dados)

    elif buf.tipo == BASTAO:
        msg.send_msg()
        bst.send_msg()