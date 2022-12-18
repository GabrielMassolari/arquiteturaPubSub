from flask import Flask, jsonify, request
from db import session, Cliente
from db import Produto, Carrinho, Venda
import zmq
import _thread

IP_ADDRESS = "10.0.1.1"

ctx = zmq.Context()
sockPub = ctx.socket(zmq.PUB)
sockPub.connect(f"tcp://{IP_ADDRESS}:5500")


def servidor():
    sockSub = ctx.socket(zmq.SUB)
    sockSub.connect(f"tcp://{IP_ADDRESS}:5501")
    sockSub.subscribe("validacaoPagamento")
    sockSub.subscribe("validacaoEstoque")

    print(f"Starting receiver from topic(s) validacaoPagamento and validacaoEstoque...")
    while True:
        msg_string = sockSub.recv_string()
        msg_json = sockSub.recv_json()
        print(f"Received json message {msg_json} from topic {msg_string}.")
        id_venda = msg_json["msg"]["id"]
        if msg_string == "validacaoEstoque":
            session.query(Venda).filter(Venda.id == id_venda).update(
                {
                    "pagamentoaprovado": True
                }
            )
            session.commit()
        elif msg_string == "validacaoPagamento":
            session.query(Venda).filter(Venda.id == id_venda).update(
                {
                    "estoqueaprovado": True
                }
            )
            session.commit()


def validarVenda(venda):
    sockPub.send_string("Estoque", flags=zmq.SNDMORE)
    sockPub.send_json({"msg": venda})
    if venda["cartao"] == "Visa":
        sockPub.send_string("Visa", flags=zmq.SNDMORE)
        sockPub.send_json({"msg": venda})
    elif venda["cartao"] == "MasterCard":
        sockPub.send_string("MasterCard", flags=zmq.SNDMORE)
        sockPub.send_json({"msg": venda})

app = Flask(__name__)


@app.route("/inicio", methods=["GET"])
@app.route("/olamundo", methods=["GET"])
def olamundo():
    return "<h1> Ola Mundo </h1>", 201


# Cliente
@app.route("/cliente", methods=["GET", "POST"])
@app.route("/cliente/<int:id_cliente>", methods=["GET", "PUT", "DELETE"])
def cliente(id_cliente=None):
    if request.method == "GET":
        if id_cliente:
            try:
                cliente = (
                    session.query(Cliente)
                    .filter(Cliente.id == id_cliente)
                    .one()
                )
                return (
                    jsonify({"id": cliente.id,
                             "nome": cliente.nome,
                             "endereco": cliente.endereco,
                             "cpf": cliente.cpf,
                             "email": cliente.email}),
                    200,
                )
            except Exception as ex:
                return "", 404
        else:
            lista_clientes = []
            clientes = session.query(Cliente).all()
            for c in clientes:
                lista_clientes.append({"id": c.id,
                                       "nome": c.nome,
                                       "endereco": c.endereco,
                                       "cpf": c.cpf,
                                       "email": c.email})
            return jsonify(lista_clientes), 200
    elif request.method == "POST":
        cliente = request.json
        session.add(
            Cliente(nome=cliente["nome"],
                    endereco=cliente["endereco"],
                    cpf=cliente["cpf"],
                    email=cliente["email"])
        )
        session.commit()
        return "", 200
    elif request.method == "PUT":
        cliente = request.json
        session.query(Cliente).filter(Cliente.id == id_cliente).update(
            {"nome": cliente["nome"],
             "endereco": cliente["endereco"],
             "cpf": cliente["cpf"],
             "email": cliente["email"]})
        session.commit()
        return "", 200
    elif request.method == "DELETE":
        session.query(Cliente).filter(
            Cliente.id == id_cliente
        ).delete()
        session.commit()
        return "", 200


# Produto
@app.route("/produto", methods=["GET", "POST"])
@app.route("/produto/<int:id_produto>", methods=["GET", "PUT", "DELETE"])
def produto(id_produto=None):
    if request.method == "GET":
        if id_produto:
            try:
                produto = (
                    session.query(Produto)
                    .filter(Produto.id == id_produto)
                    .one()
                )
                return (
                    jsonify({"id": produto.id,
                             "nome": produto.nome,
                             "preco": produto.preco,
                             "descricao": produto.descricao}),
                    200,
                )
            except Exception as ex:
                return "", 404
        else:
            lista_produtos = []
            produtos = session.query(Produto).all()
            for p in produtos:
                lista_produtos.append({"id": p.id,
                                       "nome": p.nome,
                                       "preco": p.preco,
                                       "descricao": p.descricao})
            return jsonify(lista_produtos), 200
    elif request.method == "POST":
        produto = request.json
        session.add(
            Produto(nome=produto["nome"],
                    preco=produto["preco"],
                    descricao=produto["descricao"])
        )
        session.commit()
        return "", 200
    elif request.method == "PUT":
        produto = request.json
        session.query(Produto).filter(Produto.id == id_produto).update(
            {"nome": produto["nome"],
             "preco": produto["preco"],
             "descricao": produto["descricao"]}
        )
        session.commit()
        return "", 200
    elif request.method == "DELETE":
        session.query(Produto).filter(
            Produto.id == id_produto
        ).delete()
        session.commit()
        return "", 200


@app.route("/carrinho", methods=["GET", "POST"])
@app.route("/carrinho/<int:id_carrinho>", methods=["GET", "PUT", "DELETE"])
def carrinho(id_carrinho=None):
    if request.method == "GET":
        if id_carrinho:
            try:
                carrinho = (
                    session.query(Carrinho)
                    .filter(Carrinho.id == id_carrinho)
                    .one()
                )
                return (
                    jsonify({"id": carrinho.id,
                             "preco": carrinho.preco,
                             "qtd": carrinho.qtd,
                             "produto_id": carrinho.produto_id,
                             "venda_id": carrinho.venda_id}),
                    200,
                )
            except Exception as ex:
                return "", 404
        else:
            lista_carrinhos = []
            carrinhos = session.query(Carrinho).all()
            for c in carrinhos:
                lista_carrinhos.append({"id": c.id,
                                        "preco": c.preco,
                                        "qtd": c.qtd,
                                        "produto_id": c.produto_id,
                                        "venda_id": c.venda_id})
            return jsonify(lista_carrinhos), 200
    elif request.method == "POST":
        carrinho = request.json
        session.add(
            Carrinho(preco=carrinho["preco"],
                    qtd=carrinho["qtd"],
                    produto_id=carrinho["produto_id"],
                    venda_id=carrinho["venda_id"])
        )
        session.commit()
        return "", 200
    elif request.method == "PUT":
        carrinho = request.json
        session.query(Carrinho).filter(Carrinho.id == id_carrinho).update(
            {"preco": carrinho["preco"],
             "qtd": carrinho["preco"],
             "produto_id": carrinho["produto_id"],
             "venda_id": carrinho["venda_id"]}
        )
        session.commit()
        return "", 200
    elif request.method == "DELETE":
        session.query(Carrinho).filter(
            Carrinho.id == id_carrinho
        ).delete()
        session.commit()
        return "", 200


@app.route("/venda", methods=["GET", "POST"])
@app.route("/venda/<int:id_venda>", methods=["GET", "PUT", "DELETE"])
def venda(id_venda=None):
    if request.method == "GET":
        if id_venda:
            try:
                venda = (
                    session.query(Venda)
                    .filter(Venda.id == id_venda)
                    .one()
                )
                return (
                    jsonify({"id": venda.id,
                             "cliente_id": venda.cliente_id,
                             "cartao": venda.cartao,
                             "produto_id": venda.produto_id,
                             "pagamentoaprovado": venda.pagamentoaprovado,
                             "estoqueaprovado": venda.estoqueaprovado}),
                    200,
                )
            except Exception as ex:
                return "", 404
        else:
            lista_vendas = []
            vendas = session.query(Venda).all()
            for v in vendas:
                lista_vendas.append({"id": v.id,
                                     "cliente_id": v.cliente_id,
                                     "cartao": v.cartao,
                                     "produto_id": v.produto_id,
                                     "pagamentoaprovado": v.pagamentoaprovado,
                                     "estoqueaprovado": v.estoqueaprovado})
            return jsonify(lista_vendas), 200
    elif request.method == "POST":
        venda = request.json
        vendaInsert = Venda(cliente_id=venda["cliente_id"],
                  cartao=venda["cartao"],
                  produto_id=venda["produto_id"],
                  pagamentoaprovado=False,
                  estoqueaprovado=False)
        session.add(
            vendaInsert
        )
        session.commit()
        session.flush()
        session.refresh(vendaInsert)

        msg = {
            "id": vendaInsert.id,
            "cartao": venda["cartao"]
        }

        validarVenda(msg)
        return "", 200
    elif request.method == "PUT":
        venda = request.json
        session.query(Venda).filter(Venda.id == id_venda).update(
            {"cliente_id": venda["cliente_id"],
            "cartao": venda["cartao"],
            "produto_id": venda["produto_id"],
            "pagamentoaprovado": venda["pagamentoaprovado"],
            "estoqueaprovado": venda["estoqueaprovado"]}
        )
        session.commit()
        return "", 200
    elif request.method == "DELETE":
        session.query(Venda).filter(
            Venda.id == id_venda
        ).delete()
        session.commit()
        return "", 200

def server():
    _thread.start_new_thread(servidor,())


if __name__ == "__main__":
    server()
    app.run(host="0.0.0.0", port=8080)