
# Importa as bibliotecas necessárias
import paho.mqtt.client as mqtt
import random
import json
import time
import uuid

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópico de comunicação
TOPICO = "foodguard/camara1/sensores"

# Identificação do sensor
ID_SENSOR = "sensor_temperatura_01"

# Cria o cliente MQTT
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=ID_SENSOR
)

cliente.connect(SERVIDOR, PORTA)
cliente.loop_start()

print("Sensor conectado ao FoodGuard!")
print("Enviando informações de temperatura...\n")

try:
    while True:
        # Gera valores simulados
        temperatura = round(random.uniform(2, 8), 2)
        umidade = round(random.uniform(45, 75), 2)

        # Gera um identificador único para cada leitura
        id_leitura = str(uuid.uuid4())

        # Organiza os dados
        dados = {
            "id_leitura": id_leitura,
            "sensor": ID_SENSOR,
            "temperatura": temperatura,
            "umidade": umidade
        }

        mensagem = json.dumps(dados)

        # Envia os dados pelo MQTT
        resultado = cliente.publish(TOPICO, mensagem, qos=1)
        resultado.wait_for_publish()

        print("Dados enviados:", mensagem)

        time.sleep(5)

except KeyboardInterrupt:
    print("\nSensor desligado.")

finally:
    cliente.loop_stop()
    cliente.disconnect()
