
# Importa a biblioteca MQTT
import paho.mqtt.client as mqtt

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópico que será acompanhado
TOPICO = "foodguard/camara1/sensores"


# Executada quando o cliente se conecta
def ao_conectar(cliente, dados, flags, codigo, propriedades):

    print("Monitor conectado ao FoodGuard!")

    # Inscreve o monitor no tópico do sensor
    cliente.subscribe(TOPICO, qos=1)

    print("Aguardando informações dos sensores...\n")


# Executada quando uma mensagem chega
def ao_receber(cliente, dados, mensagem):

    print("Nova informação recebida:")
    print(mensagem.payload.decode("utf-8"))
    print("--------------------------------")


# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="monitor_foodguard"
)

# Define as funções de comunicação
cliente.on_connect = ao_conectar
cliente.on_message = ao_receber

# Conecta ao broker
cliente.connect(SERVIDOR, PORTA)

# Mantém o monitor funcionando
print("Iniciando monitoramento...\n")
cliente.loop_forever()
