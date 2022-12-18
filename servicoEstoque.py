import zmq
import time
import _thread

ctx = zmq.Context()
IP_ADDRESS = "10.0.1.1"
TOPIC = "Estoque"

sockPub = ctx.socket(zmq.PUB)
sockPub.connect(f"tcp://{IP_ADDRESS}:5500")

def validarEstoque(msg):
    msg_validacao = {
        "id": msg["msg"]["id"],
        "estiqueaprovado": True
    }

    sockPub.send_string("validacaoEstoque", flags=zmq.SNDMORE)
    sockPub.send_json({"msg": msg_validacao})

def servidor():

    sockSub = ctx.socket(zmq.SUB)
    sockSub.connect(f"tcp://{IP_ADDRESS}:5501")
    sockSub.subscribe(f"{TOPIC}")

    print(f"Starting receiver from topic(s) {TOPIC}...")
    while True:
        msg_string = sockSub.recv_string()
        msg_json = sockSub.recv_json()
        print(f"Received json message {msg_json} from topic {msg_string}.")
        print(f"Conferindo estoque da venda {msg_json['msg']['id']}...")
        time.sleep(10)
        print("Enviando mensagem de validacao de EStoque")
        validarEstoque(msg_json)

def server():
    _thread.start_new_thread(servidor(),())


if __name__ == "__main__":
    server()
