import sqlite3
import os

controladores = ["replica1", "replica2", "replica3"]

for nome in controladores:

    caminho = os.path.join("banco_dados", nome + ".db")

    conexao = sqlite3.connect(caminho)

    quantidade = conexao.execute(
        "SELECT COUNT(*) FROM leituras"
    ).fetchone()[0]

    print(nome, "-", quantidade, "leituras")

    conexao.close()