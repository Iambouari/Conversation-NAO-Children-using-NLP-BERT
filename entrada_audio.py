import speech_recognition as sr
import requests

# URL do servidor Flask
url_pergunta = "http://localhost:5000/ask"

def reconhecer_fala():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Diga algo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language='pt-BR')  
        return texto
    except sr.UnknownValueError:
        print("Não consegui entender o que você disse.")
    except sr.RequestError as e:
        print(f"Erro no serviço de reconhecimento de fala; {e}")
    return None

def enviar_pergunta_para_servidor(pergunta):
    try:
        print(f"\nEnviando pergunta")

        # Dados para enviar ao servidor Flask
        dados = {'question': pergunta}

        # Enviar a pergunta para o servidor Flask
        response = requests.post(url_pergunta, json=dados)

        # Verificar se a resposta foi recebida com sucesso
        if response.status_code == 200:
            print("Pergunta enviada ao servidor com sucesso.")
        else:
            print("Erro ao enviar pergunta ao servidor:", response.status_code)
    except requests.RequestException as e:
        print(f"Erro durante a comunicação com o servidor: {e}")

if __name__ == "__main__":
    try:
        while True:
            pergunta = reconhecer_fala()
            if pergunta:
                print("Pergunta reconhecida:", pergunta)
                if "exit" in pergunta.lower():
                    print("Encerrando o programa.")
                    break
                enviar_pergunta_para_servidor(pergunta)
            else:
                print("Não foi possível reconhecer a fala. Tente novamente.")
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
