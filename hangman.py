import os
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.popup import Popup

class HangmanCanvas(Widget):
    """Виджет для отрисовки виселицы и человечка на Canvas"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attempts = 6
        self.bind(size=self.draw, pos=self.draw)

    def set_attempts(self, attempts):
        self.attempts = attempts
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.92, 0.94, 0.94, 1)
            cx = self.center_x
            cy = self.y + self.height / 2

            # 1. Основание и столб виселицы
            Line(points=[cx - 80, cy - 70, cx - 20, cy - 70], width=2)
            Line(points=[cx - 50, cy - 70, cx - 50, cy + 70], width=2)
            Line(points=[cx - 50, cy + 70, cx + 30, cy + 70], width=2)
            Line(points=[cx + 30, cy + 70, cx + 30, cy + 40], width=1.5)

            # 2. Части тела человечка при ошибках
            if self.attempts <= 5:
                Ellipse(pos=(cx + 15, cy + 10), size=(30, 30))
            if self.attempts <= 4:
                Line(points=[cx + 30, cy + 10, cx + 30, cy - 30], width=2)
            if self.attempts <= 3:
                Line(points=[cx + 30, cy - 5, cx + 5, cy + 15], width=2)
            if self.attempts <= 2:
                Line(points=[cx + 30, cy - 5, cx + 55, cy + 15], width=2)
            if self.attempts <= 1:
                Line(points=[cx + 30, cy - 30, cx + 10, cy - 65], width=2)
            if self.attempts == 0:
                Line(points=[cx + 30, cy - 30, cx + 50, cy - 65], width=2)

class HangmanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Загрузка словаря из внешнего файла words_hangman.txt
        self.words = self.load_words(os.path.join(os.path.dirname(os.path.abspath(__file__)), "words_hangman.txt"))
        self.word = ""
        self.guessed = []
        self.attempts = 6
        self.used_letters = set()

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # Верхняя панель навигации
        top_bar = BoxLayout(size_hint_y=0.08)
        btn_back = Button(
            text="<< Меню",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.20, 0.28, 0.36, 1),
            color=(0.10, 0.73, 0.61, 1),
            bold=True
        )
        btn_back.bind(on_release=self.go_back)
       
        btn_restart = Button(
            text="Новая игра",
            size_hint_x=0.4,
            background_normal='',
            background_color=(0.10, 0.73, 0.61, 1),
            bold=True
        )
        btn_restart.bind(on_release=lambda x: self.reset_game())

        top_bar.add_widget(btn_back)
        top_bar.add_widget(Widget())
        top_bar.add_widget(btn_restart)
        main_layout.add_widget(top_bar)

        # Поле рисунка виселицы
        self.hangman_canvas = HangmanCanvas(size_hint_y=0.32)
        main_layout.add_widget(self.hangman_canvas)

        # Поле загаданного слова
        self.lbl_word = Label(
            text="_ _ _ _ _",
            font_size='26sp',
            bold=True,
            size_hint_y=0.08,
            color=(0.92, 0.94, 0.94, 1)
        )
        main_layout.add_widget(self.lbl_word)

        # Счетчик оставшихся попыток
        self.lbl_attempts = Label(
            text="Осталось попыток: 6",
            font_size='16sp',
            bold=True,
            size_hint_y=0.06,
            color=(0.10, 0.73, 0.61, 1)
        )
        main_layout.add_widget(self.lbl_attempts)

        # Виртуальная клавиатура с буквами
        self.keyboard_grid = GridLayout(cols=7, spacing=3, size_hint_y=0.4)
        self.keyboard_buttons = {}
        alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

        for letter in alphabet:
            btn = Button(
                text=letter.upper(),
                font_size='14sp',
                background_normal='',
                background_color=(0.20, 0.28, 0.36, 1)
            )
            btn.bind(on_release=lambda instance, l=letter: self.press_letter(l, instance))
            self.keyboard_grid.add_widget(btn)
            self.keyboard_buttons[letter] = btn

        main_layout.add_widget(self.keyboard_grid)
        self.add_widget(main_layout)

        self.reset_game()

    def load_words(self, filename):
        """Загружает список слов из текстового файла."""
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    words = [line.strip().lower() for line in f if line.strip()]
                if words:
                    return words
            except Exception as e:
                print(f"[Warning] Не удалось прочитать файл слов: {e}")

        # Резервный список, если файл не найден
        return ["питон", "программа", "телефон", "проект", "компьютер", "алгоритм"]

    def reset_game(self):
        """Сброс состояния игры."""
        self.word = random.choice(self.words)
        self.guessed = ["_"] * len(self.word)
        self.attempts = 6
        self.used_letters.clear()

        self.hangman_canvas.set_attempts(self.attempts)
        self.update_word_label()
        self.update_attempts_label()

        for l, btn in self.keyboard_buttons.items():
            btn.disabled = False
            btn.background_color = (0.20, 0.28, 0.36, 1)

    def update_word_label(self):
        self.lbl_word.text = " ".join(self.guessed)

    def update_attempts_label(self):
        self.lbl_attempts.text = f"Осталось попыток: {self.attempts}"
        if self.attempts <= 2:
            self.lbl_attempts.color = (0.90, 0.30, 0.23, 1)
        else:
            self.lbl_attempts.color = (0.10, 0.73, 0.61, 1)

    def press_letter(self, letter, btn_widget):
        if letter in self.used_letters:
            return

        self.used_letters.add(letter)
        btn_widget.disabled = True

        if letter in self.word:
            btn_widget.background_color = (0.10, 0.73, 0.61, 1)
            for i, char in enumerate(self.word):
                if char == letter:
                    self.guessed[i] = letter
            self.update_word_label()
        else:
            btn_widget.background_color = (0.90, 0.30, 0.23, 1)
            self.attempts -= 1
            self.hangman_canvas.set_attempts(self.attempts)
            self.update_attempts_label()

        self.check_game_over()

    def check_game_over(self):
        if "_" not in self.guessed:
            self.show_popup("Победа!", f"Поздравляем!\nВы угадали слово: {self.word.upper()}")
            self.disable_all_keys()
        elif self.attempts <= 0:
            self.show_popup("Поражение", f"Вы проиграли!\nЗагаданное слово было: {self.word.upper()}")
            self.disable_all_keys()

    def disable_all_keys(self):
        for btn in self.keyboard_buttons.values():
            btn.disabled = True

    def show_popup(self, title, text):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=text, halign='center', font_size='16sp'))
        btn_close = Button(text="OK", size_hint_y=0.4)
        box.add_widget(btn_close)

        popup = Popup(title=title, content=box, size_hint=(0.8, 0.4), auto_dismiss=False)
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        """Возвращает в Главное меню."""
        if self.manager:
            self.manager.current = 'menu'
