#!/usr/bin/env python3
import requests
import time

url = "http://10.0.1.10:8080"

vendas = [
    {"cliente_id": 1, "cartao": "Visa", "produto_id": 1},
    {"cliente_id": 1, "cartao": "MasterCard", "produto_id": 1},
    {"cliente_id": 1, "cartao": "Visa", "produto_id": 1},
    {"cliente_id": 1, "cartao": "MasterCard", "produto_id": 1},
    {"cliente_id": 1, "cartao": "Visa", "produto_id": 1}
]

requests.post(f"{url}/cliente", json={
    "nome": "Gabriel",
    "endereco": "Rua Morro Grande",
    "cpf": "111.111.111-11",
    "email": "gabriel@ifes.com"
})

requests.post(f"{url}/produto", json={
    "nome": "Iphone 14",
    "preco": 5999.00,
    "descricao": "128 Gb"
})

for venda in vendas:  
    requests.post(f"{url}/venda", json=venda)
    time.sleep(3)

r = requests.get(f"{url}/venda")