import json
import requests

# URL de destino da Sentilo. Provedor de Toledo
redirect_url = "http://delrey.td.utfpr.edu.br:8081/data/toledo@utfpr"
# Header da requisição para Sentilo - IDENTITY_KEY minha (André)
headers = {
	'content-type': 'application/json',
	'IDENTITY_KEY': '11383fb02cd0157363185b8821b8bc325383b124772692c834c14e730d1a3f92'
}

# Parser da mensagem da TTN para o formato da Sentilo - to_send contém os campos a serem enviados
def parser(json_message):
    end_device_ids = json_message["end_device_ids"]
    device_id = end_device_ids["device_id"]
    received_at = json_message["received_at"]
    uplink_message = json_message["uplink_message"];
    to_send = {}
    to_send["timestamp"] = received_at

    # Checa se contém os campos necessários para envio
    for key, value in uplink_message["decoded_payload"].items():
        if key != "latitude" and key != "longitude" and key != "hdop":
            to_send["observation"] = value
        elif key == "latitude":
            to_send["latitude"] = value
        elif key == "longitude":
            to_send["longitude"] = value
    
    # Pelo menos deve conter o valor observado
    if "observation" in to_send:
        send_to_sentilo(device_id, to_send)
    else: # Caso não tenha envia -99 como padrão
        to_send["observation"] = -99
        send_to_sentilo(device_id, to_send)
    return

def send_to_sentilo(sensor_id, packet):
    data_send = {}
    # Caso tenha posiçao
    if "latitude" in packet and "longitude" in packet:
        lat, lng = packet["latitude"], packet["longitude"]
        value = packet["observation"]
        timestamp = packet["timestamp"]
        data_send = {
            "sensors":[
                {
                    "sensor": sensor_id,
                    "location": f"{lat} {lng}",
                    "observations": [{"value": f"{value}"}]
                }
            ]
        }
    else: # Caso não tenha posição
        value = packet["observation"]
        timestamp = packet["timestamp"]
        data_send = {
            "sensors":[
                {
                    "sensor": sensor_id,
                    "observations": [{"value": f"{value}"}]
                }
            ]
        }
    # Envia uma requisição PUT para Sentilo e retorna uma resposta HTTP
    resp = requests.put(url=redirect_url, data=json.dumps(data_send), headers=headers)
    if resp.status_code == 200:
        print("Uplink encaminhado com sucesso!")
    else:
        print("Erro ao encaminhar uplink")
        
    print(resp)
    return