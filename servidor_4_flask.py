# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch
import json

app = Flask(__name__)

model_name = "ArthurBaia/albertina-squad-v1.1-pt.br"
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Função para carregar o corpus do arquivo JSON
def load_corpus(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        corpus = json.load(file)
    return corpus

try:
    corpus = load_corpus('corpus_dataset.json')
except Exception as e:
    print("Erro ao carregar o corpus:", str(e))


best_answer = {}

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data['question']
        print(f"Pergunta recebida do cliente: {question}")

        # Lista para armazenar as respostas de todos os contextos
        answers = []

        for item in corpus:
            context = item['context']

            # Tokenizar a pergunta e o contexto
            inputs = tokenizer(question, context, return_tensors='pt')

            # Passar a entrada tokenizada para o modelo
            with torch.no_grad():
                outputs = model(**inputs)
                answer_start = torch.argmax(outputs.start_logits)
                answer_end = torch.argmax(outputs.end_logits) + 1
                answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end]))

            # Calcular a pontuação da resposta
            start_score = outputs.start_logits[0][answer_start].item()
            end_score = outputs.end_logits[0][answer_end - 1].item()
            total_score = start_score + end_score

            # Armazenar a resposta junto com o contexto correspondente e a pontuação
            answers.append({'answer': answer, 'info': context, 'score': total_score})

        # Selecionar a resposta com a maior pontuação
        global best_answer
        best_answer = max(answers, key=lambda x: x['score'])
        del best_answer['score']
        print("Melhor resposta selecionada:", best_answer)

        return jsonify(best_answer)

    except Exception as e:
        print("Erro ao processar a pergunta:", str(e))
        return jsonify({'error': 'Erro ao processar a pergunta'})

@app.route('/receive_best_answer', methods=['GET'])
def receive_best_answer():
    try:
        global best_answer
        if best_answer:
            response = jsonify(best_answer)
            best_answer = {}  # Limpa a resposta após enviá-la
            return response
        else:
            return jsonify({'error': 'Ainda não há melhor resposta disponível'})
    except Exception as e:
        print("Erro ao processar a requisição de melhor resposta:", str(e))
        return jsonify({'error': 'Erro ao processar a requisição de melhor resposta'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
