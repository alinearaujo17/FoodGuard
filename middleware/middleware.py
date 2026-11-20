
# Importa as bibliotecas necessárias
import paho.mqtt.client as mqtt
import json
import threading
from collections import Counter

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópicos de comunicação
TOPICO_RESPOSTAS = "foodguard/controladores/respostas"
TOPICO_ATUADOR = "foodguard/camara1/atuadores/refrigeracao"
TOPICO_RESULTADO = "foodguard/middleware/resultados"
TOPICO_ALERTAS = "foodguard/camara1/atuadores/status"

# Armazena as respostas de cada leitura
respostas = {}

# Armazena as leituras já processadas
leituras_processadas = set()

# Armazena os temporizadores
temporizadores = {}


# Publica um alerta informativo para o atuador
def publicar_alerta(cliente, mensagem):

    cliente.publish(
        TOPICO_ALERTAS,
        mensagem,
        qos=1
    )

    print("\nAlerta enviado ao atuador:", mensagem)


# Publica o resultado da votação para o FastAPI
def publicar_resultado(cliente, id_leitura, status, decisao=None):

    resultado = {
        "id_leitura": id_leitura,
        "status": status,
        "decisao": decisao,
        "votos": respostas[id_leitura],
        "quantidade_respostas": len(respostas[id_leitura])
    }

    cliente.publish(
        TOPICO_RESULTADO,
        json.dumps(resultado),
        qos=1
    )

    print("\nResultado publicado para a API!")


# Realiza a votação
def processar_votacao(cliente, id_leitura):

    if id_leitura in leituras_processadas:
        return

    votos = list(respostas[id_leitura].values())

    # Marca a leitura como processada
    leituras_processadas.add(id_leitura)
    temporizadores.pop(id_leitura, None)

    print("\nAnalisando votação...")
    print("Quantidade de respostas:", len(votos))

    # Verifica se existem pelo menos duas respostas
    if len(votos) < 2:

        print("Quórum não alcançado!")

        publicar_alerta(
            cliente,
            "QUÓRUM NÃO ALCANÇADO! Apenas um controlador respondeu. Nenhum comando foi executado."
        )

        publicar_resultado(
            cliente,
            id_leitura,
            "quorum_nao_alcancado"
        )

        return

    # Conta os votos
    contagem = Counter(votos)
    decisao_final, quantidade = contagem.most_common(1)[0]

    # Verifica se existe maioria
    if quantidade >= 2:

        print("\nMaioria alcançada!")
        print("Decisão final:", decisao_final)

        # Identifica controladores divergentes
        divergentes = []

        for controlador, comando in respostas[id_leitura].items():

            if comando != decisao_final:
                divergentes.append(controlador)

        if divergentes:

            print("\nALERTA: decisão divergente detectada!")
            print("Controladores divergentes:", divergentes)

        # Envia a decisão ao atuador
        cliente.publish(
            TOPICO_ATUADOR,
            decisao_final,
            qos=1
        )

        # Publica o resultado da votação para o FastAPI
        publicar_resultado(
            cliente,
            id_leitura,
            "maioria_alcancada",
            decisao_final
        )

    else:

        print("Não foi possível alcançar maioria!")
        print("Nenhum comando foi enviado ao atuador.")

        publicar_alerta(
            cliente,
            "SEM MAIORIA! Os controladores apresentaram decisões diferentes. Nenhum comando foi executado."
        )

        # Publica o resultado sem decisão
        publicar_resultado(
            cliente,
            id_leitura,
            "sem_maioria"
        )


# Recebe as respostas dos controladores
def ao_receber(cliente, dados, mensagem):

    informacao = json.loads(mensagem.payload.decode("utf-8"))

    id_leitura = informacao["id_leitura"]
    controlador = informacao["controlador"]
    comando = informacao["comando"]

    print("\nResposta recebida:")
    print("Controlador:", controlador)
    print("ID da leitura:", id_leitura)
    print("Temperatura:", informacao["temperatura"])
    print("Decisão:", comando)

    # Ignora respostas de leituras já processadas
    if id_leitura in leituras_processadas:
        return

    # Cria um grupo para cada leitura
    if id_leitura not in respostas:
        respostas[id_leitura] = {}

    # Armazena a decisão do controlador
    respostas[id_leitura][controlador] = comando

    # Quando as três respostas chegam, realiza a votação
    if len(respostas[id_leitura]) == 3:

        if id_leitura in temporizadores:
            temporizadores[id_leitura].cancel()

        processar_votacao(cliente, id_leitura)

    # Aguarda até 2 segundos pelas demais respostas
    elif id_leitura not in temporizadores:

        temporizador = threading.Timer(
            2.0,
            processar_votacao,
            args=(cliente, id_leitura)
        )

        temporizador.daemon = True
        temporizadores[id_leitura] = temporizador
        temporizador.start()


# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="middleware_foodguard"
)

cliente.on_message = ao_receber

cliente.connect(SERVIDOR, PORTA)
cliente.subscribe(TOPICO_RESPOSTAS, qos=1)

print("Middleware conectado ao FoodGuard!")
print("Aguardando respostas dos controladores...\n")

cliente.loop_forever()
