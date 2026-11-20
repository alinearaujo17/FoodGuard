
# Importa as bibliotecas necessárias
import paho.mqtt.client as mqtt
import sqlite3
import json
import os
import sys

# Identificação do controlador
ID_CONTROLADOR = sys.argv[1] if len(sys.argv) > 1 else "controlador1"

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópicos de comunicação
TOPICO_SENSOR = "foodguard/camara1/sensores"
TOPICO_RESPOSTA = "foodguard/controladores/respostas"

# Limite de temperatura
LIMITE_TEMPERATURA = 5.0

# Caminho do banco de dados
CAMINHO_BANCO = os.path.join(
    "banco_dados",
    ID_CONTROLADOR + ".db"
)


# Cria o banco de dados
def criar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor TEXT,
            temperatura REAL,
            umidade REAL
        )
    """)

    conexao.commit()
    conexao.close()


# Salva a leitura recebida
def salvar_leitura(informacao):
    conexao = sqlite3.connect(CAMINHO_BANCO)

    conexao.execute("""
        INSERT INTO leituras (sensor, temperatura, umidade)
        VALUES (?, ?, ?)
    """, (
        informacao["sensor"],
        informacao["temperatura"],
        informacao["umidade"]
    ))

    conexao.commit()
    conexao.close()


# Recebe os dados do sensor
def ao_receber(cliente, dados, mensagem):
    informacao = json.loads(mensagem.payload.decode("utf-8"))

    temperatura = informacao["temperatura"]

    print("\nControlador:", ID_CONTROLADOR)
    print("Temperatura recebida:", temperatura)

    salvar_leitura(informacao)

    # Define a decisão normal do controlador
    if temperatura > LIMITE_TEMPERATURA:
        comando = "LIGAR"
    else:
        comando = "DESLIGAR"

    # Simula uma decisão incorreta na replica3
    if ID_CONTROLADOR == "replica3":
        if comando == "LIGAR":
            comando = "DESLIGAR"
        else:
            comando = "LIGAR"

        print("ATENÇÃO: decisão inconsistente simulada!")

    print("Decisão:", comando)

    # Prepara a resposta
    resposta = {
        "id_leitura": informacao["id_leitura"],
        "controlador": ID_CONTROLADOR,
        "sensor": informacao["sensor"],
        "temperatura": temperatura,
        "umidade": informacao["umidade"],
        "comando": comando
    }

    # Envia a resposta ao Middleware
    cliente.publish(
        TOPICO_RESPOSTA,
        json.dumps(resposta),
        qos=1
    )


# Inicializa o banco de dados
criar_banco()

# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=ID_CONTROLADOR
)

cliente.on_message = ao_receber

cliente.connect(SERVIDOR, PORTA)
cliente.subscribe(TOPICO_SENSOR, qos=1)

print(ID_CONTROLADOR, "conectado ao FoodGuard!")
print("Banco de dados:", CAMINHO_BANCO)
print("Aguardando dados dos sensores...\n")

cliente.loop_forever()
