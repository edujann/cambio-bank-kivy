"""
Tela de Login do Cambio Bank
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class LoginScreen(Screen):
    """
    Tela de login do sistema
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
    
    def create_ui(self):
        """Cria a interface do usuário"""
        layout = BoxLayout(
            orientation='vertical',
            padding=50,
            spacing=20
        )
        
        # Título
        titulo = Label(
            text='💰 CÂMBIO BANK',
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=60
        )
        layout.add_widget(titulo)
        
        # Subtítulo
        subtitulo = Label(
            text='Sistema Premium de Câmbio',
            font_size='16sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(subtitulo)
        
        # Campo de usuário
        self.username_input = TextInput(
            hint_text='Usuário',
            size_hint_y=None,
            height=50,
            multiline=False
        )
        layout.add_widget(self.username_input)
        
        # Campo de senha
        self.password_input = TextInput(
            hint_text='Senha',
            password=True,
            size_hint_y=None,
            height=50,
            multiline=False
        )
        layout.add_widget(self.password_input)
        
        # Botão de login
        login_btn = Button(
            text='ENTRAR',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        login_btn.bind(on_press=self.fazer_login)
        layout.add_widget(login_btn)
        
        # Mensagem de status
        self.status_label = Label(
            text='Digite usuário e senha para entrar',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def fazer_login(self, instance):
        """Processa o login do usuário"""
        username = self.username_input.text
        password = self.password_input.text
        
        if username and password:
            self.status_label.text = f'Bem-vindo, {username}!'
            self.status_label.color = (0, 0.7, 0, 1)  # Verde
        else:
            self.status_label.text = 'Preencha usuário e senha!'
            self.status_label.color = (0.8, 0, 0, 1)  # Vermelho