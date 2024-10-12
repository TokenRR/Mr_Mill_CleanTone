import subprocess
import os
from datetime import datetime


def change_to_script_directory():
    script_path = os.path.abspath(__file__)  # Отримуємо повний шлях до поточного файлу
    script_dir = os.path.dirname(script_path)  # Отримуємо директорію, де знаходиться цей файл
    os.chdir(script_dir)  # Переходимо в цю директорію

def get_timestamp() -> str:
    # Отримуємо поточну дату та час у форматі YYYYMMDD_HHMM
    return datetime.now().strftime("%Y-%M-%d_%H-%M-%S")

def split_video_audio(input_file: str, video_output: str, audio_output: str):
    # Використовуємо ffmpeg для розділення відео на відеоряд та аудіодоріжку
    try:
        # Команда для збереження відеоряду без аудіо
        subprocess.run(['ffmpeg', '-loglevel', 'warning', '-y', '-i', input_file, '-an', '-vcodec', 'copy', video_output], check=True)
        
        # Команда для збереження аудіодоріжки без відео
        subprocess.run(['ffmpeg', '-loglevel', 'warning', '-y', '-i', input_file, '-vn', '-acodec', 'libmp3lame', audio_output], check=True)

        print(f"Відеоряд збережено у {video_output}")
        print(f"Аудіодоріжку збережено у {audio_output}")
    except subprocess.CalledProcessError as e:
        print(f"Помилка при розділенні файлу: {e}")

if __name__ == '__main__':
    input_file = '..\\sources\\videoplayback.mp4'
    timestamp = get_timestamp()  # Отримуємо дату та час
    video_output = f'..\\videos\\video_only_{timestamp}.mp4'  # Додаємо дату та час до назви файлу
    audio_output = f'..\\audios\\audio_only_{timestamp}.mp3'  # Додаємо дату та час до назви файлу

    # Викликаємо функцію для зміни директорії
    change_to_script_directory()

    split_video_audio(input_file, video_output, audio_output)
