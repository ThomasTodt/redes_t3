PROTOCOLO:
    header:   8
    origem:   2
    destino:  2
    tipo:     4
    dados:    8
    paridade: 8
    (total: 32)

DADOS NOS TIPOS DE MENSAGEM:

    ERRO:
        lixo: 8

    INICIA:
        jogador que vai jogar por enquanto: 2
        combinação que vai tentar: 3
        custo a ser pago: 3

    JOGA:
        jogador que vai jogar por enquanto: 2
        combinação que vai tentar: 3
        custo a ser pago: 3

    RESULTADO: 
        resultado: 1
        mudanca no saldo: 4 (o maximo eh ganhar 15 no quinteto; o sinal eh indicado pelo resultado)
        jogador: 2 (quem jogou)
        lixo: 1

    FINALIZA:
        resultado: 1
        mudanca: 4
        jogador: 2 (o jogador a ter o saldo atualizado)
        lixo: 1

    BASTAO:
        lixo: 8

    RECOMECA:
        lixo: 8