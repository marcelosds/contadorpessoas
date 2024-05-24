from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

screen = ScreenManager()


class LoginScreen(Screen):
    pass

    def login(self):
        from funcoes import login
        login(self)

    def cria_usuario(self):
        from funcoes import cria_usuario
        cria_usuario(self)

    def send_password_reset_email(self):
        from funcoes import send_password_reset_email
        send_password_reset_email(self)


class ConsultScreen(Screen):
    pass

    def analisar(self):
        from funcoes import analisar
        analisar(self)


screen.add_widget(LoginScreen(name='login'))
screen.add_widget(ConsultScreen(name='consulta'))


class LiveApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # auto reload path
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]

    def build(self):
        self.theme_cls.primary_palette = "Green"
        return Builder.load_file("telas.kv")


# finally, run the app
if __name__ == "__main__":
    LiveApp().run()
