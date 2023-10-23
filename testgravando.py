
import wave

import pyaudio

# Inicialize o objeto PyAudio
p = pyaudio.PyAudio()

# Parâmetros de gravação
chunk = 1024
formato = pyaudio.paInt16
canais = 1
taxa_amostragem = 44100
segundos_gravacao = 10

# Inicie a gravação
stream = p.open(format=formato,
                channels=canais,
                rate=taxa_amostragem,
                input=True,
                frames_per_buffer=chunk)

frames = []

print("Gravando...")

for _ in range(0, int(taxa_amostragem / chunk * segundos_gravacao)):
    data = stream.read(chunk)
    frames.append(data)

print("Gravação concluída.")

# Pare a gravação e feche o fluxo
stream.stop_stream()
stream.close()

# Feche o objeto PyAudio
p.terminate()

# Salve a gravação em um arquivo WAV
wf = wave.open("gravacao.wav", "wb")
wf.setnchannels(canais)
wf.setsampwidth(p.get_sample_size(formato))
wf.setframerate(taxa_amostragem)
wf.writeframes(b"".join(frames))
wf.close()
 