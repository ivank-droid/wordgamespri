import os
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock

class CitiesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Загрузка базы городов
        self.cities_pool = self.load_cities(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cities_db.txt"))
        self.used_cities = set()
        self.last_letter = ""
        self.player_turn = True

        # Главный контейнер
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # 1. Верхняя панель навигации
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
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
        btn_restart.bind(on_release=lambda x: self.restart_game())

        top_bar.add_widget(btn_back)
        top_bar.add_widget(Widget())
        top_bar.add_widget(btn_restart)
        main_layout.add_widget(top_bar)

        # 2. Информационная плашка (чей ход / какая буква)
        self.lbl_status = Label(
            text="Ваш ход! Начните с любого города.",
            font_size='16sp',
            bold=True,
            size_hint_y=0.08,
            color=(0.10, 0.73, 0.61, 1),
            halign='center'
        )
        main_layout.add_widget(self.lbl_status)

        # 3. Область истории сообщений (Чат/Scroll)
        self.scroll = ScrollView(size_hint_y=0.68)
        self.history_layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.scroll.add_widget(self.history_layout)
        main_layout.add_widget(self.scroll)

        # 4. Панель ввода (Поле + Кнопка Отправить)
        input_bar = BoxLayout(size_hint_y=0.10, spacing=5)
        self.txt_input = TextInput(
            hint_text="Введите город...",
            multiline=False,
            font_size='16sp',
            size_hint_x=0.7,
            padding=[10, 10, 10, 10]
        )
        self.txt_input.bind(on_text_validate=lambda x: self.handle_player_turn())

        btn_send = Button(
            text="Отправить",
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.10, 0.73, 0.61, 1),
            bold=True
        )
        btn_send.bind(on_release=lambda x: self.handle_player_turn())

        input_bar.add_widget(self.txt_input)
        input_bar.add_widget(btn_send)
        main_layout.add_widget(input_bar)

        self.add_widget(main_layout)
        self.system_message("Игра началась! Введите название любого города.")

    def load_cities(self, filename):
        """Загрузка городов из файла."""
        cities = set()
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        city = line.strip().lower().replace('ё', 'е')
                        if city:
                            cities.add(city)
                return cities
            except Exception as e:
                print(f"[Warning] Ошибка чтения базы городов: {e}")

        # Резервный набор, если файл отсутствует
        return {"москва", "анапа", "архангельск", "воронеж", "иркутск", "казань", "новгород"}

    def append_to_history(self, sender, text, color):
        """Добавляет новое сообщение в историю."""
        lbl = Label(
            text=f"[b]{sender}:[/b] {text}",
            markup=True,
            font_size='15sp',
            size_hint_y=None,
            height=32,
            color=color,
            halign='left',
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.history_layout.add_widget(lbl)
        # Автопрокрутка вниз
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0))

    def system_message(self, text):
        """Системное сообщение сервиса."""
        lbl = Label(
            text=f"[i]{text}[/i]",
            markup=True,
            font_size='13sp',
            size_hint_y=None,
            height=28,
            color=(0.7, 0.7, 0.7, 1),
            halign='center',
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.history_layout.add_widget(lbl)

    def get_valid_letter(self, city):
        """Определяет правильную последнюю букву с учетом правил русского языка."""
        last_char = city[-1]
        if last_char in ["ь", "ы", "ъ"] and len(city) > 1:
            last_char = city[-2]
        return last_char

    def handle_player_turn(self):
        """Логика хода игрока."""
        if not self.player_turn:
            return

        city = self.txt_input.text.lower().strip().replace('ё', 'е')
        self.txt_input.text = ""

        if not city:
            return

        # Валидация хода
        if city not in self.cities_pool:
            self.show_popup("Внимание", "Я не знаю такого города (или его нет в нашей базе)!")
            return
        if city in self.used_cities:
            self.show_popup("Внимание", f"Город '{city.title()}' уже использовался в этой игре!")
            return
        if self.last_letter and city[0] != self.last_letter:
            self.show_popup("Внимание", f"Город должен начинаться на букву '{self.last_letter.upper()}'!")
            return

        # Принимаем ход игрока
        self.used_cities.add(city)
        self.append_to_history("Вы", city.title(), (0.92, 0.94, 0.94, 1))

        self.last_letter = self.get_valid_letter(city)
        self.player_turn = False
        self.lbl_status.text = f"Компьютер думает над буквой '{self.last_letter.upper()}'..."

        # Реалистичная задержка для ответа бота
        Clock.schedule_once(lambda dt: self.handle_computer_turn(), 0.8)

    def handle_computer_turn(self):
        """Логика хода компьютера."""
        options = [c for c in self.cities_pool if c.startswith(self.last_letter) and c not in self.used_cities]

        if not options:
            self.append_to_history("Бот", "У меня закончились города... Вы победили!", (0.10, 0.73, 0.61, 1))
            self.show_popup("Победа!", "Поздравляем! Компьютер признал поражение.")
            self.lbl_status.text = "Игра завершена."
            return

        bot_city = random.choice(options)
        self.used_cities.add(bot_city)
        self.append_to_history("Бот", bot_city.title(), (0.10, 0.73, 0.61, 1))

        self.last_letter = self.get_valid_letter(bot_city)
        self.player_turn = True
        self.lbl_status.text = f"Ваш ход! Назовите город на букву: '{self.last_letter.upper()}'"

    def restart_game(self):
        """Перезапуск сессии."""
        self.used_cities.clear()
        self.last_letter = ""
        self.player_turn = True
        self.history_layout.clear_widgets()
        self.txt_input.text = ""
        self.lbl_status.text = "Ваш ход! Начните с любого города."
        self.system_message("Игра перезапущена. Напишите любой город.")

    def show_popup(self, title, text):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=text, halign='center', font_size='15sp'))
        btn_close = Button(text="OK", size_hint_y=0.4, background_color=(0.10, 0.73, 0.61, 1))
        box.add_widget(btn_close)

        popup = Popup(title=title, content=box, size_hint=(0.8, 0.35), auto_dismiss=False)
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        """Возврат в Главное меню."""
        if self.manager:
            self.manager.current = 'menu'

# Блок для отдельного автономного тестирования файла
if __name__ == "__main__":
    from kivy.app import App
    from kivy.core.window import Window

    Window.size = (360, 640)

    class TestApp(App):
        def build(self):
            return CitiesScreen()

    TestApp().run()
