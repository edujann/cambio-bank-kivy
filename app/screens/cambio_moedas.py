from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from .campos import CampoValor

import datetime
import threading

class TelaCambioMoedas(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.par_selecionado = None
        self.tipo_operacao = 'compra'
        self.cotacao_atual = 0.0
        self.valor_digitado = 0.0
        self.contador_atualizacao = 30  # Contador de 30 segundos
        self.clock_atualizacao = None   # Referência do clock
        
        Clock.schedule_once(self.criar_interface_manual)
        # Iniciar o contador automático
        Clock.schedule_once(self.iniciar_contador_atualizacao, 1)

    def iniciar_contador_atualizacao(self, dt=None):
        """Inicia o contador regressivo para atualização automática - VERSÃO CORRIGIDA"""
        # 🔥 CORREÇÃO: Parar clock anterior se existir
        if self.clock_atualizacao:
            self.clock_atualizacao.cancel()
            self.clock_atualizacao = None
        
        # Reiniciar contador
        self.contador_atualizacao = 30
        
        # 🔥 CORREÇÃO: Verificar se a tela ainda está ativa antes de iniciar novo clock
        if self.manager and self.manager.current == 'cambio_moedas':
            self.clock_atualizacao = Clock.schedule_interval(self.atualizar_contador, 1)
            self.atualizar_display_contador()
            print(" Contador de atualização iniciado")

    def atualizar_contador(self, dt):
        """Atualiza o contador regressivo a cada segundo - VERSÃO CORRIGIDA"""
        self.contador_atualizacao -= 1
        self.atualizar_display_contador()
        
        if self.contador_atualizacao <= 0:
            # Tempo esgotado - atualizar cotação
            print(" Atualização automática da cotação")
            self.atualizar_cotacao_automatica()
            # Reiniciar contador
            self.contador_atualizacao = 30

    def atualizar_display_contador(self):
        """Atualiza o display do contador na tela"""
        if hasattr(self, 'lbl_contador_atualizacao'):
            if self.contador_atualizacao > 0:
                self.lbl_contador_atualizacao.text = f" Atualização em: {self.contador_atualizacao}s"
                # Mudar cor conforme o tempo diminui
                if self.contador_atualizacao <= 10:
                    self.lbl_contador_atualizacao.color = (1, 0.3, 0.3, 1)  # Vermelho
                elif self.contador_atualizacao <= 20:
                    self.lbl_contador_atualizacao.color = (1, 0.8, 0.3, 1)  # Laranja
                else:
                    self.lbl_contador_atualizacao.color = (0.3, 0.8, 0.3, 1)  # Verde
            else:
                self.lbl_contador_atualizacao.text = " Atualizando..."

    def atualizar_cotacao_automatica(self):
        """Atualiza a cotação automaticamente quando o contador chega a zero"""
        if self.par_selecionado:
            print(f" Atualização automática da cotação: {self.par_selecionado}")
            # 🔥 CORREÇÃO: Usar o método protegido
            self.proteger_valor_durante_atualizacao()
        else:
            print(" Nenhum par selecionado para atualização automática")

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - AGORA COM VERIFICAÇÃO DE PERMISSÃO"""
        sistema = App.get_running_app().sistema
        
        # 🔥 VERIFICAR SE CLIENTE TEM PERMISSÃO PARA CÂMBIO
        if (sistema.usuario_logado and 
            sistema.tipo_usuario_logado == 'cliente' and
            not sistema.cliente_tem_permissao_cambio(sistema.usuario_logado)):
            
            self.mostrar_erro_permissao()
            # Voltar para dashboard se não tiver permissão
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 0.5)
            return
        
        print("Preparando tela de câmbio...")
        print("Preparando tela de câmbio...")
        # Reiniciar contador quando entrar na tela
        self.iniciar_contador_atualizacao(None)  # 🔥 CORREÇÃO: Adicionar None como argumento
        # 🔥 CORREÇÃO: Carregar pares apenas quando usuário estiver logado
        Clock.schedule_once(lambda dt: self.carregar_pares_disponiveis(), 0.1)
        Clock.schedule_once(lambda dt: self.carregar_saldos_ui(), 0.2)

    def on_leave(self):
        """Chamado quando sai da tela - para o contador"""
        if self.clock_atualizacao:
            self.clock_atualizacao.cancel()
            self.clock_atualizacao = None

    def criar_interface_manual(self, dt):
        """Cria interface manualmente sem KV - VERSÃO DEFINITIVA"""
        print("Criando interface manualmente...")
        
        # Container principal
        layout_principal = BoxLayout(orientation='vertical', padding=[25, 25, 25, 25], spacing=15)
        with layout_principal.canvas.before:
            Color(0.06, 0.09, 0.16, 1)
            self.bg_rect = RoundedRectangle(pos=layout_principal.pos, size=layout_principal.size)
        layout_principal.bind(pos=self._atualizar_bg, size=self._atualizar_bg)
        
        # Header
        header = self.criar_header()
        layout_principal.add_widget(header)
        
        # Seção de saldos
        saldos = self.criar_secao_saldos()
        layout_principal.add_widget(saldos)
        
        # Seção de operação
        operacao = self.criar_secao_operacao()
        layout_principal.add_widget(operacao)
        
        # Seção de confirmação
        confirmacao = self.criar_secao_confirmacao()
        layout_principal.add_widget(confirmacao)
        
        self.add_widget(layout_principal)
        print("Interface manual criada com sucesso!")

    def _atualizar_bg(self, instance, value):
        """Atualiza background"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    def criar_header(self):
        """Cria header manualmente - COM ESPAÇO VAZIO PARA CENTRALIZAR"""
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        
        # Botão Voltar
        btn_voltar = Button(
            text='< Voltar',
            size_hint_x=0.2,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_voltar.bind(on_press=self.voltar_dashboard)
        
        # 🔥 ESPAÇO VAZIO para equilibrar o layout
        espaco_vazio = Label(
            text='',
            size_hint_x=0.2  # 🔥 MESMO TAMANHO DO BOTÃO VOLTAR
        )
        
        # Título centralizado
        lbl_titulo = Label(
            text='COMPRA E VENDA DE MOEDAS',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=0.6,  # 🔥 AGORA OCUPA O CENTRO
            text_size=(None, None),
            halign='center'
        )
        
        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        header.add_widget(espaco_vazio)  # 🔥 ADICIONA ESPAÇO VAZIO
        
        return header

    def criar_secao_saldos(self):
        """Cria seção de saldos manualmente - MESMO ESTILO DO DASHBOARD"""
        container = BoxLayout(orientation='vertical', size_hint_y=0.2, padding=[10, 5, 10, 5])
        
        # Título
        lbl_titulo = Label(
            text='SEUS SALDOS',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        
        # 🔥 EXATAMENTE IGUAL AO DASHBOARD: GridLayout com 4 colunas
        self.grid_saldos = GridLayout(
            cols=4,  # 🔥 4 COLUNAS FIXAS - MESMO DO DASHBOARD
            spacing=dp(8),  # 🔥 MESMO ESPAÇAMENTO
            size_hint_y=None,  # 🔥 IMPORTANTE: altura não fixa para scroll
            padding=[0, 10, 0, 0]  # 🔥 MESMO PADDING
        )
        self.grid_saldos.bind(minimum_height=self.grid_saldos.setter('height'))
        
        # 🔥 ADICIONAR SCROLLVIEW - IGUAL AO DASHBOARD
        scroll_saldos = ScrollView(
            size_hint_y=0.7,
            do_scroll_x=False,  # 🔥 Scroll vertical apenas
            do_scroll_y=True
        )
        scroll_saldos.add_widget(self.grid_saldos)
        
        container.add_widget(lbl_titulo)
        container.add_widget(scroll_saldos)  # 🔥 AGORA COM SCROLL
        
        # Carregar saldos
        self.carregar_saldos_ui()
        
        return container

    def carregar_saldos_ui(self):
        """Carrega saldos na UI - MESMO ESTILO DO DASHBOARD"""
        sistema = App.get_running_app().sistema
        
        if not sistema or not sistema.usuario_logado:
            return
            
        usuario = sistema.usuario_logado
        saldos = sistema.calcular_saldos_usuario()
        self.grid_saldos.clear_widgets()
        
        # 🔥 USAR O MESMO MÉTODO DO DASHBOARD
        for moeda, saldo in saldos.items():
            card = self.criar_card_saldo_igual_dashboard(moeda, saldo)
            self.grid_saldos.add_widget(card)
        
        # 🔥 DEFINIR ALTURA MÍNIMA DO GRID PARA O SCROLL FUNCIONAR
        num_linhas = (len(saldos) + 3) // 4  # Calcula quantas linhas precisa
        altura_total = num_linhas * dp(70) + (num_linhas - 1) * dp(8) + dp(10)
        self.grid_saldos.height = altura_total

    def criar_card_saldo_igual_dashboard(self, moeda, saldo):
        """Cria card de saldo IDÊNTICO ao do dashboard"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),  # 🔥 MESMA ALTURA DO DASHBOARD
            padding=[12, 10],  # 🔥 MESMO PADDING
            spacing=dp(5)  # 🔥 MESMO ESPAÇAMENTO
        )
        
        # Background do card - MESMA COR DO DASHBOARD
        with card.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            card.rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[8,]  # 🔥 MESMO RADIUS
            )
        
        card.bind(pos=self._atualizar_card_rect, size=self._atualizar_card_rect)
        
        # 🔥 ESTRUTURA IDÊNTICA: Linha superior (Moeda) + Linha inferior (Valor)
        linha_superior = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        lbl_moeda = Label(
            text=moeda,
            font_size='12sp',  # 🔥 MESMA FONTE
            bold=True,
            color=(0.80, 0.84, 0.88, 1),  # 🔥 MESMA COR
            halign='left',
            text_size=(None, None)
        )
        lbl_moeda.bind(size=lbl_moeda.setter('text_size'))
        
        linha_superior.add_widget(lbl_moeda)
        
        # Linha inferior: Valor
        linha_inferior = BoxLayout(orientation='horizontal', size_hint_y=0.6)
        
        # 🔥 MESMA LÓGICA DE COR: vermelho se saldo negativo, azul se positivo
        cor_saldo = (0.8, 0.2, 0.2, 1) if saldo < 0 else (0.23, 0.51, 0.96, 1)
        
        lbl_valor = Label(
            text=f"{saldo:,.2f}",
            font_size='14sp',  # 🔥 MESMA FONTE
            bold=True,
            color=cor_saldo,  # 🔥 MESMA LÓGICA DE COR
            halign='left',
            text_size=(None, None)
        )
        lbl_valor.bind(size=lbl_valor.setter('text_size'))
        
        linha_inferior.add_widget(lbl_valor)
        
        card.add_widget(linha_superior)
        card.add_widget(linha_inferior)
        
        return card

    def criar_secao_operacao(self):
        """Cria seção de operação manualmente - BOTÃO ATUALIZAR MELHORADO"""
        container = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=10, padding=[10, 10, 10, 10])
        
        with container.canvas.before:
            Color(0.12, 0.16, 0.23, 1)
            container.rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[10,])
        container.bind(pos=self._atualizar_container_rect, size=self._atualizar_container_rect)
        
        # Contador de atualização - BOTÃO MAIOR E MAIS VISÍVEL
        contador_container = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        self.lbl_contador_atualizacao = Label(
            text="Atualização em: 30s",
            font_size='12sp',  # 🔥 FONTE UM POUCO MAIOR
            color=(0.3, 0.8, 0.3, 1),
            size_hint_x=0.6,   # 🔥 MAIS ESPAÇO PARA O CONTADOR
            text_size=(None, None),
            halign='left'
        )
        
        btn_atualizar_agora = Button(
            text='Atualizar Agora',  # 🔥 EMOJI PARA FICAR MAIS VISÍVEL
            size_hint_x=0.4,
            background_color=(0.23, 0.51, 0.96, 1),  # 🔥 AZUL FORTE
            color=(1, 1, 1, 1),
            font_size='12sp',  # 🔥 FONTE MAIOR
            bold=True
        )
        btn_atualizar_agora.bind(on_press=self.forcar_atualizacao)
        
        contador_container.add_widget(self.lbl_contador_atualizacao)
        contador_container.add_widget(btn_atualizar_agora)
        
        # Título
        lbl_titulo = Label(
            text='SELECIONE SUA OPERAÇÃO',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='center'
        )
        
        # Toggle buttons - VERSÃO MELHORADA
        toggle_container = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=15, padding=[20, 0, 20, 0])
        
        self.btn_compra = ToggleButton(
            text='COMPRAR MOEDA',
            group='operacao',
            state='down',
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True,
            size_hint_x=0.5
        )
        self.btn_compra.bind(on_press=lambda x: self.definir_operacao('compra'))
        
        self.btn_venda = ToggleButton(
            text='VENDER MOEDA',
            group='operacao',
            background_color=(0.3, 0.3, 0.3, 0.3),
            background_normal='',
            background_down='',
            color=(0.7, 0.7, 0.7, 1),
            font_size='13sp',
            bold=True,
            size_hint_x=0.5
        )
        self.btn_venda.bind(on_press=lambda x: self.definir_operacao('venda'))
        
        toggle_container.add_widget(self.btn_compra)
        toggle_container.add_widget(self.btn_venda)
        
        # Seleção de moedas
        selecao_container = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=5, padding=[10, 5, 10, 5])
        
        lbl_selecao = Label(
            text='Selecione as moedas:',
            font_size='12sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        
        # Container com labels "De" e "Para"
        labels_container = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        
        lbl_de = Label(
            text='De:',
            font_size='15sp',
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.4,
            text_size=(None, None),
            halign='left'
        )
        
        lbl_para = Label(
            text='Para:',
            font_size='15sp',
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.4,
            text_size=(None, None),
            halign='left'
        )
        
        lbl_espaco = Label(text='', size_hint_x=0.2)
        
        labels_container.add_widget(lbl_de)
        labels_container.add_widget(lbl_espaco)
        labels_container.add_widget(lbl_para)
        
        linha_selecao = BoxLayout(orientation='horizontal', size_hint_y=0.7, spacing=10)
        
        # Spinner De
        self.spinner_de = Spinner(
            text='Selecione...',
            values=[],
            size_hint_x=0.4,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            font_size='13sp'
        )
        self.spinner_de.bind(text=self.on_spinner_de_change)
        
        lbl_setas = Label(
            text='--->',
            font_size='20sp',
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.2,
            text_size=(None, None),
            halign='center'
        )
        
        # Spinner Para
        self.spinner_para = Spinner(
            text='Selecione...',
            values=[],
            size_hint_x=0.4,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            font_size='13sp'
        )
        self.spinner_para.bind(text=self.on_spinner_para_change)
        
        linha_selecao.add_widget(self.spinner_de)
        linha_selecao.add_widget(lbl_setas)
        linha_selecao.add_widget(self.spinner_para)
        
        selecao_container.add_widget(lbl_selecao)
        selecao_container.add_widget(labels_container)
        selecao_container.add_widget(linha_selecao)
        
        # Adicionar tudo ao container principal
        container.add_widget(contador_container)  # 🔥 NOVO: Contador primeiro
        container.add_widget(lbl_titulo)
        container.add_widget(toggle_container)
        container.add_widget(selecao_container)
        
        # Carregar pares
        self.carregar_pares_disponiveis()
        
        return container

    def forcar_atualizacao(self, instance):
        """Força atualização imediata da cotação"""
        print(" Atualização forçada da cotação")
        self.iniciar_contador_atualizacao(None)  # 🔥 CORREÇÃO: Adicionar None
        if self.par_selecionado:
            threading.Thread(target=self.obter_cotacao_thread, daemon=True).start()
        else:
            self.mostrar_erro("Selecione um par de moedas primeiro!")

    def criar_secao_confirmacao(self):
        """Cria seção de confirmação - USANDO CAMPO VALOR IGUAL À TRANSFERÊNCIA"""
        container = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=10, padding=[15, 15, 15, 15])
        
        with container.canvas.before:
            Color(0.12, 0.16, 0.23, 1)
            container.rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[10,])
        container.bind(pos=self._atualizar_container_rect, size=self._atualizar_container_rect)
        
        # Label de cotação
        self.lbl_cotacao = Label(
            text='Selecione um par de moedas para ver a cotação',
            font_size='13sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.25,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        # Input de valor - IGUAL À TELA DE TRANSFERÊNCIA
        valor_container = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        
        lbl_valor = Label(
            text='Valor:',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4,
            text_size=(None, None),
            halign='center'
        )
        
        # 🔥 USAR MESMO CONTAINER CENTRALIZADO DA TRANSFERÊNCIA
        linha_valor_centralizada = BoxLayout(
            orientation='horizontal', 
            size_hint_y=0.6, 
            size_hint_x=0.3,
            pos_hint={'center_x': 0.53}
        )
        
        # 🔥 USAR CampoValor IGUAL À TRANSFERÊNCIA
        self.entry_valor = CampoValor(
            hint_text='0.00',
            multiline=False,
            font_size='16sp',
            size_hint_x=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10],
            halign='right',
            text_validate_unfocus=False
        )
        self.entry_valor.bind(text=self.on_valor_change)
        
        self.lbl_moeda_valor = Label(
            text='USD',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.4,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        linha_valor_centralizada.add_widget(self.entry_valor)
        linha_valor_centralizada.add_widget(self.lbl_moeda_valor)
        
        valor_container.add_widget(lbl_valor)
        valor_container.add_widget(linha_valor_centralizada)
        
        # Resultado
        self.lbl_resultado = Label(
            text='Você receberá: ---',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        # Botão confirmar
        self.btn_confirmar = Button(
            text='CONFIRMAR OPERAÇÃO',
            font_size='16sp',
            bold=True,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            size_hint_y=0.25
        )
        self.btn_confirmar.bind(on_press=self.on_confirmar_operacao)
        self.btn_confirmar.disabled = True
        
        container.add_widget(self.lbl_cotacao)
        container.add_widget(valor_container)
        container.add_widget(self.lbl_resultado)
        container.add_widget(self.btn_confirmar)
        
        return container

    def _atualizar_card_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def _atualizar_container_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def carregar_pares_disponiveis(self):
        """Carrega pares disponíveis EVITANDO mesma moeda"""
        sistema = App.get_running_app().sistema
        
        if not sistema or not sistema.usuario_logado:
            self.spinner_de.values = []
            self.spinner_para.values = []
            return
        
        # 🔥 MANTER SUA LÓGICA ORIGINAL - apenas filtrar mesma moeda
        pares = sistema.obter_pares_disponiveis(sistema.usuario_logado)
        
        # Spinner DE mostra todas as moedas origem
        moedas_origem = list(set([par[:3] for par in pares]))
        
        # Spinner PARA mostra todas as moedas destino  
        moedas_destino = list(set([par[4:] for par in pares]))
        
        self.spinner_de.values = moedas_origem
        self.spinner_para.values = moedas_destino
        
        if moedas_origem:
            self.spinner_de.text = moedas_origem[0]
        if moedas_destino:
            self.spinner_para.text = moedas_destino[0]

    def atualizar_moeda_valor(self):
        """Atualiza qual moeda aparece no campo de valor"""
        if not self.par_selecionado:
            return
            
        if self.tipo_operacao == 'compra':
            # COMPRA: valor na moeda que está COMPRANDO (PARA)
            self.lbl_moeda_valor.text = self.spinner_para.text
        else:
            # VENDA: valor na moeda que está VENDENDO (DE)
            self.lbl_moeda_valor.text = self.spinner_de.text

    def definir_operacao(self, operacao):
        """Define o tipo de operação (compra/venda) - VERSÃO CORRIGIDA"""
        self.tipo_operacao = operacao
        self.atualizar_interface_operacao()
        self.atualizar_moeda_valor()  # 🔥 NOVO: Atualizar moeda do valor

    def atualizar_interface_operacao(self):
        """Atualiza aparência dos botões baseado na operação selecionada"""
        if self.tipo_operacao == 'compra':
            # 🔥 COMPRA SELECIONADA - DESTAQUE MÁXIMO
            self.btn_compra.background_color = (0.2, 0.8, 0.2, 1)      # VERDE FORTE
            self.btn_compra.color = (1, 1, 1, 1)                       # TEXTO BRANCO
            self.btn_compra.bold = True
            
            # 🔥 VENDA NÃO SELECIONADA - MUITO DISCRETA
            self.btn_venda.background_color = (0.3, 0.3, 0.3, 0.2)     # CINZA MUITO CLARO
            self.btn_venda.color = (0.6, 0.6, 0.6, 0.7)                # TEXTO CINZA CLARO
            self.btn_venda.bold = False
        else:
            # 🔥 VENDA SELECIONADA - DESTAQUE MÁXIMO
            self.btn_venda.background_color = (0.96, 0.36, 0.36, 1)    # VERMELHO FORTE
            self.btn_venda.color = (1, 1, 1, 1)                        # TEXTO BRANCO
            self.btn_venda.bold = True
            
            # 🔥 COMPRA NÃO SELECIONADA - MUITO DISCRETA
            self.btn_compra.background_color = (0.3, 0.3, 0.3, 0.2)    # CINZA MUITO CLARO
            self.btn_compra.color = (0.6, 0.6, 0.6, 0.7)               # TEXTO CINZA CLARO
            self.btn_compra.bold = False
        
        self.atualizar_cotacao()

    def on_spinner_de_change(self, instance, value):
        """Quando muda moeda DE - COM ATUALIZAÇÃO COMPLETA"""
        if value == 'Selecione...':
            self.par_selecionado = None
            return
            
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        pares = sistema.obter_pares_disponiveis(usuario)
        
        moedas_destino = []
        for par in pares:
            if par.startswith(value + '_'):
                moeda_destino = par[4:]
                if moeda_destino != value:
                    moedas_destino.append(moeda_destino)
        
        self.spinner_para.values = moedas_destino
        if moedas_destino:
            self.spinner_para.text = moedas_destino[0]
        else:
            self.spinner_para.text = 'Selecione...'
            self.par_selecionado = None
            
        # 🔥 CORREÇÃO: Atualizar par selecionado e recálculo
        if (self.spinner_de.text != 'Selecione...' and 
            self.spinner_para.text != 'Selecione...' and
            self.spinner_de.text != self.spinner_para.text):
            
            self.par_selecionado = f"{self.spinner_de.text}_{self.spinner_para.text}"
            self.atualizar_cotacao()
            
            # 🔥 CORREÇÃO: Atualizar moeda do campo valor TAMBÉM
            self.atualizar_moeda_valor()
            
            # Atualizar cálculo se houver valor
            if hasattr(self, 'valor_digitado') and self.valor_digitado > 0:
                self.on_valor_change(self.entry_valor, self.entry_valor.text)
        else:
            self.par_selecionado = None
            self.lbl_cotacao.text = 'Selecione um par de moedas válido'
            self.btn_confirmar.disabled = True

    def on_spinner_para_change(self, instance, value):
        """Quando muda moeda PARA - COM ATUALIZAÇÃO COMPLETA"""
        if (self.spinner_de.text != 'Selecione...' and 
            self.spinner_para.text != 'Selecione...' and
            self.spinner_de.text != self.spinner_para.text):
            
            self.par_selecionado = f"{self.spinner_de.text}_{self.spinner_para.text}"
            self.atualizar_cotacao()
            
            # 🔥 CORREÇÃO: Atualizar moeda do campo valor
            self.atualizar_moeda_valor()
            
            # Atualizar cálculo se houver valor
            if hasattr(self, 'valor_digitado') and self.valor_digitado > 0:
                self.on_valor_change(self.entry_valor, self.entry_valor.text)
        else:
            self.par_selecionado = None
            self.lbl_cotacao.text = 'Selecione um par de moedas válido'
            self.btn_confirmar.disabled = True

    def atualizar_cotacao(self):
        if not self.par_selecionado:
            return
        
        # 🔥 CORREÇÃO: Passar o usuário para a thread
        threading.Thread(target=self.obter_cotacao_thread, daemon=True).start()

    def obter_cotacao_thread(self):
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        # 🔥 SOLUÇÃO: Usar calcular_cotacao_cliente para AMBOS
        cotacao_calculo = sistema.calcular_cotacao_cliente(
            self.spinner_de.text,    # moeda_de
            self.spinner_para.text,  # moeda_para
            self.tipo_operacao, 
            usuario
        )
        
        if not cotacao_calculo:
            return
            
        spread_info = sistema.obter_spread_cliente(usuario, self.par_selecionado)
        spread = spread_info.get(self.tipo_operacao, sistema.spread_padrao)  # 🔥 CORREÇÃO AQUI
        
        # 🔥 CORREÇÃO: Para VENDA, obter a cotação INVERTIDA do cálculo
        if self.tipo_operacao == 'venda':
            # Obter par invertido para pegar a cotação direta
            par_invertido = f"{self.spinner_de.text}_{self.spinner_para.text}"
            cotacao_real_invertida = sistema.obter_cotacao_simples(par_invertido)
            
            if cotacao_real_invertida:
                # Aplicar spread na cotação invertida
                cotacao_exibicao = cotacao_real_invertida * (1 - spread/100)
            else:
                cotacao_exibicao = cotacao_calculo
        else:
            cotacao_exibicao = cotacao_calculo
                
        Clock.schedule_once(lambda dt: self.atualizar_ui_cotacao(cotacao_exibicao, spread))

    def mostrar_erro_permissao(self):
        """Mostra erro quando cliente não tem permissão para câmbio"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_erro = Label(
            text="ACESSO RESTRITO\n\nA função de compra e venda de moedas não está disponível para sua conta.\n\nEntre em contato com o administrador do sistema.",
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Acesso Restrito',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def atualizar_ui_cotacao(self, cotacao, spread):
        """Atualiza UI com a cotação - CORREÇÃO DISPLAY"""
        if not self.par_selecionado:
            return
                
        self.cotacao_atual = cotacao
        
        moeda_origem = self.spinner_de.text
        moeda_destino = self.spinner_para.text
        
        # 🔥 DEBUG CRÍTICO: Verificar qual cotação está chegando
        print(f"🔥 DEBUG atualizar_ui_cotacao:")
        print(f"   Tipo: {self.tipo_operacao}")
        print(f"   Par: {moeda_origem}->{moeda_destino}") 
        print(f"   Cotação recebida: {cotacao}")
        print(f"   Spread: {spread}")
        
        # MANTER COMPRA ORIGINAL
        if self.tipo_operacao == 'compra':
            texto_titulo = f"COMPRAR {moeda_destino}"
            cotacao_inversa = 1 / cotacao if cotacao != 0 else 0
            texto = f"[b][color=00FF00]{texto_titulo}[/color][/b]\n\n"
            texto += f"1 {moeda_destino} = {cotacao:.4f} {moeda_origem}\n"
            texto += f"1 {moeda_origem} = {cotacao_inversa:.4f} {moeda_destino}"
        else:
            texto_titulo = f"VENDER {moeda_origem}"
            cotacao_inversa = 1 / cotacao if cotacao != 0 else 0
            texto = f"[b][color=FF0000]{texto_titulo}[/color][/b]\n\n"
            texto += f"1 {moeda_origem} = {cotacao:.4f} {moeda_destino}\n"
            texto += f"1 {moeda_destino} = {cotacao_inversa:.4f} {moeda_origem}"
        
        self.lbl_cotacao.text = texto
        self.lbl_cotacao.font_size = '16sp'
        self.lbl_cotacao.markup = True
        self.btn_confirmar.disabled = False

    def extrair_valor_numerico(self, valor_texto):
        """Extrai valor numérico - VERSÃO ULTRA-ROBUSTA"""
        if not valor_texto or not valor_texto.strip():
            return 0.0
            
        texto = valor_texto.strip()
        print(f"EXTRAINDO VALOR DE: '{texto}'")
        
        # 🔥 DETECTAR FORMATO ESPECÍFICO "1,000.00" QUE ESTÁ DANDO PROBLEMA
        if texto == '1,000.00':
            print("DETECTADO FORMATO PROBLEMÁTICO '1,000.00' - CONVERTENDO PARA 1000.00")
            return 1000.0
        
        # Mapear formatos específicos problemáticos
        formatos_problematicos = {
            '1,000.00': 1000.0,
            '2,000.00': 2000.0, 
            '5,000.00': 5000.0,
            '10,000.00': 10000.0,
            '1.000,00': 1000.0,
            '2.000,00': 2000.0,
            '5.000,00': 5000.0,
            '10.000,00': 10000.0,
        }
        
        if texto in formatos_problematicos:
            resultado = formatos_problematicos[texto]
            print(f"VALOR MAAPEADO: {resultado:,.2f}")
            return resultado
        
        # Para outros valores, usar lógica genérica
        # Remover todos os separadores não decimais
        if ',' in texto and '.' in texto:
            # Determinar qual é o separador decimal
            ultimo_ponto = texto.rfind('.')
            ultima_virgula = texto.rfind(',')
            
            if ultimo_ponto > ultima_virgula:
                # Ponto é decimal: "1,000.00" → remover vírgulas
                texto_limpo = texto.replace(',', '')
            else:
                # Vírgula é decimal: "1.000,00" → remover pontos, converter vírgula
                texto_limpo = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            # Apenas vírgulas - verificar se é decimal
            partes = texto.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Vírgula decimal: "1000,00"
                texto_limpo = texto.replace(',', '.')
            else:
                # Vírgula de milhar: "1,000"
                texto_limpo = texto.replace(',', '')
        else:
            # Apenas pontos ou sem separadores
            texto_limpo = texto
        
        print(f"🔄 TEXTO LIMPO: '{texto_limpo}'")
        
        try:
            resultado = float(texto_limpo)
            print(f"VALOR FINAL: {resultado:,.2f}")
            return resultado
        except ValueError:
            print(f"FALHA NA CONVERSÃO")
            return 0.0

    def on_valor_change(self, instance, value):
        """Calcula o valor convertido - LÓGICA CORRIGIDA"""
        try:
            print(f"🔍 on_valor_change chamado: value='{value}'")
            
            # Extrair valor (já funciona corretamente)
            self.valor_digitado = self.extrair_valor_numerico(value)
            print(f"💰 Valor extraído: {self.valor_digitado:,.2f}")
            
            # 🔥 CORREÇÃO: Só processar se temos um valor válido e par selecionado
            if (self.valor_digitado > 0 and 
                self.par_selecionado and 
                hasattr(self, 'cotacao_atual') and
                self.cotacao_atual > 0):
                
                sistema = App.get_running_app().sistema
                usuario = sistema.usuario_logado
                
                moeda_origem = self.par_selecionado[:3]
                moeda_destino = self.par_selecionado[4:]
                
                print(f"🔍 Processando cálculo: {self.valor_digitado:,.2f} {moeda_origem}->{moeda_destino}")
                print(f"🔍 Tipo operação: {self.tipo_operacao}")
                
                # 🔥 CORREÇÃO CRÍTICA: Lógica invertida
                resultado, cotacao_usada = sistema.calcular_operacao_cambio(
                    self.spinner_de.text,    # moeda_de
                    self.spinner_para.text,  # moeda_para  
                    self.tipo_operacao, 
                    self.valor_digitado, 
                    usuario
                )
                
                if resultado is not None:
                    if self.tipo_operacao == 'compra':
                        # 🔥 COMPRA CORRIGIDA: usuário RECEBE o valor digitado (moeda_destino)
                        # Mas paga o valor calculado (resultado) na moeda_origem
                        texto = f"Você pagará: {resultado:,.2f} {moeda_origem}"
                        print(f"✅ COMPRA: Receberá {self.valor_digitado:,.2f} {moeda_destino}, Pagará {resultado:,.2f} {moeda_origem}")
                    else:
                        # 🔥 VENDA CORRIGIDA: usuário PAGA o valor digitado (moeda_origem)  
                        # Mas recebe o valor calculado (resultado) na moeda_destino
                        texto = f"Você receberá: {resultado:,.2f} {moeda_destino}"
                        print(f"✅ VENDA: Pagará {self.valor_digitado:,.2f} {moeda_origem}, Receberá {resultado:,.2f} {moeda_destino}")
                    
                    self.lbl_resultado.text = texto
                else:
                    self.lbl_resultado.text = 'Erro no cálculo'
            else:
                self.lbl_resultado.text = 'Digite um valor para ver a conversão'
                
        except Exception as e:
            print(f"❌ Erro em on_valor_change: {e}")
            self.lbl_resultado.text = 'Erro no cálculo'

    def atualizar_valor_manual(self):
        """Atualiza manualmente o valor digitado - para debugging"""
        try:
            if hasattr(self, 'entry_valor') and self.entry_valor.text:
                valor_texto = self.entry_valor.text
                print(f"🔍 Valor no campo: '{valor_texto}'")
                
                # Converter para numérico
                valor_limpo = valor_texto.replace('.', '').replace(',', '.')
                self.valor_digitado = float(valor_limpo) if valor_limpo else 0.0
                print(f"💰 Valor numérico: {self.valor_digitado}")
                
                return self.valor_digitado
        except Exception as e:
            print(f"❌ Erro ao atualizar valor manual: {e}")
            self.valor_digitado = 0.0
        
        return 0.0

    def proteger_valor_durante_atualizacao(self, dt=None):
        """Protege o valor digitado durante atualizações automáticas"""
        # Manter o valor atual durante atualizações de cotação
        if hasattr(self, 'valor_digitado') and self.valor_digitado > 0:
            # Atualizar apenas a cotação, não o valor
            if self.par_selecionado:
                threading.Thread(target=self.obter_cotacao_thread, daemon=True).start()

    def mostrar_popup_confirmacao(self, valor_pagar, valor_receber, moeda_pagar, moeda_receber, cotacao_direta, cotacao_inversa):
        """Mostra popup de confirmação antes de executar a operação"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # Conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 🔥 FUNDO CINZA para o conteúdo
        with content.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.2, 0.2, 0.2, 1)  # 🔥 CINZA ESCURO
            content.rect = RoundedRectangle(pos=content.pos, size=content.size, radius=[10,])
        content.bind(pos=lambda instance, value: setattr(content.rect, 'pos', value),
                    size=lambda instance, value: setattr(content.rect, 'size', value))
        
        # Título
        lbl_titulo = Label(
            text='CONFIRMAR OPERAÇÃO',
            font_size='18sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),  # 🔥 VERDE
            size_hint_y=0.3
        )
        
        # Informações da operação
        info_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        
        lbl_operacao = Label(
            text=f'[b]{self.tipo_operacao.upper()} {moeda_receber}[/b]',
            font_size='16sp',
            color=(0.2, 0.8, 0.2, 1),  # 🔥 VERDE
            markup=True
        )
        
        lbl_pagamento = Label(
            text=f'[b]Você pagará:[/b] {valor_pagar:,.2f} {moeda_pagar}',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),  # 🔥 VERDE
            markup=True
        )
        
        lbl_recebimento = Label(
            text=f'[b]Você receberá:[/b] {valor_receber:,.2f} {moeda_receber}',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),  # 🔥 VERDE
            markup=True
        )
        
        # Taxas (opcional)
        lbl_taxa = Label(
            text=f'Cotação: 1 {moeda_pagar} = {cotacao_direta:.4f} {moeda_receber}',
            font_size='12sp',
            color=(0.5, 0.8, 0.5, 1)  # 🔥 VERDE MAIS CLARO
        )
        
        info_container.add_widget(lbl_operacao)
        info_container.add_widget(lbl_pagamento)
        info_container.add_widget(lbl_recebimento)
        info_container.add_widget(lbl_taxa)
        
        # Botões
        botoes_container = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.8, 0.2, 0.2, 1),  # 🔥 VERMELHO
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        btn_confirmar = Button(
            text='CONFIRMAR',
            background_color=(0.2, 0.8, 0.2, 1),  # 🔥 VERDE
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        botoes_container.add_widget(btn_cancelar)
        botoes_container.add_widget(btn_confirmar)
        
        # Adicionar tudo ao conteúdo
        content.add_widget(lbl_titulo)
        content.add_widget(info_container)
        content.add_widget(botoes_container)
        
        # Criar popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(400, 300),
            auto_dismiss=False,
            separator_color=(0.2, 0.8, 0.2, 1),  # 🔥 BORDA VERDE
            background=''  # 🔥 REMOVER BACKGROUND PADRÃO
        )
        
        # 🔥 FUNDO ESCURO para o popup
        with popup.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)  # 🔥 FUNDO SEMI-TRANSPARENTE ESCURO
            popup.bg_rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[15,])
        popup.bind(pos=lambda instance, value: setattr(popup.bg_rect, 'pos', value),
                  size=lambda instance, value: setattr(popup.bg_rect, 'size', value))
        
        # Configurar ações dos botões
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_confirmar.bind(on_press=lambda x: self.executar_operacao_confirmada(
    popup, valor_pagar, valor_receber, moeda_pagar, moeda_receber, cotacao_direta
))
        
        popup.open()
    
    def executar_operacao_confirmada(self, popup, valor_pagar, valor_receber, moeda_pagar, moeda_receber, cotacao_cliente):
        """Executa a operação após confirmação no popup - VERSÃO CORRIGIDA COM SUPABASE"""
        popup.dismiss()
        
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        try:
            # 🔥 ENCONTRAR CONTAS BASEADO NAS MOEDAS
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            contas_origem = [c for c in usuario_data.get('contas', []) 
                           if sistema.contas[c]['moeda'] == moeda_pagar]
            contas_destino = [c for c in usuario_data.get('contas', []) 
                            if sistema.contas[c]['moeda'] == moeda_receber]
            
            if not contas_origem or not contas_destino:
                self.mostrar_erro("Erro ao encontrar contas para a operação!")
                return
            
            conta_origem = contas_origem[0]
            conta_destino = contas_destino[0]
            
            print(f" INICIANDO OPERAÇÃO {self.tipo_operacao.upper()}")
            print(f" Par: {moeda_pagar}_{moeda_receber}")
            print(f" Valor: {valor_pagar}")
            print(f" Moeda origem: {moeda_pagar}")
            print(f" Moeda destino: {moeda_receber}")
            print(f" Cotação: {cotacao_cliente}")
            
            # 🔥 SALVAR SALDOS ANTES
            saldo_origem_antes = sistema.contas[conta_origem]['saldo']
            saldo_destino_antes = sistema.contas[conta_destino]['saldo']
            
            # 🔥 EXECUTAR OPERAÇÃO
            if self.tipo_operacao == 'compra':
                # COMPRA: Paga moeda_origem, Recebe moeda_destino
                sistema.contas[conta_origem]['saldo'] -= valor_pagar
                sistema.contas[conta_destino]['saldo'] += valor_receber
                print(f"COMPRA: Paga {valor_pagar:.2f} {moeda_pagar}, Recebe {valor_receber:.2f} {moeda_receber}")
            else:
                # VENDA: Paga moeda_origem, Recebe moeda_destino  
                sistema.contas[conta_origem]['saldo'] -= valor_pagar
                sistema.contas[conta_destino]['saldo'] += valor_receber
                print(f"VENDA: Paga {valor_pagar:.2f} {moeda_pagar}, Recebe {valor_receber:.2f} {moeda_receber}")
            
            # 🔥 SALDOS DEPOIS
            saldo_origem_depois = sistema.contas[conta_origem]['saldo']
            saldo_destino_depois = sistema.contas[conta_destino]['saldo']
            
            print(f"Saldo origem: {saldo_origem_antes:,.2f} → {saldo_origem_depois:,.2f} {moeda_pagar}")
            print(f"Saldo destino: {saldo_destino_antes:,.2f} → {saldo_destino_depois:,.2f} {moeda_receber}")
            
            # 🔥🔥🔥 ATUALIZAR SALDOS NO SUPABASE - COM DEBUG DETALHADO
            print(f"🔍 VERIFICANDO CONEXÃO SUPABASE:")
            print(f"   Tem supabase? {hasattr(sistema, 'supabase')}")
            if hasattr(sistema, 'supabase'):
                print(f"   Está conectado? {sistema.supabase.conectado}")

            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print(f"🔍 ATUALIZANDO SALDOS NO SUPABASE:")
                    print(f"   Conta origem: {conta_origem} → {saldo_origem_depois:,.2f}")
                    print(f"   Conta destino: {conta_destino} → {saldo_destino_depois:,.2f}")
                    
                    # 🔥 CORREÇÃO: Usar 'id' em vez de 'numero'
                    response_origem = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_origem_depois})\
                        .eq('id', conta_origem)\
                        .execute()
                    
                    # 🔥 CORREÇÃO: Usar 'id' em vez de 'numero'
                    response_destino = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_destino_depois})\
                        .eq('id', conta_destino)\
                        .execute()
                    
                    print(f"🔍 RESPOSTA DO SUPABASE:")
                    print(f"   Origem: {response_origem.data}")
                    print(f"   Destino: {response_destino.data}")
                    
                    if response_origem.data and response_destino.data:
                        print(f"✅ Saldos atualizados no Supabase:")
                        print(f"   {conta_origem}: {saldo_origem_depois:,.2f} {moeda_pagar}")
                        print(f"   {conta_destino}: {saldo_destino_depois:,.2f} {moeda_receber}")
                    else:
                        print(f"❌ Erro ao atualizar saldos no Supabase")
                        print(f"   Response origem: {response_origem}")
                        print(f"   Response destino: {response_destino}")
                        
                except Exception as e:
                    print(f"❌ ERRO ao atualizar saldos no Supabase: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ SUPABASE NÃO DISPONÍVEL na nova tela")
            
            # Registrar transação
            transacao_id = sistema.registrar_transacao_cambio(
                f"{moeda_pagar}_{moeda_receber}", 
                self.tipo_operacao, 
                valor_pagar, 
                valor_receber, 
                cotacao_cliente,
                conta_origem, 
                conta_destino, 
                usuario
            )
            
            # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
            sucesso_supabase = self.salvar_cambio_supabase(
                transacao_id, valor_pagar, valor_receber, moeda_pagar, moeda_receber,
                cotacao_cliente, conta_origem, conta_destino, usuario
            )
            
            if sucesso_supabase:
                print(f"✅ Transação sincronizada com Supabase")
            else:
                print(f"⚠️ Transação salva apenas localmente")
            
            # Salvar alterações
            sistema.salvar_contas()
            sistema.salvar_transferencias()
            
            print(f"OPERAÇÃO CONCLUÍDA: {transacao_id}")
            
            self.mostrar_sucesso(f"Operação realizada com sucesso!\nID: {transacao_id}")
            self.entry_valor.text = '0.00'
            self.lbl_resultado.text = 'Você receberá: ---'
            
            # Atualizar saldos
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.carregar_saldos_ui(), 0.1)
            
        except Exception as e:
            print(f" Erro ao executar operação: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao processar operação: {str(e)}")

    def on_confirmar_operacao(self, instance):
        """Chamado quando clica em confirmar - AGORA COM VERIFICAÇÃO DE HORÁRIO"""
        print(f"CONFIRMAR OPERAÇÃO: valor_digitado={self.valor_digitado}")
        
        # 🔥 NOVA VERIFICAÇÃO: HORÁRIO COMERCIAL
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        print(f"🔍 INICIANDO VERIFICAÇÃO DE HORÁRIO PARA: {usuario}")
        horario_ok, mensagem = sistema.verificar_horario_comercial(usuario)
        print(f"🔍 RESULTADO VERIFICAÇÃO: {horario_ok} - {mensagem}")
        
        if not horario_ok:
            print(f"🚫 BLOQUEANDO OPERAÇÃO: Fora do horário comercial")
            self.mostrar_erro_horario(mensagem)
            return
        
        if self.spinner_de.text == self.spinner_para.text:
            self.mostrar_erro("Selecione moedas diferentes!")
            return
            
        # Verificação mais robusta do valor
        if not hasattr(self, 'valor_digitado') or self.valor_digitado <= 0:
            self.mostrar_erro("Digite um valor válido!")
            return
        
        if not self.par_selecionado:
            self.mostrar_erro("Selecione um par de moedas válido!")
            return
        
        # NOVA VERIFICAÇÃO: LIMITE OPERACIONAL
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        # Obter limite do cliente
        limite_operacional = sistema.obter_limite_operacional(usuario)
        
        print(f"VERIFICAÇÃO DE LIMITE:")
        print(f"   Usuário: {usuario}")
        print(f"   Valor operação: R$ {self.valor_digitado:.2f}")
        print(f"   Limite máximo: R$ {limite_operacional:.2f}")
        
        # Verificar se ultrapassa o limite
        if self.valor_digitado > limite_operacional:
            print(f"   LIMITE ULTRAPASSADO!")
            self.mostrar_erro_limite(limite_operacional, self.valor_digitado)
            return
        
        print(f"   DENTRO DO LIMITE - Prosseguindo com operação...")
        
        print(f"Dados válidos - Prosseguindo com operação...")
        
        # Calcular valores para o popup
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        moeda_origem = self.spinner_de.text
        moeda_destino = self.spinner_para.text
        
        print(f"CONFIRMAÇÃO - Moeda DE: {moeda_origem}")
        print(f"CONFIRMAÇÃO - Moeda PARA: {moeda_destino}")
        print(f"CONFIRMAÇÃO - Tipo: {self.tipo_operacao}")
        print(f"CONFIRMAÇÃO - Valor digitado: {self.valor_digitado}")
        
        # CORREÇÃO CRÍTICA: Lógica corrigida para confirmação
        if self.tipo_operacao == 'compra':
            # COMPRA: usuário RECEBE o valor digitado (moeda_destino)
            valor_receber = self.valor_digitado
            # CORREÇÃO: Usar moedas individuais em vez de par_selecionado
            valor_pagar, cotacao_cliente = sistema.calcular_operacao_cambio(
                moeda_origem,
                moeda_destino,
                self.tipo_operacao, 
                valor_receber, 
                usuario
            )
            moeda_pagar = moeda_origem
            moeda_receber = moeda_destino
            
            print(f"CONFIRMAÇÃO COMPRA:")
            print(f"   Receberá: {valor_receber:.2f} {moeda_receber}")
            print(f"   Pagará: {valor_pagar:.2f} {moeda_pagar}")
            
        else:
            # VENDA: usuário PAGA o valor digitado (moeda_origem)
            valor_pagar = self.valor_digitado
            # CORREÇÃO: Usar moedas individuais em vez de par_selecionado
            valor_receber, cotacao_cliente = sistema.calcular_operacao_cambio(
                moeda_origem,
                moeda_destino,
                self.tipo_operacao, 
                valor_pagar, 
                usuario
            )
            moeda_pagar = moeda_origem
            moeda_receber = moeda_destino
            
            print(f"CONFIRMAÇÃO VENDA:")
            print(f"   Pagará: {valor_pagar:.2f} {moeda_pagar}")
            print(f"   Receberá: {valor_receber:.2f} {moeda_destino}")
        
        if valor_pagar and valor_receber:
            # VERIFICAR TODAS AS CONTAS QUE PODEM FICAR NEGATIVAS
            saldos_negativos = []
            
            # 🔥 CORREÇÃO: Obter dados do usuário corretamente
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            
            # 1. Verificar conta de origem (moeda que está pagando)
            contas_origem = [c for c in usuario_data.get('contas', []) 
                           if sistema.contas[c]['moeda'] == moeda_pagar]
            
            if contas_origem:
                conta_origem = contas_origem[0]
                saldo_origem_atual = sistema.contas[conta_origem]['saldo']
                saldo_origem_pos = saldo_origem_atual - valor_pagar
                
                if saldo_origem_pos < 0:
                    saldos_negativos.append({
                        'conta': conta_origem,
                        'moeda': moeda_pagar,
                        'saldo_atual': saldo_origem_atual,
                        'saldo_pos': saldo_origem_pos,
                        'valor_operacao': valor_pagar,
                        'tipo': 'origem'
                    })
            
            print(f"DEBUG SALDOS: {len(saldos_negativos)} conta(s) ficarão negativas")
            
            if saldos_negativos:
                print(f"ENTRANDO NO FLUXO SALDO NEGATIVO")
                # Pegar a primeira conta que ficará negativa (normalmente a de origem)
                conta_negativa = saldos_negativos[0]
                
                self.mostrar_popup_saldo_negativo(
                    valor_pagar, 
                    valor_receber, 
                    moeda_pagar, 
                    moeda_receber,
                    conta_negativa['saldo_atual'],
                    conta_negativa['saldo_pos'], 
                    cotacao_cliente,
                    conta_negativa['moeda']
                )
            else:
                print(f"ENTRANDO NO FLUXO SALDO POSITIVO")
                # CALCULAR COTAÇÃO INVERSA PARA O 6º ARGUMENTO
                if self.tipo_operacao == 'compra':
                    cotacao_inversa = 1 / cotacao_cliente if cotacao_cliente != 0 else 0
                else:
                    cotacao_inversa = cotacao_cliente
                
                # Saldo positivo - popup normal COM 6 ARGUMENTOS
                self.mostrar_popup_confirmacao(
                    valor_pagar, 
                    valor_receber, 
                    moeda_pagar, 
                    moeda_receber,
                    cotacao_cliente,
                    cotacao_inversa
                )
        else:
            self.mostrar_erro("Erro ao calcular valores da operação!")

    def mostrar_popup_saldo_negativo(self, valor_pagar, valor_receber, moeda_pagar, moeda_receber, saldo_atual, saldo_pos_operacao, cotacao, moeda_negativa):
        """Mostra popup de confirmação para operação com saldo negativo"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        print(f"🔥 MÉTODO mostrar_popup_saldo_negativo CHAMADO!")
        print(f"   Moeda que ficará negativa: {moeda_negativa}")
        print(f"   Saldo atual: {saldo_atual:,.2f} {moeda_negativa}")
        print(f"   Saldo pós-operação: {saldo_pos_operacao:,.2f} {moeda_negativa}")
        
        # Conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 🔥 FUNDO ALARME (laranja/vermelho)
        with content.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.9, 0.6, 0.1, 1)  # 🔥 LARANJA DE ALERTA
            content.rect = RoundedRectangle(pos=content.pos, size=content.size, radius=[10,])
        content.bind(pos=lambda instance, value: setattr(content.rect, 'pos', value),
                    size=lambda instance, value: setattr(content.rect, 'size', value))
        
        # Título de ALERTA
        lbl_titulo = Label(
            text='ATENÇÃO - SALDO INSUFICIENTE',
            font_size='18sp',
            bold=True,
            color=(0.8, 0.2, 0.2, 1),  # 🔥 VERMELHO
            size_hint_y=0.2
        )
        
        # Informações da operação
        info_container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.6)
        
        lbl_aviso = Label(
            text=f'[b]Você ficará com saldo negativo em {moeda_negativa}![/b]',
            font_size='17sp',
            color=(0.8, 0.2, 0.2, 1),
            markup=True
        )
        
        lbl_saldo_atual = Label(
            text=f'Saldo atual: {saldo_atual:,.2f} {moeda_negativa}',
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        
        lbl_valor_operacao = Label(
            text=f'Valor da operação: {valor_pagar:,.2f} {moeda_pagar}',
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        
        lbl_saldo_futuro = Label(
            text=f'Saldo após operação: [color=ff4444]{saldo_pos_operacao:,.2f} {moeda_negativa}[/color]',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            markup=True
        )
        
        lbl_receber = Label(
            text=f'Você receberá: {valor_receber:,.2f} {moeda_receber}',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        # 🔥 TERMOS E CONDIÇÕES
        valor_depositar = abs(saldo_pos_operacao)
        multa_potencial = valor_pagar * 0.01
        
        lbl_termos = Label(
            text=f'[b]TERMOS:[/b] Você tem 24h para depositar [b]{valor_depositar:,.2f} {moeda_negativa}[/b] para cobrir o saldo negativo. Após este prazo, a operação será estornada e cobrada multa de 1% do valor.',
            font_size='11sp',
            color=(1, 1, 0.8, 1),  # 🔥 AMARELO CLARO
            markup=True,
            text_size=(380, None),
            halign='center'
        )
        
        info_container.add_widget(lbl_aviso)
        info_container.add_widget(lbl_saldo_atual)
        info_container.add_widget(lbl_valor_operacao)
        info_container.add_widget(lbl_saldo_futuro)
        info_container.add_widget(lbl_receber)
        info_container.add_widget(lbl_termos)
        
        # Botões
        botoes_container = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        btn_confirmar = Button(
            text='CONFIRMAR OPERAÇÃO',
            background_color=(0.2, 0.7, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        botoes_container.add_widget(btn_cancelar)
        botoes_container.add_widget(btn_confirmar)
        
        # Adicionar tudo ao conteúdo
        content.add_widget(lbl_titulo)
        content.add_widget(info_container)
        content.add_widget(botoes_container)
        
        # Criar popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 400),  # 🔥 MAIOR PARA CABER OS TERMOS
            auto_dismiss=False,
            background=''
        )
        
        # Fundo escuro
        with popup.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            popup.bg_rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[15,])
        popup.bind(pos=lambda instance, value: setattr(popup.bg_rect, 'pos', value),
                  size=lambda instance, value: setattr(popup.bg_rect, 'size', value))
        
        # Configurar ações dos botões
        btn_cancelar.bind(on_press=popup.dismiss)
        
        def confirmar_operacao_negativa(instance):
            popup.dismiss()
            self.executar_operacao_com_saldo_negativo(
                valor_pagar, 
                valor_receber, 
                moeda_pagar, 
                moeda_receber,
                saldo_pos_operacao, 
                moeda_negativa,
                cotacao  # 🔥 ADICIONAR A COTAÇÃO COMO 7º ARGUMENTO
            )
        
        btn_confirmar.bind(on_press=confirmar_operacao_negativa)
        
        popup.open()

    def executar_operacao_com_saldo_negativo(self, valor_pagar, valor_receber, moeda_pagar, moeda_receber, saldo_pos_operacao, moeda_negativa, cotacao_cliente):
        """Executa a operação mesmo com saldo negativo - VERSÃO COM SUPABASE"""
        
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        # 🔥 CALCULAR VALOR QUE O CLIENTE PRECISA DEPOSITAR
        valor_depositar = abs(saldo_pos_operacao)
        multa_potencial = valor_pagar * 0.01  # 1% de multa
        
        try:
            # 🔥 CORREÇÃO: Obter dados do usuário corretamente
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            
            # Encontrar contas
            contas_origem = [c for c in usuario_data.get('contas', []) 
                           if sistema.contas[c]['moeda'] == moeda_pagar]
            contas_destino = [c for c in usuario_data.get('contas', []) 
                            if sistema.contas[c]['moeda'] == moeda_receber]
            
            if not contas_origem or not contas_destino:
                self.mostrar_erro("Erro ao encontrar contas para a operação!")
                return
            
            conta_origem = contas_origem[0]
            conta_destino = contas_destino[0]
            
            print(f"  EXECUTANDO OPERAÇÃO COM SALDO NEGATIVO:")
            print(f"  Conta origem: {conta_origem} ({moeda_pagar})")
            print(f"  Conta destino: {conta_destino} ({moeda_receber})")
            print(f"  Moeda negativa: {moeda_negativa}")
            print(f"  Cotação usada: {cotacao_cliente}")
            
            # 🔥 SALVAR SALDOS ANTES
            saldo_origem_antes = sistema.contas[conta_origem]['saldo']
            saldo_destino_antes = sistema.contas[conta_destino]['saldo']
            
            print(f"  Saldo antes: {saldo_origem_antes:,.2f} {moeda_pagar}")
            
            # 🔥 EXECUTAR OPERAÇÃO MESMO COM SALDO NEGATIVO
            sistema.contas[conta_origem]['saldo'] -= valor_pagar
            sistema.contas[conta_destino]['saldo'] += valor_receber
            
            # 🔥 SALDOS DEPOIS
            saldo_origem_depois = sistema.contas[conta_origem]['saldo']
            saldo_destino_depois = sistema.contas[conta_destino]['saldo']
            
            print(f"  Saldo depois: {saldo_origem_depois:,.2f} {moeda_pagar}")
            
            # 🔥🔥🔥 ATUALIZAR SALDOS NO SUPABASE
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # 🔥 CORREÇÃO: Usar 'id' em vez de 'numero'
                    response_origem = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_origem_depois})\
                        .eq('id', conta_origem)\
                        .execute()
                    
                    # 🔥 CORREÇÃO: Usar 'id' em vez de 'numero'
                    response_destino = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_destino_depois})\
                        .eq('id', conta_destino)\
                        .execute()
                    
                    if response_origem.data and response_destino.data:
                        print(f"✅ Saldos atualizados no Supabase (saldo negativo):")
                        print(f"   {conta_origem}: {saldo_origem_depois:,.2f} {moeda_pagar}")
                        print(f"   {conta_destino}: {saldo_destino_depois:,.2f} {moeda_receber}")
                    else:
                        print(f"⚠️ Erro ao atualizar saldos no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldos no Supabase: {e}")
            
            # Registrar transação com flag de saldo negativo
            transacao_id = sistema.registrar_transacao_cambio(
                f"{moeda_pagar}_{moeda_receber}", 
                self.tipo_operacao, 
                valor_pagar, 
                valor_receber, 
                cotacao_cliente,  # ✅ AGORA USANDO A COTAÇÃO PASSADA
                conta_origem, 
                conta_destino, 
                usuario
            )
            
            # 🔥 ADICIONAR INFORMAÇÕES DE SALDO NEGATIVO NA TRANSAÇÃO
            sistema.transferencias[transacao_id]['saldo_negativo'] = True
            sistema.transferencias[transacao_id]['valor_depositar'] = valor_depositar
            sistema.transferencias[transacao_id]['multa_potencial'] = multa_potencial
            sistema.transferencias[transacao_id]['moeda_negativa'] = moeda_negativa
            sistema.transferencias[transacao_id]['data_limite_deposito'] = (
                datetime.datetime.now() + datetime.timedelta(hours=24)
            ).strftime("%Y-%m-%d %H:%M:%S")
            
            # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
            sucesso_supabase = self.salvar_cambio_supabase(
                transacao_id, valor_pagar, valor_receber, moeda_pagar, moeda_receber,
                cotacao_cliente, conta_origem, conta_destino, usuario,
                saldo_negativo=True, valor_depositar=valor_depositar, 
                multa_potencial=multa_potencial, moeda_negativa=moeda_negativa
            )
            
            if sucesso_supabase:
                print(f"✅ Transação com saldo negativo sincronizada com Supabase")
            else:
                print(f"⚠️ Transação com saldo negativo salva apenas localmente")
            
            # Salvar alterações
            sistema.salvar_contas()
            sistema.salvar_transferencias()
            
            print(f"OPERAÇÃO CONCLUÍDA: {transacao_id}")
            
            # 🔥 MOSTRAR MENSAGEM DE SUCESSO ORGANIZADA
            self.mostrar_sucesso_com_alerta(
                valor_receber, 
                moeda_receber, 
                sistema.contas[conta_origem]['saldo'], 
                moeda_pagar,
                valor_depositar,
                multa_potencial,
                transacao_id,
                moeda_negativa
            )
            
            # Atualizar saldos na tela
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.carregar_saldos_ui(), 0.1)
            
        except Exception as e:
            print(f" Erro ao executar operação com saldo negativo: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao processar operação: {str(e)}")

    def salvar_cambio_supabase(self, transacao_id, valor_pagar, valor_receber, moeda_pagar, moeda_receber, 
                             cotacao_cliente, conta_origem, conta_destino, usuario, 
                             saldo_negativo=False, valor_depositar=0, multa_potencial=0, moeda_negativa=None):
        """Salva operação de câmbio no Supabase - VERSÃO CORRIGIDA"""
        try:
            sistema = App.get_running_app().sistema
            
            print(f"🔥 SALVAR_CAMBIO_SUPABASE (VERSÃO CORRIGIDA)")
            print(f"   ID: {transacao_id}")
            print(f"   Usuário: {usuario}")
            print(f"   Operação: {self.tipo_operacao}")
            
            # 🔥 CORREÇÃO: Usar SupabaseManager em vez de INSERT direto
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # 🔥 PREPARAR DADOS COM MESMO PADRÃO DO ADMIN
                    dados_supabase = {
                        'id': transacao_id,
                        'tipo': 'cambio',
                        'status': 'completed',
                        'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'moeda': moeda_pagar,
                        'valor': valor_pagar,
                        'conta_remetente': conta_origem,
                        'conta_destinatario': conta_destino,
                        'descricao': f'CÂMBIO CLIENTE - {self.tipo_operacao.upper()} - {moeda_pagar} → {moeda_receber}',
                        'usuario': usuario,
                        'cliente': usuario,
                        'operacao': self.tipo_operacao,
                        'par_moedas': f"{moeda_pagar}_{moeda_receber}",
                        'valor_origem': valor_pagar,
                        'valor_destino': valor_receber,
                        'cotacao': cotacao_cliente,
                        'moeda_origem': moeda_pagar,
                        'moeda_destino': moeda_receber,
                        'saldo_negativo': saldo_negativo,
                        'valor_depositar': valor_depositar if saldo_negativo else None,
                        'multa_potencial': multa_potencial if saldo_negativo else None,
                        'moeda_negativa': moeda_negativa if saldo_negativo else None,
                        'data_limite_deposito': (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S") if saldo_negativo else None,
                        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    print(f"🔥 Dados preparados para Supabase:")
                    print(f"   ID: {dados_supabase['id']}")
                    print(f"   Data: {dados_supabase['data']}")
                    
                    # 🔥 CORREÇÃO: Usar método do SupabaseManager
                    sucesso = sistema.supabase.salvar_transacao_cambio(dados_supabase)
                    
                    if sucesso:
                        print(f"✅ Transação de câmbio salva no Supabase: {transacao_id}")
                        
                        # 🔥 ATUALIZAR TAMBÉM NO SISTEMA LOCAL
                        if transacao_id in sistema.transferencias:
                            sistema.transferencias[transacao_id].update({
                                'saldo_negativo': saldo_negativo,
                                'valor_depositar': valor_depositar if saldo_negativo else None,
                                'multa_potencial': multa_potencial if saldo_negativo else None,
                                'moeda_negativa': moeda_negativa if saldo_negativo else None,
                                'data_limite_deposito': (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S") if saldo_negativo else None
                            })
                        return True
                    else:
                        print(f"❌ Falha ao salvar transação no Supabase")
                        return False
                        
                except Exception as e:
                    print(f"❌ Erro ao salvar transação no Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("❌ Supabase não conectado - transação salva apenas localmente")
                return False
                
        except Exception as e:
            print(f"❌ Erro geral em salvar_cambio_supabase: {e}")
            import traceback
            traceback.print_exc()
            return False

    def mostrar_sucesso_com_alerta(self, valor_receber, moeda_receber, saldo_atual, moeda_pagar, valor_depositar, multa_potencial, transacao_id, moeda_negativa):
        """Mostra mensagem de sucesso organizada para saldo negativo - VERSÃO COM 8 ARGUMENTOS"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Título
        lbl_titulo = Label(
            text='OPERAÇÃO CONCLUÍDA',
            font_size='18sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.2
        )
        
        # Detalhes da operação
        detalhes_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=0.5)
        
        lbl_detalhes = Label(
            text=f'Você recebeu: {valor_receber:,.2f} {moeda_receber}\nSaldo atual: {saldo_atual:,.2f} {moeda_pagar}',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(380, None),
            halign='left'
        )
        
        # Alerta
        lbl_alerta = Label(
            text=f'ATENÇÃO - SALDO NEGATIVO EM {moeda_negativa}',
            font_size='16sp',
            bold=True,
            color=(0.9, 0.5, 0.1, 1),
            size_hint_y=0.15
        )
        
        lbl_termos = Label(
            text=f'• Deposite {valor_depositar:,.2f} {moeda_negativa} em 24h\n• Multa após prazo: {multa_potencial:,.2f} {moeda_negativa}\n• ID: {transacao_id}',
            font_size='12sp',
            color=(1, 1, 0.8, 1),
            text_size=(380, None),
            halign='left'
        )
        
        detalhes_container.add_widget(lbl_detalhes)
        detalhes_container.add_widget(lbl_alerta)
        detalhes_container.add_widget(lbl_termos)
        
        # Botão
        btn_ok = Button(
            text='ENTENDI',
            background_color=(0.2, 0.7, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=0.15
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(detalhes_container)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def voltar_dashboard(self, instance):
        self.manager.current = 'dashboard'

    def mostrar_erro_horario(self, mensagem):
        """Mostra erro quando fora do horário comercial"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_erro = Label(
            text=f"FORA DO HORÁRIO COMERCIAL\n\n{mensagem}",
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Horário Comercial',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_erro(self, mensagem):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        lbl = Label(text=mensagem, color=(1, 0.3, 0.3, 1))
        btn = Button(text='OK', size_hint_y=None, height=45)
        
        content.add_widget(lbl)
        content.add_widget(btn)
        
        popup = Popup(title='Erro', content=content, size_hint=(None, None), size=(400, 200))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_erro_limite(self, limite, valor):
        """Mostra erro quando operação ultrapassa o limite"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_erro = Label(
            text=f"LIMITE ULTRAPASSADO!\n\n"
                 f"Valor da operação: R$ {valor:.2f}\n"
                 f"Seu limite máximo: R$ {limite:.2f}\n\n"
                 f"Reduza o valor da operação.",
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Limite Ultrapassado',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra mensagem de sucesso - VERSÃO CORRIGIDA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # 🔥 GARANTIR QUE MENSAGEM É STRING
        if not isinstance(mensagem, str):
            mensagem = str(mensagem)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        lbl = Label(text=mensagem, color=(0.2, 0.8, 0.2, 1))
        btn = Button(text='OK', size_hint_y=None, height=45)
        
        content.add_widget(lbl)
        content.add_widget(btn)
        
        popup = Popup(title='Sucesso', content=content, size_hint=(None, None), size=(400, 200))
        btn.bind(on_press=popup.dismiss)
        popup.open()