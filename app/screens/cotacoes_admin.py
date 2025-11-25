from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock  # 🔥 ADICIONAR ESTA LINHA
import json
import os
import datetime
import csv

class TelaCotacoesAdmin(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cliente_selecionado = None
        self.spreads_editando = {}

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - VERSÃO CORRIGIDA"""
        print("🎯 ENTRANDO NA TELA COTAÇÕES ADMIN")
        
        from kivy.app import App
        sistema = App.get_running_app().sistema
        
        # 🔥 CARREGAR DADOS PRIMEIRO
        sistema.carregar_dados_cotacoes()
        
        self.carregar_dados()
        self.criar_interface()
        
        print(f"📊 Dados carregados - Horários: {len(sistema.horarios_clientes)} clientes")
        print(f"   Clientes com horário: {list(sistema.horarios_clientes.keys())}")
        

    def on_pre_leave(self, *args):
        """Chamado antes de sair da tela - verifica alterações não salvas"""
        # 🔥 CORREÇÃO: Se já estamos processando uma saída, ignora esta verificação
        if hasattr(self, '_saindo_voluntariamente') and self._saindo_voluntariamente:
            print("Saindo voluntariamente - ignorando verificação dupla")
            return False
            
        print("Saindo da tela - verificando alterações...")
        if self.verificar_alteracoes_pendentes():
            print("Alterações pendentes - mostrando popup")
            self.mostrar_popup_confirmacao_voltar()
            return True  # Impede a saída imediata
        return False

    def carregar_dados(self):
        """Carrega dados do sistema - COM VALIDAÇÃO DE LIMITE"""
        self.sistema = App.get_running_app().sistema
        
        # Garantir que as estruturas existam
        if not hasattr(self.sistema, 'spreads_clientes'):
            self.sistema.spreads_clientes = {}
            
        if not hasattr(self.sistema, 'permissoes_cambio'):
            self.sistema.permissoes_cambio = {}
            
        if not hasattr(self.sistema, 'limites_operacionais'):
            self.sistema.limites_operacionais = {}
        
        # 🔥 VALIDAR LIMITES EXISTENTES
        for username, limite in self.sistema.limites_operacionais.items():
            if limite > 100000:  # Se encontrar limite > 100 mil
                print(f"LIMITE SUSPEITO ENCONTRADO: {username} = US$ {limite:,.2f}")
                # Corrigir automaticamente
                self.sistema.limites_operacionais[username] = 10000.00
                print(f"Limite corrigido para: US$ 10.000,00")
        
        # 🔥 ATUALIZAR TEMPLATES COM NOVOS VALORES
        self.templates_spread = {
            'corporativo': {'compra': 0.5, 'venda': 0.5},    # 0.5%/0.5%
            'varejo': {'compra': 0.6, 'venda': 0.6},        # 0.6%/0.6%
            'vip': {'compra': 0.3, 'venda': 0.3}            # 0.3%/0.3%
        }
        
        # Pares de moedas fixos
        self.pares_moedas = [
            'USD_BRL', 'EUR_BRL', 'GBP_BRL', 
            'EUR_USD', 'GBP_USD', 'USD_EUR',
            'BRL_USD', 'BRL_EUR', 'BRL_GBP',
            'USD_GBP', 'EUR_GBP', 'GBP_EUR'
        ]
        
        self.clientes = self.obter_clientes_para_cotacoes()
    
    def obter_clientes_para_cotacoes(self):
        """Obtém lista de clientes com informações de câmbio"""
        clientes = []
        for username, dados in self.sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                # Spreads do cliente (ou vazio se não configurado)
                spreads_cliente = self.sistema.spreads_clientes.get(username, {})
                
                # Permissão (True por padrão para novos clientes)
                cambio_liberado = self.sistema.permissoes_cambio.get(username, True)
                
                # Limite operacional (R$ 10.000,00 padrão)
                limite_operacional = self.sistema.limites_operacionais.get(username, 10000.00)
                
                cliente_info = {
                    'username': username,
                    'nome': dados['nome'],
                    'email': dados['email'],
                    'cambio_liberado': cambio_liberado,
                    'spreads': spreads_cliente,
                    'limite_operacional': limite_operacional
                }
                clientes.append(cliente_info)
        return clientes

    def configurar_estado_inicial(self):
        """Configura o estado inicial da interface"""
        print("🔧 Configurando estado inicial da interface...")
        
        # Inicializar todos os controles como desabilitados
        if hasattr(self, 'input_dias'):
            self.input_dias.disabled = True
            self.input_inicio.disabled = True
            self.input_fim.disabled = True
            self.input_dias.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_inicio.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_fim.background_color = [0.15, 0.15, 0.15, 0.5]
        
        # Switch começa desligado (será ajustado quando cliente for selecionado)
        if hasattr(self, 'switch_horario_personalizado'):
            # Desvincular temporariamente para evitar eventos durante inicialização
            self.switch_horario_personalizado.unbind(active=self.toggle_horario_personalizado)
            self.switch_horario_personalizado.active = False
            # Re-vincular
            self.switch_horario_personalizado.bind(active=self.toggle_horario_personalizado)
        
        print("✅ Estado inicial configurado")

    def criar_interface(self):
        """Cria interface da tela"""
        self.clear_widgets()
        
        # Layout principal com altura mínima para garantir scroll
        layout_principal = BoxLayout(orientation='vertical', padding=[15, 15, 15, 15], spacing=10)
        
        # Header (fixo)
        header = self.criar_header()
        layout_principal.add_widget(header)
        
        # Corpo principal COM SCROLL
        scroll_principal = ScrollView(size_hint_y=0.9, do_scroll_y=True)
        corpo_scroll = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None)
        corpo_scroll.bind(minimum_height=corpo_scroll.setter('height'))
        
        # Lista de clientes
        lista_clientes = self.criar_lista_clientes()
        corpo_scroll.add_widget(lista_clientes)
        
        # Painel de detalhes
        painel_detalhes = self.criar_painel_detalhes()
        corpo_scroll.add_widget(painel_detalhes)
        
        # Definir altura mínima do corpo baseado no conteúdo
        corpo_scroll.height = max(600, len(self.clientes) * 80)  # Altura mínima de 600
        
        scroll_principal.add_widget(corpo_scroll)
        layout_principal.add_widget(scroll_principal)
        
        self.add_widget(layout_principal)
        
        # 🔥 CONFIGURAR ESTADO INICIAL
        self.configurar_estado_inicial()
    
    def criar_header(self):
        """Cria cabeçalho da tela - COM BOTÃO DEBUG TEMPORÁRIO"""
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        
        btn_voltar = Button(
            text='< Voltar',
            size_hint_x=0.15,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        btn_voltar.bind(on_press=self.voltar_dashboard)
        
        titulo = Label(
            text='GERENCIAR COTAÇÕES',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=0.6,
            text_size=(None, None),
            halign='center'
        )
        
        # Container para botões à direita
        botoes_direita = BoxLayout(orientation='horizontal', size_hint_x=0.25, spacing=5)
        
        # 🔥 BOTÃO DEBUG TEMPORÁRIO (remover depois)
        btn_debug = Button(
            text='Debug',
            size_hint_x=0.3,
            background_color=(0.8, 0.4, 0.1, 1),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        btn_debug.bind(on_press=self.debug_todos_limites)
        
        btn_exportar = Button(
            text='Exportar',
            size_hint_x=0.35,
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        btn_exportar.bind(on_press=self.exportar_para_csv)
        
        btn_salvar = Button(
            text='Salvar',
            size_hint_x=0.35,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        btn_salvar.bind(on_press=self.salvar_todas_alteracoes)
        
        botoes_direita.add_widget(btn_debug)  # 🔥 Adicionar botão debug
        botoes_direita.add_widget(btn_exportar)
        botoes_direita.add_widget(btn_salvar)
        
        header.add_widget(btn_voltar)
        header.add_widget(titulo)
        header.add_widget(botoes_direita)
        
        return header

    def debug_todos_limites(self, instance):
        """Debug de todos os limites - para investigar o problema"""
        print("=== 🔍 DEBUG COMPLETO DOS LIMITES ===")
        for username, limite in self.sistema.limites_operacionais.items():
            print(f"   {username}: US$ {limite:,.2f}")
        print("=== 🎯 FIM DEBUG LIMITES ===")
        
        if self.cliente_selecionado:
            self.debug_limite(self.cliente_selecionado['username'], "DEBUG MANUAL")
    
    def criar_lista_clientes(self):
        """Cria lista scrollável de clientes"""
        container = BoxLayout(orientation='vertical', size_hint_x=0.35, spacing=8)
        
        # Barra de pesquisa
        barra_pesquisa = BoxLayout(orientation='horizontal', size_hint_y=0.07, spacing=5)
        
        self.input_pesquisa = TextInput(
            hint_text='Pesquisar cliente...',
            size_hint_x=0.7,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            multiline=False,
            font_size='13sp',
            padding=[8, 8]
        )
        self.input_pesquisa.bind(text=self.filtrar_clientes)
        
        btn_limpar = Button(
            text='X',
            size_hint_x=0.1,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        btn_limpar.bind(on_press=self.limpar_pesquisa)
        
        barra_pesquisa.add_widget(self.input_pesquisa)
        barra_pesquisa.add_widget(btn_limpar)
        
        titulo = Label(
            text=f'CLIENTES ({len(self.clientes)})',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.05,
            text_size=(None, None),
            halign='left'
        )
        
        scroll = ScrollView(size_hint_y=0.88)
        self.grid_clientes = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid_clientes.bind(minimum_height=self.grid_clientes.setter('height'))
        
        self.carregar_lista_clientes_ui()
        
        scroll.add_widget(self.grid_clientes)
        container.add_widget(barra_pesquisa)
        container.add_widget(titulo)
        container.add_widget(scroll)
        
        return container
    
    def carregar_lista_clientes_ui(self, clientes_filtrados=None):
        """Carrega a lista de clientes na UI - COM SELEÇÃO"""
        self.grid_clientes.clear_widgets()
        
        clientes = clientes_filtrados if clientes_filtrados else self.clientes
        
        for cliente in clientes:
            # Container para cada cliente
            cliente_container = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=dp(65),
                spacing=5,
                padding=[5, 2]
            )
            
            # Marcar o container com os dados do cliente
            cliente_container.cliente_data = cliente
            
            # Botão do cliente
            btn_cliente = Button(
                text=f"{cliente['nome']}\n{cliente['email']}",
                size_hint_x=0.8,
                background_color=(0.20, 0.25, 0.33, 1),  # Cor normal
                color=(1, 1, 1, 1),
                font_size='12sp',
                halign='left',
                valign='middle'
            )
            btn_cliente.bind(on_press=lambda instance, c=cliente: self.selecionar_cliente(c))
            
            # Indicador visual de status
            status_container = BoxLayout(orientation='vertical', size_hint_x=0.2, spacing=2)
            
            # Indicador de permissão
            status_color = (0.2, 0.8, 0.2, 1) if cliente['cambio_liberado'] else (0.8, 0.2, 0.2, 1)
            status_text = "LIB" if cliente['cambio_liberado'] else "BLOQ"
            
            lbl_status = Label(
                text=status_text,
                font_size='12sp',
                color=status_color,
                bold=True
            )
            
            # Indicador de spreads configurados
            spreads_count = len(cliente['spreads'])
            lbl_spreads = Label(
                text=f'{spreads_count} spreads',
                font_size='10sp',
                color=(0.23, 0.51, 0.96, 1) if spreads_count > 0 else (0.7, 0.7, 0.7, 1)
            )
            
            status_container.add_widget(lbl_status)
            status_container.add_widget(lbl_spreads)
            
            cliente_container.add_widget(btn_cliente)
            cliente_container.add_widget(status_container)
            
            self.grid_clientes.add_widget(cliente_container)
        
        self.grid_clientes.height = len(clientes) * dp(70)
    
    def criar_painel_detalhes(self):
        """Cria painel de detalhes do cliente selecionado"""
        container = BoxLayout(orientation='vertical', size_hint_x=0.65, spacing=10)
        
        # Header do painel
        self.lbl_cliente_selecionado = Label(
            text='Selecione um cliente para configurar',
            font_size='15sp',
            bold=True,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.06,
            text_size=(None, None),
            halign='center'
        )
        
        # Container principal COM SCROLL para todo o conteúdo
        scroll_principal = ScrollView(size_hint_y=0.94, do_scroll_y=True)
        conteudo_principal = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        conteudo_principal.bind(minimum_height=conteudo_principal.setter('height'))
        
        # Seção 1: Templates de Spread
        secao_templates = self.criar_secao_templates()
        conteudo_principal.add_widget(secao_templates)
        
        # 🔥 NOVA SEÇÃO: Horário Comercial
        secao_horario = self.criar_secao_horario_comercial()
        conteudo_principal.add_widget(secao_horario)
        
        # Seção 2: Controles principais do cliente (agora Seção 3)
        secao_controles = self.criar_secao_controles()
        conteudo_principal.add_widget(secao_controles)
        
        # Seção 3: Tabela de spreads
        secao_spreads = self.criar_secao_spreads()
        conteudo_principal.add_widget(secao_spreads)
        
        # Definir altura total do conteúdo
        altura_total = (secao_templates.height + secao_controles.height + 
                       secao_spreads.height + 30)  # + espaçamento
        conteudo_principal.height = max(600, altura_total)
        
        scroll_principal.add_widget(conteudo_principal)
        
        container.add_widget(self.lbl_cliente_selecionado)
        container.add_widget(scroll_principal)
        
        return container
    
    def criar_secao_templates(self):
        """Cria seção de templates de spread"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90), spacing=5)
        
        with container.canvas.before:
            Color(0.12, 0.16, 0.23, 1)
            container.rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[8,])
        container.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        lbl_titulo = Label(
            text='TEMPLATES DE SPREAD',
            font_size='12sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        
        botoes_templates = BoxLayout(orientation='horizontal', size_hint_y=0.7, spacing=8, padding=[10, 5])
        
        btn_corporativo = Button(
            text='Corporativo\n(0.5%/0.5%)',
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        btn_corporativo.bind(on_press=lambda x: self.aplicar_template('corporativo'))
        
        btn_varejo = Button(
            text='Varejo\n(0.6%/0.6%)',
            background_color=(0.2, 0.8, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        btn_varejo.bind(on_press=lambda x: self.aplicar_template('varejo'))
        
        btn_vip = Button(
            text='VIP\n(0.3%/0.3%)',
            background_color=(0.8, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        btn_vip.bind(on_press=lambda x: self.aplicar_template('vip'))
        
        botoes_templates.add_widget(btn_corporativo)
        botoes_templates.add_widget(btn_varejo)
        botoes_templates.add_widget(btn_vip)
        
        container.add_widget(lbl_titulo)
        container.add_widget(botoes_templates)
        
        return container
    
    def criar_secao_controles(self):
        """Cria seção de controles principais do cliente"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=8)
        
        with container.canvas.before:
            Color(0.12, 0.16, 0.23, 1)
            container.rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[8,])
        container.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        # Linha 1: Permissão de câmbio
        linha_permissao = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=8, padding=[10, 0])
        
        lbl_permissao = Label(
            text='Câmbio Liberado:',
            color=(1, 1, 1, 1),
            size_hint_x=0.6,
            text_size=(None, None),
            halign='left',
            font_size='13sp'
        )
        
        self.switch_liberado = Switch(
            active=True,
            size_hint_x=0.2
        )
        self.switch_liberado.bind(active=self.alterar_permissao_cambio)
        
        linha_permissao.add_widget(lbl_permissao)
        linha_permissao.add_widget(self.switch_liberado)
        linha_permissao.add_widget(Label(size_hint_x=0.2))  # Espaço vazio
        
        # Linha 2: Limite operacional
        linha_limite = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=8, padding=[10, 0])
        
        lbl_limite = Label(
            text='Limite Máximo:',
            color=(1, 1, 1, 1),
            size_hint_x=0.6,
            text_size=(None, None),
            halign='left',
            font_size='13sp'
        )
        
        self.input_limite = TextInput(
            text='10000.00',
            size_hint_x=0.3,
            multiline=False,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1),
            font_size='13sp',
            padding=[8, 8]
        )
        self.input_limite.bind(text=self.alterar_limite_operacional)
        
        linha_limite.add_widget(lbl_limite)
        linha_limite.add_widget(self.input_limite)
        
        # Linha 3: Estatísticas
        linha_stats = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=8, padding=[10, 0])
        
        self.lbl_stats = Label(
            text='Spreads configurados: 0/12 pares',
            color=(0.8, 0.8, 0.8, 1),
            font_size='10sp',
            text_size=(None, None),
            halign='left'
        )
        
        linha_stats.add_widget(self.lbl_stats)
        
        container.add_widget(linha_permissao)
        container.add_widget(linha_limite)
        container.add_widget(linha_stats)
        
        return container
    
    def criar_secao_spreads(self):
        """Cria seção da tabela de spreads - COM NOVA COLUNA AÇÃO"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        
        # Header da tabela
        header_tabela = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=2)
        
        lbl_titulo = Label(
            text='',
            font_size='12sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(None, None),
            halign='left'
        )
        
        header_tabela.add_widget(lbl_titulo)
        
        # Container da tabela COM SCROLL PRÓPRIO
        tabela_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        
        # Cabeçalho da tabela - COLUNAS (AGORA COM AÇÃO)
        cabecalho_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=2)
        
        cabecalhos = ['AÇÃO', 'PAR', 'COMPRA %', 'VENDA %', 'SALVAR']
        larguras = [0.15, 0.25, 0.2, 0.2, 0.2]  # Proporções ajustadas
        
        for i, cabecalho in enumerate(cabecalhos):
            lbl = Label(
                text=cabecalho,
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                size_hint_x=larguras[i],
                text_size=(None, None),
                halign='center',
                font_size='13sp'
            )
            cabecalho_container.add_widget(lbl)
        
        # ScrollView para a tabela de dados
        scroll_tabela = ScrollView(size_hint_y=None, do_scroll_y=True)
        self.grid_spreads = GridLayout(cols=1, spacing=2, size_hint_y=None, padding=[0, 5, 0, 5])
        self.grid_spreads.bind(minimum_height=self.grid_spreads.setter('height'))
        
        # Altura fixa para a área da tabela
        altura_tabela = min(400, len(self.pares_moedas) * 45)
        scroll_tabela.height = altura_tabela
        scroll_tabela.size_hint_y = None
        
        scroll_tabela.add_widget(self.grid_spreads)
        
        # Adicionar tudo ao container
        tabela_container.add_widget(cabecalho_container)
        tabela_container.add_widget(scroll_tabela)
        
        # Altura total da seção
        container.height = dp(30) + dp(30) + altura_tabela + dp(20)
        
        container.add_widget(header_tabela)
        container.add_widget(tabela_container)
        
        return container

    def toggle_par_cliente(self, instance):
        """Adiciona ou remove um par do cliente"""
        par = instance.par
        liberado_atual = instance.liberado
        username = self.cliente_selecionado['username']
        
        if liberado_atual:
            # REMOVER par - Popup de confirmação
            content = BoxLayout(orientation='vertical', padding=15, spacing=10)
            
            lbl_confirmacao = Label(
                text=f'Remover par {par} do cliente?\n\nEsta ação irá excluir as configurações de spread para este par.',
                color=(1, 1, 1, 1),
                text_size=(300, None),
                halign='center'
            )
            
            botoes = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.4)
            
            btn_cancelar = Button(
                text='Cancelar',
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            
            btn_confirmar = Button(
                text='Remover',
                background_color=(0.2, 0.8, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            
            botoes.add_widget(btn_cancelar)
            botoes.add_widget(btn_confirmar)
            
            content.add_widget(lbl_confirmacao)
            content.add_widget(botoes)
            
            popup = Popup(
                title='Remover Par',
                content=content,
                size_hint=(None, None),
                size=(350, 200)
            )
            
            def confirmar_remover(btn):
                # Remover par do cliente
                if username in self.sistema.spreads_clientes and par in self.sistema.spreads_clientes[username]:
                    del self.sistema.spreads_clientes[username][par]
                
                # Atualizar dados do cliente selecionado
                self.cliente_selecionado['spreads'] = self.sistema.spreads_clientes.get(username, {})
                
                # 🔥 ATUALIZAR CONTADOR DE SPREADS
                spreads_count = len(self.cliente_selecionado['spreads'])
                self.atualizar_contador_spreads_cliente(username, spreads_count)
                
                # Recarregar tabela
                self.carregar_spreads_cliente()
                
                popup.dismiss()
                self.mostrar_sucesso(f"Par {par} removido com sucesso!")
            
            btn_cancelar.bind(on_press=popup.dismiss)
            btn_confirmar.bind(on_press=confirmar_remover)
            
            popup.open()
            
        else:
            # ADICIONAR par
            if username not in self.sistema.spreads_clientes:
                self.sistema.spreads_clientes[username] = {}
            
            # Adicionar com spreads padrão
            self.sistema.spreads_clientes[username][par] = {
                'compra': 0.5,
                'venda': 0.5
            }
            
            # Atualizar dados do cliente selecionado
            self.cliente_selecionado['spreads'] = self.sistema.spreads_clientes[username]
            
            # 🔥 ATUALIZAR CONTADOR DE SPREADS
            spreads_count = len(self.cliente_selecionado['spreads'])
            self.atualizar_contador_spreads_cliente(username, spreads_count)
            
            # Recarregar tabela
            self.carregar_spreads_cliente()
            
            self.mostrar_sucesso(f"Par {par} adicionado com sucesso!")

    def _atualizar_rect(self, instance, value):
        """Atualiza retângulo de fundo"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def _atualizar_container_rect(self, instance, value):
        """Atualiza retângulo de fundo dos containers"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    # ========== MÉTODOS DE FUNCIONALIDADE ==========
    
    def filtrar_clientes(self, instance, value):
        """Filtra lista de clientes por pesquisa"""
        if not value:
            self.carregar_lista_clientes_ui()
            return
            
        clientes_filtrados = []
        termo = value.lower()
        
        for cliente in self.clientes:
            if (termo in cliente['nome'].lower() or 
                termo in cliente['email'].lower() or
                termo in cliente['username'].lower()):
                clientes_filtrados.append(cliente)
        
        self.carregar_lista_clientes_ui(clientes_filtrados)
    
    def limpar_pesquisa(self, instance):
        """Limpa a pesquisa"""
        self.input_pesquisa.text = ''
        self.carregar_lista_clientes_ui()
    
    def selecionar_cliente(self, cliente):
        """Seleciona um cliente para edição - VERSÃO COM DEBUG"""
        # Resetar cor de todos os clientes primeiro
        for child in self.grid_clientes.children:
            if hasattr(child, 'cliente_data'):
                # Voltar para cor normal
                for widget in child.children:
                    if isinstance(widget, Button):
                        widget.background_color = (0.20, 0.25, 0.33, 1)
        
        # Destacar o cliente selecionado
        self.cliente_selecionado = cliente
        
        username = cliente['username']
        
        print(f"🔍 SELECIONANDO CLIENTE: {username}")
        print(f"   Horários disponíveis no sistema: {list(self.sistema.horarios_clientes.keys())}")
        
        # GARANTIR QUE OS DADOS ESTEJAM ATUALIZADOS
        if username in self.sistema.spreads_clientes:
            cliente['spreads'] = self.sistema.spreads_clientes[username]
        
        self.lbl_cliente_selecionado.text = f"{cliente['nome']}\n{cliente['email']}"
        self.lbl_cliente_selecionado.color = (1, 1, 1, 1)
        
        self.switch_liberado.active = cliente['cambio_liberado']
        self.input_limite.text = f"{cliente['limite_operacional']:.2f}"
        
        # 🔥 CARREGAR HORÁRIO 
        print(f"   Chamando carregar_horario_cliente...")
        self.carregar_horario_cliente()
        
        self.carregar_spreads_cliente()
        
        # Encontrar e destacar o botão do cliente selecionado
        for child in self.grid_clientes.children:
            if hasattr(child, 'cliente_data') and child.cliente_data == cliente:
                for widget in child.children:
                    if isinstance(widget, Button):
                        widget.background_color = (0.35, 0.45, 0.95, 1)  # Azul destacado

    def carregar_spreads_cliente(self):
        """Carrega os spreads do cliente selecionado na tabela - COM BOTÃO AÇÃO"""
        self.grid_spreads.clear_widgets()
        
        if not self.cliente_selecionado:
            return
            
        spreads_cliente = self.cliente_selecionado['spreads']
        spreads_configurados = 0
        
        for par in self.pares_moedas:
            # Verificar se o par está liberado (configurado)
            par_liberado = par in spreads_cliente
            
            # Valores atuais ou padrão
            spread_compra = spreads_cliente.get(par, {}).get('compra', 0.5)
            spread_venda = spreads_cliente.get(par, {}).get('venda', 0.5)
            
            if par_liberado:
                spreads_configurados += 1
            
            # Linha da tabela
            linha_container = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=dp(35),
                spacing=2
            )
            
            # BOTÃO AÇÃO - Adicionar/Remover
            if par_liberado:
                btn_acao = Button(
                    text='Remover',
                    size_hint_x=0.15,
                    background_color=(0.8, 0.2, 0.2, 1),  # Vermelho
                    color=(1, 1, 1, 1),
                    font_size='11sp'
                )
            else:
                btn_acao = Button(
                    text='Adicionar',
                    size_hint_x=0.15,
                    background_color=(0.2, 0.6, 0.2, 1),  # Verde
                    color=(1, 1, 1, 1),
                    font_size='11sp'
                )
            
            btn_acao.par = par
            btn_acao.liberado = par_liberado
            btn_acao.bind(on_press=self.toggle_par_cliente)
            
            # Par de moedas
            lbl_par = Label(
                text=par,
                color=(1, 1, 1, 1),
                size_hint_x=0.25,
                text_size=(None, None),
                halign='center',
                font_size='12sp'
            )
            
            # Input spread compra
            input_compra = TextInput(
                text=f"{spread_compra:.2f}",
                size_hint_x=0.2,
                multiline=False,
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                halign='center',
                font_size='12sp',
                padding=[4, 6]
            )
            input_compra.par = par
            input_compra.tipo = 'compra'
            input_compra.bind(text=self.on_spread_change)
            
            # Input spread venda
            input_venda = TextInput(
                text=f"{spread_venda:.2f}",
                size_hint_x=0.2,
                multiline=False,
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                halign='center',
                font_size='12sp',
                padding=[4, 6]
            )
            input_venda.par = par
            input_venda.tipo = 'venda'
            input_venda.bind(text=self.on_spread_change)
            
            # Botão salvar
            btn_salvar = Button(
                text='Salvar',
                size_hint_x=0.2,
                background_color=(0.2, 0.6, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size='12sp'
            )
            btn_salvar.par = par
            btn_salvar.input_compra = input_compra
            btn_salvar.input_venda = input_venda
            btn_salvar.bind(on_press=self.salvar_spread_individual)
            
            # Adicionar widgets à linha
            linha_container.add_widget(btn_acao)
            linha_container.add_widget(lbl_par)
            linha_container.add_widget(input_compra)
            linha_container.add_widget(input_venda)
            linha_container.add_widget(btn_salvar)
            
            self.grid_spreads.add_widget(linha_container)
        
        # Atualizar estatísticas
        self.lbl_stats.text = f'Spreads configurados: {spreads_configurados}/{len(self.pares_moedas)} pares'
        
        # Ajustar altura da grid
        self.grid_spreads.height = len(self.pares_moedas) * dp(37)

    def on_spread_change(self, instance, value):
        """Quando um spread é alterado (marca como não salvo)"""
        try:
            # Validar se é um número válido
            valor = float(value) if value else 0.0
            if valor < 0 or valor > 100:
                instance.background_color = (0.8, 0.2, 0.2, 1)  # Vermelho se inválido
            else:
                instance.background_color = (0.95, 0.6, 0.5, 1)  # Salmão
        except ValueError:
            instance.background_color = (0.8, 0.2, 0.2, 1)  # Vermelho se inválido

    def salvar_spread_individual(self, instance):
        """Salva um spread individual com confirmação - COM ATUALIZAÇÃO VISUAL"""
        par = instance.par
        try:
            spread_compra = float(instance.input_compra.text)
            spread_venda = float(instance.input_venda.text)
            
            # Validar valores
            if spread_compra < 0 or spread_venda < 0:
                self.mostrar_erro("Os spreads não podem ser negativos!")
                return
            
            # Popup de confirmação
            content = BoxLayout(orientation='vertical', padding=15, spacing=10)
            
            lbl_confirmacao = Label(
                text=f'Confirmar alteração no par {par}?\nCompra: {spread_compra:.2f}%\nVenda: {spread_venda:.2f}%',
                color=(1, 1, 1, 1),
                text_size=(300, None),
                halign='center'
            )
            
            botoes = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.4)
            
            btn_cancelar = Button(
                text='Cancelar',
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            
            btn_confirmar = Button(
                text='Confirmar',
                background_color=(0.2, 0.8, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            
            botoes.add_widget(btn_cancelar)
            botoes.add_widget(btn_confirmar)
            
            content.add_widget(lbl_confirmacao)
            content.add_widget(botoes)
            
            popup = Popup(
                title='Confirmação',
                content=content,
                size_hint=(None, None),
                size=(350, 200)
            )
            
            def confirmar_salvar(btn):
                # Atualizar no cliente selecionado
                username = self.cliente_selecionado['username']
                
                if username not in self.sistema.spreads_clientes:
                    self.sistema.spreads_clientes[username] = {}
                
                self.sistema.spreads_clientes[username][par] = {
                    'compra': spread_compra,
                    'venda': spread_venda
                }
                
                # 🔥 ATUALIZAR OS DADOS DO CLIENTE SELECIONADO
                self.cliente_selecionado['spreads'] = self.sistema.spreads_clientes[username]
                
                # Atualizar visual
                instance.input_compra.background_color = (0.20, 0.25, 0.33, 1)
                instance.input_venda.background_color = (0.20, 0.25, 0.33, 1)
                
                # 🔥 ATUALIZAR CONTADOR DE SPREADS E VISUAL
                spreads_configurados = len(self.sistema.spreads_clientes[username])
                self.lbl_stats.text = f'Spreads configurados: {spreads_configurados}/{len(self.pares_moedas)} pares'
                
                # 🔥 ATUALIZAR VISUAL NA LISTA DE CLIENTES
                self.atualizar_contador_spreads_cliente(username, spreads_configurados)
                
                popup.dismiss()
                self.mostrar_sucesso(f"Spread {par} salvo com sucesso!")
            
            btn_cancelar.bind(on_press=popup.dismiss)
            btn_confirmar.bind(on_press=confirmar_salvar)
            
            popup.open()
            
        except ValueError:
            self.mostrar_erro("Valores inválidos! Use números decimais.")

    def atualizar_contador_spreads_cliente(self, username, spreads_count):
        """Atualiza o contador de spreads na lista de clientes"""
        for child in self.grid_clientes.children:
            if hasattr(child, 'cliente_data') and child.cliente_data['username'] == username:
                # Encontrar o label de spreads dentro do container
                for widget in child.children:
                    if isinstance(widget, BoxLayout):  # Container de status
                        for sub_widget in widget.children:
                            if isinstance(sub_widget, Label) and 'spreads' in sub_widget.text:
                                # Atualizar contador
                                sub_widget.text = f'{spreads_count} spreads'
                                sub_widget.color = (0.23, 0.51, 0.96, 1) if spreads_count > 0 else (0.7, 0.7, 0.7, 1)
                                break
                        break

    def aplicar_template(self, template_nome):
        """Aplica um template de spread ao cliente selecionado - COM ATUALIZAÇÃO VISUAL"""
        if not self.cliente_selecionado:
            self.mostrar_erro("Selecione um cliente primeiro!")
            return
        
        spreads = self.templates_spread[template_nome]
        
        # Popup de confirmação
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_confirmacao = Label(
            text=f'Aplicar template {template_nome.upper()} a TODOS os pares?\nCompra: {spreads["compra"]:.1f}% | Venda: {spreads["venda"]:.1f}%',
            color=(1, 1, 1, 1),
            text_size=(300, None),
            halign='center'
        )
        
        botoes = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.4)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Aplicar a Todos',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes.add_widget(btn_cancelar)
        botoes.add_widget(btn_confirmar)
        
        content.add_widget(lbl_confirmacao)
        content.add_widget(botoes)
        
        popup = Popup(
            title=f'Template {template_nome.upper()}',
            content=content,
            size_hint=(None, None),
            size=(400, 200)
        )
        
        def confirmar_template(btn):
            username = self.cliente_selecionado['username']
            
            if username not in self.sistema.spreads_clientes:
                self.sistema.spreads_clientes[username] = {}
            
            # Aplicar a todos os pares
            for par in self.pares_moedas:
                self.sistema.spreads_clientes[username][par] = {
                    'compra': spreads['compra'],
                    'venda': spreads['venda']
                }
            
            # 🔥 ATUALIZAR OS DADOS DO CLIENTE SELECIONADO
            self.cliente_selecionado['spreads'] = self.sistema.spreads_clientes[username].copy()
            
            # 🔥 ATUALIZAR CONTADOR E VISUAL
            spreads_configurados = len(self.pares_moedas)  # Todos os pares configurados
            self.lbl_stats.text = f'Spreads configurados: {spreads_configurados}/{len(self.pares_moedas)} pares'
            self.atualizar_contador_spreads_cliente(username, spreads_configurados)
            
            # 🔥 FORÇAR A RECARGA DA TABELA
            self.carregar_spreads_cliente()
            
            # 🔥 MARCAR TODOS OS INPUTS COMO ALTERADOS (PARA O POPUP DETECTAR)
            self.marcar_todos_inputs_como_alterados()
            
            popup.dismiss()
            self.mostrar_sucesso(f"Template {template_nome} aplicado a todos os pares!")
        
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_confirmar.bind(on_press=confirmar_template)
        
        popup.open()

    def marcar_todos_inputs_como_alterados(self):
        """Marca todos os inputs da tabela como alterados (para o popup detectar)"""
        print("Marcando todos os inputs como alterados...")
        cor_alterado = (0.95, 0.7, 0.3, 1)  # Laranja suave
        
        for child in self.grid_spreads.children:
            for widget in child.children:
                if isinstance(widget, TextInput):
                    widget.background_color = cor_alterado
                    print(f"   Input marcado: {widget.text}")

    def alterar_permissao_cambio(self, instance, value):
        """Altera permissão de câmbio do cliente - COM ATUALIZAÇÃO VISUAL"""
        if not self.cliente_selecionado:
            return
        
        username = self.cliente_selecionado['username']
        self.sistema.permissoes_cambio[username] = value
        
        # Atualizar no cliente da lista
        for cliente in self.clientes:
            if cliente['username'] == username:
                cliente['cambio_liberado'] = value
                break
        
        # 🔥 ATUALIZAR VISUALMENTE A LISTA DE CLIENTES
        self.atualizar_visual_cliente_selecionado(username, value)
        
        self.mostrar_sucesso(f"Câmbio {'liberado' if value else 'bloqueado'} para {username}")

    def atualizar_visual_cliente_selecionado(self, username, cambio_liberado):
        """Atualiza visualmente o cliente na lista"""
        for child in self.grid_clientes.children:
            if hasattr(child, 'cliente_data') and child.cliente_data['username'] == username:
                # Encontrar os labels de status dentro do container
                for widget in child.children:
                    if isinstance(widget, BoxLayout):  # Container de status
                        for sub_widget in widget.children:
                            if isinstance(sub_widget, Label) and sub_widget.text in ['LIB', 'BLOQ']:
                                # Atualizar texto e cor
                                sub_widget.text = "LIB" if cambio_liberado else "BLOQ"
                                sub_widget.color = (0.2, 0.8, 0.2, 1) if cambio_liberado else (0.8, 0.2, 0.2, 1)
                                break
                        break

    def alterar_limite_operacional(self, instance, value):
        """Altera limite operacional do cliente - COM DEBUG E VALIDAÇÃO CORRIGIDA"""
        if not self.cliente_selecionado:
            return
        
        try:
            # 🔍 ADICIONAR DEBUG
            if self.cliente_selecionado:
                self.debug_limite(self.cliente_selecionado['username'], "ANTES alterar_limite")
            
            # 🔥 CORREÇÃO MELHORADA: Melhor parsing do valor
            valor_limpo = value.replace('R$', '').replace(' ', '').strip()
            
            # 🔥 CORREÇÃO: Substituir vírgula por ponto
            valor_limpo = valor_limpo.replace(',', '.')
            
            # 🔥 CORREÇÃO: Validar se tem apenas um ponto decimal
            partes = valor_limpo.split('.')
            if len(partes) > 2:
                # Múltiplos pontos - usar apenas a primeira parte
                valor_limpo = partes[0] + '.' + ''.join(partes[1:])
            
            # Converter para float
            limite = float(valor_limpo) if valor_limpo else 10000.00
            
            # 🔥 VALIDAÇÃO DE VALOR MÁXIMO
            if limite < 0:
                raise ValueError("Limite não pode ser negativo")
            if limite > 100000:  # 100 mil como limite máximo
                self.mostrar_erro(f"Limite muito alto! Máximo permitido: R$ 100,000.00")
                # Restaurar valor anterior
                limite_anterior = self.sistema.limites_operacionais.get(self.cliente_selecionado['username'], 10000.00)
                instance.text = f"{limite_anterior:.2f}"
                return
            
            username = self.cliente_selecionado['username']
            limite_atual = self.sistema.limites_operacionais.get(username, 10000.00)
            
            # Mudar cor apenas se for diferente
            if abs(limite - limite_atual) > 0.01:  # Tolerância para float
                instance.background_color = [0.95, 0.7, 0.3, 1]  # Laranja - alterado
                print(f"🎨 Limite alterado visualmente: {limite_atual} -> {limite}")
            else:
                instance.background_color = [0.20, 0.25, 0.33, 1]  # Cor normal
            
            # Atualizar no cliente da lista
            for cliente in self.clientes:
                if cliente['username'] == username:
                    cliente['limite_operacional'] = limite
                    break
            
            # 🔍 DEBUG APÓS ALTERAÇÃO
            self.debug_limite(username, "APÓS alterar_limite")
            
        except ValueError as e:
            print(f"❌ Erro ao processar limite: {e}")
            # 🔥 CORREÇÃO: Restaurar valor anterior em caso de erro
            if self.cliente_selecionado:
                username = self.cliente_selecionado['username']
                limite_anterior = self.sistema.limites_operacionais.get(username, 10000.00)
                instance.text = f"{limite_anterior:.2f}"
                instance.background_color = [0.20, 0.25, 0.33, 1]  # Cor normal
            self.mostrar_erro("Valor de limite inválido! Use apenas números.")

    def salvar_todas_alteracoes(self, instance=None):
        """Salva todas as alterações pendentes - AGORA COM SUPABASE"""
        print("💾 SALVANDO TODAS AS ALTERAÇÕES NO SUPABASE...")
        
        if not self.cliente_selecionado:
            self.mostrar_erro("Nenhum cliente selecionado")
            return
            
        username = self.cliente_selecionado['username']
        
        try:
            # 🔍 DEBUG ANTES DE SALVAR
            self.debug_limite(username, "ANTES de salvar")
            
            # 1. 🔥 SALVAR HORÁRIO NO SUPABASE
            self.salvar_horario_cliente_supabase()
            
            # 2. 🔥 SALVAR LIMITE NO SUPABASE
            try:
                limite_texto = self.input_limite.text.strip()
                limite_texto = limite_texto.replace('R$', '').replace(' ', '').replace(',', '.')
                
                partes = limite_texto.split('.')
                if len(partes) > 1:
                    limite_texto = partes[0] + '.' + ''.join(partes[1:])
                
                if not limite_texto or not limite_texto.replace('.', '').isdigit():
                    limite = self.sistema.limites_operacionais.get(username, 10000.00)
                else:
                    limite = float(limite_texto)
                
                if limite > 100000:
                    limite = 10000.00
                
                # 🔥 SALVAR NO SUPABASE
                sucesso = self.salvar_limite_supabase(username, limite)
                if sucesso:
                    self.sistema.limites_operacionais[username] = limite
                    print(f"✅ Limite salvo no Supabase: R$ {limite:.2f}")
                
            except ValueError as e:
                print(f"❌ Erro ao converter limite: {e}")
                
            # 3. 🔥 SALVAR PERMISSÃO NO SUPABASE
            permissao = self.switch_liberado.active
            sucesso = self.salvar_permissao_supabase(username, permissao)
            if sucesso:
                self.sistema.permissoes_cambio[username] = permissao
                print(f"✅ Permissão salva no Supabase: {permissao}")
            
            # 4. 🔥 SALVAR SPREADS NO SUPABASE
            spreads_configurados = len(self.cliente_selecionado['spreads'])
            if spreads_configurados > 0:
                sucesso = self.salvar_spreads_supabase(username, self.cliente_selecionado['spreads'])
                if sucesso:
                    print(f"✅ {spreads_configurados} spreads salvos no Supabase")
            
            # 5. 🔥🔥🔥 CORREÇÃO CRÍTICA: SALVAR TUDO NO SUPABASE
            sucesso_geral = self.sistema.salvar_cotacoes_supabase()
            
            if sucesso_geral:
                print("💾 TODAS AS ALTERAÇÕES SALVAS NO SUPABASE!")
            else:
                print("⚠️ Algumas alterações não foram salvas no Supabase")
            
            # 6. Resetar cores de alteração
            self.resetar_cores_alteracao()
            
            # 🔍 DEBUG APÓS SALVAR
            self.debug_limite(username, "APÓS salvar")
            
            # 7. Mostrar confirmação
            self.mostrar_sucesso("Todas as alterações foram salvas no Supabase!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar alterações no Supabase: {e}")
            self.mostrar_erro(f"Erro ao salvar: {str(e)}")

    def salvar_horario_cliente(self):
        """Salva o horário personalizado do cliente - VERSÃO FINAL CORRIGIDA"""
        if not self.cliente_selecionado:
            return
            
        username = self.cliente_selecionado['username']
        
        print(f"💾 SALVANDO HORÁRIO PARA {username}:")
        print(f"   Switch ativo: {self.switch_horario_personalizado.active}")
        
        # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: Verificar se o switch está ATIVO
        if self.switch_horario_personalizado.active:
            # 🔥 HORÁRIO PERSONALIZADO ATIVO - Salvar dados
            try:
                dias_texto = self.input_dias.text.strip()
                inicio = self.input_inicio.text.strip()
                fim = self.input_fim.text.strip()
                
                # Converter texto para dias da semana
                dias_semana = self.texto_para_dias_semana(dias_texto)
                
                if dias_semana and inicio and fim:
                    self.sistema.horarios_clientes[username] = {
                        'dias_semana': dias_semana,
                        'inicio': inicio,
                        'fim': fim
                    }
                    print(f"   ✅ Horário PERSONALIZADO salvo: {dias_semana} das {inicio} às {fim}")
                else:
                    print("   ❌ Dados de horário incompletos")
                    
            except Exception as e:
                print(f"   ❌ Erro ao salvar horário personalizado: {e}")
                
        else:
            # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: Switch DESATIVADO - REMOVER horário personalizado
            if username in self.sistema.horarios_clientes:
                del self.sistema.horarios_clientes[username]
                print(f"   🗑️  Horário personalizado REMOVIDO para {username} (voltou para padrão)")
            else:
                print(f"   ℹ️  {username} já usa horário padrão")
        
        # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: SALVAR NO ARQUIVO SEMPRE
        self.sistema.salvar_dados_cotacoes()
        print(f"   💾 Alterações de horário salvas no arquivo!")

    def validar_horario(self, horario):
        """Valida se o horário está no formato HH:MM"""
        try:
            if len(horario) != 5 or horario[2] != ':':
                return False
            horas = int(horario[:2])
            minutos = int(horario[3:])
            return 0 <= horas <= 23 and 0 <= minutos <= 59
        except:
            return False

    def exportar_para_csv(self, instance):
        """Exporta configurações para CSV"""
        try:
            filename = f"spreads_clientes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                header = ['Cliente', 'Email', 'Câmbio Liberado', 'Limite Operacional']
                for par in self.pares_moedas:
                    header.extend([f'{par} Compra%', f'{par} Venda%'])
                
                writer.writerow(header)
                
                # Dados
                for cliente in self.clientes:
                    linha = [
                        cliente['nome'],
                        cliente['email'],
                        'Sim' if cliente['cambio_liberado'] else 'Não',
                        f"{cliente['limite_operacional']:.2f}"
                    ]
                    
                    spreads_cliente = cliente['spreads']
                    for par in self.pares_moedas:
                        spread_par = spreads_cliente.get(par, {'compra': 0.5, 'venda': 0.5})
                        linha.extend([
                            f"{spread_par['compra']:.2f}",
                            f"{spread_par['venda']:.2f}"
                        ])
                    
                    writer.writerow(linha)
            
            self.mostrar_sucesso(f"Configurações exportadas para:\n{filename}")
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao exportar: {str(e)}")

    def salvar_dados_sistema(self):
        """Salva dados no sistema COM PERSISTÊNCIA REAL"""
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 SALVAR LIMITES ALTERADOS
            if self.cliente_selecionado:
                username = self.cliente_selecionado['username']
                try:
                    novo_limite = float(self.input_limite.text) if self.input_limite.text else 10000.00
                    sistema.limites_operacionais[username] = novo_limite
                    print(f"Limite salvo para {username}: R$ {novo_limite:.2f}")
                except ValueError:
                    print("Erro ao salvar limite - valor inválido")
            
            # Salvar tudo no arquivo
            sucesso = sistema.salvar_dados_cotacoes()
            
            if sucesso:
                print("Dados de cotações salvos com sucesso!")
                # Resetar cores dos inputs
                self.resetar_cores_inputs()
            else:
                print("Aviso: Dados não foram salvos")
                
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    def salvar_todas_alteracoes_pendentes(self):
        """Salva todas as alterações pendentes nos spreads"""
        for child in self.grid_spreads.children:
            for widget in child.children:
                if isinstance(widget, TextInput) and widget.background_color == [0.9, 0.9, 0.2, 1]:
                    # Encontrar o botão salvar correspondente
                    for sibling in child.children:
                        if isinstance(sibling, Button) and sibling.text == 'Salvar':
                            # Simular clique no botão salvar
                            sibling.dispatch('on_press')
                            break

    def salvar_alteracoes_pendentes(self):
        """Salva apenas as alterações pendentes - VERSÃO COMPLETA CORRIGIDA"""
        print("💾 SALVANDO ALTERAÇÕES PENDENTES...")
        
        if not self.cliente_selecionado:
            return True
            
        username = self.cliente_selecionado['username']
        
        try:
            alteracoes = False
            
            # 🔥 VERIFICAR ALTERAÇÃO NO HORÁRIO PERSONALIZADO
            tinha_horario_personalizado = username in self.sistema.horarios_clientes
            agora_tem_horario_personalizado = self.switch_horario_personalizado.active
            
            if tinha_horario_personalizado != agora_tem_horario_personalizado:
                print(f"⚠️  Alteração detectada no horário personalizado")
                self.salvar_horario_cliente()
                alteracoes = True
            elif agora_tem_horario_personalizado:
                # 🔥 Verificar se os dados do horário mudaram
                if username in self.sistema.horarios_clientes:
                    horario_antigo = self.sistema.horarios_clientes[username]
                    try:
                        dias_texto = self.input_dias.text.strip()
                        inicio = self.input_inicio.text.strip()
                        fim = self.input_fim.text.strip()
                        dias_semana = self.texto_para_dias_semana(dias_texto)
                        
                        if (horario_antigo['dias_semana'] != dias_semana or
                            horario_antigo['inicio'] != inicio or
                            horario_antigo['fim'] != fim):
                            print(f"⚠️  Alteração detectada nos dados do horário")
                            self.salvar_horario_cliente()
                            alteracoes = True
                    except:
                        pass
            
            # 🔥 VERIFICAR ALTERAÇÃO NO LIMITE (CORREÇÃO: usar limites_operacionais)
            limite_atual = self.cliente_selecionado.get('limite_operacional', 10000.0)
            try:
                limite_texto = self.input_limite.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                limite_novo = float(limite_texto) if limite_texto else 10000.0
                
                if abs(limite_atual - limite_novo) > 0.01:  # Tolerância para float
                    print(f"⚠️  Alteração detectada no limite: R$ {limite_atual:.2f} -> R$ {limite_novo:.2f}")
                    self.cliente_selecionado['limite_operacional'] = limite_novo
                    self.sistema.limites_operacionais[username] = limite_novo  # 🔥 CORREÇÃO AQUI
                    alteracoes = True
            except ValueError:
                print("❌ Erro ao converter limite novo")
            
            # 🔥 VERIFICAR ALTERAÇÃO NA PERMISSÃO (CORREÇÃO: usar permissoes_cambio)
            permissao_antiga = self.cliente_selecionado.get('cambio_liberado', False)
            permissao_nova = self.switch_liberado.active
            
            if permissao_antiga != permissao_nova:
                print(f"⚠️  Alteração detectada na permissão: {permissao_antiga} -> {permissao_nova}")
                self.cliente_selecionado['cambio_liberado'] = permissao_nova
                self.sistema.permissoes_cambio[username] = permissao_nova  # 🔥 CORREÇÃO AQUI
                alteracoes = True
            
            # 🔥 VERIFICAR ALTERAÇÃO NOS SPREADS
            spreads_alterados = False
            if hasattr(self, 'grid_spreads') and self.grid_spreads:
                for child in self.grid_spreads.children:
                    if hasattr(child, 'spread_data'):
                        par = child.spread_data['par']
                        spread_antigo = self.sistema.spreads_clientes.get(username, {}).get(par, 0.0)
                        
                        # Encontrar o input de spread
                        for widget in child.children:
                            if hasattr(widget, 'text') and not isinstance(widget, Button) and not isinstance(widget, Label):
                                try:
                                    spread_novo = float(widget.text.replace('%', '').strip())
                                    if abs(spread_antigo - spread_novo) > 0.001:  # Tolerância para float
                                        print(f"⚠️  Alteração detectada no spread {par}: {spread_antigo}% -> {spread_novo}%")
                                        if username not in self.sistema.spreads_clientes:
                                            self.sistema.spreads_clientes[username] = {}
                                        self.sistema.spreads_clientes[username][par] = spread_novo
                                        spreads_alterados = True
                                except ValueError:
                                    pass
            
            if spreads_alterados:
                alteracoes = True
                print("📊 Spreads alterados salvos")
            
            if alteracoes:
                # 🔥 SALVAR NO ARQUIVO SE HOUVE ALTERAÇÕES
                self.sistema.salvar_dados_cotacoes()
                print("✅ Alterações pendentes salvas")
                
                # 🔥 RESETAR CORES DE ALTERAÇÃO
                self.resetar_cores_inputs()
            else:
                print("ℹ️  Nenhuma alteração pendente para salvar")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar alterações pendentes: {e}")
            import traceback
            traceback.print_exc()
            return False

    def resetar_cores_inputs(self):
        """Reseta as cores dos inputs para o padrão após salvar - VERSÃO COMPLETA"""
        cor_normal = (0.20, 0.25, 0.33, 1)
        cor_desabilitado = (0.15, 0.15, 0.15, 0.5)
        
        # Resetar spreads
        for child in self.grid_spreads.children:
            for widget in child.children:
                if isinstance(widget, TextInput):
                    widget.background_color = cor_normal
        
        # Resetar limite
        if hasattr(self, 'input_limite'):
            self.input_limite.background_color = cor_normal
        
        # 🔥 🔥 🔥 Resetar horários baseado no estado do switch
        if hasattr(self, 'input_dias'):
            if self.switch_horario_personalizado.active:
                # Switch ON - cor normal
                self.input_dias.background_color = cor_normal
                self.input_inicio.background_color = cor_normal
                self.input_fim.background_color = cor_normal
            else:
                # Switch OFF - cor desabilitado
                self.input_dias.background_color = cor_desabilitado
                self.input_inicio.background_color = cor_desabilitado
                self.input_fim.background_color = cor_desabilitado
        
        print("✅ Cores dos inputs resetadas")

    def resetar_cores_alteracao(self):
        """Reseta cores de alteração - método auxiliar"""
        self.resetar_cores_inputs()

    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            text_size=(300, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=0.4,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Erro',
            content=content,
            size_hint=(None, None),
            size=(350, 150)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            text_size=(300, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=0.4,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Sucesso',
            content=content,
            size_hint=(None, None),
            size=(350, 150)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def voltar_dashboard(self, instance):
        print("🔍 Botão Voltar clicado - verificando alterações...")
        
        # 🔥 CORREÇÃO: Marcar que estamos saindo voluntariamente
        self._saindo_voluntariamente = True
        
        # APENAS verificar se há alterações não salvas
        if self.verificar_alteracoes_pendentes():
            print("🚨 Alterações pendentes detectadas - mostrando popup")
            self.mostrar_popup_confirmacao_voltar()
        else:
            print("✅ Nenhuma alteração pendente - voltando direto")
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 0.1)

    def verificar_alteracoes_pendentes(self):
        """Verifica se há alterações não salvas - VERSÃO CORRIGIDA"""
        try:
            print("🔍 VERIFICANDO ALTERAÇÕES PENDENTES...")
            
            if not self.cliente_selecionado:
                print("   Nenhum cliente selecionado")
                return False
            
            username = self.cliente_selecionado['username']
            cor_alterado = [0.95, 0.7, 0.3, 1]  # Laranja suave
            
            # 1. 🔥 VERIFICAR SPREADS ALTERADOS
            if hasattr(self, 'grid_spreads') and self.grid_spreads:
                for child in self.grid_spreads.children:
                    for widget in child.children:
                        if isinstance(widget, TextInput):
                            if widget.background_color == cor_alterado:
                                print("   Alteração detectada em spreads")
                                return True
            
            # 2. 🔥 VERIFICAR LIMITE ALTERADO - CORREÇÃO: usar limites_operacionais
            if hasattr(self, 'input_limite'):
                limite_atual = self.sistema.limites_operacionais.get(username, 10000.00)
                try:
                    limite_texto = self.input_limite.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                    limite_digitado = float(limite_texto) if limite_texto else 10000.00
                    if abs(limite_digitado - limite_atual) > 0.01:  # Tolerância para float
                        print(f"   Alteração detectada em limite: {limite_atual} -> {limite_digitado}")
                        return True
                except ValueError:
                    pass
            
            # 3. 🔥 VERIFICAR PERMISSÃO ALTERADA - CORREÇÃO: usar permissoes_cambio
            permissao_atual = self.sistema.permissoes_cambio.get(username, False)
            permissao_atual_bool = bool(permissao_atual)
            permissao_nova = self.switch_liberado.active
            
            if permissao_atual_bool != permissao_nova:
                print(f"   Alteração detectada em permissão: {permissao_atual_bool} -> {permissao_nova}")
                return True
            
            # 4. 🔥 🔥 🔥 VERIFICAR MUDANÇA NO SWITCH DE HORÁRIO
            tinha_horario_personalizado = username in self.sistema.horarios_clientes
            agora_tem_horario_personalizado = self.switch_horario_personalizado.active
            
            print(f"   VERIFICAÇÃO SWITCH HORÁRIO:")
            print(f"      Tinha personalizado: {tinha_horario_personalizado}")
            print(f"      Agora tem personalizado: {agora_tem_horario_personalizado}")
            
            if tinha_horario_personalizado != agora_tem_horario_personalizado:
                print(f"   ⚠️  Alteração detectada no SWITCH de horário!")
                return True
            
            # 5. 🔥 VERIFICAR HORÁRIOS PERSONALIZADOS ALTERADOS (apenas se switch ON)
            if (agora_tem_horario_personalizado and
                hasattr(self, 'input_dias') and hasattr(self, 'input_inicio') and hasattr(self, 'input_fim')):
                
                # Verificar se algum campo de horário está com cor de alteração
                if (self.input_dias.background_color == cor_alterado or
                    self.input_inicio.background_color == cor_alterado or
                    self.input_fim.background_color == cor_alterado):
                    print("   Alteração detectada em horário comercial (cor)")
                    return True
                
                # Verificar se valores foram modificados em relação ao salvo
                if username in self.sistema.horarios_clientes:
                    horario_atual = self.sistema.horarios_clientes[username]
                    dias_atual = horario_atual['dias_semana']
                    inicio_atual = horario_atual['inicio']
                    fim_atual = horario_atual['fim']
                    
                    # 🔥 CORREÇÃO: Usar o método correto para obter dias
                    try:
                        dias_texto = self.input_dias.text.strip()
                        dias_digitado = self.texto_para_dias_semana(dias_texto)
                        inicio_digitado = self.input_inicio.text.strip()
                        fim_digitado = self.input_fim.text.strip()
                        
                        if (dias_digitado != dias_atual or 
                            inicio_digitado != inicio_atual or 
                            fim_digitado != fim_atual):
                            print(f"   Alteração detectada em horário: {dias_atual}->{dias_digitado}, {inicio_atual}->{inicio_digitado}, {fim_atual}->{fim_digitado}")
                            return True
                    except Exception as e:
                        print(f"   ❌ Erro ao comparar horários: {e}")
            
            print("   ✅ Nenhuma alteração pendente")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar alterações: {e}")
            import traceback
            traceback.print_exc()
            return False

    def mostrar_popup_confirmacao_voltar(self):
        """Mostra popup de confirmação para salvar antes de voltar - VERSÃO CORRIGIDA"""
        print("🎯🎯🎯 MOSTRAR_POPUP_CONFIRMACAO_VOLTAR CHAMADO! 🎯🎯🎯")
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_confirmacao = Label(
            text='EXISTEM ALTERAÇÕES NÃO SALVAS!\n\nDeseja salvar antes de voltar?',
            color=(1, 1, 1, 1),
            text_size=(300, None),
            halign='center'
        )
        
        botoes = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.4)
        
        btn_voltar_sem_salvar = Button(
            text='Voltar sem Salvar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_salvar_voltar = Button(
            text='Salvar e Voltar',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes.add_widget(btn_voltar_sem_salvar)
        botoes.add_widget(btn_cancelar)
        botoes.add_widget(btn_salvar_voltar)
        
        content.add_widget(lbl_confirmacao)
        content.add_widget(botoes)
        
        popup = Popup(
            title='ALTERAÇÕES NÃO SALVAS',
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False
        )
        
        def voltar_sem_salvar(btn):
            print("📤 Voltando sem salvar alterações...")
            # 🔥 CORREÇÃO: Marcar que estamos saindo voluntariamente
            self._saindo_voluntariamente = True
            popup.dismiss()
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 0.1)
        
        def cancelar(btn):
            print("❌ Cancelando volta...")
            popup.dismiss()
        
        def salvar_e_voltar(btn):
            print("💾 SALVAR E VOLTAR: Iniciando salvamento completo...")
            
            # 🔥 CORREÇÃO: Marcar que estamos saindo voluntariamente
            self._saindo_voluntariamente = True
            
            # 🔥 SALVAMENTO COMPLETO E GARANTIDO
            self.salvar_todas_alteracoes_silencioso()
            
            print("SALVAR E VOLTAR: Salvamento concluído, voltando...")
            popup.dismiss()
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 0.1)
        
        btn_voltar_sem_salvar.bind(on_press=voltar_sem_salvar)
        btn_cancelar.bind(on_press=cancelar)
        btn_salvar_voltar.bind(on_press=salvar_e_voltar)
        
        print("ABRINDO POPUP...")
        popup.open()
        print("POPUP ABERTO!")

    def debug_limite(self, username, acao):
        """Função de debug para rastrear alterações no limite - VERSÃO MELHORADA"""
        if hasattr(self, 'sistema') and hasattr(self.sistema, 'limites_operacionais'):
            limite_atual = self.sistema.limites_operacionais.get(username, 10000.00)
            print(f"🔍 DEBUG LIMITE [{acao}]:")
            print(f"   Cliente: {username}")
            print(f"   Limite atual no sistema: R$ {limite_atual:,.2f}")
            if hasattr(self, 'input_limite'):
                print(f"   Limite no input: '{self.input_limite.text}'")
            
            # 🔥 NOVO: Mostrar todos os limites para debug
            print(f"   Todos os limites no sistema:")
            for user, lim in self.sistema.limites_operacionais.items():
                print(f"      {user}: R$ {lim:,.2f}")
            print("   " + "="*50)

    def salvar_todas_alteracoes_silencioso(self):
        """Salva todas as alterações sem mostrar popup - VERSÃO SUPABASE"""
        print("🔍 SALVAMENTO SILENCIOSO NO SUPABASE: Iniciando...")
        
        try:
            sistema = App.get_running_app().sistema
            
            # 1. SALVAR HORÁRIOS
            if self.cliente_selecionado and hasattr(self, 'switch_horario_personalizado'):
                self.salvar_horario_cliente_supabase()
                print("⏰ Horários salvos")
            
            # 2. 🔥 CORREÇÃO: Salvar limite COM VALIDAÇÃO
            if self.cliente_selecionado and hasattr(self, 'input_limite'):
                username = self.cliente_selecionado['username']
                try:
                    limite_texto = self.input_limite.text.strip()
                    limite_texto = limite_texto.replace('R$', '').replace(' ', '').replace(',', '.')
                    
                    partes = limite_texto.split('.')
                    if len(partes) > 1:
                        limite_texto = partes[0] + '.' + ''.join(partes[1:])
                    
                    if not limite_texto or not limite_texto.replace('.', '').isdigit():
                        novo_limite = sistema.limites_operacionais.get(username, 10000.00)
                    else:
                        novo_limite = float(limite_texto)
                    
                    # Validar valor
                    if novo_limite > 100000:
                        novo_limite = 10000.00
                    
                    # Só atualizar se for diferente
                    limite_atual = sistema.limites_operacionais.get(username, 10000.00)
                    if abs(novo_limite - limite_atual) > 0.01:
                        sistema.limites_operacionais[username] = novo_limite
                        print(f"✅ Limite salvo silenciosamente: R$ {novo_limite:.2f}")
                    else:
                        print(f"ℹ️ Limite não alterado no salvamento silencioso")
                        
                except ValueError as e:
                    print(f"❌ Erro ao salvar limite silenciosamente: {e}")
            
            # 3. SALVAR PERMISSÃO
            if self.cliente_selecionado and hasattr(self, 'switch_liberado'):
                username = self.cliente_selecionado['username']
                sistema.permissoes_cambio[username] = self.switch_liberado.active
                print(f"✅ Permissão salva silenciosamente: {self.switch_liberado.active}")
            
            # 4. SALVAR SPREADS INDIVIDUAIS
            spreads_salvos = 0
            for child in self.grid_spreads.children:
                for widget in child.children:
                    if (isinstance(widget, TextInput) and 
                        hasattr(widget, 'background_color') and
                        widget.background_color == [0.95, 0.7, 0.3, 1]):  # Laranja = alterado
                        
                        # Encontrar o botão salvar
                        for sibling in child.children:
                            if isinstance(sibling, Button) and sibling.text == 'Salvar':
                                # Simular clique para salvar este spread
                                sibling.dispatch('on_press')
                                spreads_salvos += 1
                                break
            
            print(f"📊 {spreads_salvos} spreads salvos silenciosamente")
            
            # 5. 🔥🔥🔥 SALVAR TUDO NO SUPABASE
            sucesso = sistema.salvar_cotacoes_supabase()
            if sucesso:
                print("💾 Todas as cotações salvas no Supabase (silencioso)")
                self.resetar_cores_inputs()
            else:
                print("⚠️ Falha ao salvar no Supabase (silencioso)")
                
        except Exception as e:
            print(f"❌ Erro no salvamento silencioso: {e}")
            import traceback
            traceback.print_exc()


    # ========== SEÇÃO HORÁRIO COMERCIAL ==========

    
    def criar_secao_horario_comercial(self):
        """Cria seção de configuração de horário comercial"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=8)
        
        with container.canvas.before:
            Color(0.12, 0.16, 0.23, 1)
            container.rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[8,])
        container.bind(pos=self._atualizar_container_rect, size=self._atualizar_container_rect)
        
        # Título
        lbl_titulo = Label(
            text='HORÁRIO COMERCIAL PERSONALIZADO',
            font_size='12sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        
        # Checkbox para usar horário personalizado
        linha_checkbox = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=8, padding=[10, 0])
        
        # 🔥 CORREÇÃO: NÃO definir valor inicial aqui - será definido no carregar_horario_cliente
        self.switch_horario_personalizado = Switch(
            # ❌ REMOVER: active=False - isso causa o problema
            size_hint_x=0.2
        )
        self.switch_horario_personalizado.bind(active=self.toggle_horario_personalizado)
        
        lbl_checkbox = Label(
            text='Usar horário personalizado',
            color=(1, 1, 1, 1),
            size_hint_x=0.8,
            text_size=(None, None),
            halign='left',
            font_size='13sp'
        )
        
        linha_checkbox.add_widget(self.switch_horario_personalizado)
        linha_checkbox.add_widget(lbl_checkbox)
        
        # Linha de horários
        linha_horarios = BoxLayout(orientation='horizontal', size_hint_y=0.45, spacing=10, padding=[10, 5])
        
        # Dias da semana
        lbl_dias = Label(
            text='Dias:',
            color=(1, 1, 1, 1),
            size_hint_x=0.2,
            text_size=(None, None),
            halign='left',
            font_size='13sp'
        )
        
        self.input_dias = TextInput(
            text='Seg-Sex',  # Valor padrão, será sobrescrito se houver horário personalizado
            size_hint_x=0.3,
            multiline=False,
            background_color=(0.15, 0.15, 0.15, 0.5),  # Inicialmente desabilitado
            foreground_color=(1, 1, 1, 1),
            font_size='13sp',
            padding=[8, 8],
            readonly=True,
            disabled=True  # Inicialmente desabilitado
        )
        
        # Horário início
        lbl_inicio = Label(
            text='Início:',
            color=(1, 1, 1, 1),
            size_hint_x=0.15,
            text_size=(None, None),
            halign='center',
            font_size='13sp'
        )
        
        self.input_inicio = TextInput(
            text='10:00',  # Valor padrão
            size_hint_x=0.15,
            multiline=False,
            background_color=(0.15, 0.15, 0.15, 0.5),  # Inicialmente desabilitado
            foreground_color=(1, 1, 1, 1),
            font_size='13sp',
            padding=[8, 8],
            halign='center',
            disabled=True  # Inicialmente desabilitado
        )
        self.input_inicio.bind(text=self.on_horario_change)
        
        # Horário fim
        lbl_fim = Label(
            text='Fim:',
            color=(1, 1, 1, 1),
            size_hint_x=0.1,
            text_size=(None, None),
            halign='center',
            font_size='13sp'
        )
        
        self.input_fim = TextInput(
            text='15:00',  # Valor padrão
            size_hint_x=0.15,
            multiline=False,
            background_color=(0.15, 0.15, 0.15, 0.5),  # Inicialmente desabilitado
            foreground_color=(1, 1, 1, 1),
            font_size='13sp',
            padding=[8, 8],
            halign='center',
            disabled=True  # Inicialmente desabilitado
        )
        self.input_fim.bind(text=self.on_horario_change)
        
        # Botão para selecionar dias
        btn_selecionar_dias = Button(
            text='Selecionar\nDias',
            size_hint_x=0.25,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='11sp',
            disabled=True  # Inicialmente desabilitado
        )
        btn_selecionar_dias.bind(on_press=self.mostrar_selecao_dias)
        
        linha_horarios.add_widget(lbl_dias)
        linha_horarios.add_widget(self.input_dias)
        linha_horarios.add_widget(lbl_inicio)
        linha_horarios.add_widget(self.input_inicio)
        linha_horarios.add_widget(lbl_fim)
        linha_horarios.add_widget(self.input_fim)
        linha_horarios.add_widget(btn_selecionar_dias)
        
        # Adicionar tudo ao container
        container.add_widget(lbl_titulo)
        container.add_widget(linha_checkbox)
        container.add_widget(linha_horarios)
        
        # 🔥 CORREÇÃO: NÃO chamar toggle_horario_personalizado aqui
        # O estado será definido quando um cliente for selecionado
        
        return container
    
    def toggle_horario_personalizado(self, instance, value):
        """Habilita/desabilita os controles de horário personalizado - VERSÃO CORRIGIDA"""
        print(f"🔧 TOGGLE HORÁRIO PERSONALIZADO: {value}")
        
        # 🔥 CORREÇÃO: Encontrar e habilitar/desabilitar o botão de seleção de dias
        btn_selecionar_dias = None
        
        # Procurar o botão na hierarquia da interface
        def encontrar_botao_selecionar_dias(widget):
            nonlocal btn_selecionar_dias
            if hasattr(widget, 'children'):
                for child in widget.children:
                    if (hasattr(child, 'text') and 'Selecionar\nDias' in child.text):
                        btn_selecionar_dias = child
                        return
                    encontrar_botao_selecionar_dias(child)
        
        encontrar_botao_selecionar_dias(self)
        
        if value:
            # 🔥 HORÁRIO PERSONALIZADO ATIVADO
            self.input_dias.background_color = [0.20, 0.25, 0.33, 1]
            self.input_inicio.background_color = [0.20, 0.25, 0.33, 1]
            self.input_fim.background_color = [0.20, 0.25, 0.33, 1]
            
            self.input_dias.disabled = False
            self.input_inicio.disabled = False
            self.input_fim.disabled = False
            
            # 🔥 CORREÇÃO: Habilitar o botão de seleção de dias
            if btn_selecionar_dias:
                btn_selecionar_dias.disabled = False
                btn_selecionar_dias.background_color = (0.23, 0.51, 0.96, 1)
            
            print("✅ Controles habilitados - valores mantidos")
            
        else:
            # 🔥 HORÁRIO PERSONALIZADO DESATIVADO
            self.input_dias.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_inicio.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_fim.background_color = [0.15, 0.15, 0.15, 0.5]
            
            self.input_dias.disabled = True
            self.input_inicio.disabled = True
            self.input_fim.disabled = True
            
            # 🔥 CORREÇÃO: Desabilitar o botão de seleção de dias
            if btn_selecionar_dias:
                btn_selecionar_dias.disabled = True
                btn_selecionar_dias.background_color = (0.15, 0.15, 0.15, 0.5)
            
            # 🔥 CORREÇÃO: SÓ DEFINIR PADRÃO SE ESTIVER VAZIO
            if not self.input_dias.text or self.input_dias.text == 'Seg-Sex':
                self.input_dias.text = 'Seg-Sex'
                self.input_inicio.text = '10:00'
                self.input_fim.text = '15:00'
                print("🔄 Horário redefinido para padrão: Seg-Sex das 10:00 às 15:00")
            else:
                print("✅ Valores mantidos - apenas controles desabilitados")
        
        # 🔥 CORREÇÃO CRÍTICA: MARCAR COMO ALTERAÇÃO PENDENTE
        if self.cliente_selecionado:
            username = self.cliente_selecionado['username']
            
            # Verificar se houve mudança real no estado do horário personalizado
            tinha_horario_personalizado = username in self.sistema.horarios_clientes
            agora_tem_horario_personalizado = value
            
            print(f"🔍 DETECÇÃO ALTERAÇÃO HORÁRIO:")
            print(f"   Antes: {tinha_horario_personalizado} (tinha personalizado)")
            print(f"   Agora: {agora_tem_horario_personalizado} (tem personalizado)")
            
            # Se o estado mudou, marcar como alteração pendente
            if tinha_horario_personalizado != agora_tem_horario_personalizado:
                print(f"   ⚠️  ALTERAÇÃO DETECTADA NO SWITCH!")
                # 🔥 CORREÇÃO: Marcar visualmente que houve alteração
                cor_alterado = [0.95, 0.7, 0.3, 1]  # Laranja
                self.input_dias.background_color = cor_alterado
                self.input_inicio.background_color = cor_alterado  
                self.input_fim.background_color = cor_alterado
                
                # 🔥 CORREÇÃO: Forçar o salvamento imediato se for uma remoção
                if not value and tinha_horario_personalizado:
                    print(f"   💾 Salvando remoção de horário personalizado...")
                    self.salvar_horario_cliente()

    def on_horario_change(self, instance, value):
        """Quando um horário é alterado - marca como modificado"""
        if self.switch_horario_personalizado.active:
            instance.background_color = [0.95, 0.7, 0.3, 1]  # Laranja - alterado

    def carregar_horario_cliente(self):
        """Carrega o horário personalizado do cliente selecionado - VERSÃO CORRIGIDA"""
        if not self.cliente_selecionado:
            return
            
        username = self.cliente_selecionado['username']
        
        print(f"🔍 CARREGANDO HORÁRIO PARA {username}:")
        print(f"   Horários no sistema: {list(self.sistema.horarios_clientes.keys())}")
        
        # 🔥 CORREÇÃO: Encontrar o botão de seleção de dias
        btn_selecionar_dias = None
        
        def encontrar_botao_selecionar_dias(widget):
            nonlocal btn_selecionar_dias
            if hasattr(widget, 'children'):
                for child in widget.children:
                    if (hasattr(child, 'text') and 'Selecionar\nDias' in child.text):
                        btn_selecionar_dias = child
                        return
                    encontrar_botao_selecionar_dias(child)
        
        encontrar_botao_selecionar_dias(self)
        
        if username in self.sistema.horarios_clientes:
            # 🔥 CLIENTE TEM HORÁRIO PERSONALIZADO
            horario = self.sistema.horarios_clientes[username]
            dias_semana = horario['dias_semana']
            inicio = horario['inicio']
            fim = horario['fim']
            
            print(f"   📥 Dados encontrados: {dias_semana} das {inicio} às {fim}")
            
            # Converter dias para texto
            dias_texto = self.dias_semana_para_texto(dias_semana)
            
            # 🔥 CORREÇÃO: ATUALIZAR INTERFACE PRIMEIRO
            self.input_dias.text = dias_texto
            self.input_inicio.text = inicio
            self.input_fim.text = fim
            
            # 🔥 DEPOIS configurar o switch SEM disparar o evento
            # Desvincular temporariamente o evento para evitar loop
            self.switch_horario_personalizado.unbind(active=self.toggle_horario_personalizado)
            self.switch_horario_personalizado.active = True
            # Re-vincular o evento
            self.switch_horario_personalizado.bind(active=self.toggle_horario_personalizado)
            
            # Habilitar controles
            self.input_dias.disabled = False
            self.input_inicio.disabled = False
            self.input_fim.disabled = False
            self.input_dias.background_color = [0.20, 0.25, 0.33, 1]
            self.input_inicio.background_color = [0.20, 0.25, 0.33, 1]
            self.input_fim.background_color = [0.20, 0.25, 0.33, 1]
            
            # 🔥 CORREÇÃO: Habilitar botão de seleção de dias
            if btn_selecionar_dias:
                btn_selecionar_dias.disabled = False
                btn_selecionar_dias.background_color = (0.23, 0.51, 0.96, 1)
            
            print(f"✅ Interface ATUALIZADA: {dias_texto} das {inicio} às {fim}")
            
        else:
            # 🔥 CLIENTE USA HORÁRIO PADRÃO
            print(f"   📥 Nenhum horário personalizado encontrado - usando padrão")
            
            self.input_dias.text = 'Seg-Sex'
            self.input_inicio.text = '10:00'
            self.input_fim.text = '15:00'
            
            # 🔥 CONFIGURAR SWITCH DESATIVADO SEM DISPARAR EVENTO
            # Desvincular temporariamente o evento para evitar loop
            self.switch_horario_personalizado.unbind(active=self.toggle_horario_personalizado)
            self.switch_horario_personalizado.active = False
            # Re-vincular o evento
            self.switch_horario_personalizado.bind(active=self.toggle_horario_personalizado)
            
            # Manter controles desabilitados
            self.input_dias.disabled = True
            self.input_inicio.disabled = True
            self.input_fim.disabled = True
            self.input_dias.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_inicio.background_color = [0.15, 0.15, 0.15, 0.5]
            self.input_fim.background_color = [0.15, 0.15, 0.15, 0.5]
            
            # 🔥 CORREÇÃO: Desabilitar botão de seleção de dias
            if btn_selecionar_dias:
                btn_selecionar_dias.disabled = True
                btn_selecionar_dias.background_color = (0.15, 0.15, 0.15, 0.5)
            
            print(f"✅ Interface configurada para PADRÃO")

    def dias_semana_para_texto(self, dias_semana):
        """Converte lista de dias para texto amigável"""
        dias_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        if dias_semana == [0, 1, 2, 3, 4]:
            return 'Seg-Sex'
        elif dias_semana == [0, 1, 2, 3, 4, 5]:
            return 'Seg-Sáb'
        elif dias_semana == list(range(7)):
            return 'Todos'
        else:
            dias_selecionados = [dias_nomes[d] for d in sorted(dias_semana)]
            return ', '.join(dias_selecionados)
        
    def mostrar_selecao_dias(self, instance):
        """Mostra popup para seleção de dias da semana - VERSÃO CORRIGIDA"""
        from kivy.uix.gridlayout import GridLayout
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_titulo = Label(
            text='Selecione os dias da semana:\n(Clique para selecionar/deselecionar)',
            color=(1, 1, 1, 1),
            font_size='14sp',
            size_hint_y=0.2,
            text_size=(350, None),
            halign='center'
        )
        
        # Grid para os botões de dias
        grid_dias = GridLayout(cols=3, spacing=10, size_hint_y=0.6)
        
        dias_nomes = [
            ('Segunda', 0), ('Terça', 1), ('Quarta', 2),
            ('Quinta', 3), ('Sexta', 4), ('Sábado', 5),
            ('Domingo', 6)
        ]
        
        self.botoes_dias = {}
        
        # Obter dias atualmente selecionados
        dias_selecionados = self.obter_dias_selecionados()
        
        for nome, numero in dias_nomes:
            # 🔥 CORREÇÃO: Usar Button normal com toggle manual
            btn = Button(
                text=nome,
                background_color=(0.23, 0.51, 0.96, 1) if numero in dias_selecionados else (0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1),
                font_size='12sp',
                size_hint_y=None,
                height=dp(40)
            )
            btn.numero_dia = numero
            btn.selecionado = (numero in dias_selecionados)
            
            # 🔥 CORREÇÃO: Função para alternar estado
            def criar_callback(botao):
                def alternar_selecao(inst):
                    botao.selecionado = not botao.selecionado
                    if botao.selecionado:
                        botao.background_color = (0.23, 0.51, 0.96, 1)  # Azul - selecionado
                    else:
                        botao.background_color = (0.20, 0.25, 0.33, 1)  # Cinza - não selecionado
                return alternar_selecao
            
            btn.bind(on_press=criar_callback(btn))
            self.botoes_dias[numero] = btn
            grid_dias.add_widget(btn)
        
        # Botões de ação
        botoes_acao = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Confirmar',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        # 🔥 BOTÃO NOVO: Selecionar Todos
        btn_todos = Button(
            text='Selecionar Todos',
            background_color=(0.5, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        
        btn_nenhum = Button(
            text='Limpar Todos', 
            background_color=(0.8, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        
        botoes_selecao = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=0.15)
        botoes_selecao.add_widget(btn_todos)
        botoes_selecao.add_widget(btn_nenhum)
        
        botoes_acao.add_widget(btn_cancelar)
        botoes_acao.add_widget(btn_confirmar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(grid_dias)
        content.add_widget(botoes_selecao)  # 🔥 Adicionar botões de seleção em massa
        content.add_widget(botoes_acao)
        
        popup = Popup(
            title='Selecionar Dias',
            content=content,
            size_hint=(None, None),
            size=(420, 450)  # 🔥 Aumentei a altura para caber os novos botões
        )
        
        def confirmar_dias(btn):
            dias_selecionados = []
            for numero, btn_dia in self.botoes_dias.items():
                if btn_dia.selecionado:
                    dias_selecionados.append(numero)
            
            # Ordenar os dias
            dias_selecionados.sort()
            
            # 🔥 CORREÇÃO: Se nenhum dia selecionado, usar padrão
            if not dias_selecionados:
                dias_selecionados = [0, 1, 2, 3, 4]  # Seg-Sex padrão
                self.mostrar_sucesso("Nenhum dia selecionado. Usando padrão Segunda-Sexta.")
            
            # Atualizar o campo de texto
            self.input_dias.text = self.dias_semana_para_texto(dias_selecionados)
            
            # Marcar como alterado
            self.input_dias.background_color = [0.95, 0.7, 0.3, 1]
            
            popup.dismiss()
        
        def selecionar_todos(btn):
            """Seleciona todos os dias"""
            for numero, btn_dia in self.botoes_dias.items():
                btn_dia.selecionado = True
                btn_dia.background_color = (0.23, 0.51, 0.96, 1)
        
        def limpar_todos(btn):
            """Deseleciona todos os dias"""
            for numero, btn_dia in self.botoes_dias.items():
                btn_dia.selecionado = False
                btn_dia.background_color = (0.20, 0.25, 0.33, 1)
        
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_confirmar.bind(on_press=confirmar_dias)
        btn_todos.bind(on_press=selecionar_todos)
        btn_nenhum.bind(on_press=limpar_todos)
        
        popup.open()

    def obter_dias_selecionados(self):
        """Obtém os dias atualmente selecionados do campo de texto"""
        texto_dias = self.input_dias.text
        
        if texto_dias == 'Seg-Sex':
            return [0, 1, 2, 3, 4]
        elif texto_dias == 'Seg-Sáb':
            return [0, 1, 2, 3, 4, 5]
        elif texto_dias == 'Todos':
            return [0, 1, 2, 3, 4, 5, 6]
        else:
            # Tentar parsear dias individuais
            dias_nomes = {'Seg': 0, 'Ter': 1, 'Qua': 2, 'Qui': 3, 'Sex': 4, 'Sáb': 5, 'Dom': 6}
            dias_selecionados = []
            for parte in texto_dias.split(','):
                parte = parte.strip()
                if parte in dias_nomes:
                    dias_selecionados.append(dias_nomes[parte])
            return dias_selecionados if dias_selecionados else [0, 1, 2, 3, 4]
        
    def texto_para_dias_semana(self, texto_dias):
        """Converte texto para lista de dias da semana"""
        if texto_dias == 'Seg-Sex':
            return [0, 1, 2, 3, 4]
        elif texto_dias == 'Seg-Sáb':
            return [0, 1, 2, 3, 4, 5]
        elif texto_dias == 'Todos':
            return [0, 1, 2, 3, 4, 5, 6]
        else:
            # Tentar parsear dias individuais
            dias_nomes = {'Seg': 0, 'Ter': 1, 'Qua': 2, 'Qui': 3, 'Sex': 4, 'Sáb': 5, 'Dom': 6}
            dias_selecionados = []
            for parte in texto_dias.split(','):
                parte = parte.strip()
                if parte in dias_nomes:
                    dias_selecionados.append(dias_nomes[parte])
            return dias_selecionados if dias_selecionados else [0, 1, 2, 3, 4]

    def salvar_horario_cliente_supabase(self):
        """Salva horário personalizado no Supabase"""
        if not self.cliente_selecionado:
            return
            
        username = self.cliente_selecionado['username']
        
        try:
            sistema = App.get_running_app().sistema
            
            if self.switch_horario_personalizado.active:
                # Salvar horário personalizado
                dias_texto = self.input_dias.text.strip()
                inicio = self.input_inicio.text.strip()
                fim = self.input_fim.text.strip()
                dias_semana = self.texto_para_dias_semana(dias_texto)
                
                if dias_semana and inicio and fim:
                    horario_data = {
                        'dias_semana': dias_semana,
                        'inicio': inicio,
                        'fim': fim
                    }
                    
                    # 🔥 SALVAR NO SUPABASE
                    sucesso = sistema.supabase.salvar_horario_cliente(username, horario_data)
                    if sucesso:
                        sistema.horarios_clientes[username] = horario_data
                        print(f"✅ Horário salvo no Supabase: {dias_semana} das {inicio} às {fim}")
                    
            else:
                # Remover horário personalizado
                sucesso = sistema.supabase.salvar_horario_cliente(username, None)  # None para remover
                if sucesso and username in sistema.horarios_clientes:
                    del sistema.horarios_clientes[username]
                    print(f"✅ Horário removido do Supabase")
                    
        except Exception as e:
            print(f"❌ Erro ao salvar horário no Supabase: {e}")

    def salvar_limite_supabase(self, username, limite):
        """Salva limite operacional no Supabase"""
        try:
            sistema = App.get_running_app().sistema
            return sistema.supabase.salvar_limite_operacional(username, limite)
        except Exception as e:
            print(f"❌ Erro ao salvar limite no Supabase: {e}")
            return False

    def salvar_permissao_supabase(self, username, permissao):
        """Salva permissão de câmbio no Supabase"""
        try:
            sistema = App.get_running_app().sistema
            return sistema.supabase.salvar_permissao_cambio(username, permissao)
        except Exception as e:
            print(f"❌ Erro ao salvar permissão no Supabase: {e}")
            return False

    def salvar_spreads_supabase(self, username, spreads):
        """Salva spreads do cliente no Supabase"""
        try:
            sistema = App.get_running_app().sistema
            return sistema.supabase.salvar_spreads_cliente(username, spreads)
        except Exception as e:
            print(f"❌ Erro ao salvar spreads no Supabase: {e}")
            return False





    def debug_horarios(self, instance):
        """Método para debug dos horários"""
        print("=== 🔍 DEBUG MANUAL HORÁRIOS ===")
        print(f"Cliente selecionado: {self.cliente_selecionado['username'] if self.cliente_selecionado else 'Nenhum'}")
        print(f"Horários no sistema: {self.sistema.horarios_clientes}")
        print(f"Switch ativo: {self.switch_horario_personalizado.active}")
        print(f"Input dias: {self.input_dias.text}")
        print(f"Input início: {self.input_inicio.text}")
        print(f"Input fim: {self.input_fim.text}")
        print("=== 🎯 FIM DEBUG ===")

    def debug_limite(self, username, acao):
        """Função de debug para rastrear alterações no limite"""
        if hasattr(self, 'sistema') and hasattr(self.sistema, 'limites_operacionais'):
            limite_atual = self.sistema.limites_operacionais.get(username, 10000.00)
            print(f"🔍 DEBUG LIMITE [{acao}]:")
            print(f"   Cliente: {username}")
            print(f"   Limite atual no sistema: R$ {limite_atual:,.2f}")
            if hasattr(self, 'input_limite'):
                print(f"   Limite no input: {self.input_limite.text}")
            print(f"   Limites no sistema: {dict(list(self.sistema.limites_operacionais.items())[:3])}")  # Mostra só os 3 primeiros

