# screens/verificacao_email.py
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App

class TelaVerificacaoEmail(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email_pendente = ""
        self.email_alvo = ""  # 🔥 ADICIONAR ESTE ATRIBUTO
        self.codigo_esperado = ""  # 🔥 ADICIONAR ESTE ATRIBUTO
        self.tempo_restante = 900  # 15 minutos
        self._timer_event = None
    
    def on_pre_enter(self):
        """Prepara a tela antes de entrar"""
        from kivy.core.window import Window
        Window.size = (400, 700)
        self.iniciar_timer()
    
    def configurar_dados(self, email, codigo_simulacao):
        """Configura o email e código para verificação"""
        self.email_pendente = email
        self.email_alvo = email  # 🔥 ATRIBUIR O EMAIL AQUI TAMBÉM
        self.codigo_esperado = str(codigo_simulacao) if codigo_simulacao else ""  # 🔥 ATRIBUIR CÓDIGO
        
        print(f"⚙️ Configurando dados:")
        print(f"   Email pendente: {self.email_pendente}")
        print(f"   Email alvo: {self.email_alvo}")
        print(f"   Código esperado: {self.codigo_esperado}")
        
        # Mostrar email mascarado por segurança
        if '@' in email:
            usuario, dominio = email.split('@')
            if len(usuario) > 2:
                email_mascarado = usuario[:2] + '***' + '@' + dominio
                self.ids.email_label.text = f"Enviamos um código para:\n{email_mascarado}"
            else:
                self.ids.email_label.text = f"Enviamos um código para:\n{email}"
        else:
            self.ids.email_label.text = f"Enviamos um código para:\n{email}"
        
        # 🔥 MODO SIMULAÇÃO: Mostrar código diretamente
        if codigo_simulacao:
            self.ids.codigo_simulacao.text = f"CÓDIGO DE VERIFICAÇÃO: {codigo_simulacao}"
            self.ids.codigo_simulacao.opacity = 1  # Tornar visível
    
    def iniciar_timer(self):
        """Inicia o timer de expiração"""
        self.tempo_restante = 900
        if self._timer_event:
            self._timer_event.cancel()
        self._timer_event = Clock.schedule_interval(self.atualizar_timer, 1)
        self.atualizar_display_timer()
    
    def atualizar_timer(self, dt):
        """Atualiza o timer a cada segundo"""
        self.tempo_restante -= 1
        self.atualizar_display_timer()
        
        if self.tempo_restante <= 0:
            if self._timer_event:
                self._timer_event.cancel()
            self.mostrar_erro("Tempo esgotado! Solicite um novo código.")
    
    def atualizar_display_timer(self):
        """Atualiza o display do timer"""
        minutos = self.tempo_restante // 60
        segundos = self.tempo_restante % 60
        self.ids.timer_label.text = f"Tempo restante: {minutos:02d}:{segundos:02d}"
    
    def verificar_codigo(self):
        """Verifica o código digitado"""
        if not hasattr(self, 'ids') or 'codigo_input' not in self.ids:
            print("❌ Interface não carregada")
            return
        
        codigo_digitado = self.ids.codigo_input.text.strip()
        
        # 🔥 CORREÇÃO: Usar self.email_alvo ou self.email_pendente
        email_para_verificar = self.email_alvo or self.email_pendente
        
        if not email_para_verificar:
            print("❌ Nenhum email configurado para verificação")
            self.mostrar_mensagem("Erro: Email não configurado")
            return
        
        sistema = App.get_running_app().sistema
        
        print(f"🔍 Verificando código:")
        print(f"   Email: {email_para_verificar}")
        print(f"   Código digitado: {codigo_digitado}")
        print(f"   Código esperado (simulação): {self.codigo_esperado}")
        
        if not codigo_digitado:
            self.mostrar_mensagem("Digite o código de verificação")
            return
        
        if len(codigo_digitado) != 6:
            self.mostrar_mensagem("Código deve ter 6 dígitos")
            return
        
        try:
            # 🔥 Método deve retornar (sucesso, mensagem)
            sucesso, mensagem = sistema.verificar_codigo_email(email_para_verificar, codigo_digitado)
            
            if sucesso:
                print(f"✅ Verificação bem-sucedida: {mensagem}")
                self.mostrar_mensagem(mensagem, sucesso=True)
                
                # Navegar para login após 2 segundos
                Clock.schedule_once(lambda dt: self.ir_para_login(), 2)
            else:
                print(f"❌ Verificação falhou: {mensagem}")
                self.mostrar_mensagem(mensagem, sucesso=False)
                
        except ValueError as e:
            print(f"❌ Erro no retorno do método: {e}")
            print("🔄 Tentando verificação local (fallback)...")
            
            # Fallback: verificar localmente se tiver código esperado
            if self.codigo_esperado and codigo_digitado == self.codigo_esperado:
                print("✅ Código correto (verificação local)")
                self.mostrar_mensagem("Email verificado localmente!", sucesso=True)
                Clock.schedule_once(lambda dt: self.ir_para_login(), 2)
            else:
                print("❌ Código incorreto (verificação local)")
                self.mostrar_mensagem("Código incorreto", sucesso=False)
    
    def mostrar_mensagem(self, mensagem, sucesso=False):
        """Mostra mensagem na tela"""
        if sucesso:
            self.ids.mensagem_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.ids.mensagem_label.color = (1, 0.3, 0.3, 1)
        
        self.ids.mensagem_label.text = mensagem

    def reenviar_codigo(self):
        """Reenvia o código de verificação"""
        sistema = App.get_running_app().sistema
        sucesso, mensagem = sistema.reenviar_codigo_verificacao(self.email_pendente)
        
        if sucesso:
            # Obter novo código para mostrar em simulação
            novo_codigo = sistema.codigos_verificacao[self.email_pendente]['codigo']
            self.ids.codigo_simulacao.text = f"CÓDIGO DE VERIFICAÇÃO: {novo_codigo}"
            
            self.mostrar_sucesso("Novo código enviado!")
            self.reiniciar_timer()
        else:
            self.mostrar_erro(mensagem)
    
    def reiniciar_timer(self):
        """Reinicia o timer"""
        self.iniciar_timer()
    
    def ir_para_login(self):
        """Vai para tela de login após verificação bem-sucedida"""
        self.manager.current = 'login'
    
    def voltar_para_cadastro(self):
        """Volta para tela de cadastro"""
        self.manager.current = 'cadastro_conta'
    
    def mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        self.ids.mensagem_label.color = (1, 0.3, 0.3, 1)
        self.ids.mensagem_label.text = mensagem
    
    def mostrar_sucesso(self, mensagem):
        """Mostra mensagem de sucesso"""
        self.ids.mensagem_label.color = (0.2, 0.8, 0.2, 1)
        self.ids.mensagem_label.text = mensagem
    
    def on_leave(self):
        """Limpa recursos ao sair da tela"""
        if self._timer_event:
            self._timer_event.cancel()