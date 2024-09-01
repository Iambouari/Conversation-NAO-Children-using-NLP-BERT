# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import speech_recognition as sr
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


app = Flask(__name__)

@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    print("Rota /start_recognition acessada.")
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        print("Esperando pergunta...")
        audio = r.listen(source)
        print("Áudio capturado.")
    
    try:
        question = r.recognize_google(audio, language="pt-BR")
        print("Pergunta reconhecida:", question)
        return jsonify({'question': question})
    except sr.UnknownValueError:
        print("Não consegui entender o que você disse.")
        return jsonify({'error': 'Não consegui entender a pergunta.'}), 400
    except sr.RequestError as e:
        print("Erro no serviço de reconhecimento de fala:", e)
        return jsonify({'error': 'Erro no serviço de reconhecimento de fala: {}'.format(e)}), 500

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    app.run(port=5001, debug=True)
