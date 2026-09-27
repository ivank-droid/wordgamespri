import sys
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

# Настройка размера окна под мобильный экран при тестировании на ПК
Window.size = (360, 640)

# Импорт экранов игр
try:
    from scrabble import ScrabbleScreen
except ImportError:
    ScrabbleScreen = None

try:
    from cities import CitiesScreen
except ImportError:
    CitiesScreen = None

try:
    from hangman import HangmanScreen
except ImportError:
    HangmanScreen = None

try:
    from balda import BaldaScreen
except ImportError:
    BaldaScreen = None


class MenuScreen(Screen):
    """Главное меню Игрового Центра."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(
            orientation='vertical',
            padding=[25, 35, 25, 35],
            spacing=15
        )

        # Заголовок
        lbl_title = Label(
            text="[b]Игровой Центр[/b]",
            markup=True,
            font_size='26sp',
            size_hint_y=0.15,
            color=(0.10, 0.73, 0.61, 1)
        )
        main_layout.add_widget(lbl_title)

        lbl_subtitle = Label(
            text="Выберите игру:",
            font_size='16sp',
            size_hint_y=0.08,
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(lbl_subtitle)

        # Конфигурация меню игр
        games_config = [
            {"name": "1. Эрудит (Scrabble)", "screen_name": "scrabble"},
            {"name": "2. Игра в города", "screen_name": "cities"},
            {"name": "3. Виселица", "screen_name": "hangman"},
            {"name": "4. Балда", "screen_name": "balda"},
        ]

        # Создание кнопок для перехода в игры
        for game in games_config:
            btn = Button(
                text=game["name"],
                font_size='17sp',
                bold=True,
                size_hint_y=0.12,
                background_normal='',
                background_color=(0.20, 0.28, 0.36, 1),
                color=(0.10, 0.73, 0.61, 1)
            )
            btn.bind(on_release=lambda instance, name=game["screen_name"]: self.open_game(name))
            main_layout.add_widget(btn)

        # Кнопка полного выхода
        btn_exit = Button(
            text="Выход",
            font_size='16sp',
            bold=True,
            size_hint_y=0.10,
            background_normal='',
            background_color=(0.91, 0.30, 0.24, 1)
        )
        btn_exit.bind(on_release=self.exit_app)
        main_layout.add_widget(btn_exit)

        self.add_widget(main_layout)

    def open_game(self, screen_name):
        if self.manager and self.manager.has_screen(screen_name):
            self.manager.current = screen_name
        else:
            print(f"[Предупреждение] Экран '{screen_name}' не найден в менеджере!")

    def exit_app(self, instance):
        """Мгновенное закрытие окна приложения и завершение процесса."""
        Window.close()
        App.get_running_app().stop()
        sys.exit(0)


class GameCenterApp(App):
    def build(self):
        self.title = "Игровой Центр"
        
        # Менеджер экранов с анимацией затухания
        sm = ScreenManager(transition=FadeTransition(duration=0.12))

        # Добавляем главное меню
        sm.add_widget(MenuScreen(name='menu'))

        # Добавляем экраны игр при их наличии
        if ScrabbleScreen:
            sm.add_widget(ScrabbleScreen(name='scrabble'))
        if CitiesScreen:
            sm.add_widget(CitiesScreen(name='cities'))
        if HangmanScreen:
            sm.add_widget(HangmanScreen(name='hangman'))
        if BaldaScreen:
            sm.add_widget(BaldaScreen(name='balda'))

        return sm


if __name__ == "__main__":
    GameCenterApp().run()
