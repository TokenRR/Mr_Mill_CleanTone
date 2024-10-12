import subprocess
import os

def change_to_script_directory():
    script_path = os.path.abspath(__file__)  # Отримуємо повний шлях до поточного файлу
    script_dir = os.path.dirname(script_path)  # Отримуємо директорію, де знаходиться цей файл
    os.chdir(script_dir)  # Переходимо в цю директорію

def add_watermark(input_video: str, output_video: str, watermark_image: str, position: str):
    # Використовуємо ffmpeg для додавання водяного знаку
    try:
        # Формуємо команду для ffmpeg
        command = [
            'ffmpeg',
            '-loglevel', 'warning', '-y', 
            '-i', input_video,  # Вхідне відео
            '-i', watermark_image,  # Зображення водяного знаку
            '-filter_complex', f"overlay={position}",  # Позиція водяного знаку
            '-codec:a', 'copy',  # Копіюємо аудіо без змін
            output_video  # Вихідне відео
        ]
        
        # Виконуємо команду
        subprocess.run(command, check=True)
        print(f"Водяний знак додано до {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Помилка при додаванні водяного знаку: {e}")

if __name__ == '__main__':
    input_video = '..\\sources\\video.mp4'  # Шлях до вхідного відео
    output_video = '..\\videos\\watermarked_video.mp4'  # Шлях до вихідного відео
    watermark_image = '..\\watermark.png'  # Шлях до зображення водяного знаку
    position = '10:10'  # Позиція водяного знаку (X:Y), наприклад, 10:10 для координат (10, 10)

    # Викликаємо функцію для зміни директорії
    change_to_script_directory()

    add_watermark(input_video, output_video, watermark_image, position)
