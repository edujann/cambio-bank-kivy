
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.clock import Clock 
from kivy.uix.tabbedpanel import TabbedPanelHeader  # 🔥 IMPORT ADICIONADO
from screens.gerenciar_cliente_detalhe import TelaGerenciarClienteDetalhe
from kivy.factory import Factory
from .campos import CampoValor
from kivy.uix.widget import Widget
import datetime
import random

# 🔥 Registrar as classes personalizadas para as abas
Factory.register('TabbedPanelHeader', cls=TabbedPanelHeader)

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

    # 🔥 NOVO MÉTODO: Permitir MUITAS casas decimais
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

# 🔥 AQUI - DEPOIS da classe TextInputTaxaCambio e ANTES da próxima classe
Factory.register('TextInputTaxaCambio', cls=TextInputTaxaCambio)


class CardCliente(BoxLayout):
    """Card para exibir informações de um cliente - VERSÃO UMA LINHA"""
    
    def __init__(self, username, dados_cliente, contas, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)  # 🔥 Altura reduzida para uma linha
        self.padding = [dp(15), dp(8), dp(15), dp(8)]
        self.spacing = dp(15)
        
        self.username = username
        self.dados_cliente = dados_cliente
        self.contas = contas
        self.tela_pai = tela_pai
        
        # Background do card
        with self.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(6),]
            )
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        self.criar_conteudo_uma_linha()
    
    def _atualizar_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def criar_conteudo_uma_linha(self):
        """Cria o conteúdo em uma única linha"""
        
        # 🔥 COLUNA 1: Nome do Cliente (40%)
        coluna_nome = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        lbl_nome = Label(
            text=self.dados_cliente['nome'],
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            text_size=(None, None),
            valign='middle'
        )
        
        lbl_username = Label(
            text=f"({self.username})",
            font_size='11sp',
            color=(0.85, 0.88, 0.92, 0.8),
            halign='left',
            text_size=(None, None),
            valign='middle'
        )
        
        coluna_nome.add_widget(lbl_nome)
        coluna_nome.add_widget(lbl_username)
        
        # 🔥 COLUNA 2: Moedas Disponíveis (40%)
        coluna_moedas = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        moedas_texto = self.obter_moedas_formatadas()
        lbl_moedas = Label(
            text=moedas_texto,
            font_size='12sp',
            color=(0.85, 0.88, 0.92, 1),
            halign='center',
            text_size=(None, None),
            valign='middle'
        )
        
        saldo_total = self.calcular_saldo_total()
        lbl_saldo = Label(
            text=f"Saldo Total: {saldo_total:,.2f}",
            font_size='11sp',
            color=(0.23, 0.51, 0.96, 1),
            halign='center',
            text_size=(None, None),
            valign='middle'
        )
        
        coluna_moedas.add_widget(lbl_moedas)
        coluna_moedas.add_widget(lbl_saldo)
        
        # 🔥 COLUNA 3: Botão Gerenciar (20%)
        coluna_botao = BoxLayout(orientation='vertical', size_hint_x=0.2)
        
        btn_gerenciar = Button(
            text='GERENCIAR',
            font_size='11sp',
            bold=True,
            size_hint=(0.8, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0, 0, 0, 0),  # Fundo transparente
            background_normal='',
            color=(1, 1, 1, 1)
        )
        btn_gerenciar.bind(on_press=self.abrir_gerenciamento_cliente)

        # Efeito visual do botão
        with btn_gerenciar.canvas.before:
            # Sombra sutil
            Color(0.04, 0.08, 0.16, 0.6)
            RoundedRectangle(
                pos=(btn_gerenciar.x, btn_gerenciar.y - dp(1)),
                size=(btn_gerenciar.width, btn_gerenciar.height),
                radius=[dp(4),]
            )
            
            # Botão principal
            Color(0.08, 0.16, 0.32, 1)
            RoundedRectangle(
                pos=btn_gerenciar.pos,
                size=btn_gerenciar.size,
                radius=[dp(4),]
            )

        # Atualizar posição da sombra quando o botão se move
        def atualizar_sombra(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                # Sombra
                Color(0.04, 0.08, 0.16, 0.6)
                RoundedRectangle(
                    pos=(instance.x, instance.y - dp(1)),
                    size=(instance.width, instance.height),
                    radius=[dp(4),]
                )
                # Botão
                Color(0.08, 0.16, 0.32, 1)
                RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(4),]
                )

        btn_gerenciar.bind(pos=atualizar_sombra, size=atualizar_sombra)
        
        # Container para centralizar o botão
        botao_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        botao_container.add_widget(Widget(size_hint_y=0.2))  # Espaço acima
        botao_container.add_widget(btn_gerenciar)
        botao_container.add_widget(Widget(size_hint_y=0.2))  # Espaço abaixo
        
        coluna_botao.add_widget(botao_container)
        
        # 🔥 ADICIONAR AS 3 COLUNAS
        self.add_widget(coluna_nome)
        self.add_widget(coluna_moedas)
        self.add_widget(coluna_botao)

    def obter_moedas_formatadas(self):
        """Retorna as moedas formatadas de forma compacta"""
        if not self.contas:
            return "Sem contas"
        
        moedas = {}
        for conta in self.contas:
            moeda = conta['moeda']
            if moeda not in moedas:
                moedas[moeda] = 0
            moedas[moeda] += 1
        
        # Formatar como: "USD, EUR, BRL" ou "USD (2), EUR (1)"
        texto_moedas = []
        for moeda, quantidade in moedas.items():
            if quantidade > 1:
                texto_moedas.append(f"{moeda} ({quantidade})")
            else:
                texto_moedas.append(moeda)
        
        return ", ".join(texto_moedas)

    def calcular_saldo_total(self):
        """Calcula saldo total"""
        if not self.contas:
            return 0.0
        return sum(conta['saldo'] for conta in self.contas)

    def abrir_gerenciamento_cliente(self, instance):
        """Abre a tela de gerenciamento detalhado do cliente"""
        try:
            if 'gerenciar_cliente_detalhe' not in self.tela_pai.manager.screen_names:
                self.tela_pai.mostrar_erro("Tela de gerenciamento não disponível")
                return
            
            tela_detalhe = self.tela_pai.manager.get_screen('gerenciar_cliente_detalhe')
            sistema = App.get_running_app().sistema
            dados_cliente = sistema.usuarios[self.username]
            
            tela_detalhe.carregar_dados_cliente(self.username, dados_cliente)
            self.tela_pai.manager.current = 'gerenciar_cliente_detalhe'
            
        except Exception as e:
            self.tela_pai.mostrar_erro(f"Erro ao abrir gerenciamento: {str(e)}")

class CardTransacao(BoxLayout):
    """Card para exibir uma transação no extrato - VERSÃO COM DATA BR"""
    
    def __init__(self, transacao, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [10, 5, 10, 5]
        self.spacing = dp(5)
        
        # Definir cor baseada no tipo - CORES MAIS SUAVES
        if transacao.get('credito', 0) > 0:
            cor_fundo = (0.85, 0.95, 0.85, 1)  # 🟢 Verde bem suave
        elif transacao.get('debito', 0) > 0:
            cor_fundo = (0.95, 0.85, 0.85, 1)  # 🔴 Vermelho bem suave
        else:
            cor_fundo = (0.92, 0.94, 0.96, 1)  # ⚪ Cinza azulado suave (saldo inicial)
        
        # Background do card
        with self.canvas.before:
            Color(*cor_fundo)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        self.criar_conteudo(transacao)
    
    def _atualizar_rect(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def criar_conteudo(self, transacao):
        """Cria o conteúdo do card com data no formato BR"""
        
        # 🔥🔥🔥 CORREÇÃO: LIDAR COM FORMATO ISO (com T)
        data_original = transacao['data']
        
        # Se tiver formato ISO com T, converter
        if 'T' in data_original:
            # Formato: 2025-11-28T10:04:24.541064 → 2025-11-28
            data_original = data_original.split('T')[0]
        
        # Agora formatar normalmente
        data_sem_hora = data_original.split(' ')[0] if ' ' in data_original else data_original
        
        try:
            partes = data_sem_hora.split('-')
            if len(partes) == 3:
                data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"
            else:
                data_formatada = data_sem_hora
        except:
            data_formatada = data_sem_hora
        
        # Coluna 1: Data (12%) - REDUZIDA PELA METADE
        col_data = BoxLayout(orientation='vertical', size_hint_x=0.10)  # 🔥 12%
        lbl_data = Label(
            text=data_formatada,  # 🔥 SUA DATA FORMATADA
            font_size='11sp',
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        col_data.add_widget(lbl_data)
        
        # Coluna 2: Descrição (48%) - AUMENTADA SIGNIFICATIVAMENTE
        col_descricao = BoxLayout(orientation='vertical', size_hint_x=0.60)  # 🔥 60%
        lbl_descricao = Label(
            text=transacao['descricao'],
            font_size='11sp',
            color=(0.3, 0.3, 0.3, 1),
            text_size=(None, None),
            halign='left',
            valign='middle',
            shorten=True,  # 🔥 PERMITE ENCURTAR TEXTO SE NECESSÁRIO
            shorten_from='right'  # 🔥 ENCURTA DO FIM
        )
        col_descricao.add_widget(lbl_descricao)
        
        # Coluna 3: Crédito (15%) - MANTIDO
        col_credito = BoxLayout(orientation='vertical', size_hint_x=0.10)
        credito = transacao.get('credito', 0)
        lbl_credito = Label(
            text=f"{credito:,.2f}" if credito > 0 else "",
            font_size='12sp',
            color=(0.1, 0.6, 0.1, 1) if credito > 0 else (0.3, 0.3, 0.3, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_credito.add_widget(lbl_credito)
        
        # Coluna 4: Débito (15%) - MANTIDO
        col_debito = BoxLayout(orientation='vertical', size_hint_x=0.10)
        debito = transacao.get('debito', 0)
        lbl_debito = Label(
            text=f"{debito:,.2f}" if debito > 0 else "",
            font_size='12sp',
            color=(0.8, 0.2, 0.2, 1) if debito > 0 else (0.3, 0.3, 0.3, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_debito.add_widget(lbl_debito)
        
        # Coluna 5: Saldo (10%) - MANTIDO
        col_saldo = BoxLayout(orientation='vertical', size_hint_x=0.10)
        saldo_apos = transacao.get('saldo_apos', 0)
        
        cor_saldo = (0.8, 0.2, 0.2, 1) if saldo_apos < 0 else (0.1, 0.3, 0.8, 1)
        
        lbl_saldo = Label(
            text=f"{saldo_apos:,.2f}",
            font_size='11sp',
            color=cor_saldo,
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_saldo.add_widget(lbl_saldo)
        
        # Adicionar todas as colunas
        self.add_widget(col_data)
        self.add_widget(col_descricao)
        self.add_widget(col_credito)
        self.add_widget(col_debito)
        self.add_widget(col_saldo)


class TelaGerenciarContas(Screen):
    """Tela para gerenciar contas de clientes (Admin)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operacao_atual = 'credito'  # credito ou debito
        
        # Agendar a configuração inicial dos botões
        from kivy.clock import Clock
        Clock.schedule_once(self._configurar_botoes_iniciais, 0.1)
    
    def _configurar_botoes_iniciais(self, dt):
        """Configura o estado inicial dos botões de operação"""
        if hasattr(self, 'ids'):
            # Definir crédito como padrão
            self.definir_operacao('credito')

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - VERSÃO SIMPLIFICADA PARA TESTE"""
        from kivy.core.window import Window
        
        # Definir tamanho da janela
        Window.size = (1400, 900)
        
        # 🔥 MOVER PARA ESQUERDA - VERSÃO SIMPLES
        Window.left = 300
        Window.top = 70

        # 🔥 ATUALIZAR SALDOS NOS SPINNERS
        self.atualizar_saldos_spinners_extrato()

        # Carregar dados SIMPLES - sem callbacks complexos
        from kivy.clock import Clock
        
        def carregar_simples(dt):
            # Apenas o essencial - versão mínima
            try:
                print("🎯 CARREGAMENTO SIMPLES INICIADO")
                self.carregar_dados_iniciais()
                print("✅ Carregamento básico concluído")
            except Exception as e:
                print(f"❌ Erro no carregamento simples: {e}")
        
        # Apenas uma chamada simples
        Clock.schedule_once(carregar_simples, 0.1)

    def configurar_binds_taxas(self):
        """Configura os binds para os campos de taxa"""
        if hasattr(self, 'ids'):
            # Bind para atualizar cálculo quando valor mudar
            if 'entry_valor_cambio' in self.ids:
                self.ids.entry_valor_cambio.bind(text=lambda instance, value: self.atualizar_calculo_conversao())
            
            # Bind para atualizar cálculo quando contas mudarem
            if 'combo_conta_origem' in self.ids:
                self.ids.combo_conta_origem.bind(text=lambda instance, value: self.atualizar_calculo_conversao())
            
            if 'combo_conta_destino' in self.ids:
                self.ids.combo_conta_destino.bind(text=lambda instance, value: self.atualizar_calculo_conversao())

    def inicializar_campos_taxa(self):
        """Inicializa os campos de taxa bidirecional na interface"""
        if hasattr(self, 'ids'):
            # Remover o campo de taxa antigo se existir
            if 'container_taxas_cambio' in self.ids:
                container = self.ids.container_taxas_cambio
                container.clear_widgets()
                
                # Adicionar os novos campos de taxa
                campos_taxa = self.criar_campos_taxa_bidirecional()
                container.add_widget(campos_taxa)

    def forcar_atualizacao_combos(self):
        """Força a atualização de todos os combos após a interface carregar"""
        try:
            if hasattr(self, 'ids'):
                # Forçar atualização dos combos de contas
                if 'combo_cliente_ajuste' in self.ids and self.ids.combo_cliente_ajuste.text:
                    self.atualizar_contas_ajuste()
                if 'combo_cliente_cambio' in self.ids and self.ids.combo_cliente_cambio.text:
                    self.atualizar_contas_cambio() 
                if 'combo_cliente_extrato' in self.ids and self.ids.combo_cliente_extrato.text:
                    self.atualizar_contas_extrato()
                if 'combo_cliente_receita' in self.ids and self.ids.combo_cliente_receita.text:
                    self.atualizar_contas_cliente_receita()
                    
        except Exception as e:
            print(f"⚠️ Erro ao forçar atualização de combos: {e}")
    
    def formatar_data_para_exibicao_admin(self, data_string):
        """Formata data para exibição amigável: DD/MM/AAAA HH:MM"""
        if not data_string or data_string == 'SEM DATA' or data_string == 'Data não disponível':
            return data_string
        
        try:
            # Remover microssegundos e timezone se existir
            if 'T' in data_string:
                # Formato ISO: 2025-11-28T10:04:24.541064
                partes = data_string.split('T')
                if len(partes) == 2:
                    data = partes[0]
                    hora_completa = partes[1]
                    
                    # Remover timezone e microssegundos
                    hora = hora_completa.split('.')[0] if '.' in hora_completa else hora_completa
                    hora = hora.split('+')[0]  # Remover timezone (+00:00)
                    hora = hora.split('Z')[0]  # Remover Z
                    
                    # Formatar para DD/MM/AAAA HH:MM
                    try:
                        ano, mes, dia = data.split('-')
                        hora_parts = hora.split(':')
                        hora_fmt = f"{hora_parts[0]}:{hora_parts[1]}" if len(hora_parts) >= 2 else hora
                        
                        return f"{dia}/{mes}/{ano} {hora_fmt}"
                    except:
                        return f"{data} {hora}"
            
            elif ' ' in data_string:
                # Formato normal: 2025-11-28 10:04:24
                data, hora_completa = data_string.split(' ', 1)
                hora = hora_completa.split('.')[0] if '.' in hora_completa else hora_completa
                
                # Formatar para DD/MM/AAAA HH:MM
                try:
                    ano, mes, dia = data.split('-')
                    hora_parts = hora.split(':')
                    hora_fmt = f"{hora_parts[0]}:{hora_parts[1]}" if len(hora_parts) >= 2 else hora
                    
                    return f"{dia}/{mes}/{ano} {hora_fmt}"
                except:
                    # Se não conseguir formatar, retornar a data original
                    return data_string
            
            else:
                # Apenas data: 2025-11-28
                try:
                    ano, mes, dia = data_string.split('-')
                    return f"{dia}/{mes}/{ano}"
                except:
                    return data_string
                    
        except Exception as e:
            print(f"⚠️ Erro ao formatar data admin '{data_string}': {e}")
            # Fallback: mostrar apenas a parte da data
            return data_string.split(' ')[0] if ' ' in data_string else data_string

    def on_enter(self):
        """Chamado quando a tela é carregada - VERSÃO DEFINITIVA"""
        from kivy.core.window import Window
        
        Window.left = 300
        Window.top = 70
        
        print("🎯 Configurando bindings definitivos...")

        self.configurar_bindings_taxas()  # ✅ Cálculo entre taxas direta/inversa
        self.configurar_binds_taxas()     # ✅ Cálculo de conversão valor

        # 🔥 BINDINGS SIMPLES E DIRETOS
        if hasattr(self, 'ids'):
            # === DESPESAS ===
            # 1. Quando muda categoria → atualizar contas contábeis
            if 'combo_categoria_despesa' in self.ids:
                self.ids.combo_categoria_despesa.bind(
                    text=lambda instance, value: self.atualizar_contas_despesa()
                )
                print("✅ Binding: categoria_despesa → atualizar_contas_despesa")
            
            # 2. Quando muda conta bancária → atualizar contas contábeis
            if 'combo_conta_bancaria_despesa' in self.ids:
                self.ids.combo_conta_bancaria_despesa.bind(
                    text=lambda instance, value: self.atualizar_contas_despesa()
                )
                print("✅ Binding: conta_bancaria_despesa → atualizar_contas_despesa")
            
            # === RECEITAS ===
            # 3. Quando muda cliente → atualizar contas receita
            if 'combo_cliente_receita' in self.ids:
                self.ids.combo_cliente_receita.bind(
                    text=lambda instance, value: self.atualizar_contas_receita()
                )
                print("✅ Binding: cliente_receita → atualizar_contas_receita")
            
            # 4. Quando muda categoria receita → atualizar contas receita
            if 'combo_categoria_receita' in self.ids:
                self.ids.combo_categoria_receita.bind(
                    text=lambda instance, value: self.atualizar_contas_receita()
                )
                print("✅ Binding: categoria_receita → atualizar_contas_receita")
            
            # 🔥 IMPORTANTE: NÃO ADICIONE ESTE BINDING (causa deadlock):
            # if 'combo_conta_receita' in self.ids:
            #     self.ids.combo_conta_receita.bind(
            #         text=lambda instance, value: self.atualizar_contas_cliente_receita()
            #     )
            #     print("✅ Binding: conta_receita → atualizar_contas_cliente_receita")
            
            # 🔥 MAS ADICIONE ESTE: Quando muda conta cliente → atualizar contas receita
            if 'combo_conta_cliente_receita' in self.ids:
                self.ids.combo_conta_cliente_receita.bind(
                    text=lambda instance, value: self.atualizar_contas_receita()
                )
                print("✅ Binding: conta_cliente_receita → atualizar_contas_receita")
        
        print("✅ Todos os bindings configurados (baseados em dados reais do Supabase)")
        
        # 🔥 CARREGAMENTO INICIAL
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.carregar_dados_iniciais_despesa(), 0.5)

    def carregar_dados_iniciais_despesa(self):
        """Carrega dados iniciais para a aba despesa"""
        print("🎯 Carregando dados iniciais despesa...")
        
        if not hasattr(self, 'ids'):
            return
        
        sistema = App.get_running_app().sistema
        
        try:
            # 1. Carregar categorias de despesa
            categorias = set()
            response = sistema.supabase.client.table('contas_contabeis')\
                .select('categoria')\
                .eq('tipo', 'despesa')\
                .execute()
            
            for item in response.data:
                categorias.add(item['categoria'])
            
            if 'combo_categoria_despesa' in self.ids:
                self.ids.combo_categoria_despesa.values = list(categorias)
                if categorias:
                    self.ids.combo_categoria_despesa.text = list(categorias)[0]
            
            # 2. Carregar contas bancárias iniciais (sem filtro)
            contas_bancarias = self.carregar_contas_bancarias_com_filtro()
            if contas_bancarias and 'combo_conta_bancaria_despesa' in self.ids:
                textos = [conta['texto'] for conta in contas_bancarias]
                self.ids.combo_conta_bancaria_despesa.values = textos
                if textos:
                    self.ids.combo_conta_bancaria_despesa.text = textos[0]
            
            print("✅ Dados iniciais carregados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados iniciais: {e}")

    def carregar_dados_iniciais(self):
        """Carrega todos os dados iniciais da tela - VERSÃO COMPLETA COM FILTRO MOEDA"""
        print("🎯 carregar_dados_iniciais COMPLETO")
        sistema = App.get_running_app().sistema
        
        # Verificar se é admin
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            self.voltar_dashboard()
            return
        
        try:
            self.carregar_clientes_combos()
            self.carregar_combos_contabeis()
            self.carregar_combos_receita()
            self.carregar_lista_clientes()
            print("✅ Todos os dados iniciais carregados")
            
            # 🔥 🔥 🔥 ADICIONE ESTA PARTE NO FINAL:
            # Configurar bindings para filtro automático de moeda
            if hasattr(self, 'ids'):
                print("🔧 Configurando bindings para filtro automático de moeda...")
                
                # Quando conta bancária mudar, filtrar contas despesa
                if 'combo_conta_bancaria_despesa' in self.ids:
                    self.ids.combo_conta_bancaria_despesa.bind(on_text=self._on_conta_bancaria_change)
                    print("✅ Binding: conta_bancaria_despesa → contas_despesa")
                
                # Quando conta cliente mudar, filtrar contas receita  
                if 'combo_conta_cliente_receita' in self.ids:
                    self.ids.combo_conta_cliente_receita.bind(on_text=self._on_conta_cliente_change)
                    print("✅ Binding: conta_cliente_receita → contas_receita")
                
                # Quando conta despesa mudar, filtrar contas bancárias
                if 'combo_conta_despesa' in self.ids:
                    self.ids.combo_conta_despesa.bind(on_text=self._on_conta_despesa_change)
                    print("✅ Binding: conta_despesa → contas_bancarias")
                
                # Quando conta receita mudar, filtrar contas cliente
                if 'combo_conta_receita' in self.ids:
                    self.ids.combo_conta_receita.bind(on_text=self._on_conta_receita_change)
                    print("✅ Binding: conta_receita → contas_cliente")
                
                print("🎯 Todos os bindings configurados para filtro de moeda!")
            
        except Exception as e:
            print(f"❌ Erro em carregar_dados_iniciais: {e}")
    
    def carregar_clientes_combos(self):
        """Carrega a lista de clientes nos comboboxes - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = []
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        print(f"🔍 DEBUG carregar_clientes_combos: {len(clientes_opcoes)} clientes encontrados")
        
        # Atualizar todos os combos de cliente - COM VERIFICAÇÃO DE EXISTÊNCIA
        if hasattr(self, 'ids'):
            # Combo da aba Ajustar Saldos
            if 'combo_cliente_ajuste' in self.ids:
                self.ids.combo_cliente_ajuste.values = clientes_opcoes
                if clientes_opcoes and not self.ids.combo_cliente_ajuste.text:
                    self.ids.combo_cliente_ajuste.text = clientes_opcoes[0]
            
            # Combo da aba Câmbio entre Moedas
            if 'combo_cliente_cambio' in self.ids:
                self.ids.combo_cliente_cambio.values = clientes_opcoes
                if clientes_opcoes and not self.ids.combo_cliente_cambio.text:
                    self.ids.combo_cliente_cambio.text = clientes_opcoes[0]
            
            # Combo da aba Extratos
            if 'combo_cliente_extrato' in self.ids:
                self.ids.combo_cliente_extrato.values = clientes_opcoes
                if clientes_opcoes and not self.ids.combo_cliente_extrato.text:
                    self.ids.combo_cliente_extrato.text = clientes_opcoes[0]
            
            # 🔥 CORREÇÃO CRÍTICA: Combo da aba Receitas
            if 'combo_cliente_receita' in self.ids:
                self.ids.combo_cliente_receita.values = clientes_opcoes
                print(f"✅ Combo receita carregado: {len(clientes_opcoes)} opções")
                if clientes_opcoes and not self.ids.combo_cliente_receita.text:
                    self.ids.combo_cliente_receita.text = clientes_opcoes[0]
                    print(f"✅ Texto definido: {self.ids.combo_cliente_receita.text}")
            else:
                print("❌ combo_cliente_receita não encontrado!")

    def forcar_atualizacao_combos_receita(self):
        """Força a atualização dos combos da aba receitas"""
        try:
            if hasattr(self, 'ids'):
                print("🔄 Forçando atualização combos receita...")
                
                # Forçar atualização do combo de cliente
                if 'combo_cliente_receita' in self.ids:
                    sistema = App.get_running_app().sistema
                    clientes_opcoes = []
                    for username, dados in sistema.usuarios.items():
                        if dados['tipo'] == 'cliente':
                            clientes_opcoes.append(f"{username} - {dados['nome']}")
                    
                    self.ids.combo_cliente_receita.values = clientes_opcoes
                    if clientes_opcoes and not self.ids.combo_cliente_receita.text:
                        self.ids.combo_cliente_receita.text = clientes_opcoes[0]
                    
                    print(f"✅ Combo cliente receita atualizado: {len(clientes_opcoes)} opções")
                
                # Forçar atualização do combo de categorias de receita
                if 'combo_categoria_receita' in self.ids:
                    sistema = App.get_running_app().sistema
                    categorias = list(sistema.contas_contabeis['receitas'].keys())
                    self.ids.combo_categoria_receita.values = categorias
                    if categorias and not self.ids.combo_categoria_receita.text:
                        self.ids.combo_categoria_receita.text = categorias[0]
                    
                    print(f"✅ Combo categoria receita atualizado: {len(categorias)} opções")
                    
        except Exception as e:
            print(f"⚠️ Erro ao forçar atualização combos receita: {e}")

    def carregar_lista_clientes(self, filtro=None):
        """Carrega a lista de clientes na primeira aba com filtro opcional"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or 'lista_clientes' not in self.ids:
            return
        
        container = self.ids.lista_clientes
        container.clear_widgets()
        
        # Coletar todos os clientes
        clientes_com_contas = []
        
        for username, dados_usuario in sistema.usuarios.items():
            if dados_usuario['tipo'] == 'cliente':
                # Aplicar filtro se existir
                if filtro:
                    filtro_lower = filtro.lower()
                    # Buscar no nome, username ou número da conta
                    nome_match = filtro_lower in dados_usuario['nome'].lower()
                    username_match = filtro_lower in username.lower()
                    conta_match = False
                    
                    # Verificar se o filtro corresponde a alguma conta
                    for conta_num in dados_usuario.get('contas', []):
                        if conta_num in sistema.contas:
                            if filtro_lower in conta_num.lower():
                                conta_match = True
                                break
                    
                    if not (nome_match or username_match or conta_match):
                        continue
                
                contas_cliente = []
                
                # Coletar informações das contas
                for conta_num in dados_usuario.get('contas', []):
                    if conta_num in sistema.contas:
                        dados_conta = sistema.contas[conta_num]
                        contas_cliente.append({
                            'numero': conta_num,
                            'moeda': dados_conta['moeda'],
                            'saldo': dados_conta['saldo']
                        })
                
                clientes_com_contas.append((username, dados_usuario, contas_cliente))
        
        if not clientes_com_contas:
            # Mensagem quando não há clientes
            lbl_vazio = Label(
                text="📭 Nenhum cliente encontrado" + (" para o filtro aplicado" if filtro else ""),
                font_size='14sp',
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(lbl_vazio)
            return
        
        # Criar cards para cada cliente
        for username, dados_usuario, contas in clientes_com_contas:
            card = CardCliente(username, dados_usuario, contas, self)
            container.add_widget(card)
        
        print(f"✅ {len(clientes_com_contas)} clientes carregados" + (f" (filtro: {filtro})" if filtro else ""))

    def teste_rapido_spinner(self):
        """Teste rápido do spinner após carregamento"""
        from kivy.clock import Clock
        
        def testar(dt):
            if hasattr(self, 'ids') and 'combo_cliente_receita' in self.ids:
                spinner = self.ids.combo_cliente_receita
                print(f"🎯 TESTE RÁPIDO SPINNER:")
                print(f"   Valores: {len(spinner.values)}")
                print(f"   Texto: '{spinner.text}'")
                print("   ✅ Tente clicar no spinner agora!")
        
        Clock.schedule_once(testar, 0.5)

    def filtrar_clientes_delay(self):
        """Busca em tempo real com delay para melhor performance"""
        from kivy.clock import Clock
        # Cancela qualquer busca anterior agendada
        if hasattr(self, '_busca_clock'):
            Clock.unschedule(self._busca_clock)
        
        # Agenda nova busca após 300ms (0.3 segundos)
        self._busca_clock = Clock.schedule_once(lambda dt: self.filtrar_clientes(), 0.3)
    
    def filtrar_clientes(self):
        """Aplica o filtro na lista de clientes"""
        if hasattr(self, 'ids') and 'input_busca_clientes' in self.ids:
            filtro = self.ids.input_busca_clientes.text.strip()
            print(f"🔍 FILTRO: Buscando por '{filtro}'")
            self.carregar_lista_clientes(filtro if filtro else None)
    
    def limpar_filtro_clientes(self):
        """Limpa o filtro e recarrega a lista completa"""
        if hasattr(self, 'ids'):
            self.ids.input_busca_clientes.text = ""
            self.carregar_lista_clientes()
    
    def atualizar_contas_ajuste(self):
        """Atualiza as contas quando selecionar cliente na aba de ajuste"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_cliente_ajuste.text:
            return
        
        username_selecionado = self.ids.combo_cliente_ajuste.text.split(' - ')[0]
        
        if username_selecionado in sistema.usuarios:
            contas_cliente = sistema.usuarios[username_selecionado].get('contas', [])
            opcoes_contas = []
            
            for conta_num in contas_cliente:
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    opcoes_contas.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            self.ids.combo_conta_ajuste.values = opcoes_contas
            if opcoes_contas:
                self.ids.combo_conta_ajuste.text = opcoes_contas[0]


    def atualizar_contas_despesa(self):
        """Atualiza as contas de despesa - FILTRADAS pela moeda da conta bancária"""
        if not hasattr(self, 'ids') or not self.ids.combo_categoria_despesa.text:
            return
        
        sistema = App.get_running_app().sistema
        categoria = self.ids.combo_categoria_despesa.text
        
        print(f"🔍 Atualizando contas despesa para categoria: {categoria}")
        
        # 🔥 1. Obter moeda da conta bancária selecionada (se houver)
        moeda_filtro = None
        if self.ids.combo_conta_bancaria_despesa.text and ' - ' in self.ids.combo_conta_bancaria_despesa.text:
            numero_conta = self.ids.combo_conta_bancaria_despesa.text.split(' - ')[0]
            moeda_filtro = self.obter_moeda_conta_bancaria_real(numero_conta)
            print(f"🎯 Filtrando contas contábeis por moeda: {moeda_filtro}")
        
        # 🔥 2. Carregar contas contábeis COM FILTRO (ou todas se não houver seleção)
        try:
            # Construir query base
            query = sistema.supabase.client.table('contas_contabeis')\
                .select('nome, moeda, saldo')\
                .eq('categoria', categoria)\
                .eq('tipo', 'despesa')
            
            # Aplicar filtro de moeda se existir
            if moeda_filtro:
                query = query.eq('moeda', moeda_filtro)
            
            response = query.execute()
            
            contas_formatadas = []
            for conta in response.data:
                texto = f"{conta['nome']} ({conta['moeda']})"
                contas_formatadas.append({
                    'texto': texto,
                    'nome': conta['nome'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo'])
                })
            
            print(f"✅ {len(contas_formatadas)} contas contábeis carregadas (filtro: {moeda_filtro})")
            
            # 🔥 3. Atualizar spinner
            if contas_formatadas and 'combo_conta_despesa' in self.ids:
                textos = [conta['texto'] for conta in contas_formatadas]
                self.ids.combo_conta_despesa.values = textos
                
                # 🔥 LÓGICA INTELIGENTE: Se não tem seleção OU seleção não está nas opções
                selecao_atual = self.ids.combo_conta_despesa.text
                
                if not selecao_atual or selecao_atual not in textos:
                    # Tentar manter conta com mesmo nome (se existir)
                    if selecao_atual and ' (' in selecao_atual:
                        nome_atual = selecao_atual.split(' (')[0]
                        for texto in textos:
                            if texto.startswith(nome_atual + ' ('):
                                self.ids.combo_conta_despesa.text = texto
                                print(f"✅ Mantida conta similar: {texto}")
                                return
                    
                    # Se não encontrou, selecionar primeira
                    if textos:
                        self.ids.combo_conta_despesa.text = textos[0]
                        print(f"✅ Nova seleção: {textos[0]}")
                else:
                    print(f"✅ Seleção mantida: {selecao_atual}")
                    
        except Exception as e:
            print(f"❌ Erro ao carregar contas contábeis: {e}")

    def atualizar_contas_cambio(self):
        """Atualiza as contas quando selecionar cliente na aba de câmbio"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_cliente_cambio.text:
            return
        
        username_selecionado = self.ids.combo_cliente_cambio.text.split(' - ')[0]
        
        if username_selecionado in sistema.usuarios:
            contas_cliente = sistema.usuarios[username_selecionado].get('contas', [])
            opcoes_contas = []
            
            for conta_num in contas_cliente:
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    opcoes_contas.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            self.ids.combo_conta_origem.values = opcoes_contas
            self.ids.combo_conta_destino.values = opcoes_contas
            
            if opcoes_contas:
                self.ids.combo_conta_origem.text = opcoes_contas[0]
                if len(opcoes_contas) > 1:
                    self.ids.combo_conta_destino.text = opcoes_contas[1]
            
            # 🔥 NOVO: Atualizar cálculo de conversão quando contas mudarem
            self.atualizar_calculo_conversao()
    
    def atualizar_contas_extrato(self):
        """Atualiza as contas quando selecionar cliente na aba de extrato - COM SALDOS ATUALIZADOS"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_cliente_extrato.text:
            return
        
        username_selecionado = self.ids.combo_cliente_extrato.text.split(' - ')[0]
        
        if username_selecionado in sistema.usuarios:
            contas_cliente = sistema.usuarios[username_selecionado].get('contas', [])
            opcoes_contas = []
            
            for conta_num in contas_cliente:
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    # 🔥 SEMPRE USAR SALDO ATUALIZADO
                    opcoes_contas.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            self.ids.combo_conta_extrato.values = opcoes_contas
            if opcoes_contas:
                self.ids.combo_conta_extrato.text = opcoes_contas[0]
    
    def definir_operacao(self, tipo):
        """Define o tipo de operação (crédito/débito) - VERSÃO CORRIGIDA"""
        self.operacao_atual = tipo
        
        if hasattr(self, 'ids'):
            if tipo == 'credito':
                # Crédito ativo (verde), Débito inativo (cinza)
                self.ids.btn_credito.background_color = (0.2, 0.8, 0.2, 1)      # Verde brilhante
                self.ids.btn_debito.background_color = (0.15, 0.20, 0.27, 1)    # Cinza escuro
            else:
                # Débito ativo (vermelho), Crédito inativo (cinza)
                self.ids.btn_credito.background_color = (0.15, 0.20, 0.27, 1)   # Cinza escuro
                self.ids.btn_debito.background_color = (0.96, 0.36, 0.36, 1)    # Vermelho brilhante
            
            # Forçar atualização da tela
            self.ids.btn_credito.canvas.ask_update()
            self.ids.btn_debito.canvas.ask_update()
    
    def _processar_ajuste_saldo(self, conta_num, valor, operacao, descricao, username):
        """Processa o ajuste de saldo após confirmação"""
        sistema = App.get_running_app().sistema
        
        # Executar operação
        if self.executar_ajuste_saldo_sistema(conta_num, valor, operacao, descricao, username):
            # Buscar saldo atualizado do Supabase para mostrar corretamente
            try:
                from supabase import create_client
                import os
                from dotenv import load_dotenv
                
                load_dotenv()
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_KEY')
                
                if supabase_url and supabase_key:
                    supabase = create_client(supabase_url, supabase_key)
                    response = supabase.table('contas').select('saldo, moeda').eq('id', conta_num).execute()
                    
                    if response.data:
                        novo_saldo = float(response.data[0]['saldo'])
                        moeda = response.data[0]['moeda']
                    else:
                        # Fallback para cache local
                        novo_saldo = sistema.contas[conta_num]['saldo']
                        moeda = sistema.contas[conta_num]['moeda']
                else:
                    novo_saldo = sistema.contas[conta_num]['saldo']
                    moeda = sistema.contas[conta_num]['moeda']
            except:
                novo_saldo = sistema.contas[conta_num]['saldo']
                moeda = sistema.contas[conta_num]['moeda']
            
            tipo_operacao = "CRÉDITO" if operacao == "credito" else "DÉBITO"
            
            # ✅ MENSAGEM ATUALIZADA - SEMPRE SUPABASE AGORA
            mensagem_sucesso = (
                f"{tipo_operacao} realizado com sucesso!\n\n"
                f"Novo saldo: {novo_saldo:,.2f} {moeda}\n"
                f"Sincronizado com Supabase"
            )
            
            self.mostrar_sucesso(mensagem_sucesso)
            
            # Limpar campos
            self.ids.entry_valor_ajuste.text = ""
            self.ids.entry_descricao_ajuste.text = ""
            self.atualizar_contas_ajuste()
            self.atualizar_combos_apos_operacao()

        else:
            self.mostrar_erro("Falha ao executar operação!")

    def executar_ajuste_saldo(self):
        """Executa o ajuste de saldo - PERMITE SALDO NEGATIVO SEM RESTRIÇÕES"""
        sistema = App.get_running_app().sistema
        
        print("💰 Executando ajuste de saldo...")
        
        # Validar campos
        if not all([
            self.ids.combo_cliente_ajuste.text,
            self.ids.combo_conta_ajuste.text,
            self.ids.entry_valor_ajuste.text,
            self.ids.entry_descricao_ajuste.text
        ]):
            self.mostrar_erro("Preencha todos os campos!")
            return
        
        try:
            # Obter dados
            username = self.ids.combo_cliente_ajuste.text.split(' - ')[0]
            conta_num = self.ids.combo_conta_ajuste.text.split(' - ')[0]
            valor_str = self.ids.entry_valor_ajuste.text.strip()
            descricao = self.ids.entry_descricao_ajuste.text.strip()
            operacao = self.operacao_atual
            
            print(f"🔍 DEBUG executar_ajuste_saldo: valor_str = '{valor_str}'")
            
            # Converter valor corretamente
            try:
                valor = self._parse_valor_br(valor_str)
                
                if valor <= 0:
                    self.mostrar_erro("Valor deve ser positivo!")
                    return
                    
                print(f"✅ DEBUG valor convertido: {valor}")
                
            except ValueError as e:
                print(f"❌ DEBUG erro no parse: {e}")
                self.mostrar_erro(f"Valor inválido! {str(e)}")
                return
            
            # Verificar se conta existe
            if conta_num not in sistema.contas:
                self.mostrar_erro("Conta não encontrada!")
                return
            
            # 🔥🔥🔥 CORREÇÃO: REMOVER TODAS AS RESTRIÇÕES - PERMITIR SEMPRE
            # Mostrar confirmação com aviso de saldo negativo (se aplicável)
            tipo_operacao = "CRÉDITO" if operacao == "credito" else "DÉBITO"
            
            if operacao == "debito":
                saldo_atual = sistema.contas[conta_num]['saldo']
                saldo_futuro = saldo_atual - valor
                
                if saldo_futuro < 0:
                    # 🔥 AVISO, MAS PERMITE CONTINUAR
                    self.mostrar_confirmacao(
                        f"ATENÇÃO: {tipo_operacao} deixará a conta NEGATIVA",
                        f"Cliente: {username}\n"
                        f"Conta: {conta_num}\n"
                        f"Operação: {descricao}\n"
                        f"Valor: {valor:,.2f} {sistema.contas[conta_num]['moeda']}\n"
                        f"Saldo atual: {saldo_atual:,.2f}\n"
                        f"Saldo futuro: {saldo_futuro:,.2f}\n\n"
                        f"Deseja continuar mesmo assim?",
                        lambda: self._processar_ajuste_saldo(conta_num, valor, operacao, descricao, username)
                    )
                    return
            
            # Confirmação normal para outras situações
            self.mostrar_confirmacao(
                f"Confirmar {tipo_operacao}?",
                f"Cliente: {username}\n"
                f"Conta: {conta_num}\n"
                f"Valor: {valor:,.2f} {sistema.contas[conta_num]['moeda']}\n"
                f"Descrição: {descricao}",
                lambda: self._processar_ajuste_saldo(conta_num, valor, operacao, descricao, username)
            )
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao executar ajuste: {str(e)}")

    def executar_ajuste_saldo_sistema(self, conta_num, valor, operacao, descricao, username):
        """Executa o ajuste de saldo no sistema - 100% SUPABASE"""
        sistema = App.get_running_app().sistema
        
        try:
            print(f"💰 AJUSTE SALDO - Conta: {conta_num}, Valor: {valor}, Operação: {operacao}")
            
            from supabase import create_client
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("❌ Credenciais do Supabase não encontradas")
                return False
            
            supabase = create_client(supabase_url, supabase_key)
            
            # 1. BUSCAR SALDO ATUAL DO SUPABASE
            response = supabase.table('contas').select('saldo, moeda').eq('id', conta_num).execute()
            
            if not response.data:
                print(f"❌ Conta {conta_num} não encontrada no Supabase")
                return False
            
            conta_data = response.data[0]
            saldo_atual_supabase = float(conta_data['saldo'])
            moeda_conta = conta_data['moeda']
            
            # 2. CALCULAR NOVO SALDO
            if operacao == "credito":
                novo_saldo = saldo_atual_supabase + valor
            else:  # debito
                novo_saldo = saldo_atual_supabase - valor
            
            # 3. ATUALIZAR SALDO NO SUPABASE
            update_response = supabase.table('contas').update({
                'saldo': novo_saldo
            }).eq('id', conta_num).execute()
            
            if not update_response.data:
                print(f"❌ Erro ao atualizar saldo no Supabase: {update_response.error}")
                return False
            
            print(f"✅ Saldo atualizado no Supabase: {saldo_atual_supabase} → {novo_saldo}")
            
            # 4. CRIAR REGISTRO DO AJUSTE NO SUPABASE
            transacao_id = str(random.randint(100000, 999999))
            
            # ✅ USAR APENAS COLUNAS QUE EXISTEM NA TABELA
            dados_ajuste = {
                'id': transacao_id,
                'conta_remetente': conta_num,
                'valor': valor,
                'moeda': moeda_conta,
                'tipo': 'ajuste_admin',
                'tipo_ajuste': 'CREDITO' if operacao == 'credito' else 'DEBITO',
                'descricao_ajuste': f"Ajuste: {descricao} | Cliente: {username}",
                'status': 'completed',
                'data': datetime.datetime.now().isoformat(),
                'executado_por': sistema.usuario_logado
                # ❌ REMOVIDO: 'cliente_afetado' (não existe na tabela)
            }
            
            # Salvar o registro do ajuste na tabela transferencias do Supabase
            ajuste_response = supabase.table('transferencias').insert(dados_ajuste).execute()
            
            if not ajuste_response.data:
                print(f"❌ FALHA AO SALVAR REGISTRO DO AJUSTE NO SUPABASE")
                return False
            
            print(f"✅ REGISTRO DE AJUSTE SALVO NO SUPABASE: ID {transacao_id}")
            
            # 5. ATUALIZAR CACHE LOCAL (OPCIONAL - PARA PERFORMANCE)
            if conta_num in sistema.contas:
                sistema.contas[conta_num]['saldo'] = novo_saldo
            
            # Adicionar ao cache de transferências
            sistema.transferencias[transacao_id] = dados_ajuste
            
            print(f"✅ Ajuste de saldo realizado com sucesso no Supabase")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao ajustar saldo: {e}")
            import traceback
            traceback.print_exc()
            return False

    def executar_operacao_cambio(self):
        """Executa operação de câmbio entre moedas - VERSÃO FLEXÍVEL"""
        sistema = App.get_running_app().sistema
        
        print("💱 Executando operação de câmbio...")
        
        # Validar campos
        if not all([
            self.ids.combo_cliente_cambio.text,
            self.ids.combo_conta_origem.text,
            self.ids.combo_conta_destino.text,
            self.ids.entry_valor_cambio.text
        ]):
            self.mostrar_erro("Preencha todos os campos!")
            return
        
        # 🔥 FLEXÍVEL: Validar pelo menos uma taxa preenchida
        if not hasattr(self, 'entry_taxa_principal') or not self.entry_taxa_principal.text:
            if not hasattr(self, 'entry_taxa_inversa') or not self.entry_taxa_inversa.text:
                self.mostrar_erro("Preencha pelo menos uma taxa de câmbio!")
                return
        
        try:
            # Obter dados
            username = self.ids.combo_cliente_cambio.text.split(' - ')[0]
            conta_origem = self.ids.combo_conta_origem.text.split(' - ')[0]
            conta_destino = self.ids.combo_conta_destino.text.split(' - ')[0]
            valor_str = self.ids.entry_valor_cambio.text.strip()
            
            print(f"🔍 DEBUG executar_operacao_cambio: valor_str = '{valor_str}'")
            
            # Validar contas diferentes
            if conta_origem == conta_destino:
                self.mostrar_erro("Conta origem e destino devem ser diferentes!")
                return
            
            # 🔥 CORREÇÃO: Converter valor corretamente
            try:
                # Converter valor
                valor = self._parse_valor_br(valor_str)
                
                if valor <= 0:
                    self.mostrar_erro("Valor deve ser positivo!")
                    return
                    
                print(f"✅ DEBUG valor convertido: {valor}")
                
            except ValueError as e:
                print(f"❌ DEBUG erro no parse: {e}")
                self.mostrar_erro(f"Valor inválido! {str(e)}")
                return
            
            # 🔥 FLEXÍVEL: Usar taxa principal como padrão
            # O usuário pode escolher manualmente qual taxa usar
            taxa = None
            tipo_taxa = 'principal'
            
            if hasattr(self, 'entry_taxa_principal') and self.entry_taxa_principal.text:
                taxa = self._parse_valor_br(self.entry_taxa_principal.text)
                tipo_taxa = 'principal'
            
            # Se não tiver taxa principal, tentar taxa inversa
            elif hasattr(self, 'entry_taxa_inversa') and self.entry_taxa_inversa.text:
                taxa = self._parse_valor_br(self.entry_taxa_inversa.text)
                tipo_taxa = 'inversa'
            
            if not taxa or taxa <= 0:
                self.mostrar_erro("Taxa de câmbio inválida!")
                return
            
            # Calcular valor destino
            valor_destino = valor * taxa
            
            # 🔥 MUDANÇA CRÍTICA: NÃO VERIFICAR SALDO para câmbio
            saldo_origem = sistema.contas[conta_origem]['saldo']
            moeda_origem = sistema.contas[conta_origem]['moeda']
            moeda_destino = sistema.contas[conta_destino]['moeda']
            
            # Mostrar AVISO se saldo ficará negativo
            saldo_futuro = saldo_origem - valor
            tipo_taxa_texto = "PRINCIPAL" if tipo_taxa == 'principal' else "INVERSA"
            
            if saldo_futuro < 0:
                self.mostrar_confirmacao(
                    "ATENÇÃO: Saldo Negativo",
                    f"Cliente: {username}\n"
                    f"Origem: {conta_origem} ({moeda_origem})\n"
                    f"Destino: {conta_destino} ({moeda_destino})\n"
                    f"Valor: {valor:,.2f} {moeda_origem}\n"
                    f"Taxa {tipo_taxa_texto}: {taxa:.6f}\n"
                    f"Receberá: {valor_destino:,.2f} {moeda_destino}\n\n"
                    f"Saldo ficará NEGATIVO: {saldo_futuro:,.2f} {moeda_origem}",
                    lambda: self._processar_cambio(conta_origem, conta_destino, valor, taxa, username, tipo_taxa)
                )
            else:
                # Mostrar confirmação normal
                self.mostrar_confirmacao(
                    "Confirmar Câmbio?",
                    f"Cliente: {username}\n"
                    f"Origem: {conta_origem} ({moeda_origem})\n"
                    f"Destino: {conta_destino} ({moeda_destino})\n"
                    f"Valor: {valor:,.2f} {moeda_origem}\n"
                    f"Taxa {tipo_taxa_texto}: {taxa:.6f}\n"
                    f"Receberá: {valor_destino:,.2f} {moeda_destino}",
                    lambda: self._processar_cambio(conta_origem, conta_destino, valor, taxa, username, tipo_taxa)
                )
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao executar câmbio: {str(e)}")

    def _parse_valor_br(self, valor_str):
        """Converte string de valor no formato brasileiro para float"""
        print(f"🔍 DEBUG _parse_valor_br: valor_str = '{valor_str}'")
        
        if not valor_str:
            raise ValueError("Valor vazio")
        
        # Remover espaços
        valor_str = valor_str.strip()
        print(f"🔍 DEBUG após strip: '{valor_str}'")
        
        # Verificar caracteres
        print(f"🔍 DEBUG caracteres: {[c for c in valor_str]}")
        
        # CORREÇÃO: Lidar com formato brasileiro (26,384.00)
        try:
            # Se tem vírgula E ponto, é formato brasileiro com separador de milhar
            if ',' in valor_str and '.' in valor_str:
                # Exemplo: "26,384.00" -> virgula é separador de milhar, ponto é decimal
                # Remover a vírgula (separador de milhar) e manter o ponto (decimal)
                valor_limpo = valor_str.replace(',', '')
                print(f"🔍 DEBUG formato BR com milhar: '{valor_limpo}'")
            elif ',' in valor_str:
                # Apenas vírgula: "300,00" -> substituir por ponto
                valor_limpo = valor_str.replace(',', '.')
                print(f"🔍 DEBUG formato BR decimal: '{valor_limpo}'")
            else:
                # Apenas ponto: "300.00" -> manter como está
                valor_limpo = valor_str
                print(f"🔍 DEBUG formato internacional: '{valor_limpo}'")
            
            valor_float = float(valor_limpo)
            print(f"✅ DEBUG valor_float convertido: {valor_float}")
            
            return valor_float
            
        except ValueError as e:
            print(f"❌ DEBUG erro na conversão: {e}")
            raise ValueError("Valor inválido! Use números como: 300.00 ou 26,384.00")
    
    def _processar_cambio(self, conta_origem, conta_destino, valor, taxa, username, tipo_taxa):
        """Processa a operação de câmbio após confirmação - COM TIPO DE TAXA"""
        sistema = App.get_running_app().sistema
        
        # Executar câmbio
        if self.executar_cambio_sistema(conta_origem, conta_destino, valor, taxa, username, tipo_taxa):
            valor_destino = valor * taxa
            moeda_origem = sistema.contas[conta_origem]['moeda']
            moeda_destino = sistema.contas[conta_destino]['moeda']
            tipo_taxa_texto = "DIRETA" if tipo_taxa == 'direta' else "INVERSA"
            
            self.mostrar_sucesso(
                f"Câmbio realizado com sucesso!\n\n"
                f"Debitado: {valor:,.2f} {moeda_origem}\n"
                f"Creditado: {valor_destino:,.2f} {moeda_destino}\n"
                f"Taxa {tipo_taxa_texto} aplicada: {taxa:.6f}"
            )
            
            # Limpar campos
            self.ids.entry_valor_cambio.text = ""
            self.atualizar_contas_cambio()
            self.atualizar_combos_apos_operacao()
            
            # 🔥🔥🔥 ADICIONAR ESTA LINHA: Atualizar saldos na UI
            self.atualizar_saldos_ui()

        else:
            self.mostrar_erro("Falha ao executar câmbio!")

    def atualizar_saldos_ui(self):
        """Atualiza os saldos exibidos na UI após operações"""
        try:
            sistema = App.get_running_app().sistema
            
            print("🔄 Atualizando saldos na UI...")
            
            # 🔥 ATUALIZAR SALDOS NA ABA CÂMBIO
            if hasattr(self, 'ids') and hasattr(self.ids, 'label_saldo_origem'):
                # Atualizar saldo da conta origem
                conta_origem = self.ids.combo_conta_origem.text
                if conta_origem and conta_origem != 'Selecione...':
                    try:
                        numero_conta = conta_origem.split(' - ')[0]
                        if numero_conta in sistema.contas:
                            saldo = sistema.contas[numero_conta]['saldo']
                            moeda = sistema.contas[numero_conta]['moeda']
                            self.ids.label_saldo_origem.text = f"Saldo: {saldo:,.2f} {moeda}"
                            print(f"✅ Saldo origem atualizado: {saldo:,.2f} {moeda}")
                    except Exception as e:
                        print(f"⚠️ Erro ao atualizar saldo origem: {e}")
            
            if hasattr(self, 'ids') and hasattr(self.ids, 'label_saldo_destino'):
                # Atualizar saldo da conta destino
                conta_destino = self.ids.combo_conta_destino.text
                if conta_destino and conta_destino != 'Selecione...':
                    try:
                        numero_conta = conta_destino.split(' - ')[0]
                        if numero_conta in sistema.contas:
                            saldo = sistema.contas[numero_conta]['saldo']
                            moeda = sistema.contas[numero_conta]['moeda']
                            self.ids.label_saldo_destino.text = f"Saldo: {saldo:,.2f} {moeda}"
                            print(f"✅ Saldo destino atualizado: {saldo:,.2f} {moeda}")
                    except Exception as e:
                        print(f"⚠️ Erro ao atualizar saldo destino: {e}")
            
            # 🔥 TAMBÉM ATUALIZAR OS SPINNERS (se existirem)
            self.atualizar_contas_cambio()
                        
        except Exception as e:
            print(f"⚠️ Erro ao atualizar saldos na UI: {e}")

    def executar_cambio_sistema(self, conta_origem, conta_destino, valor, taxa, username, tipo_taxa):
        """Executa a operação de câmbio no sistema - COM SUPABASE COMPLETO"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 ARREDONDAR VALOR DE ORIGEM ANTES DE USAR (CÓDIGO ORIGINAL MANTIDO)
            valor_arredondado = sistema.arredondar_valor(valor)
            
            # 🔥 SALVAR SALDOS ANTES PARA DEBUG
            saldo_origem_antes = sistema.contas[conta_origem]['saldo']
            saldo_destino_antes = sistema.contas[conta_destino]['saldo']
            
            # Aplicar operações (CÓDIGO ORIGINAL MANTIDO)
            sistema.contas[conta_origem]['saldo'] -= valor_arredondado
            
            # 🔥 CÁLCULO COM ARREDONDAMENTO DUPLO (CÓDIGO ORIGINAL MANTIDO)
            valor_destino = valor_arredondado * taxa
            valor_destino_arredondado = sistema.arredondar_valor(valor_destino)
            
            sistema.contas[conta_destino]['saldo'] += valor_destino_arredondado
            
            # 🔥 ARREDONDAR OS SALDOS FINAIS TAMBÉM (CÓDIGO ORIGINAL MANTIDO)
            sistema.contas[conta_origem]['saldo'] = sistema.arredondar_valor(sistema.contas[conta_origem]['saldo'])
            sistema.contas[conta_destino]['saldo'] = sistema.arredondar_valor(sistema.contas[conta_destino]['saldo'])
            
            # 🔥 SALVOS DEPOIS PARA DEBUG
            saldo_origem_depois = sistema.contas[conta_origem]['saldo']
            saldo_destino_depois = sistema.contas[conta_destino]['saldo']
            
            print(f"💱 CÂMBIO ADMIN - SALDOS:")
            print(f"  Origem {conta_origem}: {saldo_origem_antes:,.2f} → {saldo_origem_depois:,.2f} (-{valor_arredondado:,.2f})")
            print(f"  Destino {conta_destino}: {saldo_destino_antes:,.2f} → {saldo_destino_depois:,.2f} (+{valor_destino_arredondado:,.2f})")
            
            # Obter moedas para a descrição (CÓDIGO ORIGINAL MANTIDO)
            moeda_origem = sistema.contas[conta_origem]['moeda']
            moeda_destino = sistema.contas[conta_destino]['moeda']
            
            # 🔥🔥🔥 CORREÇÃO: SEMPRE USAR TAXA PRINCIPAL NA DESCRIÇÃO (CÓDIGO ORIGINAL MANTIDO)
            if tipo_taxa == 'inversa':
                taxa_principal = 1.0 / taxa
                taxa_exibicao = taxa_principal
                tipo_taxa_exibicao = "PRINCIPAL"
            else:
                taxa_exibicao = taxa
                tipo_taxa_exibicao = "PRINCIPAL"
            
            # 🔥 NOVO: Criar descrições com TAXA PRINCIPAL (CÓDIGO ORIGINAL MANTIDO)
            descricao_origem = f"OPERAÇÃO DE CÂMBIO - VENDA - {moeda_origem} {valor:,.2f} - Taxa {tipo_taxa_exibicao}: {taxa_exibicao:.6f} - {moeda_destino} {valor_destino_arredondado:,.2f}"
            descricao_destino = f"OPERAÇÃO DE CÂMBIO - COMPRA - {moeda_origem} {valor:,.2f} - Taxa {tipo_taxa_exibicao}: {taxa_exibicao:.6f} - {moeda_destino} {valor_destino_arredondado:,.2f}"
            
            # Registrar a transação (CÓDIGO ORIGINAL MANTIDO)
            transacao_id = str(random.randint(100000, 999999))
            while transacao_id in sistema.transferencias:
                transacao_id = str(random.randint(100000, 999999))
            
            sistema.transferencias[transacao_id] = {
                'id': transacao_id,
                'conta_remetente': conta_origem,
                'conta_destinatario': conta_destino,
                'valor': valor,
                'valor_destino': valor_destino_arredondado,
                'moeda': moeda_origem,
                'moeda_destino': moeda_destino,
                'tipo': 'cambio',
                'taxa_cambio': taxa,
                'tipo_taxa': tipo_taxa,
                'taxa_principal_exibicao': taxa_exibicao,
                'descricao_origem': descricao_origem,
                'descricao_destino': descricao_destino,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'executado_por': self._obter_usuario_executor(),
                'cliente_afetado': username
            }
            
            # 🔥🔥🔥 NOVO: ATUALIZAR SALDOS NO SUPABASE ANTES DE SALVAR TRANSAÇÃO
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # Atualizar conta origem
                    response_origem = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_origem_depois})\
                        .eq('id', conta_origem)\
                        .execute()
                    
                    # Atualizar conta destino  
                    response_destino = sistema.supabase.client.table('contas')\
                        .update({'saldo': saldo_destino_depois})\
                        .eq('id', conta_destino)\
                        .execute()
                    
                    if response_origem.data and response_destino.data:
                        print(f"✅ Saldos atualizados no Supabase:")
                        print(f"   {conta_origem}: {saldo_origem_depois:,.2f}")
                        print(f"   {conta_destino}: {saldo_destino_depois:,.2f}")
                    else:
                        print(f"⚠️ Erro ao atualizar saldos no Supabase")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar saldos no Supabase: {e}")
            
            # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
            self.salvar_cambio_supabase(
                transacao_id, valor, valor_destino_arredondado, moeda_origem, moeda_destino,
                taxa, conta_origem, conta_destino, username, tipo_taxa, taxa_exibicao
            )
            
            # Salvar dados (CÓDIGO ORIGINAL MANTIDO)
            sistema.salvar_contas()
            sistema.salvar_transferencias()
            
            print(f"Câmbio registrado: {valor} -> {valor_destino_arredondado}")
            print(f"Taxa principal exibida: {taxa_exibicao:.6f}")
            return True
            
        except Exception as e:
            print(f"Erro ao executar câmbio: {e}")
            return False

    def salvar_cambio_supabase(self, transacao_id, valor_origem, valor_destino, moeda_origem, moeda_destino,
                             taxa, conta_origem, conta_destino, username, tipo_taxa, taxa_exibicao):
        """Salva operação de câmbio do Gerenciar Contas no Supabase - VERSÃO CORRIGIDA"""
        try:
            sistema = App.get_running_app().sistema
            
            print(f"🔥 SALVAR_CAMBIO_SUPABASE (Gerenciar Contas) INICIADO")
            
            # 🔥 CORREÇÃO: Usar método direto do Supabase (sem asyncio complexo)
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # 🔥 CORREÇÃO CRÍTICA: Tratar sistema.usuario_logado corretamente
                    usuario_executor = sistema.usuario_logado
                    if isinstance(usuario_executor, dict):
                        usuario_executor = usuario_executor.get('username', 'sistema')
                    elif not isinstance(usuario_executor, str):
                        usuario_executor = 'sistema'
                    
                    # Preparar dados para Supabase
                    dados_supabase = {
                        'id': transacao_id,
                        'tipo': 'cambio',
                        'status': 'completed',
                        'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'moeda': moeda_origem,
                        'valor': valor_origem,
                        'conta_remetente': conta_origem,
                        'conta_destinatario': conta_destino,
                        'descricao': f'CÂMBIO ADMIN - {moeda_origem} → {moeda_destino}',
                        'usuario': self._obter_usuario_executor(),  # 🔥 CORREÇÃO APLICADA
                        'cliente': username,
                        'operacao': 'cambio_admin',
                        'par_moedas': f"{moeda_origem}_{moeda_destino}",
                        'valor_origem': valor_origem,
                        'valor_destino': valor_destino,
                        'cotacao': taxa_exibicao,
                        'moeda_origem': moeda_origem,
                        'moeda_destino': moeda_destino,
                        'tipo_taxa_usada': tipo_taxa,
                        'taxa_principal_registro': taxa_exibicao
                    }
                    
                    # 🔥 SALVAR TRANSAÇÃO NO SUPABASE (método direto)
                    response = sistema.supabase.client.table('transferencias')\
                        .insert(dados_supabase)\
                        .execute()
                    
                    if response.data:
                        print(f"✅ Transação de câmbio salva no Supabase: {transacao_id}")
                        return True
                    else:
                        print(f"⚠️ Erro ao salvar transação de câmbio no Supabase")
                        return False
                        
                except Exception as e:
                    print(f"⚠️ Erro ao salvar transação no Supabase: {e}")
                    return False
            else:
                print("❌ Supabase não conectado - transação salva apenas localmente")
                return False
                
        except Exception as e:
            print(f"❌ Erro geral em salvar_cambio_supabase: {e}")
            import traceback
            traceback.print_exc()
            return False



    def processar_cambio_nova_tela_admin(self, dados, conta_num, transacoes, transacoes_ids_utilizados, parse_data):
        """Processa operações de câmbio da nova tela - VERSÃO CORRIGIDA COM DESCRIÇÃO INTELIGENTE"""
        
        # Verificar se é uma operação de câmbio da nova tela
        if dados.get('tipo') != 'cambio' or 'conta_origem' not in dados:
            return False
        
        # Verificar se envolve nossa conta
        if dados.get('conta_origem') != conta_num and dados.get('conta_destino') != conta_num:
            return False
        
        sistema = App.get_running_app().sistema
        moeda = sistema.contas[conta_num]['moeda']
        
        try:
            # 🔥 USAR MÉTODO INTELIGENTE PARA GERAR DESCRIÇÃO
            descricao_inteligente = sistema.gerar_descricao_cambio_inteligente(dados, conta_num)
            
            # CLIENTE É ORIGEM (SAÍDA/DÉBITO)
            if dados.get('conta_origem') == conta_num:
                
                nova_transacao = {
                    'data': dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'descricao': descricao_inteligente,  # 🔥 DESCRIÇÃO INTELIGENTE
                    'credito': 0.00,
                    'debito': dados.get('valor_origem', 0),
                    'tipo': "Câmbio",
                    'moeda': dados.get('moeda_origem', moeda),
                    'timestamp': parse_data(dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    'id': dados.get('id', '')
                }
                
                transacoes.append(nova_transacao)
                transacoes_ids_utilizados.add(dados.get('id', ''))
                print(f"✅ CÂMBIO NOVA TELA ADMIN (ORIGEM): {descricao_inteligente}")
                return True
            
            # CLIENTE É DESTINO (ENTRADA/CRÉDITO)
            elif dados.get('conta_destino') == conta_num:
                
                nova_transacao = {
                    'data': dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'descricao': descricao_inteligente,  # 🔥 DESCRIÇÃO INTELIGENTE
                    'credito': dados.get('valor_destino', 0),
                    'debito': 0.00,
                    'tipo': "Câmbio",
                    'moeda': dados.get('moeda_destino', moeda),
                    'timestamp': parse_data(dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    'id': dados.get('id', '')
                }
                
                transacoes.append(nova_transacao)
                transacoes_ids_utilizados.add(dados.get('id', ''))
                print(f"✅ CÂMBIO NOVA TELA ADMIN (DESTINO): {descricao_inteligente}")
                return True
                
        except Exception as e:
            print(f"⚠️ Erro ao processar câmbio nova tela admin: {e}")
        
        return False

    def carregar_extrato_admin(self):
        """Carrega o extrato - VERSÃO REFATORADA IDÊNTICA AO CLIENTE"""
        print("🔄 INICIANDO carregar_extrato_admin...")  
        
        # 🔥 LIMPAR EXTRATO ANTES DE CARREGAR NOVOS DADOS
        self.limpar_extrato_admin()
        
        sistema = App.get_running_app().sistema
        
        # ✅ DEBUG CRÍTICO - VERIFICAR DE ONDE VÊM AS TRANSAÇÕES
        print(f"🔍 DEBUG ADMIN: Sistema tem {len(sistema.transferencias)} transferências totais")
        
        # 🔥 DEBUG: Verificar qual período está ativo
        periodo_texto = self.ids.combo_periodo_extrato.text if hasattr(self.ids, 'combo_periodo_extrato') else "30 dias"
        print(f"🔧 Período ativo: {periodo_texto}")
        
        # Validar seleção de cliente e conta
        if not hasattr(self, 'ids') or not self.ids.combo_cliente_extrato.text or not self.ids.combo_conta_extrato.text:
            self.mostrar_erro("Selecione um cliente e uma conta!")
            return
        
        # Obter dados da conta selecionada
        username = self.ids.combo_cliente_extrato.text.split(' - ')[0]
        conta_filtro = self.ids.combo_conta_extrato.text
        conta_num = conta_filtro.split(' - ')[0].strip()  # 🔥 ESTA É A VARIÁVEL CORRETA
        
        print(f"🔍 DEBUG ADMIN: Cliente selecionado: {username}")
        print(f"🔍 DEBUG ADMIN: Conta selecionada: {conta_num}")
        
        if conta_num not in sistema.contas:
            self.mostrar_erro("Conta não encontrada!")
            return
        
        dados_conta = sistema.contas[conta_num]
        moeda = dados_conta['moeda']
        saldo_atual = dados_conta['saldo']

        # ========== 🔥 🔥 🔥 DEBUG CRÍTICO - VERIFICAR SE O AJUSTE ESTÁ SENDO PROCESSADO ==========
        print("=== 🔍 DEBUG PROCESSAMENTO DO AJUSTE ADMIN ===")
        ajuste_encontrado = False
        for transferencia_id, dados in sistema.transferencias.items():
            if (dados.get('tipo') == 'ajuste_admin' and 
                abs(dados.get('valor', 0) - 10000) < 0.01):  # Encontrar ajuste de ~10,000
                ajuste_encontrado = True
                print(f"💰 AJUSTE ENCONTRADO NO SISTEMA: {transferencia_id}")
                print(f"   Valor: {dados.get('valor')}")
                print(f"   Tipo: {dados.get('tipo_ajuste')}")
                print(f"   Conta: {dados.get('conta_remetente')}")
                
                # Verificar se passa no filtro de conta
                conta_envolvida = (
                    dados['conta_remetente'] == conta_num or 
                    dados.get('conta_destinatario') == conta_num
                )
                print(f"   ✅ PASSA NO FILTRO DE CONTA? {conta_envolvida}")

        if not ajuste_encontrado:
            print("❌ AJUSTE DE 10,000 USD NÃO ENCONTRADO NO SISTEMA!")
        # ========== FIM DO DEBUG ==========

        # 🔥 INICIALIZAR VARIÁVEIS DE TRANSAÇÕES NO INÍCIO
        transacoes_todas = []  # Todas as transações sem filtro
        transacoes_filtradas = []  # Transações após filtro
        transacoes_ids_utilizados = set()
        
        # 🔥 DETERMINAR PERÍODO DO FILTRO - CONVERTER TEXTO PARA VALOR
        if periodo_texto == "7 dias":
            periodo = "7"
        elif periodo_texto == "30 dias":
            periodo = "30"
        elif periodo_texto == "90 dias":
            periodo = "90"
        else:  # Todo período
            periodo = "0"
        
        data_inicio_filtro = None
        data_fim_filtro = None
        
        print(f"🔧 Aplicando filtro do período: {periodo}")
        
        # 🔥 VARIÁVEL: Saldo inicial do período (para TODOS os períodos)
        saldo_inicial_periodo = 0.0
        
        # 🔥 PERÍODO PERSONALIZADO (se aplicável)
        if periodo == "personalizado":
            try:
                # Implementar lógica de período personalizado se necessário
                data_inicio_br = "01/01/2024"  # Placeholder
                data_fim_br = "31/12/2024"     # Placeholder
                
                print(f"🔧 Datas personalizadas: {data_inicio_br} -> {data_fim_br}")
                
                # Validar formato das datas
                if not self.validar_data_br(data_inicio_br) or not self.validar_data_br(data_fim_br):
                    self.mostrar_erro("Formato de data inválido! Use DD/MM/AAAA")
                    return
                
                # Converter para formato ISO
                data_inicio_iso = self.formatar_data_para_iso(data_inicio_br)
                data_fim_iso = self.formatar_data_para_iso(data_fim_br)
                
                data_inicio_filtro = datetime.datetime.strptime(data_inicio_iso, "%Y-%m-%d")
                data_fim_filtro = datetime.datetime.strptime(data_fim_iso, "%Y-%m-%d")
                
                if data_inicio_filtro > data_fim_filtro:
                    self.mostrar_erro("Data inicial não pode ser maior que data final!")
                    return
                    
                print(f"🔧 Datas convertidas: {data_inicio_filtro} -> {data_fim_filtro}")
                
                # 🔥 CORREÇÃO: CALCULAR SALDO DO DIA ANTERIOR PARA PERÍODO PERSONALIZADO
                data_dia_anterior = data_inicio_filtro - datetime.timedelta(days=1)
                print(f"🔧 Calculando saldo do dia anterior: {data_dia_anterior.date()}")
                
                # Chamar função auxiliar para calcular saldo até o dia anterior
                saldo_inicial_periodo = self.calcular_saldo_ate_data_admin(conta_num, data_dia_anterior)
                print(f"💰 SALDO INICIAL DO PERÍODO (dia anterior): {saldo_inicial_periodo:,.2f}")
                    
            except ValueError as e:
                self.mostrar_erro(f"Data inválida! Use o formato DD/MM/AAAA. Erro: {e}")
                return
        else:
            # 🔥 🔥 🔥 CORREÇÃO: PERÍODOS RÁPIDOS TAMBÉM USAM SALDO DO DIA ANTERIOR
            data_fim_filtro = datetime.datetime.now()

            # ========== 🔥 CARREGAR TRANSFERÊNCIAS DO SISTEMA ==========
            print("🔄 Buscando transferências do sistema...")
            
            # ✅ CORRETO: Usar sistema.transferencias (já carregado do Supabase)
            todas_transferencias = sistema.transferencias
            print(f"📊 Total de transferências no sistema: {len(todas_transferencias)}")
            
            # Filtrar transferências da conta selecionada
            contador_filtradas = 0
            for transferencia_id, dados in todas_transferencias.items():
                
                # 🔍 DEBUG ESPECÍFICO PARA TRANSFERÊNCIAS IMPORTANTES
                if transferencia_id in ["520676", "975457"]:
                    print(f"🔍 DEBUG {transferencia_id}: Data='{dados.get('data')}' | Tipo='{dados.get('tipo')}' | Status='{dados.get('status')}'")
                    print(f"🔍 DEBUG {transferencia_id}: Estrutura completa: {dados}")
                
                # ✅ FILTRO RIGOROSO - Apenas transações que REALMENTE afetam a conta
                conta_principal = (
                    dados.get('conta_remetente') == conta_num or 
                    dados.get('conta_destinatario') == conta_num or
                    dados.get('conta_origem') == conta_num or
                    dados.get('conta_destino') == conta_num
                )
                
                if conta_principal:
                    # ✅ VERIFICAÇÃO EXTRA: A transação deve ter valor DIFERENTE de zero
                    valor = dados.get('valor', 0)
                    valor_valido = valor != 0 and valor is not None
                    
                    # ✅ VERIFICAÇÃO EXTRA: Deve ter uma descrição/dados válidos
                    tem_descricao = bool(dados.get('descricao'))
                    tem_tipo = bool(dados.get('tipo'))
                    dados_validos = tem_descricao or tem_tipo
                    
                    # ✅ VERIFICAÇÃO EXTRA: Não pode ser apenas uma transação de câmbio zerada
                    nao_e_cambio_zerado = not (dados.get('tipo') == 'cambio' and valor == 0)
                    
                    if valor_valido and dados_validos and nao_e_cambio_zerado:
                        # 🔍 DEBUG TEMPORÁRIO PARA RASTREAR TRANSFERÊNCIAS IMPORTANTES
                        if transferencia_id in ["520676", "975457"]:
                            print(f"✅✅✅ TRANSFERÊNCIA {transferencia_id} PASSOU NO FILTRO PRINCIPAL!")
                            print(f"✅✅✅ Valor: {valor}, Dados válidos: {dados_validos}, Não é câmbio zerado: {nao_e_cambio_zerado}")
                        
                        # ✅ VOLTAR A ADICIONAR AQUI (enquanto não corrigimos o processamento principal)
                        transacoes_todas.append({
                            'id': transferencia_id,
                            'dados': dados,
                            'data': dados.get('data', ''),
                            'tipo': dados.get('tipo', 'transferencia')
                        })
                    
                    else:
                        contador_filtradas += 1
                        # DEBUG para ver o que está sendo filtrado
                        if transferencia_id in ["520676", "975457"]:
                            print(f"🚫 TRANSFERÊNCIA {transferencia_id} NÃO PASSOU NO FILTRO: valor_valido={valor_valido}, dados_validos={dados_validos}, nao_e_cambio_zerado={nao_e_cambio_zerado}")
            
            print(f"✅ {len(transacoes_todas)} transações válidas para a conta {conta_num}")
            print(f"🚫 {contador_filtradas} transações filtradas (zeradas/sem dados)")
            
            # ✅ DEBUG CRÍTICO - VERIFICAR O QUE FOI ADICIONADO
            print("🔍 DEBUG DAS TRANSAÇÕES ADICIONADAS:")
            for i, trans in enumerate(transacoes_todas[:5]):  # Mostrar apenas as 5 primeiras
                dados = trans['dados']
                print(f"   {i+1}. ID: {trans['id']} | Valor: {dados.get('valor')} | Descrição: {dados.get('descricao')} | Tipo: {dados.get('tipo')}")

            if periodo == "0":  # Todo período
                data_inicio_filtro = datetime.datetime(2020, 1, 1)  # Data bem antiga
                saldo_inicial_periodo = 0.0  # Começa do zero para todo período
                print("🔧 Período: TODO O PERÍODO (começa do zero)")
            else:
                # Calcular data de início baseada no período
                dias = int(periodo)
                data_inicio_filtro = data_fim_filtro - datetime.timedelta(days=dias)
                
                # 🔥 CALCULAR SALDO DO DIA ANTERIOR AO INÍCIO DO PERÍODO
                data_dia_anterior = data_inicio_filtro - datetime.timedelta(days=1)
                print(f"🔧 Calculando saldo do dia anterior ao período: {data_dia_anterior.date()}")
                
                saldo_inicial_periodo = self.calcular_saldo_ate_data_admin(conta_num, data_dia_anterior)
                print(f"💰 SALDO INICIAL DO PERÍODO RÁPIDO (dia anterior): {saldo_inicial_periodo:,.2f}")
            
            print(f"🔧 Período rápido: {data_inicio_filtro.date()} -> {data_fim_filtro.date()}")
        
        # 🔥 MOSTRAR FEEDBACK VISUAL DO FILTRO APLICADO
        if periodo == "personalizado":
            print(f"🎯 FILTRO PERSONALIZADO APLICADO: {data_inicio_filtro.date()} a {data_fim_filtro.date()}")
            print(f"💰 SALDO INICIAL DO PERÍODO: {saldo_inicial_periodo:,.2f}")
        else:
            if periodo == "0":
                periodo_texto = "TODO O PERÍODO"
            else:
                periodo_texto = f"ÚLTIMOS {periodo} DIAS"
            print(f"🎯 FILTRO RÁPIDO APLICADO: {periodo_texto}")
            print(f"💰 SALDO INICIAL DO PERÍODO: {saldo_inicial_periodo:,.2f}")
        
        # 🔥 USAR FUNÇÃO UNIFICADA DO SISTEMA
        def parse_data(data_str):
            sistema = App.get_running_app().sistema
            return sistema.parse_data_unificada(data_str)

        # 🔥 PASSO 1: CRIAR TRANSAÇÃO DE SALDO INICIAL COM VALOR CORRETO PARA TODOS OS PERÍODOS
        if periodo == "personalizado":
            # Para período personalizado, usar o saldo calculado do dia anterior
            saldo_inicial_transacao = {
                'data': data_inicio_filtro.strftime("%Y-%m-%d") + " 00:00:00",
                'descricao': "SALDO INICIAL DO PERÍODO",
                'credito': 0.00,
                'debito': 0.00,
                'saldo_apos': saldo_inicial_periodo,  # 🔥 USAR SALDO CALCULADO
                'tipo': "Saldo Inicial",
                'moeda': moeda,
                'timestamp': data_inicio_filtro.replace(hour=0, minute=0, second=0)
            }
        elif periodo == "0":
            # Para "Todo período", manter comportamento original (saldo zero)
            saldo_inicial_transacao = {
                'data': dados_conta.get('data_criacao', '2024-01-01 00:00:00'),
                'descricao': "SALDO INICIAL",
                'credito': 0.00,
                'debito': 0.00,
                'saldo_apos': 0.00,  # 🔥 COMPORTAMENTO ORIGINAL
                'tipo': "Saldo Inicial", 
                'moeda': moeda,
                'timestamp': parse_data(dados_conta.get('data_criacao', '2024-01-01 00:00:00'))
            }
        else:
            # 🔥 🔥 🔥 CORREÇÃO: PERÍODOS RÁPIDOS TAMBÉM USAM SALDO CALCULADO
            saldo_inicial_transacao = {
                'data': data_inicio_filtro.strftime("%Y-%m-%d") + " 00:00:00",
                'descricao': f"SALDO INICIAL - {periodo} DIAS",
                'credito': 0.00,
                'debito': 0.00,
                'saldo_apos': saldo_inicial_periodo,  # 🔥 USAR SALDO CALCULADO
                'tipo': "Saldo Inicial",
                'moeda': moeda,
                'timestamp': data_inicio_filtro.replace(hour=0, minute=0, second=0)
            }
        
        transacoes_todas.append(saldo_inicial_transacao)

        # 🔥 🔥 🔥 DEBUG ESPECÍFICO PARA TRANSAÇÕES IMPORTANTES
        print("=== 🚨 DEBUG ESPECÍFICO TRANSAÇÕES IMPORTANTES ===")
        for trans_id in ["408044_nt", "975457"]:
            if trans_id in sistema.transferencias:
                dados_trans = sistema.transferencias[trans_id]
                print(f"🔍 TRANSAÇÃO {trans_id} ENCONTRADA:")
                print(f"   Tipo: {dados_trans.get('tipo')}")
                print(f"   Conta remetente: {dados_trans.get('conta_remetente')}") 
                print(f"   Conta destinatario: {dados_trans.get('conta_destinatario')}")
                print(f"   Moeda: {dados_trans.get('moeda')}")
                print(f"   Valor: {dados_trans.get('valor')}")
                print(f"   Tem conta_origem? {'conta_origem' in dados_trans}")
                if 'conta_origem' in dados_trans:
                    print(f"   Conta origem: {dados_trans.get('conta_origem')}")
                    print(f"   Conta destino: {dados_trans.get('conta_destino')}")
            else:
                print(f"❌ {trans_id} NÃO ENCONTRADA NO SISTEMA")

        # 🔥 🔥 🔥 NOVO: PROCESSAR OPERACOES DE CAMBIO DA NOVA TELA PRIMEIRO
        for transferencia_id, dados in sistema.transferencias.items():
            if not dados or not isinstance(dados, dict):
                continue
                
            # 🔥 DEBUG: RASTREAR PROCESSAMENTO DAS TRANSAÇÕES IMPORTANTES
            if transferencia_id in ["408044_nt", "975457"]:
                print(f"🎯🎯🎯 {transferencia_id} NO PRIMEIRO LOOP")
                print(f"   Passa no filtro '_nt'? {('_nt' in transferencia_id or '_novatela' in transferencia_id)}")
                print(f"   Já processada? {transferencia_id in transacoes_ids_utilizados}")
                print(f"   Tem conta_origem? {'conta_origem' in dados}")
                print(f"   Vai chamar processar_cambio_nova_tela? {('conta_origem' in dados)}")

            # Tentar processar APENAS operacoes da nova tela
            if self.processar_cambio_nova_tela_admin(dados, conta_num, transacoes_todas, transacoes_ids_utilizados, parse_data):
                # Se processou, já foi adicionada às transacoes_todas
                pass

        # 🔥 PASSO 2: CRIAR TODAS AS TRANSAÇÕES COM PROCESSAMENTO DE RECEITAS
        for transferencia_id, dados in sistema.transferencias.items():
            
            # 🔥 DEBUG: RASTREAR PROCESSAMENTO DAS TRANSAÇÕES IMPORTANTES
            if transferencia_id in ["408044_nt", "975457"]:
                print(f"🎯🎯🎯 {transferencia_id} NO SEGUNDO LOOP")
                print(f"   Já processada? {transferencia_id in transacoes_ids_utilizados}")
                print(f"   Tipo: {dados.get('tipo')}")
                print(f"   Conta remetente: {dados.get('conta_remetente')}")
                print(f"   Conta destinatario: {dados.get('conta_destinatario')}")
                print(f"   Nossa conta: {conta_num}")
                print(f"   É remetente? {dados.get('conta_remetente') == conta_num}")
                print(f"   É destinatario? {dados.get('conta_destinatario') == conta_num}")
            
            # 🔥 CORREÇÃO: VERIFICAR SE JÁ FOI PROCESSADA NO PRIMEIRO LOOP
            if transferencia_id in transacoes_ids_utilizados:
                print(f"🔧 TRANSAÇÃO {transferencia_id} JÁ PROCESSADA - PULANDO DUPLICAÇÃO")
                continue  # 🔥 PULAR SE JÁ FOI PROCESSADA
            
            # 🔥 VERIFICAÇÃO ROBUSTA: Pular transferências inválidas
            if not dados or not isinstance(dados, dict):
                continue
                
            # 🔥 CORREÇÃO CRÍTICA: VERIFICAR SE 'conta_remetente' EXISTE ANTES DE USAR
            if 'conta_remetente' not in dados:
                print(f"⚠️ Transferência {transferencia_id} sem conta_remetente, ignorando...")
                continue
                
            # 🔥 VERIFICAÇÃO ESPECIAL PARA RECEITAS: Elas podem não ter 'conta_remetente'
            tipo = dados.get('tipo', '')
            
            # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: PROCESSAR RECEITAS PRIMEIRO (MESMA LÓGICA DO CLIENTE)
            if tipo == 'receita' or 'receita' in str(tipo).lower():
                print(f"✅ ENCONTRADA RECEITA NO EXTRATO ADMIN: {transferencia_id}")
                
                # 🔥 CORREÇÃO: Usar APENAS a descrição_receita, sem prefixos
                descricao_receita = dados.get('descricao_receita', dados.get('descricao', 'Lançamento de receita'))
                # 🔥 REMOVER qualquer prefixo de "RECEITA - " se existir
                if descricao_receita.startswith('RECEITA - '):
                    descricao_receita = descricao_receita.replace('RECEITA - ', '', 1)
                if ' - ' in descricao_receita and 'RECEITA' in descricao_receita:
                    # Se ainda tiver "RECEITA" em qualquer lugar, pegar apenas a parte final
                    partes = descricao_receita.split(' - ')
                    descricao_receita = partes[-1]  # Pegar apenas a última parte
                
                valor_receita = dados.get('valor', 0)
                data_receita = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                conta_remetente = dados.get('conta_remetente', '')
                conta_destinatario = dados.get('conta_destinatario', '')
                
                print(f"💰 RECEITA DEBUG ADMIN: remetente='{conta_remetente}', destinatario='{conta_destinatario}', conta_num='{conta_num}'")
                print(f"💰 DESCRIÇÃO FINAL: '{descricao_receita}'")
                
                # 🔥 CORREÇÃO: Se a conta remetente é a nossa conta, é um DÉBITO (saída)
                if conta_remetente == conta_num:
                    nova_transacao = {
                        'data': data_receita,
                        'descricao': descricao_receita,  # 🔥 APENAS A DESCRIÇÃO LIMPA
                        'credito': 0.00,
                        'debito': valor_receita,
                        'tipo': "Taxa/Despesa",  # 🔥 TIPO CORRETO
                        'moeda': dados.get('moeda', moeda),
                        'timestamp': parse_data(data_receita),
                        'id': transferencia_id
                    }
                    print(f"💰 RECEITA COMO DÉBITO: {valor_receita} {dados.get('moeda', moeda)}")
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                # 🔥 NOVA CONDIÇÃO: Se NENHUMA conta é nossa, mas somos o remetente
                elif conta_remetente == conta_num and conta_destinatario != conta_num:
                    # Somos o remetente pagando uma receita (débito)
                    nova_transacao = {
                        'data': data_receita,
                        'descricao': descricao_receita,  # 🔥 APENAS A DESCRIÇÃO LIMPA
                        'credito': 0.00,
                        'debito': valor_receita,
                        'tipo': "Taxa/Despesa",  # 🔥 TIPO CORRETO
                        'moeda': dados.get('moeda', moeda),
                        'timestamp': parse_data(data_receita),
                        'id': transferencia_id
                    }
                    print(f"💰 RECEITA COMO DÉBITO (conta contábil): {valor_receita} {dados.get('moeda', moeda)}")
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                else:
                    print(f"❌ RECEITA não processada - estrutura não reconhecida: {transferencia_id}")
                
                continue  # 🔥 IMPORTANTE: Pular para próxima transferência

            # 🔥 CORREÇÃO: VERIFICAR SE TEM 'conta_remetente' ANTES DE ACESSAR
            if 'conta_remetente' not in dados:
                print(f"⚠️ Transferência {transferencia_id} sem conta_remetente, ignorando...")
                continue

            # Para outros tipos, verificar a estrutura normal
            # 🔥 AGORA ESTÁ SEGURO ACESSAR dados['conta_remetente'] porque já verificamos que existe
            
            # 🔍 DEBUG: VERIFICAR CONTA ANTES DO FILTRO
            if transferencia_id in ["520676", "975457"]:
                print(f"🎯🎯🎯 DEBUG {transferencia_id} - ANTES DO FILTRO DE CONTA")
                print(f"🎯🎯🎯 Conta remetente: {dados.get('conta_remetente')}, Conta destinatario: {dados.get('conta_destinatario')}")
                print(f"🎯🎯🎯 Nossa conta: {conta_num}, Conta envolvida: {dados['conta_remetente'] == conta_num or dados.get('conta_destinatario') == conta_num}")

            # Verificar se a transação envolve nossa conta
            conta_envolvida = (
                dados['conta_remetente'] == conta_num or 
                dados.get('conta_destinatario') == conta_num
            )
            
            if not conta_envolvida:
                continue
            
            # MESMA LÓGICA DE DECISÃO DO CLIENTE
            status = dados['status']
            tipo = dados.get('tipo', 'transferencia_interna')
            
            # REGRAS DEFINITIVAS:
            if tipo in ['ajuste_admin', 'cambio']:
                # OPERAÇÕES DO ADMIN: SEMPRE incluir (não são transferências)
                deve_incluir = True
            elif status == 'pending':
                # SOLICITAÇÕES: incluir
                deve_incluir = True
            elif status == 'rejected':
                # ESTORNOS: incluir (nova transação de estorno)
                deve_incluir = True
            elif status in ['processing', 'completed']:
                # STATUS INTERMEDIÁRIOS/FINAIS: incluir para atualização
                deve_incluir = True
            else:
                deve_incluir = False
            
            if not deve_incluir:
                continue
            
            # 🔥 CONTINUAR COM A LÓGICA ORIGINAL DE CRIAÇÃO DAS TRANSAÇÕES (MESMA DO CLIENTE)
            
            # CLIENTE É REMETENTE (SAÍDAS/DÉBITOS)
            if dados['conta_remetente'] == conta_num:
                
                # 🔥 🔥 🔥 CORREÇÃO: CASO ESPECIAL PARA DEPÓSITOS (cliente como remetente)
                if tipo == 'deposito':
                    # Cliente está como remetente no depósito - isso é um CRÉDITO para o cliente
                    banco_origem = dados.get('banco_origem', 'Banco')
                    remetente = dados.get('remetente', 'Remetente')
                    descricao = f"DEPÓSITO CONFIRMADO - {banco_origem} - {remetente}"
                    
                    nova_transacao = {
                        'data': dados['data'],
                        'descricao': descricao,
                        'credito': dados['valor'],  # 🔥 CRÉDITO (entrada)
                        'debito': 0.00,
                        'tipo': "Depósito",
                        'moeda': dados['moeda'],
                        'timestamp': parse_data(dados['data']),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                    print(f"💰 DEPÓSITO CORRIGIDO: Cliente recebe CRÉDITO - {descricao}")
                    continue  # 🔥 IMPORTANTE: Pular o resto do processamento
                
                # AJUSTE ADMINISTRATIVO
                elif tipo == 'ajuste_admin':
                    tipo_ajuste = dados.get('tipo_ajuste', 'DÉBITO')
                    descricao = dados.get('descricao_ajuste', dados.get('finalidade', 'Ajuste administrativo'))
                    
                    data_operacao = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    if tipo_ajuste and (tipo_ajuste.upper() == 'CREDITO' or tipo_ajuste == 'credito'):
                        nova_transacao = {
                            'data': data_operacao,
                            'descricao': f"CRÉDITO ADMINISTRATIVO - {descricao}",
                            'credito': dados['valor'],
                            'debito': 0.00,
                            'tipo': "Crédito Admin",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_operacao),
                            'id': transferencia_id
                        }
                    else:
                        nova_transacao = {
                            'data': data_operacao,
                            'descricao': f"DÉBITO ADMINISTRATIVO - {descricao}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Débito Admin", 
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_operacao),
                            'id': transferencia_id
                        }
                    
                    # Adicionar transação à lista geral
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                # TRANSFERÊNCIA INTERNACIONAL
                elif tipo == 'internacional' or tipo == 'transferencia_internacional':
                    # 🔍 DEBUG: PROCESSAMENTO DE TRANSFERÊNCIA INTERNACIONAL
                    if transferencia_id in ["520676", "975457"]:
                        print(f"🎯🎯🎯 DEBUG {transferencia_id} - PROCESSANDO COMO TRANSFERÊNCIA INTERNACIONAL")
                        print(f"🎯🎯🎯 Status: {status}, Valor: {dados['valor']}")
                    
                    # 🔥🔥🔥 CORREÇÃO CRÍTICA: GARANTIR DATA VÁLIDA PARA PROCESSING
                    data_transacao = dados.get('data')
                    if status == 'processing':
                        if not data_transacao or data_transacao is None:
                            # Tentar várias fontes de data
                            data_transacao = (dados.get('data_solicitacao') or 
                                             dados.get('data_aprovacao') or 
                                             dados.get('data_processing') or 
                                             dados.get('data') or
                                             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            print(f"🔧🔧🔧 CORREÇÃO CRÍTICA ADMIN: Data None para {transferencia_id} -> {data_transacao}")
                        
                        # 🔥 GARANTIR que a data está no formato correto
                        try:
                            if data_transacao and 'T' in data_transacao:
                                # Converter de ISO para formato com espaço
                                data_obj = datetime.datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
                                data_transacao = data_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            # Fallback para data atual
                            data_transacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 🔥 CORREÇÃO: PARA REJEITADAS, CRIAR DUAS TRANSAÇÕES
                    # TRANSFERENCIA INTERNACIOAL REJEITADAS
                    if status == 'rejected':
                        # 1. Transação de débito (quando foi solicitada)
                        data_solicitacao = dados.get('data_solicitacao') or dados.get('data')
                        if not data_solicitacao:
                            data_solicitacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        timestamp_debito = parse_data(data_solicitacao)
                        
                        transacao_debito = {
                            'data': data_solicitacao,
                            'descricao': f"TRANSF. INTERNACIONAL SOLICITADA - {dados.get('beneficiario', 'N/A')}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Transferência Internacional",
                            'moeda': dados['moeda'],
                            'timestamp': timestamp_debito,
                            'id': f"{transferencia_id}_DEBITO"
                        }
                        
                        # 2. Transação de crédito (estorno quando foi rejeitada)
                        data_estorno = dados.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        transacao_credito = {
                            'data': data_estorno,
                            'descricao': f"ESTORNO TRANSF. INTERNACIONAL - {dados.get('beneficiario', 'N/A')}",
                            'credito': dados['valor'],
                            'debito': 0.00,
                            'tipo': "Estorno",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_estorno),
                            'id': f"{transferencia_id}_CREDITO"
                        }
                        
                        # Adicionar ambas as transações
                        transacoes_todas.append(transacao_debito)
                        transacoes_todas.append(transacao_credito)
                        transacoes_ids_utilizados.add(f"{transferencia_id}_DEBITO")
                        transacoes_ids_utilizados.add(f"{transferencia_id}_CREDITO")
                        
                        print(f"  -> CRIADAS DUAS TRANSAÇÕES: Débito + Estorno para transferência {transferencia_id}")
                    
                    else:
                        # Para outros status: criar UMA transação com status apropriado
                        status_text = "SOLICITADA" if status == 'pending' else "EM PROCESSAMENTO" if status == 'processing' else "CONCLUÍDA"

                        # 🔥🔥🔥 CORREÇÃO: GARANTIR DATA VÁLIDA PARA TODOS OS STATUS
                        # Buscar data de MÚLTIPLAS fontes para evitar None
                        data_transacao = (dados.get('data_conclusao') or 
                                         dados.get('data_aprovacao') or 
                                         dados.get('data_processing') or 
                                         dados.get('data_solicitacao') or 
                                         dados.get('data') or  # 🔥 ADICIONAR ESTA LINHA
                                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        # 🔥 CONVERTER para formato padrão se necessário
                        try:
                            if data_transacao and 'T' in data_transacao:
                                data_obj = datetime.datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
                                data_transacao = data_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception as e:
                            print(f"⚠️ Erro ao converter data {data_transacao}: {e}")
                            data_transacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        nova_transacao = {
                            'data': data_transacao,
                            'descricao': f"TRANSF. INTERNACIONAL {status_text} - {dados.get('beneficiario', 'N/A')}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Transferência Internacional",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_transacao),
                            'id': transferencia_id
                        }

                        # 🔍 DEBUG: ANTES DE ADICIONAR AO EXTRATO
                        if transferencia_id in ["520676", "975457"]:
                            print(f"🎯🎯🎯 DEBUG {transferencia_id} - CRIANDO TRANSAÇÃO FINAL")
                            print(f"🎯🎯🎯 Nova transação: {nova_transacao}")

                        transacoes_todas.append(nova_transacao)
                        transacoes_ids_utilizados.add(transferencia_id)
                
                # CÂMBIO (quando cliente vende moeda)
                elif tipo == 'cambio':
                    data_cambio = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    # 🔥 MUDANÇA: Usar descrição_origem se disponível, senão criar
                    descricao = dados.get('descricao_origem', 
                        sistema.gerar_descricao_cambio_inteligente(dados, conta_num))
                    
                    nova_transacao = {
                        'data': data_cambio,
                        'descricao': descricao,  # 🔥 USAR DESCRIÇÃO DETALHADA
                        'credito': 0.00,
                        'debito': dados['valor'],
                        'tipo': "Câmbio",
                        'moeda': dados['moeda'],
                        'timestamp': parse_data(data_cambio),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                # TRANSFERÊNCIA INTERNA ou TRANSFERÊNCIA INTERNA CLIENTE
                elif tipo in ['transferencia_interna', 'transferencia_interna_cliente']:
                    # 🔥 CORREÇÃO: PARA REJEITADAS, CRIAR DUAS TRANSAÇÕES
                    if status == 'rejected':
                        # 1. Transação de débito (quando foi solicitada)
                        data_solicitacao = dados.get('data_solicitacao') or dados.get('data')
                        if not data_solicitacao:
                            data_solicitacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        timestamp_debito = parse_data(data_solicitacao)
                        
                        transacao_debito = {
                            'data': data_solicitacao,
                            'descricao': f"TRANSFERÊNCIA SOLICITADA - {self.obter_nome_cliente_por_conta(sistema, dados.get('conta_destinatario', 'N/A'))}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Transferência",
                            'moeda': dados['moeda'],
                            'timestamp': timestamp_debito,
                            'id': f"{transferencia_id}_DEBITO"
                        }
                        
                        # 2. Transação de crédito (estorno quando foi rejeitada)
                        data_estorno = dados.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        transacao_credito = {
                            'data': data_estorno,
                            'descricao': f"ESTORNO TRANSFERÊNCIA - {self.obter_nome_cliente_por_conta(sistema, dados.get('conta_destinatario', 'N/A'))}",
                            'credito': dados['valor'],
                            'debito': 0.00,
                            'tipo': "Estorno",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_estorno),
                            'id': f"{transferencia_id}_CREDITO"
                        }
                        
                        # Adicionar ambas as transações
                        transacoes_todas.append(transacao_debito)
                        transacoes_todas.append(transacao_credito)
                        transacoes_ids_utilizados.add(f"{transferencia_id}_DEBITO")
                        transacoes_ids_utilizados.add(f"{transferencia_id}_CREDITO")
                        
                        print(f"  -> CRIADAS DUAS TRANSAÇÕES: Débito + Estorno para transferência {transferencia_id}")
                    
                    else:
                        # Para outros status: criar UMA transação com status apropriado
                        status_text = "SOLICITADA" if status == 'pending' else "EM PROCESSAMENTO" if status == 'processing' else "CONCLUÍDA"
                        
                        # 🔥🔥🔥 CORREÇÃO CRÍTICA: OBTER DATA CORRETA
                        # Primeiro tentar 'data', depois 'data_conclusao', depois fallback
                        data_transferencia = dados.get('data')
                        
                        # 🔥 DEBUG ESPECÍFICO PARA 733125
                        if transferencia_id == "733125":
                            print(f"🎯🎯🎯 DEBUG 733125 - OBTENDO DATA")
                            print(f"   Campo 'data': {dados.get('data')}")
                            print(f"   Campo 'data_conclusao': {dados.get('data_conclusao')}")
                            print(f"   Campo 'created_at': {dados.get('created_at')}")
                        
                        if not data_transferencia or data_transferencia == 'None':
                            data_transferencia = dados.get('data_conclusao', 
                                        dados.get('data_solicitacao', 
                                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        
                        # 🔥 CORREÇÃO: Se ainda não tem data, usar fallback com horário da transação
                        if not data_transferencia or data_transferencia == 'None':
                            data_transferencia = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        nova_transacao = {
                            'data': data_transferencia,
                            'descricao': f"TRANSFERÊNCIA {status_text} - {self.obter_nome_cliente_por_conta(sistema, dados.get('conta_destinatario', 'N/A'))}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Transferência" if tipo == 'transferencia_interna' else "Transferência Interna",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_transferencia),
                            'id': transferencia_id
                        }
                        
                        # 🔥 DEBUG ESPECÍFICO PARA 733125
                        if transferencia_id == "733125":
                            print(f"🎯🎯🎯 DEBUG 733125 - TRANSAÇÃO CRIADA")
                            print(f"   Data usada: {data_transferencia}")
                            print(f"   Timestamp: {parse_data(data_transferencia)}")
                            print(f"   Descrição: {nova_transacao['descricao']}")
                        
                        transacoes_todas.append(nova_transacao)
                        transacoes_ids_utilizados.add(transferencia_id)
            
            # CLIENTE É DESTINATÁRIO (ENTRADAS/CRÉDITOS)
            elif dados.get('conta_destinatario') == conta_num:
                
                # 🔥 🔥 🔥 CORREÇÃO: CASO ESPECÍFICO PARA DEPÓSITOS
                if tipo == 'deposito':
                    # Cliente recebe crédito de depósito confirmado
                    banco_origem = dados.get('banco_origem', 'Banco')
                    remetente = dados.get('remetente', 'Remetente')
                    descricao = f"DEPÓSITO CONFIRMADO - {banco_origem} - {remetente}"
                    
                    nova_transacao = {
                        'data': dados['data'],
                        'descricao': descricao,
                        'credito': dados['valor'],
                        'debito': 0.00,
                        'tipo': "Depósito",
                        'moeda': dados['moeda'],
                        'timestamp': parse_data(dados['data']),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                    print(f"💰 DEPÓSITO ADICIONADO NO EXTRATO ADMIN: {descricao}")
                
                # AJUSTES ADMIN COMO CRÉDITO
                elif tipo == 'ajuste_admin' and dados.get('tipo_ajuste') == 'CREDITO':
                    descricao = dados.get('descricao_ajuste', dados.get('finalidade', 'Ajuste administrativo'))
                    data_ajuste = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    nova_transacao = {
                        'data': data_ajuste,
                        'descricao': f"CRÉDITO ADMINISTRATIVO - {descricao}",
                        'credito': dados['valor'],
                        'debito': 0.00,
                        'tipo': "Crédito Admin",
                        'moeda': dados['moeda'],
                        'timestamp': parse_data(data_ajuste),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                # CÂMBIO (quando cliente compra moeda)
                elif tipo == 'cambio':
                    # 🔥 MUDANÇA: Usar descrição_destino se disponível, senão criar
                    descricao = dados.get('descricao_destino', 
                        sistema.gerar_descricao_cambio_inteligente(dados, conta_num))
                    
                    # 🔥 CORREÇÃO: Definir valor_credito ANTES de usar
                    valor_credito = dados.get('valor_destino', dados['valor'])
                    
                    nova_transacao = {
                        'data': dados['data'],
                        'descricao': descricao,  # 🔥 USAR DESCRIÇÃO DETALHADA
                        'credito': valor_credito,  # 🔥 AGORA valor_credito ESTÁ DEFINIDO
                        'debito': 0.00,
                        'tipo': "Câmbio",
                        'moeda': dados.get('moeda_destino', dados['moeda']),
                        'timestamp': parse_data(dados['data']),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
                
                # TRANSFERÊNCIA RECEBIDA
                elif tipo not in ['ajuste_admin']:
                    status_text = "SOLICITADA" if status == 'pending' else "EM PROCESSAMENTO" if status == 'processing' else "CONCLUÍDA" if status == 'completed' else "RECUSADA"
                    nova_transacao = {
                        'data': dados['data'],
                        'descricao': f"TRANSFERÊNCIA {status_text} RECEBIDA - {self.obter_nome_cliente_por_conta(sistema, dados['conta_remetente'])}",
                        'credito': dados['valor'],
                        'debito': 0.00,
                        'tipo': "Transferência",
                        'moeda': dados['moeda'],
                        'timestamp': parse_data(dados['data']),
                        'id': transferencia_id
                    }
                    
                    transacoes_todas.append(nova_transacao)
                    transacoes_ids_utilizados.add(transferencia_id)
        
        # 🔥 CORREÇÃO: PROCESSAR TRANSFERÊNCIAS INTERNACIONAIS QUE FORAM ADICIONADAS NO INÍCIO
        # (ANTES do filtro para garantir que tenham os campos necessários)
        for transacao in transacoes_todas:
            if 'dados' in transacao and transacao['dados'].get('tipo') in ['internacional', 'transferencia_internacional']:
                dados = transacao['dados']
                status = dados.get('status', '')
                
                # Só processar se ainda não foi processada (não tem campos de crédito/débito)
                if 'credito' not in transacao and 'debito' not in transacao:
                    # Para transferências internacionais com status 'solicitada'
                    if status == 'solicitada':
                        transacao['descricao'] = f"TRANSF. INTERNACIONAL SOLICITADA - {dados.get('beneficiario', 'N/A')}"
                        transacao['debito'] = dados['valor']
                        transacao['credito'] = 0.00
                        transacao['tipo'] = "Transferência Internacional"
                        transacao['moeda'] = dados['moeda']
                        transacao['timestamp'] = parse_data(dados['data'])  # 🔥 ADICIONAR TIMESTAMP
                        
                        # 🔍 DEBUG
                        if transacao.get('id') in ["520676", "975457"]:
                            print(f"🎯🎯🎯 DEBUG {transacao.get('id')} - PROCESSADA COMO TRANSFERÊNCIA SOLICITADA")
                            print(f"🎯🎯🎯 Descrição: {transacao['descricao']}")
                            print(f"🎯🎯🎯 Débito: {transacao['debito']}")

        # ✅ DEBUG FINAL - VERIFICAR SE O AJUSTE ESTÁ NA LISTA FINAL
        print("=== 🔍 DEBUG LISTA FINAL DE TRANSAÇÕES ADMIN ===")
        ajuste_na_lista = False
        for trans in transacoes_todas:
            if (trans.get('dados', {}).get('tipo') == 'ajuste_admin' and 
                abs(trans.get('dados', {}).get('valor', 0) - 10000) < 0.01):
                ajuste_na_lista = True
                print(f"✅ AJUSTE ENCONTRADO NA LISTA FINAL: {trans.get('id')}")
                break

        if not ajuste_na_lista:
            print("❌ AJUSTE NÃO ESTÁ NA LISTA FINAL!")

        # 🔥 PASSO 3: AGORA APLICAR O FILTRO NAS TRANSAÇÕES JÁ CRIADAS
        for transacao in transacoes_todas:
            
            # 🔍 DEBUG ESPECÍFICO PARA TRANSAÇÕES IMPORTANTES
            if transacao.get('id') in ["520676", "975457"]:
                print(f"🎯🎯🎯 DEBUG {transacao.get('id')} NO PROCESSAMENTO FINAL")
                print(f"🎯🎯🎯 Transação: {transacao}")
                print(f"🎯🎯🎯 Tem dados: {'dados' in transacao}")
                if 'dados' in transacao:
                    print(f"🎯🎯🎯 Dados: {transacao['dados']}")

            data_transacao_str = transacao['data']
            
            # Se não há filtro de data, incluir todas as transações
            if data_inicio_filtro is None or data_fim_filtro is None:
                transacoes_filtradas.append(transacao)
                continue
            
            try:
                data_transacao = parse_data(data_transacao_str)
                
                # Converter para data apenas (sem hora) para comparação
                data_transacao_sem_hora = data_transacao.replace(hour=0, minute=0, second=0, microsecond=0)
                data_inicio_sem_hora = data_inicio_filtro.replace(hour=0, minute=0, second=0, microsecond=0)
                data_fim_sem_hora = data_fim_filtro.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Verificar se a transação está dentro do período
                if data_transacao_sem_hora >= data_inicio_sem_hora and data_transacao_sem_hora <= data_fim_sem_hora:
                    transacoes_filtradas.append(transacao)
                    print(f"✅ TRANSAÇÃO INCLUÍDA: {data_transacao_sem_hora.date()} - {transacao['descricao']}")
                else:
                    print(f"🔧 TRANSAÇÃO FILTRADA FORA DO PERÍODO: {data_transacao_sem_hora.date()} - {transacao['descricao']}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao processar data da transação: {e}")
                # Em caso de erro, incluir a transação
                transacoes_filtradas.append(transacao)
        
        # ✅ FILTRO FINAL - REMOVER TRANSAÇÕES ZERADAS E SEM DESCRIÇÃO (VERSÃO CORRIGIDA)
        print(f"🔍 FILTRO FINAL ADMIN: {len(transacoes_todas)} transações antes do filtro")
        
        transacoes_filtradas_final = []
        for trans in transacoes_todas:
            # ✅ CORREÇÃO: Verificar se a transação tem estrutura válida
            if not isinstance(trans, dict):
                print(f"🚫 FILTRO FINAL REMOVIDA: Transação inválida (não é dict): {trans}")
                continue
                
            # ✅ CORREÇÃO: Verificar se tem a chave 'dados'
            if 'dados' not in trans:
                print(f"🚫 FILTRO FINAL REMOVIDA: Sem chave 'dados': {trans}")
                continue
                
            dados = trans['dados']
            
            # ✅ CORREÇÃO: Verificar se dados é um dict válido
            if not isinstance(dados, dict):
                print(f"🚫 FILTRO FINAL REMOVIDA: Dados inválidos: {dados}")
                continue
            
            # Verificar se tem valor válido E descrição/tipo válido
            valor_valido = dados.get('valor', 0) != 0
            tem_descricao = bool(dados.get('descricao'))
            tem_tipo_valido = bool(dados.get('tipo')) and dados.get('tipo') != 'cambio'
            
            if valor_valido or tem_descricao or tem_tipo_valido:
                transacoes_filtradas_final.append(trans)
            else:
                print(f"🚫 FILTRO FINAL REMOVIDA: ID {trans.get('id', 'N/A')} - Valor: {dados.get('valor')}, Descrição: {dados.get('descricao')}")
        
        transacoes_todas = transacoes_filtradas_final
        print(f"✅ FILTRO FINAL ADMIN: {len(transacoes_todas)} transações após filtro")

        # 🔍 DEBUG CRÍTICO - VERIFICAR ONDE AS TRANSAÇÕES SÃO ADICIONADAS
        print(f"🔍 DEBUG FINAL ADMIN: transacoes_todas tem {len(transacoes_todas)} itens")
        
        # Verificar a estrutura real das transações
        if transacoes_todas:
            print("🔍 ESTRUTURA DA PRIMEIRA TRANSAÇÃO ADMIN:")
            print(f"   Tipo: {type(transacoes_todas[0])}")
            print(f"   Conteúdo: {transacoes_todas[0]}")
            if isinstance(transacoes_todas[0], dict):
                print(f"   Chaves: {transacoes_todas[0].keys()}")
        print(f"📊 TRANSAÇÕES APÓS FILTRO ADMIN: {len(transacoes_filtradas)}")
        
        # 🔥🔥🔥 CORREÇÃO CRÍTICA: VERIFICAR E CORRIGIR DATAS None ANTES DO FILTRO
        for trans in transacoes_filtradas:
            if trans.get('data') is None or trans.get('data') == 'None':
                # Tentar obter data do timestamp
                timestamp = trans.get('timestamp')
                if timestamp:
                    trans['data'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔧 CORREÇÃO PÓS-PROCESSAMENTO ADMIN: Data None corrigida para {trans.get('id')} -> {trans['data']}")
                else:
                    # Data fallback
                    trans['data'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔧 CORREÇÃO PÓS-PROCESSAMENTO ADMIN: Data None com fallback para {trans.get('id')}")

        # ✅ FILTRO FINAL DEFINITIVO - REMOVER TRANSAÇÕES ZERADAS
        print(f"🔍 FILTRO FINAL DEFINITIVO ADMIN: {len(transacoes_filtradas)} transações antes do filtro")

        # 🔍 DEBUG ESPECÍFICO PARA TRANSAÇÕES IMPORTANTES
        for trans in transacoes_filtradas:
            if trans.get('id') in ["520676", "975457"]:
                print(f"🔍 DEBUG {trans.get('id')} NO FILTRO FINAL: {trans}")
                print(f"🔍 DEBUG {trans.get('id')} - credito: {trans.get('credito')}, debito: {trans.get('debito')}, descricao: '{trans.get('descricao')}'")

        transacoes_finais = []
        for trans in transacoes_filtradas:
            # ✅ CORREÇÃO: Converter None para 0 (NÃO ALTERA A LÓGICA DOS CÁLCULOS)
            credito = trans.get('credito') or 0
            debito = trans.get('debito') or 0
            descricao = trans.get('descricao', '')
            
            # MANTER apenas transações com valor OU com descrição válida
            if credito != 0 or debito != 0 or (descricao and descricao.strip() != ''):
                transacoes_finais.append(trans)
            else:
                print(f"🚫 FILTRO FINAL REMOVIDA ADMIN: {trans.get('id', 'N/A')} - '{descricao}'")
        
        print(f"✅ FILTRO FINAL DEFINITIVO ADMIN: {len(transacoes_finais)} transações após filtro")
        
        # 🔥 DEFINIR transacoes FINALMENTE
        transacoes = transacoes_finais
        
        # 🔥 DEBUG CRÍTICO DA ORDENAÇÃO
        print("=== 🚨 DEBUG CRÍTICO DA ORDENAÇÃO ADMIN ===")
        for i, trans in enumerate(transacoes[:10]):  # Mostrar primeiras 10
            timestamp = trans.get('timestamp')
            data = trans.get('data', '')
            print(f"{i}. Data: {data} | Timestamp: {timestamp} | Tipo: {type(timestamp)}")
        
        # 4. CALCULAR SALDO SEQUENCIAL CORRETAMENTE
        # Ordenar por timestamp (mais antiga primeiro) para cálculo
        transacoes_ordenadas_calculo = sorted(
            transacoes, 
            key=lambda x: x.get('timestamp') or datetime.datetime(2000, 1, 1)
        )
        
        # 🔥 VERIFICAR SE ORDENOU CORRETAMENTE
        print("=== ✅ VERIFICAÇÃO DA ORDENAÇÃO ADMIN ===")
        for i, trans in enumerate(transacoes_ordenadas_calculo[:10]):
            timestamp = trans.get('timestamp')
            data = trans.get('data', '')
            print(f"{i}. Data: {data} | Timestamp: {timestamp}")

        # 🔥 CORREÇÃO: Para TODOS os períodos (exceto "Todo período"), começar do saldo calculado
        if periodo == "0":
            saldo_sequencial = 0
            print("💰 CALCULANDO SALDO SEQUENCIAL A PARTIR DE ZERO (TODO PERÍODO)")
        else:
            saldo_sequencial = saldo_inicial_periodo
            print(f"💰 CALCULANDO SALDO SEQUENCIAL A PARTIR DE: {saldo_sequencial:,.2f}")

        for transacao in transacoes_ordenadas_calculo:
            # 🔥 PULAR o saldo inicial (já definimos como saldo_inicial_periodo)
            if transacao['tipo'] == "Saldo Inicial":
                # Já tem o saldo_apos correto, pular cálculo
                continue
                
            # Aplicar a transação ao saldo
            saldo_sequencial += transacao.get('credito', 0) - transacao.get('debito', 0)
            transacao['saldo_apos'] = saldo_sequencial

        # 5. 🔥 PASSO 2: VERIFICAR SE PRECISA DE AJUSTE (APÓS calcular o saldo sequencial)
        total_creditos = sum(t.get('credito', 0) for t in transacoes_ordenadas_calculo)
        total_debitos = sum(t.get('debito', 0) for t in transacoes_ordenadas_calculo)
        saldo_calculado_final = saldo_sequencial  # Já calculado acima

        # 🔥 DEBUG DETALHADO: Verificar todas as transações
        print("=== DEBUG TRANSAÇÕES DETALHADO ADMIN ===")
        for i, t in enumerate(transacoes_ordenadas_calculo):
            print(f"{i+1}. {t.get('data', '')} | {t.get('descricao', '')} | Crédito: {t.get('credito', 0):,.2f} | Débito: {t.get('debito', 0):,.2f} | Saldo: {t.get('saldo_apos', 0):,.2f}")

        print(f"💰 DEBUG SALDO ADMIN: Atual={saldo_atual:,.2f} | Calculado={saldo_calculado_final:,.2f} | Diferença={saldo_atual - saldo_calculado_final:,.2f}")

        diferenca = saldo_atual - saldo_calculado_final
        
        # 6. ORDENAR PARA EXIBIÇÃO (mais antiga primeiro) - CORREÇÃO
        transacoes_exibicao = transacoes_ordenadas_calculo  # Já está ordenada do mais antigo para o mais recente
        
        # 7. 🔥 CALCULAR TOTAIS FINAIS (APÓS todas as correções)
        total_entradas = sum(t.get('credito', 0) for t in transacoes_exibicao)
        total_saidas = sum(t.get('debito', 0) for t in transacoes_exibicao)
        
        print(f"💰 TOTAIS CALCULADOS ADMIN: Entradas={total_entradas:,.2f}, Saídas={total_saidas:,.2f}")  # DEBUG
        
        # 8. ATUALIZAR A INTERFACE
        self.atualizar_interface_extrato_admin(transacoes_exibicao, saldo_atual, total_entradas, total_saidas, moeda, periodo, username)
        
        print("✅ Extrato admin carregado com sucesso!")

    def calcular_saldo_ate_data_admin(self, conta_num, data_limite):
        """Calcula o saldo da conta ADMINISTRATIVA até uma data específica - VERSÃO ADAPTADA"""
        sistema = App.get_running_app().sistema
        
        if conta_num not in sistema.contas:
            return 0.0
        
        # Iniciar saldo como zero
        saldo_acumulado = 0.0
        moeda = sistema.contas[conta_num]['moeda']
        
        print(f"\n🔧🔧🔧 CALCULANDO SALDO ADMIN PARA CONTA {conta_num} ({moeda}) 🔧🔧🔧")
        print(f"🔧 Data limite: {data_limite}")
        
        # Coletar TODAS as transações da conta (sem filtro de data)
        todas_transacoes = []
        
        # 🔥 DEBUG: Contador de transações
        total_transacoes = 0
        transacoes_processadas = 0
        
        # Coletar transações de transferências
        for transferencia_id, dados in sistema.transferencias.items():
            total_transacoes += 1
            
            # 🔥 CORREÇÃO: Verificar se a transferência tem a estrutura básica necessária
            if not dados or not isinstance(dados, dict):
                continue
            
            # 🔥 🔥 🔥 CORREÇÃO ADMIN: VERIFICAR SE A CONTA ADMIN ESTÁ ENVOLVIDA
            # Para extrato administrativo, consideramos contas da empresa também
            conta_envolvida = False
            tipo_transacao = dados.get('tipo', '')
            
            # 1. VERIFICAR SE NOSSA CONTA ESTÁ ENVOLVIDA (MESMA LÓGICA DO CLIENTE)
            conta_remetente = dados.get('conta_remetente')
            conta_destinatario = dados.get('conta_destinatario')
            
            conta_envolvida = (
                conta_remetente == conta_num or 
                conta_destinatario == conta_num
            )
            
            if not conta_envolvida:
                # 🔥 PARA ADMIN: Verificar também se é uma transação da empresa (contas comuns)
                # Se a conta não está envolvida diretamente, pode ser uma transação administrativa
                if tipo_transacao == 'ajuste_admin':
                    # Para ajustes admin, verificar se a conta é a destinatária ou remetente
                    if dados.get('conta') == conta_num:
                        conta_envolvida = True
            
            if not conta_envolvida:
                continue
            
            # 🔥 ADMIN: Incluir transações com diferentes status
            status = dados.get('status')
            if status not in ['completed', 'processing', 'pending']:
                continue
            
            # 🔥🔥🔥 USAR DATA REAL DA TRANSAÇÃO
            data_transacao = dados.get('data', '2024-01-01 00:00:00')
            timestamp = self.parse_data_simples(data_transacao)
            valor = dados.get('valor', 0)
            
            transacoes_processadas += 1
            
            # 🔥 DEBUG ADMIN
            print(f"🎯 TRANSAÇÃO ADMIN ENCONTRADA: {transferencia_id} | Tipo: {tipo_transacao} | Valor: {valor:,.2f}")
            
            # 🔥 PROCESSAR CADA TIPO DE TRANSAÇÃO COM LÓGICA ADMINISTRATIVA
            
            # 1. AJUSTES ADMINISTRATIVOS (ESPECIAL PARA ADMIN)
            if tipo_transacao == 'ajuste_admin':
                # 🔥 ADMIN: Lógica específica para ajustes
                tipo_ajuste = dados.get('tipo_ajuste', 'DÉBITO')
                
                # Verificar se é CRÉDITO ou DÉBITO para a conta específica
                if tipo_ajuste and (tipo_ajuste.upper() == 'CREDITO' or tipo_ajuste == 'credito'):
                    # AJUSTE POSITIVO → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,  # Aumenta saldo
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': 'ajuste_admin',
                        'id': transferencia_id
                    })
                    print(f"   💰 AJUSTE POSITIVO ADMIN: +{valor:,.2f}")
                else:
                    # AJUSTE NEGATIVO → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,  # Diminui saldo
                        'timestamp': timestamp,
                        'tipo': 'ajuste_admin',
                        'id': transferencia_id
                    })
                    print(f"   💰 AJUSTE NEGATIVO ADMIN: -{valor:,.2f}")
            
            # 2. CÂMBIO (lógica similar ao cliente, mas com debug admin)
            elif tipo_transacao == 'cambio':
                if dados.get('conta_remetente') == conta_num:
                    # Conta é REMETENTE (vendeu moeda) → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': 'cambio',
                        'id': transferencia_id
                    })
                    print(f"   💰 CÂMBIO ADMIN SAÍDA: -{valor:,.2f}")
                elif dados.get('conta_destinatario') == conta_num:
                    # Conta é DESTINATÁRIO (comprou moeda) → ENTRADA
                    valor_entrada = dados.get('valor_destino', valor)
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor_entrada,
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': 'cambio',
                        'id': transferencia_id
                    })
                    print(f"   💰 CÂMBIO ADMIN ENTRADA: +{valor_entrada:,.2f}")
            
            # 3. TRANSFERÊNCIAS INTERNACIONAIS
            elif tipo_transacao in ['transferencia_internacional', 'internacional']:
                if dados.get('conta_remetente') == conta_num:
                    # Conta é REMETENTE → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': 'transferencia_internacional',
                        'id': transferencia_id
                    })
                    print(f"   💰 INTERNACIONAL ADMIN SAÍDA: -{valor:,.2f}")
                elif dados.get('conta_destinatario') == conta_num:
                    # Conta é DESTINATÁRIO → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': 'transferencia_internacional',
                        'id': transferencia_id
                    })
                    print(f"   💰 INTERNACIONAL ADMIN ENTRADA: +{valor:,.2f}")
            
            # 4. RECEITAS
            elif tipo_transacao == 'receita':
                if dados.get('conta_remetente') == conta_num:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': 'receita',
                        'id': transferencia_id
                    })
                    print(f"   💰 RECEITA ADMIN: +{valor:,.2f}")
            
            # 5. DESPESAS
            elif tipo_transacao == 'despesa':
                if dados.get('conta_remetente') == conta_num:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': 'despesa',
                        'id': transferencia_id
                    })
                    print(f"   💰 DESPESA ADMIN: -{valor:,.2f}")
            
            # 6. DEPÓSITOS
            elif tipo_transacao == 'deposito':
                if dados.get('conta_destinatario') == conta_num:
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': 'deposito',
                        'id': transferencia_id
                    })
                    print(f"   💰 DEPÓSITO ADMIN: +{valor:,.2f}")
            
            # 7. TRANSFERÊNCIAS INTERNAS (NOVO)
            elif tipo_transacao in ['transferencia_interna', 'transferencia_interna_cliente']:
                if dados.get('conta_remetente') == conta_num:
                    # Conta fez transferência → SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': 'transferencia_interna',
                        'id': transferencia_id
                    })
                    print(f"   💰 TRANSFERÊNCIA INTERNA ADMIN SAÍDA: -{valor:,.2f}")
                elif dados.get('conta_destinatario') == conta_num:
                    # Conta recebeu transferência → ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': 'transferencia_interna',
                        'id': transferencia_id
                    })
                    print(f"   💰 TRANSFERÊNCIA INTERNA ADMIN ENTRADA: +{valor:,.2f}")
            
            # 8. OUTROS TIPOS - LÓGICA GENÉRICA
            else:
                print(f"   ⚠️ TIPO ADMIN NÃO MAPEADO: {tipo_transacao}")
                if dados.get('conta_remetente') == conta_num:
                    # SAÍDA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': 0.00,
                        'debito': valor,
                        'timestamp': timestamp,
                        'tipo': tipo_transacao,
                        'id': transferencia_id
                    })
                    print(f"   💰 SAÍDA GENÉRICA ADMIN: -{valor:,.2f}")
                elif dados.get('conta_destinatario') == conta_num:
                    # ENTRADA
                    todas_transacoes.append({
                        'data': data_transacao,
                        'credito': valor,
                        'debito': 0.00,
                        'timestamp': timestamp,
                        'tipo': tipo_transacao,
                        'id': transferencia_id
                    })
                    print(f"   💰 ENTRADA GENÉRICA ADMIN: +{valor:,.2f}")
        
        # 🔥 DEBUG: Resumo do processamento ADMIN
        print(f"\n📊 RESUMO PROCESSAMENTO ADMIN:")
        print(f"   Total de transações no sistema: {total_transacoes}")
        print(f"   Transações processadas: {transacoes_processadas}")
        print(f"   Transações na lista final: {len(todas_transacoes)}")
        
        if not todas_transacoes:
            print("⚠️ Nenhuma transação encontrada para esta conta administrativa")
            return 0.0
        
        # Ordenar transações por data (mais antigas primeiro)
        todas_transacoes_ordenadas = sorted(todas_transacoes, key=lambda x: x['timestamp'])
        
        # 🔥 DEBUG: Mostrar todas as transações que serão consideradas
        print(f"\n📋 TRANSAÇÕES ADMIN NA LISTA DE CÁLCULO:")
        for i, transacao in enumerate(todas_transacoes_ordenadas[:20]):  # Mostrar só as primeiras 20
            tipo = transacao.get('tipo', 'desconhecido')
            print(f"   {i}. {transacao['timestamp']} | {tipo} | Crédito: {transacao['credito']:,.2f} | Débito: {transacao['debito']:,.2f}")
        
        if len(todas_transacoes_ordenadas) > 20:
            print(f"   ... e mais {len(todas_transacoes_ordenadas) - 20} transações")
        
        # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: Calcular saldo acumulado até o FINAL do dia ANTERIOR
        import datetime
        
        # 🔥 DEBUG DETALHADO ADMIN
        print(f"\n🔧🔧🔧 DEBUG CALCULAR_SALDO_ADMIN:")
        print(f"   Data limite recebida: {data_limite}")
        
        # Subtrair UM DIA para obter o dia anterior
        data_fim_calculo = data_limite - datetime.timedelta(days=1)
        
        # Ajustar para o FINAL do dia anterior (23:59:59.999999)
        data_fim_calculo = data_fim_calculo.replace(hour=23, minute=59, second=59, microsecond=999999)
        print(f"   🔥 Calculando saldo até o FINAL de {data_fim_calculo.date()}")
        
        # Calcular saldo acumulado até a data limite (FINAL do dia anterior)
        saldo_acumulado = 0.0
        transacoes_incluidas = 0
        transacoes_excluidas = 0
        
        print(f"\n🔧 FILTRANDO TRANSAÇÕES ADMIN (até {data_fim_calculo}):")
        
        for i, transacao in enumerate(todas_transacoes_ordenadas):
            # Só incluir transações até o FINAL do dia anterior
            if transacao['timestamp'] <= data_fim_calculo:
                credito = transacao.get('credito', 0)
                debito = transacao.get('debito', 0)
                saldo_acumulado += credito - debito
                transacoes_incluidas += 1
                
                if i < 10:  # Mostrar detalhes das primeiras 10 transações incluídas
                    tipo = transacao.get('tipo', 'desconhecido')
                    print(f"  ✅ #{i} [{tipo}] {transacao['timestamp']} | +{credito:,.2f}/-{debito:,.2f} | Saldo: {saldo_acumulado:,.2f}")
            else:
                transacoes_excluidas += 1
                if transacoes_excluidas == 1:
                    print(f"  🔧 PRIMEIRA TRANSAÇÃO EXCLUÍDA: {transacao['timestamp']} (após {data_fim_calculo.date()})")
        
        print(f"\n📊 RESUMO FINAL ADMIN:")
        print(f"   Transações totais: {len(todas_transacoes_ordenadas)}")
        print(f"   Transações incluídas: {transacoes_incluidas}")
        print(f"   Transações excluídas: {transacoes_excluidas}")
        print(f"   💰 SALDO FINAL CALCULADO: {saldo_acumulado:,.2f} {moeda}")
        
        return saldo_acumulado

    def limpar_extrato_admin(self):
        """Limpa o extrato administrativo antes de carregar novos dados"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'lista_transacoes_admin'):
            self.ids.lista_transacoes_admin.clear_widgets()
        
        # Limpar variáveis de estado
        if hasattr(self, 'transacoes_filtradas_admin'):
            self.transacoes_filtradas_admin = []
        
        print("🧹 Extrato administrativo limpo")

    def scroll_para_topo_admin(self):
        """Rola automaticamente para o topo da lista de transações administrativas"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'scroll_extrato_admin'):
            # Agendar o scroll para depois que a interface for atualizada
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_extrato_admin, 'scroll_y', 1), 0.1)


    def atualizar_resumo_admin(self, saldo_atual, total_entradas, total_saidas, total_transacoes, moeda, periodo, username):
        """Atualiza o painel de resumo administrativo"""
        if not hasattr(self, 'ids'):
            print("❌ DEBUG ADMIN: Não tem ids!")  # DEBUG
            return
        
        print(f"🔥 DEBUG RESUMO ADMIN: Entradas={total_entradas:,.2f}, Saídas={total_saidas:,.2f}, Transações={total_transacoes}")  # DEBUG
        
        # Atualizar labels de resumo
        self.ids.lbl_saldo_total_admin.text = f"{saldo_atual:,.2f} {moeda}"
        self.ids.lbl_total_entradas_admin.text = f"{total_entradas:,.2f} {moeda}"
        self.ids.lbl_total_saidas_admin.text = f"{total_saidas:,.2f} {moeda}"
        self.ids.lbl_total_transacoes_admin.text = f"{total_transacoes}"
        
        # Atualizar informação do período e cliente
        if periodo == "0":
            periodo_texto = "Todo período"
        else:
            periodo_texto = f"Últimos {periodo} dias"
        
        self.ids.lbl_periodo_admin.text = f"{periodo_texto} - Cliente: {username}"



    def validar_data_br(self, data_br):
        """Valida data no formato DD/MM/AAAA"""
        try:
            partes = data_br.split('/')
            if len(partes) != 3:
                return False
            dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
            datetime.datetime(ano, mes, dia)
            return True
        except:
            return False

    def formatar_data_para_iso(self, data_br):
        """Converte data de DD/MM/AAAA para AAAA-MM-DD"""
        try:
            partes = data_br.split('/')
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
        except:
            pass
        return data_br

    def obter_nome_cliente_por_conta(self, sistema, conta_num):
        """Obtém o nome do cliente por número da conta"""
        if conta_num in sistema.contas:
            return sistema.contas[conta_num].get('cliente_nome', 'N/A')
        return 'N/A'

    def parse_data_simples(self, data_str):
        """Versão simplificada do parse_data para uso no cálculo de saldo - CORREÇÃO CRÍTICA"""
        if not data_str:
            return datetime.datetime(2024, 1, 1)  # 🔥 DATA FIXA ANTIGA
            
        try:
            # 🔥 CORREÇÃO: Tentar múltiplos formatos de data
            formatos = [
                '%Y-%m-%d %H:%M:%S',      # 2025-11-27 15:45:56
                '%Y-%m-%dT%H:%M:%S',      # 2025-11-27T15:45:56 (ISO)
                '%Y-%m-%dT%H:%M:%S.%f',   # 2025-11-27T15:45:56.123456
                '%Y-%m-%d',               # 2025-11-27
                '%d/%m/%Y %H:%M:%S',      # 27/11/2025 15:45:56
                '%d/%m/%Y'                # 27/11/2025
            ]
            
            for formato in formatos:
                try:
                    return datetime.datetime.strptime(data_str, formato)
                except ValueError:
                    continue
            
            # 🔥 SE NENHUM FORMATO FUNCIONAR, USAR DATA MÍNIMA (NUNCA DATA ATUAL)
            print(f"⚠️ Não foi possível analisar a data ADMIN: {data_str}")
            return datetime.datetime(2024, 1, 1)
            
        except Exception as e:
            # 🔥 LOG ESPECÍFICO DO ERRO
            print(f"❌ Erro crítico ao analisar data ADMIN {data_str}: {e}")
            return datetime.datetime(2024, 1, 1)  # 🔥 SEMPRE DATA FIXA
    
    def exportar_extrato_pdf(self):
        """Exporta extrato em PDF"""
        if not self.ids.combo_cliente_extrato.text or not self.ids.combo_conta_extrato.text:
            self.mostrar_erro("Selecione um cliente e uma conta!")
            return
        
        username = self.ids.combo_cliente_extrato.text.split(' - ')[0]
        conta_num = self.ids.combo_conta_extrato.text.split(' - ')[0]
        sistema = App.get_running_app().sistema
        
        if conta_num not in sistema.contas:
            self.mostrar_erro("Conta não encontrada!")
            return
        
        dados_conta = sistema.contas[conta_num]
        
        self.mostrar_sucesso(
            f"PDF gerado com sucesso!\n\n"
            f"Cliente: {username}\n"
            f"Conta: {conta_num}\n"
            f"Moeda: {dados_conta['moeda']}\n"
            f"Saldo: {dados_conta['saldo']:,.2f}\n\n"
            f"(Recurso em desenvolvimento - usaríamos a mesma lógica do extrato)"
        )
    
    def adicionar_conta_cliente(self):
        """Abre a tela para adicionar nova conta"""
        self.mostrar_sucesso("➕ Funcionalidade 'Adicionar Conta' em desenvolvimento!")

    def atualizar_interface_extrato_admin(self, transacoes, saldo_atual, total_entradas, total_saidas, moeda, periodo, username):
        """Atualiza a interface do extrato administrativo"""
        try:
            print(f"🎯 ATUALIZANDO INTERFACE ADMIN: {len(transacoes)} transações")
            
            # 🔥🔥🔥 CORREÇÃO: INVERTER ORDEM - MAIS RECENTES NO TOPO
            transacoes = list(reversed(transacoes))
            
            # 🔥🔥🔥 CORREÇÃO CRÍTICA: FILTRAR TRANSAÇÕES COM DATA None
            transacoes_validas = []
            transacoes_invalidas = []
            
            for transacao in transacoes:
                if transacao is None:
                    transacoes_invalidas.append("Transação None")
                    continue
                    
                data = transacao.get('data')
                if data is None:
                    # Tentar obter data de campos alternativos
                    timestamp = transacao.get('timestamp')
                    if timestamp:
                        # Converter timestamp para string de data
                        if hasattr(timestamp, 'strftime'):
                            data_formatada = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                            transacao['data'] = data_formatada
                            transacoes_validas.append(transacao)
                        else:
                            transacao['data'] = "Data não disponível"
                            transacoes_validas.append(transacao)
                    else:
                        transacao['data'] = "Data não disponível"
                        transacoes_validas.append(transacao)
                else:
                    transacoes_validas.append(transacao)
            
            if transacoes_invalidas:
                print(f"🚫 {len(transacoes_invalidas)} transações inválidas removidas")
            
            # 🔥 SUBSTITUIR A LISTA ORIGINAL PELA LISTA CORRIGIDA
            transacoes = transacoes_validas
            print(f"✅ {len(transacoes)} transações válidas para exibição")
            
            # CONTINUA COM O DEBUG DAS PRIMEIRAS 5 TRANSAÇÕES...
            for i, transacao in enumerate(transacoes[:5]):
                print(f"   📋 Transação {i}:")
                print(f"      Data: {transacao.get('data')}")
                print(f"      Descrição: {transacao.get('descricao')}")
                print(f"      Crédito: {transacao.get('credito')}")
                print(f"      Débito: {transacao.get('debito')}")
                print(f"      Tipo: {transacao.get('tipo')}")
                print(f"      ID: {transacao.get('id')}")
            
            # 🔥🔥🔥 NOVO: VERIFICAR TRANSAÇÕES PROBLEMÁTICAS
            print("=== 🔍 PROCURANDO TRANSAÇÕES COM CAMPOS None ===")
            for i, transacao in enumerate(transacoes):
                if transacao is None:
                    print(f"❌ TRANSAÇÃO {i} É None!")
                    continue
                    
                # Verificar campos críticos que podem ser None
                data = transacao.get('data')
                descricao = transacao.get('descricao')
                credito = transacao.get('credito')
                debito = transacao.get('debito')
                tipo = transacao.get('tipo')
                
                problemas = []
                if data is None:
                    problemas.append("data")
                if descricao is None:
                    problemas.append("descricao") 
                if credito is None:
                    problemas.append("credito")
                if debito is None:
                    problemas.append("debito")
                if tipo is None:
                    problemas.append("tipo")
                
                if problemas:
                    print(f"🚨 TRANSAÇÃO {i} (ID: {transacao.get('id')}) TEM CAMPOS None: {problemas}")
                    print(f"   Dados completos: {transacao}")

            container = self.ids.lista_transacoes
            container.clear_widgets()
            
            # Atualizar resumo COM RÓTULOS E FONTE MAIOR
            resumo_text = (
                f"[b]Extrato[/b] | {username} | "
                f"[color=23a0fa][b]Saldo:[/b] {saldo_atual:,.2f} {moeda}[/color] | "
                f"[color=20cc66][b]Entradas:[/b] {total_entradas:,.2f}[/color] | "
                f"[color=ff5c5c][b]Saídas:[/b] {total_saidas:,.2f}[/color]"
            )
            
            self.ids.label_resumo_extrato.text = resumo_text
            self.ids.label_resumo_extrato.markup = True
            self.ids.label_resumo_extrato.font_size = '14sp'  # AUMENTADO para 14sp
            
            if not transacoes:
                lbl = Label(
                    text="Nenhuma transação encontrada",
                    size_hint_y=None, 
                    height=dp(50),
                    color=(0.8, 0.8, 0.8, 1),
                    font_size='14sp'
                )
                container.add_widget(lbl)
                return
            
            # Adicionar transações
            total_height = 0
            for transacao in transacoes:
                card = CardTransacao(transacao)
                container.add_widget(card)
                total_height += dp(60)
            
            # Forçar altura
            container.height = total_height
            print(f"✅ Altura do container: {total_height}")
            
            # 🔥 NOVO: Rolar para o topo após carregar as transações
            self.scroll_para_topo()
            
        except Exception as e:
            print(f"❌ ERRO: {e}")

    def atualizar_saldos_spinners_extrato(self):
        """Atualiza os saldos nos spinners da aba extrato - VERSÃO ROBUSTA"""
        sistema = App.get_running_app().sistema
        
        try:
            print("🔄 Atualizando saldos nos spinners do extrato...")
            
            # 🔥 ATUALIZAR COMBO DE CLIENTES (com saldos atualizados)
            if hasattr(self, 'ids') and 'combo_cliente_extrato' in self.ids:
                clientes_opcoes = []
                for username, dados in sistema.usuarios.items():
                    if dados['tipo'] == 'cliente':
                        # Calcular saldo total do cliente
                        saldo_total = 0.0
                        contas_info = []
                        
                        for conta_num in dados.get('contas', []):
                            if conta_num in sistema.contas:
                                conta_data = sistema.contas[conta_num]
                                saldo = conta_data['saldo']
                                moeda = conta_data['moeda']
                                saldo_total += saldo
                                contas_info.append(f"{conta_num} ({moeda}: {saldo:,.2f})")
                        
                        # Formatar texto do cliente com saldo total
                        texto_cliente = f"{username} - {dados['nome']} - Saldo Total: {saldo_total:,.2f}"
                        clientes_opcoes.append(texto_cliente)
                
                # Manter a seleção atual se possível
                cliente_selecionado_anterior = self.ids.combo_cliente_extrato.text
                
                self.ids.combo_cliente_extrato.values = clientes_opcoes
                
                # Restaurar seleção anterior ou selecionar primeiro
                if cliente_selecionado_anterior and any(cliente_selecionado_anterior in opcao for opcao in clientes_opcoes):
                    self.ids.combo_cliente_extrato.text = cliente_selecionado_anterior
                elif clientes_opcoes:
                    self.ids.combo_cliente_extrato.text = clientes_opcoes[0]
            
            # 🔥 ATUALIZAR COMBO DE CONTAS (quando cliente estiver selecionado)
            if (hasattr(self, 'ids') and 'combo_cliente_extrato' in self.ids and 
                self.ids.combo_cliente_extrato.text and 
                'combo_conta_extrato' in self.ids):
                
                username = self.ids.combo_cliente_extrato.text.split(' - ')[0]
                
                if username in sistema.usuarios:
                    contas_cliente = []
                    for conta_num in sistema.usuarios[username].get('contas', []):
                        if conta_num in sistema.contas:
                            dados_conta = sistema.contas[conta_num]
                            # Formatar com saldo ATUALIZADO
                            texto_conta = f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}"
                            contas_cliente.append(texto_conta)
                    
                    # Manter a seleção atual se possível
                    conta_selecionada_anterior = self.ids.combo_conta_extrato.text
                    
                    self.ids.combo_conta_extrato.values = contas_cliente
                    
                    # Restaurar seleção anterior ou selecionar primeira conta
                    if conta_selecionada_anterior:
                        # Extrair número da conta da seleção anterior
                        conta_num_anterior = conta_selecionada_anterior.split(' - ')[0]
                        conta_encontrada = None
                        
                        for opcao in contas_cliente:
                            if opcao.startswith(conta_num_anterior + ' - '):
                                conta_encontrada = opcao
                                break
                        
                        if conta_encontrada:
                            self.ids.combo_conta_extrato.text = conta_encontrada
                        elif contas_cliente:
                            self.ids.combo_conta_extrato.text = contas_cliente[0]
                    elif contas_cliente:
                        self.ids.combo_conta_extrato.text = contas_cliente[0]
            
            print("✅ Saldos nos spinners do extrato atualizados!")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar saldos nos spinners: {e}")


    def abrir_gerenciamento_cliente(self, instance):
        """Abre a tela de gerenciamento detalhado do cliente - VERSÃO ULTRA-ROBUSTA"""
        try:
            sistema = App.get_running_app().sistema
            
            print(f"🔍 INÍCIO: Tentando abrir gerenciamento para: {self.username}")
            print(f"📱 Telas disponíveis: {self.tela_pai.manager.screen_names}")
            
            # SOLUÇÃO DEFINITIVA: Sempre criar a tela dinamicamente
            tela_detalhe = None
            
            # Tentar obter a tela se já existir
            if 'gerenciar_cliente_detalhe' in self.tela_pai.manager.screen_names:
                print("🔄 Tela encontrada, obtendo...")
                tela_detalhe = self.tela_pai.manager.get_screen('gerenciar_cliente_detalhe')
            else:
                print("🔄 Tela NÃO encontrada, criando dinamicamente...")
                try:
                    # Tentar importar de screens
                    from screens.gerenciar_cliente_detalhe import TelaGerenciarClienteDetalhe
                    tela_detalhe = TelaGerenciarClienteDetalhe()
                    self.tela_pai.manager.add_widget(tela_detalhe)
                    print("✅ Tela criada e registrada com sucesso!")
                except ImportError as e:
                    print(f"❌ Erro de import: {e}")
                    # Tentar criar diretamente (se estiver no mesmo arquivo)
                    try:
                        tela_detalhe = TelaGerenciarClienteDetalhe()
                        self.tela_pai.manager.add_widget(tela_detalhe)
                        print("✅ Tela criada via fallback!")
                    except Exception as fallback_error:
                        print(f"❌ Erro no fallback: {fallback_error}")
                        self.tela_pai.mostrar_erro("Falha crítica ao criar tela")
                        return
            
            # Verificar se conseguimos obter a tela
            if tela_detalhe is None:
                print("❌ Falha: tela_detalhe é None")
                self.tela_pai.mostrar_erro("Falha ao criar tela de gerenciamento")
                return
            
            print(f"✅ Tela obtida com sucesso: {tela_detalhe}")
            
            # Carregar dados do cliente
            dados_cliente = sistema.usuarios[self.username]
            print(f"📊 Carregando dados para: {self.username}")
            
            # Verificar se o método existe
            if hasattr(tela_detalhe, 'carregar_dados_cliente'):
                tela_detalhe.carregar_dados_cliente(self.username, dados_cliente)
                print("✅ Dados carregados com sucesso!")
            else:
                print("❌ Método carregar_dados_cliente não encontrado!")
                self.tela_pai.mostrar_erro("Erro: método de carregamento não disponível")
                return
            
            # Navegar para a tela
            self.tela_pai.manager.current = 'gerenciar_cliente_detalhe'
            
            print(f"🎉 NAVEGAÇÃO BEM-SUCEDIDA para: {self.username}")
            print(f"📱 Telas disponíveis FINAL: {self.tela_pai.manager.screen_names}")
            
        except Exception as e:
            print(f"💥 ERRO CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            self.tela_pai.mostrar_erro(f"Erro crítico: {str(e)}")
    
    # ========== MÉTODOS AUXILIARES ==========

    def scroll_para_topo(self):
        """Rola automaticamente para o topo da lista de transações"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'scroll_extrato_admin'):
            # Agendar o scroll para depois que a interface for atualizada
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_extrato_admin, 'scroll_y', 1), 0.1)
            
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
        """Mostra popup de sucesso - VERSÃO COM ALTURA MAIOR"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='15sp',  # 🔥 Aumentado para 15sp
            text_size=(350, None),
            halign='center',
            valign='top',  # 🔥 Adicionado para alinhar ao topo
            size_hint_y=None,
            height=250  # 🔥 Altura fixa para a mensagem
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
        
        # 🔥 AUMENTAR ALTURA DO POPUP
        popup = Popup(
            title='Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 350),  # 🔥 Aumentado de 300 para 350
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_confirmacao(self, titulo, mensagem, callback_confirmar):
        """Mostra popup de confirmação - VERSÃO COM ALTURA MAIOR"""
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
            font_size='14sp',  # 🔥 Aumentado para 14sp
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center',
            valign='top',  # 🔥 Adicionado para alinhar ao topo
            size_hint_y=None,
            height=200  # 🔥 Altura fixa para a mensagem
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
        
        # 🔥 AUMENTAR ALTURA DO POPUP
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 350),  # 🔥 Aumentado de 300 para 350
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

    def obter_nome_cliente_por_conta(self, sistema, conta_numero):
        """Obtém o nome do cliente por número da conta"""
        if conta_numero in sistema.contas:
            return sistema.contas[conta_numero].get('cliente_nome', 'N/A')
        return 'N/A'

    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'

    # ========== MÉTODOS AUXILIARES ==========

    def configurar_bindings_spinners(self):
        """Configura os bindings dos spinners para atualização automática"""
        try:
            if hasattr(self, 'ids'):
                # Binding para categoria de receita
                if 'combo_categoria_receita' in self.ids:
                    self.ids.combo_categoria_receita.bind(text=lambda instance, value: self.atualizar_contas_receita())
                
                # Binding para categoria de despesa
                if 'combo_categoria_despesa' in self.ids:
                    self.ids.combo_categoria_despesa.bind(text=lambda instance, value: self.atualizar_contas_despesa())
                
                print("✅ Bindings dos spinners configurados")
        except Exception as e:
            print(f"❌ Erro ao configurar bindings: {e}")

    def _extrair_moeda_conta(self, texto_conta):
        """Extrai a moeda de uma conta bancária ou contábil - VERSÃO CORRIGIDA"""
        if not texto_conta:
            return None
        
        # Para contas bancárias: "BANK_USD_001 - 997,900.00 USD"
        if ' - ' in texto_conta:
            partes = texto_conta.split(' - ')[-1].split()
            if partes and partes[-1] in ['USD', 'EUR', 'GBP', 'BRL', 'UST']:
                return partes[-1]
        
        # Para contas contábeis: "Internet e Telefonia (USD)"
        if ' (' in texto_conta and ')' in texto_conta:
            moeda = texto_conta.split(' (')[1].replace(')', '').strip()
            if moeda in ['USD', 'EUR', 'GBP', 'BRL', 'UST']:
                return moeda
        
        # Para contas cliente: "607906288 - 44,460.00 USD"
        if ' - ' in texto_conta and len(texto_conta.split(' - ')) > 1:
            partes = texto_conta.split(' - ')[1].split()
            if partes and partes[-1] in ['USD', 'EUR', 'GBP', 'BRL', 'UST']:
                return partes[-1]
        
        print(f"⚠️ Não foi possível extrair moeda de: {texto_conta}")
        return None


    def atualizar_contas_receita(self):
        """Atualiza as contas de receita quando selecionar categoria - COM FILTRO DE MOEDA CORRIGIDO"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_categoria_receita.text:
            return
        
        categoria_selecionada = self.ids.combo_categoria_receita.text
        print(f"🔍 Categoria receita selecionada: {categoria_selecionada}")
        
        # 🔥 CORREÇÃO: OBTER MOEDA DA CONTA CLIENTE SELECIONADA
        moeda_alvo = None
        if self.ids.combo_conta_cliente_receita.text:
            moeda_alvo = self._extrair_moeda_conta(self.ids.combo_conta_cliente_receita.text)
            print(f"💰 Moeda alvo (conta cliente): {moeda_alvo}")
        
        if categoria_selecionada in sistema.contas_contabeis['receitas']:
            # 🔥 AGORA COM MOEDA: "Comissões de Câmbio (USD)", etc.
            contas_com_moeda = []
            for conta_nome, moedas in sistema.contas_contabeis['receitas'][categoria_selecionada].items():
                for moeda in moedas.keys():
                    contas_com_moeda.append(f"{conta_nome} ({moeda})")
            
            # 🔥 CORREÇÃO: APLICAR FILTRO POR MOEDA SE HOUVER MOEDA_ALVO
            if moeda_alvo:
                contas_filtradas = []
                for conta in contas_com_moeda:
                    moeda_conta = self._extrair_moeda_conta(conta)
                    if moeda_conta == moeda_alvo:
                        contas_filtradas.append(conta)
                contas_com_moeda = contas_filtradas
                print(f"✅ Filtro aplicado: mostrando apenas contas em {moeda_alvo}")
            
            print(f"✅ Contas receita atualizadas: {len(contas_com_moeda)} opções COM MOEDA (filtro: {moeda_alvo})")
            
            if 'combo_conta_receita' in self.ids:
                self.ids.combo_conta_receita.values = contas_com_moeda
                if contas_com_moeda:
                    # 🔥 CORREÇÃO: Selecionar a primeira opção apenas se não houver seleção atual
                    if not self.ids.combo_conta_receita.text:
                        self.ids.combo_conta_receita.text = contas_com_moeda[0]
                else:
                    self.ids.combo_conta_receita.text = ""
        else:
            print(f"⚠️ Categoria '{categoria_selecionada}' não encontrada nas receitas")

    def criar_nova_conta_despesa(self):
        """Abre popup para criar nova categoria/conta de despesa - VERSÃO MULTI-MOEDA MELHORADA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        from kivy.uix.togglebutton import ToggleButton
        from kivy.uix.gridlayout import GridLayout
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Título
        content.add_widget(Label(
            text='NOVA CONTA DE DESPESA - MULTI-MOEDA',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40
        ))
        
        # Tipo (Categoria ou Subconta)
        tipo_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        tipo_layout.add_widget(Label(
            text='Tipo *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        spinner_tipo = Spinner(
            text='Nova Subconta',
            values=['Nova Categoria', 'Nova Subconta'],
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        tipo_layout.add_widget(spinner_tipo)
        content.add_widget(tipo_layout)
        
        # Categoria Pai (apenas para subconta)
        categoria_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        categoria_layout.add_widget(Label(
            text='Categoria Pai *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        spinner_categoria = Spinner(
            text='Selecione a categoria',
            values=list(App.get_running_app().sistema.contas_contabeis['despesas'].keys()),
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        categoria_layout.add_widget(spinner_categoria)
        content.add_widget(categoria_layout)
        
        # Nome da Conta
        nome_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        nome_layout.add_widget(Label(
            text='Nome da Conta *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        input_nome = TextInput(
            hint_text='Digite o nome da conta...',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1)
        )
        nome_layout.add_widget(input_nome)
        content.add_widget(nome_layout)
        
        # 🔥 SELEÇÃO DE MOEDAS MELHORADA
        moedas_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=140)
        moedas_layout.add_widget(Label(
            text='Moedas * (Selecione uma ou mais)',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3
        ))
        
        grid_moedas = GridLayout(cols=4, size_hint_y=0.7, spacing=5)
        
        # Toggle buttons para moedas - SEM GRUPO para seleção múltipla
        moedas_disponiveis = ['USD', 'EUR', 'GBP', 'BRL']
        toggle_moedas = {}
        
        for moeda in moedas_disponiveis:
            btn = ToggleButton(
                text=moeda,
                # 🔥 REMOVIDO group='moedas' para permitir seleção múltipla
                state='down',  # Selecionado por padrão
                background_color=(0.23, 0.51, 0.96, 1),
                background_normal='',
                size_hint=(None, None),
                size=(80, 40)
            )
            toggle_moedas[moeda] = btn
            grid_moedas.add_widget(btn)
        
        moedas_layout.add_widget(grid_moedas)
        
        # Label para mostrar moedas selecionadas
        label_moedas_selecionadas = Label(
            text='Moedas selecionadas: USD, EUR, GBP, BRL',
            font_size='11sp',
            color=(0.7, 0.9, 0.7, 1),
            size_hint_y=0.2
        )
        moedas_layout.add_widget(label_moedas_selecionadas)
        content.add_widget(moedas_layout)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_criar = Button(
            text='Criar Conta',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_criar)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.8),  # 🔥 Aumentado para caber melhor
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def atualizar_moedas_selecionadas():
            """Atualiza o label com as moedas selecionadas"""
            moedas_selecionadas = [moeda for moeda, btn in toggle_moedas.items() if btn.state == 'down']
            if moedas_selecionadas:
                label_moedas_selecionadas.text = f'Moedas selecionadas: {", ".join(moedas_selecionadas)}'
                label_moedas_selecionadas.color = (0.7, 0.9, 0.7, 1)
            else:
                label_moedas_selecionadas.text = 'Nenhuma moeda selecionada!'
                label_moedas_selecionadas.color = (0.9, 0.7, 0.7, 1)
        
        def on_moeda_state(instance, value):
            """Callback quando o estado de uma moeda muda"""
            atualizar_moedas_selecionadas()
        
        # Configurar callbacks para os toggle buttons
        for btn in toggle_moedas.values():
            btn.bind(state=on_moeda_state)
        
        def criar_conta(instance):
            sistema = App.get_running_app().sistema
            tipo = spinner_tipo.text
            nome = input_nome.text.strip()
            categoria_pai = spinner_categoria.text
            
            # 🔥 OBTER MOEDAS SELECIONADAS
            moedas_selecionadas = [moeda for moeda, btn in toggle_moedas.items() if btn.state == 'down']
            
            if not nome:
                self.mostrar_erro("Digite o nome da conta!")
                return
            
            if not moedas_selecionadas:
                self.mostrar_erro("Selecione pelo menos uma moeda!")
                return
            
            if tipo == 'Nova Categoria':
                # Criar nova categoria em TODAS as moedas selecionadas
                for moeda in moedas_selecionadas:
                    sistema.criar_conta_despesa(nome, nome, moeda)
                self.mostrar_sucesso(f"Categoria '{nome}' criada com sucesso em {len(moedas_selecionadas)} moeda(s)!")
            else:
                # Criar nova subconta em TODAS as moedas selecionadas
                if categoria_pai == 'Selecione a categoria':
                    self.mostrar_erro("Selecione uma categoria pai!")
                    return
                for moeda in moedas_selecionadas:
                    sistema.criar_conta_despesa(categoria_pai, nome, moeda)
                self.mostrar_sucesso(f"Subconta '{nome}' criada em '{categoria_pai}' em {len(moedas_selecionadas)} moeda(s)!")
            
            popup.dismiss()
            # Recarregar combos
            self.carregar_combos_contabeis()
            # Atualizar spinners
            self.atualizar_contas_despesa()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_criar.bind(on_press=criar_conta)
        btn_cancelar.bind(on_press=cancelar)
        
        # Inicializar label de moedas
        atualizar_moedas_selecionadas()
        
        popup.open()

    def criar_nova_conta_receita(self):
        """Abre popup para criar nova categoria/conta de receita - VERSÃO MULTI-MOEDA MELHORADA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        from kivy.uix.togglebutton import ToggleButton
        from kivy.uix.gridlayout import GridLayout
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Título
        content.add_widget(Label(
            text='NOVA CONTA DE RECEITA - MULTI-MOEDA',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40
        ))
        
        # Tipo (Categoria ou Subconta)
        tipo_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        tipo_layout.add_widget(Label(
            text='Tipo *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        spinner_tipo = Spinner(
            text='Nova Subconta',
            values=['Nova Categoria', 'Nova Subconta'],
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        tipo_layout.add_widget(spinner_tipo)
        content.add_widget(tipo_layout)
        
        # Categoria Pai (apenas para subconta)
        categoria_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        categoria_layout.add_widget(Label(
            text='Categoria Pai *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        spinner_categoria = Spinner(
            text='Selecione a categoria',
            values=list(App.get_running_app().sistema.contas_contabeis['receitas'].keys()),
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        categoria_layout.add_widget(spinner_categoria)
        content.add_widget(categoria_layout)
        
        # Nome da Conta
        nome_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        nome_layout.add_widget(Label(
            text='Nome da Conta *',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        ))
        
        input_nome = TextInput(
            hint_text='Digite o nome da conta...',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1)
        )
        nome_layout.add_widget(input_nome)
        content.add_widget(nome_layout)
        
        # 🔥 SELEÇÃO DE MOEDAS MELHORADA
        moedas_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=140)
        moedas_layout.add_widget(Label(
            text='Moedas * (Selecione uma ou mais)',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3
        ))
        
        grid_moedas = GridLayout(cols=4, size_hint_y=0.7, spacing=5)
        
        # Toggle buttons para moedas - SEM GRUPO para seleção múltipla
        moedas_disponiveis = ['USD', 'EUR', 'GBP', 'BRL']
        toggle_moedas = {}
        
        for moeda in moedas_disponiveis:
            btn = ToggleButton(
                text=moeda,
                # 🔥 REMOVIDO group='moedas' para permitir seleção múltipla
                state='down',  # Selecionado por padrão
                background_color=(0.23, 0.51, 0.96, 1),
                background_normal='',
                size_hint=(None, None),
                size=(80, 40)
            )
            toggle_moedas[moeda] = btn
            grid_moedas.add_widget(btn)
        
        moedas_layout.add_widget(grid_moedas)
        
        # Label para mostrar moedas selecionadas
        label_moedas_selecionadas = Label(
            text='Moedas selecionadas: USD, EUR, GBP, BRL',
            font_size='11sp',
            color=(0.7, 0.9, 0.7, 1),
            size_hint_y=0.2
        )
        moedas_layout.add_widget(label_moedas_selecionadas)
        content.add_widget(moedas_layout)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_criar = Button(
            text='Criar Conta',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_criar)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.8),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def atualizar_moedas_selecionadas():
            """Atualiza o label com as moedas selecionadas"""
            moedas_selecionadas = [moeda for moeda, btn in toggle_moedas.items() if btn.state == 'down']
            if moedas_selecionadas:
                label_moedas_selecionadas.text = f'Moedas selecionadas: {", ".join(moedas_selecionadas)}'
                label_moedas_selecionadas.color = (0.7, 0.9, 0.7, 1)
            else:
                label_moedas_selecionadas.text = 'Nenhuma moeda selecionada!'
                label_moedas_selecionadas.color = (0.9, 0.7, 0.7, 1)
        
        def on_moeda_state(instance, value):
            """Callback quando o estado de uma moeda muda"""
            atualizar_moedas_selecionadas()
        
        # Configurar callbacks para os toggle buttons
        for btn in toggle_moedas.values():
            btn.bind(state=on_moeda_state)
        
        def criar_conta(instance):
            sistema = App.get_running_app().sistema
            tipo = spinner_tipo.text
            nome = input_nome.text.strip()
            categoria_pai = spinner_categoria.text
            
            # 🔥 OBTER MOEDAS SELECIONADAS
            moedas_selecionadas = [moeda for moeda, btn in toggle_moedas.items() if btn.state == 'down']
            
            if not nome:
                self.mostrar_erro("Digite o nome da conta!")
                return
            
            if not moedas_selecionadas:
                self.mostrar_erro("Selecione pelo menos uma moeda!")
                return
            
            if tipo == 'Nova Categoria':
                # Criar nova categoria em TODAS as moedas selecionadas
                for moeda in moedas_selecionadas:
                    sistema.criar_conta_receita(nome, nome, moeda)
                self.mostrar_sucesso(f"Categoria '{nome}' criada com sucesso em {len(moedas_selecionadas)} moeda(s)!")
            else:
                # Criar nova subconta em TODAS as moedas selecionadas
                if categoria_pai == 'Selecione a categoria':
                    self.mostrar_erro("Selecione uma categoria pai!")
                    return
                for moeda in moedas_selecionadas:
                    sistema.criar_conta_receita(categoria_pai, nome, moeda)
                self.mostrar_sucesso(f"Subconta '{nome}' criada em '{categoria_pai}' em {len(moedas_selecionadas)} moeda(s)!")
            
            popup.dismiss()
            # Recarregar combos
            self.carregar_combos_contabeis()
            # Atualizar spinners
            self.atualizar_contas_receita()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_criar.bind(on_press=criar_conta)
        btn_cancelar.bind(on_press=cancelar)
        
        # Inicializar label de moedas
        atualizar_moedas_selecionadas()
        
        popup.open()

    def atualizar_contas_cliente_receita(self):
        """Atualiza as contas do cliente quando selecionar cliente - SEM FILTRO (todas moedas)"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_cliente_receita.text:
            return
        
        username = self.ids.combo_cliente_receita.text.split(' - ')[0]
        print(f"🔍 Atualizando contas cliente: {username} (TODAS as moedas)")
        
        # 🔥 REMOVA a sincronização forçada se não for crítica
        # sistema.sincronizar_todos_saldos_com_supabase()
        
        # 🔥 REMOVA o filtro por moeda da conta receita
        # moeda_alvo = None  # ❌ REMOVER
        
        # Buscar TODAS as contas do cliente (sem filtro)
        contas_cliente = []
        for conta_id, conta_info in sistema.contas.items():
            if (isinstance(conta_info, dict) and 
                conta_info.get('cliente') == username):
                
                saldo = conta_info.get('saldo', 0)
                moeda = conta_info.get('moeda', 'USD')
                
                # 🔥 Mostrar TODAS as contas, independente do saldo
                # (ou mantenha > 0 se preferir)
                if saldo >= 0:  # Mude para >= 0 para mostrar todas, mesmo com saldo zero
                    contas_cliente.append(f"{conta_id} - {saldo:,.2f} {moeda}")
        
        print(f"✅ {len(contas_cliente)} contas cliente carregadas (TODAS as moedas)")
        
        if 'combo_conta_cliente_receita' in self.ids:
            self.ids.combo_conta_cliente_receita.values = contas_cliente
            
            # 🔥 LÓGICA MELHORADA PARA MANTER SELEÇÃO
            if contas_cliente:
                # Se já tem uma conta selecionada, tentar mantê-la
                if self.ids.combo_conta_cliente_receita.text:
                    conta_selecionada_id = self.ids.combo_conta_cliente_receita.text.split(' - ')[0]
                    for conta in contas_cliente:
                        if conta.startswith(conta_selecionada_id):
                            self.ids.combo_conta_cliente_receita.text = conta
                            print(f"✅ Mantida seleção: {conta}")
                            return
                
                # Se não tem seleção ou não encontrou a conta anterior
                self.ids.combo_conta_cliente_receita.text = contas_cliente[0]
            else:
                self.ids.combo_conta_cliente_receita.text = ""

    def carregar_combos_contabeis(self):
        """Carrega todos os combos das abas contábeis - VERSÃO ATUALIZADA (DADOS REAIS)"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            print("⚠️ IDs não disponíveis ainda")
            return
        
        # 🔥 DESPESAS: Carregar categorias do SUPABASE
        try:
            # Buscar categorias ÚNICAS de despesa do Supabase
            response = sistema.supabase.client.table('contas_contabeis')\
                .select('categoria')\
                .eq('tipo', 'despesa')\
                .execute()
            
            categorias_despesa = list(set([item['categoria'] for item in response.data]))
            
            if 'combo_categoria_despesa' in self.ids:
                self.ids.combo_categoria_despesa.values = categorias_despesa
                if categorias_despesa and not self.ids.combo_categoria_despesa.text:
                    self.ids.combo_categoria_despesa.text = categorias_despesa[0]
                print(f"✅ {len(categorias_despesa)} categorias de despesa carregadas do Supabase")
                
                # 🔥 AGORA O BINDING VAI CHAMAR atualizar_contas_despesa() AUTOMATICAMENTE
                # Não precisamos carregar contas aqui, o binding cuida disso
                
        except Exception as e:
            print(f"❌ Erro ao carregar categorias despesa: {e}")
        
        # 🔥 RECEITAS: Carregar categorias do SUPABASE
        try:
            # Buscar categorias ÚNICAS de receita do Supabase
            response = sistema.supabase.client.table('contas_contabeis')\
                .select('categoria')\
                .eq('tipo', 'receita')\
                .execute()
            
            categorias_receita = list(set([item['categoria'] for item in response.data]))
            
            if 'combo_categoria_receita' in self.ids:
                self.ids.combo_categoria_receita.values = categorias_receita
                if categorias_receita and not self.ids.combo_categoria_receita.text:
                    self.ids.combo_categoria_receita.text = categorias_receita[0]
                print(f"✅ {len(categorias_receita)} categorias de receita carregadas do Supabase")
                
        except Exception as e:
            print(f"❌ Erro ao carregar categorias receita: {e}")
        
        # 🔥 CONTAS BANCÁRIAS: Carregar do Supabase (sem filtro inicial)
        self.atualizar_contas_bancarias_despesa()

    def carregar_combos_receita(self):
        """Carrega especificamente os combos da aba receitas - VERSÃO MULTI-MOEDA CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        print("🔍 Carregando combos receita...")
        
        # 🔥 CARREGAR CATEGORIAS DE RECEITA
        categorias_receita = list(sistema.contas_contabeis['receitas'].keys())
        print(f"📋 Categorias de receita disponíveis: {categorias_receita}")
        
        if hasattr(self, 'ids') and 'combo_categoria_receita' in self.ids:
            self.ids.combo_categoria_receita.values = categorias_receita
            if categorias_receita and not self.ids.combo_categoria_receita.text:
                self.ids.combo_categoria_receita.text = categorias_receita[0]
                print(f"✅ Categoria receita selecionada: {categorias_receita[0]}")
        
        # 🔥 CARREGAR CONTAS DE RECEITA COM MOEDA (VERSÃO MULTI-MOEDA)
        if hasattr(self, 'ids') and 'combo_conta_receita' in self.ids:
            categoria_selecionada = self.ids.combo_categoria_receita.text if self.ids.combo_categoria_receita.text else ""
            if categoria_selecionada and categoria_selecionada in sistema.contas_contabeis['receitas']:
                # 🔥 AGORA COM MOEDA: "Comissões de Câmbio (USD)", "Comissões de Câmbio (EUR)", etc.
                contas_com_moeda = []
                for conta_nome, moedas in sistema.contas_contabeis['receitas'][categoria_selecionada].items():
                    for moeda in moedas.keys():
                        contas_com_moeda.append(f"{conta_nome} ({moeda})")
                
                self.ids.combo_conta_receita.values = contas_com_moeda
                if contas_com_moeda and not self.ids.combo_conta_receita.text:
                    self.ids.combo_conta_receita.text = contas_com_moeda[0]
                print(f"✅ Contas receita carregadas: {len(contas_com_moeda)} opções COM MOEDA")
            else:
                print(f"⚠️ Categoria '{categoria_selecionada}' não encontrada ou vazia")

    def lancar_despesa(self):
        """Executa o lançamento de despesa - VERSÃO MULTI-MOEDA"""
        sistema = App.get_running_app().sistema
        
        print("💰 Executando lançamento de despesa...")
        
        # 🔥 DEBUG: Verificar spinner
        self.debug_spinner_despesa()
        
        try:
            # Validar campos
            if not all([
                self.ids.combo_conta_bancaria_despesa.text,
                self.ids.combo_categoria_despesa.text,
                self.ids.combo_conta_despesa.text,
                self.ids.entry_valor_despesa.text,
                self.ids.entry_descricao_despesa.text
            ]):
                self.mostrar_erro("Preencha todos os campos!")
                return
            
            # Obter dados
            conta_bancaria = self.ids.combo_conta_bancaria_despesa.text.split(' - ')[0]
            categoria_despesa = self.ids.combo_categoria_despesa.text
            
            # 🔥 CORREÇÃO: Se não tem moeda no nome, usar moeda da conta bancária
            conta_despesa_completa = self.ids.combo_conta_despesa.text
            print(f"🔍 Conta despesa completa: {conta_despesa_completa}")
            
            if ' (' in conta_despesa_completa and ')' in conta_despesa_completa:
                # Formato com moeda: "Software e Licenças (USD)"
                conta_despesa = conta_despesa_completa.split(' (')[0].strip()
                moeda_despesa = conta_despesa_completa.split(' (')[1].replace(')', '').strip()
                print(f"✅ Extraído: conta='{conta_despesa}', moeda='{moeda_despesa}'")
            else:
                # 🔥 CORREÇÃO: Usar moeda da conta bancária selecionada
                conta_despesa = conta_despesa_completa
                # Obter moeda da conta bancária
                if self.ids.combo_conta_bancaria_despesa.text:
                    moeda_despesa = self._extrair_moeda_conta(self.ids.combo_conta_bancaria_despesa.text)
                    print(f"✅ Usando moeda da conta bancária: '{conta_despesa}' com moeda '{moeda_despesa}'")
                else:
                    self.mostrar_erro("Selecione uma conta bancária primeiro!")
                    return
            
            valor_str = self.ids.entry_valor_despesa.text.strip()
            descricao = self.ids.entry_descricao_despesa.text.strip()
            
            # Converter valor
            valor = self._parse_valor_br(valor_str)
            
            if valor <= 0:
                self.mostrar_erro("Valor deve ser positivo!")
                return
            
            print(f"🔍 DADOS DESPESA:")
            print(f"  Conta Bancária: {conta_bancaria}")
            print(f"  Categoria: {categoria_despesa}")
            print(f"  Conta Despesa: {conta_despesa}")
            print(f"  Moeda: {moeda_despesa}")
            print(f"  Valor: {valor}")
            print(f"  Descrição: {descricao}")
            
            # 🔥 CORREÇÃO: Chamar método ATUALIZADO com parâmetro de moeda
            sucesso, mensagem = sistema.lancar_despesa(
                conta_bancaria=conta_bancaria,
                valor=valor,
                conta_despesa=conta_despesa,
                categoria_despesa=categoria_despesa,
                descricao=descricao,
                moeda_despesa=moeda_despesa  # 🔥 NOVO PARÂMETRO
            )
            
            if sucesso:
                self.mostrar_sucesso(mensagem)
                # Limpar campos
                self.ids.entry_valor_despesa.text = ""
                self.ids.entry_descricao_despesa.text = ""
                
                # 🔥 🔥 🔥 ATUALIZAÇÕES IMPORTANTES AQUI:
                # 1. Forçar sincronização dos saldos
                sistema.sincronizar_todos_saldos_com_supabase()
                
                # 2. Recarregar contas bancárias ATUALIZADAS
                sistema.carregar_contas_bancarias()
                
                # 3. Atualizar o spinner da conta bancária COM SALDO ATUAL
                if self.ids.combo_conta_bancaria_despesa.text:
                    conta_bancaria = self.ids.combo_conta_bancaria_despesa.text.split(' - ')[0]
                    
                    # Buscar saldo ATUALIZADO
                    if conta_bancaria in sistema.contas_bancarias_empresa:
                        conta_info = sistema.contas_bancarias_empresa[conta_bancaria]
                        saldo_atual = conta_info['saldo']
                        moeda = conta_info['moeda']
                        banco = conta_info.get('banco', 'Banco Principal')
                        
                        # 🔥 Atualizar texto do spinner com novo saldo
                        novo_texto = f"{conta_bancaria} - {banco} - {moeda} - Saldo: {saldo_atual:,.2f}"
                        
                        # Salvar seleção atual
                        selecao_anterior = self.ids.combo_conta_bancaria_despesa.text
                        
                        # Atualizar valores do spinner
                        self.atualizar_contas_bancarias_despesa()  # 🔥 CORREÇÃO: Usar o novo método
                        
                        # Restaurar seleção (com saldo atualizado)
                        self.ids.combo_conta_bancaria_despesa.text = novo_texto
                        print(f"✅ Saldo atualizado: {novo_texto}")
                
                # 4. Atualizar filtro de moeda nas contas de despesa
                self.atualizar_contas_despesa()
                
                # 5. Atualizar todos os combos
                self.atualizar_combos_apos_operacao()
                
                print("✅ Despesa lançada e spinners atualizados!")
            else:
                self.mostrar_erro(mensagem)
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em lancar_despesa: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao lançar despesa: {str(e)}")

    def debug_spinner_despesa(self):
        """Debug do spinner de despesa para ver o formato das opções"""
        if hasattr(self, 'ids') and 'combo_conta_despesa' in self.ids:
            print("=== 🔍 DEBUG SPINNER DESPESA ===")
            print(f"Texto atual: {self.ids.combo_conta_despesa.text}")
            print(f"Opções disponíveis: {self.ids.combo_conta_despesa.values}")
            print("=== 🎯 FIM DEBUG ===")

    def limpar_filtro_despesa(self):
        """Limpa filtro de moeda e recarrega todas as opções"""
        print("🔄 Limpando filtro de moeda...")
        
        if not hasattr(self, 'ids'):
            return
        
        # 1. Recarregar TODAS as contas bancárias
        self.atualizar_contas_bancarias_despesa()
        
        # 2. Recarregar TODAS as contas contábeis (sem filtro)
        if self.ids.combo_categoria_despesa.text:
            # Forçar recarga sem filtro
            sistema = App.get_running_app().sistema
            categoria = self.ids.combo_categoria_despesa.text
            
            try:
                response = sistema.supabase.client.table('contas_contabeis')\
                    .select('nome, moeda, saldo')\
                    .eq('categoria', categoria)\
                    .eq('tipo', 'despesa')\
                    .execute()
                
                contas_formatadas = []
                for conta in response.data:
                    texto = f"{conta['nome']} ({conta['moeda']})"
                    contas_formatadas.append(texto)
                
                if 'combo_conta_despesa' in self.ids:
                    self.ids.combo_conta_despesa.values = contas_formatadas
                    if contas_formatadas:
                        self.ids.combo_conta_despesa.text = contas_formatadas[0]
                
                print(f"✅ Filtro limpo: {len(contas_formatadas)} contas contábeis (TODAS as moedas)")
                
            except Exception as e:
                print(f"❌ Erro ao limpar filtro: {e}")

    def atualizar_saldo_conta_bancaria_spinner(self, conta_numero):
        """Atualiza o saldo de uma conta bancária específica no spinner"""
        sistema = App.get_running_app().sistema
        
        if conta_numero not in sistema.contas_bancarias_empresa:
            return
        
        conta_info = sistema.contas_bancarias_empresa[conta_numero]
        
        # Buscar saldo ATUAL do Supabase
        saldo_atual = sistema.supabase.obter_saldo_conta_bancaria_empresa(conta_numero)
        if saldo_atual is None:
            saldo_atual = conta_info['saldo']
        
        # Atualizar cache local
        sistema.contas_bancarias_empresa[conta_numero]['saldo'] = saldo_atual
        
        # Criar novo texto para o spinner
        novo_texto = f"{conta_numero} - {conta_info.get('banco', 'Banco')} - {conta_info['moeda']} - Saldo: {saldo_atual:,.2f}"
        
        # Atualizar o spinner se esta conta estiver selecionada
        if (hasattr(self, 'ids') and 'combo_conta_bancaria_despesa' in self.ids and
            self.ids.combo_conta_bancaria_despesa.text.startswith(conta_numero)):
            
            self.ids.combo_conta_bancaria_despesa.text = novo_texto
            print(f"✅ Spinner atualizado: {novo_texto}")
        
        return saldo_atual



    def obter_moeda_conta_bancaria_real(self, numero_conta):
        """Obtém a moeda REAL de uma conta bancária direto do Supabase"""
        sistema = App.get_running_app().sistema
        
        try:
            response = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('moeda')\
                .eq('numero', numero_conta)\
                .execute()
            
            if response.data and len(response.data) > 0:
                moeda = response.data[0]['moeda']
                print(f"✅ Moeda REAL da conta {numero_conta}: {moeda}")
                return moeda
            else:
                print(f"⚠️ Conta bancária {numero_conta} não encontrada")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar moeda da conta {numero_conta}: {e}")
            return None

    def carregar_contas_bancarias_com_filtro(self, moeda_filtro=None):
        """Carrega contas bancárias filtrando por moeda se especificado"""
        sistema = App.get_running_app().sistema
        
        try:
            # Construir query base
            query = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('numero, banco, moeda, saldo')\
                .gt('saldo', 0)  # Apenas contas com saldo > 0
            
            # Aplicar filtro de moeda se existir
            if moeda_filtro:
                query = query.eq('moeda', moeda_filtro)
            
            response = query.execute()
            
            contas_formatadas = []
            for conta in response.data:
                texto = f"{conta['numero']} - {conta['banco']} - {conta['moeda']} - Saldo: {float(conta['saldo']):,.2f}"
                contas_formatadas.append({
                    'texto': texto,
                    'numero': conta['numero'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo'])
                })
            
            print(f"✅ {len(contas_formatadas)} contas bancárias carregadas (filtro: {moeda_filtro})")
            return contas_formatadas
            
        except Exception as e:
            print(f"❌ Erro ao carregar contas bancárias: {e}")
            return []

    def carregar_contas_contabeis_com_filtro(self, categoria, moeda_filtro=None, tipo='despesa'):
        """Carrega contas contábeis filtrando por moeda se especificado"""
        sistema = App.get_running_app().sistema
        
        try:
            # Construir query base
            query = sistema.supabase.client.table('contas_contabeis')\
                .select('nome, moeda, saldo')\
                .eq('categoria', categoria)\
                .eq('tipo', tipo)
            
            # Aplicar filtro de moeda se existir
            if moeda_filtro:
                query = query.eq('moeda', moeda_filtro)
            
            response = query.execute()
            
            contas_formatadas = []
            for conta in response.data:
                texto = f"{conta['nome']} ({conta['moeda']})"
                contas_formatadas.append({
                    'texto': texto,
                    'nome': conta['nome'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo'])
                })
            
            print(f"✅ {len(contas_formatadas)} contas contábeis carregadas (categoria: {categoria}, filtro: {moeda_filtro})")
            return contas_formatadas
            
        except Exception as e:
            print(f"❌ Erro ao carregar contas contábeis: {e}")
            return []

    def atualizar_contas_despesa(self):
        """Atualiza as contas de despesa - VERSÃO CORRIGIDA COM DADOS REAIS"""
        if not hasattr(self, 'ids') or not self.ids.combo_categoria_despesa.text:
            return
        
        sistema = App.get_running_app().sistema
        categoria = self.ids.combo_categoria_despesa.text
        
        print(f"🔍 Atualizando contas despesa para categoria: {categoria}")
        
        # 🔥 1. Obter moeda da conta bancária selecionada (se houver)
        moeda_filtro = None
        if self.ids.combo_conta_bancaria_despesa.text and ' - ' in self.ids.combo_conta_bancaria_despesa.text:
            numero_conta = self.ids.combo_conta_bancaria_despesa.text.split(' - ')[0]
            moeda_filtro = self.obter_moeda_conta_bancaria_real(numero_conta)
        
        # 🔥 2. Carregar contas contábeis COM FILTRO
        contas = self.carregar_contas_contabeis_com_filtro(categoria, moeda_filtro, 'despesa')
        
        # 🔥 3. Atualizar spinner
        if contas and 'combo_conta_despesa' in self.ids:
            textos = [conta['texto'] for conta in contas]
            self.ids.combo_conta_despesa.values = textos
            
            # Manter seleção atual ou selecionar primeira
            if textos:
                if not self.ids.combo_conta_despesa.text or self.ids.combo_conta_despesa.text not in textos:
                    self.ids.combo_conta_despesa.text = textos[0]

    def atualizar_contas_bancarias_despesa(self):
        """Atualiza as contas bancárias para despesa - SEM FILTRO (sempre todas as moedas)"""
        if not hasattr(self, 'ids'):
            return
        
        print("🔍 Atualizando contas bancárias (TODAS as moedas)")
        
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 BUSCAR TODAS AS CONTAS BANCÁRIAS (SEM FILTRO DE MOEDA)
            response = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('numero, banco, moeda, saldo')\
                .gt('saldo', 0)\
                .order('moeda')  # Ordenar por moeda para ficar organizado
            
            contas_formatadas = []
            for conta in response.data:
                texto = f"{conta['numero']} - {conta['banco']} - {conta['moeda']} - Saldo: {float(conta['saldo']):,.2f}"
                contas_formatadas.append({
                    'texto': texto,
                    'numero': conta['numero'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo'])
                })
            
            print(f"✅ {len(contas_formatadas)} contas bancárias carregadas (TODAS as moedas)")
            
            # Atualizar spinner
            if contas_formatadas and 'combo_conta_bancaria_despesa' in self.ids:
                textos = [conta['texto'] for conta in contas_formatadas]
                self.ids.combo_conta_bancaria_despesa.values = textos
                
                # Manter seleção atual se possível
                if self.ids.combo_conta_bancaria_despesa.text:
                    selecao_atual = self.ids.combo_conta_bancaria_despesa.text
                    conta_atual_numero = selecao_atual.split(' - ')[0] if ' - ' in selecao_atual else ""
                    
                    # Verificar se a conta atual ainda existe
                    for texto in textos:
                        if texto.startswith(conta_atual_numero):
                            self.ids.combo_conta_bancaria_despesa.text = texto
                            break
                    else:
                        # Se não encontrou, manter a primeira
                        if textos:
                            self.ids.combo_conta_bancaria_despesa.text = textos[0]
                elif textos:
                    self.ids.combo_conta_bancaria_despesa.text = textos[0]
                    
        except Exception as e:
            print(f"❌ Erro ao carregar contas bancárias: {e}")






    def lancar_receita_ui(self):
        """Método simplificado para ser chamado do KV - VERSÃO MULTI-MOEDA"""
        sistema = App.get_running_app().sistema
        
        print("💰💰💰 LANÇAR RECEITA UI CHAMADO!")
        
        # Validar campos
        if not all([
            self.ids.combo_cliente_receita.text,
            self.ids.combo_conta_cliente_receita.text,
            self.ids.combo_categoria_receita.text,
            self.ids.combo_conta_receita.text,
            self.ids.entry_valor_receita.text,
            self.ids.entry_descricao_receita.text
        ]):
            self.mostrar_erro("Preencha todos os campos!")
            return
        
        try:
            # Obter dados
            username = self.ids.combo_cliente_receita.text.split(' - ')[0]
            conta_cliente_completa = self.ids.combo_conta_cliente_receita.text
            conta_cliente = conta_cliente_completa.split(' - ')[0]  # Número da conta
            
            categoria_receita = self.ids.combo_categoria_receita.text
            
            # 🔥 CORREÇÃO: Extrair nome da conta E moeda
            conta_receita_completa = self.ids.combo_conta_receita.text
            if ' (' in conta_receita_completa and ')' in conta_receita_completa:
                conta_receita = conta_receita_completa.split(' (')[0]  # "Comissões de Câmbio"
                moeda_receita = conta_receita_completa.split(' (')[1].replace(')', '')  # "USD"
            else:
                self.mostrar_erro("Formato de conta inválido! Selecione uma conta com moeda.")
                return
            
            valor_str = self.ids.entry_valor_receita.text.strip()
            descricao = self.ids.entry_descricao_receita.text.strip()
            
            # Converter valor
            valor = self._parse_valor_br(valor_str)
            
            if valor <= 0:
                self.mostrar_erro("Valor deve ser positivo!")
                return
            
            print(f"🔍 DADOS RECEITA:")
            print(f"  Cliente: {username}")
            print(f"  Conta Cliente: {conta_cliente}")
            print(f"  Categoria: {categoria_receita}")
            print(f"  Conta Receita: {conta_receita}")
            print(f"  Moeda: {moeda_receita}")
            print(f"  Valor: {valor}")
            print(f"  Descrição: {descricao}")
            
            # 🔥 CORREÇÃO: Chamar método ATUALIZADO com parâmetro de moeda
            sucesso, mensagem = sistema.lancar_receita(
                conta_cliente=conta_cliente,
                valor=valor,
                conta_receita=conta_receita,
                categoria_receita=categoria_receita,
                descricao=descricao,
                moeda_receita=moeda_receita  # 🔥 NOVO PARÂMETRO
            )
            
            if sucesso:
                self.mostrar_sucesso(mensagem)
                # Limpar campos
                self.ids.entry_valor_receita.text = ""
                self.ids.entry_descricao_receita.text = ""
                
                # 🔥 ADICIONAR ESTAS LINHAS:
                # Atualizar combo para mostrar novo saldo EM TEMPO REAL
                self.atualizar_combos_apos_operacao()
                
                # 🔥 FORÇAR SINCRONIZAÇÃO DO CACHE LOCAL
                sistema.sincronizar_todos_saldos_com_supabase()
                
                # 🔥 RECARREGAR AS CONTAS DO CLIENTE
                if self.ids.combo_cliente_receita.text:
                    username = self.ids.combo_cliente_receita.text.split(' - ')[0]
                    self.atualizar_contas_cliente_receita()
            else:
                self.mostrar_erro(mensagem)
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em lancar_receita_ui: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao lançar receita: {str(e)}")

    def atualizar_combos_apos_operacao(self):
        """Atualiza todos os combos/spinners após uma operação de lançamento"""
        sistema = App.get_running_app().sistema
        
        print("🔄 Atualizando combos após operação...")
        
        # 🔥 ATUALIZAR OS DADOS DO SUPABASE EM TEMPO REAL
        sistema.carregar_contas_background()  # Forçar recarga das contas
        
        # 🔥 ABA RECEITA
        if hasattr(self, 'ids'):
            # 1. Atualizar conta do cliente selecionado
            if self.ids.combo_cliente_receita.text:
                username = self.ids.combo_cliente_receita.text.split(' - ')[0]
                
                # Buscar contas atualizadas do Supabase
                contas_atualizadas = []
                for conta_id, conta_info in sistema.contas.items():
                    if (conta_info.get('cliente') == username and 
                        conta_info.get('saldo', 0) > 0):
                        
                        # Buscar saldo REAL do Supabase
                        saldo_real = sistema.supabase.obter_saldo_conta(conta_id)
                        if saldo_real is None:
                            saldo_real = conta_info.get('saldo', 0)
                        
                        contas_atualizadas.append(
                            f"{conta_id} - {saldo_real:,.2f} {conta_info.get('moeda', 'USD')}"
                        )
                
                # Atualizar o spinner
                self.ids.combo_conta_cliente_receita.values = contas_atualizadas
                
                # Manter a seleção atual ou selecionar a primeira
                if contas_atualizadas:
                    if self.ids.combo_conta_cliente_receita.text:
                        # Tentar manter a mesma conta selecionada
                        conta_atual = self.ids.combo_conta_cliente_receita.text.split(' - ')[0]
                        conta_encontrada = False
                        
                        for conta in contas_atualizadas:
                            if conta.startswith(conta_atual):
                                self.ids.combo_conta_cliente_receita.text = conta
                                conta_encontrada = True
                                break
                        
                        if not conta_encontrada and contas_atualizadas:
                            self.ids.combo_conta_cliente_receita.text = contas_atualizadas[0]
                    else:
                        self.ids.combo_conta_cliente_receita.text = contas_atualizadas[0]
                else:
                    self.ids.combo_conta_cliente_receita.text = ""
            
            print("✅ Combos atualizados após operação!")

    def atualizar_campos_transferencia(self):
        """Atualiza os campos dinâmicos baseado no tipo de transferência selecionado - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'ids'):
            return
            
        tipo = self.ids.combo_tipo_transferencia.text if 'combo_tipo_transferencia' in self.ids else ''
        
        print(f"🎯 Tipo de transferência selecionado: {tipo}")
        
        if tipo == 'Transferência Internacional':
            # Para internacional, usar estrutura antiga ou criar nova
            self.criar_campos_transferencia_internacional()
        elif tipo == 'Transferência Interna':
            self.criar_campos_transferencia_interna()
            

    def criar_campos_transferencia_internacional(self):
        """Cria campos para transferência internacional - VERSÃO CORRIGIDA"""
        # 🔥 CORREÇÃO: Usar os containers das colunas que EXISTEM no KV
        container_origem = self.ids.container_origem_coluna
        container_destino = self.ids.container_destino_coluna
        
        container_origem.clear_widgets()
        container_destino.clear_widgets()
        
        # Botão para abrir modal de transferência internacional
        btn_abrir_modal = Button(
            text='ABRIR TRANSFERÊNCIA INTERNACIONAL',
            font_size='14sp',
            bold=True,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50
        )
        btn_abrir_modal.bind(on_press=self.abrir_modal_transferencia_internacional)
        
        # Label informativo
        lbl_info = Label(
            text='Clique no botão acima para criar uma transferência internacional em nome de um cliente',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=40
        )
        
        # Adicionar à coluna da esquerda
        container_origem.add_widget(btn_abrir_modal)
        container_origem.add_widget(lbl_info)
        
        # Deixar coluna da direita vazia
        container_destino.add_widget(Label(text='', size_hint_y=1))
        
        # Ajustar altura
        container_origem.height = 100
        container_destino.height = 100

    def abrir_modal_transferencia_internacional(self, instance):
        """Abre o modal para transferência internacional em nome do cliente"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        
        # Criar conteúdo do modal
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        content.size_hint_y = None
        content.height = 600
        
        # Título
        lbl_titulo = Label(
            text='TRANSFERÊNCIA INTERNACIONAL - EM NOME DO CLIENTE',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40,
            text_size=(400, None),
            halign='center'
        )
        
        # Seletor de cliente
        lbl_selecionar_cliente = Label(
            text='SELECIONAR CLIENTE *',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=30,
            text_size=(400, None),
            halign='left'
        )
        
        # Spinner para selecionar cliente
        self.spinner_cliente_modal = Spinner(
            text='Selecione um cliente',
            font_size='12sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        
        # Carregar clientes no spinner
        self.carregar_clientes_modal()
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_continuar = Button(
            text='CONTINUAR',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_continuar)
        
        # Adicionar tudo ao conteúdo
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_selecionar_cliente)
        content.add_widget(self.spinner_cliente_modal)
        content.add_widget(botoes_layout)
        
        # Criar popup
        self.popup_transferencia_internacional = Popup(
            title='Transferência Internacional',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(0.9, 0.8),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def continuar(instance):
            """Abre a tela completa de transferência para o cliente selecionado"""
            if self.spinner_cliente_modal.text == 'Selecione um cliente':
                self.mostrar_erro("Selecione um cliente!")
                return
            
            # Fechar este modal
            self.popup_transferencia_internacional.dismiss()
            
            # Abrir modal completo de transferência
            self.abrir_modal_transferencia_completa()
        
        def cancelar(instance):
            self.popup_transferencia_internacional.dismiss()
        
        btn_continuar.bind(on_press=continuar)
        btn_cancelar.bind(on_press=cancelar)
        
        self.popup_transferencia_internacional.open()

    def abrir_modal_transferencia_completa(self):
        """Abre o modal completo de transferência internacional replicando a interface do cliente"""
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.checkbox import CheckBox
        
        # Obter cliente selecionado
        cliente_texto = self.spinner_cliente_modal.text
        username_cliente = cliente_texto.split(' - ')[0]
        nome_cliente = cliente_texto.split(' - ')[1]
        
        sistema = App.get_running_app().sistema
        
        # Criar conteúdo principal com ScrollView
        scroll_content = ScrollView(do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Título com informações do cliente
        lbl_titulo = Label(
            text=f'TRANSFERÊNCIA INTERNACIONAL - {nome_cliente.upper()}',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40,
            text_size=(None, None),
            halign='center'
        )
        main_layout.add_widget(lbl_titulo)
        
        # 🔥 CONTA DE ORIGEM
        box_conta_origem = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        
        lbl_conta_origem = Label(
            text='Conta de Origem *',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        box_conta_origem.add_widget(lbl_conta_origem)
        
        self.spinner_conta_cliente = Spinner(
            text='Selecione uma conta',
            font_size='12sp',
            size_hint_y=0.4,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        self.carregar_contas_cliente_modal(username_cliente)
        self.spinner_conta_cliente.bind(text=self.atualizar_info_conta_modal)
        box_conta_origem.add_widget(self.spinner_conta_cliente)
        
        self.lbl_info_conta_modal = Label(
            text='Selecione uma conta para verificar o saldo',
            font_size='10sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        box_conta_origem.add_widget(self.lbl_info_conta_modal)
        
        main_layout.add_widget(box_conta_origem)
        
        # 🔥 BENEFICIÁRIO SALVO
        box_beneficiario_salvo = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        
        lbl_benef_salvo = Label(
            text='SELECIONAR BENEFICIÁRIO SALVO',
            font_size='12sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.4,
            text_size=(None, None),
            halign='left'
        )
        box_beneficiario_salvo.add_widget(lbl_benef_salvo)
        
        self.spinner_beneficiarios_modal = Spinner(
            text='',
            font_size='11sp',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            values=['']
        )
        self.carregar_beneficiarios_cliente_modal(username_cliente)
        self.spinner_beneficiarios_modal.bind(text=self.preencher_dados_beneficiario_modal)
        box_beneficiario_salvo.add_widget(self.spinner_beneficiarios_modal)
        
        main_layout.add_widget(box_beneficiario_salvo)
        
        # 🔥 DADOS DO BENEFICIÁRIO
        box_dados_beneficiario = BoxLayout(orientation='vertical', size_hint_y=None, height=300)
        
        lbl_titulo_benef = Label(
            text='DADOS DO BENEFICIÁRIO',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.1,
            text_size=(None, None),
            halign='left'
        )
        box_dados_beneficiario.add_widget(lbl_titulo_benef)
        
        grid_beneficiario = GridLayout(cols=1, size_hint_y=0.9, spacing=8)
        
        # Campos de texto para dados do beneficiário
        self.entry_beneficiario_modal = TextInput(
            hint_text='Nome Completo do Beneficiário *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_beneficiario.add_widget(self.entry_beneficiario_modal)
        
        self.entry_endereco_modal = TextInput(
            hint_text='Endereço Completo *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_beneficiario.add_widget(self.entry_endereco_modal)
        
        self.entry_cidade_modal = TextInput(
            hint_text='Cidade *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_beneficiario.add_widget(self.entry_cidade_modal)
        
        self.entry_pais_modal = TextInput(
            hint_text='País *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_beneficiario.add_widget(self.entry_pais_modal)
        
        box_dados_beneficiario.add_widget(grid_beneficiario)
        main_layout.add_widget(box_dados_beneficiario)
        
        # 🔥 DADOS DO BANCO
        box_dados_banco = BoxLayout(orientation='vertical', size_hint_y=None, height=350)
        
        lbl_titulo_banco = Label(
            text='DADOS DO BANCO DESTINATÁRIO',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.1,
            text_size=(None, None),
            halign='left'
        )
        box_dados_banco.add_widget(lbl_titulo_banco)
        
        grid_banco = GridLayout(cols=1, size_hint_y=0.9, spacing=8)
        
        self.entry_banco_modal = TextInput(
            hint_text='Nome do Banco Destinatário *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_banco.add_widget(self.entry_banco_modal)
        
        self.entry_endereco_banco_modal = TextInput(
            hint_text='Endereço do Banco',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_banco.add_widget(self.entry_endereco_banco_modal)
        
        self.entry_swift_modal = TextInput(
            hint_text='Código SWIFT/BIC *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_banco.add_widget(self.entry_swift_modal)
        
        self.entry_iban_modal = TextInput(
            hint_text='Código IBAN / Account # *',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_banco.add_widget(self.entry_iban_modal)
        
        self.entry_aba_modal = TextInput(
            hint_text='Código ABA/Routing (se aplicável)',
            font_size='11sp',
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        grid_banco.add_widget(self.entry_aba_modal)
        
        box_dados_banco.add_widget(grid_banco)
        main_layout.add_widget(box_dados_banco)
        
        # 🔥 SALVAR BENEFICIÁRIO
        box_salvar_benef = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        self.check_salvar_benef_modal = CheckBox(
            size_hint_x=0.2,
            active=False
        )
        
        lbl_salvar_benef = Label(
            text='Salvar este beneficiário para transferências futuras',
            font_size='11sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        box_salvar_benef.add_widget(self.check_salvar_benef_modal)
        box_salvar_benef.add_widget(lbl_salvar_benef)
        main_layout.add_widget(box_salvar_benef)
        
        # 🔥 VALOR E INFORMAÇÕES
        box_valor_info = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        
        lbl_titulo_valor = Label(
            text='VALOR E INFORMAÇÕES',
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='left'
        )
        box_valor_info.add_widget(lbl_titulo_valor)
        
        # Layout para valor
        layout_valor = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        self.lbl_moeda_modal = Label(
            text='USD',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.2,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        self.entry_valor_modal = TextInput(
            hint_text='0.00',
            font_size='16sp',
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[15, 12],
            halign='right'
        )
        
        layout_valor.add_widget(self.lbl_moeda_modal)
        layout_valor.add_widget(self.entry_valor_modal)
        box_valor_info.add_widget(layout_valor)
        
        # Finalidade
        layout_finalidade = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=5)
        
        lbl_finalidade = Label(
            text='Finalidade da Transferência *',
            font_size='11sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        
        self.spinner_finalidade_modal = Spinner(
            text='Pagamento de Serviços',
            font_size='11sp',
            size_hint_y=0.7,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            values=['Pagamento de Serviços', 'Investimentos', 'Manutenção de Conta', 'Doação', 'Presente', 'Outros']
        )
        
        layout_finalidade.add_widget(lbl_finalidade)
        layout_finalidade.add_widget(self.spinner_finalidade_modal)
        box_valor_info.add_widget(layout_finalidade)
        
        main_layout.add_widget(box_valor_info)
        
        # 🔥 DESCRIÇÃO
        box_descricao = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        
        lbl_descricao = Label(
            text='Descrição Adicional (opcional):',
            font_size='11sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        box_descricao.add_widget(lbl_descricao)
        
        self.entry_descricao_modal = TextInput(
            hint_text='Digite uma descrição adicional...',
            font_size='11sp',
            size_hint_y=0.7,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10],
            multiline=True
        )
        box_descricao.add_widget(self.entry_descricao_modal)
        main_layout.add_widget(box_descricao)
        
        # 🔥 ADICIONAR: SEÇÃO DE INVOICE (EXATAMENTE IGUAL AO CLIENTE)
        box_invoice = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        
        lbl_invoice = Label(
            text='ANEXAR INVOICE (OPCIONAL)',
            font_size='11sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='left'
        )
        box_invoice.add_widget(lbl_invoice)

        btn_upload_invoice_modal = Button(
            text='SELECIONAR INVOICE',
            font_size='11sp',
            size_hint_y=0.4,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            on_press=lambda x: self.selecionar_invoice_admin()
        )
        box_invoice.add_widget(btn_upload_invoice_modal)

        self.lbl_arquivo_invoice_modal = Label(
            text='Nenhum arquivo selecionado',
            font_size='9sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        box_invoice.add_widget(self.lbl_arquivo_invoice_modal)
        
        main_layout.add_widget(box_invoice)
        
        # BOTÕES FINAIS
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_solicitar = Button(
            text='SOLICITAR TRANSFERÊNCIA',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_solicitar)
        main_layout.add_widget(botoes_layout)
        
        # Configurar ScrollView
        scroll_content.add_widget(main_layout)
        
        # 🔥 CORREÇÃO: Largura reduzida pela metade (0.45 em vez de 0.85)
        self.popup_transferencia_completa = Popup(
            title=f'Transferência - {nome_cliente}',
            title_color=(0.23, 0.51, 0.96, 1),
            content=scroll_content,
            size_hint=(0.45, 0.95),  # 🔥 ALTERADO: 0.85 → 0.45 (metade da largura)
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def solicitar_transferencia(instance):
            """Processa a solicitação de transferência em nome do cliente"""
            self.processar_transferencia_admin(username_cliente)
        
        def cancelar(instance):
            self.popup_transferencia_completa.dismiss()
        
        btn_solicitar.bind(on_press=solicitar_transferencia)
        btn_cancelar.bind(on_press=cancelar)
        
        self.popup_transferencia_completa.open()

    def carregar_contas_cliente_modal(self, username_cliente):
        """Carrega as contas internacionais do cliente selecionado - VERSÃO HÍBRIDA CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 PADRÃO: Tentar Supabase primeiro
            contas_internacionais = []
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                print(f"📡 Buscando contas do cliente {username_cliente} no Supabase...")
                try:
                    # 🔥 CORREÇÃO: Buscar direto do Supabase (método não existe no manager)
                    response = sistema.supabase.client.table('contas')\
                        .select('*')\
                        .eq('cliente_username', username_cliente)\
                        .execute()
                    
                    if response.data:
                        for conta in response.data:
                            if conta.get('moeda') in ['USD', 'EUR', 'GBP']:
                                texto = f"{conta['id']} | {conta['moeda']} | Saldo: {conta['saldo']:,.2f}"
                                contas_internacionais.append(texto)
                        
                        print(f"✅ {len(contas_internacionais)} contas internacionais carregadas do Supabase")
                        
                except Exception as supabase_error:
                    print(f"❌ Erro ao buscar contas no Supabase: {supabase_error}")
            
            # 🔥 FALLBACK: Se Supabase falhou ou não tem dados, usar local
            if not contas_internacionais and username_cliente in sistema.usuarios:
                print("🔄 Usando fallback local para contas...")
                for conta_num in sistema.usuarios[username_cliente].get('contas', []):
                    if conta_num in sistema.contas and sistema.contas[conta_num]['moeda'] in ['USD', 'EUR', 'GBP']:
                        dados_conta = sistema.contas[conta_num]
                        texto = f"{conta_num} | {dados_conta['moeda']} | Saldo: {dados_conta['saldo']:,.2f}"
                        contas_internacionais.append(texto)
            
            # Atualizar UI
            if hasattr(self, 'spinner_conta_cliente'):
                self.spinner_conta_cliente.values = contas_internacionais
                if contas_internacionais:
                    self.spinner_conta_cliente.text = contas_internacionais[0]
                    self.atualizar_info_conta_modal()
                else:
                    self.spinner_conta_cliente.text = "Nenhuma conta internacional encontrada"
                    if hasattr(self, 'lbl_info_conta_modal'):
                        self.lbl_info_conta_modal.text = "Nenhuma conta disponível"
                
        except Exception as e:
            print(f"❌ Erro ao carregar contas do cliente: {e}")


    def carregar_beneficiarios_cliente_modal(self, username_cliente):
        """Carrega os beneficiários salvos do cliente selecionado - VERSÃO HÍBRIDA"""
        sistema = App.get_running_app().sistema
        
        try:
            beneficiarios = []
            
            # 🔥 PADRÃO: Tentar Supabase primeiro
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                print(f"📡 Buscando beneficiários do cliente {username_cliente} no Supabase...")
                beneficiarios_supabase = sistema.supabase.obter_beneficiarios_cliente(username_cliente)
                
                if beneficiarios_supabase:
                    beneficiarios = beneficiarios_supabase
                    print(f"✅ {len(beneficiarios)} beneficiários carregados do Supabase")
            
            # 🔥 FALLBACK: Se Supabase falhou, usar local
            if not beneficiarios and username_cliente in sistema.beneficiarios:
                print("🔄 Usando fallback local para beneficiários...")
                beneficiarios = sistema.beneficiarios[username_cliente]
            
            # Preparar valores para o spinner
            valores = ['']  # Opção vazia
            for benef in beneficiarios:
                nome_formatado = f"{benef['nome']} | {benef['banco']} | {benef['pais']}"
                valores.append(nome_formatado)
            
            if hasattr(self, 'spinner_beneficiarios_modal'):
                self.spinner_beneficiarios_modal.values = valores
                
        except Exception as e:
            print(f"❌ Erro ao carregar beneficiários: {e}")

    def atualizar_info_conta_modal(self, instance=None, value=None):
        """Atualiza informações da conta selecionada no modal"""
        sistema = App.get_running_app().sistema
        
        if hasattr(self, 'spinner_conta_cliente') and self.spinner_conta_cliente.text:
            conta_texto = self.spinner_conta_cliente.text
            if ' | ' in conta_texto:
                conta_selecionada = conta_texto.split(' | ')[0].strip()
                
                if conta_selecionada in sistema.contas:
                    dados = sistema.contas[conta_selecionada]
                    if hasattr(self, 'lbl_info_conta_modal'):
                        self.lbl_info_conta_modal.text = f"Saldo disponível: {dados['saldo']:,.2f} {dados['moeda']} | Moeda: {dados['moeda']}"

    def preencher_dados_beneficiario_modal(self, instance, value):
        """Preenche automaticamente os campos quando um beneficiário é selecionado"""
        if not value or value == "":
            return
        
        sistema = App.get_running_app().sistema
        username_cliente = self.spinner_cliente_modal.text.split(' - ')[0]
        
        try:
            if username_cliente in sistema.beneficiarios:
                # Extrair o nome do beneficiário do texto formatado
                nome_beneficiario = value.split(' | ')[0]
                
                for benef in sistema.beneficiarios[username_cliente]:
                    if benef['nome'] == nome_beneficiario:
                        # Preencher todos os campos
                        if hasattr(self, 'entry_beneficiario_modal'):
                            self.entry_beneficiario_modal.text = benef['nome']
                        if hasattr(self, 'entry_endereco_modal'):
                            self.entry_endereco_modal.text = benef['endereco']
                        if hasattr(self, 'entry_cidade_modal'):
                            self.entry_cidade_modal.text = benef['cidade']
                        if hasattr(self, 'entry_pais_modal'):
                            self.entry_pais_modal.text = benef['pais']
                        if hasattr(self, 'entry_banco_modal'):
                            self.entry_banco_modal.text = benef['banco']
                        if hasattr(self, 'entry_endereco_banco_modal'):
                            self.entry_endereco_banco_modal.text = benef.get('endereco_banco', '')
                        if hasattr(self, 'entry_swift_modal'):
                            self.entry_swift_modal.text = benef['swift']
                        if hasattr(self, 'entry_iban_modal'):
                            self.entry_iban_modal.text = benef['iban']
                        if hasattr(self, 'entry_aba_modal'):
                            self.entry_aba_modal.text = benef.get('aba', '')
                        
                        print(f"✅ Dados do beneficiário '{benef['nome']}' preenchidos automaticamente")
                        break
                        
        except Exception as e:
            print(f"❌ Erro ao preencher dados do beneficiário: {e}")


    def processar_transferencia_admin(self, username_cliente):
        """Processa a transferência internacional em nome do cliente - COM SUPABASE"""
        sistema = App.get_running_app().sistema
        
        print("🌍 Processando transferência internacional (admin)...")
        
        # 🔥 VALIDAÇÃO SIMPLIFICADA (CÓDIGO ORIGINAL MANTIDO)
        try:
            # Validar conta de origem (CÓDIGO ORIGINAL MANTIDO)
            if not hasattr(self, 'spinner_conta_cliente') or not self.spinner_conta_cliente.text or 'Selecione' in self.spinner_conta_cliente.text:
                self.mostrar_erro("Selecione uma conta de origem!")
                return
                
            # Validar campos de texto obrigatórios (CÓDIGO ORIGINAL MANTIDO)
            campos_texto = [
                (self.entry_beneficiario_modal, "Nome Completo do Beneficiário"),
                (self.entry_endereco_modal, "Endereço Completo"),
                (self.entry_cidade_modal, "Cidade"),
                (self.entry_pais_modal, "País"),
                (self.entry_banco_modal, "Nome do Banco Destinatário"),
                (self.entry_swift_modal, "Código SWIFT/BIC"),
                (self.entry_iban_modal, "Código IBAN / Account #"),
                (self.entry_valor_modal, "Valor da transferência")
            ]
            
            for campo, nome in campos_texto:
                if not campo.text.strip():
                    self.mostrar_erro(f"Preencha o campo: {nome}")
                    return
            
            # Extrair dados da conta de origem (CÓDIGO ORIGINAL MANTIDO)
            conta_texto = self.spinner_conta_cliente.text
            conta_origem = conta_texto.split(' | ')[0].strip()
            
            # Validar valor (CÓDIGO ORIGINAL MANTIDO)
            try:
                valor = float(self.entry_valor_modal.text.replace(',', '').strip())
                if valor <= 0:
                    self.mostrar_erro("Valor deve ser maior que zero!")
                    return
            except ValueError:
                self.mostrar_erro("Valor inválido! Use apenas números.")
                return
            
            # Preparar dados para o sistema (CÓDIGO ORIGINAL MANTIDO)
            dados_transferencia = {
                'conta_origem': conta_origem,
                'valor': valor,
                'finalidade': self.spinner_finalidade_modal.text if hasattr(self, 'spinner_finalidade_modal') else 'Pagamento de Serviços',
                'descricao': self.entry_descricao_modal.text if hasattr(self, 'entry_descricao_modal') else '',
                'beneficiario': self.entry_beneficiario_modal.text.strip(),
                'endereco': self.entry_endereco_modal.text.strip(),
                'cidade': self.entry_cidade_modal.text.strip(),
                'pais': self.entry_pais_modal.text.strip(),
                'banco': self.entry_banco_modal.text.strip(),
                'endereco_banco': self.entry_endereco_banco_modal.text.strip() if hasattr(self, 'entry_endereco_banco_modal') else '',
                'swift': self.entry_swift_modal.text.strip(),
                'iban': self.entry_iban_modal.text.strip(),
                'aba': self.entry_aba_modal.text.strip() if hasattr(self, 'entry_aba_modal') else ''
            }
            
            # 🔥 VERIFICAR SE TEM INVOICE (CÓDIGO ORIGINAL MANTIDO)
            tem_invoice = hasattr(self, 'arquivo_invoice_selecionado_admin') and self.arquivo_invoice_selecionado_admin
            
            # 🔥 CHAMAR MÉTODO DO SISTEMA (CÓDIGO ORIGINAL MANTIDO)
            sucesso, resultado = sistema.solicitar_transferencia_internacional(
                dados_transferencia, 
                usuario_solicitante=username_cliente
            )
            
            if sucesso:
                transferencia_id = resultado
                
                # 🔥 ANEXAR INVOICE SE EXISTIR (CÓDIGO ORIGINAL MANTIDO)
                if tem_invoice:
                    print("📎 Invoice detectado, anexando...")
                    if self.anexar_invoice_transferencia_admin(transferencia_id):
                        print(f"✅ Invoice anexado com sucesso à transferência {transferencia_id}")
                    else:
                        print(f"⚠️ Invoice não pôde ser anexado à transferência {transferencia_id}")
                
                # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
                self.salvar_transferencia_internacional_supabase(
                    transferencia_id, dados_transferencia, username_cliente, tem_invoice
                )
                
                # Salvar beneficiário se solicitado (CÓDIGO ORIGINAL MANTIDO)
                if hasattr(self, 'check_salvar_benef_modal') and self.check_salvar_benef_modal.active:
                    dados_beneficiario = {
                        'nome': dados_transferencia['beneficiario'],
                        'endereco': dados_transferencia['endereco'],
                        'cidade': dados_transferencia['cidade'],
                        'pais': dados_transferencia['pais'],
                        'banco': dados_transferencia['banco'],
                        'endereco_banco': dados_transferencia['endereco_banco'],
                        'swift': dados_transferencia['swift'],
                        'iban': dados_transferencia['iban'],
                        'aba': dados_transferencia['aba']
                    }
                    
                    if username_cliente not in sistema.beneficiarios:
                        sistema.beneficiarios[username_cliente] = []
                    
                    beneficiario_existe = False
                    for benef in sistema.beneficiarios[username_cliente]:
                        if benef['nome'] == dados_beneficiario['nome'] and benef['iban'] == dados_beneficiario['iban']:
                            beneficiario_existe = True
                            break
                    
                    if not beneficiario_existe:
                        sistema.beneficiarios[username_cliente].append(dados_beneficiario)
                        sistema.salvar_beneficiarios()
                        print(f"✅ Beneficiário salvo para {username_cliente}")
                
                # Fechar modal e mostrar sucesso (CÓDIGO ORIGINAL MANTIDO)
                self.popup_transferencia_completa.dismiss()
                
                # Obter dados atualizados (CÓDIGO ORIGINAL MANTIDO)
                if conta_origem in sistema.contas:
                    novo_saldo = sistema.contas[conta_origem]['saldo']
                    moeda_origem = sistema.contas[conta_origem]['moeda']
                else:
                    novo_saldo = 0
                    moeda_origem = 'USD'
                
                # Mensagem com info do invoice (CÓDIGO ORIGINAL MANTIDO)
                mensagem_invoice = "\n📎 INVOICE: ANEXADO" if tem_invoice else "\n📎 INVOICE: NÃO ANEXADO"
                
                self.mostrar_sucesso(
                    f"Transferência solicitada com sucesso!\n\n"
                    f"ID: {transferencia_id}\n"
                    f"Cliente: {username_cliente}\n"
                    f"Valor: {valor:,.2f} {moeda_origem}\n"
                    f"Conta: {conta_origem}\n"
                    f"Novo saldo: {novo_saldo:,.2f} {moeda_origem}"
                    f"{mensagem_invoice}\n\n"
                    f"A transferência aparecerá nas solicitações do cliente."
                )
                
            else:
                self.mostrar_erro(f"Erro na transferência: {resultado}")
            
        except Exception as e:
            print(f"❌ Erro ao processar transferência: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro interno: {str(e)}")

    def salvar_ajuste_supabase(self, transacao_id, conta_num, valor, operacao, descricao, username):
        """Salva ajuste de saldo no Supabase - MANTÉM COMPATIBILIDADE"""
        try:
            from supabase_service import SupabaseService
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            # Preparar dados para o Supabase
            dados_supabase = {
                'id': transacao_id,
                'tipo': 'ajuste_admin',
                'status': 'completed',
                'data': datetime.now().isoformat(),
                'moeda': sistema.contas[conta_num]['moeda'],
                'valor': valor,
                'conta_remetente': conta_num,
                'descricao': descricao,
                'executado_por': sistema.usuario_logado['username'],
                'cliente_afetado': username,
                'tipo_ajuste': 'CREDITO' if operacao == 'credito' else 'DEBITO',
                'descricao_ajuste': descricao,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            service = SupabaseService()
            resultado = service.salvar_transacao(dados_supabase)
            
            if resultado:
                print(f"✅ Ajuste salvo no Supabase! ID: {transacao_id}")
            else:
                print(f"⚠️ Ajuste NÃO salvo no Supabase (mas foi salvo localmente)")
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar ajuste no Supabase: {e} (mas operação foi salva localmente)")

    def salvar_despesa_supabase(self, conta_bancaria, valor, conta_despesa, categoria_despesa, descricao):
        """Salva lançamento de despesa no Supabase - MANTÉM COMPATIBILIDADE"""
        try:
            from supabase_service import SupabaseService
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            # Preparar dados para o Supabase
            dados_supabase = {
                'id': str(random.randint(100000, 999999)),
                'tipo': 'despesa',
                'status': 'completed',
                'data': datetime.now().isoformat(),
                'moeda': 'USD',  # Assumindo USD para despesas
                'valor': valor,
                'conta_remetente': conta_bancaria,
                'descricao': descricao,
                'executado_por': sistema.usuario_logado['username'],
                'categoria_despesa': categoria_despesa,
                'descricao_despesa': descricao,
                'conta_despesa': conta_despesa,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            service = SupabaseService()
            resultado = service.salvar_transacao(dados_supabase)
            
            if resultado:
                print(f"✅ Despesa salva no Supabase! Valor: {valor}")
            else:
                print(f"⚠️ Despesa NÃO salva no Supabase (mas foi salva localmente)")
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar despesa no Supabase: {e} (mas operação foi salva localmente)")

    def salvar_receita_supabase(self, conta_cliente, valor, conta_receita, categoria_receita, descricao, username):
        """Salva lançamento de receita no Supabase - MANTÉM COMPATIBILIDADE"""
        try:
            from supabase_service import SupabaseService
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            # Preparar dados para o Supabase
            dados_supabase = {
                'id': str(random.randint(100000, 999999)),
                'tipo': 'receita',
                'status': 'completed',
                'data': datetime.now().isoformat(),
                'moeda': sistema.contas[conta_cliente]['moeda'],
                'valor': valor,
                'conta_remetente': conta_cliente,
                'descricao': descricao,
                'executado_por': sistema.usuario_logado['username'],
                'cliente_afetado': username,
                'categoria_receita': categoria_receita,
                'descricao_receita': descricao,
                'conta_receita': conta_receita,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            service = SupabaseService()
            resultado = service.salvar_transacao(dados_supabase)
            
            if resultado:
                print(f"✅ Receita salva no Supabase! Valor: {valor}")
            else:
                print(f"⚠️ Receita NÃO salva no Supabase (mas foi salva localmente)")
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar receita no Supabase: {e} (mas operação foi salva localmente)")

    def _atualizar_saldos_supabase(self, conta_origem, conta_destino, valor, moeda, origem_empresa, destino_empresa):
        """Atualiza saldos no Supabase após transferência interna"""
        try:
            sistema = App.get_running_app().sistema
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível para atualizar saldos")
                return False
            
            print(f"🔄 Atualizando saldos no Supabase: {conta_origem} -> {conta_destino}")
            
            # 🔥 ATUALIZAR CONTA DE ORIGEM
            if origem_empresa:
                # É conta da empresa
                novo_saldo_origem = sistema.contas_bancarias_empresa[conta_origem]['saldo']
                response_origem = sistema.supabase.client.table('contas_bancarias_empresa')\
                    .update({'saldo': novo_saldo_origem})\
                    .eq('id', conta_origem)\
                    .execute()
            else:
                # É conta de cliente
                novo_saldo_origem = sistema.contas[conta_origem]['saldo']
                response_origem = sistema.supabase.client.table('contas')\
                    .update({'saldo': novo_saldo_origem})\
                    .eq('id', conta_origem)\
                    .execute()
            
            # 🔥 ATUALIZAR CONTA DE DESTINO
            if destino_empresa:
                # É conta da empresa
                novo_saldo_destino = sistema.contas_bancarias_empresa[conta_destino]['saldo']
                response_destino = sistema.supabase.client.table('contas_bancarias_empresa')\
                    .update({'saldo': novo_saldo_destino})\
                    .eq('id', conta_destino)\
                    .execute()
            else:
                # É conta de cliente
                novo_saldo_destino = sistema.contas[conta_destino]['saldo']
                response_destino = sistema.supabase.client.table('contas')\
                    .update({'saldo': novo_saldo_destino})\
                    .eq('id', conta_destino)\
                    .execute()
            
            # Verificar resultados
            sucesso_origem = bool(response_origem.data)
            sucesso_destino = bool(response_destino.data)
            
            if sucesso_origem and sucesso_destino:
                print(f"✅✅✅ Saldos atualizados no Supabase: {conta_origem}={novo_saldo_origem}, {conta_destino}={novo_saldo_destino}")
                return True
            else:
                print(f"❌ Erro ao atualizar saldos: origem={sucesso_origem}, destino={sucesso_destino}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar saldos no Supabase: {e}")
            return False

    def salvar_transferencia_interna_supabase(self, transferencia_id, conta_origem, conta_destino, valor, moeda, 
                                            tipo, descricao, origem_empresa, destino_empresa):
        """Salva transferência interna no Supabase - VERSÃO CORRIGIDA"""
        try:
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            print(f"🔍 DEBUG SUPABASE: Salvando transferência {transferencia_id}")
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível")
                return False
            
            # Preparar dados
            dados_supabase = {
                'id': transferencia_id,
                'tipo': tipo,
                'status': 'completed', 
                'data': datetime.now().isoformat(),
                'moeda': moeda,
                'valor': valor,
                'conta_remetente': conta_origem,
                'conta_destinatario': conta_destino,
                'descricao': descricao,
                'executado_por': sistema.usuario_logado,
                'finalidade': 'Transferência Interna',
                'created_at': datetime.now().isoformat()
            }
            
            print(f"📦 Dados para Supabase: {dados_supabase}")
            
            # 🔥 USAR CLIENTE SUPABASE DIRETO
            response = sistema.supabase.client.table('transferencias')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅✅✅ TRANSFERÊNCIA INTERNA {transferencia_id} SALVA NO SUPABASE!")
                return True
            else:
                print(f"❌❌❌ ERRO AO SALVAR NO SUPABASE: {response.error}")
                return False
                
        except Exception as e:
            print(f"💥 ERRO CRÍTICO NO SUPABASE: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _obter_cliente_por_conta(self, conta_numero):
        """Obtém o username do cliente por número da conta"""
        sistema = App.get_running_app().sistema
        
        # Buscar em contas de clientes
        for username, dados_usuario in sistema.usuarios.items():
            if conta_numero in dados_usuario.get('contas', []):
                return username
        
        # Se não encontrou, pode ser conta da empresa
        return None

    def salvar_transferencia_internacional_supabase(self, transferencia_id, dados_transferencia, username_cliente, tem_invoice):
        """Salva transferência internacional no Supabase - MANTÉM COMPATIBILIDADE"""
        try:
            from supabase_service import SupabaseService
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            # Preparar dados para o Supabase
            dados_supabase = {
                'id': transferencia_id,
                'tipo': 'transferencia_internacional',
                'status': 'solicitada',
                'data': datetime.now().isoformat(),
                'moeda': sistema.contas[dados_transferencia['conta_origem']]['moeda'],
                'valor': dados_transferencia['valor'],
                'conta_remetente': dados_transferencia['conta_origem'],
                'descricao': dados_transferencia.get('descricao', ''),
                'executado_por': sistema.usuario_logado['username'],
                'cliente_afetado': username_cliente,
                'beneficiario': dados_transferencia['beneficiario'],
                'endereco_beneficiario': dados_transferencia['endereco'],
                'cidade': dados_transferencia['cidade'],
                'pais': dados_transferencia['pais'],
                'nome_banco': dados_transferencia['banco'],
                'endereco_banco': dados_transferencia.get('endereco_banco', ''),
                'codigo_swift': dados_transferencia['swift'],
                'iban_account': dados_transferencia['iban'],
                'aba_routing': dados_transferencia.get('aba', ''),
                'finalidade': dados_transferencia['finalidade'],
                'tem_invoice': tem_invoice,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            service = SupabaseService()
            resultado = service.salvar_transacao(dados_supabase)
            
            if resultado:
                print(f"✅ Transferência internacional salva no Supabase! ID: {transferencia_id}")
            else:
                print(f"⚠️ Transferência internacional NÃO salva no Supabase (mas foi salva localmente)")
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar transferência internacional no Supabase: {e} (mas operação foi salva localmente)")

    def anexar_invoice_transferencia_admin(self, transferencia_id):
        """Anexa o invoice selecionado à transferência do admin"""
        try:
            print(f"🔍 DEBUG ANEXAR INVOICE ADMIN: Iniciando anexação para {transferencia_id}")
            
            if not hasattr(self, 'arquivo_invoice_selecionado_admin') or not self.arquivo_invoice_selecionado_admin:
                print("ℹ️ Nenhum invoice selecionado para anexar (admin)")
                return True  # Não é obrigatório, então retorna sucesso
            
            sistema = App.get_running_app().sistema
            
            print(f"🔍 DEBUG ANEXAR INVOICE ADMIN: Copiando arquivo...")
            # Copiar arquivo para pasta do sistema
            caminho_destino = self.copiar_arquivo_invoice_admin(self.arquivo_invoice_selecionado_admin, transferencia_id)
            
            if caminho_destino:
                print(f"🔍 DEBUG ANEXAR INVOICE ADMIN: Arquivo copiado, adicionando ao sistema...")
                # Adicionar informações ao sistema
                sucesso = sistema.adicionar_invoice_info_transferencia(transferencia_id, caminho_destino)
                
                if sucesso:
                    print(f"✅ Invoice anexado à transferência {transferencia_id} (admin)")
                    return True
                else:
                    print(f"❌ Erro ao anexar invoice à transferência (admin)")
                    return False
            else:
                print(f"❌ Erro ao copiar arquivo de invoice (admin)")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao anexar invoice (admin): {e}")
            return False

    def copiar_arquivo_invoice_admin(self, caminho_origem, transferencia_id):
        """Copia o arquivo de invoice para a pasta do sistema - VERSÃO ADMIN"""
        try:
            import os
            import shutil
            
            # 🔥 CRIAR PASTA invoices SE NÃO EXISTIR
            pasta_invoices = 'data/invoices'
            if not os.path.exists(pasta_invoices):
                os.makedirs(pasta_invoices)
                print(f"✅ Pasta '{pasta_invoices}' criada (admin)")
            
            # Gerar nome único para o arquivo
            nome_arquivo = os.path.basename(caminho_origem)
            nome_base, extensao = os.path.splitext(nome_arquivo)
            novo_nome = f"{transferencia_id}_{nome_base}{extensao}"
            caminho_destino = os.path.join(pasta_invoices, novo_nome)
            
            # Copiar arquivo
            shutil.copy2(caminho_origem, caminho_destino)
            
            print(f"✅ Invoice copiado para: {caminho_destino} (admin)")
            return caminho_destino
            
        except Exception as e:
            print(f"❌ Erro ao copiar invoice (admin): {e}")
            return None


    def carregar_clientes_modal(self):
        """Carrega a lista de clientes no spinner do modal"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = ['Selecione um cliente']
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                # Verificar se tem contas internacionais
                tem_contas_internacionais = any(
                    sistema.contas[conta]['moeda'] in ['USD', 'EUR', 'GBP'] 
                    for conta in dados.get('contas', []) 
                    if conta in sistema.contas
                )
                if tem_contas_internacionais:
                    clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        self.spinner_cliente_modal.values = clientes_opcoes

    def criar_campos_transferencia_interna(self):
        """Cria campos para transferência interna - VERSÃO 2 COLUNAS"""
        # Usar os novos containers
        container_origem = self.ids.container_origem_coluna
        container_destino = self.ids.container_destino_coluna
        
        container_origem.clear_widgets()
        container_destino.clear_widgets()
        
        # 🔥 TIPO DE ORIGEM (na coluna esquerda)
        tipo_origem_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        tipo_origem_layout.add_widget(Label(
            text='Tipo de Origem *',
            font_size='13sp',
            bold=True,
            color=(0.7, 0.8, 1, 1),
            size_hint_y=0.4,
            text_size=(None, None),
            halign='left'
        ))
        
        self.spinner_tipo_origem = Spinner(
            text='Selecione o tipo de origem',
            font_size='13sp',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            values=['Selecione o tipo de origem', 'Conta Bancária da Empresa', 'Conta de Cliente']
        )
        tipo_origem_layout.add_widget(self.spinner_tipo_origem)
        container_origem.add_widget(tipo_origem_layout)
        
        # 🔥 TIPO DE DESTINO (na coluna direita)
        tipo_destino_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        tipo_destino_layout.add_widget(Label(
            text='Tipo de Destino *',
            font_size='13sp',
            bold=True,
            color=(0.7, 0.8, 1, 1),
            size_hint_y=0.4,
            text_size=(None, None),
            halign='left'
        ))
        
        self.spinner_tipo_destino = Spinner(
            text='Selecione o tipo de destino',
            font_size='13sp',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            values=['Selecione o tipo de destino', 'Conta de Cliente', 'Conta Bancária da Empresa']
        )
        tipo_destino_layout.add_widget(self.spinner_tipo_destino)
        container_destino.add_widget(tipo_destino_layout)
        
        # Container dinâmico para origem (dentro da coluna esquerda)
        self.container_origem_dinamica = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=0
        )
        container_origem.add_widget(self.container_origem_dinamica)
        
        # Container dinâmico para destino (dentro da coluna direita)
        self.container_destino_dinamica = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=0
        )
        container_destino.add_widget(self.container_destino_dinamica)
        
        # Bind para atualizar campos dinâmicos
        self.spinner_tipo_origem.bind(text=lambda instance, value: self.atualizar_origem_transferencia_interna())
        self.spinner_tipo_destino.bind(text=lambda instance, value: self.atualizar_destino_transferencia_interna())

    def atualizar_moeda_valor(self, instance, value):
        """Atualiza a moeda mostrada no campo de valor baseado na conta origem selecionada"""
        moeda = self.obter_moeda_origem()
        if moeda and hasattr(self, 'label_moeda_transferencia'):
            self.label_moeda_transferencia.text = moeda
            print(f"💰 Moeda do valor atualizada para: {moeda}")

    def carregar_clientes_transferencia_internacional(self):
        """Carrega clientes para transferência internacional"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = []
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                # Verificar se tem contas internacionais
                tem_contas_internacionais = any(
                    sistema.contas[conta]['moeda'] in ['USD', 'EUR', 'GBP'] 
                    for conta in dados.get('contas', []) 
                    if conta in sistema.contas
                )
                if tem_contas_internacionais:
                    clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        if hasattr(self, 'spinner_cliente_transf_internacional'):
            self.spinner_cliente_transf_internacional.values = clientes_opcoes
            if clientes_opcoes:
                self.spinner_cliente_transf_internacional.text = clientes_opcoes[0]

    def atualizar_contas_transferencia_internacional(self, instance, value):
        """Atualiza contas quando cliente é selecionado na transferência internacional"""
        sistema = App.get_running_app().sistema
        
        if not value or value == 'Selecione o cliente':
            return
        
        username = value.split(' - ')[0]
        
        if username in sistema.usuarios:
            # Filtrar apenas contas internacionais (USD, EUR, GBP)
            contas_internacionais = []
            for conta_num in sistema.usuarios[username].get('contas', []):
                if conta_num in sistema.contas:
                    moeda = sistema.contas[conta_num]['moeda']
                    if moeda in ['USD', 'EUR', 'GBP']:
                        saldo = sistema.contas[conta_num]['saldo']
                        contas_internacionais.append(f"{conta_num} - {moeda} - Saldo: {saldo:,.2f}")
            
            if hasattr(self, 'spinner_conta_transf_internacional'):
                self.spinner_conta_transf_internacional.values = contas_internacionais
                if contas_internacionais:
                    self.spinner_conta_transf_internacional.text = contas_internacionais[0]

    def atualizar_origem_transferencia_interna(self, instance=None, value=None):
        """Atualiza campos de origem para transferência interna - VERSÃO 2 COLUNAS"""
        if not hasattr(self, 'container_origem_dinamica'):
            return
        
        container = self.container_origem_dinamica
        container.clear_widgets()
        container.height = 0
        
        tipo_origem = self.spinner_tipo_origem.text
        
        # 🔥 CORREÇÃO: Só criar campos se não for a opção de seleção
        if tipo_origem == 'Selecione o tipo de origem':
            # Não mostrar nada - aguardar seleção do usuário
            return
            
        elif tipo_origem == 'Conta Bancária da Empresa':
            # Contas bancárias da empresa
            layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            layout.add_widget(Label(
                text='Conta Bancária Origem *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_conta_empresa_origem = Spinner(
                text='Selecione a conta',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            layout.add_widget(self.spinner_conta_empresa_origem)
            container.add_widget(layout)
            container.height += 80
            
            # Carregar contas da empresa
            self.carregar_contas_empresa_origem()
            
        else:  # Conta de Cliente
            # Cliente
            cliente_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            cliente_layout.add_widget(Label(
                text='Cliente Origem *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_cliente_interna_origem = Spinner(
                text='Selecione o cliente',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            cliente_layout.add_widget(self.spinner_cliente_interna_origem)
            container.add_widget(cliente_layout)
            
            # Conta do Cliente
            conta_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            conta_layout.add_widget(Label(
                text='Conta do Cliente *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_conta_interna_origem = Spinner(
                text='Selecione a conta',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            conta_layout.add_widget(self.spinner_conta_interna_origem)
            container.add_widget(conta_layout)
            
            container.height += 160
            
            # Carregar clientes imediatamente
            self.carregar_clientes_transferencia_interna_origem()
            
            # Bind para atualizar contas quando cliente mudar
            if hasattr(self, 'spinner_cliente_interna_origem'):
                # Remover bind anterior se existir
                try:
                    self.spinner_cliente_interna_origem.unbind(text=self.atualizar_contas_interna_origem)
                except:
                    pass
                # Adicionar novo bind
                self.spinner_cliente_interna_origem.bind(text=self.atualizar_contas_interna_origem)
            
            # 🔥 CORREÇÃO: Usar lambda para passar os argumentos corretos
            if hasattr(self, 'spinner_conta_interna_origem'):
                try:
                    self.spinner_conta_interna_origem.unbind(text=self.atualizar_filtro_destino_por_moeda)
                except:
                    pass
                self.spinner_conta_interna_origem.bind(text=lambda instance, value: self.atualizar_filtro_destino_por_moeda())

    def selecionar_invoice_admin(self):
        """Abre seletor de invoice para o admin - VERSÃO SIMPLIFICADA"""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            from kivy.uix.label import Label
            from kivy.uix.filechooser import FileChooserListView
            import os
            
            # Criar popup minimalista
            content = BoxLayout(orientation='vertical', spacing=15, padding=25)
            
            # Título amigável
            lbl_titulo = Label(
                text='[b]ANEXAR INVOICE[/b]',
                markup=True,
                color=(0.9, 0.9, 0.9, 1),
                font_size='18sp',
                size_hint_y=0.2,
                text_size=(400, None),
                halign='center'
            )
            
            # Área de Drag & Drop
            area_drag_drop = Button(
                text='[b]SOLTE O ARQUIVO AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)',
                markup=True,
                background_color=(0.2, 0.3, 0.4, 0.3),
                background_normal='',
                color=(0.8, 0.8, 0.8, 1),
                font_size='14sp',
                size_hint_y=0.4,
                halign='center'
            )
            
            # Pastas rápidas
            pastas_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
            
            btn_documentos = Button(
                text='Documentos',
                background_color=(0.3, 0.5, 0.7, 1),
                font_size='12sp'
            )
            
            btn_downloads = Button(
                text='Downloads', 
                background_color=(0.3, 0.5, 0.7, 1),
                font_size='12sp'
            )
            
            btn_desktop = Button(
                text='Desktop',
                background_color=(0.3, 0.5, 0.7, 1),
                font_size='12sp'
            )
            
            pastas_layout.add_widget(btn_documentos)
            pastas_layout.add_widget(btn_downloads)
            pastas_layout.add_widget(btn_desktop)
            
            # Botões de ação
            botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
            
            btn_limpar = Button(
                text='Limpar',
                background_color=(0.8, 0.3, 0.3, 1),
                font_size='12sp'
            )
            
            btn_fechar = Button(
                text='Concluir',
                background_color=(0.2, 0.7, 0.3, 1),
                font_size='14sp',
                bold=True
            )
            
            botoes_layout.add_widget(btn_limpar)
            botoes_layout.add_widget(btn_fechar)
            
            content.add_widget(lbl_titulo)
            content.add_widget(area_drag_drop)
            content.add_widget(pastas_layout)
            content.add_widget(botoes_layout)
            
            # Variável para armazenar arquivo selecionado
            arquivo_selecionado = None
            lbl_status = None
            
            # Criar popup
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.85, 0.6),
                background_color=(0.12, 0.16, 0.23, 1),
                auto_dismiss=False
            )
            
            def atualizar_status(nome_arquivo, sucesso=True):
                """Atualiza o status visual"""
                nonlocal lbl_status
                
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                
                if sucesso:
                    texto = f'✅ [b]{nome_arquivo}[/b]\nPronto para anexar!'
                    cor = (0.2, 0.8, 0.2, 1)
                else:
                    texto = f'❌ {nome_arquivo}'
                    cor = (1, 0.3, 0.3, 1)
                
                lbl_status = Label(
                    text=texto,
                    markup=True,
                    color=cor,
                    font_size='12sp',
                    size_hint_y=0.15,
                    text_size=(400, None),
                    halign='center'
                )
                content.add_widget(lbl_status)
                content.do_layout()
            
            def processar_arquivo(caminho):
                """Processa o arquivo selecionado"""
                nonlocal arquivo_selecionado
                
                try:
                    # Verificar se é arquivo válido
                    if not os.path.isfile(caminho):
                        return False
                    
                    # Verificar extensão
                    extensoes_validas = ['.pdf', '.jpg', '.jpeg', '.png']
                    _, ext = os.path.splitext(caminho)
                    if ext.lower() not in extensoes_validas:
                        atualizar_status(f'Tipo não suportado: {ext}', False)
                        return False
                    
                    # Verificar tamanho (5MB)
                    tamanho = os.path.getsize(caminho) / (1024 * 1024)
                    if tamanho > 5:
                        atualizar_status('Arquivo muito grande! Máx: 5MB', False)
                        return False
                    
                    arquivo_selecionado = caminho
                    nome_arquivo = os.path.basename(caminho)
                    atualizar_status(nome_arquivo, True)
                    
                    # Atualizar área visual
                    area_drag_drop.text = f'[b]✅ PRONTO![/b]\n\n{nome_arquivo}\n({tamanho:.1f} MB)'
                    area_drag_drop.background_color = (0.2, 0.5, 0.2, 0.5)
                    
                    return True
                    
                except Exception as e:
                    atualizar_status(f'Erro: {str(e)}', False)
                    return False
            
            def abrir_seletor_pasta(pasta):
                """Abre seletor em pasta específica"""
                nonlocal popup
                
                # Fechar popup atual
                popup.dismiss()
                
                # Criar novo popup com filechooser
                content_avancado = BoxLayout(orientation='vertical', spacing=10, padding=10)
                
                lbl_instrucao = Label(
                    text=f'Procurando em: {pasta}',
                    color=(0.9, 0.9, 0.9, 1),
                    font_size='14sp'
                )
                
                filechooser = FileChooserListView(
                    path=pasta,
                    filters=['*.pdf', '*.jpg', '*.jpeg', '*.png'],
                    size_hint_y=0.7
                )
                
                botoes_avancado = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
                
                btn_voltar = Button(
                    text='⬅Voltar',
                    background_color=(0.5, 0.5, 0.5, 1)
                )
                
                btn_escolher = Button(
                    text='Usar Este',
                    background_color=(0.2, 0.7, 0.3, 1)
                )
                
                botoes_avancado.add_widget(btn_voltar)
                botoes_avancado.add_widget(btn_escolher)
                
                content_avancado.add_widget(lbl_instrucao)
                content_avancado.add_widget(filechooser)
                content_avancado.add_widget(botoes_avancado)
                
                popup_avancado = Popup(
                    title='Selecione o arquivo',
                    content=content_avancado,
                    size_hint=(0.9, 0.8),
                    background_color=(0.12, 0.16, 0.23, 1),
                    auto_dismiss=False
                )
                
                def voltar_simples(instance):
                    popup_avancado.dismiss()
                    self.selecionar_invoice_admin()  # Reabre o popup simples
                
                def escolher_arquivo(instance=None, selection=None, touch=None):
                    """Função corrigida para aceitar diferentes chamadas"""
                    if filechooser.selection:
                        caminho = filechooser.selection[0]
                        if processar_arquivo(caminho):
                            popup_avancado.dismiss()
                    else:
                        lbl_instrucao.text = 'Selecione um arquivo!'
                        lbl_instrucao.color = (1, 0.3, 0.3, 1)
                
                btn_voltar.bind(on_press=voltar_simples)
                btn_escolher.bind(on_press=escolher_arquivo)
                
                # Usar lambda para evitar problemas de argumentos
                filechooser.bind(on_submit=lambda instance, value, touch: escolher_arquivo())
                
                popup_avancado.open()
            
            def abrir_seletor_generico(instance):
                """Abre seletor de arquivos genérico"""
                abrir_seletor_pasta(os.path.expanduser('~'))
            
            def limpar_selecao(instance):
                """Limpa a seleção atual"""
                nonlocal arquivo_selecionado
                arquivo_selecionado = None
                area_drag_drop.text = '[b]SOLTE O ARQUIVO AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)'
                area_drag_drop.background_color = (0.2, 0.3, 0.4, 0.3)
                
                # Remover status
                nonlocal lbl_status
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                    content.do_layout()
            
            def finalizar(instance):
                """Finaliza o processo"""
                if arquivo_selecionado:
                    self.processar_arquivo_selecionado_admin(arquivo_selecionado)
                    popup.dismiss()
                    self.mostrar_mensagem_sucesso_admin("Invoice anexado com sucesso!")
                else:
                    atualizar_status("Nenhum arquivo selecionado!", False)
            
            # Bind dos eventos
            area_drag_drop.bind(on_press=abrir_seletor_generico)
            btn_documentos.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Documents')))
            btn_downloads.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Downloads')))
            btn_desktop.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Desktop')))
            btn_limpar.bind(on_press=limpar_selecao)
            btn_fechar.bind(on_press=finalizar)
            
            # Suporte a drag & drop real
            def on_drop_file(window, file_path, x, y):
                """Processa arquivo arrastado para a janela"""
                try:
                    file_path_str = file_path.decode('utf-8') if isinstance(file_path, bytes) else str(file_path)
                    if processar_arquivo(file_path_str):
                        print(f"✅ Arquivo arrastado processado: {file_path_str}")
                except Exception as e:
                    print(f"❌ Erro ao processar arquivo arrastado: {e}")
            
            # Registrar evento de drop
            from kivy.core.window import Window
            Window.bind(on_drop_file=on_drop_file)
            
            # Limpar binding quando popup fechar
            def on_dismiss(instance):
                Window.unbind(on_drop_file=on_drop_file)
            
            popup.bind(on_dismiss=on_dismiss)
            
            # Abrir popup
            popup.open()
            
        except Exception as e:
            print(f"❌ Erro ao abrir seletor de arquivos: {e}")
            self.mostrar_erro_simples_admin("Erro ao abrir seletor de arquivos")

    def processar_arquivo_selecionado_admin(self, caminho_arquivo):
        """Processa o arquivo de invoice selecionado para o admin"""
        try:
            import os
            
            # Verificar tamanho do arquivo (máx 5MB)
            tamanho_arquivo = os.path.getsize(caminho_arquivo) / (1024 * 1024)  # MB
            if tamanho_arquivo > 5:
                self.mostrar_erro_simples_admin("Arquivo muito grande! Escolha um arquivo menor que 5MB.")
                return
            
            # Obter nome do arquivo
            nome_arquivo = os.path.basename(caminho_arquivo)
            
            # Atualizar interface
            self.lbl_arquivo_invoice_modal.text = f"📎 {nome_arquivo} ({tamanho_arquivo:.1f} MB)"
            self.lbl_arquivo_invoice_modal.color = (0.2, 0.8, 0.2, 1)  # Verde
            self.arquivo_invoice_selecionado_admin = caminho_arquivo
            
            print(f"✅ Invoice selecionado (admin): {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo (admin): {e}")
            self.mostrar_erro_simples_admin("Erro ao processar arquivo. Tente novamente.")

    def mostrar_mensagem_sucesso_admin(self, mensagem):
        """Mostra mensagem de sucesso simples para o admin"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl = Label(
            text=mensagem, 
            color=(0.2, 0.8, 0.2, 1), 
            font_size='16sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        content.add_widget(lbl)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        def fechar_popup(instance):
            popup.dismiss()
        
        btn_ok.bind(on_press=fechar_popup)
        popup.open()

    def mostrar_erro_simples_admin(self, mensagem):
        """Mostra mensagem de erro simples para o admin"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20)
        lbl = Label(text=mensagem, color=(1, 0.3, 0.3, 1), font_size='16sp')
        content.add_widget(lbl)
        
        popup = Popup(
            title='❌ Erro',
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=True,
            background_color=(0.12, 0.16, 0.23, 1)
        )
        popup.open()

    def atualizar_destino_transferencia_interna(self, instance=None, value=None):
        """Atualiza campos de destino para transferência interna - VERSÃO 2 COLUNAS"""
        if not hasattr(self, 'container_destino_dinamica'):
            return
        
        container = self.container_destino_dinamica
        container.clear_widgets()
        container.height = 0
        
        tipo_destino = self.spinner_tipo_destino.text
        
        # 🔥 CORREÇÃO: Só criar campos se não for a opção de seleção
        if tipo_destino == 'Selecione o tipo de destino':
            # Não mostrar nada - aguardar seleção do usuário
            return
            
        elif tipo_destino == 'Conta Bancária da Empresa':
            # Contas bancárias da empresa
            layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            layout.add_widget(Label(
                text='Conta Bancária Destino *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_conta_empresa_destino = Spinner(
                text='Selecione a conta',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            layout.add_widget(self.spinner_conta_empresa_destino)
            container.add_widget(layout)
            container.height += 80
            
            # Carregar contas da empresa
            self.carregar_contas_empresa_destino()
            
        else:  # Conta de Cliente
            # Cliente
            cliente_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            cliente_layout.add_widget(Label(
                text='Cliente Destino *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_cliente_interna_destino = Spinner(
                text='Selecione o cliente',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            cliente_layout.add_widget(self.spinner_cliente_interna_destino)
            container.add_widget(cliente_layout)
            
            # Conta do Cliente
            conta_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            conta_layout.add_widget(Label(
                text='Conta do Cliente *',
                font_size='13sp',
                bold=True,
                color=(0.7, 0.8, 1, 1),
                size_hint_y=0.4,
                text_size=(None, None),
                halign='left'
            ))
            
            self.spinner_conta_interna_destino = Spinner(
                text='Selecione a conta',
                font_size='13sp',
                size_hint_y=0.6,
                background_color=(0.20, 0.25, 0.33, 1),
                color=(1, 1, 1, 1)
            )
            conta_layout.add_widget(self.spinner_conta_interna_destino)
            container.add_widget(conta_layout)
            
            container.height += 160
            
            # Carregar clientes imediatamente
            self.carregar_clientes_transferencia_interna_destino()
            
            # Bind para atualizar contas quando cliente mudar
            if hasattr(self, 'spinner_cliente_interna_destino'):
                # Remover bind anterior se existir
                try:
                    self.spinner_cliente_interna_destino.unbind(text=self.atualizar_contas_interna_destino)
                except:
                    pass
                # Adicionar novo bind
                self.spinner_cliente_interna_destino.bind(text=self.atualizar_contas_interna_destino)
            
            # 🔥 CORREÇÃO: Usar lambda para passar os argumentos corretos
            if hasattr(self, 'spinner_cliente_interna_destino'):
                try:
                    self.spinner_cliente_interna_destino.unbind(text=self.atualizar_filtro_destino_por_moeda)
                except:
                    pass
                self.spinner_cliente_interna_destino.bind(text=lambda instance, value: self.atualizar_filtro_destino_por_moeda())

    def carregar_contas_empresa_origem(self):
        """Carrega contas da empresa para origem"""
        sistema = App.get_running_app().sistema
        
        opcoes_contas = []
        for conta_num, dados_conta in sistema.contas_bancarias_empresa.items():
            opcoes_contas.append(f"{conta_num} - {dados_conta['banco']} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
        
        if hasattr(self, 'spinner_conta_empresa_origem'):
            self.spinner_conta_empresa_origem.values = opcoes_contas
            if opcoes_contas:
                self.spinner_conta_empresa_origem.text = opcoes_contas[0]

    def carregar_contas_empresa_destino(self):
        """Carrega contas da empresa para destino - VERSÃO CORRIGIDA PARA 2 COLUNAS"""
        sistema = App.get_running_app().sistema
        
        opcoes_contas = []
        for conta_num, dados_conta in sistema.contas_bancarias_empresa.items():
            opcoes_contas.append(f"{conta_num} - {dados_conta['banco']} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
        
        # 🔥 CORREÇÃO: Usar o spinner diretamente
        if hasattr(self, 'spinner_conta_empresa_destino'):
            self.spinner_conta_empresa_destino.values = opcoes_contas
            if opcoes_contas:
                self.spinner_conta_empresa_destino.text = opcoes_contas[0]

    def carregar_clientes_transferencia_interna_origem(self):
        """Carrega clientes para origem da transferência interna - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = []
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        if hasattr(self, 'spinner_cliente_interna_origem'):
            self.spinner_cliente_interna_origem.values = clientes_opcoes
            if clientes_opcoes:
                self.spinner_cliente_interna_origem.text = clientes_opcoes[0]
                # 🔥 FORÇAR atualização das contas imediatamente
                self.atualizar_contas_interna_origem(None, clientes_opcoes[0])

    def carregar_clientes_transferencia_interna_destino(self):
        """Carrega clientes para destino da transferência interna - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = []
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        if hasattr(self, 'spinner_cliente_interna_destino'):
            self.spinner_cliente_interna_destino.values = clientes_opcoes
            if clientes_opcoes:
                self.spinner_cliente_interna_destino.text = clientes_opcoes[0]
                # 🔥 FORÇAR atualização das contas imediatamente
                self.atualizar_contas_interna_destino(None, clientes_opcoes[0])

    def atualizar_contas_interna_origem(self, instance, value):
        """Atualiza contas quando cliente origem é selecionado na transferência interna - COM FILTRO DE MOEDA"""
        sistema = App.get_running_app().sistema
        
        if not value or value == 'Selecione o cliente':
            return
        
        username = value.split(' - ')[0]
        
        if username in sistema.usuarios:
            contas_cliente = []
            for conta_num in sistema.usuarios[username].get('contas', []):
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    contas_cliente.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            # Atualizar spinner de contas
            if hasattr(self, 'spinner_conta_interna_origem'):
                self.spinner_conta_interna_origem.values = contas_cliente
                if contas_cliente:
                    self.spinner_conta_interna_origem.text = contas_cliente[0]
                    # 🔥 ATUALIZAR FILTRO DE DESTINO BASEADO NA MOEDA SELECIONADA
                    self.atualizar_filtro_destino_por_moeda()
                else:
                    self.spinner_conta_interna_origem.text = 'Nenhuma conta disponível'

    def atualizar_filtro_destino_por_moeda(self, instance=None, value=None):
        """Filtra as contas destino baseado na moeda da conta origem selecionada - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        # 🔥 OBTER MOEDA DA CONTA ORIGEM
        moeda_origem = None
        
        # Verificar se origem é conta bancária da empresa
        if (hasattr(self, 'spinner_tipo_origem') and 
            self.spinner_tipo_origem.text == 'Conta Bancária da Empresa' and
            hasattr(self, 'spinner_conta_empresa_origem') and
            'Selecione' not in self.spinner_conta_empresa_origem.text):
            
            conta_origem_num = self.spinner_conta_empresa_origem.text.split(' - ')[0]
            if conta_origem_num in sistema.contas_bancarias_empresa:
                moeda_origem = sistema.contas_bancarias_empresa[conta_origem_num]['moeda']
        
        # Verificar se origem é conta de cliente
        elif (hasattr(self, 'spinner_tipo_origem') and 
              self.spinner_tipo_origem.text == 'Conta de Cliente' and
              hasattr(self, 'spinner_conta_interna_origem') and
              'Selecione' not in self.spinner_conta_interna_origem.text):
            
            conta_origem_num = self.spinner_conta_interna_origem.text.split(' - ')[0]
            if conta_origem_num in sistema.contas:
                moeda_origem = sistema.contas[conta_origem_num]['moeda']
        
        if not moeda_origem:
            return
        
        print(f"🎯 Filtrando destino por moeda: {moeda_origem}")
        
        # 🔥 APLICAR FILTRO NO DESTINO
        # Se destino for conta bancária da empresa
        if (hasattr(self, 'spinner_tipo_destino') and 
            self.spinner_tipo_destino.text == 'Conta Bancária da Empresa' and
            hasattr(self, 'spinner_conta_empresa_destino')):
            
            contas_filtradas = []
            for conta_num, dados_conta in sistema.contas_bancarias_empresa.items():
                if dados_conta['moeda'] == moeda_origem:
                    contas_filtradas.append(f"{conta_num} - {dados_conta['banco']} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            self.spinner_conta_empresa_destino.values = contas_filtradas
            if contas_filtradas:
                self.spinner_conta_empresa_destino.text = contas_filtradas[0]
            else:
                self.spinner_conta_empresa_destino.text = f'Nenhuma conta {moeda_origem} disponível'
        
        # Se destino for conta de cliente
        elif (hasattr(self, 'spinner_tipo_destino') and 
              self.spinner_tipo_destino.text == 'Conta de Cliente' and
              hasattr(self, 'spinner_cliente_interna_destino') and
              hasattr(self, 'spinner_conta_interna_destino') and
              'Selecione' not in self.spinner_cliente_interna_destino.text):
            
            username_destino = self.spinner_cliente_interna_destino.text.split(' - ')[0]
            if username_destino in sistema.usuarios:
                contas_filtradas = []
                for conta_num in sistema.usuarios[username_destino].get('contas', []):
                    if conta_num in sistema.contas and sistema.contas[conta_num]['moeda'] == moeda_origem:
                        dados_conta = sistema.contas[conta_num]
                        contas_filtradas.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
                
                self.spinner_conta_interna_destino.values = contas_filtradas
                if contas_filtradas:
                    self.spinner_conta_interna_destino.text = contas_filtradas[0]
                else:
                    self.spinner_conta_interna_destino.text = f'Nenhuma conta {moeda_origem} disponível'

    def atualizar_contas_interna_destino(self, instance, value):
        """Atualiza contas quando cliente destino é selecionado na transferência interna - COM FILTRO DE MOEDA"""
        sistema = App.get_running_app().sistema
        
        if not value or value == 'Selecione o cliente':
            return
        
        username = value.split(' - ')[0]
        
        if username in sistema.usuarios:
            # 🔥 OBTER MOEDA DA CONTA ORIGEM PARA FILTRAR
            moeda_origem = self.obter_moeda_origem()
            
            contas_cliente = []
            for conta_num in sistema.usuarios[username].get('contas', []):
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    # 🔥 FILTRAR POR MOEDA SE ORIGEM JÁ FOI SELECIONADA
                    if moeda_origem and dados_conta['moeda'] != moeda_origem:
                        continue
                    contas_cliente.append(f"{conta_num} - {dados_conta['moeda']} - Saldo: {dados_conta['saldo']:,.2f}")
            
            # Atualizar spinner de contas
            if hasattr(self, 'spinner_conta_interna_destino'):
                self.spinner_conta_interna_destino.values = contas_cliente
                if contas_cliente:
                    self.spinner_conta_interna_destino.text = contas_cliente[0]
                else:
                    if moeda_origem:
                        self.spinner_conta_interna_destino.text = f'Nenhuma conta {moeda_origem} disponível'
                    else:
                        self.spinner_conta_interna_destino.text = 'Nenhuma conta disponível'

    def obter_moeda_origem(self):
        """Obtém a moeda da conta origem selecionada"""
        sistema = App.get_running_app().sistema
        
        # Verificar se origem é conta bancária da empresa
        if (hasattr(self, 'spinner_tipo_origem') and 
            self.spinner_tipo_origem.text == 'Conta Bancária da Empresa' and
            hasattr(self, 'spinner_conta_empresa_origem') and
            'Selecione' not in self.spinner_conta_empresa_origem.text):
            
            conta_origem_num = self.spinner_conta_empresa_origem.text.split(' - ')[0]
            if conta_origem_num in sistema.contas_bancarias_empresa:
                return sistema.contas_bancarias_empresa[conta_origem_num]['moeda']
        
        # Verificar se origem é conta de cliente
        elif (hasattr(self, 'spinner_tipo_origem') and 
              self.spinner_tipo_origem.text == 'Conta de Cliente' and
              hasattr(self, 'spinner_conta_interna_origem') and
              'Selecione' not in self.spinner_conta_interna_origem.text):
            
            conta_origem_num = self.spinner_conta_interna_origem.text.split(' - ')[0]
            if conta_origem_num in sistema.contas:
                return sistema.contas[conta_origem_num]['moeda']
        
        return None


    def limpar_campos_transferencia(self):
        """Limpa todos os campos da aba transferências - VERSÃO 2 COLUNAS"""
        if hasattr(self, 'ids'):
            # Limpar campos de valor e descrição
            if 'entry_valor_transferencia_interna' in self.ids:
                self.ids.entry_valor_transferencia_interna.text = ''
            
            if 'entry_descricao_transferencia_interna' in self.ids:
                self.ids.entry_descricao_transferencia_interna.text = ''
            
            # Limpar containers das colunas
            if hasattr(self, 'container_origem_dinamica'):
                self.container_origem_dinamica.clear_widgets()
                self.container_origem_dinamica.height = 0
            
            if hasattr(self, 'container_destino_dinamica'):
                self.container_destino_dinamica.clear_widgets()
                self.container_destino_dinamica.height = 0
            
            # Limpar spinners principais (mas manter o tipo de transferência)
            if hasattr(self, 'spinner_tipo_origem'):
                self.spinner_tipo_origem.text = 'Selecione o tipo de origem'
            
            if hasattr(self, 'spinner_tipo_destino'):
                self.spinner_tipo_destino.text = 'Selecione o tipo de destino'
            
            print("✅ Campos de transferência limpos com sucesso!")

    def executar_transferencia_interna_admin(self):
        """Executa transferência interna como admin - COM VALIDAÇÃO COMPLETA"""
        sistema = App.get_running_app().sistema
        
        print("🔄 Executando transferência interna...")
        
        try:
            # 🔥 DEBUG: Verificar se os IDs estão disponíveis
            print(f"🔍 DEBUG IDs disponíveis: {list(self.ids.keys())}")
            
            # Validar campos básicos
            if not hasattr(self, 'spinner_tipo_origem') or self.spinner_tipo_origem.text == 'Selecione o tipo de origem':
                self.mostrar_erro("Selecione o tipo de origem!")
                return
                
            if not hasattr(self, 'spinner_tipo_destino') or self.spinner_tipo_destino.text == 'Selecione o tipo de destino':
                self.mostrar_erro("Selecione o tipo de destino!")
                return
            
            # 🔥 INICIALIZAR VARIÁVEIS
            conta_origem_num = None
            moeda_origem = None
            saldo_origem = 0
            
            conta_destino_num = None
            moeda_destino = None
            
            # 🔥 OBTER INFORMAÇÕES DA CONTA ORIGEM
            if self.spinner_tipo_origem.text == 'Conta Bancária da Empresa':
                if not hasattr(self, 'spinner_conta_empresa_origem') or 'Selecione' in self.spinner_conta_empresa_origem.text:
                    self.mostrar_erro("Selecione uma conta de origem!")
                    return
                
                conta_origem_num = self.spinner_conta_empresa_origem.text.split(' - ')[0]
                if conta_origem_num in sistema.contas_bancarias_empresa:
                    moeda_origem = sistema.contas_bancarias_empresa[conta_origem_num]['moeda']
                    saldo_origem = sistema.contas_bancarias_empresa[conta_origem_num]['saldo']
                else:
                    self.mostrar_erro("Conta de origem não encontrada!")
                    return
                    
            else:  # Conta de Cliente
                if not hasattr(self, 'spinner_conta_interna_origem') or 'Selecione' in self.spinner_conta_interna_origem.text:
                    self.mostrar_erro("Selecione uma conta de origem!")
                    return
                
                conta_origem_num = self.spinner_conta_interna_origem.text.split(' - ')[0]
                if conta_origem_num in sistema.contas:
                    moeda_origem = sistema.contas[conta_origem_num]['moeda']
                    saldo_origem = sistema.contas[conta_origem_num]['saldo']
                else:
                    self.mostrar_erro("Conta de origem não encontrada!")
                    return
            
            # 🔥 OBTER INFORMAÇÕES DA CONTA DESTINO
            if self.spinner_tipo_destino.text == 'Conta Bancária da Empresa':
                if not hasattr(self, 'spinner_conta_empresa_destino') or 'Selecione' in self.spinner_conta_empresa_destino.text:
                    self.mostrar_erro("Selecione uma conta de destino!")
                    return
                
                conta_destino_num = self.spinner_conta_empresa_destino.text.split(' - ')[0]
                if conta_destino_num in sistema.contas_bancarias_empresa:
                    moeda_destino = sistema.contas_bancarias_empresa[conta_destino_num]['moeda']
                else:
                    self.mostrar_erro("Conta de destino não encontrada!")
                    return
                    
            else:  # Conta de Cliente
                if not hasattr(self, 'spinner_conta_interna_destino') or 'Selecione' in self.spinner_conta_interna_destino.text:
                    self.mostrar_erro("Selecione uma conta de destino!")
                    return
                
                conta_destino_num = self.spinner_conta_interna_destino.text.split(' - ')[0]
                if conta_destino_num in sistema.contas:
                    moeda_destino = sistema.contas[conta_destino_num]['moeda']
                else:
                    self.mostrar_erro("Conta de destino não encontrada!")
                    return
            
            # 🔥 VALIDAÇÃO CRÍTICA: MOEDAS DEVEM SER IGUAIS
            if moeda_origem != moeda_destino:
                self.mostrar_erro(
                    f"❌ Moedas diferentes!\n\n"
                    f"Origem: {moeda_origem}\n"
                    f"Destino: {moeda_destino}\n\n"
                    f"Transferências internas só podem ser feitas entre contas da mesma moeda."
                )
                return
            
            # 🔥 VALIDAR QUE NÃO É A MESMA CONTA
            if conta_origem_num == conta_destino_num:
                self.mostrar_erro("Conta origem e destino não podem ser a mesma!")
                return
            
            # 🔥 CORREÇÃO: ACESSAR PELOS IDs
            if 'entry_valor_transferencia_interna' not in self.ids:
                self.mostrar_erro("Erro interno: campo de valor não encontrado!")
                return
            
            valor_text = self.ids.entry_valor_transferencia_interna.text
            print(f"🔍 DEBUG: Valor digitado = '{valor_text}'")
            
            # Validar valor
            if not valor_text or not valor_text.strip():
                self.mostrar_erro("Digite o valor da transferência!")
                return
            
            # 🔥 CORREÇÃO: ACESSAR DESCRIÇÃO PELOS IDs
            if 'entry_descricao_transferencia_interna' not in self.ids:
                self.mostrar_erro("Erro interno: campo de descrição não encontrado!")
                return
            
            descricao_text = self.ids.entry_descricao_transferencia_interna.text.strip()
            
            # Validar descrição
            if not descricao_text:
                self.mostrar_erro("Digite uma descrição para a transferência!")
                return
            
            # 🔥 OBTER E VALIDAR VALOR
            try:
                valor = self._parse_valor_br(valor_text)
                
                if valor <= 0:
                    self.mostrar_erro("Valor deve ser maior que zero!")
                    return
                    
            except ValueError as e:
                self.mostrar_erro(f"Valor inválido! {str(e)}")
                return

            # 🔥 DETERMINAR TIPO DE TRANSFERÊNCIA PARA CALCULAR SALDO CORRETO
            origem_empresa = conta_origem_num in sistema.contas_bancarias_empresa
            destino_empresa = conta_destino_num in sistema.contas_bancarias_empresa
            origem_cliente = conta_origem_num in sistema.contas
            destino_cliente = conta_destino_num in sistema.contas

            # 🔥 CALCULAR SALDO APÓS OPERAÇÃO COM A LÓGICA INVERTIDA
            if origem_cliente and destino_empresa:
                # Cliente → Empresa: Cliente GANHA dinheiro (CRÉDITO)
                saldo_apos_operacao = saldo_origem + valor
                tipo_operacao = "CRÉDITO (cliente ganha)"
                efeito = "+"
                
            elif origem_empresa and destino_cliente:
                # Empresa → Cliente: Cliente PERDE dinheiro (DÉBITO)
                saldo_apos_operacao = saldo_origem - valor
                tipo_operacao = "DÉBITO (cliente perde)"
                efeito = "-"
                
            else:
                # Outras combinações (empresa→empresa, cliente→cliente) - sem inversão
                saldo_apos_operacao = saldo_origem - valor
                tipo_operacao = "DÉBITO (padrão)"
                efeito = "-"

            # 🔥 VERIFICAR SE FICARÁ NEGATIVO (APENAS PARA CLIENTE ORIGEM)
            ficara_negativo = (origem_cliente and saldo_apos_operacao < 0)

            # 🔥 VALIDAÇÃO DE SALDO (MODIFICADA PARA PERMITIR NEGATIVO COM ALERTA)
            if ficara_negativo:
                # Cliente ficará com saldo negativo - mostra alerta especial
                self.mostrar_confirmacao_saldo_negativo(
                    f"⚠️ ATENÇÃO: CONTA DO CLIENTE FICARÁ NEGATIVA!\n\n"
                    f"Conta: {conta_origem_num}\n"
                    f"Tipo: {'Cliente' if origem_cliente else 'Empresa'} → {'Empresa' if destino_empresa else 'Cliente'}\n"
                    f"Efeito no saldo: {tipo_operacao}\n"
                    f"Saldo atual: {saldo_origem:,.2f} {moeda_origem}\n"
                    f"Valor da transferência: {valor:,.2f} {moeda_origem}\n"
                    f"Saldo após operação: {saldo_apos_operacao:,.2f} {moeda_origem} {efeito}{valor:,.2f}\n\n"
                    f"⚠️ O saldo ficará NEGATIVO em {abs(saldo_apos_operacao):,.2f} {moeda_origem}!\n"
                    f"Deseja continuar mesmo assim?",
                    lambda: self._processar_transferencia_interna(conta_origem_num, conta_destino_num, valor, moeda_origem, descricao_text)
                )
            else:
                # Saldo suficiente ou não afeta cliente - mostra confirmação normal
                self.mostrar_confirmacao(
                    "Confirmar Transferência Interna?",
                    f"Origem: {conta_origem_num} ({'Cliente' if origem_cliente else 'Empresa'})\n"
                    f"Destino: {conta_destino_num} ({'Cliente' if destino_cliente else 'Empresa'})\n"
                    f"Valor: {valor:,.2f} {moeda_origem}\n"
                    f"Descrição: {descricao_text}\n\n"
                    f"📊 INFORMAÇÕES DA OPERAÇÃO:\n"
                    f"Tipo: {tipo_operacao}\n"
                    f"Saldo atual: {saldo_origem:,.2f} {moeda_origem}\n"
                    f"Saldo após: {saldo_apos_operacao:,.2f} {moeda_origem} ({efeito}{valor:,.2f})\n\n"
                    f"✅ Saldo ficará {'POSITIVO' if saldo_apos_operacao >= 0 else 'NEGATIVO, MAS AUTORIZADO'}",
                    lambda: self._processar_transferencia_interna(conta_origem_num, conta_destino_num, valor, moeda_origem, descricao_text)
                )
            
        except Exception as e:
            print(f"❌ Erro na transferência interna: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao processar transferência: {str(e)}")

    def _processar_transferencia_interna(self, conta_origem, conta_destino, valor, moeda, descricao):
        """Processa a transferência interna após confirmação - COM SUPABASE COMPLETO"""
        sistema = App.get_running_app().sistema
        
        try:
            print(f"🔄 Processando transferência interna: {conta_origem} -> {conta_destino} | {valor} {moeda}")
            
            # 🔥 VERIFICAR TIPOS DE CONTAS
            origem_empresa = conta_origem in sistema.contas_bancarias_empresa
            destino_empresa = conta_destino in sistema.contas_bancarias_empresa
            
            origem_cliente = conta_origem in sistema.contas
            destino_cliente = conta_destino in sistema.contas
            
            # 🔥 EXECUTAR TRANSFERÊNCIA LOCAL - VERSÃO INVERTIDA
            if origem_empresa and destino_empresa:
                # Entre contas da empresa
                sistema.contas_bancarias_empresa[conta_origem]['saldo'] -= valor
                sistema.contas_bancarias_empresa[conta_destino]['saldo'] += valor
                print(f"✅ Transferência entre contas empresa: -{valor} {moeda} em {conta_origem}, +{valor} {moeda} em {conta_destino}")
                
            elif origem_empresa and destino_cliente:
                # 🔥 INVERTIDO: Da empresa para cliente - AGORA CLIENTE PERDE DINHEIRO (DÉBITO)
                sistema.contas_bancarias_empresa[conta_origem]['saldo'] -= valor  # Empresa perde (ok)
                sistema.contas[conta_destino]['saldo'] -= valor  # 🔥 ALTERADO: Cliente PERDE dinheiro (antes era +=)
                print(f"✅ Transferência empresa->cliente (INVERTIDA): -{valor} {moeda} em {conta_origem}, -{valor} {moeda} em {conta_destino}")
                
            elif origem_cliente and destino_empresa:
                # 🔥 INVERTIDO: Cliente → Empresa - AMBOS GANHAM (crédito para ambos)
                sistema.contas[conta_origem]['saldo'] += valor
                sistema.contas_bancarias_empresa[conta_destino]['saldo'] += valor
                print(f"✅ Transferência cliente->empresa: Cliente +{valor}, Empresa +{valor}")
                
            elif origem_cliente and destino_cliente:
                # Entre clientes (mantém igual)
                sistema.contas[conta_origem]['saldo'] -= valor
                sistema.contas[conta_destino]['saldo'] += valor
                print(f"✅ Transferência entre clientes: -{valor} {moeda} em {conta_origem}, +{valor} {moeda} em {conta_destino}")
            else:
                raise ValueError("Combinação de contas inválida")
            
            # 🔥 REGISTRAR A TRANSFERÊNCIA LOCAL
            import random
            transferencia_id = str(random.randint(100000, 999999))
            while transferencia_id in sistema.transferencias:
                transferencia_id = str(random.randint(100000, 999999))
            
            # Determinar tipo baseado nas contas envolvidas
            if origem_empresa and destino_empresa:
                tipo = 'transferencia_interna_empresa'
            elif origem_empresa and destino_cliente:
                tipo = 'transferencia_empresa_cliente'
            elif origem_cliente and destino_empresa:
                tipo = 'transferencia_cliente_empresa'
            else:
                tipo = 'transferencia_interna_cliente'
            
            sistema.transferencias[transferencia_id] = {
                'id': transferencia_id,
                'conta_remetente': conta_origem,
                'conta_destinatario': conta_destino,
                'valor': valor,
                'moeda': moeda,
                'tipo': tipo,
                'descricao': descricao,
                'status': 'completed',
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'executado_por': sistema.usuario_logado,
                'tipo_operacao': 'transferencia_interna_admin'
            }
            
            # 🔥 ATUALIZAR SALDOS NO SUPABASE
            sucesso_saldos = self._atualizar_saldos_supabase(conta_origem, conta_destino, valor, moeda, origem_empresa, destino_empresa)
            
            # 🔥 SALVAR TRANSFERÊNCIA NO SUPABASE
            sucesso_transferencia = self.salvar_transferencia_interna_supabase(
                transferencia_id, conta_origem, conta_destino, valor, moeda, 
                tipo, descricao, origem_empresa, destino_empresa
            )
            
            if sucesso_transferencia and sucesso_saldos:
                print(f"🎉 TRANSFERÊNCIA {transferencia_id} COMPLETAMENTE SINCRONIZADA NO SUPABASE!")
            elif sucesso_transferencia:
                print(f"✅ Transferência {transferencia_id} salva no Supabase, mas saldos não atualizados")
            elif sucesso_saldos:
                print(f"✅ Saldos atualizados no Supabase, mas transferência não salva")
            else:
                print(f"⚠️ Transferência salva apenas localmente")
            
            # 🔥 SALVAR DADOS LOCAIS
            sistema.salvar_contas()
            sistema.salvar_contas_bancarias()
            sistema.salvar_transferencias()
            
            # 🔥 OBTER NOVOS SALDOS PARA MENSAGEM
            if origem_empresa:
                novo_saldo_origem = sistema.contas_bancarias_empresa[conta_origem]['saldo']
            else:
                novo_saldo_origem = sistema.contas[conta_origem]['saldo']
                
            if destino_empresa:
                novo_saldo_destino = sistema.contas_bancarias_empresa[conta_destino]['saldo']
            else:
                novo_saldo_destino = sistema.contas[conta_destino]['saldo']
            
            # 🔥 LIMPAR CAMPOS APÓS SUCESSO
            self.limpar_campos_transferencia()
            
            self.mostrar_sucesso(
                f"Transferência interna realizada!\n\n"
                f"ID: {transferencia_id}\n"
                f"Origem: {conta_origem}\n"
                f"Destino: {conta_destino}\n"
                f"Valor: {valor:,.2f} {moeda}\n"
                f"Descrição: {descricao}\n\n"
                f"Novo saldo origem: {novo_saldo_origem:,.2f} {moeda}\n"
                f"Novo saldo destino: {novo_saldo_destino:,.2f} {moeda}"
            )
            
        except Exception as e:
            print(f"❌ Erro ao processar transferência: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao processar transferência: {str(e)}")

    def mostrar_confirmacao_saldo_negativo(self, mensagem, callback):
        """Mostra popup de confirmação para saldo negativo"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', spacing=20, padding=25)
        
        # Título com ícone de alerta
        lbl_titulo = Label(
            text='⚠️ ALERTA DE SALDO NEGATIVO ⚠️',
            font_size='18sp',
            bold=True,
            color=(1, 0.8, 0.2, 1),  # Amarelo
            size_hint_y=None,
            height=50,
            text_size=(500, None),
            halign='center'
        )
        
        # Mensagem
        lbl_mensagem = Label(
            text=mensagem,
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=150,
            text_size=(500, None),
            halign='left',
            valign='top'
        )
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=15)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        btn_continuar = Button(
            text='CONTINUAR MESMO ASSIM',
            background_color=(1, 0.5, 0, 1),  # Laranja para chamar atenção
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_continuar)
        
        # Adicionar tudo ao conteúdo
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_mensagem)
        content.add_widget(botoes_layout)
        
        # Ajustar altura dinâmica
        content.bind(minimum_height=content.setter('height'))
        
        # Criar popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, None),
            height=350,
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def continuar(instance):
            popup.dismiss()
            callback()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_continuar.bind(on_press=continuar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    def executar_transferencia_internacional_admin(self):
        """Executa transferência internacional como admin"""
        # TODO: Implementar lógica completa
        self.mostrar_sucesso("Transferência Internacional - Em desenvolvimento")

    

    def configurar_bindings_taxas(self):
        """Configura os bindings dos campos de taxa - VERSÃO LIMPA"""
        try:
            if hasattr(self, 'ids'):
                if 'entry_taxa_principal' in self.ids:
                    self.entry_taxa_principal = self.ids.entry_taxa_principal
                    self.entry_taxa_principal.bind(text=self.calcular_taxa_inversa)
                
                if 'entry_taxa_inversa' in self.ids:
                    self.entry_taxa_inversa = self.ids.entry_taxa_inversa
                    self.entry_taxa_inversa.bind(text=self.calcular_taxa_principal)
        except Exception:
            pass  # Falha silenciosa

    def criar_campos_taxa_bidirecional(self):
        """Cria os campos de taxa bidirecional com cálculo automático - VERSÃO FLEXÍVEL"""
        print("🎯 CRIAR_CAMPOS_TAXA_BIDIRECIONAL CHAMADO!")
        
        # Layout principal
        layout_principal = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        
        # Título
        lbl_titulo = Label(
            text='TAXAS DE CÂMBIO - SISTEMA FLEXÍVEL',
            font_size='12sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='center'
        )
        layout_principal.add_widget(lbl_titulo)
        
        # Container para as taxas
        layout_taxas = BoxLayout(orientation='horizontal', size_hint_y=0.8, spacing=10, padding=[5, 5, 5, 5])
        
        # Taxa Principal
        box_taxa_principal = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        lbl_taxa_principal = Label(
            text='Taxa Principal *',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        box_taxa_principal.add_widget(lbl_taxa_principal)
        
        lbl_explicacao_principal = Label(
            text='Digite a taxa que conhece',
            font_size='11sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='center'
        )
        box_taxa_principal.add_widget(lbl_explicacao_principal)
        
        self.entry_taxa_principal = TextInputTaxaCambio(
            hint_text='ex: 5.10',
            font_size='13sp',
            size_hint_y=0.5,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[8, 8]
        )
        self.entry_taxa_principal.bind(text=self.calcular_taxa_inversa)
        box_taxa_principal.add_widget(self.entry_taxa_principal)
        
        # Botão de Troca
        box_troca = BoxLayout(orientation='vertical', size_hint_x=0.2)
        
        box_troca.add_widget(Label(text='', size_hint_y=0.3))
        
        btn_trocar = Button(
            text='<=>',
            font_size='16sp',
            bold=True,
            size_hint_y=0.4,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_trocar.bind(on_press=self.trocar_taxas)
        box_troca.add_widget(btn_trocar)
        
        box_troca.add_widget(Label(
            text='Trocar', 
            font_size='15sp', 
            color=(0.80, 0.84, 0.88, 1), 
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        ))
        
        # Taxa Inversa
        box_taxa_inversa = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        lbl_taxa_inversa = Label(
            text='Taxa Inversa *',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        box_taxa_inversa.add_widget(lbl_taxa_inversa)
        
        lbl_explicacao_inversa = Label(
            text='Calculada automaticamente',
            font_size='11sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=0.2,
            text_size=(None, None),
            halign='center'
        )
        box_taxa_inversa.add_widget(lbl_explicacao_inversa)
        
        self.entry_taxa_inversa = TextInputTaxaCambio(
            hint_text='0.196078',
            font_size='13sp',
            size_hint_y=0.5,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[8, 8]
        )
        self.entry_taxa_inversa.bind(text=self.calcular_taxa_principal)
        box_taxa_inversa.add_widget(self.entry_taxa_inversa)
        
        # Adicionar tudo ao layout
        layout_taxas.add_widget(box_taxa_principal)
        layout_taxas.add_widget(box_troca)
        layout_taxas.add_widget(box_taxa_inversa)
        
        layout_principal.add_widget(layout_taxas)

        
        return layout_principal

    def calcular_taxa_inversa(self, instance, value):
        """Calcula a taxa inversa automaticamente com ALTA PRECISÃO"""
        if not value or value == '.' or value == ',':
            return
            
        try:
            # Converter para float com alta precisão
            taxa_principal = float(value.replace(',', '.'))
            
            if taxa_principal > 0:
                # 🔥 CÁLCULO COM MÁXIMA PRECISÃO
                taxa_inversa = 1.0 / taxa_principal
                
                # 🔥 FORMATAR COM ATÉ 20 CASAS DECIMAIS
                taxa_inversa_str = f"{taxa_inversa:.20f}"
                
                # Remover zeros desnecessários no final
                if '.' in taxa_inversa_str:
                    taxa_inversa_str = taxa_inversa_str.rstrip('0').rstrip('.')
                
                # Atualizar o campo da taxa inversa (evitando loop)
                self.entry_taxa_inversa.unbind(text=self.calcular_taxa_principal)
                self.entry_taxa_inversa.text = taxa_inversa_str
                self.entry_taxa_inversa.bind(text=self.calcular_taxa_principal)
                
                # Atualizar o cálculo de conversão
                self.atualizar_calculo_conversao()
        except Exception as e:
            print(f"❌ Erro em calcular_taxa_inversa: {e}")

    def trocar_taxas(self, instance=None):
        """Troca os valores entre taxa direta e inversa - VERSÃO COM IDs"""
        try:
            print("🔄 TROCANDO TAXAS...")
            
            # Verificar se os campos existem nos IDs
            if not hasattr(self, 'ids'):
                print("❌ IDs não disponíveis")
                return
                
            if 'entry_taxa_principal' not in self.ids or 'entry_taxa_inversa' not in self.ids:
                print("❌ Campos de taxa não encontrados nos IDs")
                return
            
            taxa_principal = self.ids.entry_taxa_principal.text
            taxa_inversa = self.ids.entry_taxa_inversa.text
            
            print(f"🔍 Antes da troca - Principal: '{taxa_principal}', Inversa: '{taxa_inversa}'")
            
            # Trocar os valores (evitando loops)
            self.ids.entry_taxa_principal.unbind(text=self.calcular_taxa_inversa)
            self.ids.entry_taxa_inversa.unbind(text=self.calcular_taxa_principal)
            
            self.ids.entry_taxa_principal.text = taxa_inversa
            self.ids.entry_taxa_inversa.text = taxa_principal
            
            self.ids.entry_taxa_principal.bind(text=self.calcular_taxa_inversa)
            self.ids.entry_taxa_inversa.bind(text=self.calcular_taxa_principal)
            
            print(f"🔍 Após troca - Principal: '{self.ids.entry_taxa_principal.text}', Inversa: '{self.ids.entry_taxa_inversa.text}'")
            
            # Atualizar o cálculo
            self.atualizar_calculo_conversao()
            
        except Exception as e:
            print(f"❌ Erro ao trocar taxas: {e}")

    def calcular_taxa_principal(self, instance, value):
        """Calcula a taxa principal automaticamente quando a taxa inversa é alterada"""
        if not value or value == '.' or value == ',':
            return
            
        try:
            # Converter para float
            taxa_inversa = self._parse_valor_br(value)
            
            if taxa_inversa > 0:
                taxa_principal = 1.0 / taxa_inversa
                # Atualizar o campo da taxa principal (evitando loop)
                self.entry_taxa_principal.unbind(text=self.calcular_taxa_inversa)
                self.entry_taxa_principal.text = f"{taxa_principal:.6f}".rstrip('0').rstrip('.')
                self.entry_taxa_principal.bind(text=self.calcular_taxa_inversa)
                
                # Atualizar o cálculo de conversão
                self.atualizar_calculo_conversao()
        except:
            pass

    def atualizar_calculo_conversao(self):
        """Atualiza o cálculo de conversão com ALTA PRECISÃO"""
        try:
            # Obter valor a converter
            if hasattr(self, 'ids') and 'entry_valor_cambio' in self.ids and self.ids.entry_valor_cambio.text:
                valor_str = self.ids.entry_valor_cambio.text.strip()
                if valor_str:
                    valor = self._parse_valor_br(valor_str)
                    
                    # Obter moedas das contas selecionadas
                    moeda_origem, moeda_destino = self.obter_moedas_contas()
                    
                    if moeda_origem and moeda_destino:
                        # 🔥 USAR TAXA COM ALTA PRECISÃO
                        if hasattr(self, 'entry_taxa_principal') and self.entry_taxa_principal.text:
                            taxa_str = self.entry_taxa_principal.text.replace(',', '.')
                            taxa = float(taxa_str)  # 🔥 Conversão direta para máxima precisão
                            
                            # 🔥 CÁLCULO COM PRECISÃO MÁXIMA
                            valor_convertido = valor * taxa
                            
                            self.atualizar_label_conversao(valor, moeda_origem, valor_convertido, moeda_destino, taxa, 'principal')
        
        except Exception as e:
            print(f"❌ Erro em atualizar_calculo_conversao: {e}")

    def obter_moedas_contas(self):
        """Obtém as moedas das contas origem e destino selecionadas"""
        sistema = App.get_running_app().sistema
        
        moeda_origem = None
        moeda_destino = None
        
        try:
            # Obter conta origem
            if hasattr(self, 'ids') and 'combo_conta_origem' in self.ids and self.ids.combo_conta_origem.text:
                conta_origem = self.ids.combo_conta_origem.text.split(' - ')[0]
                if conta_origem in sistema.contas:
                    moeda_origem = sistema.contas[conta_origem]['moeda']
            
            # Obter conta destino
            if hasattr(self, 'ids') and 'combo_conta_destino' in self.ids and self.ids.combo_conta_destino.text:
                conta_destino = self.ids.combo_conta_destino.text.split(' - ')[0]
                if conta_destino in sistema.contas:
                    moeda_destino = sistema.contas[conta_destino]['moeda']
        
        except:
            pass
        
        return moeda_origem, moeda_destino

    def atualizar_label_conversao(self, valor_origem, moeda_origem, valor_destino, moeda_destino, taxa, tipo_taxa):
        """Atualiza o label de informações de conversão - VERSÃO FLEXÍVEL"""
        if hasattr(self, 'ids') and 'label_info_cambio' in self.ids:
            tipo_texto = "PRINCIPAL" if tipo_taxa == 'principal' else "INVERSA"
            self.ids.label_info_cambio.text = (
                f"{valor_origem:,.2f} {moeda_origem} → {valor_destino:,.2f} {moeda_destino}\n"
                f"Taxa {tipo_texto}: {taxa:.6f}\n"
                f"Use a taxa que corresponde à sua operação"
            )


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

    def _on_conta_bancaria_change(self, instance, value):
        """Quando conta bancária mudar, filtrar contas despesa"""
        print(f"🔄 Conta bancária alterada: {value}")
        self.atualizar_contas_despesa()

    def _on_conta_cliente_change(self, instance, value):
        """Quando conta cliente mudar, filtrar contas receita"""
        print(f"🔄 Conta cliente alterada: {value}")
        self.atualizar_contas_receita()

    def _on_conta_despesa_change(self, instance, value):
        """Quando conta despesa mudar, filtrar contas bancárias"""
        print(f"🔄 Conta despesa alterada: {value}")
        self.atualizar_contas_bancarias_despesa()

    def _on_conta_receita_change(self, instance, value):
        """Quando conta receita mudar, filtrar contas cliente"""
        print(f"🔄 Conta receita alterada: {value}")
        self.atualizar_contas_cliente_receita()


    def debug_estado_spinners(self):
        """Debug completo do estado dos spinners"""
        sistema = App.get_running_app().sistema
        
        print("=== 🔍 DEBUG SPINNERS ===")
        print(f"Receitas carregadas: {len(sistema.contas_contabeis['receitas'])} categorias")
        print(f"Despesas carregadas: {len(sistema.contas_contabeis['despesas'])} categorias")
        
        # Verificar spinners de receita
        if hasattr(self, 'ids'):
            if 'combo_categoria_receita' in self.ids:
                print(f"combo_categoria_receita: {self.ids.combo_categoria_receita.values}")
            if 'combo_conta_receita' in self.ids:
                print(f"combo_conta_receita: {self.ids.combo_conta_receita.values}")
        
        print("=== 🎯 FIM DEBUG ===")
