from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import ctypes

class TelaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._focus_scheduled = False
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        Window.size = (400, 700)
        print("📍 Login: Configurando tamanho da janela")
        self.posicionar_janela_login()
    
    def on_enter(self):
        """Chamado quando a tela é carregada - COM FOCO GARANTIDO"""
        print("🔑 Tela de login carregada - configurando foco...")
        
        # Resetar flag de foco
        self._focus_scheduled = False
        
        # Garantir que o foco seja aplicado após a tela estar completamente carregada
        Clock.schedule_once(self.set_focus_username, 0.3)
    
    def set_focus_username(self, dt):
        """Define o foco no campo username com garantia"""
        if not self._focus_scheduled and hasattr(self, 'ids') and 'usuario' in self.ids:
            self.ids.usuario.focus = True
            print("✅ Cursor DEFINIDO no campo Username")
            self._focus_scheduled = True
            
            # Forçar o foco novamente após um pequeno delay
            Clock.schedule_once(self.force_focus_username, 0.1)
        else:
            print("❌ Campo 'usuario' não encontrado nos IDs")
    
    def force_focus_username(self, dt):
        """Força o foco no username novamente para garantir"""
        if hasattr(self, 'ids') and 'usuario' in self.ids:
            self.ids.usuario.focus = True
            print("🔧 Foco FORÇADO no campo Username")
    
    def posicionar_janela_login(self):
        """Centraliza a janela do login na tela"""
        try:
            user32 = ctypes.windll.user32
            
            # Obter tamanho da tela
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # Tamanho da janela
            window_width, window_height = Window.size
            
            # Centralizar
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Garantir posições mínimas
            x = max(x, 50)
            y = max(y, 50)
            
            Window.top = y
            Window.left = x
            
            print(f"📍 Login: Janela posicionada em ({x}, {y})")
            
        except Exception as e:
            print(f"⚠️ Não foi possível posicionar login: {e}")
            # Fallback
            Window.top = 100
            Window.left = 200
            print("📍 Login: Posição fallback definida")
    
    def mostrar_erro_login(self, mensagem):
        """Mostra um popup de erro para login falho"""
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensagem de erro
        lbl_erro = Label(
            text=mensagem,
            color=(1, 1, 1, 1),
            font_size='14sp',
            text_size=(300, None),
            halign='center'
        )
        
        # Botão OK
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title='❌ Erro no Login',
            title_color=(1, 0.3, 0.3, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(350, 200),
            background_color=(0.12, 0.16, 0.23, 1),
            separator_color=(0.55, 0.36, 0.96, 1)
        )
        
        # Fechar popup ao clicar OK
        btn_ok.bind(on_press=popup.dismiss)
        
        # Mostrar popup
        popup.open()
    
    def fazer_login(self):
        """Função de login principal"""
        print("🎯 Tentando fazer login...")
        
        # Verificar se IDs estão disponíveis
        if not hasattr(self, 'ids'):
            print("❌ IDs não disponíveis")
            self.mostrar_erro_login("Erro interno do sistema")
            return
        
        # Obter credenciais
        usuario = self.ids.usuario.text.strip()
        senha = self.ids.senha.text.strip()
        
        print(f"👤 Usuário digitado: {usuario}")
        print(f"🔐 Senha digitada: {senha}")
        
        # Validar campos vazios
        if not usuario or not senha:
            print("❌ Erro: Usuário ou senha vazios")
            self.mostrar_erro_login("Preencha usuário e senha!")
            
            # Focar no campo vazio
            if not usuario:
                self.ids.usuario.focus = True
            else:
                self.ids.senha.focus = True
            return
        
        # Tentar login no sistema
        app = App.get_running_app()
        sistema = app.sistema
        
        if sistema.fazer_login(usuario, senha):
            print(f"✅ Login bem-sucedido! Usuário: {usuario}")
            
            # Inicializar pares padrão para novos clientes
            # Verificar se é cliente
            if hasattr(sistema, 'tipo_usuario_logado') and sistema.tipo_usuario_logado == 'cliente':
                # Redirecionar para dashboard cliente
                self.manager.current = 'dashboard'
            else:
                # Redirecionar para dashboard admin
                self.manager.current = 'dashboard'
                sistema.inicializar_pares_cliente(usuario)
            
            # Limpar campos antes de sair
            self.ids.usuario.text = ""
            self.ids.senha.text = ""
            
        else:
            print("❌ Login falhou - usuário ou senha incorretos")
            self.mostrar_erro_login("Usuário ou senha incorretos!\nVerifique suas credenciais.")
            
            # Focar no campo usuário novamente
            self.ids.usuario.focus = True
    
    def abrir_cadastro(self):
        """Abre a tela de cadastro de nova conta"""
        print("🎯🎯🎯 BOTÃO CLICADO - Criar Nova Conta! 🎯🎯🎯")
        
        # Limpar campos antes de sair
        if hasattr(self, 'ids'):
            self.ids.usuario.text = ""
            self.ids.senha.text = ""
        
        self.manager.current = 'cadastro_conta'
    
    def abrir_recuperacao(self):
        """Abre a tela de recuperação de senha"""
        print("🔐 Botão recuperação clicado")
        # TODO: Implementar tela de recuperação
        self.mostrar_erro_login("Funcionalidade em desenvolvimento")
    
    def on_kv_post(self, base_widget):
        """Chamado após o KV ser carregado - para debug"""
        super().on_kv_post(base_widget)
        print("✅ TelaLogin KV carregado")
        if hasattr(self, 'ids'):
            print(f"🔍 IDs disponíveis na tela login: {list(self.ids.keys())}")
    
    def focus_next_field(self):
        """Muda o foco para o campo senha (para ser usado com Enter)"""
        if hasattr(self, 'ids') and 'senha' in self.ids:
            self.ids.senha.focus = True
            print("🔍 Enter pressionado: Indo para campo Senha")
    
    def fazer_login_por_enter(self):
        """Permite fazer login pressionando Enter no campo senha"""
        self.fazer_login()
    
    def on_leave(self):
        """Chamado quando sai da tela"""
        print("🚪 Saindo da tela de login...")
        
        # Cancelar qualquer schedule pendente
        Clock.unschedule(self.set_focus_username)
        Clock.unschedule(self.force_focus_username)
        
        # Limpar campos (opcional)
        if hasattr(self, 'ids'):
            self.ids.senha.text = ""  # Limpa apenas a senha por segurança