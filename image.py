import json
import time
import requests
import base64
from PIL import Image
from io import BytesIO
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class Text2ImageAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

    def save_image_from_base64(self, base64_string, output_path):
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image.save(output_path)
        print(f"Изображение сохранено в {output_path}")
        image.show()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор изображений - СИИ")
        self.root.geometry("600x400")
        self.root.configure(bg="#2C2F36")

        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TButton",
                             background="#333232",
                             foreground="#706d6d",
                             font=("Arial", 12),
                             padding=10)
        self.style.configure("TLabel",
                             background="#2C2F36",
                             foreground="white",
                             font=("Arial", 12))

        # Поле ввода текста
        self.label = ttk.Label(root, text="Введите запрос для генерации изображения:")
        self.label.pack(pady=10)

        self.entry = ttk.Entry(root, width=50, font=("Arial", 12))
        self.entry.pack(pady=10)

        # Выбор ширины
        self.width_label = ttk.Label(root, text="Выберите ширину изображения:")
        self.width_label.pack(pady=5)

        self.width_combo = ttk.Combobox(root, values=[256, 512, 1024], font=("Arial", 12))
        self.width_combo.set(1024)
        self.width_combo.pack(pady=5)

        # Выбор высоты
        self.height_label = ttk.Label(root, text="Выберите высоту изображения:")
        self.height_label.pack(pady=5)

        self.height_combo = ttk.Combobox(root, values=[256, 512, 1024], font=("Arial", 12))
        self.height_combo.set(1024)
        self.height_combo.pack(pady=5)

        # Кнопка генерации
        self.generate_button = ttk.Button(root, text="Генерировать", command=self.generate_image)
        self.generate_button.pack(pady=20)

        self.result_label = ttk.Label(root, text="")
        self.result_label.pack(pady=10)

        # Инициализация API
        self.api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '7FA8793A9DC7C49F88DCDE41E8B96D55', 'E9BE0959F5EAC00535ADED229EA85ECB')
        self.model_id = self.api.get_model()

    def generate_image(self):
        prompt = self.entry.get()
        if not prompt:
            messagebox.showerror("Ошибка", "Введите запрос для генерации изображения.")
            return

        try:
            width = int(self.width_combo.get())
            height = int(self.height_combo.get())

            uuid = self.api.generate(prompt, self.model_id, width=width, height=height)
            images = self.api.check_generation(uuid)

            if images:
                base64_image = images[0]
                output_path = r"C:/Users/agucz/OneDrive/Рабочий стол/IDZ/generated_image.png"
                self.api.save_image_from_base64(base64_image, output_path)
                self.result_label.config(text="Изображение успешно создано!")
            else:
                self.result_label.config(text="Ошибка: Изображение не было создано.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()