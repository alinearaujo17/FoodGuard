# FoodGuard – Sistema Distribuído de Monitoramento de Câmara Fria

## 1. Apresentação

O FoodGuard é um sistema distribuído desenvolvido como trabalho prático da disciplina de Sistemas Distribuídos.

O projeto tem como finalidade monitorar as condições de temperatura e umidade de uma câmara fria, utilizando sensores, controladores, um Middleware e um atuador responsável pelo controle da refrigeração.

O sistema utiliza comunicação MQTT para troca de mensagens entre os componentes e FastAPI para permitir o envio de leituras e a consulta dos resultados.

## 2. Objetivo

Desenvolver um sistema distribuído capaz de receber informações de sensores, processar essas informações por meio de diferentes controladores e tomar decisões utilizando votação por maioria.

O sistema também busca demonstrar tolerância a falhas, identificando situações em que os controladores apresentam decisões divergentes ou quando não há respostas suficientes para uma decisão.

## 3. Arquitetura do sistema

O FoodGuard é composto pelos seguintes elementos:

- **Sensor:** responsável por gerar informações de temperatura e umidade.
- **Controladores:** recebem as leituras e realizam o processamento individualmente.
- **Middleware:** recebe as respostas dos controladores, realiza a votação e define a decisão final.
- **Atuador:** recebe os comandos de refrigeração ou alertas informativos.
- **FastAPI:** disponibiliza uma API para enviar leituras e consultar os resultados.
- **Broker MQTT:** responsável por intermediar a comunicação entre os componentes.
- **Banco de dados SQLite:** utilizado para armazenar as leituras processadas pelos controladores.

## 4. Tecnologias utilizadas

- Python
- FastAPI
- MQTT
- Eclipse Mosquitto
- Paho MQTT
- SQLite
- Docker
- Uvicorn
- Swagger

## 5. Funcionamento do sistema

O funcionamento ocorre da seguinte maneira:

1. O sensor gera uma leitura de temperatura e umidade.
2. A leitura é publicada no broker MQTT.
3. Os três controladores recebem a mesma informação.
4. Cada controlador analisa a temperatura e define uma decisão.
5. As respostas são enviadas ao Middleware.
6. O Middleware realiza a votação por maioria.
7. Quando existe maioria, a decisão é enviada ao atuador.
8. Quando não existe maioria ou quórum, um alerta informativo é enviado ao atuador.
9. Os resultados também são publicados para a API FastAPI.

Foi utilizada a temperatura de 5 °C como referência para a decisão dos controladores.

- Temperatura acima de 5 °C: LIGAR a refrigeração.
- Temperatura igual ou abaixo de 5 °C: DESLIGAR a refrigeração.

A réplica 3 foi configurada para inverter sua decisão, permitindo simular divergência entre controladores.

## 6. Sistema de votação

O Middleware utiliza votação por maioria para definir a decisão final.

O sistema trabalha com três controladores e considera uma decisão válida quando pelo menos dois apresentam o mesmo resultado.

São tratados três cenários:

**Maioria alcançada**

Quando pelo menos dois controladores apresentam a mesma decisão, o Middleware envia o comando ao atuador.

**Sem maioria**

Quando dois controladores respondem com decisões diferentes, não existe maioria. Nesse caso, nenhum comando de refrigeração é enviado.

**Quórum não alcançado**

Quando menos de dois controladores respondem dentro do tempo de espera de dois segundos, o sistema identifica que não há respostas suficientes para tomar uma decisão.

Nos cenários sem maioria e sem quórum, o Middleware publica um alerta informativo em um tópico MQTT específico. O atuador recebe a mensagem e apresenta o aviso, sem executar alterações na refrigeração.

## 7. Integração com FastAPI

A API permite enviar leituras ao sistema e consultar os resultados das votações.

A documentação interativa pode ser acessada pelo Swagger:

`http://127.0.0.1:8000/docs`

### Rotas disponíveis

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Verifica se a API está funcionando |
| GET | `/status` | Consulta o status do sistema |
| POST | `/leituras` | Envia uma leitura para processamento |
| GET | `/resultados` | Consulta todos os resultados |
| GET | `/resultados/{id_leitura}` | Consulta um resultado específico |

A integração permite que uma leitura enviada pela API seja encaminhada pelo MQTT aos controladores, processada pelo Middleware e tenha seu resultado disponibilizado novamente na API.

## 8. Testes realizados

Foram realizados testes para verificar a comunicação entre os componentes e o comportamento do sistema em diferentes situações.

### Teste 1 – Comunicação entre sensores e controladores

Foi verificado o envio das leituras pelo sensor e o recebimento das informações pelos controladores.

### Teste 2 – Votação por maioria

Os três controladores receberam uma leitura. Dois apresentaram a mesma decisão e um apresentou uma decisão divergente.

O Middleware identificou a maioria e enviou o comando correspondente ao atuador.

### Teste 3 – Identificação de divergência

Foi simulada uma decisão diferente na réplica 3 para verificar se o Middleware conseguiria identificar o controlador divergente.

### Teste 4 – Integração com FastAPI

Foi realizado o envio de uma leitura pela rota POST `/leituras`.

A leitura foi processada pelos controladores e pelo Middleware, e o resultado foi recebido e consultado pela API.

### Teste 5 – Ausência de maioria

Foram mantidos ativos dois controladores com decisões diferentes.

O Middleware identificou a ausência de maioria, não enviou comando de refrigeração e publicou um alerta informativo para o atuador.

### Teste 6 – Ausência de quórum

Foi mantido apenas um controlador ativo.

O Middleware identificou que não havia respostas suficientes dentro do tempo de espera, não enviou comando de refrigeração e publicou um alerta informativo para o atuador.

## 9. Estrutura do projeto

```text
FoodGuard/
├── atuadores/
│   └── atuador.py
├── banco_dados/
├── cliente/
├── controladores/
│   ├── controlador.py
│   └── controlador1.py
├── evidencias/
├── middleware/
│   └── middleware.py
├── mosquitto/
├── .gitignore
├── README.md
├── docker-compose.yml
├── main.py
├── requirements.txt
└── verificar_replicas.py
```

## 10. Como executar o projeto

### Pré-requisitos

- Python instalado.
- Docker instalado.
- Broker Mosquitto configurado pelo Docker Compose.

### Instalação

Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
```

Acesse a pasta do projeto:

```bash
cd FoodGuard
```

Crie e ative um ambiente virtual, se necessário.

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o broker MQTT:

```bash
docker compose up -d
```

### Execução dos componentes

Abra terminais separados, com o ambiente virtual ativado.

**1. Inicie o Middleware:**

```bash
python middleware/middleware.py
```

**2. Inicie os três controladores:**

```bash
python controladores/controlador.py replica1
```

```bash
python controladores/controlador.py replica2
```

```bash
python controladores/controlador.py replica3
```

**3. Inicie o atuador:**

```bash
python atuadores/atuador.py
```

**4. Inicie o FastAPI:**

```bash
uvicorn main:app --reload
```

**5. Inicie o sensor:**

```bash
python sensores/sensor.py
```

A API estará disponível em:

`http://127.0.0.1:8000`

A documentação interativa estará disponível em:

`http://127.0.0.1:8000/docs`

## 11. Evidências

As imagens dos testes realizados estão organizadas na pasta `evidencias/`.

Elas demonstram o funcionamento dos sensores, controladores, Middleware, votação por maioria, comunicação com o atuador e integração com a API.

## 12. Considerações finais

O desenvolvimento do FoodGuard permitiu aplicar conceitos de Sistemas Distribuídos, como comunicação por mensagens, replicação, tolerância a falhas e tomada de decisão por votação.

Os testes demonstraram que o sistema consegue processar leituras, identificar divergências entre controladores e evitar o envio de comandos quando não existe maioria ou quórum suficiente.

A integração com FastAPI também permitiu disponibilizar uma interface para envio de leituras e consulta dos resultados do processamento.

O projeto demonstra, na prática, como diferentes componentes podem trabalhar de forma distribuída para realizar uma tarefa em conjunto.