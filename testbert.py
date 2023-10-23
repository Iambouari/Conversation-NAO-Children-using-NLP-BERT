import numpy as np
import speech_recognition as sr
import tensorflow as tf
from transformers import BertTokenizer, TFBertForQuestionAnswering

# Inicialize o reconhecimento de fala
recognizer = sr.Recognizer()

# Carregue o modelo BERT pré-treinado e o tokenizador
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
modelo_bert = TFBertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# Função para responder a perguntas usando o modelo BERT
def responder_pergunta(contexto, pergunta):
    # Tokenize a pergunta e o contexto
    inputs = tokenizer.encode_plus(pergunta, contexto, add_special_tokens=True, return_tensors="tf")
    
    # Obtenha a resposta do modelo BERT
    resposta = modelo_bert(inputs)
    
    # Decodifique a resposta
    start_logits, end_logits = resposta['start_logits'], resposta['end_logits']
    inicio, fim = tf.argmax(start_logits, axis=1).numpy()[0], tf.argmax(end_logits, axis=1).numpy()[0]
    resposta_texto = tokenizer.decode(inputs['input_ids'][0][inicio:fim+1])
    
    return resposta_texto

# Função para capturar entrada de áudio e responder
def chatbot():
    with sr.Microphone() as source:
        print("Diga algo:")
        try:
            audio_data = recognizer.listen(source, timeout=5)
            texto_reconhecido = recognizer.recognize_google(audio_data, language="pt-BR")
            print("Você disse:", texto_reconhecido)
            
            # Contexto (informações gerais)
            contexto = "dialogo de apresentação."
            
            resposta = responder_pergunta(contexto, texto_reconhecido)
            print("Resposta do Chatbot:", resposta)
        except sr.WaitTimeoutError:
            print("Nenhum som detectado. Tente novamente.")
        except sr.UnknownValueError:
            print("Não foi possível reconhecer a fala. Tente novamente.")
        except Exception as e:
            print(f"Erro: {e}")

# Inicie o chatbot
while True:
    chatbot()
