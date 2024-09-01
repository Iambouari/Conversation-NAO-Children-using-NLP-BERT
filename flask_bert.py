from flask import Flask, request, jsonify
import torch
import json
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuração do dispositivo
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# Nome do modelo
model_name_bl = "ArthurBaia/albertina-squad-v1.1-pt.br"

# Carregar o modelo e o tokenizer usando AutoModelForQuestionAnswering e AutoTokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_name_bl).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name_bl)

# Carregar contexto do arquivo corpus.json
with open('corpus.json', 'r', encoding='utf-8') as f:
    corpus_data = json.load(f)
contexts = [item['context'] for item in corpus_data]
context_ids = [item['id'] for item in corpus_data]

# Inicializar o TF-IDF Vectorizer e ajustar aos contextos
vectorizer = TfidfVectorizer().fit(contexts)
context_vectors = vectorizer.transform(contexts)

app = Flask(__name__)

def get_answer(context, question):
    try:
        # Tokenizar a pergunta e o contexto
        inputs = tokenizer(question, context, return_tensors='pt').to(device)

        # Obter previsões do modelo
        with torch.no_grad():
            outputs = model(**inputs)
            answer_start_scores = outputs.start_logits
            answer_end_scores = outputs.end_logits

            # Obter as melhores posições de início e fim
            answer_start = torch.argmax(answer_start_scores)
            answer_end = torch.argmax(answer_end_scores) + 1

            # Converter tokens para string
            answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end]))

            # Calcular a pontuação da resposta
            start_score = answer_start_scores[0][answer_start].item()
            end_score = answer_end_scores[0][answer_end - 1].item()
            total_score = start_score + end_score

            # Validar resposta vazia
            if answer.strip() == "":
                total_score = float('-inf')

        return {"answer": answer, "score": total_score}
    except Exception as e:
        print("Erro ao obter resposta: ", str(e))
        return None

@app.route('/process', methods=['POST'])
def process_question():
    start_time = time.time()  # Captura o tempo no início do processamento
    try:
        data = request.get_json()
        question = data['question']
        print("Pergunta recebida do cliente: {}".format(question))

        # Calcular o vetor TF-IDF para a pergunta
        question_vector = vectorizer.transform([question])

        # Calcular similaridade do cosseno entre a pergunta e todos os contextos
        similarities = cosine_similarity(question_vector, context_vectors).flatten()

        # Selecionar os contextos mais relevantes (top 5)
        top_k = 5
        relevant_indices = np.argsort(similarities)[-top_k:][::-1]

        # Lista para armazenar as respostas dos contextos relevantes
        answers = []

        for idx in relevant_indices:
            context = contexts[idx]
            context_id = context_ids[idx]
            print("Processando contexto ID: {}".format(context_id))

            # Obter a resposta usando o método get_answer
            answer = get_answer(context, question)
            if answer is not None:
                # Armazenar a resposta junto com o contexto correspondente e a pontuação
                answers.append({'answer': answer['answer'], 'info': context, 'score': answer['score'], 'context_id': context_id})
                print("Context ID: {} | Score: {} | Answer: {}".format(context_id, answer['score'], answer['answer']))

        if not answers:
            return jsonify({'error': 'Nenhuma resposta válida encontrada'})

        # Selecionar a resposta com a melhor pontuação
        best_answer = max(answers, key=lambda x: x['score'])
        print("Melhor resposta encontrada:", best_answer)

        del best_answer['score']

        return jsonify({'response': best_answer})

    except Exception as e:
        print("Erro ao processar a pergunta:", str(e))
        return jsonify({'error': 'Erro ao processar a pergunta'})
    finally:
        end_time = time.time()  # Captura o tempo no final do processamento
        elapsed_time = end_time - start_time
        print("Tempo total de processamento: {:.2f} segundos".format(elapsed_time))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
