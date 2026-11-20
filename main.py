
# Importa as bibliotecas necessárias
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import paho.mqtt.client as mqtt
import json
import threading
import uuid

# Configurações do MQTT
SERVIDOR = "localhost"
PORTA = 1884

# Tópicos de comunicação
TOPICO_RESULTADO = "foodguard/middleware/resultados"
TOPICO_SENSOR = "foodguard/camara1/sensores"

# Armazena os resultados recebidos
resultados_recebidos = {}

# Controla o acesso aos resultados
bloqueio = threading.Lock()


# Modelo dos dados enviados pela API
class Leitura(BaseModel):
    sensor: str
    temperatura: float
    umidade: float


# Recebe os resultados publicados pelo Middleware
def ao_receber(cliente, dados, mensagem):

    informacao = json.loads(mensagem.payload.decode("utf-8"))

    id_leitura = informacao["id_leitura"]

    with bloqueio:
        resultados_recebidos[id_leitura] = informacao

    print("\nResultado recebido pelo FastAPI!")
    print("ID da leitura:", id_leitura)
    print("Status:", informacao["status"])
    print("Decisão:", informacao["decisao"])


# Configura e inicia a conexão MQTT
@asynccontextmanager
async def ciclo_vida(app):

    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="foodguard_api"
    )

    cliente.on_message = ao_receber

    cliente.connect(SERVIDOR, PORTA)
    cliente.subscribe(TOPICO_RESULTADO, qos=1)

    cliente.loop_start()

    app.state.mqtt_cliente = cliente

    print("FastAPI conectado ao MQTT!")
    print("Aguardando resultados do Middleware...\n")

    yield

    cliente.loop_stop()
    cliente.disconnect()


# Cria a aplicação FastAPI
app = FastAPI(
    title="FoodGuard API",
    description="API de monitoramento e controle de camara fria",
    version="1.0.0",
    lifespan=ciclo_vida
)


# Rota inicial
@app.get("/")
def inicio():
    return {
        "mensagem": "FoodGuard API funcionando!"
    }


# Rota de status
@app.get("/status")
def verificar_status():
    return {
        "sistema": "FoodGuard",
        "status": "Online"
    }


# Rota para consultar todos os resultados
@app.get("/resultados")
def consultar_resultados():

    with bloqueio:
        return {
            "total": len(resultados_recebidos),
            "resultados": list(resultados_recebidos.values())
        }


# Rota para consultar um resultado específico
@app.get("/resultados/{id_leitura}")
def consultar_resultado(id_leitura: str):

    with bloqueio:
        resultado = resultados_recebidos.get(id_leitura)

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Resultado não encontrado."
        )

    return resultado


# Rota para enviar uma leitura pelo FastAPI
@app.post("/leituras")
def enviar_leitura(leitura: Leitura):

    id_leitura = str(uuid.uuid4())

    dados = {
        "id_leitura": id_leitura,
        "sensor": leitura.sensor,
        "temperatura": leitura.temperatura,
        "umidade": leitura.umidade
    }

    cliente = app.state.mqtt_cliente

    resultado = cliente.publish(
        TOPICO_SENSOR,
        json.dumps(dados),
        qos=1
    )

    if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível enviar a leitura pelo MQTT."
        )

    print("\nLeitura enviada pela API!")
    print(dados)

    return {
        "mensagem": "Leitura enviada com sucesso!",
        "dados": dados
    }
