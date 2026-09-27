import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


class BaldaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.DICT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words_dictionary.txt")
        self.grid_size = 5
        self.load_dictionary()

        # Инициализация логики и интерфейса
        self.reset_game_state()
        self.build_ui()

    def load_dictionary(self):
        """Загружает словарь из файла words_dictionary.txt."""
        self.dictionary = set()
        if os.path.exists(self.DICT_FILE):
            try:
                with open(self.DICT_FILE, "r", encoding="utf-8") as f:
                    self.dictionary = {line.strip().lower().replace('ё', 'е') for line in f if line.strip()}
            except Exception as e:
                print(f"[Warning] Ошибка загрузки словаря: {e}")
        
        if not self.dictionary:
            self.dictionary = {"балда", "питон", "понт", "нить", "тон", "нота", "итог", "тропа", "напиток"}

    def reset_game_state(self):
        """Сбрасывает состояние игры."""
        self.scores = {1: 0, 2: 0}
        self.current_player = 1
        self.used_words = {"балда"}

        self.letter_placed_this_turn = False
        self.new_letter_coords = None
        self.selected_path = []

        self.board_letters = [[" " for _ in range(5)] for _ in range(5)]
        start_word = "балда"
        for col, letter in enumerate(start_word):
            self.board_letters[2][col] = letter

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # 1. Верхняя панель: Кнопка «<< Меню», Кнопка «Новая игра» и Счет
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

        self.lbl_scores = Label(
            text=f"И1: {self.scores[1]} | И2: {self.scores[2]}",
            size_hint_x=0.40,
            bold=True,
            font_size='14sp'
        )

        top_bar.add_widget(btn_back)
        top_bar.add_widget(btn_restart)
        top_bar.add_widget(self.lbl_scores)
        main_layout.add_widget(top_bar)

        # 2. Информационная плашка
        self.status_label = Label(
            text=f"Ход Игрока {self.current_player}. Шаг 1: Поставьте букву.",
            font_size='15sp',
            bold=True,
            size_hint_y=0.06,
            color=(0.95, 0.77, 0.06, 1)
        )
        main_layout.add_widget(self.status_label)

        # 3. Игровое поле 5x5
        self.grid = GridLayout(cols=5, rows=5, spacing=4, size_hint_y=0.58)
        self.board_buttons = [[None for _ in range(5)] for _ in range(5)]

        for r in range(5):
            for c in range(5):
                text = self.board_letters[r][c].upper()
                btn = Button(
                    text=text,
                    font_size='22sp',
                    bold=True,
                    background_normal='',
                    background_color=(0.92, 0.94, 0.94, 1) if text != " " else (0.58, 0.64, 0.65, 1),
                    color=(0.17, 0.24, 0.31, 1)
                )
                btn.bind(on_release=lambda instance, row=r, col=c: self.handle_cell_click(row, col))
                self.board_buttons[r][c] = btn
                self.grid.add_widget(btn)

        main_layout.add_widget(self.grid)

        # 4. Отображение слова
        self.lbl_current_word = Label(
            text="Слово: ",
            font_size='18sp',
            bold=True,
            size_hint_y=0.08
        )
        main_layout.add_widget(self.lbl_current_word)

        # 5. Кнопки управления
        control_frame = BoxLayout(size_hint_y=0.10, spacing=8)
        
        btn_reset_selection = Button(
            text="Сбросить выделение",
            background_normal='',
            background_color=(0.90, 0.49, 0.13, 1),
            bold=True
        )
        btn_reset_selection.bind(on_release=lambda x: self.reset_word_selection())

        btn_confirm = Button(
            text="Готово",
            background_normal='',
            background_color=(0.18, 0.80, 0.44, 1),
            bold=True
        )
        btn_confirm.bind(on_release=lambda x: self.confirm_word())

        control_frame.add_widget(btn_reset_selection)
        control_frame.add_widget(btn_confirm)
        main_layout.add_widget(control_frame)

        self.add_widget(main_layout)

    def update_ui_labels(self):
        self.lbl_scores.text = f"И1: {self.scores[1]} | И2: {self.scores[2]}"
        self.status_label.text = f"Ход Игрока {self.current_player}. Шаг 1: Поставьте букву."

    def handle_cell_click(self, r, c):
        if not self.letter_placed_this_turn:
            if self.board_letters[r][c] != " ":
                self.show_popup("Внимание", "Эта ячейка уже занята!")
                return

            has_neighbor = False
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 5 and 0 <= nc < 5 and self.board_letters[nr][nc] != " ":
                    has_neighbor = True
                    break

            if not has_neighbor:
                self.show_popup("Внимание", "Букву можно ставить только рядом с уже существующими!")
                return

            self.prompt_letter_input(r, c)

        else:
            if self.board_letters[r][c] == " ":
                return

            if (r, c) in self.selected_path:
                return

            if self.selected_path:
                last_r, last_c = self.selected_path[-1]
                if abs(last_r - r) + abs(last_c - c) != 1:
                    self.show_popup("Внимание", "Выбирать можно только соседние по вертикали или горизонтали буквы!")
                    return

            self.selected_path.append((r, c))
            self.board_buttons[r][c].background_color = (0.18, 0.80, 0.44, 1)
            self.board_buttons[r][c].color = (1, 1, 1, 1)
            self.update_current_word_label()

    def prompt_letter_input(self, r, c):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        txt = TextInput(font_size='24sp', multiline=False, size_hint_y=0.5, halign='center')
        btn = Button(text="Поставить", size_hint_y=0.5, background_color=(0.18, 0.80, 0.44, 1))

        box.add_widget(txt)
        box.add_widget(btn)

        popup = Popup(title="Введите одну букву", content=box, size_hint=(0.7, 0.3), auto_dismiss=False)

        def apply_letter(instance):
            val = txt.text.strip().lower().replace('ё', 'е')
            if len(val) == 1 and 'а' <= val <= 'я':
                self.board_letters[r][c] = val
                self.new_letter_coords = (r, c)
                self.board_buttons[r][c].text = val.upper()
                self.board_buttons[r][c].background_color = (0.95, 0.77, 0.06, 1)
                self.letter_placed_this_turn = True
                self.status_label.text = f"Ход Игрока {self.current_player}. Шаг 2: Выделите слово кликами."
                popup.dismiss()
            else:
                self.show_popup("Ошибка", "Введите ровно одну русскую букву!")

        btn.bind(on_release=apply_letter)
        popup.open()

    def update_current_word_label(self):
        word = "".join([self.board_letters[r][c] for r, c in self.selected_path])
        self.lbl_current_word.text = f"Слово: {word.upper()}"

    def reset_word_selection(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.board_letters[r][c] != " ":
                    if (r, c) == self.new_letter_coords:
                        self.board_buttons[r][c].background_color = (0.95, 0.77, 0.06, 1)
                        self.board_buttons[r][c].color = (0.17, 0.24, 0.31, 1)
                    else:
                        self.board_buttons[r][c].background_color = (0.92, 0.94, 0.94, 1)
                        self.board_buttons[r][c].color = (0.17, 0.24, 0.31, 1)
        self.selected_path.clear()
        self.update_current_word_label()

    def confirm_word(self):
        if not self.letter_placed_this_turn or not self.selected_path:
            self.show_popup("Внимание", "Вы не поставили букву или не выделили слово!")
            return

        word = "".join([self.board_letters[r][c] for r, c in self.selected_path]).lower().replace('ё', 'е')

        if self.new_letter_coords not in self.selected_path:
            self.show_popup("Ошибка", "Составленное слово должно обязательно содержать новую букву!")
            return

        if word in self.used_words:
            self.show_popup("Ошибка", f"Слово '{word.upper()}' уже использовалось в этой игре!")
            return

        if word not in self.dictionary:
            self.show_popup("Ошибка", f"Слова '{word.upper()}' нет в словаре!")
            return

        word_len = len(word)
        self.scores[self.current_player] += word_len
        self.used_words.add(word)

        self.show_popup("Успех!", f"Игрок {self.current_player} составил слово '{word.upper()}' (+{word_len} очков)!")

        self.letter_placed_this_turn = False
        self.new_letter_coords = None
        self.reset_word_selection()

        empty_cells = any(self.board_letters[r][c] == " " for r in range(5) for c in range(5))
        if not empty_cells:
            self.end_game()
            return

        self.current_player = 2 if self.current_player == 1 else 1
        self.update_ui_labels()

    def restart_game(self):
        """Полный сброс и перезапуск игры."""
        self.reset_game_state()
        self.build_ui()

    def end_game(self):
        p1 = self.scores[1]
        p2 = self.scores[2]

        if p1 > p2:
            result = f"Победил Игрок 1 со счетом {p1}:{p2}!"
        elif p2 > p1:
            result = f"Победил Игрок 2 со счетом {p2}:{p1}!"
        else:
            result = f"Ничья со счетом {p1}:{p2}!"

        self.show_popup("Игра окончена!", f"На поле не осталось пустых мест!\n\n{result}")
        self.status_label.text = "Игра завершена."

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
            return BaldaScreen()

    TestApp().run()
