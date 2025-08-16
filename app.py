import os
import tempfile
import wave
import pyaudio
import keyboard
import pyautogui
import pyperclip 
from groq import Groq
import subprocess
import time



client = Groq(api_key="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")

def grabar_audio(rate=16000, canales=1, fragmento=1024):
    """
    
    Args:
        rate (int): Frecuencia de muestreo en Hz
        canales (int): Número de canales de audio
        fragmento (int): Tamaño del buffer
        
    Returns:
        tuple: (frames grabados, frecuencia de muestreo)
    """
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=canales,
        rate=rate,
        input=True,
        frames_per_buffer=fragmento,
    )

    print("Presiona y mantén presionada la tecla INSERT para comenzar a grabar...")
    frames = []

    # Espera a que se presione la tecla Insert
    keyboard.wait('insert')
    print("Grabando... Suelta INSERT para detener.")

    # Mientras se mantenga presionada la tecla Insert, graba audio
    while keyboard.is_pressed('insert'):
        data = stream.read(fragmento)
        frames.append(data)

    print("Grabación finalizada.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    return frames, rate

def guardar_audio(frames, frecuencia_muestreo):
    

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp:
        wf= wave.open(audio_temp.name, 'wb') 
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(frecuencia_muestreo)
        wf.writeframes(b''.join(frames))
        wf.close()

    return audio_temp.name

def transcribir_audio(ruta_archivo_audio):
    """
    Transcribe el archivo de audio usando la API de Grock y retorna el texto.
    """
    try:
        with open(ruta_archivo_audio, "rb") as archivo:
            transcripcion = client.audio.transcriptions.create(
                file=(os.path.basename(ruta_archivo_audio),archivo.read()),
                model="whisper-large-v3",
                prompt="Una persona normal hablando",
                response_format="text",
                language="es",
            )
        return transcripcion

    except Exception as e:
        print(f"Ocurrió un error durante la transcripción: {str (e)}")
        return None

def copiar_transcripcion_al_portapapeles(texto):
    """
    Copia el texto al portapapeles y lo pega automáticamente en el Bloc de notas
    """
    pyperclip.copy(texto)
    print("Abriendo el Bloc de notas...") 
    # Abre el Bloc de notas
    notepad = subprocess.Popen(['notepad.exe'])
    
    # Espera un momento para que el Bloc de notas se abra
    time.sleep(1)
    
    # Pega el texto
    pyautogui.hotkey('ctrl', 'v')
    
    print("El texto ha sido pegado en el Bloc de notas.")

def main():
    while True:
        frames,frecuencia_muestreo = grabar_audio()
        archivo_audio_temp = guardar_audio(frames, frecuencia_muestreo)
        print("Transcribiendo...")
        transcripcion = transcribir_audio(archivo_audio_temp)

        if transcripcion:
            print("\nTranscripción completada.")
            print("-------------------------------")
            print(transcripcion)
            print("-------------------------------")
            copiar_transcripcion_al_portapapeles(transcripcion)
        else:
            print("No se pudo obtener transcripción.")

        os.unlink(archivo_audio_temp)
        print("\nListo para la próxima grabación. Presiona INS para comenzar.")

if __name__ == "__main__":
    main()
