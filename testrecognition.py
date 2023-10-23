import speech_recognition as sr

recognizer = sr.Recognizer()

audio_file = "gravacao.wav"  # Substitua pelo caminho do seu arquivo de áudio

with sr.AudioFile(audio_file) as source:
    audio_data = recognizer.record(source)  # Grava o áudio do arquivo

try:
    # Reconhece o discurso do áudio
    texto_reconhecido = recognizer.recognize_google(audio_data, language="pt-BR")
    print("Texto Reconhecido:", texto_reconhecido)
except sr.UnknownValueError:
    print("Não foi possível reconhecer o áudio")
except sr.RequestError as e:
    print(f"Erro na solicitação de reconhecimento de fala: {e}")
