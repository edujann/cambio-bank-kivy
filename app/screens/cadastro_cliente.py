from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import ctypes


class TelaCadastroCliente(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        # 🔥 Tamanho do CADASTRO: 500x1000
        Window.size = (500, 1000)
        self.posicionar_janela()
        print(f"🎯 Cadastro: Tamanho forçado para {Window.size}")

    def on_enter(self):
        """Chamado quando a tela é carregada"""
        self.limpar_formulario()
        
        # 🔥 CONFIGURAR ORDEM DE NAVEGAÇÃO COM TAB
        self.ids.username.focus_next = self.ids.senha
        self.ids.senha.focus_next = self.ids.confirmar_senha
        self.ids.confirmar_senha.focus_next = self.ids.nome
        self.ids.nome.focus_next = self.ids.email
        self.ids.email.focus_next = self.ids.documento
        self.ids.documento.focus_next = self.ids.telefone
        self.ids.telefone.focus_next = self.ids.outras_moedas
        self.ids.outras_moedas.focus_next = self.ids.username  # Loop
        
        # Focar no primeiro campo
        self.ids.username.focus = True

    def posicionar_janela(self):
        """Centraliza a janela na tela"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            
            # Obter tamanho da tela
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # 🔥 POSIÇÃO PERSONALIZADA
            window_width, window_height = Window.size
            
            # Mais para cima e esquerda
            x = (screen_width - window_width) // 4
            y = (screen_height - window_height) // 6
            
            # Garantir posições mínimas
            x = max(x, 20)
            y = max(y, 20)
            
            Window.top = y
            Window.left = x
            
            print(f"📍 Cadastro: Janela posicionada em ({x}, {y})")
            
        except Exception as e:
            print(f"⚠️ Não foi possível posicionar: {e}")
            # FALLBACK: Posição fixa
            Window.top = 30
            Window.left = 50
            print("📍 Cadastro: Posição fallback definida")

    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        campos = [
            'username', 'senha', 'confirmar_senha', 'nome', 
            'email', 'documento', 'telefone', 'outras_moedas'
        ]
        
        for campo_id in campos:
            if hasattr(self, 'ids') and campo_id in self.ids:
                self.ids[campo_id].text = ''
        
        # Resetar checkboxes das moedas (todas marcadas por padrão)
        moedas_checkboxes = ['moeda_usd', 'moeda_eur', 'moeda_gbp', 'moeda_brl']
        for checkbox_id in moedas_checkboxes:
            if hasattr(self, 'ids') and checkbox_id in self.ids:
                self.ids[checkbox_id].active = True
    
    def validar_formulario(self):
        """Valida todos os campos do formulário"""
        # Verificar campos obrigatórios
        campos_obrigatorios = {
            'username': 'Usuário',
            'senha': 'Senha', 
            'confirmar_senha': 'Confirmar Senha',
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'documento': 'CPF/CNPJ'
        }
        
        for campo_id, nome_campo in campos_obrigatorios.items():
            if not self.ids[campo_id].text.strip():
                return False, f"Preencha o campo: {nome_campo}"
        
        # Verificar se senhas coincidem
        if self.ids.senha.text != self.ids.confirmar_senha.text:
            return False, "As senhas não coincidem"
        
        # Verificar tamanho mínimo da senha
        if len(self.ids.senha.text) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres"
        
        # Validar email básico
        if '@' not in self.ids.email.text or '.' not in self.ids.email.text:
            return False, "Digite um e-mail válido"
        
        # Validar que pelo menos uma moeda foi selecionada
        moedas_selecionadas = self.obter_moedas_selecionadas()
        if not moedas_selecionadas:
            return False, "Selecione pelo menos uma moeda"
        
        return True, ""
    
    def obter_moedas_selecionadas(self):
        """Retorna lista de moedas selecionadas"""
        moedas_selecionadas = []
        
        # Moedas padrão
        if self.ids.moeda_usd.active:
            moedas_selecionadas.append('USD')
        if self.ids.moeda_eur.active:
            moedas_selecionadas.append('EUR')
        if self.ids.moeda_gbp.active:
            moedas_selecionadas.append('GBP')
        if self.ids.moeda_brl.active:
            moedas_selecionadas.append('BRL')
        
        # Outras moedas personalizadas
        outras_moedas_texto = self.ids.outras_moedas.text.strip()
        if outras_moedas_texto:
            outras_moedas = [moeda.strip().upper() for moeda in outras_moedas_texto.split(',') if moeda.strip()]
            moedas_selecionadas.extend(outras_moedas)
        
        return moedas_selecionadas
    
    def cadastrar_cliente(self):
        """Processa o cadastro do cliente"""
        sistema = App.get_running_app().sistema
        
        print("👥 Processando cadastro de cliente...")
        
        # Validar formulário
        valido, mensagem = self.validar_formulario()
        if not valido:
            print(f"❌ {mensagem}")
            self.mostrar_erro_cadastro(mensagem)
            return
        
        try:
            # Coletar moedas selecionadas
            moedas_selecionadas = self.obter_moedas_selecionadas()
            
            # Preparar dados
            dados_cliente = {
                'username': self.ids.username.text.strip(),
                'senha': self.ids.senha.text,
                'nome': self.ids.nome.text.strip(),
                'email': self.ids.email.text.strip(),
                'documento': self.ids.documento.text.strip(),
                'telefone': self.ids.telefone.text.strip(),
                'moedas_selecionadas': moedas_selecionadas
            }
            
            # Cadastrar no sistema
            sucesso, resultado = sistema.cadastrar_cliente(dados_cliente)
            
            if sucesso:
                print(f"🎉 CLIENTE CADASTRADO COM SUCESSO!")
                # 🔥 MOSTRAR POPUP DE SUCESSO em vez de voltar direto
                self.mostrar_sucesso_cadastro(dados_cliente, moedas_selecionadas)
            else:
                print(f"❌ Erro no cadastro: {resultado}")
                self.mostrar_erro_cadastro(resultado)
            
        except Exception as e:
            print(f"❌ Erro ao cadastrar cliente: {e}")
            self.mostrar_erro_cadastro(f"Erro interno: {str(e)}")
    
    def mostrar_sucesso_cadastro(self, dados_cliente, moedas_selecionadas):
        """Mostra um popup de sucesso quando o cliente é cadastrado"""
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Mensagem de sucesso
        lbl_sucesso = Label(
            text='🎉 CLIENTE CADASTRADO COM SUCESSO!',
            color=(0.2, 0.8, 0.2, 1),  # Verde para sucesso
            font_size='16sp',
            bold=True,
            text_size=(400, None),
            halign='center'
        )
        
        # Detalhes do cadastro
        detalhes = f"""
👤 Usuário: {dados_cliente['username']}
📝 Nome: {dados_cliente['nome']}
📧 E-mail: {dados_cliente['email']}
📄 Documento: {dados_cliente['documento']}
💰 Moedas: {', '.join(moedas_selecionadas)}
        """.strip()
        
        lbl_detalhes = Label(
            text=detalhes,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            text_size=(400, None),
            halign='left'
        )
        
        # Botão OK
        btn_ok = Button(
            text='VOLTAR AO DASHBOARD',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(lbl_detalhes)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title='✅ Cadastro Concluído',
            title_color=(0.2, 0.8, 0.2, 1),  # Verde para sucesso
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1),
            separator_color=(0.55, 0.36, 0.96, 1),
            auto_dismiss=False  # Só fecha quando clicar no botão
        )
        
        # Fechar popup e voltar ao dashboard
        def voltar_dashboard(instance):
            popup.dismiss()
            self.manager.current = 'dashboard'
        
        btn_ok.bind(on_press=voltar_dashboard)
        
        # Mostrar popup
        popup.open()

    def mostrar_erro_cadastro(self, mensagem):
        """Mostra um popup de erro para cadastro falho"""
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensagem de erro
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),  # Vermelho para erro
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        # Botão OK
        btn_ok = Button(
            text='TENTAR NOVAMENTE',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title='❌ Erro no Cadastro',
            title_color=(1, 0.3, 0.3, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # Fechar popup ao clicar OK
        btn_ok.bind(on_press=popup.dismiss)
        
        # Mostrar popup
        popup.open()

    def cancelar_cadastro(self):
        """Volta para o dashboard"""
        print("❌ Cadastro cancelado")
        self.manager.current = 'dashboard'