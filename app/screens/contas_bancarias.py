from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.factory import Factory
import datetime
import os
import random

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from pdf_generator import PDFGenerator

class TextInputTaxaCambio(TextInput):
    """TextInput customizado para taxa de câmbio com MUITAS casas decimais"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_filter = 'float'
        self._updating_text = False  # Flag para evitar loop
        self.bind(focus=self.on_focus)
        self.bind(text=self.on_text)
    
    def on_focus(self, instance, value):
        """Quando o campo ganha foco, seleciona todo o texto"""
        if value:  # Se ganhou foco
            Clock.schedule_once(lambda dt: self.select_all())
    
    def on_text(self, instance, value):
        """Substitui vírgula por ponto quando o texto muda"""
        if self._updating_text:
            return
            
        if value and ',' in value:
            self._updating_text = True
            new_value = value.replace(',', '.')
            self.text = new_value
            self.cursor = (len(new_value), 0)
            self._updating_text = False
    
    def insert_text(self, substring, from_undo=False):
        """Substitui vírgula por ponto durante a digitação"""
        if ',' in substring:
            substring = substring.replace(',', '.')
        return super().insert_text(substring, from_undo=from_undo)

    def on_text_validate(self):
        """Garante que temos precisão máxima quando o campo perde foco"""
        if self.text:
            try:
                # Converter para float e formatar com 20 casas decimais
                valor = float(self.text)
                # Manter o valor original se já tiver alta precisão
                if len(self.text.split('.')[-1]) < 15:
                    self.text = f"{valor:.20f}".rstrip('0').rstrip('.')
            except ValueError:
                pass

# 🔥 Registrar a classe personalizada
Factory.register('TextInputTaxaCambio', cls=TextInputTaxaCambio)


# 🔥 CAMINHO CORRETO PARA O KV
current_dir = os.path.dirname(os.path.abspath(__file__))
kv_path = os.path.join(current_dir, 'kv', 'telaContasBancarias.kv')

print(f"🔍 Tentando carregar KV: {kv_path}")
print(f"🔍 Arquivo existe: {os.path.exists(kv_path)}")

if os.path.exists(kv_path):
    Builder.load_file(kv_path)
    print("✅ telaContasBancarias.kv carregado com sucesso!")
else:
    print(f"❌ Arquivo KV não encontrado: {kv_path}")
    # 🔥 LISTAR O QUE EXISTE NA PASTA PARA DEBUG
    kv_dir = os.path.join(current_dir, 'kv')
    if os.path.exists(kv_dir):
        print(f"📁 Conteúdo da pasta kv: {os.listdir(kv_dir)}")
    else:
        print(f"❌ Pasta kv não existe: {kv_dir}")

# 🔥 REGISTRAR CLASSES PERSONALIZADAS
Factory.register('TabbedPanelHeader', cls=TabbedPanelHeader)

class CardContaBancaria(BoxLayout):
    """Card para exibir uma conta bancária da empresa com botões de depósito, saque e extrato"""
    
    banco_info = StringProperty('')
    numero_conta = StringProperty('')
    moeda_conta = StringProperty('')
    saldo_formatado = StringProperty('')
    cor_saldo = ListProperty([0.23, 0.51, 0.96, 1])
    
    def __init__(self, conta_info, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.conta_info = conta_info
        self.tela_pai = tela_pai
        
        # 🔥 DEFINIR AS PROPRIEDADES PARA O KV
        self.banco_info = f"{conta_info['banco']} - Ag: {conta_info['agencia']}"
        self.numero_conta = conta_info['numero']
        self.moeda_conta = conta_info['moeda']
        self.saldo_formatado = f"{conta_info['saldo']:,.2f}"
        
        # 🔥 DEFINIR COR DO SALDO
        saldo = conta_info['saldo']
        self.cor_saldo = [0.8, 0.2, 0.2, 1] if saldo < 0 else [0.23, 0.51, 0.96, 1]
        
        # Background do card
        with self.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]
            )
        
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
    
    def _atualizar_rect(self, instance, value):
        """Atualiza o retângulo de background quando o card muda"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def ver_extrato_conta(self):
        """Abre o extrato da conta bancária"""
        print(f"📊 Abrindo extrato da conta: {self.numero_conta}")
        self.tela_pai.ver_extrato_conta_bancaria(self.numero_conta)
    
    def deposito_conta(self):
        """Abre popup para depósito na conta"""
        print(f"💰 Depósito na conta: {self.numero_conta}")
        self.tela_pai.deposito_conta(self.numero_conta)
    
    def saque_conta(self):
        """Abre popup para saque da conta"""
        print(f"💸 Saque da conta: {self.numero_conta}")
        self.tela_pai.saque_conta(self.numero_conta)

class TelaContasBancarias(Screen):
    """Tela para gerenciar contas bancárias da empresa"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.carregado = False
        self.operacao_ajuste_atual = 'credito'  # credito ou debito
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1200, 800)
        
        # 🔥 MOVER PARA ESQUERDA
        Window.left = 300    # 300 pixels da borda esquerda
        Window.top = 70      # 70 pixels do topo
        
        print("🏦 Tela Contas Bancárias - on_pre_enter")
        self.carregado = False
    
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        from kivy.core.window import Window
        
        Window.left = 300
        Window.top = 70
        
        print("🏦 Tela Contas Bancárias carregada - on_enter")
        
        if not self.carregado:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.carregar_contas_bancarias(), 0.5)
            Clock.schedule_once(lambda dt: self.carregar_contas_para_ajuste(), 0.7)
            Clock.schedule_once(lambda dt: self.definir_operacao_ajuste('credito'), 0.8)
            Clock.schedule_once(lambda dt: self.configurar_bindings_taxas_cambio(), 1.0)  # 🔥 NOVO
            self.carregado = True
    
    def carregar_contas_bancarias(self):
        """Carrega e exibe as contas bancárias da empresa - VERSÃO SUPABASE"""
        sistema = App.get_running_app().sistema
        
        # 🔥 NOVO: CARREGAR CONTAS DO SUPABASE SE NECESSÁRIO
        if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
            try:
                print("📡 Buscando contas bancárias no Supabase...")
                response = sistema.supabase.client.table('contas_bancarias_empresa')\
                    .select('*')\
                    .execute()
                
                if response.data:
                    # Limpar e recarregar do Supabase
                    sistema.contas_bancarias_empresa.clear()
                    for conta in response.data:
                        conta_num = conta['numero']  # Coluna correta
                        sistema.contas_bancarias_empresa[conta_num] = {
                            'numero': conta['numero'],
                            'banco': conta['banco'],
                            'moeda': conta['moeda'], 
                            'saldo': float(conta['saldo']),
                            'tipo': conta.get('tipo', 'corrente'),
                            'agencia': conta.get('agencia', ''),
                            'saldo_inicial': float(conta.get('saldo_inicial', conta['saldo']))
                        }
                    print(f"✅ {len(response.data)} contas bancárias carregadas do Supabase")
                    
                    # 🔥 SALVAR LOCALMENTE PARA BACKUP
                    sistema.salvar_contas_bancarias()
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar contas do Supabase: {e}")
                # Fallback: usar dados locais existentes
        
        if not hasattr(self, 'ids'):
            return
        
        container = self.ids.lista_contas_bancarias
        container.clear_widgets()
        
        # 🔥 AGORA USA OS DADOS ATUALIZADOS (SUPABASE OU LOCAIS)
        print(f"🔍 Exibindo {len(sistema.contas_bancarias_empresa)} contas bancárias")
        
        # 🔥 O RESTO DO MÉTODO CONTINUA EXATAMENTE IGUAL
        if not sistema.contas_bancarias_empresa:
            # Mensagem quando não há contas
            lbl_vazio = Label(
                text="Nenhuma conta bancária cadastrada",
                font_size='14sp',
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(lbl_vazio)
            return
        
        # Criar cards para cada conta bancária
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            print(f"➕ Adicionando conta: {conta_num} - Saldo: {conta_info['saldo']:,.2f} {conta_info['moeda']}")
            
            card = CardContaBancaria(conta_info, self)
            container.add_widget(card)
        
        # 🔥 CORREÇÃO: ATUALIZAR OS TOTAIS NO HEADER
        self.atualizar_totais_contas_bancarias()
        
        print(f"✅ {len(sistema.contas_bancarias_empresa)} contas bancárias carregadas")

    def atualizar_totais_contas_bancarias(self):
        """Atualiza os totais no header da tela de contas bancárias - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        # Calcular totais por moeda
        totais_moeda = {'USD': 0, 'EUR': 0, 'GBP': 0, 'BRL': 0}
        
        for conta_info in sistema.contas_bancarias_empresa.values():
            moeda = conta_info['moeda']
            if moeda in totais_moeda:
                totais_moeda[moeda] += conta_info['saldo']
        
        print(f"💰 TOTAIS CONTAS BANCÁRIAS: {totais_moeda}")
        
        # Atualizar os labels
        try:
            self.ids.lbl_total_usd.text = f"{totais_moeda['USD']:,.2f}"
            self.ids.lbl_total_eur.text = f"{totais_moeda['EUR']:,.2f}"
            self.ids.lbl_total_gbp.text = f"{totais_moeda['GBP']:,.2f}"
            self.ids.lbl_total_brl.text = f"{totais_moeda['BRL']:,.2f}"
            print("✅ Totais atualizados no header das contas bancárias")
        except Exception as e:
            print(f"❌ Erro ao atualizar totais contas bancárias: {e}")

    def _carregar_contas_apos_delay(self, dt):
        """Carrega as contas bancárias após um delay - VERSÃO SUPABASE"""
        sistema = App.get_running_app().sistema
        
        # 🔥 NOVO: MESMA VERIFICAÇÃO DO SUPABASE
        if hasattr(sistema, 'supabase') and sistema.supabase.conectado and not sistema.contas_bancarias_empresa:
            try:
                response = sistema.supabase.client.table('contas_bancarias_empresa')\
                    .select('*')\
                    .execute()
                
                if response.data:
                    sistema.contas_bancarias_empresa.clear()
                    for conta in response.data:
                        conta_num = conta['numero']
                        sistema.contas_bancarias_empresa[conta_num] = {
                            'numero': conta['numero'],
                            'banco': conta['banco'],
                            'moeda': conta['moeda'],
                            'saldo': float(conta['saldo']),
                            'tipo': conta.get('tipo', 'corrente'),
                            'agencia': conta.get('agencia', ''),
                            'saldo_inicial': float(conta.get('saldo_inicial', conta['saldo']))
                        }
                    print(f"✅ {len(response.data)} contas carregadas do Supabase (delay)")
            except Exception as e:
                print(f"⚠️ Erro ao carregar contas do Supabase (delay): {e}")
        
        # 🔥 O RESTO DO MÉTODO CONTINUA EXATAMENTE IGUAL
        if not hasattr(self, 'ids'):
            return
        
        container = self.ids.lista_contas_bancarias
        container.clear_widgets()
        
        print(f"🔍 Carregando contas bancárias... Total: {len(sistema.contas_bancarias_empresa)}")
        
        if not sistema.contas_bancarias_empresa:
            # Mensagem quando não há contas
            lbl_vazio = Label(
                text="📭 Nenhuma conta bancária cadastrada",
                font_size='14sp',
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(lbl_vazio)
            return
        
        # Calcular totais por moeda para o header
        totais_moeda = {}
        for conta_info in sistema.contas_bancarias_empresa.values():
            moeda = conta_info['moeda']
            if moeda not in totais_moeda:
                totais_moeda[moeda] = 0
            totais_moeda[moeda] += conta_info['saldo']
        
        print(f"💰 Totais por moeda: {totais_moeda}")
        
        # Atualizar header com totais
        if hasattr(self, 'ids') and hasattr(self.ids, 'lbl_totais_header'):
            texto_totais = " | ".join([f"{saldo:,.2f} {moeda}" for moeda, saldo in totais_moeda.items()])
            self.ids.lbl_totais_header.text = texto_totais
            print(f"✅ Totais atualizados no header")
        
        # Criar cards para cada conta bancária - 🔥 CORREÇÃO AQUI
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            print(f"➕ Adicionando conta: {conta_num} - Saldo: {conta_info['saldo']:,.2f} {conta_info['moeda']}")
            
            # 🔥 CORREÇÃO: Passar self como tela_pai
            card = CardContaBancaria(conta_info, self)  # 🔥 ADICIONAR self AQUI
            
            container.add_widget(card)
        
        print(f"✅ {len(sistema.contas_bancarias_empresa)} contas bancárias carregadas")
    
    def calcular_totais_por_moeda(self, sistema):
        """Calcula totais por moeda para exibir no header"""
        totais = {'USD': 0, 'EUR': 0, 'GBP': 0, 'BRL': 0}
        
        for conta_info in sistema.contas_bancarias_empresa.values():
            moeda = conta_info['moeda']
            if moeda in totais:
                totais[moeda] += conta_info['saldo']
        
        print(f"💰 Totais por moeda: {totais}")
        return totais
    
    def atualizar_totais_header(self, totais):
        """Atualiza os labels de totais no header"""
        try:
            if hasattr(self, 'ids'):
                self.ids.lbl_total_usd.text = f"{totais['USD']:,.2f}"
                self.ids.lbl_total_eur.text = f"{totais['EUR']:,.2f}"
                self.ids.lbl_total_gbp.text = f"{totais['GBP']:,.2f}"
                self.ids.lbl_total_brl.text = f"{totais['BRL']:,.2f}"
                print("✅ Totais atualizados no header")
        except Exception as e:
            print(f"❌ Erro ao atualizar totais: {e}")

    def ver_extrato_conta_bancaria(self, conta_numero):
        """Abre o extrato da conta bancária selecionada"""
        sistema = App.get_running_app().sistema
        
        print(f"📊 Abrindo extrato da conta: {conta_numero}")
        
        # Verificar se a tela de extrato existe
        if 'extrato_conta_bancaria' not in self.manager.screen_names:
            # Adicionar a tela se não existir
            tela_extrato = TelaExtratoContaBancaria(name='extrato_conta_bancaria')
            self.manager.add_widget(tela_extrato)
            print("✅ Tela de extrato conta bancária adicionada")
        
        # Obter a tela de extrato e configurar a conta
        tela_extrato = self.manager.get_screen('extrato_conta_bancaria')
        tela_extrato.configurar_conta(conta_numero)
        
        # Navegar para a tela de extrato
        self.manager.current = 'extrato_conta_bancaria'
        print(f"✅ Navegando para extrato da conta: {conta_numero}")

    def nova_conta_bancaria(self):
        """Abre popup para criar nova conta bancária - COM MOEDA MANUAL"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        from kivy.uix.togglebutton import ToggleButton
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        content.add_widget(Label(
            text='NOVA CONTA BANCÁRIA',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40
        ))
        
        # Banco
        content.add_widget(Label(
            text='Nome do Banco:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_banco = TextInput(
            hint_text='Ex: Banco Principal, Banco Internacional, etc',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_banco)
        
        # Agência
        content.add_widget(Label(
            text='Agência:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_agencia = TextInput(
            hint_text='Ex: 0001, 1234',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_agencia)
        
        # Número da Conta
        content.add_widget(Label(
            text='Número da Conta:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_numero_conta = TextInput(
            hint_text='Ex: BANK_USD_002, 123456789',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_numero_conta)
        
        # 🔥 NOVO: SELEÇÃO DE TIPO DE MOEDA
        content.add_widget(Label(
            text='Tipo de Moeda:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        tipo_moeda_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        
        self.toggle_moeda_principal = ToggleButton(
            text='Moeda Principal',
            group='tipo_moeda',
            state='down',
            size_hint_x=0.5
        )
        
        self.toggle_moeda_manual = ToggleButton(
            text='Outra Moeda',
            group='tipo_moeda',
            size_hint_x=0.5
        )
        
        tipo_moeda_layout.add_widget(self.toggle_moeda_principal)
        tipo_moeda_layout.add_widget(self.toggle_moeda_manual)
        content.add_widget(tipo_moeda_layout)
        
        # 🔥 MOEDA PRINCIPAL (Spinner)
        self.moeda_principal_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=70, spacing=5)
        
        self.spinner_moeda = Spinner(
            text='USD',
            values=('USD', 'EUR', 'GBP', 'BRL'),
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        self.moeda_principal_layout.add_widget(Label(
            text='Selecione a moeda:',
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=20
        ))
        self.moeda_principal_layout.add_widget(self.spinner_moeda)
        content.add_widget(self.moeda_principal_layout)
        
        # 🔥 MOEDA MANUAL (Input)
        self.moeda_manual_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=70, spacing=5)
        self.moeda_manual_layout.opacity = 0  # Inicialmente invisível
        
        content.add_widget(Label(
            text='Sigla da Moeda (3 letras):',
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=20
        ))
        
        self.entry_moeda_manual = TextInput(
            hint_text='Ex: JPY, CAD, AUD, CHF...',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.moeda_manual_layout.add_widget(self.entry_moeda_manual)
        content.add_widget(self.moeda_manual_layout)
        
        # Informação sobre saldo
        content.add_widget(Label(
            text='A nova conta será criada com saldo ZERO.\nUse "Depósito" para adicionar fundos depois.',
            font_size='12sp',
            color=(0.6, 0.8, 1, 1),
            size_hint_y=None,
            height=50,
            text_size=(400, None),
            halign='center'
        ))
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_criar = Button(
            text='Criar Conta',
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_criar)
        content.add_widget(botoes_layout)
        
        # 🔥🔥🔥 CORREÇÃO: AUMENTAR SIGNIFICATIVAMENTE A ALTURA DO POPUP
        self.popup_nova_conta = Popup(
            title='Nova Conta Bancária',
            content=content,
            size_hint=(None, None),
            size=(500, 850),  # 🔥 AUMENTADO de 600 para 650 (ou até 900 se necessário)
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # 🔥 VINCULAR EVENTOS DOS TOGGLE BUTTONS
        self.toggle_moeda_principal.bind(state=self.on_tipo_moeda_change)
        self.toggle_moeda_manual.bind(state=self.on_tipo_moeda_change)
        
        btn_cancelar.bind(on_press=self.popup_nova_conta.dismiss)
        btn_criar.bind(on_press=self.confirmar_criacao_conta)
        
        self.popup_nova_conta.open()

    def on_tipo_moeda_change(self, instance, value):
        """Alterna entre moeda principal e moeda manual"""
        if value == 'down':
            if instance.text == 'Moeda Principal':
                # Mostrar spinner, esconder input manual
                self.moeda_principal_layout.opacity = 1
                self.moeda_principal_layout.disabled = False
                self.moeda_manual_layout.opacity = 0
                self.moeda_manual_layout.disabled = True
            else:
                # Mostrar input manual, esconder spinner
                self.moeda_principal_layout.opacity = 0
                self.moeda_principal_layout.disabled = True
                self.moeda_manual_layout.opacity = 1
                self.moeda_manual_layout.disabled = False

    def confirmar_criacao_conta(self, instance):
        """Confirma e cria a nova conta bancária - COM VALIDAÇÃO DE MOEDA"""
        try:
            banco = self.entry_banco.text.strip()
            agencia = self.entry_agencia.text.strip()
            numero_conta = self.entry_numero_conta.text.strip()
            
            # 🔥 DETERMINAR MOEDA BASEADO NA SELEÇÃO
            if self.toggle_moeda_principal.state == 'down':
                moeda = self.spinner_moeda.text
            else:
                moeda = self.entry_moeda_manual.text.strip().upper()
            
            # Validar campos obrigatórios
            if not banco:
                self.mostrar_erro("Informe o nome do banco!")
                return
                
            if not agencia:
                self.mostrar_erro("Informe o número da agência!")
                return
                
            if not numero_conta:
                self.mostrar_erro("Informe o número da conta!")
                return
            
            # 🔥 VALIDAÇÃO DA MOEDA - 3 DÍGITOS
            if not moeda:
                self.mostrar_erro("Informe a moeda!")
                return
                
            if len(moeda) != 3 or not moeda.isalpha():
                self.mostrar_erro("A moeda deve ter exatamente 3 letras!\nEx: USD, EUR, JPY, CAD, etc.")
                return
            
            # 🔥 SEMPRE SALDO ZERO - não pedir saldo inicial
            saldo_inicial = 0.00
            
            sistema = App.get_running_app().sistema
            
            print(f"🔧 CRIANDO NOVA CONTA BANCÁRIA:")
            print(f"  Banco: {banco}")
            print(f"  Agência: {agencia}")
            print(f"  Número: {numero_conta}")
            print(f"  Moeda: {moeda} ({'Principal' if self.toggle_moeda_principal.state == 'down' else 'Manual'})")
            print(f"  Saldo: {saldo_inicial:,.2f} (SEMPRE ZERO)")
            
            # Chamar método do sistema
            sucesso, mensagem = sistema.criar_conta_bancaria_empresa(
                banco, agencia, numero_conta, moeda
            )
            
            if sucesso:
                self.popup_nova_conta.dismiss()
                self.mostrar_sucesso(mensagem)
                
                # 🔥 FORÇAR RECARGA DAS CONTAS BANCÁRIAS
                sistema.carregar_contas_bancarias()
                
                # Atualizar a tela
                self.carregar_contas_bancarias()
            else:
                self.mostrar_erro(mensagem)
                
        except Exception as e:
            self.mostrar_erro(f"Erro ao criar conta: {str(e)}")

    def deposito_conta(self, conta_numero):
        """Abre popup para depósito na conta bancária"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        
        self.conta_selecionada = conta_numero
        conta_info = App.get_running_app().sistema.contas_bancarias_empresa[conta_numero]
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        content.add_widget(Label(
            text=f'DEPÓSITO - {conta_info["banco"]}',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40
        ))
        
        # Informações da conta
        content.add_widget(Label(
            text=f'Conta: {conta_numero} | Saldo atual: {conta_info["saldo"]:,.2f} {conta_info["moeda"]}',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Valor do depósito
        content.add_widget(Label(
            text='Valor do Depósito:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_valor_deposito = TextInput(
            hint_text='0.00',
            font_size='16sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_valor_deposito)
        
        # Descrição
        content.add_widget(Label(
            text='Descrição:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_descricao_deposito = TextInput(
            hint_text='Depósito em conta',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_descricao_deposito)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Confirmar Depósito',
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        content.add_widget(botoes_layout)
        
        self.popup_deposito = Popup(
            title='💰 Depósito',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_cancelar.bind(on_press=self.popup_deposito.dismiss)
        btn_confirmar.bind(on_press=self.confirmar_deposito)
        
        self.popup_deposito.open()

    def saque_conta(self, conta_numero):
        """Abre popup para saque da conta bancária"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        
        self.conta_selecionada = conta_numero
        conta_info = App.get_running_app().sistema.contas_bancarias_empresa[conta_numero]
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        content.add_widget(Label(
            text=f'SAQUE - {conta_info["banco"]}',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40
        ))
        
        # Informações da conta
        content.add_widget(Label(
            text=f'Conta: {conta_numero} | Saldo atual: {conta_info["saldo"]:,.2f} {conta_info["moeda"]}',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Valor do saque
        content.add_widget(Label(
            text='Valor do Saque:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_valor_saque = TextInput(
            hint_text='0.00',
            font_size='16sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_valor_saque)
        
        # Descrição
        content.add_widget(Label(
            text='Descrição:',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.entry_descricao_saque = TextInput(
            hint_text='Saque da conta',
            font_size='14sp',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        content.add_widget(self.entry_descricao_saque)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Confirmar Saque',
            background_color=(0.1, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        content.add_widget(botoes_layout)
        
        self.popup_saque = Popup(
            title='💸 Saque',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_cancelar.bind(on_press=self.popup_saque.dismiss)
        btn_confirmar.bind(on_press=self.confirmar_saque)
        
        self.popup_saque.open()

    def confirmar_deposito(self, instance):
        """Confirma e processa o depósito na conta - VERSÃO CORRIGIDA"""
        try:
            valor = float(self.entry_valor_deposito.text.replace(',', ''))
            descricao = self.entry_descricao_deposito.text or "Depósito em conta"
            
            if valor <= 0:
                self.mostrar_erro("Valor do depósito deve ser maior que zero!")
                return
            
            sistema = App.get_running_app().sistema
            conta_numero = self.conta_selecionada
            
            print(f"💰 CONFIRMAR DEPÓSITO:")
            print(f"  Conta: {conta_numero}")
            print(f"  Valor: {valor:,.2f}")
            print(f"  Descrição: {descricao}")
            
            # Processar depósito
            if sistema.deposito_conta_bancaria(conta_numero, valor, descricao):
                self.popup_deposito.dismiss()
                self.mostrar_sucesso(f"Depósito de {valor:,.2f} realizado com sucesso!")
                
                # 🔥 FORÇAR RECARGA DAS CONTAS BANCÁRIAS
                sistema.carregar_contas_bancarias()
                
                # Atualiza a tela
                self.carregar_contas_bancarias()
            else:
                self.mostrar_erro("Erro ao processar depósito!")
                
        except ValueError:
            self.mostrar_erro("Valor inválido! Use números.")
        except Exception as e:
            self.mostrar_erro(f"Erro: {str(e)}")

    def confirmar_saque(self, instance):
        """Confirma e processa o saque da conta - VERSÃO CORRIGIDA"""
        try:
            valor = float(self.entry_valor_saque.text.replace(',', ''))
            descricao = self.entry_descricao_saque.text or "Saque da conta"
            
            if valor <= 0:
                self.mostrar_erro("Valor do saque deve ser maior que zero!")
                return
            
            sistema = App.get_running_app().sistema
            conta_numero = self.conta_selecionada
            
            print(f"💸 CONFIRMAR SAQUE:")
            print(f"  Conta: {conta_numero}")
            print(f"  Valor: {valor:,.2f}")
            print(f"  Descrição: {descricao}")
            
            # Verificar saldo suficiente
            conta_info = sistema.contas_bancarias_empresa[conta_numero]
            if valor > conta_info['saldo']:
                self.mostrar_erro("Saldo insuficiente para o saque!")
                return
            
            # Processar saque
            if sistema.saque_conta_bancaria(conta_numero, valor, descricao):
                self.popup_saque.dismiss()
                self.mostrar_sucesso(f"Saque de {valor:,.2f} realizado com sucesso!")
                
                # 🔥 FORÇAR RECARGA DAS CONTAS BANCÁRIAS
                sistema.carregar_contas_bancarias()
                
                # Atualiza a tela
                self.carregar_contas_bancarias()
            else:
                self.mostrar_erro("Erro ao processar saque!")
                
        except ValueError:
            self.mostrar_erro("Valor inválido! Use números.")
        except Exception as e:
            self.mostrar_erro(f"Erro: {str(e)}")

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
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.1, 0.8, 0.1, 1),
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
            title_color=(0.1, 0.8, 0.1, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

# 🔥 MÉTODOS AJUSTE SALDO CONTAS BANCÁRIAS

    def definir_operacao_ajuste(self, tipo):
        """Define o tipo de operação para ajuste de saldo - LÓGICA CORRIGIDA"""
        self.operacao_ajuste_atual = tipo
        
        if hasattr(self, 'ids'):
            if tipo == 'credito':
                # Crédito = Aumenta saldo (verde) - gera DÉBITO na conta
                self.ids.btn_credito_ajuste.background_color = (0.2, 0.8, 0.2, 1)      # Verde
                self.ids.btn_debito_ajuste.background_color = (0.15, 0.20, 0.27, 1)    # Cinza
            else:
                # Débito = Diminui saldo (vermelho) - gera CRÉDITO na conta
                self.ids.btn_credito_ajuste.background_color = (0.15, 0.20, 0.27, 1)   # Cinza
                self.ids.btn_debito_ajuste.background_color = (0.96, 0.36, 0.36, 1)    # Vermelho

    def carregar_contas_para_ajuste(self):
        """Carrega as contas bancárias nos combos das novas abas - COM DADOS ATUALIZADOS"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        # 🔥 DEBUG: Verificar contas disponíveis
        print(f"📊 Carregando {len(sistema.contas_bancarias_empresa)} contas para os spinners:")
        for chave in sistema.contas_bancarias_empresa.keys():
            print(f"   - '{chave}' - Saldo: {sistema.contas_bancarias_empresa[chave]['saldo']:,.2f}")
        
        # Carregar contas para ajuste de saldo
        opcoes_contas = []
        for conta_num, dados_conta in sistema.contas_bancarias_empresa.items():
            # 🔥 GARANTIR que o número da conta seja a PRIMEIRA parte do texto
            opcoes_contas.append(f"{conta_num} - {dados_conta['banco']} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
        
        if 'combo_conta_ajuste' in self.ids:
            # Salvar a seleção atual antes de atualizar
            selecao_atual = self.ids.combo_conta_ajuste.text
            
            self.ids.combo_conta_ajuste.values = opcoes_contas
            
            # Tentar restaurar a seleção anterior
            if selecao_atual and selecao_atual in opcoes_contas:
                self.ids.combo_conta_ajuste.text = selecao_atual
            elif opcoes_contas:
                self.ids.combo_conta_ajuste.text = opcoes_contas[0]
                
            print(f"✅ combo_conta_ajuste carregado com {len(opcoes_contas)} opções")
        
        # Carregar contas para câmbio (origem)
        if 'combo_conta_origem_cambio' in self.ids:
            selecao_atual = self.ids.combo_conta_origem_cambio.text
            
            self.ids.combo_conta_origem_cambio.values = opcoes_contas
            
            if selecao_atual and selecao_atual in opcoes_contas:
                self.ids.combo_conta_origem_cambio.text = selecao_atual
            elif opcoes_contas:
                self.ids.combo_conta_origem_cambio.text = opcoes_contas[0]
                
            print(f"✅ combo_conta_origem_cambio carregado")
        
        # Carregar contas para câmbio (destino)
        if 'combo_conta_destino_cambio' in self.ids:
            selecao_atual = self.ids.combo_conta_destino_cambio.text
            
            self.ids.combo_conta_destino_cambio.values = opcoes_contas
            
            if selecao_atual and selecao_atual in opcoes_contas:
                self.ids.combo_conta_destino_cambio.text = selecao_atual
            elif opcoes_contas and len(opcoes_contas) > 1:
                self.ids.combo_conta_destino_cambio.text = opcoes_contas[1]
            elif opcoes_contas:
                self.ids.combo_conta_destino_cambio.text = opcoes_contas[0]
                
            print(f"✅ combo_conta_destino_cambio carregado")

    def executar_ajuste_saldo_empresa(self):
        """Executa ajuste de saldo em conta bancária da empresa - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        print("💰 Executando ajuste de saldo empresa...")
        
        # Validar campos
        if not all([
            self.ids.combo_conta_ajuste.text,
            self.ids.entry_valor_ajuste.text,
            self.ids.entry_descricao_ajuste.text
        ]):
            self.mostrar_erro("Preencha todos os campos!")
            return
        
        try:
            # Obter texto do spinner
            texto_conta = self.ids.combo_conta_ajuste.text
            print(f"🔍 DEBUG - Texto conta: '{texto_conta}'")
            
            # 🔥🔥🔥 CORREÇÃO: Encontrar a conta pelo texto completo
            conta_num = None
            for chave in sistema.contas_bancarias_empresa.keys():
                if texto_conta.startswith(chave) or chave in texto_conta:
                    conta_num = chave
                    print(f"✅ Conta encontrada: '{conta_num}'")
                    break
            
            if not conta_num:
                self.mostrar_erro(f"Conta não encontrada! Texto: '{texto_conta}'")
                print(f"❌ Chaves disponíveis: {list(sistema.contas_bancarias_empresa.keys())}")
                return
            
            valor_str = self.ids.entry_valor_ajuste.text.strip()
            descricao = self.ids.entry_descricao_ajuste.text.strip()
            operacao = getattr(self, 'operacao_ajuste_atual', 'credito')
            
            # Converter valor
            valor = self._parse_valor_br(valor_str)
            
            if valor <= 0:
                self.mostrar_erro("Valor deve ser positivo!")
                return
            
            # 🔥 LÓGICA INVERTIDA PARA CONTAS BANCÁRIAS DA EMPRESA
            # Crédito (verde) = AUMENTA saldo (gera débito)
            # Débito (vermelho) = DIMINUI saldo (gera crédito)
            
            saldo_atual = sistema.contas_bancarias_empresa[conta_num]['saldo']
            moeda = sistema.contas_bancarias_empresa[conta_num]['moeda']
            
            if operacao == 'credito':
                # AUMENTAR saldo (Crédito na interface = Débito na conta)
                saldo_futuro = saldo_atual + valor
                tipo_operacao = "CRÉDITO"
                tipo_registro = "DÉBITO"  # 🔥 INVERTIDO
            else:
                # DIMINUIR saldo (Débito na interface = Crédito na conta)
                saldo_futuro = saldo_atual - valor
                if saldo_futuro < 0:
                    self.mostrar_erro(f"Saldo insuficiente! Saldo atual: {saldo_atual:,.2f} {moeda}")
                    return
                tipo_operacao = "DÉBITO"
                tipo_registro = "CRÉDITO"  # 🔥 INVERTIDO
            
            # Mostrar confirmação
            self.mostrar_confirmacao(
                f"Confirmar {tipo_operacao}?",
                f"Conta: {conta_num}\n"
                f"Valor: {valor:,.2f} {moeda}\n"
                f"Descrição: {descricao}\n"
                f"Saldo atual: {saldo_atual:,.2f} {moeda}\n"
                f"Saldo futuro: {saldo_futuro:,.2f} {moeda}\n\n"
                f"Tipo registro: {tipo_registro}",
                lambda: self._processar_ajuste_saldo_empresa(conta_num, valor, operacao, descricao)
            )
            
        except Exception as e:
            print(f"❌ Erro ao executar ajuste: {str(e)}")
            import traceback
            traceback.print_exc()

    def salvar_ajuste_supabase(self, transacao_id, conta_num, valor, operacao, descricao, username, tipo_registro):
        """Salva o ajuste na tabela transferencias do Supabase - USANDO TODAS AS COLUNAS"""
        try:
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível para salvar ajuste")
                return False
            
            moeda = sistema.contas_bancarias_empresa[conta_num]['moeda']
            
            # Determinar o tipo de operação para campos adicionais
            if operacao == "credito":
                tipo_interface = "CRÉDITO"  # O que o usuário clicou
                operacao_real = "entrada"    # Efeito real no saldo
            else:
                tipo_interface = "DÉBITO"    # O que o usuário clicou
                operacao_real = "saida"       # Efeito real no saldo
            
            # 🔥🔥🔥 AGORA USANDO TODAS AS COLUNAS DISPONÍVEIS
            dados_supabase = {
                'id': transacao_id,
                'tipo': 'ajuste_saldo_empresa',
                'status': 'completed',
                'data': datetime.now().isoformat(),
                'moeda': moeda,
                'valor': valor,
                'conta_remetente': conta_num,
                'descricao': descricao,              # Campo genérico
                'executado_por': self._safe_usuario_logado(),
                
                # 🔥 CAMPOS ESPECÍFICOS PARA AJUSTE (TODOS EXISTEM!)
                'tipo_ajuste': tipo_registro,        # DÉBITO/CRÉDITO (para o extrato)
                'tipo_interface': tipo_interface,     # O que o usuário clicou
                'descricao_ajuste': descricao,        # Descrição específica do ajuste
                
                # 🔥 CAMPOS ADICIONAIS PARA REFERÊNCIA
                'operacao': operacao_real,            # 'entrada' ou 'saida'
                'created_at': datetime.now().isoformat()
            }
            
            print(f"📦 Salvando ajuste no Supabase: {transacao_id}")
            print(f"   tipo_ajuste: {tipo_registro} (como aparece no extrato)")
            print(f"   tipo_interface: {tipo_interface} (como o usuário clicou)")
            print(f"   operacao: {operacao_real} (efeito real)")
            
            response = sistema.supabase.client.table('transferencias')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅✅✅ AJUSTE {transacao_id} SALVO NO SUPABASE!")
                print(f"   Campos preenchidos: id, tipo, tipo_ajuste, tipo_interface, operacao, ...")
                return True
            else:
                print(f"❌ Erro ao salvar ajuste no Supabase: {response.error if hasattr(response, 'error') else 'Resposta vazia'}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar ajuste no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _processar_ajuste_saldo_empresa(self, conta_num, valor, operacao, descricao):
        """Processa o ajuste de saldo após confirmação - COM ATUALIZAÇÃO DOS SPINNERS"""
        sistema = App.get_running_app().sistema
        
        print("\n" + "="*50)
        print("🔍 DEBUG - PROCESSANDO AJUSTE DE SALDO")
        print("="*50)
        print(f"📌 conta_num: '{conta_num}'")
        print(f"📌 valor: {valor}")
        print(f"📌 operacao: {operacao}")
        print(f"📌 descricao: '{descricao}'")
        
        # Verificar se a conta existe
        if conta_num not in sistema.contas_bancarias_empresa:
            print(f"❌ ERRO: Conta '{conta_num}' não encontrada em sistema.contas_bancarias_empresa!")
            print(f"📊 Contas disponíveis: {list(sistema.contas_bancarias_empresa.keys())}")
            self.mostrar_erro(f"Conta '{conta_num}' não encontrada!")
            return
        
        # Executar operação
        sucesso = self.executar_ajuste_saldo_sistema_empresa(conta_num, valor, operacao, descricao)
        
        if sucesso:
            # 🔥🔥🔥 FORÇAR RECARGA DO SUPABASE PARA OBTER SALDO ATUALIZADO
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print("🔄 Recarregando contas do Supabase...")
                    response = sistema.supabase.client.table('contas_bancarias_empresa')\
                        .select('*')\
                        .execute()
                    
                    if response.data:
                        # Atualizar o dicionário local com os dados mais recentes do Supabase
                        sistema.contas_bancarias_empresa.clear()
                        for conta in response.data:
                            conta_num_supabase = conta['numero']
                            sistema.contas_bancarias_empresa[conta_num_supabase] = {
                                'numero': conta['numero'],
                                'banco': conta['banco'],
                                'agencia': conta.get('agencia', ''),
                                'moeda': conta['moeda'],
                                'saldo': float(conta['saldo']),
                                'tipo': conta.get('tipo', 'empresa'),
                                'data_criacao': conta.get('data_criacao', ''),
                                'saldo_inicial': float(conta.get('saldo_inicial', conta['saldo']))
                            }
                        print(f"✅ {len(response.data)} contas recarregadas do Supabase")
                except Exception as e:
                    print(f"⚠️ Erro ao recarregar do Supabase: {e}")
            
            novo_saldo = sistema.contas_bancarias_empresa[conta_num]['saldo']
            moeda = sistema.contas_bancarias_empresa[conta_num]['moeda']
            tipo_operacao = "CRÉDITO" if operacao == 'credito' else "DÉBITO"
            
            print(f"✅ AJUSTE REALIZADO COM SUCESSO!")
            print(f"   Novo saldo: {novo_saldo:,.2f} {moeda}")
            
            self.mostrar_sucesso(
                f"✅ {tipo_operacao} realizado com sucesso!\n\n"
                f"Novo saldo: {novo_saldo:,.2f} {moeda}"
            )
            
            # Limpar campos
            self.ids.entry_valor_ajuste.text = ""
            self.ids.entry_descricao_ajuste.text = ""
            
            # 🔥🔥🔥 ATUALIZAR A LISTA PRINCIPAL DE CONTAS (CARDS)
            self.carregar_contas_bancarias()
            
            # 🔥🔥🔥 ATUALIZAR OS SPINNERS DA ABA AJUSTE
            self.carregar_contas_para_ajuste()
            
            # 🔥🔥🔥 FORÇAR ATUALIZAÇÃO DO TEXTO DO SPINNER COM O NOVO SALDO
            if 'combo_conta_ajuste' in self.ids:
                # Encontrar a opção atualizada para esta conta
                for opcao in self.ids.combo_conta_ajuste.values:
                    if opcao.startswith(conta_num):
                        self.ids.combo_conta_ajuste.text = opcao
                        print(f"✅ Spinner ajuste atualizado: {opcao}")
                        break
            
            # 🔥🔥🔥 ATUALIZAR OS SPINNERS DA ABA CÂMBIO (origem e destino)
            if 'combo_conta_origem_cambio' in self.ids:
                # Atualizar valores do spinner origem
                opcoes_contas = []
                for c_num, c_dados in sistema.contas_bancarias_empresa.items():
                    opcoes_contas.append(f"{c_num} - {c_dados['banco']} - {c_dados['moeda']} - Saldo: {c_dados['saldo']:,.2f}")
                
                self.ids.combo_conta_origem_cambio.values = opcoes_contas
                
                # Manter a seleção atual se possível
                if self.ids.combo_conta_origem_cambio.text:
                    texto_atual = self.ids.combo_conta_origem_cambio.text
                    for opcao in opcoes_contas:
                        if opcao.startswith(texto_atual.split(' - ')[0]):
                            self.ids.combo_conta_origem_cambio.text = opcao
                            break
            
            if 'combo_conta_destino_cambio' in self.ids:
                # Atualizar valores do spinner destino
                opcoes_contas = []
                for c_num, c_dados in sistema.contas_bancarias_empresa.items():
                    opcoes_contas.append(f"{c_num} - {c_dados['banco']} - {c_dados['moeda']} - Saldo: {c_dados['saldo']:,.2f}")
                
                self.ids.combo_conta_destino_cambio.values = opcoes_contas
                
                # Manter a seleção atual se possível
                if self.ids.combo_conta_destino_cambio.text:
                    texto_atual = self.ids.combo_conta_destino_cambio.text
                    for opcao in opcoes_contas:
                        if opcao.startswith(texto_atual.split(' - ')[0]):
                            self.ids.combo_conta_destino_cambio.text = opcao
                            break
            
            print("✅ Todos os spinners atualizados com os novos saldos!")
        else:
            print("❌ FALHA: executar_ajuste_saldo_sistema_empresa retornou False")
            self.mostrar_erro("Falha ao executar operação!")

    def executar_ajuste_saldo_sistema_empresa(self, conta_num, valor, operacao, descricao):
        """Executa o ajuste de saldo no sistema - COM SUPABASE COMPLETO"""
        sistema = App.get_running_app().sistema
        
        print("\n🔧 DENTRO DE executar_ajuste_saldo_sistema_empresa")
        print(f"   conta_num: '{conta_num}'")
        print(f"   tipo(conta_num): {type(conta_num)}")
        print(f"   valor: {valor}")
        print(f"   operacao: {operacao}")
        print(f"   descricao: '{descricao}'")
        
        try:
            # 🔥 VERIFICAR SE A CONTA EXISTE
            if conta_num not in sistema.contas_bancarias_empresa:
                print(f"   ❌ ERRO: Conta '{conta_num}' não encontrada!")
                return False
            
            # Salvar saldo antes
            saldo_antes = sistema.contas_bancarias_empresa[conta_num]['saldo']
            moeda = sistema.contas_bancarias_empresa[conta_num]['moeda']
            
            print(f"   💰 Saldo antes: {saldo_antes:,.2f} {moeda}")
            
            # 🔥🔥🔥 LÓGICA SIMPLES E DIRETA
            if operacao == "credito":
                # CRÉDITO = AUMENTA SALDO (Entrada)
                sistema.contas_bancarias_empresa[conta_num]['saldo'] += valor
                tipo_registro = "DÉBITO"  # Aparece na coluna DÉBITO do extrato
                print(f"   💰 SISTEMA: CRÉDITO -> Aumenta saldo (+{valor}) -> DÉBITO no extrato")
            else:
                # DÉBITO = DIMINUI SALDO (Saída)
                sistema.contas_bancarias_empresa[conta_num]['saldo'] -= valor
                tipo_registro = "CRÉDITO"  # Aparece na coluna CRÉDITO do extrato
                print(f"   💰 SISTEMA: DÉBITO -> Diminui saldo (-{valor}) -> CRÉDITO no extrato")
            
            # Saldo depois
            saldo_depois = sistema.contas_bancarias_empresa[conta_num]['saldo']
            print(f"   💰 Saldo depois: {saldo_depois:,.2f} {moeda}")
            
            # 🔥 GERAR ID DA TRANSAÇÃO
            import random
            import datetime
            
            transacao_id = str(random.randint(100000, 999999)) + "_aj"
            
            # 🔥🔥🔥 PRIMEIRO: ATUALIZAR SALDO NO SUPABASE
            sucesso_saldo = False
            sucesso_transacao = False
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print("   📡 Atualizando saldo no Supabase...")
                    
                    # Atualizar saldo no Supabase
                    response_saldo = sistema.supabase.client.table('contas_bancarias_empresa')\
                        .update({'saldo': saldo_depois})\
                        .eq('numero', conta_num)\
                        .execute()
                    
                    if response_saldo.data:
                        print(f"   ✅ Saldo atualizado no Supabase: {saldo_depois:,.2f}")
                        sucesso_saldo = True
                    else:
                        print(f"   ❌ Erro ao atualizar saldo no Supabase")
                        
                except Exception as e:
                    print(f"   ❌ Exceção ao atualizar saldo: {e}")
            
            # 🔥🔥🔥 SEGUNDO: SALVAR TRANSAÇÃO NO SUPABASE
            if sucesso_saldo or True:  # Tenta salvar transação mesmo se saldo falhou
                sucesso_transacao = self.salvar_ajuste_supabase(
                    transacao_id, conta_num, valor, operacao, descricao, 'EMPRESA', tipo_registro
                )
            
            # 🔥 REGISTRAR LOCALMENTE (sempre, como backup)
            sistema.transferencias[transacao_id] = {
                'id': transacao_id,
                'conta_remetente': conta_num,
                'valor': valor,
                'moeda': moeda,
                'tipo': 'ajuste_saldo_empresa',
                'tipo_ajuste': tipo_registro,
                'tipo_interface': 'CRÉDITO' if operacao == 'credito' else 'DÉBITO',
                'descricao_ajuste': descricao,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'executado_por': self._safe_usuario_logado()
            }
            
            print(f"   📝 Registro local criado: {transacao_id}")
            
            # 🔥 SALVAR DADOS LOCAIS
            sistema.salvar_contas_bancarias()
            sistema.salvar_transferencias()
            print(f"   ✅ Dados salvos localmente")
            
            # 🔥 RESUMO FINAL
            print("\n" + "="*40)
            print("📊 RESUMO DA OPERAÇÃO:")
            print(f"   Saldo no Supabase: {'✅' if sucesso_saldo else '❌'}")
            print(f"   Transação no Supabase: {'✅' if sucesso_transacao else '❌'}")
            print(f"   Dados locais: ✅")
            print("="*40)
            
            if sucesso_saldo and sucesso_transacao:
                print(f"   🎉🎉🎉 OPERAÇÃO COMPLETA: Local + Supabase (saldo + transação)!")
            elif sucesso_saldo:
                print(f"   ⚠️ Saldo atualizado no Supabase, mas transação NÃO foi salva!")
            elif sucesso_transacao:
                print(f"   ⚠️ Transação salva no Supabase, mas saldo NÃO foi atualizado!")
            else:
                print(f"   ⚠️ Operação salva apenas LOCALMENTE!")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao ajustar saldo empresa: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _safe_usuario_logado(self):
        """Retorna o usuário logado de forma segura"""
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        if isinstance(usuario, dict):
            return usuario.get('username', 'sistema')
        elif isinstance(usuario, str):
            return usuario
        else:
            return 'sistema'
        
# 🔥 MÉTODOS CAMBIO ENTRE CONTAS BANCÁRIAS

    def debug_verificar_contas_cambio(self):
        """Método de debug para verificar o estado das contas e spinners"""
        sistema = App.get_running_app().sistema
        
        print("\n" + "="*50)
        print("🔍 DEBUG COMPLETO - VERIFICAÇÃO DE CONTAS PARA CÂMBIO")
        print("="*50)
        
        # 1. Verificar contas no sistema
        print(f"\n📊 CONTAS NO SISTEMA ({len(sistema.contas_bancarias_empresa)}):")
        for num, dados in sistema.contas_bancarias_empresa.items():
            print(f"   - '{num}': {dados['banco']} - {dados['moeda']} - Saldo: {dados['saldo']:,.2f}")
        
        # 2. Verificar spinners
        if hasattr(self, 'ids'):
            print("\n🎯 SPINNER ORIGEM:")
            if 'combo_conta_origem_cambio' in self.ids:
                spinner_origem = self.ids.combo_conta_origem_cambio
                print(f"   Texto selecionado: '{spinner_origem.text}'")
                print(f"   Valores disponíveis ({len(spinner_origem.values)}):")
                for i, valor in enumerate(spinner_origem.values):
                    print(f"      {i+1}. '{valor}'")
            else:
                print("   ❌ spinner NÃO encontrado!")
            
            print("\n🎯 SPINNER DESTINO:")
            if 'combo_conta_destino_cambio' in self.ids:
                spinner_destino = self.ids.combo_conta_destino_cambio
                print(f"   Texto selecionado: '{spinner_destino.text}'")
                print(f"   Valores disponíveis ({len(spinner_destino.values)}):")
                for i, valor in enumerate(spinner_destino.values):
                    print(f"      {i+1}. '{valor}'")
            else:
                print("   ❌ spinner NÃO encontrado!")
        
        # 3. Verificar extração do número da conta
        print("\n🔧 TESTE DE EXTRAÇÃO:")
        if hasattr(self, 'ids') and 'combo_conta_origem_cambio' in self.ids:
            texto_teste = self.ids.combo_conta_origem_cambio.text
            if texto_teste:
                # Tentar diferentes métodos de extração
                print(f"   Texto original: '{texto_teste}'")
                
                # Método 1: split simples
                num1 = texto_teste.split(' - ')[0].strip()
                print(f"   Método 1 (split ' - '): '{num1}'")
                
                # Método 2: pegar primeira palavra
                num2 = texto_teste.split()[0].strip() if texto_teste.split() else ''
                print(f"   Método 2 (primeira palavra): '{num2}'")
                
                # Método 3: remover tudo após espaço
                num3 = texto_teste.split(' ')[0].strip()
                print(f"   Método 3 (split espaço): '{num3}'")
                
                # Verificar se algum método encontra a conta
                for metodo, num in [('1', num1), ('2', num2), ('3', num3)]:
                    if num in sistema.contas_bancarias_empresa:
                        print(f"   ✅ Método {metodo} ENCONTROU a conta!")
                    else:
                        print(f"   ❌ Método {metodo} NÃO encontrou a conta")
        
        print("="*50 + "\n")

    def executar_cambio_contas_empresa(self):
        """Executa câmbio entre contas bancárias da empresa - VERSÃO CORRIGIDA"""
        
        sistema = App.get_running_app().sistema
        
        print("💱 Executando câmbio entre contas empresa...")
        
        # Validar campos obrigatórios
        if not all([
            self.ids.combo_conta_origem_cambio.text,
            self.ids.combo_conta_destino_cambio.text,
            self.ids.entry_valor_cambio.text
        ]):
            self.mostrar_erro("Preencha todos os campos obrigatórios!")
            return
        
        # Validar taxas
        taxa_principal = self.ids.entry_taxa_principal_cambio.text.strip() if 'entry_taxa_principal_cambio' in self.ids else ""
        taxa_inversa = self.ids.entry_taxa_inversa_cambio.text.strip() if 'entry_taxa_inversa_cambio' in self.ids else ""
        
        if not taxa_principal and not taxa_inversa:
            self.mostrar_erro("Preencha pelo menos uma taxa de câmbio!")
            return
        
        try:
            # Obter dados dos spinners
            texto_origem = self.ids.combo_conta_origem_cambio.text
            texto_destino = self.ids.combo_conta_destino_cambio.text
            
            print(f"🔍 DEBUG - Texto origem: '{texto_origem}'")
            print(f"🔍 DEBUG - Texto destino: '{texto_destino}'")
            
            # 🔥🔥🔥 CORREÇÃO DEFINITIVA: Encontrar a conta pelo texto completo
            conta_origem = None
            conta_destino = None
            
            # Percorrer todas as contas e encontrar qual corresponde ao texto selecionado
            for chave in sistema.contas_bancarias_empresa.keys():
                if texto_origem.startswith(chave) or chave in texto_origem:
                    conta_origem = chave
                    print(f"✅ Conta origem encontrada: '{conta_origem}'")
                    break
            
            for chave in sistema.contas_bancarias_empresa.keys():
                if texto_destino.startswith(chave) or chave in texto_destino:
                    conta_destino = chave
                    print(f"✅ Conta destino encontrada: '{conta_destino}'")
                    break
            
            if not conta_origem:
                self.mostrar_erro(f"Conta origem não encontrada! Texto: '{texto_origem}'")
                print(f"❌ Chaves disponíveis: {list(sistema.contas_bancarias_empresa.keys())}")
                return
            
            if not conta_destino:
                self.mostrar_erro(f"Conta destino não encontrada! Texto: '{texto_destino}'")
                print(f"❌ Chaves disponíveis: {list(sistema.contas_bancarias_empresa.keys())}")
                return
            
            print(f"🔍 Conta origem final: '{conta_origem}'")
            print(f"🔍 Conta destino final: '{conta_destino}'")
            
            # Validar contas diferentes
            if conta_origem == conta_destino:
                self.mostrar_erro("Conta origem e destino devem ser diferentes!")
                return
            
            # Converter valor
            valor_str = self.ids.entry_valor_cambio.text.strip()
            valor = self._parse_valor_br(valor_str)
            
            if valor <= 0:
                self.mostrar_erro("Valor deve ser positivo!")
                return
            
            # Determinar taxa
            taxa = None
            tipo_taxa = None
            
            if taxa_principal:
                taxa = self._parse_valor_br(taxa_principal)
                tipo_taxa = 'principal'
            else:
                taxa = self._parse_valor_br(taxa_inversa)
                tipo_taxa = 'inversa'
            
            if not taxa or taxa <= 0:
                self.mostrar_erro("Taxa de câmbio inválida!")
                return
            
            # Obter dados das contas
            moeda_origem = sistema.contas_bancarias_empresa[conta_origem]['moeda']
            moeda_destino = sistema.contas_bancarias_empresa[conta_destino]['moeda']
            saldo_origem = sistema.contas_bancarias_empresa[conta_origem]['saldo']
            
            # Calcular valor destino
            if tipo_taxa == 'principal':
                valor_destino = valor * taxa
            else:
                valor_destino = valor / taxa
            
            # Verificar saldo
            if valor > saldo_origem:
                self.mostrar_erro(f"Saldo insuficiente! Disponível: {saldo_origem:,.2f} {moeda_origem}")
                return
            
            # Mostrar confirmação
            tipo_taxa_texto = "PRINCIPAL" if tipo_taxa == 'principal' else "INVERSA"
            
            self.mostrar_confirmacao(
                "Confirmar Câmbio entre Contas?",
                f"Origem: {conta_origem} ({moeda_origem})\n"
                f"Destino: {conta_destino} ({moeda_destino})\n"
                f"Valor: {valor:,.2f} {moeda_origem}\n"
                f"Taxa {tipo_taxa_texto}: {taxa:.6f}\n"
                f"Receberá: {valor_destino:,.2f} {moeda_destino}",
                lambda: self._processar_cambio_contas_empresa(
                    conta_origem, conta_destino, valor, taxa, valor_destino, tipo_taxa
                )
            )
            
        except Exception as e:
            print(f"❌ Erro ao executar câmbio: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao executar câmbio: {str(e)}")

    def _processar_cambio_contas_empresa(self, conta_origem, conta_destino, valor, taxa, valor_destino, tipo_taxa):
        """Processa o câmbio entre contas após confirmação"""
        sistema = App.get_running_app().sistema
        
        # Executar câmbio
        if self.executar_cambio_sistema_empresa(conta_origem, conta_destino, valor, taxa, valor_destino, tipo_taxa):
            moeda_origem = sistema.contas_bancarias_empresa[conta_origem]['moeda']
            moeda_destino = sistema.contas_bancarias_empresa[conta_destino]['moeda']
            
            tipo_taxa_texto = "PRINCIPAL" if tipo_taxa == 'principal' else "INVERSA"
            
            self.mostrar_sucesso(
                f"Câmbio entre contas realizado!\n\n"
                f"Conta origem ({conta_origem}): CRÉDITO de {valor:,.2f} {moeda_origem}\n"
                f"Conta destino ({conta_destino}): DÉBITO de {valor_destino:,.2f} {moeda_destino}\n"
                f"Taxa {tipo_taxa_texto} aplicada: {taxa:.6f}"
            )
            
            # Limpar campos
            self.ids.entry_valor_cambio.text = ""
            self.ids.entry_taxa_principal_cambio.text = ""
            self.ids.entry_taxa_inversa_cambio.text = ""
            
            # Atualizar a tela
            self.carregar_contas_bancarias()
            self.carregar_contas_para_ajuste()
        else:
            self.mostrar_erro("Falha ao executar câmbio!")

    def executar_cambio_sistema_empresa(self, conta_origem, conta_destino, valor, taxa, valor_destino, tipo_taxa):
        """Executa o câmbio entre contas - SUPABASE FIRST"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 PASSO 1: SALVAR PRIMEIRO NO SUPABASE
            usuario_executor = self._obter_usuario_executor()
            moeda_origem = sistema.contas_bancarias_empresa[conta_origem]['moeda']
            moeda_destino = sistema.contas_bancarias_empresa[conta_destino]['moeda']
            
            # 🔥 CORREÇÃO: DEFINIR taxa_principal AQUI
            if tipo_taxa == 'inversa':
                taxa_principal = 1.0 / taxa
            else:
                taxa_principal = taxa
            
            # Gerar ID da transação
            transacao_id = str(random.randint(100000, 999999)) + "_cb"
            
            print(f"🎯 INICIANDO CÂMBIO SUPABASE FIRST: {transacao_id}")
            print(f"   Origem: {conta_origem} (-{valor:,.2f} {moeda_origem})")
            print(f"   Destino: {conta_destino} (+{valor_destino:,.2f} {moeda_destino})")
            print(f"   Taxa {tipo_taxa}: {taxa:.6f}, Taxa principal: {taxa_principal:.6f}")
            
            # 🔥 PASSO 2: SALVAR TRANSAÇÃO NO SUPABASE
            sucesso_transacao = self.salvar_cambio_supabase(
                transacao_id, conta_origem, conta_destino, valor, valor_destino,
                moeda_origem, moeda_destino, taxa, tipo_taxa, usuario_executor
            )
            
            if not sucesso_transacao:
                self.mostrar_erro("Falha ao salvar transação no Supabase!")
                return False
            
            # 🔥 PASSO 3: ATUALIZAR SALDOS NO SUPABASE
            sucesso_saldos = self.atualizar_saldos_supabase_cambio(
                conta_origem, conta_destino, valor, valor_destino
            )
            
            if not sucesso_saldos:
                self.mostrar_erro("Falha ao atualizar saldos no Supabase!")
                return False
            
            # 🔥 PASSO 4: SOMENTE DEPOIS DO SUPABASE, ATUALIZAR LOCALMENTE
            saldo_origem_antes = sistema.contas_bancarias_empresa[conta_origem]['saldo']
            saldo_destino_antes = sistema.contas_bancarias_empresa[conta_destino]['saldo']
            
            sistema.contas_bancarias_empresa[conta_origem]['saldo'] -= valor
            sistema.contas_bancarias_empresa[conta_destino]['saldo'] += valor_destino
            
            # Registrar localmente
            sistema.transferencias[transacao_id] = {
                'id': transacao_id,
                'conta_remetente': conta_origem,
                'conta_destinatario': conta_destino,
                'valor': valor,
                'valor_destino': valor_destino,
                'moeda': moeda_origem,
                'moeda_destino': moeda_destino,
                'tipo': 'cambio_contas_empresa',
                'taxa_cambio': taxa,
                'tipo_taxa_usada': tipo_taxa,
                'taxa_principal_registro': taxa_principal,  # ✅ AGORA ESTÁ DEFINIDA
                'operacao_origem': 'CRÉDITO',
                'operacao_destino': 'DÉBITO',
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'executado_por': usuario_executor
            }
            
            # Salvar dados locais (backup)
            sistema.salvar_contas_bancarias()
            sistema.salvar_transferencias()
            
            print(f"✅✅✅ CÂMBIO {transacao_id} CONCLUÍDO COM SUCESSO!")
            print(f"   {conta_origem}: {saldo_origem_antes:,.2f} → {sistema.contas_bancarias_empresa[conta_origem]['saldo']:,.2f}")
            print(f"   {conta_destino}: {saldo_destino_antes:,.2f} → {sistema.contas_bancarias_empresa[conta_destino]['saldo']:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao executar câmbio empresa: {e}")
            import traceback
            traceback.print_exc()
            return False

    def salvar_cambio_supabase(self, transacao_id, conta_origem, conta_destino, valor_origem, valor_destino, 
                             moeda_origem, moeda_destino, taxa, tipo_taxa, usuario_executor):
        """Salva operação de câmbio no Supabase - SUPABASE FIRST"""
        try:
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível para salvar câmbio")
                return False
            
            # Calcular taxa principal para registro
            if tipo_taxa == 'inversa':
                taxa_principal = 1.0 / taxa
            else:
                taxa_principal = taxa
            
            dados_supabase = {
                'id': transacao_id,
                'tipo': 'cambio_contas_empresa',
                'status': 'completed',
                'data': datetime.now().isoformat(),
                'moeda_origem': moeda_origem,
                'moeda_destino': moeda_destino,
                'valor_origem': valor_origem,
                'valor_destino': valor_destino,
                'taxa_cambio': taxa,
                'tipo_taxa_usada': tipo_taxa,
                'taxa_principal_registro': taxa_principal,
                'conta_origem': conta_origem,
                'conta_destino': conta_destino,
                'usuario': usuario_executor,
                'created_at': datetime.now().isoformat()
            }
            
            print(f"📦 Salvando câmbio no Supabase: {transacao_id}")
            response = sistema.supabase.client.table('transferencias')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅✅✅ CÂMBIO {transacao_id} SALVO NO SUPABASE!")
                return True
            else:
                print(f"❌ Erro ao salvar câmbio no Supabase: {response.error}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar câmbio no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def atualizar_saldos_supabase_cambio(self, conta_origem, conta_destino, valor_origem, valor_destino):
        """Atualiza saldos das contas no Supabase após câmbio - SUPABASE FIRST"""
        try:
            sistema = App.get_running_app().sistema
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível para atualizar saldos")
                return False
            
            print(f"🔄 Atualizando saldos no Supabase:")
            print(f"   {conta_origem}: -{valor_origem:,.2f}")
            print(f"   {conta_destino}: +{valor_destino:,.2f}")
            
            # Buscar saldos atuais do Supabase
            response_origem = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('saldo')\
                .eq('numero', conta_origem)\
                .execute()
            
            response_destino = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('saldo')\
                .eq('numero', conta_destino)\
                .execute()
            
            if not response_origem.data or not response_destino.data:
                print("❌ Erro ao buscar saldos atuais do Supabase")
                return False
            
            saldo_origem_atual = float(response_origem.data[0]['saldo'])
            saldo_destino_atual = float(response_destino.data[0]['saldo'])
            
            novo_saldo_origem = saldo_origem_atual - valor_origem
            novo_saldo_destino = saldo_destino_atual + valor_destino
            
            # Atualizar conta origem
            response_update_origem = sistema.supabase.client.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo_origem})\
                .eq('numero', conta_origem)\
                .execute()
            
            # Atualizar conta destino
            response_update_destino = sistema.supabase.client.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo_destino})\
                .eq('numero', conta_destino)\
                .execute()
            
            sucesso_origem = bool(response_update_origem.data)
            sucesso_destino = bool(response_update_destino.data)
            
            if sucesso_origem and sucesso_destino:
                print(f"✅✅✅ SALDOS ATUALIZADOS NO SUPABASE!")
                print(f"   {conta_origem}: {saldo_origem_atual:,.2f} → {novo_saldo_origem:,.2f}")
                print(f"   {conta_destino}: {saldo_destino_atual:,.2f} → {novo_saldo_destino:,.2f}")
                
                # 🔥 ATUALIZAR LOCALMENTE APÓS SUPABASE
                sistema.contas_bancarias_empresa[conta_origem]['saldo'] = novo_saldo_origem
                sistema.contas_bancarias_empresa[conta_destino]['saldo'] = novo_saldo_destino
                
                return True
            else:
                print(f"❌ Erro ao atualizar saldos: origem={sucesso_origem}, destino={sucesso_destino}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar saldos no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False


# 🔥 ADICIONAR ESTES MÉTODOS DE TAXA BIDIRECIONAL

    def configurar_bindings_taxas_cambio(self):
        """Configura os bindings para os campos de taxa da aba câmbio - CORRIGIDO"""
        try:
            if hasattr(self, 'ids'):
                # Bind para taxa principal -> calcular inversa
                if 'entry_taxa_principal_cambio' in self.ids:
                    self.ids.entry_taxa_principal_cambio.bind(
                        text=self.calcular_taxa_inversa_cambio  # 🔥 SEM lambda
                    )
                
                # Bind para taxa inversa -> calcular principal
                if 'entry_taxa_inversa_cambio' in self.ids:
                    self.ids.entry_taxa_inversa_cambio.bind(
                        text=self.calcular_taxa_principal_cambio  # 🔥 SEM lambda
                    )
                
                # Bind para valor -> atualizar cálculo
                if 'entry_valor_cambio' in self.ids:
                    self.ids.entry_valor_cambio.bind(
                        text=lambda instance, value: self.atualizar_calculo_conversao_cambio()
                    )
                
                # Bind para contas -> atualizar cálculo quando mudarem
                if 'combo_conta_origem_cambio' in self.ids:
                    self.ids.combo_conta_origem_cambio.bind(
                        text=lambda instance, value: self.atualizar_calculo_conversao_cambio()
                    )
                
                if 'combo_conta_destino_cambio' in self.ids:
                    self.ids.combo_conta_destino_cambio.bind(
                        text=lambda instance, value: self.atualizar_calculo_conversao_cambio()
                    )
                    
        except Exception as e:
            print(f"❌ Erro ao configurar bindings de taxa: {e}")

    def calcular_taxa_inversa_cambio(self, instance=None, value=None):
        """Calcula a taxa inversa quando a principal é alterada - CORRIGIDO"""
        try:
            if not hasattr(self, 'ids') or 'entry_taxa_principal_cambio' not in self.ids:
                return
            
            taxa_principal_text = self.ids.entry_taxa_principal_cambio.text
            if not taxa_principal_text or taxa_principal_text in ['.', ',']:
                return
            
            # Converter para float
            taxa_principal = float(taxa_principal_text.replace(',', '.'))
            
            if taxa_principal > 0:
                # Calcular taxa inversa
                taxa_inversa = 1.0 / taxa_principal
                
                # Formatar com alta precisão
                taxa_inversa_str = f"{taxa_inversa:.20f}".rstrip('0').rstrip('.')
                
                # Atualizar campo (evitando loop)
                if 'entry_taxa_inversa_cambio' in self.ids:
                    self.ids.entry_taxa_inversa_cambio.unbind(text=self.calcular_taxa_principal_cambio)
                    self.ids.entry_taxa_inversa_cambio.text = taxa_inversa_str
                    self.ids.entry_taxa_inversa_cambio.bind(text=self.calcular_taxa_principal_cambio)
                
                # Atualizar cálculo de conversão
                self.atualizar_calculo_conversao_cambio()
                
        except Exception as e:
            print(f"❌ Erro em calcular_taxa_inversa_cambio: {e}")

    def calcular_taxa_principal_cambio(self, instance=None, value=None):
        """Calcula a taxa principal quando a inversa é alterada - CORRIGIDO"""
        try:
            if not hasattr(self, 'ids') or 'entry_taxa_inversa_cambio' not in self.ids:
                return
            
            taxa_inversa_text = self.ids.entry_taxa_inversa_cambio.text
            if not taxa_inversa_text or taxa_inversa_text in ['.', ',']:
                return
            
            # Converter para float
            taxa_inversa = float(taxa_inversa_text.replace(',', '.'))
            
            if taxa_inversa > 0:
                # Calcular taxa principal
                taxa_principal = 1.0 / taxa_inversa
                
                # Formatar com alta precisão
                taxa_principal_str = f"{taxa_principal:.20f}".rstrip('0').rstrip('.')
                
                # Atualizar campo (evitando loop)
                if 'entry_taxa_principal_cambio' in self.ids:
                    self.ids.entry_taxa_principal_cambio.unbind(text=self.calcular_taxa_inversa_cambio)
                    self.ids.entry_taxa_principal_cambio.text = taxa_principal_str
                    self.ids.entry_taxa_principal_cambio.bind(text=self.calcular_taxa_inversa_cambio)
                
                # Atualizar cálculo de conversão
                self.atualizar_calculo_conversao_cambio()
                
        except Exception as e:
            print(f"❌ Erro em calcular_taxa_principal_cambio: {e}")

    def trocar_taxas_cambio(self):
        """Troca os valores entre taxa principal e inversa"""
        try:
            if not hasattr(self, 'ids'):
                return
            
            taxa_principal = self.ids.entry_taxa_principal_cambio.text if 'entry_taxa_principal_cambio' in self.ids else ""
            taxa_inversa = self.ids.entry_taxa_inversa_cambio.text if 'entry_taxa_inversa_cambio' in self.ids else ""
            
            # Trocar os valores (evitando loops)
            if 'entry_taxa_principal_cambio' in self.ids and 'entry_taxa_inversa_cambio' in self.ids:
                self.ids.entry_taxa_principal_cambio.unbind(text=self.calcular_taxa_inversa_cambio)
                self.ids.entry_taxa_inversa_cambio.unbind(text=self.calcular_taxa_principal_cambio)
                
                self.ids.entry_taxa_principal_cambio.text = taxa_inversa
                self.ids.entry_taxa_inversa_cambio.text = taxa_principal
                
                self.ids.entry_taxa_principal_cambio.bind(text=self.calcular_taxa_inversa_cambio)
                self.ids.entry_taxa_inversa_cambio.bind(text=self.calcular_taxa_principal_cambio)
            
            # Atualizar cálculo
            self.atualizar_calculo_conversao_cambio()
            
        except Exception as e:
            print(f"❌ Erro ao trocar taxas: {e}")

    def atualizar_calculo_conversao_cambio(self):
        """Atualiza o cálculo de conversão baseado nos valores atuais - VERSÃO CORRIGIDA"""
        try:
            if not hasattr(self, 'ids'):
                return
            
            # Resetar label se não tiver dados suficientes
            if ('label_info_conversao_cambio' in self.ids and 
                (not self.ids.entry_valor_cambio.text or 
                not self.ids.combo_conta_origem_cambio.text or
                not self.ids.combo_conta_destino_cambio.text)):
                
                self.ids.label_info_conversao_cambio.text = 'Digite o valor e selecione as contas para ver a conversão'
                return
            
            # Obter valor a converter
            if 'entry_valor_cambio' in self.ids and self.ids.entry_valor_cambio.text:
                valor_str = self.ids.entry_valor_cambio.text.strip()
                if valor_str:
                    try:
                        valor = float(valor_str.replace(',', '.'))
                        
                        # 🔥 USAR A VERSÃO CORRIGIDA PARA OBTER AS MOEDAS
                        moeda_origem, moeda_destino = self.obter_moedas_contas_cambio()
                        
                        if not moeda_origem or not moeda_destino:
                            if 'label_info_conversao_cambio' in self.ids:
                                self.ids.label_info_conversao_cambio.text = 'Selecione contas origem e destino'
                            return
                        
                        # Usar taxa principal se disponível
                        if ('entry_taxa_principal_cambio' in self.ids and 
                            self.ids.entry_taxa_principal_cambio.text):
                            
                            taxa_str = self.ids.entry_taxa_principal_cambio.text.replace(',', '.')
                            taxa = float(taxa_str)
                            tipo_taxa = 'principal'
                            
                        # Se não tiver taxa principal, usar inversa
                        elif ('entry_taxa_inversa_cambio' in self.ids and 
                            self.ids.entry_taxa_inversa_cambio.text):
                            
                            taxa_str = self.ids.entry_taxa_inversa_cambio.text.replace(',', '.')
                            taxa = float(taxa_str)
                            tipo_taxa = 'inversa'
                            
                        else:
                            # Nenhuma taxa preenchida
                            if 'label_info_conversao_cambio' in self.ids:
                                self.ids.label_info_conversao_cambio.text = 'Digite uma taxa para ver a conversão'
                            return
                        
                        # Calcular valor convertido
                        if tipo_taxa == 'principal':
                            valor_convertido = valor * taxa
                        else:  # inversa
                            valor_convertido = valor / taxa
                        
                        # Atualizar label de informações
                        self.atualizar_label_conversao_cambio(
                            valor, moeda_origem, valor_convertido, moeda_destino, taxa, tipo_taxa
                        )
                        
                    except ValueError:
                        # Valor inválido
                        if 'label_info_conversao_cambio' in self.ids:
                            self.ids.label_info_conversao_cambio.text = 'Valor ou taxa inválidos'
                    except Exception as e:
                        print(f"❌ Erro no cálculo: {e}")
                        
        except Exception as e:
            print(f"❌ Erro em atualizar_calculo_conversao_cambio: {e}")

    def obter_moedas_contas_cambio(self):
        """Obtém as moedas das contas origem e destino selecionadas - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        moeda_origem = None
        moeda_destino = None
        
        try:
            # Obter textos dos spinners
            texto_origem = None
            texto_destino = None
            
            if ('combo_conta_origem_cambio' in self.ids and 
                self.ids.combo_conta_origem_cambio.text and
                'Selecione' not in self.ids.combo_conta_origem_cambio.text):
                texto_origem = self.ids.combo_conta_origem_cambio.text
            
            if ('combo_conta_destino_cambio' in self.ids and 
                self.ids.combo_conta_destino_cambio.text and
                'Selecione' not in self.ids.combo_conta_destino_cambio.text):
                texto_destino = self.ids.combo_conta_destino_cambio.text
            
            # 🔥🔥🔥 CORREÇÃO: Encontrar a conta pelo texto completo
            if texto_origem:
                for chave in sistema.contas_bancarias_empresa.keys():
                    if texto_origem.startswith(chave) or chave in texto_origem:
                        moeda_origem = sistema.contas_bancarias_empresa[chave]['moeda']
                        print(f"✅ Moeda origem encontrada: {moeda_origem} para conta '{chave}'")
                        break
            
            if texto_destino:
                for chave in sistema.contas_bancarias_empresa.keys():
                    if texto_destino.startswith(chave) or chave in texto_destino:
                        moeda_destino = sistema.contas_bancarias_empresa[chave]['moeda']
                        print(f"✅ Moeda destino encontrada: {moeda_destino} para conta '{chave}'")
                        break
            
        except Exception as e:
            print(f"❌ Erro ao obter moedas: {e}")
        
        return moeda_origem, moeda_destino

    def atualizar_label_conversao_cambio(self, valor_origem, moeda_origem, valor_destino, moeda_destino, taxa, tipo_taxa):
        """Atualiza o label de informações de conversão - COM LABEL REAL"""
        try:
            if not hasattr(self, 'ids') or 'label_info_conversao_cambio' not in self.ids:
                return
            
            tipo_taxa_texto = "PRINCIPAL" if tipo_taxa == 'principal' else "INVERSA"
            
            texto = (
                f"{valor_origem:,.2f} {moeda_origem} ---> {valor_destino:,.2f} {moeda_destino}\n"
                f"Taxa {tipo_taxa_texto}: {taxa:.6f}"
            )
            
            self.ids.label_info_conversao_cambio.text = texto
            
            # Também imprimir no console para debug
            print(f"Conversão: {valor_origem:,.2f} {moeda_origem} → {valor_destino:,.2f} {moeda_destino} | Taxa {tipo_taxa_texto}: {taxa:.6f}")
            
        except Exception as e:
            print(f"Erro ao atualizar label conversão: {e}")

    def debug_ajustes_saldo(self):
        """Debug para verificar ajustes de saldo no sistema"""
        sistema = App.get_running_app().sistema
        print(f"🔍 DEBUG GERAL - PROCURANDO AJUSTES DE SALDO:")
        
        ajustes_encontrados = 0
        for transferencia_id, dados in sistema.transferencias.items():
            if dados and isinstance(dados, dict) and dados.get('tipo') == 'ajuste_saldo_empresa':
                print(f"🎯 AJUSTE ENCONTRADO:")
                print(f"   - ID: {transferencia_id}")
                print(f"   - Conta: {dados.get('conta_remetente')}")
                print(f"   - Tipo: {dados.get('tipo_ajuste')}")
                print(f"   - Valor: {dados['valor']}")
                print(f"   - Data: {dados.get('data')}")
                print(f"   - Descrição: {dados.get('descricao_ajuste')}")
                ajustes_encontrados += 1
        
        print(f"📊 TOTAL DE AJUSTES NO SISTEMA: {ajustes_encontrados}")
        
        # Verificar se há ajustes para BANK_BRL_001 especificamente
        ajustes_brl = 0
        for transferencia_id, dados in sistema.transferencias.items():
            if (dados and isinstance(dados, dict) and 
                dados.get('tipo') == 'ajuste_saldo_empresa' and 
                dados.get('conta_remetente') == 'BANK_BRL_001'):
                ajustes_brl += 1
        
        print(f"🎯 AJUSTES PARA BANK_BRL_001: {ajustes_brl}")


# 🔥 ADICIONAR ESTES MÉTODOS AUXILIARES

    def _parse_valor_br(self, valor_str):
        """Converte string de valor no formato brasileiro para float"""
        if not valor_str:
            raise ValueError("Valor vazio")
        
        valor_str = valor_str.strip()
        
        try:
            # CORREÇÃO: Lidar com formato brasileiro (26,384.00)
            if ',' in valor_str and '.' in valor_str:
                # Exemplo: "26,384.00" -> virgula é separador de milhar, ponto é decimal
                valor_limpo = valor_str.replace(',', '')
            elif ',' in valor_str:
                # Apenas vírgula: "300,00" -> substituir por ponto
                valor_limpo = valor_str.replace(',', '.')
            else:
                # Apenas ponto: "300.00" -> manter como está
                valor_limpo = valor_str
            
            valor_float = float(valor_limpo)
            return valor_float
            
        except ValueError:
            raise ValueError("Valor inválido! Use números como: 300.00 ou 26,384.00")

    def mostrar_confirmacao(self, titulo, mensagem, callback_confirmar):
        """Mostra popup de confirmação"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_titulo = Label(
            text=titulo,
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(400, None),
            halign='center'
        )
        
        lbl_mensagem = Label(
            text=mensagem,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center',
            valign='top',
            size_hint_y=None,
            height=200
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Confirmar',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_mensagem)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            popup.dismiss()
            callback_confirmar()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    def _obter_usuario_executor(self):
        """Obtém o username do executor de forma segura"""
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        if isinstance(usuario, dict):
            return usuario.get('username', 'sistema')
        elif isinstance(usuario, str):
            return usuario
        else:
            return 'sistema'

    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'

class TelaExtratoContaBancaria(Screen):
    """Tela de extrato para contas bancárias da empresa - LÓGICA INVERTIDA"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conta_bancaria_numero = None
        self.transacoes_carregadas = []
        self.periodo_var = "30"
        self.saldo_final = 0
        self.total_entradas = 0
        self.total_saidas = 0
        self.transacoes_filtradas = []
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1400, 1000)

        # 🔥 MOVER PARA ESQUERDA - VERSÃO SIMPLES
        Window.left = 300    # 300 pixels da borda esquerda
        Window.top = 40    # 70 pixels do topo
        
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        from kivy.core.window import Window  # 🔥 ADICIONAR ESTA LINHA
        
        print("🏦 Tela Extrato Conta Bancária carregada")

        # 🔥 GARANTIR que está na posição correta
        Window.left = 300
        Window.top = 40
        
        if self.conta_bancaria_numero:
            # Carregar dados iniciais
            self.carregar_dados_iniciais()
            # Carregar extrato com delay
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.carregar_extrato(), 0.8)
            Clock.schedule_once(lambda dt: self.scroll_para_topo(), 1.0)
    
    def configurar_conta(self, conta_numero):
        """Configura a conta bancária para visualização"""
        self.conta_bancaria_numero = conta_numero
        print(f"🔧 Configurando extrato para conta: {conta_numero}")
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais da tela"""
        sistema = App.get_running_app().sistema
        
        if not self.conta_bancaria_numero:
            self.mostrar_erro("Nenhuma conta configurada!")
            return
        
        # Verificar se a conta existe
        if self.conta_bancaria_numero not in sistema.contas_bancarias_empresa:
            self.mostrar_erro("Conta bancária não encontrada!")
            return
        
        # Configurar período padrão
        if hasattr(self, 'ids'):
            self.periodo_var = "30"  # 30 dias padrão
            
            # Configurar data atual
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
            self.ids.entry_data_fim.text = data_atual
            self.ids.entry_data_inicio.text = "01/01/2024"
            
            # Configurar máscaras de data
            self.ids.entry_data_inicio.bind(text=self.aplicar_mascara_data)
            self.ids.entry_data_fim.bind(text=self.aplicar_mascara_data)
            
            # Configurar eventos de foco
            self.ids.entry_data_inicio.bind(focus=self.on_focus_data_inicio)
            self.ids.entry_data_fim.bind(focus=self.on_focus_data_fim)
            
            # Atualizar saldo na parte superior
            self.atualizar_saldo_superior()
    
    def aplicar_mascara_data(self, instance, value):
        """Aplica máscara de data DD/MM/AAAA"""
        if getattr(instance, '_processing', False):
            return
            
        instance._processing = True
        
        try:
            texto_limpo = ''.join(c for c in value if c.isdigit())
            
            if len(texto_limpo) > 8:
                texto_limpo = texto_limpo[:8]
            
            texto_formatado = ""
            if len(texto_limpo) > 0:
                texto_formatado = texto_limpo[0:2]
            if len(texto_limpo) > 2:
                texto_formatado += '/' + texto_limpo[2:4]
            if len(texto_limpo) > 4:
                texto_formatado += '/' + texto_limpo[4:8]
            
            if texto_formatado != instance.text:
                instance.unbind(text=self.aplicar_mascara_data)
                instance.text = texto_formatado
                instance.bind(text=self.aplicar_mascara_data)
                
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: setattr(instance, 'cursor', (len(texto_formatado), 0)), 0.01)
                
        finally:
            instance._processing = False
    
    def validar_data_br(self, data_br):
        """Valida se a data no formato BR é válida"""
        try:
            partes = data_br.split('/')
            if len(partes) != 3:
                return False
                
            dia, mes, ano = partes
            if len(dia) != 2 or len(mes) != 2 or len(ano) != 4:
                return False
                
            dia_int, mes_int, ano_int = int(dia), int(mes), int(ano)
            
            if mes_int < 1 or mes_int > 12:
                return False
            if dia_int < 1 or dia_int > 31:
                return False
            if ano_int < 1900 or ano_int > 2100:
                return False
                
            return True
        except:
            return False
    
    def atualizar_saldo_superior(self):
        """Atualiza o saldo mostrado na parte superior da tela"""
        sistema = App.get_running_app().sistema
        
        if not self.conta_bancaria_numero:
            return
            
        try:
            conta_info = sistema.contas_bancarias_empresa[self.conta_bancaria_numero]
            saldo = conta_info['saldo']
            moeda = conta_info['moeda']
            
            # Atualizar labels
            self.ids.lbl_saldo_total.text = f"{saldo:,.2f} {moeda}"
            self.ids.lbl_total_entradas.text = f"0.00 {moeda}"
            self.ids.lbl_total_saidas.text = f"0.00 {moeda}"
            self.ids.lbl_total_transacoes.text = "0"
            self.ids.lbl_periodo.text = "Últimos 30 dias"
            
            # Atualizar título com informações da conta
            self.ids.lbl_titulo_extrato.text = f"EXTRATO - {self.conta_bancaria_numero} - {conta_info['banco']} - {moeda}"
            
            print(f"✅ Saldo superior atualizado: {saldo:,.2f} {moeda}")
            
        except Exception as e:
            print(f"Erro ao atualizar saldo superior: {e}")
    
    def definir_periodo(self, periodo):
        """Define o período selecionado"""
        self.periodo_var = periodo
        print(f"🔧 Período definido para: {periodo}")
    
    def usar_periodo_personalizado(self, forcar_validacao=False):
        """Define o período como personalizado"""
        print("🔧 Usando período personalizado...")
        
        self.definir_periodo("personalizado")
        
        if forcar_validacao:
            data_inicio_br = self.ids.entry_data_inicio.text
            data_fim_br = self.ids.entry_data_fim.text
            
            print(f"🔧 Datas: {data_inicio_br} até {data_fim_br}")
            
            if not self.validar_data_br(data_inicio_br):
                self.mostrar_erro("Data inicial inválida! Use DD/MM/AAAA")
                return
                
            if not self.validar_data_br(data_fim_br):
                self.mostrar_erro("Data final inválida! Use DD/MM/AAAA")
                return
            
            self.mostrar_sucesso(f"Período personalizado definido: {data_inicio_br} a {data_fim_br}")
            
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.carregar_extrato(), 0.5)
    
    def on_focus_data_inicio(self, instance, value):
        """Manipula o foco no campo data início"""
        if value:
            print("🔧 Foco no campo data início")
            self.definir_periodo("personalizado")
    
    def on_focus_data_fim(self, instance, value):
        """Manipula o foco no campo data fim"""
        if value:
            print("🔧 Foco no campo data fim")
            self.definir_periodo("personalizado")

    def obter_nome_cliente_por_conta(self, sistema, conta_numero):
        """Obtém o nome do cliente por número da conta"""
        if conta_numero in sistema.contas:
            return sistema.contas[conta_numero].get('cliente_nome', 'Cliente')
        return 'Conta Externa'
    
    def obter_banco_por_conta(self, sistema, conta_numero):
        """Obtém o nome do banco por número da conta"""
        if conta_numero in sistema.contas:
            return sistema.contas[conta_numero].get('banco', 'Banco não informado')
        return 'Banco não informado'
    
    def obter_cliente_por_remetente(self, sistema, remetente_conta):
        """Busca o nome do cliente pelo número do remetente"""
        print(f"🔍 BUSCANDO CLIENTE PELO REMETENTE: {remetente_conta}")
        
        # 🔥 BUSCAR NAS CONTAS DO SISTEMA
        if remetente_conta in sistema.contas:
            cliente_nome = sistema.contas[remetente_conta].get('cliente_nome', '')
            if cliente_nome:
                print(f"   ✅ CLIENTE ENCONTRADO: {cliente_nome}")
                return cliente_nome
        
        # 🔥 BUSCAR NOS USUÁRIOS
        for username, user_data in sistema.usuarios.items():
            if 'contas' in user_data and remetente_conta in user_data['contas']:
                cliente_nome = user_data.get('empresa', user_data.get('nome', ''))
                if cliente_nome:
                    print(f"   ✅ CLIENTE ENCONTRADO EM USUÁRIO: {cliente_nome}")
                    return cliente_nome
        
        # 🔥 MAPEAMENTO DIRETO (fallback)
        clientes_mapeamento = {
            "202973672": "TEXACO LLC",
            "802194129": "PANTANAL COMERCIO IMP LTDA", 
            "873134916": "JACKS DISTRIBUIDORA"
        }
        
        if remetente_conta in clientes_mapeamento:
            cliente_nome = clientes_mapeamento[remetente_conta]
            print(f"   ✅ CLIENTE ENCONTRADO NO MAPEAMENTO: {cliente_nome}")
            return cliente_nome
        
        print(f"   ❌ CLIENTE NÃO ENCONTRADO")
        return "Cliente não informado"

    def inferir_banco_por_conta(self, conta_numero):
        """Infere o banco pelos primeiros dígitos da conta"""
        print(f"🔍 INFERINDO BANCO PELA CONTA: {conta_numero}")
        
        prefixos_bancos = {
            "202": "Banco do Brasil",
            "802": "Itaú Unibanco", 
            "873": "Bradesco",
            "001": "Banco do Brasil",
            "341": "Itaú",
            "237": "Bradesco",
            "104": "Caixa Econômica",
            "033": "Santander"
        }
        
        for prefixo, banco in prefixos_bancos.items():
            if conta_numero.startswith(prefixo):
                print(f"   ✅ BANCO INFERIDO: {banco}")
                return banco
        
        print(f"   ❌ BANCO NÃO IDENTIFICADO")
        return "Banco não informado"

    def obter_nome_remetente_por_conta(self, conta_numero):
        """Obtém o nome REAL do remetente por número da conta"""
        print(f"🔍 BUSCANDO NOME REAL DO REMETENTE PARA CONTA: {conta_numero}")
        
        remetentes_conhecidos = {
            "202973672": "OLD PARR LTDA",
            "802194129": "ATLAS IMEC LIMITADA", 
            "873134916": "SYMAS TURBO TDA"
        }
        
        if conta_numero in remetentes_conhecidos:
            nome_correto = remetentes_conhecidos[conta_numero]
            print(f"   ✅ REMETENTE ENCONTRADO: {nome_correto}")
            return nome_correto
        
        print(f"   ❌ REMETENTE NÃO ENCONTRADO PARA CONTA: {conta_numero}")
        return conta_numero

    def limpar_extrato(self):
        """Limpa a visualização do extrato"""
        if hasattr(self, 'ids'):
            container = self.ids.lista_transacoes
            container.clear_widgets()
            
            from kivy.uix.label import Label
            from kivy.metrics import dp
            
            lbl_carregando = Label(
                text="Carregando extrato...",
                font_size='14sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(lbl_carregando)
    
    def _safe_float(self, value, default=0.0):
        """Converte valor para float de forma segura, tratando None e strings vazias"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def carregar_extrato(self):
        """Carrega o extrato da conta bancária - VERSÃO CORRIGIDA (TODO PERÍODO + SALDO CORRETO)"""
        print("🔄 INICIANDO carregar_extrato CONTA BANCÁRIA - VERSÃO CORRIGIDA...")
        
        self.limpar_extrato()
        
        sistema = App.get_running_app().sistema
        
        if not self.conta_bancaria_numero:
            self.mostrar_erro("Nenhuma conta configurada!")
            return
        
        # 🔥 CARREGAR CONTAS DO SUPABASE (mesmo código)
        if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
            try:
                print("📡 Buscando contas bancárias no Supabase...")
                response = sistema.supabase.client.table('contas_bancarias_empresa')\
                    .select('*')\
                    .execute()
                
                if response.data:
                    sistema.contas_bancarias_empresa.clear()
                    for conta in response.data:
                        conta_num = conta['numero']
                        sistema.contas_bancarias_empresa[conta_num] = {
                            'numero': conta['numero'],
                            'banco': conta['banco'],
                            'agencia': conta.get('agencia', ''),
                            'moeda': conta['moeda'],
                            'saldo': float(conta['saldo']),
                            'tipo': conta.get('tipo', 'empresa'),
                            'data_criacao': conta.get('data_criacao', ''),
                            'saldo_inicial': float(conta.get('saldo_inicial', conta['saldo']))
                        }
                    print(f"✅ {len(response.data)} contas carregadas do Supabase")
            except Exception as e:
                print(f"⚠️ Erro ao carregar contas do Supabase: {e}")
        
        # Verificar se a conta existe
        if self.conta_bancaria_numero not in sistema.contas_bancarias_empresa:
            self.mostrar_erro("Conta bancária não encontrada!")
            return
        
        conta_info = sistema.contas_bancarias_empresa[self.conta_bancaria_numero]
        moeda = conta_info['moeda']
        saldo_atual = conta_info['saldo']
        
        print(f"🔍 Processando conta: {self.conta_bancaria_numero} - Saldo: {saldo_atual:,.2f} {moeda}")

        # 🔥 CARREGAR TRANSFERÊNCIAS DO SUPABASE
        if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
            try:
                print("📡 Buscando TODAS as transferências no Supabase...")
                response = sistema.supabase.client.table('transferencias')\
                    .select('*')\
                    .execute()
                
                if response.data:
                    sistema.transferencias.clear()
                    for transf in response.data:
                        transf_id = str(transf['id'])
                        
                        sistema.transferencias[transf_id] = {
                            'id': transf_id,
                            'tipo': 'internacional' if transf.get('tipo') == 'transferencia_internacional' else transf.get('tipo', ''),
                            'operacao': transf.get('operacao', ''),
                            'par_moedas': transf.get('par_moedas', ''),
                            
                            'valor': self._safe_float(transf.get('valor', transf.get('valor_origem'))),
                            'valor_origem': self._safe_float(transf.get('valor_origem', transf.get('valor'))),
                            'valor_destino': self._safe_float(transf.get('valor_destino')),
                            'cotacao': self._safe_float(transf.get('cotacao')),
                            
                            'conta_remetente': transf.get('conta_remetente', ''),
                            'conta_destinatario': transf.get('conta_destinatario', ''),
                            'conta_origem': transf.get('conta_origem', ''),
                            'conta_destino': transf.get('conta_destino', ''),
                            'conta_bancaria_credito': transf.get('conta_bancaria_credito', ''),
                            
                            'moeda': transf.get('moeda', transf.get('moeda_origem', '')),
                            'moeda_origem': transf.get('moeda_origem', ''),
                            'moeda_destino': transf.get('moeda_destino', ''),
                            
                            'status': transf.get('status', ''),
                            'data': transf.get('data', ''),
                            'data_conclusao': transf.get('data_conclusao', ''),
                            
                            'usuario': transf.get('usuario', ''),
                            'beneficiario': transf.get('beneficiario', ''),
                            'descricao': transf.get('descricao', ''),
                            'descricao_despesa': transf.get('descricao_despesa', ''),
                            'descricao_receita': transf.get('descricao_receita', ''),
                            
                            'tipo_ajuste': transf.get('tipo_ajuste', ''),
                            'descricao_ajuste': transf.get('descricao_ajuste', ''),
                            
                            'taxa_principal_registro': self._safe_float(transf.get('taxa_principal_registro', transf.get('taxa_cambio'))),
                            'taxa_cambio': self._safe_float(transf.get('taxa_cambio'))
                        }
                    
                    print(f"✅ {len(response.data)} transferências carregadas do Supabase")
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar transferências do Supabase: {e}")
                import traceback
                traceback.print_exc()

        # 🔥🔥🔥 CORREÇÃO 1: REMOVER FILTRO DE PERÍODO - SEMPRE TODO PERÍODO
        # Definir data de início fixa (01/01/2024)
        data_inicio_filtro = datetime.datetime(2024, 1, 1, 0, 0, 0)
        data_fim_filtro = datetime.datetime.now()
        
        print(f"🔧 PERÍODO CONFIGURADO (TODO PERÍODO):")
        print(f"   Data início: {data_inicio_filtro.strftime('%d/%m/%Y')}")
        print(f"   Data fim: {data_fim_filtro.strftime('%d/%m/%Y')}")
        
        # 🔥 OBTER SALDO INICIAL REAL DA CONTA
        saldo_inicial_real = conta_info.get('saldo_inicial', 0.0)
        print(f"💰 SALDO INICIAL REAL DA CONTA: {saldo_inicial_real:,.2f}")
        
        # Função auxiliar para parse de datas
        def parse_data(data_str):
            if not data_str:
                return datetime.datetime.now()
                
            try:
                if 'T' in data_str:
                    data_limpa = data_str.split('+')[0].split('Z')[0]
                    if '.' in data_limpa:
                        data_limpa = data_limpa.split('.')[0]
                    return datetime.datetime.fromisoformat(data_limpa)
                elif ' ' in data_str and ':' in data_str:
                    return datetime.datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                elif ' ' in data_str:
                    return datetime.datetime.strptime(data_str.split(' ')[0], "%Y-%m-%d")
                else:
                    return datetime.datetime.strptime(data_str, "%Y-%m-%d")
            except Exception as e:
                print(f"⚠️ Erro ao converter data '{data_str}': {e}")
                return datetime.datetime.now()
        
        # 🔥 COLETAR TODAS AS TRANSAÇÕES (SEM FILTRO DE PERÍODO NA COLETA)
        transacoes_todas = []
        transacoes_ids_utilizados = set()
        
        # 🔥 ADICIONAR SALDO INICIAL COMO PRIMEIRA TRANSAÇÃO (data mais antiga)
        transacao_saldo_inicial = {
            'data': '2024-01-01 00:00:00',
            'descricao': "SALDO INICIAL DA CONTA",
            'credito': 0.00,
            'debito': 0.00,
            'tipo': "Saldo Inicial",
            'moeda': moeda,
            'timestamp': datetime.datetime(2024, 1, 1, 0, 0, 0),
            'id': 'SALDO_INICIAL'
        }
        transacoes_todas.append(transacao_saldo_inicial)
        
        # 🔥 PROCESSAR TODAS AS TRANSAÇÕES (sem filtro de período)
        for transferencia_id, dados in sistema.transferencias.items():
            
            if not dados or not isinstance(dados, dict):
                continue
                
            status = dados.get('status', '')
            
            # Verificar se a transação envolve nossa conta bancária
            conta_envolvida = (
                dados.get('conta_remetente') == self.conta_bancaria_numero or 
                dados.get('conta_destinatario') == self.conta_bancaria_numero or
                dados.get('conta_origem') == self.conta_bancaria_numero or
                dados.get('conta_destino') == self.conta_bancaria_numero or
                dados.get('conta_bancaria_credito') == self.conta_bancaria_numero
            )
            
            if not conta_envolvida:
                continue
            
            # Incluir apenas transações concluídas
            if status not in ['completed', 'processing']:
                continue
            
            data_transacao = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            timestamp = self.parse_data_simples(data_transacao)
            
            # 🔥 FILTRO DE PERÍODO APLICADO AQUI - GARANTIR QUE ESTÁ DENTRO DO PERÍODO
            # 🔥 CORREÇÃO: Verificar se a transação está dentro do período (01/01/2024 até hoje)
            if timestamp < data_inicio_filtro or timestamp > data_fim_filtro:
                print(f"   ⏭️ Transação fora do período: {timestamp.date()} | ID: {transferencia_id}")
                continue
            
            tipo = dados.get('tipo', '')
            
            # 🔥 PROCESSAR CÂMBIOS ENTRE CONTAS
            if tipo == 'cambio_contas_empresa':
                conta_origem = dados.get('conta_origem')
                conta_destino = dados.get('conta_destino')
                valor_origem = dados.get('valor_origem', 0)
                valor_destino = dados.get('valor_destino', 0)
                moeda_origem = dados.get('moeda_origem', '')
                moeda_destino = dados.get('moeda_destino', '')
                taxa = dados.get('taxa_principal_registro') or dados.get('taxa_cambio') or 0
                
                if conta_origem == self.conta_bancaria_numero:
                    # SAÍDA de dinheiro
                    descricao = f"CÂMBIO ENTRE CONTAS - {moeda_origem} {valor_origem:,.2f} --> {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.6f})"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': valor_origem,
                        'debito': 0.00,
                        'tipo': "Câmbio entre Contas",
                        'moeda': moeda_origem,
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                    
                elif conta_destino == self.conta_bancaria_numero:
                    # ENTRADA de dinheiro
                    descricao = f"CÂMBIO ENTRE CONTAS - {moeda_origem} {valor_origem:,.2f} --> {moeda_destino} {valor_destino:,.2f} (Taxa: {taxa:.6f})"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': 0.00,
                        'debito': valor_destino,
                        'tipo': "Câmbio entre Contas",
                        'moeda': moeda_destino,
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
            
            # 🔥 PROCESSAR AJUSTES DE SALDO
            elif tipo == 'ajuste_saldo_empresa':
                if dados.get('conta_remetente') != self.conta_bancaria_numero:
                    continue
                
                tipo_ajuste_real = dados.get('tipo_ajuste', 'DÉBITO')
                descricao_ajuste = dados.get('descricao_ajuste', 'Ajuste de saldo')
                valor = dados['valor']
                
                if tipo_ajuste_real == 'DÉBITO':
                    # DÉBITO = ENTRADA (aumenta saldo)
                    descricao = f"AJUSTE - ENTRADA - {descricao_ajuste}"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': 0.00,
                        'debito': valor,
                        'tipo': "Ajuste de Saldo",
                        'moeda': dados['moeda'],
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                else:  # 'CRÉDITO'
                    # CRÉDITO = SAÍDA (diminui saldo)
                    descricao = f"AJUSTE - SAÍDA - {descricao_ajuste}"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': valor,
                        'debito': 0.00,
                        'tipo': "Ajuste de Saldo",
                        'moeda': dados['moeda'],
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                
                transacoes_todas.append(nova_transacao)
                transacoes_ids_utilizados.add(transferencia_id)
            
            # 🔥 PROCESSAR DEPÓSITOS
            elif tipo == 'deposito' or tipo == 'deposito_confirmado':
                if dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    descricao = dados.get('descricao', f"DEPÓSITO - {dados.get('banco_origem', 'Banco')}")
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': 0.00,
                        'debito': dados['valor'],
                        'tipo': "Depósito",
                        'moeda': dados['moeda'],
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
            
            # 🔥 PROCESSAR DESPESAS
            elif tipo == 'despesa':
                if dados.get('conta_remetente') == self.conta_bancaria_numero:
                    descricao = f"PAGAMENTO - {dados.get('descricao_despesa', 'Despesa')}"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': dados['valor'],
                        'debito': 0.00,
                        'tipo': "Despesa",
                        'moeda': dados['moeda'],
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
            
            # 🔥 PROCESSAR RECEITAS
            elif tipo == 'receita':
                if dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    descricao = f"RECEITA - {dados.get('descricao_receita', 'Receita')}"
                    nova_transacao = {
                        'data': data_transacao,
                        'descricao': descricao,
                        'credito': 0.00,
                        'debito': dados['valor'],
                        'tipo': "Receita",
                        'moeda': dados['moeda'],
                        'timestamp': timestamp,
                        'id': transferencia_id
                    }
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
            
            # 🔥 PROCESSAR OUTROS TIPOS (internacional, etc)
            elif dados.get('conta_bancaria_credito') == self.conta_bancaria_numero:
                # Transação onde nossa conta foi debitada (pagamento concluído)
                if dados.get('tipo') == 'internacional':
                    descricao = f"PAGAMENTO INTERNACIONAL - {dados.get('beneficiario', 'Destinatário')}"
                else:
                    destinatario_nome = self.obter_nome_cliente_por_conta(sistema, dados.get('conta_destinatario', 'N/A'))
                    descricao = f"PAGAMENTO TRANSFERÊNCIA - {destinatario_nome}"
                
                nova_transacao = {
                    'data': data_transacao,
                    'descricao': descricao,
                    'credito': dados['valor'],
                    'debito': 0.00,
                    'tipo': "Pagamento",
                    'moeda': dados['moeda'],
                    'timestamp': timestamp,
                    'id': f"{transferencia_id}_PAGAMENTO"
                }
                transacoes_todas.append(nova_transacao)
                transacoes_ids_utilizados.add(f"{transferencia_id}_PAGAMENTO")
        
        print(f"📊 TOTAL DE TRANSAÇÕES COLETADAS: {len(transacoes_todas)}")
        
        # 🔥🔥🔥 CORREÇÃO 2: CALCULAR SALDOS NA ORDEM CORRETA (CRONOLÓGICA)
        # Ordenar transações do MAIS ANTIGO para o MAIS NOVO para calcular saldos
        transacoes_ordenadas_calculo = sorted(transacoes_todas, key=lambda x: x['timestamp'])
        
        print(f"\n🔧 CALCULANDO SALDOS NA ORDEM CRONOLÓGICA:")
        
        # Calcular saldo sequencial
        saldo_sequencial = saldo_inicial_real
        for i, transacao in enumerate(transacoes_ordenadas_calculo):
            if transacao['tipo'] == "Saldo Inicial":
                transacao['saldo_apos'] = saldo_sequencial
                print(f"   {i+1}. SALDO INICIAL: {transacao['descricao']} | Saldo: {saldo_sequencial:,.2f}")
            else:
                saldo_anterior = saldo_sequencial
                # Débito aumenta saldo, Crédito diminui saldo
                saldo_sequencial += transacao['debito'] - transacao['credito']
                transacao['saldo_apos'] = saldo_sequencial
                print(f"   {i+1}. {transacao['timestamp'].strftime('%d/%m/%Y')} | Débito: {transacao['debito']:,.2f} | Crédito: {transacao['credito']:,.2f} | Saldo: {saldo_sequencial:,.2f}")
        
        # 🔥🔥🔥 CORREÇÃO 3: PARA EXIBIÇÃO, ORDENAR DO MAIS NOVO PARA O MAIS ANTIGO
        # Mas MANTENDO O SALDO_APOS CORRETO (já calculado na ordem cronológica)
        transacoes_exibicao = sorted(transacoes_ordenadas_calculo, key=lambda x: x['timestamp'], reverse=True)
        
        # Calcular totais
        total_entradas = sum(t['debito'] for t in transacoes_ordenadas_calculo if t['tipo'] != "Saldo Inicial")
        total_saidas = sum(t['credito'] for t in transacoes_ordenadas_calculo if t['tipo'] != "Saldo Inicial")
        
        print(f"\n💰 TOTAIS CALCULADOS:")
        print(f"   Total Entradas (Débito): {total_entradas:,.2f} {moeda}")
        print(f"   Total Saídas (Crédito): {total_saidas:,.2f} {moeda}")
        print(f"   Saldo Final: {saldo_sequencial:,.2f} {moeda}")
        
        # Atualizar interface
        self.atualizar_interface_extrato(
            transacoes_exibicao, 
            saldo_sequencial, 
            total_entradas, 
            total_saidas, 
            moeda, 
            "0"  # Período "Todo período"
        )
        
        print("✅ Extrato conta bancária carregado com sucesso (TODO PERÍODO + SALDO CORRETO)!")
    
    def calcular_saldo_ate_data_empresa(self, data_limite):
        """Calcula o saldo da conta bancária até uma data específica - LÓGICA NORMAL"""
        sistema = App.get_running_app().sistema
        
        if not self.conta_bancaria_numero:
            return 0.0
        
        saldo_acumulado = 0.0
        
        # Coletar TODAS as transações da conta bancária
        todas_transacoes = []
        
        # Adicionar saldo inicial zero
        todas_transacoes.append({
            'data': '2024-01-01 00:00:00',
            'credito': 0.00,
            'debito': 0.00,
            'timestamp': datetime.datetime(2024, 1, 1)
        })
        
        # Coletar transações de transferências
        for transferencia_id, dados in sistema.transferencias.items():
            if not dados or not isinstance(dados, dict):
                continue
                
            # 🔥 🔥 🔥 CORREÇÃO COMPLETA: PROCESSAR TODOS OS TIPOS DE TRANSAÇÕES
            conta_envolvida = False
            tipo_transacao = dados.get('tipo')
            
            # 1. VERIFICAR SE NOSSA CONTA ESTÁ ENVOLVIDA - CORREÇÃO: INCLUIR conta_bancaria_credito
            if tipo_transacao == 'cambio_contas_empresa':
                # Câmbios entre contas da empresa
                conta_origem = dados.get('conta_origem')
                conta_destino = dados.get('conta_destino')
                conta_envolvida = (
                    conta_origem == self.conta_bancaria_numero or 
                    conta_destino == self.conta_bancaria_numero
                )
                
            elif tipo_transacao in ['deposito', 'despesa', 'receita', 'ajuste_admin', 
                                    'internacional', 'transferencia_interancional', 'cambio', 
                                    'transferencia_interna_cliente', 'saque']:
                # Outros tipos de transações - CORREÇÃO: INCLUIR conta_bancaria_credito
                conta_envolvida = (
                    dados.get('conta_remetente') == self.conta_bancaria_numero or 
                    dados.get('conta_destinatario') == self.conta_bancaria_numero or
                    dados.get('conta_origem') == self.conta_bancaria_numero or
                    dados.get('conta_destino') == self.conta_bancaria_numero or
                    dados.get('conta_bancaria_credito') == self.conta_bancaria_numero  # 🔥 NOVA VERIFICAÇÃO
                )
            else:
                # Tipos não identificados - verificar campos genéricos
                conta_envolvida = (
                    dados.get('conta_remetente') == self.conta_bancaria_numero or 
                    dados.get('conta_destinatario') == self.conta_bancaria_numero or
                    dados.get('conta_origem') == self.conta_bancaria_numero or
                    dados.get('conta_destino') == self.conta_bancaria_numero or
                    dados.get('conta_bancaria_credito') == self.conta_bancaria_numero  # 🔥 NOVA VERIFICAÇÃO
                )
            
            if not conta_envolvida:
                continue
            
            if dados['status'] not in ['completed', 'processing']:
                continue
            
            data_transacao = dados.get('data', '2024-01-01 00:00:00')
            timestamp = self.parse_data_simples(data_transacao)
            valor = dados.get('valor', 0)
            
            # 🔥 DEBUG
            print(f"🎯 TRANSAÇÃO ENCONTRADA: {transferencia_id} | Tipo: {tipo_transacao}")
            
            # 2. PROCESSAR CADA TIPO DE TRANSAÇÃO
            if tipo_transacao == 'cambio_contas_empresa':
                # 🔥 CÂMBIO ENTRE CONTAS
                conta_origem = dados.get('conta_origem')
                conta_destino = dados.get('conta_destino')
                valor_origem = dados.get('valor_origem', 0)
                valor_destino = dados.get('valor_destino', 0)
                
                if conta_origem == self.conta_bancaria_numero:
                    # Nossa conta é ORIGEM → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor_origem,  # Diminui saldo
                        'debito': 0.00,
                        'timestamp': timestamp
                    })
                    print(f"💰 CÂMBIO ORIGEM: -{valor_origem:,.2f}")
                
                elif conta_destino == self.conta_bancaria_numero:
                    # Nossa conta é DESTINO → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor_destino,  # Aumenta saldo
                        'timestamp': timestamp
                    })
                    print(f"💰 CÂMBIO DESTINO: +{valor_destino:,.2f}")
            
            elif tipo_transacao == 'deposito':
                # 🔥 DEPÓSITO - Nossa conta é DESTINATÁRIO → ENTRADA
                if dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,  # Aumenta saldo
                        'timestamp': timestamp
                    })
                    print(f"💰 DEPÓSITO: +{valor:,.2f}")
            
            elif tipo_transacao == 'despesa':
                # 🔥 DESPESA - Nossa conta é REMETENTE → SAÍDA
                if dados.get('conta_remetente') == self.conta_bancaria_numero:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,  # Diminui saldo
                        'debito': 0.00,
                        'timestamp': timestamp
                    })
                    print(f"💰 DESPESA: -{valor:,.2f}")
            
            elif tipo_transacao == 'receita':
                # 🔥 RECEITA - Nossa conta é DESTINATÁRIO → ENTRADA
                if dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,  # Aumenta saldo
                        'timestamp': timestamp
                    })
                    print(f"💰 RECEITA: +{valor:,.2f}")
            
            elif tipo_transacao == 'ajuste_admin':
                # 🔥 AJUSTE - Verificar se nossa conta foi creditada/debitada
                conta_credito = dados.get('conta_bancaria_credito')
                if conta_credito == self.conta_bancaria_numero:
                    # AJUSTE POSITIVO → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,  # Aumenta saldo
                        'timestamp': timestamp
                    })
                    print(f"💰 AJUSTE POSITIVO: +{valor:,.2f}")
                elif dados.get('conta_remetente') == self.conta_bancaria_numero:
                    # AJUSTE NEGATIVO → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,  # Diminui saldo
                        'debito': 0.00,
                        'timestamp': timestamp
                    })
                    print(f"💰 AJUSTE NEGATIVO: -{valor:,.2f}")
            
            elif tipo_transacao in ['internacional', 'transferencia_interancional', 'cambio', 'transferencia_interna_cliente', 'saque']:
                # 🔥 TRANSAÇÕES INTERNACIONAIS/CÂMBIO/INTERNAS/SAQUES - Lógica padrão
                # CORREÇÃO: VERIFICAR TAMBÉM conta_bancaria_credito PARA SAÍDAS
                if (dados.get('conta_remetente') == self.conta_bancaria_numero or 
                    dados.get('conta_bancaria_credito') == self.conta_bancaria_numero):
                    # Nossa conta é REMETENTE ou CONTA_CREDITO → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,  # Diminui saldo
                        'debito': 0.00,
                        'timestamp': timestamp
                    })
                    print(f"💰 {tipo_transacao.upper()} SAÍDA: -{valor:,.2f}")
                
                elif dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    # Nossa conta é DESTINATÁRIO → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,  # Aumenta saldo
                        'timestamp': timestamp
                    })
                    print(f"💰 {tipo_transacao.upper()} ENTRADA: +{valor:,.2f}")
            
            else:
                # 🔥 TIPO NÃO IDENTIFICADO - Tentar lógica genérica
                print(f"⚠️ TIPO NÃO MAPEADO: {tipo_transacao}")
                if (dados.get('conta_remetente') == self.conta_bancaria_numero or 
                    dados.get('conta_bancaria_credito') == self.conta_bancaria_numero):
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,
                        'debito': 0.00,
                        'timestamp': timestamp
                    })
                elif dados.get('conta_destinatario') == self.conta_bancaria_numero:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp
                    })
        
        # Ordenar transações
        todas_transacoes_ordenadas = sorted(todas_transacoes, key=lambda x: x['timestamp'])
        
        # Calcular até o final do dia anterior
        data_fim_calculo = data_limite.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"🔧 CALCULANDO SALDO EMPRESA ATÉ: {data_fim_calculo}")
        
        # 🔥 LÓGICA NORMAL: Débito aumenta, Crédito diminui
        for transacao in todas_transacoes_ordenadas:
            if transacao['timestamp'] <= data_fim_calculo:
                saldo_acumulado += transacao['debito'] - transacao['credito']
                print(f"  ✅ INCLUÍDA: {transacao['timestamp']} | Crédito: {transacao['credito']:,.2f} | Débito: {transacao['debito']:,.2f} | Saldo: {saldo_acumulado:,.2f}")
            else:
                break
        
        print(f"💰 SALDO FINAL CALCULADO EMPRESA: {saldo_acumulado:,.2f}")
        
        return saldo_acumulado
    
    def parse_data_simples(self, data_str):
        """Versão CORRIGIDA do parse_data - trata formato ISO com T"""
        if not data_str:
            return datetime.datetime.now()
            
        try:
            # 1. Tentar formato ISO com T (2025-11-28T10:04:24.541064)
            if 'T' in data_str:
                # Remover timezone e microssegundos se existirem
                data_limpa = data_str.split('+')[0].split('Z')[0]
                if '.' in data_limpa:
                    data_limpa = data_limpa.split('.')[0]  # Remover microssegundos
                return datetime.datetime.fromisoformat(data_limpa)
            
            # 2. Tentar formato com espaço (2025-11-28 10:04:24)
            elif ' ' in data_str and ':' in data_str:
                return datetime.datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            
            # 3. Tentar apenas data (2025-11-28)
            elif ' ' in data_str:
                return datetime.datetime.strptime(data_str.split(' ')[0], "%Y-%m-%d")
            
            # 4. Tentar formato básico
            else:
                return datetime.datetime.strptime(data_str, "%Y-%m-%d")
                
        except Exception as e:
            print(f"⚠️ Erro ao converter data '{data_str}': {e}")
            return datetime.datetime.now()
    
    def formatar_data_para_iso(self, data_br):
        """Converte data de DD/MM/AAAA para AAAA-MM-DD"""
        try:
            partes = data_br.split('/')
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
        except:
            pass
        return data_br
    
    def formatar_data_curta(self, data_string):
        """Formata data curta para exibição: DD/MM/AAAA"""
        try:
            # Extrair apenas a parte da data
            if 'T' in data_string:
                data = data_string.split('T')[0]
            elif ' ' in data_string:
                data = data_string.split(' ')[0]
            else:
                data = data_string
            
            # Formatar DD/MM/AAAA
            if '-' in data:
                ano, mes, dia = data.split('-')
                return f"{dia}/{mes}/{ano}"
            return data
        except:
            return data_string

    def scroll_para_topo(self):
        """Rola automaticamente para o topo"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'scroll_extrato'):
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_extrato, 'scroll_y', 1), 0.1)
    
    def atualizar_interface_extrato(self, transacoes, saldo_atual, total_entradas, total_saidas, moeda, periodo):
        """Atualiza a interface com os dados do extrato - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'ids'):
            return
        
        # Salvar dados para possível exportação
        self.transacoes_filtradas = transacoes
        self.saldo_final = saldo_atual  # 🔥 SALVAR O SALDO ATUAL
        self.total_entradas = total_entradas
        self.total_saidas = total_saidas
        
        # Limpar transações anteriores
        container = self.ids.lista_transacoes
        container.clear_widgets()
        
        # Adicionar header
        header = self.criar_header_colunas()
        container.add_widget(header)
        
        # Adicionar transações
        for transacao in transacoes:
            card = CardTransacaoExtrato(transacao)
            container.add_widget(card)
        
        # 🔥 CORREÇÃO: Usar SEMPRE o saldo_atual passado como parâmetro
        # NÃO tentar recalcular a partir das transações
        self.atualizar_resumo(saldo_atual, total_entradas, total_saidas, len(transacoes), moeda, periodo)
        
        self.scroll_para_topo()
    
    def criar_header_colunas(self):
        """Cria o header das colunas do extrato"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, RoundedRectangle
        from kivy.metrics import dp
        
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[10, 5, 10, 5],
            spacing=dp(5)
        )
        
        with header.canvas.before:
            Color(0.15, 0.20, 0.27, 1)
            header.rect = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[5,]
            )
        header.bind(pos=self._atualizar_header_rect, size=self._atualizar_header_rect)
        
        # 🔥 ALTERADO: Ajuste das larguras das colunas
        colunas = [
            ('Data', 0.08),        # 🔥 ALTERADO: era 0.15
            ('Descrição', 0.51),   # 🔥 ALTERADO: era 0.35  
            ('Crédito', 0.08),     # 🔥 ALTERADO: era 0.125
            ('Débito', 0.08),      # 🔥 ALTERADO: era 0.125
            ('Saldo', 0.13),       # 🔥 ALTERADO: era 0.15
            ('Detalhes', 0.1)      # 🔥 MANTIDO: 0.1
        ]
        
        for texto, largura in colunas:
            lbl = Label(
                text=texto,
                font_size='11sp',
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                text_size=(None, None),
                halign='center' if texto != 'Descrição' else 'left',
                valign='middle'
            )
            lbl.size_hint_x = largura
            header.add_widget(lbl)
        
        return header
    
    def _atualizar_header_rect(self, instance, value):
        """Atualiza o retângulo do header"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def atualizar_resumo(self, saldo_atual, total_entradas, total_saidas, total_transacoes, moeda, periodo):
        """Atualiza o painel de resumo - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'ids'):
            return
        
        print(f"🔥 DEBUG RESUMO CONTA BANCÁRIA:")
        print(f"  Saldo atual recebido: {saldo_atual:,.2f}")
        print(f"  Total entradas: {total_entradas:,.2f}")
        print(f"  Total saídas: {total_saidas:,.2f}")
        print(f"  Total transações: {total_transacoes}")
        
        # 🔥 CORREÇÃO CRÍTICA: Usar o saldo_atual que foi passado como parâmetro
        # NÃO recalcular ou usar outro valor
        saldo_final = saldo_atual
        
        self.ids.lbl_saldo_total.text = f"{saldo_final:,.2f} {moeda}"
        self.ids.lbl_total_entradas.text = f"{total_entradas:,.2f} {moeda}"
        self.ids.lbl_total_saidas.text = f"{total_saidas:,.2f} {moeda}"
        self.ids.lbl_total_transacoes.text = f"{total_transacoes}"
        
        if periodo == "0":
            periodo_texto = "Todo período"
        elif periodo == "personalizado":
            data_inicio_br = self.ids.entry_data_inicio.text
            data_fim_br = self.ids.entry_data_fim.text
            periodo_texto = f"{data_inicio_br} a {data_fim_br}"
        else:
            periodo_texto = f"Últimos {periodo} dias"
        
        self.ids.lbl_periodo.text = periodo_texto
        
        print(f"✅ RESUMO CONTA BANCÁRIA ATUALIZADO:")
        print(f"  Saldo: {saldo_final:,.2f} {moeda}")
        print(f"  Entradas: {total_entradas:,.2f} {moeda}")
        print(f"  Saídas: {total_saidas:,.2f} {moeda}")

    def exportar_extrato_pdf(self):
        """Exporta o extrato da conta bancária para PDF"""
        try:
            # Verificar se há transações para exportar
            if not hasattr(self, 'transacoes_filtradas') or not self.transacoes_filtradas:
                self.mostrar_erro("Não há transações para exportar!")
                return
            
            print("📊 Iniciando exportação de extrato para PDF...")
            
            # Obter sistema e conta atual
            sistema = App.get_running_app().sistema
            
            if not self.conta_bancaria_numero:
                self.mostrar_erro("Nenhuma conta configurada!")
                return
            
            # Verificar se a conta existe
            if self.conta_bancaria_numero not in sistema.contas_bancarias_empresa:
                self.mostrar_erro("Conta bancária não encontrada!")
                return
            
            conta_info = sistema.contas_bancarias_empresa[self.conta_bancaria_numero]
            
            # 1. DADOS DA CONTA
            dados_conta = {
                'numero': conta_info['numero'],
                'banco': conta_info['banco'],
                'agencia': conta_info.get('agencia', 'N/A'),
                'titular': 'EMPRESA - Câmbio Bank',
                'moeda': conta_info['moeda'],
                'saldo': conta_info['saldo'],
                'tipo': conta_info.get('tipo', 'empresa')
            }
            
            # 2. DADOS DO RESUMO
            dados_resumo = {
                'saldo_final': getattr(self, 'saldo_final', 0.0),
                'entradas': getattr(self, 'total_entradas', 0.0),
                'saidas': getattr(self, 'total_saidas', 0.0),
                'total_transacoes': len(self.transacoes_filtradas),
                'periodo': self.ids.lbl_periodo.text if hasattr(self, 'ids') and 'lbl_periodo' in self.ids else 'N/A'
            }
            
            print(f"📋 Dados para PDF:")
            print(f"   Conta: {dados_conta['numero']}")
            print(f"   Banco: {dados_conta['banco']}")
            print(f"   Moeda: {dados_conta['moeda']}")
            print(f"   Saldo: {dados_conta['saldo']:,.2f}")
            print(f"   Transações: {dados_resumo['total_transacoes']}")
            print(f"   Período: {dados_resumo['periodo']}")
            
            # 🔥 CORREÇÃO: Criar PDFGenerator aqui mesmo
            pdf_generator = PDFGenerator()
            
            # Mostrar popup de carregamento
            self.mostrar_popup_carregando("Gerando PDF...")
            
            from kivy.clock import Clock
            
            def gerar_pdf_thread(dt):
                """Função para gerar PDF em background"""
                try:
                    # Ordenar transações do mais antigo para o mais novo (para PDF)
                    transacoes_ordenadas = sorted(
                        self.transacoes_filtradas, 
                        key=lambda x: x.get('timestamp', datetime.datetime.min)
                    )
                    
                    print("🔍 DEBUG - Primeiras transações no PDF:")
                    for i, t in enumerate(transacoes_ordenadas[:3]):
                        data = t.get('data', '')[:10]
                        descricao = t.get('descricao', '')[:30]
                        print(f"   {i+1}. {data} | {descricao}...")
                    
                    # Gerar o PDF
                    caminho_pdf = pdf_generator.gerar_extrato(
                        transacoes=transacoes_ordenadas,
                        dados_conta=dados_conta,
                        dados_resumo=dados_resumo
                    )
                    
                    # Fechar popup de carregamento
                    Clock.schedule_once(lambda dt: self.fechar_popup_carregando(), 0.1)
                    
                    if caminho_pdf:
                        # Mostrar sucesso
                        Clock.schedule_once(lambda dt: self.mostrar_sucesso_pdf(caminho_pdf), 0.2)
                    else:
                        Clock.schedule_once(lambda dt: self.mostrar_erro("Falha ao gerar PDF!"), 0.2)
                        
                except Exception as e:
                    print(f"❌ Erro ao gerar PDF: {e}")
                    import traceback
                    traceback.print_exc()
                    Clock.schedule_once(lambda dt: self.fechar_popup_carregando(), 0.1)
                    Clock.schedule_once(lambda dt: self.mostrar_erro(f"Erro: {str(e)[:50]}..."), 0.2)
            
            # Executar em background
            Clock.schedule_once(gerar_pdf_thread, 0.5)
            
        except Exception as e:
            print(f"❌ Erro no exportar_extrato_pdf: {e}")
            self.mostrar_erro(f"Erro ao exportar PDF: {str(e)[:50]}...")

    def mostrar_popup_carregando(self, mensagem="Processando..."):
        """Mostra popup de carregamento"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_carregando = Label(
            text=mensagem,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            text_size=(300, None),
            halign='center'
        )
        
        content.add_widget(lbl_carregando)
        
        self.popup_carregando = Popup(
            title='Gerando PDF',
            content=content,
            size_hint=(None, None),
            size=(350, 150),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        self.popup_carregando.open()

    def fechar_popup_carregando(self):
        """Fecha o popup de carregamento"""
        if hasattr(self, 'popup_carregando'):
            self.popup_carregando.dismiss()

    def mostrar_sucesso_pdf(self, caminho_pdf):
        """Mostra popup de sucesso com opção para abrir o PDF"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        import os
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Mensagem de sucesso
        lbl_sucesso = Label(
            text="✅ PDF gerado com sucesso!",
            font_size='16sp',
            bold=True,
            color=(0.1, 0.8, 0.1, 1),
            text_size=(350, None),
            halign='center'
        )
        
        lbl_caminho = Label(
            text=f"Arquivo salvo em:\n{os.path.basename(caminho_pdf)}",
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            text_size=(350, None),
            halign='center'
        )
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_fechar = Button(
            text='FECHAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_abrir = Button(
            text='ABRIR PDF',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_fechar)
        botoes_layout.add_widget(btn_abrir)
        
        content.add_widget(lbl_sucesso)
        content.add_widget(lbl_caminho)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='PDF Gerado',
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        def abrir_pdf(instance):
            """Abre o PDF no visualizador padrão do sistema"""
            try:
                import platform
                import subprocess
                import os
                
                sistema_operacional = platform.system()
                
                if sistema_operacional == 'Windows':
                    os.startfile(caminho_pdf)
                elif sistema_operacional == 'Darwin':  # macOS
                    subprocess.call(['open', caminho_pdf])
                else:  # Linux
                    subprocess.call(['xdg-open', caminho_pdf])
                
                popup.dismiss()
                
            except Exception as e:
                print(f"❌ Erro ao abrir PDF: {e}")
                self.mostrar_erro("Não foi possível abrir o PDF automaticamente.")
                popup.dismiss()
        
        btn_abrir.bind(on_press=abrir_pdf)
        btn_fechar.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def voltar_contas_bancarias(self):
        """Volta para a tela de contas bancárias"""
        self.manager.current = 'contas_bancarias'
    
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
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.1, 0.8, 0.1, 1),
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
            title='Sucesso',
            title_color=(0.1, 0.8, 0.1, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

class CardTransacaoExtrato(BoxLayout):
    """Card para exibir uma transação no extrato da conta bancária"""
    
    def __init__(self, transacao, **kwargs):
        super().__init__(**kwargs)
        self.transacao = transacao
        
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [10, 5, 10, 5]
        self.spacing = dp(5)
        
        # Background do card
        with self.canvas.before:
            Color(0.15, 0.20, 0.27, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        # Criar os widgets do card
        self.criar_widgets()
    
    def _atualizar_rect(self, instance, value):
        """Atualiza o retângulo de background"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def formatar_data_para_exibicao(self, data_string):
        """Formata data para exibição amigável: 2025-11-28 10:04"""
        try:
            # Remover microssegundos e timezone se existir
            if 'T' in data_string:
                # Formato ISO: 2025-11-28T10:04:24.541064
                data_str_limpa = data_string.split('T')[0] + ' ' + data_string.split('T')[1].split('.')[0]
            else:
                # Formato normal: 2025-11-28 10:04:24
                data_str_limpa = data_string.split('.')[0] if '.' in data_string else data_string
            
            # Converter para datetime
            if 'T' in data_str_limpa:
                # Ainda tem T? Remover
                data_str_limpa = data_str_limpa.replace('T', ' ')
            
            # Formatar para datetime
            try:
                data_obj = datetime.datetime.strptime(data_str_limpa, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    data_obj = datetime.datetime.strptime(data_str_limpa, "%Y-%m-%d")
                except:
                    return data_string.split(' ')[0]  # Fallback
            
            # Formatar para exibição: DD/MM/AAAA HH:MM
            return data_obj.strftime("%d/%m/%Y %H:%M")
            
        except Exception as e:
            print(f"⚠️ Erro ao formatar data '{data_string}': {e}")
            return data_string.split(' ')[0] if ' ' in data_string else data_string

    def criar_widgets(self):
        """Cria os widgets do card de transação"""
        transacao = self.transacao
        
        # Data - REDUZIDA
        data_str = self.formatar_data_para_exibicao(transacao['data'])
        lbl_data = Label(
            text=data_str,
            font_size='11sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_x=0.08,  # 🔥 ALTERADO: era 0.15
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        self.add_widget(lbl_data)
        
        # Descrição - AUMENTADA
        descricao = transacao['descricao']
        lbl_descricao = Label(
            text=descricao,
            font_size='11sp',
            color=(1, 1, 1, 1),
            size_hint_x=0.51,
            text_size=(self.width * 0.51, None),
            halign='center',
            valign='middle',
            shorten=False
        )
        # Atualiza a text_size quando o widget for redimensionado
        lbl_descricao.bind(width=self._atualizar_texto_descricao)
        self.add_widget(lbl_descricao)
        
        # Crédito (Saída) - REDUZIDA
        credito = transacao['credito']
        cor_credito = (0.8, 0.2, 0.2, 1) if credito > 0 else (0.5, 0.5, 0.5, 1)
        lbl_credito = Label(
            text=f"{credito:,.2f}" if credito > 0 else "",
            font_size='11sp',
            color=cor_credito,
            size_hint_x=0.08,  # 🔥 ALTERADO: era 0.125
            text_size=(None, None),
            halign='right',
            valign='middle',
            bold=True
        )
        self.add_widget(lbl_credito)
        
        # Débito (Entrada) - REDUZIDA
        debito = transacao['debito']
        cor_debito = (0.1, 0.6, 0.1, 1) if debito > 0 else (0.5, 0.5, 0.5, 1)
        lbl_debito = Label(
            text=f"{debito:,.2f}" if debito > 0 else "",
            font_size='11sp',
            color=cor_debito,
            size_hint_x=0.08,  # 🔥 ALTERADO: era 0.125
            text_size=(None, None),
            halign='right',
            valign='middle',
            bold=True
        )
        self.add_widget(lbl_debito)
        
        # Saldo - REDUZIDA
        saldo = transacao.get('saldo_apos', 0)
        cor_saldo = (0.8, 0.2, 0.2, 1) if saldo < 0 else (0.23, 0.51, 0.96, 1)
        lbl_saldo = Label(
            text=f"{saldo:,.2f}",
            font_size='11sp',
            color=cor_saldo,
            size_hint_x=0.13,  # 🔥 ALTERADO: era 0.15
            text_size=(None, None),
            halign='right',
            valign='middle',
            bold=True
        )
        self.add_widget(lbl_saldo)
        
        # Detalhes (botão) - MANTIDO IGUAL
        btn_detalhes = Button(
            text='Detalhes',
            font_size='12sp',
            size_hint_x=0.1,  # 🔥 MANTIDO: 0.1
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_detalhes.bind(on_press=self.mostrar_detalhes)
        self.add_widget(btn_detalhes)
    
    def _atualizar_texto_descricao(self, instance, value):
        """Atualiza o text_size da descrição quando o tamanho muda"""
        if hasattr(instance, 'text_size'):
            instance.text_size = (instance.width, None)

    def mostrar_detalhes(self, instance):
        """Mostra detalhes da transação"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        transacao = self.transacao
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Título
        content.add_widget(Label(
            text='DETALHES DA TRANSAÇÃO',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Informações
        info_layout = BoxLayout(orientation='vertical', spacing=5)
        
        info_items = [
            f"Data: {transacao['data']}",
            f"Descrição: {transacao['descricao']}",
            f"Tipo: {transacao.get('tipo', 'N/A')}",
            f"Moeda: {transacao.get('moeda', 'N/A')}",
            f"Crédito: {transacao['credito']:,.2f}",
            f"Débito: {transacao['debito']:,.2f}",
            f"Saldo após: {transacao.get('saldo_apos', 0):,.2f}"
        ]
        
        for info in info_items:
            info_layout.add_widget(Label(
                text=info,
                font_size='12sp',
                color=(0.9, 0.9, 0.9, 1),
                text_size=(350, None),
                halign='left'
            ))
        
        content.add_widget(info_layout)
        
        # Botão Fechar
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(btn_fechar)
        
        popup = Popup(
            title='Detalhes da Transação',
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()
