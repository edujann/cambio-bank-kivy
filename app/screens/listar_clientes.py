from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import datetime

class CardCliente(BoxLayout):
    """Card para exibir um cliente na lista"""
    
    def __init__(self, cliente, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = [15, 10, 15, 10]
        self.spacing = dp(5)
        self.cliente = cliente
        self.tela_pai = tela_pai
        
        # Background do card
        with self.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]
            )
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        self.criar_conteudo(cliente)
    
    def _atualizar_rect(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def criar_conteudo(self, cliente):
        """Cria o conteúdo do card do cliente"""
        
        # Linha 1: Nome e Status
        linha1 = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        lbl_nome = Label(
            text=cliente['nome'],
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        # Status (sempre ativo por enquanto)
        lbl_status = Label(
            text='🟢 ATIVO',
            font_size='11sp',
            color=(0.2, 0.8, 0.2, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        
        linha1.add_widget(lbl_nome)
        linha1.add_widget(lbl_status)
        
        # Linha 2: Email
        linha2 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        lbl_email = Label(
            text=f"📧 {cliente['email']}",
            font_size='11sp',
            color=(0.80, 0.84, 0.88, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        linha2.add_widget(lbl_email)
        linha2.add_widget(Label())  # Espaço vazio
        
        # Linha 3: Documento e Data
        linha3 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        lbl_documento = Label(
            text=f"📋 {cliente['documento']}",
            font_size='10sp',
            color=(0.80, 0.84, 0.88, 0.8),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        # Formatar data de cadastro
        data_cadastro = cliente.get('data_cadastro', 'N/A')
        lbl_data = Label(
            text=f"📅 {data_cadastro}",
            font_size='10sp',
            color=(0.80, 0.84, 0.88, 0.8),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        
        linha3.add_widget(lbl_documento)
        linha3.add_widget(lbl_data)
        
        # Adicionar todas as linhas
        self.add_widget(linha1)
        self.add_widget(linha2)
        self.add_widget(linha3)
        
        # Botão de detalhes
        btn_detalhes = Button(
            text='Ver Detalhes',
            size_hint_y=None,
            height=dp(30),
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='11sp'
        )
        btn_detalhes.bind(on_press=self.mostrar_detalhes)
        
        self.add_widget(btn_detalhes)
    
    def mostrar_detalhes(self, instance):
        """Mostra detalhes do cliente - VERSÃO CORRIGIDA"""
        self.tela_pai.mostrar_modal_detalhes(self.cliente)  # ✅ CORRETO

class TelaListarClientes(Screen):
    """Tela para listar e gerenciar clientes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1200, 900)
        self.carregar_clientes()
    
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("👥 Tela Listar Clientes carregada")
    
    def carregar_clientes(self, filtro_nome=None):
        """Carrega a lista de clientes com filtro opcional"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        container = self.ids.lista_clientes
        container.clear_widgets()
        
        # Header das colunas
        header = self.criar_header_colunas()
        container.add_widget(header)
        
        # Coletar e filtrar clientes
        clientes_filtrados = []
        
        for username, dados in sistema.usuarios.items():
            # 🔥 CORREÇÃO: Usar .get() com valor padrão
            if dados.get('tipo') == 'cliente':
                # Aplicar filtro por nome
                if filtro_nome:
                    if filtro_nome.lower() not in dados.get('nome', '').lower():
                        continue
                
                clientes_filtrados.append({
                    'username': username,
                    'nome': dados.get('nome', 'N/A'),
                    'email': dados.get('email', 'N/A'),
                    'documento': dados.get('documento', 'N/A'),  # 🔥 CORREÇÃO AQUI
                    'telefone': dados.get('telefone', ''),
                    'data_cadastro': dados.get('data_cadastro', 'N/A'),
                    'contas': dados.get('contas', [])
                })
        
        # Ordenar por nome
        clientes_ordenados = sorted(clientes_filtrados, key=lambda x: x['nome'])
        
        # Adicionar cards
        for cliente in clientes_ordenados:
            card = CardCliente(cliente, self)
            container.add_widget(card)
        
        # Atualizar contador
        total_clientes = len([u for u in sistema.usuarios.values() if u.get('tipo') == 'cliente'])
        filtrados = len(clientes_ordenados)
        
        self.ids.lbl_contador.text = f"Mostrando {filtrados} de {total_clientes} clientes"
        
        # Atualizar estatísticas
        self.atualizar_estatisticas(clientes_ordenados)
    
    def criar_header_colunas(self):
        """Cria o header das colunas"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[15, 5, 15, 5],
            spacing=dp(10)
        )
        
        # Background do header
        with header.canvas.before:
            Color(0.15, 0.20, 0.27, 1)
            header.rect = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[8, 8, 0, 0]
            )
        header.bind(pos=self._atualizar_header_rect, size=self._atualizar_header_rect)
        
        # Colunas
        colunas = [
            ('Cliente', 0.4),
            ('Contato', 0.3),
            ('Documento', 0.2),
            ('Ações', 0.1)
        ]
        
        for texto, largura in colunas:
            lbl = Label(
                text=texto,
                font_size='12sp',
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                text_size=(None, None),
                halign='left',
                valign='middle'
            )
            lbl.size_hint_x = largura
            header.add_widget(lbl)
        
        return header
    
    def _atualizar_header_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def atualizar_estatisticas(self, clientes):
        """Atualiza o painel de estatísticas"""
        if not hasattr(self, 'ids'):
            return
        
        total_clientes = len(clientes)
        
        # Calcular estatísticas básicas
        total_contas = sum(len(cliente['contas']) for cliente in clientes)
        
        # Atualizar labels
        self.ids.lbl_total_clientes.text = f"{total_clientes}"
        self.ids.lbl_total_contas.text = f"{total_contas}"
        
        # Clientes recentes (últimos 30 dias)
        hoje = datetime.datetime.now()
        clientes_recentes = 0
        
        for cliente in clientes:
            try:
                data_cadastro = datetime.datetime.strptime(cliente['data_cadastro'], "%Y-%m-%d")
                if (hoje - data_cadastro).days <= 30:
                    clientes_recentes += 1
            except:
                pass
        
        self.ids.lbl_clientes_recentes.text = f"{clientes_recentes}"
    
    def aplicar_busca(self):
        """Aplica busca por nome"""
        if not hasattr(self, 'ids'):
            return
        
        texto_busca = self.ids.input_busca.text.strip()
        self.carregar_clientes(filtro_nome=texto_busca)
    
    def limpar_busca(self):
        """Limpa a busca"""
        if hasattr(self, 'ids'):
            self.ids.input_busca.text = ''
            self.carregar_clientes()
    
    def exportar_relatorio(self):
        """Exporta relatório de clientes"""
        self.mostrar_sucesso("📊 Funcionalidade de exportação em desenvolvimento!")
    
    def mostrar_modal_detalhes(self, cliente):
        """Modal com detalhes completos do cliente - VERSÃO CORRIGIDA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        lbl_titulo = Label(
            text=f"DETALHES DO CLIENTE",
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        
        # ScrollView para conteúdo
        scroll = ScrollView()
        main_content = BoxLayout(orientation='vertical', size_hint_y=None)
        main_content.bind(minimum_height=main_content.setter('height'))
        
        # Informações do cliente
        informacoes = [
            f"Nome: {cliente['nome']}",
            f"Email: {cliente['email']}",
            f"Documento: {cliente['documento']}",
            f"Telefone: {cliente.get('telefone', 'Não informado')}",
            f"Data de Cadastro: {cliente.get('data_cadastro', 'N/A')}",
            f"Contas: {len(cliente.get('contas', []))} conta(s)"
        ]
        
        for info in informacoes:
            lbl_info = Label(
                text=info,
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
                halign='left',
                text_size=(None, None)
            )
            main_content.add_widget(lbl_info)
        
        scroll.add_widget(main_content)
        
        # Botões de ação
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
        
        btn_fechar = Button(
            text='Fechar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_gerenciar = Button(
            text='Gerenciar Contas',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_fechar)
        botoes_layout.add_widget(btn_gerenciar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(scroll)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(500, 400),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # 🔥 CORREÇÃO: Usar 'email' em vez de 'username'
        email_cliente = cliente['email']
        
        btn_fechar.bind(on_press=popup.dismiss)
        btn_gerenciar.bind(on_press=lambda x: self.ir_para_gerenciar_contas(email_cliente, popup))
        
        popup.open()
    
    def ir_para_gerenciar_contas(self, email_cliente, popup):
        """Navega para gerenciar contas do cliente específico"""
        popup.dismiss()
        print(f"🔧 Indo gerenciar contas do cliente: {email_cliente}")
        # Aqui você pode implementar a navegação para gerenciar contas específicas
        # Por enquanto, apenas mostra uma mensagem
        self.mostrar_sucesso(f"Funcionalidade para gerenciar contas de {email_cliente} em desenvolvimento!")
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'
    
    # ========== MÉTODOS AUXILIARES ==========
    
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