from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
import datetime
import random

class TelaSuporte(Screen):
    """Tela de suporte ao cliente"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (700, 1000)
        self.carregar_dados_usuario()
    
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("📞 Tela de Suporte carregada")
    
    def carregar_dados_usuario(self):
        """Carrega os dados do usuário logado"""
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados completos do usuário
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        
        if sistema.usuario_logado and hasattr(self, 'ids'):
            # Configurar informações do usuário
            info_texto = f"👤 Usuário: {sistema.usuario_logado} | 📋 Nome: {usuario_data.get('nome', sistema.usuario_logado)}"
            
            # 🔥 CORREÇÃO: Usar usuario_data e tipo_usuario_logado
            if sistema.tipo_usuario_logado == 'cliente' and usuario_data.get('contas'):
                contas = ', '.join(usuario_data.get('contas', []))
                info_texto += f" | 🏦 Contas: {contas}"
            
            self.ids.lbl_info_usuario.text = info_texto
    
    def enviar_solicitacao(self):
        """Envia solicitação de suporte"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        assunto = self.ids.combo_assunto.text
        descricao = self.ids.text_descricao.text.strip()
        
        if not assunto or not descricao:
            self.mostrar_erro("Preencha todos os campos obrigatórios!")
            return
        
        # Simular envio (em produção, integrar com sistema de tickets)
        ticket_id = f"TK{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Obter email do usuário
        email_usuario = sistema.usuarios.get(sistema.usuario_logado['username'], {}).get('email', '')
        
        self.mostrar_sucesso(
            f"✅ SOLICITAÇÃO REGISTRADA!\n\n"
            f"📋 Ticket: {ticket_id}\n"
            f"📞 Assunto: {assunto}\n"
            f"⏰ Previsão: 24h para resposta\n\n"
            f"Acompanhe pelo email: {email_usuario}"
        )
        
        # Limpar campos
        self.ids.combo_assunto.text = ""
        self.ids.text_descricao.text = ""
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='❌ Erro',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='✅ Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()