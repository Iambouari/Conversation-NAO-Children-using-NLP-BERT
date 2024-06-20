# -*- coding: utf-8 -*-
import requests
import time
from naoqi import ALProxy

ip_nao = "192.168.0.230"
port_nao = 9559
tts = ALProxy("ALTextToSpeech", ip_nao, port_nao)

url = "http://localhost:5000/receive_best_answer"

print("Bem-vindo ao Chatbot do Robo NAO!")
print("Pressione Ctrl+C para sair.")

while True:
    try:
        resposta_recebida = False
        
        while not resposta_recebida:
            try:
                response = requests.get(url)

                if response.status_code == 200:
                    resposta_servidor = response.json()

                    texto_resposta = resposta_servidor.get('answer')
                    info = resposta_servidor.get('info')

                    if texto_resposta:
                        print("Resposta do servidor:", texto_resposta)
                        print("Robô NAO:", info)
                        info = str(info.encode('utf-8'))
                        tts.say(info)
                        resposta_recebida = True
                    else:
                        print("Servidor retornou uma resposta vazia")

                else:
                    print("Houve um problema ao obter a resposta do servidor (status code:", response.status_code, ")")

            except requests.RequestException as e:
                print("Erro ao fazer a requisição:", str(e))
                time.sleep(1)  # Espera 1 segundo antes de tentar novamente

    except KeyboardInterrupt:
        print("\nChatbot encerrado pelo usuário. Obrigado!")
