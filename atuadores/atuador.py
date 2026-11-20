
# Importa a biblioteca MQTT
import paho.mqtt.client as mqtt

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópicos de comunicação
TOPICO = "foodguard/camara1/atuadores/refrigeracao"
TOPICO_ALERTAS = "foodguard/camara1/atuadores/status"


# Função executada quando recebe uma mensagem
def ao_receber(cliente, dados, mensagem):

    conteudo = mensagem.payload.decode("utf-8")

    # Recebe comandos de refrigeração
    if mensagem.topic == TOPICO:

        print("\nComando recebido:", conteudo)

        if conteudo == "LIGAR":
            print("Refrigeração LIGADA!")

        elif conteudo == "DESLIGAR":
            print("Refrigeração DESLIGADA!")

    # Recebe alertas do Middleware
    elif mensagem.topic == TOPICO_ALERTAS:

        print("\n================================")
        print("ALERTA DO SISTEMA!")
        print(conteudo)
        print("Nenhum comando de refrigeração foi executado.")
        print("================================\n")


# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="atuador_refrigeracao"
)

# Define a função de recebimento
cliente.on_message = ao_receber

# Conecta ao broker
cliente.connect(SERVIDOR, PORTA)

# Inscreve o atuador nos dois tópicos
cliente.subscribe(TOPICO, qos=1)
cliente.subscribe(TOPICO_ALERTAS, qos=1)

print("Atuador de refrigeração conectado!")
print("Aguardando comandos e alertas do sistema...\n")

# Mantém o atuador funcionando
cliente.loop_forever()
