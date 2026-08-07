import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import sys
import whisper
import os
import glob

def grabar_reunion(duracion_minutos=30, filename="meet_audio.wav"):
    fs = 48000  # Frecuencia de muestreo estándar
    
    # Intentar detectar el dispositivo de mezcla estéreo (Stereo Mix) o WASAPI Loopback para grabar audio del sistema
    print(f"[+] Usando dispositivo ID: 9 (Varios micrófonos / Sistema)")
    print("[+] Grabando audio del sistema...")
    print("[!] Presiona Ctrl+C en cualquier momento para detener y transcribir.")
    
    audio_data = []
    
    def callback(indata, frames, time_info, status):
        audio_data.append(indata.copy())

    try:
        # Grabar usando el dispositivo configurado
        with sd.InputStream(samplerate=fs, channels=2, callback=callback, device=9):
            duracion_segundos = duracion_minutos * 60
            tiempo_inicio = time.time()
            
            while True:
                if time.time() - tiempo_inicio > duracion_segundos:
                    break
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n[!] ¡Grabación detenida manualmente con Ctrl+C!")
    except Exception as e:
        print(f"\n[!] Error durante la grabación: {e}")
        return None

    if audio_data:
        audio_completo = np.concatenate(audio_data, axis=0)
        wav.write(filename, fs, audio_completo)
        print(f"[v] Audio guardado en: {filename}")
        return filename
    else:
        print("[!] No se capturó audio.")
        return None

def transcribir(filename):
    # Buscar ffmpeg.exe automáticamente en todo el sistema
    print("[+] Buscando la ruta de FFmpeg en tu computadora...")
    ffmpeg_encontrado = None
    patrones = [
        r"C:\Users\Lenovo\Downloads\**\ffmpeg.exe",
        r"C:\ffmpeg\**\ffmpeg.exe",
        r"C:\**\ffmpeg.exe"
    ]
    
    for patron in patrones:
        resultados = glob.glob(patron, recursive=True)
        if resultados:
            ffmpeg_encontrado = resultados[0]
            break
            
    if ffmpeg_encontrado:
        ruta_bin = os.path.dirname(ffmpeg_encontrado)
        os.environ["PATH"] = ruta_bin + os.pathsep + os.environ.get("PATH", "")
        print(f"[v] ¡FFmpeg encontrado en: {ruta_bin}!")
    else:
        print("[!] ADVERTENCIA: No se encontró ffmpeg.exe automáticamente.")

    print("\n[+] Cargando modelo Whisper ...")
    model = whisper.load_model("base") 

    print("[+] Transcribiendo audio de la reunión ...")
    result = model.transcribe(filename, language="es")
    texto = result["text"]

    # Definir la carpeta y asegurar que exista
    carpeta_destino = r"C:\Users\Lenovo\Documents\MisTranscripciones"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Guardar el archivo en la carpeta específica
    ruta_archivo = os.path.join(carpeta_destino, "transcripcion_meet.txt")
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(texto)

    print("[v] ¡Transcripción completada con éxito!")
    print(f"[v] Guardada en: {ruta_archivo}")

if __name__ == "__main__":
    entrada = input("Introduce los minutos estimados que durará la reunión (o presiona Enter para 30 min): ")
    
    if entrada.strip() == "":
        minutos = 30.0
        print("[+] No ingresaste número, usando valor por defecto: 30 minutos.")
    else:
        minutos = float(entrada)
        
    archivo = grabar_reunion(duracion_minutos=minutos)
    
    if archivo:
        transcribir(archivo)
        
        # Eliminar el archivo de audio temporal si ya no se necesita
        if os.path.exists(archivo):
            os.remove(archivo)
            print("[+] Archivo temporal eliminado.")