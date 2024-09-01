# -*- coding: utf-8 -*-
import qi
import sys
import time
import functools
from naoqi import ALProxy
import requests
import json
import os

# Garantir que stdout e stderr estejam usando UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')


ip = "192.168.137.252"
port = 9559

def set_eyes_color(leds, color):
    color_map = {
        "branco": 0xFFFFFF,
        "laranja": 0xFFA500,
        "verde": 0x00FF00,
        "vermelho": 0xFF0000,
        "desligado": 0x000000
    }
    if color in color_map:
        leds.fadeRGB("FaceLeds", color_map[color], 1.0)
        print("Cor dos olhos definida")

def nao_speech_recognition(asr_service):
    print("Ativando reconhecimento de fala do Nao.")
    asr_service.pause(True)
    asr_service.setVocabulary(["NAO", "STOP"], False)
    asr_service.pause(False)
    asr_service.subscribe("Comand")
    print("Reconhecimento de fala ativado e vocabulário definido.")

def deactivate_nao_speech_recognition(asr_service):
    try:
        asr_service.unsubscribe("Test_ASR")
        print("Reconhecimento de fala desativado.")
    except RuntimeError as e:
        print("Erro ao desinscrever: {}".format(e))
    asr_service.pause(True)

def load_corpus(filename):
    file_path = os.path.join(os.getcwd(), filename)
    try:
        with open(file_path, 'r') as f:
            corpus = json.load(f)
            print("Corpus carregado com sucesso")
        return corpus
    except IOError:
        print("Arquivo {} não encontrado.".format(filename))
        sys.exit(1)

def find_context_by_id(corpus, context_id):
    for context in corpus:
        if context['id'] == context_id:
            return context['context']
    return None

class WordRecognizedModule(object):
    def __init__(self, app):
        super(WordRecognizedModule, self).__init__()
        app.start()
        session = app.session
        self.asr_service = session.service("ALSpeechRecognition")
        self.memory_service = session.service("ALMemory")
        self.leds_service = session.service("ALLeds")
        self.tts_service = session.service("ALTextToSpeech")
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.corpus = load_corpus('corpus.json')
        self.signal_id = None
        self.touch_id = None
        self.subscribe_to_word_recognized()
        self.subscribe_to_touch()

        self.asr_service.setLanguage("English")
        nao_speech_recognition(self.asr_service)
        print("Module initialized and ALSpeechRecognition subscribed.")

    def subscribe_to_word_recognized(self):
        if self.signal_id:
            self.subscriber.signal.disconnect(self.signal_id)
            print("Desconectando sinal anterior de reconhecimento de palavras.")
        self.subscriber = self.memory_service.subscriber("WordRecognized")
        self.signal_id = self.subscriber.signal.connect(self.on_word_recognized)
        print("Inscrito para o evento WordRecognized.")

    def subscribe_to_touch(self):
        if self.touch_id:
            self.touch.signal.disconnect(self.touch_id)
            print("Desconectando sinal anterior de toque.")
        self.touch_id = self.touch.signal.connect(functools.partial(self.on_touched, "TouchChanged"))
        print("Inscrito para o evento TouchChanged.")

    def on_word_recognized(self, value):
        if len(value) > 1 and isinstance(value[0], str) and isinstance(value[1], float):
            command = value[0].strip()
            if command:
                print("Comando reconhecido: {}".format(command))
                
                if command.lower() == "nao":
                    self.handle_nao_command()
                
                elif command.lower() == "stop":
                    self.handle_stop_command()

    def handle_nao_command(self):
        deactivate_nao_speech_recognition(self.asr_service)
        self.tts_service.say("Ola humano!, espere 5 segundos, e me fala como eu posso te ajudar")
        time.sleep(3)
        set_eyes_color(self.leds_service, "laranja")
    
        question = None
        for attempt in range(3):
            print("Enviando sinal para iniciar o reconhecimento de fala no Python 3.10, tentativa {}".format(attempt + 1))
            try:
                response = requests.post('http://localhost:5001/start_recognition')
                response.raise_for_status()
                if response.status_code == 200:
                    response_data = response.json()
                    question = response_data.get('question', '').strip()
                    if question:
                        break
            except requests.RequestException as e:
                print("Falha ao enviar sinal para iniciar o reconhecimento de fala: {}".format(e))
                self.tts_service.say("Nao consegui entender tua pergunta, você pode repetir após 5 segundos, por favor?")
                time.sleep(3)

        if question:
            set_eyes_color(self.leds_service, "branco")
            print("Pergunta recebida do ASR do Google: {}".format(question.encode('utf-8')))
            self.tts_service.say("Eu ouvi tua pergunta, me da um minuto, eu ja te respondo")
            set_eyes_color(self.leds_service, "laranja")

            start_time = time.time()  # Captura o tempo no início do processamento

            try:
                response = requests.post('http://localhost:5000/process', json={'question': question})
                response.raise_for_status()
                response_data = response.json().get('response', {})
                answer = response_data.get('answer', 'Desculpe, não consegui encontrar a resposta.')
                context_id = response_data.get('context_id', 'N/A')
                context_text = find_context_by_id(self.corpus, context_id)

                end_time = time.time()  # Captura o tempo no final do processamento
                elapsed_time = end_time - start_time
                print("Tempo decorrido no processamento: {:.2f} segundos".format(elapsed_time))

                set_eyes_color(self.leds_service, "verde")
                if context_text:
                    print("Contexto: {}".format(context_text.encode('utf-8')))
                    self.tts_service.say(context_text)
                    set_eyes_color(self.leds_service, "branco")
                    time.sleep(1)
                    self.tts_service.say("Espero que a resposta lhe agradou, não hesite em me chamar se tiver outra pergunta.")
                else:
                    set_eyes_color(self.leds_service, "vermelho")
                    print("Contexto não encontrado para o ID: {}".format(context_id))
                    self.tts_service.say("Contexto não encontrado.")
            except requests.RequestException as e:
                print("Falha ao enviar pergunta para o servidor Flask: {}".format(e))
                self.tts_service.say("Desculpe, ocorreu um erro ao processar sua pergunta.")
        else:
            set_eyes_color(self.leds_service, "vermelho")
            self.tts_service.say("Desculpe, não consegui entender a sua pergunta.")
    
        set_eyes_color(self.leds_service, "desligado")
        nao_speech_recognition(self.asr_service)
        print("Reconhecimento de fala reativado após lidar com o comando 'nao'.")

    def handle_stop_command(self):
        print("Processo parado. Reiniciando reconhecimento de fala.")
        try:
            self.asr_service.unsubscribe("Test_ASR")
        except RuntimeError as e:
            print("Erro ao desinscrever: {}".format(e))
        self.subscribe_to_word_recognized()
        nao_speech_recognition(self.asr_service)
        print("Reconhecimento de fala reiniciado.") 

    def on_touched(self, strVarName, value):
        touched_bodies = [p[0] for p in value if p[1]]
        if "Head/Touch/Middle" in touched_bodies:
            print("Cabeça tocada.")
            self.handle_stop_command()
        if "LArm" in touched_bodies:
            print("Braço esquerdo tocado. Ativando reconhecimento de fala.")
            nao_speech_recognition(self.asr_service)
        if "RArm" in touched_bodies:
            print("Braço direito tocado. Desativando reconhecimento de fala.")
            deactivate_nao_speech_recognition(self.asr_service)

def main(ip, port):
    try:
        connection_url = "tcp://" + ip + ":" + str(port)
        app = qi.Application(["WordRecognizedModule", "--qi-url=" + connection_url])
        print("Conectando ao Naoqi no IP {ip} e porta {port}.")
    except RuntimeError:
        print("Não foi possível conectar ao Naoqi no ip \"{}\" na porta {}.\n".format(ip, port))
        sys.exit(1)
    
    word_recognized_module = WordRecognizedModule(app)
    print("Iniciando o módulo WordRecognizedModule.") 
    app.run()

if __name__ == "__main__":
    main(ip, port)
