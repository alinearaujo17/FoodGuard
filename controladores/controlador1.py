# Importa as bibliotecas necessárias
import paho.mqtt.client as mqtt
import json

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópicos de comunicação
TOPICO_SENSOR = "foodguard/camara1/sensores"
TOPICO_ATUADOR = "foodguard/camara1/atuadores/refrigeracao"

# Limite de temperatura
LIMITE_TEMPERATURA = 5.0


# Função executada quando recebe dados do sensor
def ao_receber(cliente, dados, mensagem):

    # Converte a mensagem recebida para JSON
    informacao = json.loads(mensagem.payload.decode("utf-8"))

    # Obtém a temperatura
    temperatura = informacao["temperatura"]

    print("\nDados recebidos do sensor:")
    print("Temperatura:", temperatura, "°C")

    # Verifica se a temperatura está acima do limite
    if temperatura > LIMITE_TEMPERATURA:
        comando = "LIGAR"
        print("ALERTA: Temperatura acima do limite!")

    else:
        comando = "DESLIGAR"
        print("Temperatura adequada.")

    # Envia o comando para o atuador
    cliente.publish(
        TOPICO_ATUADOR,
        comando,
        qos=1
    )

    print("Comando enviado:", comando)


# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="controlador1"
)

# Define a função que recebe mensagens
cliente.on_message = ao_receber


# Conecta ao broker
cliente.connect(SERVIDOR, PORTA)

# Inscreve o controlador no tópico do sensor
cliente.subscribe(TOPICO_SENSOR, qos=1)

print("Controlador 1 conectado ao FoodGuard!")
print("Aguardando dados dos sensores...\n")

# Mantém o controlador funcionando
cliente.loop_forever()