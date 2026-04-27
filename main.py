import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = 'weather_data.json'

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")

        # Ввод данных
        self.frame_input = ttk.Frame(root)
        self.frame_input.pack(padx=10, pady=10, fill='x')

        # Дата
        ttk.Label(self.frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky='w')
        self.entry_date = ttk.Entry(self.frame_input)
        self.entry_date.grid(row=0, column=1)

        # Температура
        ttk.Label(self.frame_input, text="Температура (°C):").grid(row=1, column=0, sticky='w')
        self.entry_temp = ttk.Entry(self.frame_input)
        self.entry_temp.grid(row=1, column=1)

        # Описание
        ttk.Label(self.frame_input, text="Описание погоды:").grid(row=2, column=0, sticky='w')
        self.entry_desc = ttk.Entry(self.frame_input)
        self.entry_desc.grid(row=2, column=1)

        # Осадки
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(self.frame_input, text="Осадки", variable=self.precip_var).grid(row=3, column=0, sticky='w')

        # Кнопка добавить
        ttk.Button(self.frame_input, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=2, pady=5)

        # Таблица для отображения записей
        columns = ('date', 'temp', 'desc', 'precip')
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        self.tree.heading('date', text='Дата')
        self.tree.heading('temp', text='Температура')
        self.tree.heading('desc', text='Описание')
        self.tree.heading('precip', text='Осадки')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

        # Фильтр
        self.frame_filter = ttk.Frame(root)
        self.frame_filter.pack(padx=10, pady=5, fill='x')

        ttk.Label(self.frame_filter, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky='w')
        self.filter_date_entry = ttk.Entry(self.frame_filter)
        self.filter_date_entry.grid(row=0, column=1)

        ttk.Label(self.frame_filter, text="Температура выше:").grid(row=0, column=2, sticky='w')
        self.filter_temp_entry = ttk.Entry(self.frame_filter)
        self.filter_temp_entry.grid(row=0, column=3)

        ttk.Button(self.frame_filter, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=5)
        ttk.Button(self.frame_filter, text="Сбросить фильтр", command=self.load_records).grid(row=0, column=5, padx=5)

        # Кнопки сохранения/загрузки
        self.frame_save_load = ttk.Frame(root)
        self.frame_save_load.pack(padx=10, pady=5)

        ttk.Button(self.frame_save_load, text="Сохранить", command=self.save_records).pack(side='left', padx=5)
        ttk.Button(self.frame_save_load, text="Загрузить", command=self.load_records).pack(side='left', padx=5)

        # Храним записи
        self.records = []

        # Загружаем из файла при старте
        self.load_records()

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def add_record(self):
        date_str = self.entry_date.get().strip()
        temp_str = self.entry_temp.get().strip()
        desc = self.entry_desc.get().strip()
        precip = self.precip_var.get()

        # Проверка
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Некорректный формат даты.")
            return
        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Заполните описание погоды.")
            return

        record = {
            'date': date_str,
            'temp': temp,
            'desc': desc,
            'precip': precip
        }
        self.records.append(record)
        self.insert_record(record)
        self.clear_inputs()

    def insert_record(self, record):
        precip_text = 'Да' if record['precip'] else 'Нет'
        self.tree.insert('', 'end', values=(record['date'], record['temp'], record['desc'], precip_text))

    def clear_inputs(self):
        self.entry_date.delete(0, tk.END)
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.precip_var.set(False)

    def save_records(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные сохранены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_records(self):
        self.tree.delete(*self.tree.get_children())
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except:
                self.records = []
        else:
            self.records = []

        for rec in self.records:
            self.insert_record(rec)

    def apply_filter(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter_str = self.filter_temp_entry.get().strip()

        filtered = self.records

        if date_filter:
            try:
                datetime.strptime(date_filter, '%Y-%m-%d')
                filtered = [r for r in filtered if r['date'] == date_filter]
            except:
                messagebox.showerror("Ошибка", "Некорректный формат даты фильтра.")
                return

        if temp_filter_str:
            try:
                temp_filter = float(temp_filter_str)
                filtered = [r for r in filtered if r['temp'] > temp_filter]
            except:
                messagebox.showerror("Ошибка", "Температура фильтр должна быть числом.")
                return

        self.tree.delete(*self.tree.get_children())
        for rec in filtered:
            self.insert_record(rec)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
