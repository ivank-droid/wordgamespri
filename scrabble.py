import os
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


class ScrabbleTile(Button):
    """Визуальная плашка буквы в стиле классического Эрудита."""
    def __init__(self, letter="", score=0, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.92, 0.85, 0.70, 1) if letter else (0.3, 0.3, 0.35, 0.5)
        self.color = (0.15, 0.15, 0.20, 1)
        self.bold = True
        self.set_tile(letter, score)

    def set_tile(self, letter, score):
        if letter:
            self.text = f"[size=24sp][b]{letter.upper()}[/b][/size]\n[size=10sp][color=555555]{score}[/color][/size]"
            self.markup = True
            self.background_color = (0.92, 0.85, 0.70, 1)
        else:
            self.text = ""
            self.background_color = (0.25, 0.25, 0.30, 0.5)


class ScrabbleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.DICT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words_dictionary.txt")
        
        # Стоимость букв (классические очки Эрудит/Scrabble)
        self.scores = {
            'а': 1, 'в': 1, 'е': 1, 'и': 1, 'н': 1, 'о': 1, 'р': 1, 'с': 1, 'т': 1,
            'д': 2, 'к': 2, 'л': 2, 'м': 2, 'п': 2, 'у': 2,
            'б': 3, 'г': 3, 'е': 3, 'ь': 3, 'я': 3,
            'й': 4, 'ы': 4, 'ж': 5, 'з': 5, 'х': 5, 'ц': 5, 'ч': 5,
            'ш': 8, 'э': 8, 'ю': 8, 'ф': 10, 'щ': 10, 'ъ': 10
        }

        # Генерация мешка с буквами
        self.letter_bag = []
        for letter, score in self.scores.items():
            count = max(1, 10 - score)
            self.letter_bag.extend([letter] * count)

        # Загрузка словаря
        self.load_dictionary()

        # Инициализация состояния и интерфейса
        self.reset_game_state()
        self.build_ui()

    def load_dictionary(self):
        """Загрузка базы слов из словаря."""
        self.dictionary = set()
        if os.path.exists(self.DICT_FILE):
            try:
                with open(self.DICT_FILE, "r", encoding="utf-8") as f:
                    self.dictionary = {line.strip().lower().replace('ё', 'е') for line in f if line.strip()}
            except Exception as e:
                print(f"[Warning] Ошибка загрузки словаря: {e}")

        if not self.dictionary:
            self.dictionary = {"код", "кот", "ток", "робот", "питон", "нота", "пират", "автор"}

    def reset_game_state(self):
        """Сброс игрового состояния."""
        self.player_letters = []
        self.total_score = 0
        self.draw_new_letters()

    def draw_new_letters(self):
        """Добор букв в руку до 7 штук."""
        while len(self.player_letters) < 7:
            self.player_letters.append(random.choice(self.letter_bag))

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)

        # 1. Верхняя панель: Навигация, Кнопка «Новая игра» и Счет
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        
        btn_back = Button(
            text="<< Меню",
            size_hint_x=0.28,
            background_normal='',
            background_color=(0.20, 0.28, 0.36, 1),
            color=(0.10, 0.73, 0.61, 1),
            bold=True
        )
        btn_back.bind(on_release=self.go_back)

        btn_restart = Button(
            text="Новая игра",
            size_hint_x=0.32,
            background_normal='',
            background_color=(0.10, 0.73, 0.61, 1),
            bold=True
        )
        btn_restart.bind(on_release=lambda x: self.restart_game())

        self.lbl_score = Label(
            text=f"Счет: {self.total_score}",
            size_hint_x=0.40,
            bold=True,
            font_size='16sp',
            color=(0.10, 0.73, 0.61, 1)
        )

        top_bar.add_widget(btn_back)
        top_bar.add_widget(btn_restart)
        top_bar.add_widget(self.lbl_score)
        main_layout.add_widget(top_bar)

        # 2. Панель плашек (Буквы на руках)
        lbl_tiles_title = Label(
            text="Ваши буквы (нажмите, чтобы добавить в слово):",
            font_size='13sp',
            size_hint_y=0.05,
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(lbl_tiles_title)

        self.tiles_grid = GridLayout(cols=7, spacing=5, size_hint_y=0.15)
        self.tile_buttons = []

        for i in range(7):
            tile = ScrabbleTile()
            tile.bind(on_release=lambda instance, idx=i: self.on_tile_click(idx))
            self.tile_buttons.append(tile)
            self.tiles_grid.add_widget(tile)

        self.update_tiles_display()
        main_layout.add_widget(self.tiles_grid)

        # 3. Поле ввода слова
        self.txt_word = TextInput(
            hint_text="Введите или наберите слово...",
            font_size='20sp',
            multiline=False,
            halign='center',
            size_hint_y=0.12,
            padding=[10, 12, 10, 10]
        )
        self.txt_word.bind(on_text_validate=lambda x: self.submit_word())
        main_layout.add_widget(self.txt_word)

        # 4. Панель управления (Сыграть слово / Очистить / Поменять буквы)
        btn_submit = Button(
            text="Сыграть слово",
            font_size='16sp',
            bold=True,
            size_hint_y=0.12,
            background_normal='',
            background_color=(0.18, 0.80, 0.44, 1)
        )
        btn_submit.bind(on_release=lambda x: self.submit_word())
        main_layout.add_widget(btn_submit)

        actions_bar = BoxLayout(size_hint_y=0.10, spacing=8)

        btn_clear = Button(
            text="Очистить ввод",
            background_normal='',
            background_color=(0.90, 0.49, 0.13, 1),
            bold=True
        )
        btn_clear.bind(on_release=lambda x: setattr(self.txt_word, 'text', ''))

        btn_refresh = Button(
            text="Сменить буквы (-5 очков)",
            background_normal='',
            background_color=(0.91, 0.30, 0.24, 1),
            bold=True
        )
        btn_refresh.bind(on_release=lambda x: self.refresh_letters_penalty())

        actions_bar.add_widget(btn_clear)
        actions_bar.add_widget(btn_refresh)
        main_layout.add_widget(actions_bar)

        self.add_widget(main_layout)

    def on_tile_click(self, idx):
        """Нажатие на плашку с буквой подставляет её в поле ввода."""
        if idx < len(self.player_letters):
            letter = self.player_letters[idx]
            self.txt_word.text += letter.upper()

    def update_tiles_display(self):
        """Обновляет внешний вид 7 плашек на экране."""
        for i in range(7):
            if i < len(self.player_letters):
                let = self.player_letters[i]
                sc = self.scores.get(let, 0)
                self.tile_buttons[i].set_tile(let, sc)
            else:
                self.tile_buttons[i].set_tile("", 0)

    def submit_word(self):
        """Проверяет и принимает составленное слово."""
        word = self.txt_word.text.lower().strip().replace('ё', 'е')
        self.txt_word.text = ""

        if not word:
            return

        # 1. Проверка наличия букв в руке
        letters_copy = self.player_letters.copy()
        can_build = True

        for char in word:
            if char in letters_copy:
                letters_copy.remove(char)
            else:
                can_build = False
                break

        if not can_build:
            self.show_popup("Ошибка", "Вы использовали буквы, которых нет у вас на плашках!")
            return

        # 2. Проверка наличия слова в словаре
        if word not in self.dictionary:
            self.show_popup("Увы", f"Слова '{word.upper()}' нет в словаре игры!")
            return

        # Валидация прошла: начисление очков
        word_score = sum(self.scores.get(char, 0) for char in word)
        self.total_score += word_score

        # Удаление использованных букв из руки
        for char in word:
            self.player_letters.remove(char)

        self.lbl_score.text = f"Счет: {self.total_score}"
        self.draw_new_letters()
        self.update_tiles_display()

        self.show_popup("Отлично!", f"Слово '{word.upper()}' принято!\n+{word_score} очков.")

    def refresh_letters_penalty(self):
        """Сброс руки с вычетом 5 очков."""
        self.player_letters.clear()
        self.total_score = max(0, self.total_score - 5)
        self.lbl_score.text = f"Счет: {self.total_score}"
        self.draw_new_letters()
        self.update_tiles_display()
        self.show_popup("Обновление", "Вы сменили буквы.\nВыдано 7 новых плашек (-5 очков).")

    def restart_game(self):
        """Перезапуск игры."""
        self.reset_game_state()
        self.lbl_score.text = f"Счет: {self.total_score}"
        self.update_tiles_display()
        self.txt_word.text = ""

    def show_popup(self, title, text):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=text, halign='center', font_size='15sp'))
        btn_close = Button(text="OK", size_hint_y=0.4, background_color=(0.10, 0.73, 0.61, 1))
        box.add_widget(btn_close)

        popup = Popup(title=title, content=box, size_hint=(0.85, 0.35), auto_dismiss=False)
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        if self.manager:
            self.manager.current = 'menu'


if __name__ == "__main__":
    from kivy.app import App
    from kivy.core.window import Window

    Window.size = (360, 640)

    class TestApp(App):
        def build(self):
            return ScrabbleScreen()

    TestApp().run()
