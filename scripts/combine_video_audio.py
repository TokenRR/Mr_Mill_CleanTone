import subprocess
import os

def change_to_script_directory():
    script_path = os.path.abspath(__file__)  # Отримуємо повний шлях до поточного файлу
    script_dir = os.path.dirname(script_path)  # Отримуємо директорію, де знаходиться цей файл
    os.chdir(script_dir)  # Переходимо в цю директорію

def combine_video_audio(video_file: str, audio_file: str, output_file: str):
    # Використовуємо ffmpeg для об'єднання відео та аудіо
    try:
        command = [
            'ffmpeg',
            '-loglevel', 'warning', '-y', 
            '-i', video_file,  # Вхідне відео
            '-i', audio_file,  # Вхідна аудіодоріжка
            '-c:v', 'copy',  # Копіюємо відео без змін
            '-c:a', 'aac',  # Кодек для аудіо
            '-strict', 'experimental',  # Додаткова опція для використання aac
            output_file  # Вихідний файл
        ]

        # Виконуємо команду
        subprocess.run(command, check=True)
        print(f"Відео та аудіо об'єднано у {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Помилка при об'єднанні: {e}")

if __name__ == '__main__':
    video_file = '..\\videos\\video_only_2024-15-05_03-15-38.mp4'  # Шлях до відео
    audio_file = '..\\audios\\audio_only_2024-15-05_03-15-38.mp3'  # Шлях до аудіо
    output_file = '..\\videos\\combined_video.mp4'  # Шлях до виходу

    # Викликаємо функцію для зміни директорії
    change_to_script_directory()

    combine_video_audio(video_file, audio_file, output_file)
