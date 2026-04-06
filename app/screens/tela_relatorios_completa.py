from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from datetime import datetime
import os
import calendar

class TelaRelatoriosCompleta(Screen):
    """Tela completa de relatórios com 3 abas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        self.ano_atual = datetime.now().year
        self.mes_atual = datetime.now().month
        
        # Atributos para cada aba
        self.tipo_atual = 'receita'           # Aba Mensal
        self.tipo_comp_atual = 'receita'      # Aba Comparativo
        self.tipo_anual_atual = 'receita'     # Aba Anual
        
        # Dados de resultados
        self.dados_mensal = None
        self.dados_comparativo = None
        self.dados_anual = None

        # 🔥 NOVOS ATRIBUTOS PARA FILTROS
        self.categoria_selecionada = 'TODAS'
        self.conta_selecionada = 'TODAS'
        self.lista_categorias = ['TODAS']
        self.lista_contas = ['TODAS']        
        
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        print("📊 Tela de relatórios completa carregada")
        self.construir_interface()
        Clock.schedule_once(lambda dt: self.carregar_dados_padrao(), 0.1)
        
    def construir_interface(self):
        """Constrói a interface completa com abas"""
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 🔥 COR ORIGINAL DO DASHBOARD (cinza-azulado escuro)
        with main_layout.canvas.before:
            Color(0.12, 0.16, 0.23, 1)  # Mesmo fundo do dashboard
            self.main_rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._atualizar_fundo, size=self._atualizar_fundo)
        
        # Header
        header = self.criar_header()
        main_layout.add_widget(header)
        
        # TabbedPanel
        self.tab_panel = TabbedPanel(size_hint_y=1, do_default_tab=False)
        
        # 🔥 CONFIGURAR CORES DAS ABAS
        self.tab_panel.background_color = (0.12, 0.16, 0.23, 1)      # Mesmo fundo
        self.tab_panel.background_tab = (0.20, 0.25, 0.33, 1)       # Cinza-azulado médio
        self.tab_panel.background_selected = (0.23, 0.51, 0.96, 1)  # Azul do sistema
        
        # ABA 1: RELATÓRIO MENSAL
        tab_mensal = TabbedPanelItem(text='MENSAL')
        self.layout_mensal = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.construir_aba_mensal()
        tab_mensal.add_widget(self.layout_mensal)
        
        # ABA 2: COMPARATIVO MENSAL
        tab_comparativo = TabbedPanelItem(text='COMPARATIVO')
        self.layout_comparativo = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.construir_aba_comparativo()
        tab_comparativo.add_widget(self.layout_comparativo)
        
        # ABA 3: EVOLUÇÃO ANUAL
        tab_anual = TabbedPanelItem(text='ANUAL')
        self.layout_anual = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.construir_aba_anual()
        tab_anual.add_widget(self.layout_anual)
        
        self.tab_panel.add_widget(tab_mensal)
        self.tab_panel.add_widget(tab_comparativo)
        self.tab_panel.add_widget(tab_anual)
        
        main_layout.add_widget(self.tab_panel)
        self.add_widget(main_layout)
        
        # Vincular evento de troca de aba
        self.tab_panel.bind(current_tab=self.on_tab_changed)
    
    def criar_header(self):
        """Cria o header da tela"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        
        btn_voltar = Button(
            text='< VOLTAR',
            font_size='14sp',
            size_hint_x=0.2,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_voltar.bind(on_press=self.voltar_dashboard)
        
        lbl_titulo = Label(
            text='RELATÓRIOS FINANCEIROS',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_x=0.6
        )
        
        btn_exportar = Button(
            text='EXPORTAR PDF',
            font_size='14sp',
            size_hint_x=0.2,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_exportar.bind(on_press=self.exportar_pdf)
        
        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        header.add_widget(btn_exportar)
        
        return header
    
    # ==================== ABA 1: RELATÓRIO MENSAL ====================
    
    def construir_aba_mensal(self):
        """Constrói a aba de relatório mensal com filtros de categoria e conta"""
        # Painel de controles
        painel_controles = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(280),
            spacing=dp(10),
            padding=[dp(15), dp(10)]
        )
        
        with painel_controles.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            painel_controles.rect = RoundedRectangle(pos=painel_controles.pos, size=painel_controles.size, radius=[8,])
        painel_controles.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        # 🔥 LARGURA FIXA PARA TODOS OS LABELS DA ESQUERDA
        LARGURA_LABEL = 0.12  # 12% da largura total
        
        # Linha Mês/Ano
        linha_mes_ano = BoxLayout(orientation='horizontal', size_hint_y=0.22, spacing=dp(10))
        lbl_mes = Label(text='MÊS:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_mes.bind(text_size=lbl_mes.setter('size'))
        self.spinner_mes = Spinner(text=self.meses[self.mes_atual], values=list(self.meses.values()), size_hint_x=0.35, font_size='12sp')
        lbl_ano = Label(text='ANO:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_ano.bind(text_size=lbl_ano.setter('size'))
        self.spinner_ano = Spinner(text=str(self.ano_atual), values=[str(a) for a in range(2020, self.ano_atual + 2)], size_hint_x=0.35, font_size='12sp')
        linha_mes_ano.add_widget(lbl_mes)
        linha_mes_ano.add_widget(self.spinner_mes)
        linha_mes_ano.add_widget(lbl_ano)
        linha_mes_ano.add_widget(self.spinner_ano)
        
        # Linha Tipo
        linha_tipo = BoxLayout(orientation='horizontal', size_hint_y=0.22, spacing=dp(10))
        lbl_tipo = Label(text='TIPO:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_tipo.bind(text_size=lbl_tipo.setter('size'))
        self.btn_receitas = ToggleButton(text='RECEITAS', group='tipo', size_hint_x=0.35, font_size='12sp', background_normal='', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        self.btn_receitas.bind(on_press=lambda x: self.mudar_tipo('receita'))
        self.btn_despesas = ToggleButton(text='DESPESAS', group='tipo', size_hint_x=0.35, font_size='12sp', background_normal='', background_color=(0.30, 0.35, 0.43, 1), color=(1,1,1,1))
        self.btn_despesas.bind(on_press=lambda x: self.mudar_tipo('despesa'))
        linha_tipo.add_widget(lbl_tipo)
        linha_tipo.add_widget(self.btn_receitas)
        linha_tipo.add_widget(self.btn_despesas)
        
        # Linha Moeda
        linha_moeda = BoxLayout(orientation='horizontal', size_hint_y=0.18, spacing=dp(10))
        lbl_moeda = Label(text='MOEDA:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_moeda.bind(text_size=lbl_moeda.setter('size'))
        self.spinner_moeda = Spinner(text='TODAS', values=['TODAS', 'USD', 'EUR', 'GBP', 'BRL'], size_hint_x=0.35, font_size='12sp')
        linha_moeda.add_widget(lbl_moeda)
        linha_moeda.add_widget(self.spinner_moeda)
        linha_moeda.add_widget(Label(size_hint_x=0.53))  # 🔥 AJUSTADO para compensar
        
        # Linha Categoria
        linha_categoria = BoxLayout(orientation='horizontal', size_hint_y=0.19, spacing=dp(10))
        lbl_categoria = Label(text='CATEGORIA:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_categoria.bind(text_size=lbl_categoria.setter('size'))
        self.spinner_categoria = Spinner(text='TODAS', values=['TODAS'], size_hint_x=0.35, font_size='12sp')
        self.spinner_categoria.bind(text=self.on_categoria_changed)
        linha_categoria.add_widget(lbl_categoria)
        linha_categoria.add_widget(self.spinner_categoria)
        linha_categoria.add_widget(Label(size_hint_x=0.53))  # 🔥 AJUSTADO para compensar
        
        # Linha Conta
        linha_conta = BoxLayout(orientation='horizontal', size_hint_y=0.19, spacing=dp(10))
        lbl_conta = Label(text='CONTA:', font_size='12sp', color=(1,1,1,1), size_hint_x=LARGURA_LABEL, halign='right')
        lbl_conta.bind(text_size=lbl_conta.setter('size'))
        self.spinner_conta = Spinner(text='TODAS', values=['TODAS'], size_hint_x=0.35, font_size='12sp')
        
        # Botão Gerar
        btn_gerar = Button(text='GERAR RELATÓRIO', size_hint_x=0.35, font_size='12sp', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        btn_gerar.bind(on_press=self.gerar_relatorio_mensal)
        
        linha_conta.add_widget(lbl_conta)
        linha_conta.add_widget(self.spinner_conta)
        linha_conta.add_widget(btn_gerar)
        
        painel_controles.add_widget(linha_mes_ano)
        painel_controles.add_widget(linha_tipo)
        painel_controles.add_widget(linha_moeda)
        painel_controles.add_widget(linha_categoria)
        painel_controles.add_widget(linha_conta)
        
        self.layout_mensal.add_widget(painel_controles)
        
        # Área de resultados
        self.scroll_mensal = ScrollView(size_hint_y=1, do_scroll_x=False)
        self.resultados_mensal = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.resultados_mensal.bind(minimum_height=self.resultados_mensal.setter('height'))
        self.scroll_mensal.add_widget(self.resultados_mensal)
        self.layout_mensal.add_widget(self.scroll_mensal)
    
    def mudar_tipo(self, tipo):
        """Muda o tipo entre receitas e despesas (aba mensal)"""
        self.tipo_atual = tipo
        if tipo == 'receita':
            self.btn_receitas.background_color = (0.23, 0.51, 0.96, 1)
            self.btn_despesas.background_color = (0.30, 0.35, 0.43, 1)
        else:
            self.btn_receitas.background_color = (0.30, 0.35, 0.43, 1)
            self.btn_despesas.background_color = (0.23, 0.51, 0.96, 1)
        
        # 🔥 RECARREGAR CATEGORIAS E CONTAS
        self.carregar_categorias_e_contas(tipo)
    
    def carregar_dados_padrao(self):
        """Carrega dados do mês atual e categorias"""
        self.carregar_categorias_e_contas(self.tipo_atual)
        Clock.schedule_once(lambda dt: self.gerar_relatorio_mensal(None), 0.2)
    
    def gerar_relatorio_mensal(self, instance):
        """Gera o relatório mensal com filtros de categoria e conta"""
        try:
            mes_nome = self.spinner_mes.text
            ano = int(self.spinner_ano.text)
            mes = {v: k for k, v in self.meses.items()}[mes_nome]
            moeda = self.spinner_moeda.text
            tipo = self.tipo_atual
            categoria = self.spinner_categoria.text
            conta = self.spinner_conta.text
            
            print(f"📊 Gerando relatório mensal: {tipo} - {mes}/{ano} - Moeda: {moeda}")
            print(f"   Filtros: Categoria={categoria}, Conta={conta}")
            
            sistema = App.get_running_app().sistema
            dados = sistema.buscar_relatorio_mensal_filtrado(ano, mes, tipo, moeda, categoria, conta)
            
            if not dados:
                self.mostrar_mensagem("Nenhum dado encontrado para o período selecionado")
                self.resultados_mensal.clear_widgets()
                return
            
            self.dados_mensal = dados
            
            # Se moeda for TODAS, perguntar taxas
            if moeda == 'TODAS':
                if dados.get('total_por_moeda') and len(dados['total_por_moeda']) > 1:
                    self.abrir_popup_taxas(lambda taxas: self.exibir_relatorio_mensal_com_taxas(dados, tipo, ano, mes, moeda, taxas))
                else:
                    self.exibir_relatorio_mensal(dados, tipo, ano, mes, moeda, None)
            else:
                self.exibir_relatorio_mensal(dados, tipo, ano, mes, moeda, None)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem(f"Erro: {str(e)}")

    def exibir_relatorio_mensal_com_taxas(self, dados, tipo, ano, mes, moeda, taxas):
        """Exibe relatório com taxas de conversão"""
        self.exibir_relatorio_mensal(dados, tipo, ano, mes, moeda, taxas)
    
    def exibir_relatorio_mensal(self, dados, tipo, ano, mes, moeda, taxas_conversao=None):
        """Exibe o relatório mensal com opção de conversão para USD"""
        self.resultados_mensal.clear_widgets()
        
        # 🔥 Calcular total em USD se tiver taxas
        if moeda == 'TODAS' and taxas_conversao and dados.get('total_por_moeda'):
            total_usd = 0
            for moeda_item, valor in dados['total_por_moeda'].items():
                if moeda_item == 'USD':
                    total_usd += valor
                else:
                    taxa = taxas_conversao.get(moeda_item, 1)
                    total_usd += valor / taxa if taxa > 0 else 0
            dados['total_geral_usd'] = total_usd
        
        # Título
        mes_nome = self.meses[mes]
        tipo_texto = "RECEITAS" if tipo == 'receita' else "DESPESAS"
        titulo = f"{tipo_texto} - {mes_nome}/{ano}"
        if moeda != 'TODAS':
            titulo += f" - Moeda: {moeda}"
        else:
            titulo += " - Todas as Moedas"
            if taxas_conversao:
                titulo += " (convertido para USD)"
        
        lbl_titulo = Label(text=titulo, font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(40))
        self.resultados_mensal.add_widget(lbl_titulo)
        
        # Cards de resumo (passar taxas)
        self.exibir_cards_resumo(self.resultados_mensal, dados, moeda, taxas_conversao)
        
        # Detalhamento por categoria
        self.exibir_agrupamento_categorias(self.resultados_mensal, dados, tipo)
        
        # Lista de transações
        self.exibir_lista_transacoes(self.resultados_mensal, dados, tipo)
    
    # ==================== ABA 2: COMPARATIVO MENSAL ====================
    
    def construir_aba_comparativo(self):
        """Constrói a aba de comparativo mensal"""
        # Painel de controles
        painel_controles = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=dp(10),
            padding=[dp(15), dp(10)]
        )
        
        with painel_controles.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            painel_controles.rect = RoundedRectangle(pos=painel_controles.pos, size=painel_controles.size, radius=[8,])
        painel_controles.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        # Linha Mês Referência
        linha_ref = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=dp(20))
        lbl_ref = Label(text='PERÍODO 1:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.15)
        self.spinner_mes_ref = Spinner(text=self.meses[self.mes_atual], values=list(self.meses.values()), size_hint_x=0.35, font_size='12sp')
        self.spinner_ano_ref = Spinner(text=str(self.ano_atual), values=[str(a) for a in range(2020, self.ano_atual + 2)], size_hint_x=0.35, font_size='12sp')
        linha_ref.add_widget(lbl_ref)
        linha_ref.add_widget(self.spinner_mes_ref)
        linha_ref.add_widget(self.spinner_ano_ref)
        
        # Linha Mês Comparação
        linha_comp = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=dp(20))
        lbl_comp = Label(text='PERÍODO 2:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.15)
        mes_anterior = self.meses[self.mes_atual - 1 if self.mes_atual > 1 else 12]
        self.spinner_mes_comp = Spinner(text=mes_anterior, values=list(self.meses.values()), size_hint_x=0.35, font_size='12sp')
        ano_anterior = str(self.ano_atual if self.mes_atual > 1 else self.ano_atual - 1)
        self.spinner_ano_comp = Spinner(text=ano_anterior, values=[str(a) for a in range(2020, self.ano_atual + 2)], size_hint_x=0.35, font_size='12sp')
        linha_comp.add_widget(lbl_comp)
        linha_comp.add_widget(self.spinner_mes_comp)
        linha_comp.add_widget(self.spinner_ano_comp)
        
        # Linha Tipo e Moeda
        linha_tipo_moeda = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=dp(20))
        lbl_tipo = Label(text='TIPO:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.15)
        self.btn_comp_receitas = ToggleButton(text='RECEITAS', group='tipo_comp', size_hint_x=0.2, font_size='12sp', background_normal='', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        self.btn_comp_despesas = ToggleButton(text='DESPESAS', group='tipo_comp', size_hint_x=0.2, font_size='12sp', background_normal='', background_color=(0.30, 0.35, 0.43, 1), color=(1,1,1,1))
        self.btn_comp_receitas.bind(on_press=lambda x: self.mudar_tipo_comparativo('receita'))
        self.btn_comp_despesas.bind(on_press=lambda x: self.mudar_tipo_comparativo('despesa'))
        
        lbl_moeda = Label(text='MOEDA:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.1)
        self.spinner_moeda_comp = Spinner(text='TODAS', values=['TODAS', 'USD', 'EUR', 'GBP', 'BRL'], size_hint_x=0.25, font_size='12sp')
        btn_gerar = Button(text='GERAR COMPARATIVO', size_hint_x=0.25, font_size='12sp', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        btn_gerar.bind(on_press=self.gerar_comparativo)
        
        linha_tipo_moeda.add_widget(lbl_tipo)
        linha_tipo_moeda.add_widget(self.btn_comp_receitas)
        linha_tipo_moeda.add_widget(self.btn_comp_despesas)
        linha_tipo_moeda.add_widget(lbl_moeda)
        linha_tipo_moeda.add_widget(self.spinner_moeda_comp)
        linha_tipo_moeda.add_widget(btn_gerar)
        
        painel_controles.add_widget(linha_ref)
        painel_controles.add_widget(linha_comp)
        painel_controles.add_widget(linha_tipo_moeda)
        
        self.layout_comparativo.add_widget(painel_controles)
        
        # Área de resultados
        self.scroll_comparativo = ScrollView(size_hint_y=1, do_scroll_x=False)
        self.resultados_comparativo = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.resultados_comparativo.bind(minimum_height=self.resultados_comparativo.setter('height'))
        self.scroll_comparativo.add_widget(self.resultados_comparativo)
        self.layout_comparativo.add_widget(self.scroll_comparativo)
    
    def mudar_tipo_comparativo(self, tipo):
        """Muda o tipo no comparativo"""
        self.tipo_comp_atual = tipo
        if tipo == 'receita':
            self.btn_comp_receitas.background_color = (0.23, 0.51, 0.96, 1)
            self.btn_comp_despesas.background_color = (0.30, 0.35, 0.43, 1)
        else:
            self.btn_comp_receitas.background_color = (0.30, 0.35, 0.43, 1)
            self.btn_comp_despesas.background_color = (0.23, 0.51, 0.96, 1)
    
    def gerar_comparativo(self, instance):
        """Gera o comparativo mensal"""
        try:
            mes_ref_nome = self.spinner_mes_ref.text
            ano_ref = int(self.spinner_ano_ref.text)
            mes_ref = {v: k for k, v in self.meses.items()}[mes_ref_nome]
            
            mes_comp_nome = self.spinner_mes_comp.text
            ano_comp = int(self.spinner_ano_comp.text)
            mes_comp = {v: k for k, v in self.meses.items()}[mes_comp_nome]
            
            moeda = self.spinner_moeda_comp.text
            tipo = self.tipo_comp_atual
            
            print(f"Gerando comparativo: {tipo} - {mes_ref}/{ano_ref} vs {mes_comp}/{ano_comp}")
            
            sistema = App.get_running_app().sistema
            dados = sistema.buscar_comparativo_mensal(ano_ref, mes_ref, ano_comp, mes_comp, tipo, moeda)
            
            if not dados:
                self.mostrar_mensagem("Nenhum dado encontrado para o período selecionado")
                self.resultados_comparativo.clear_widgets()
                return
            
            self.dados_comparativo = dados
            self.exibir_comparativo(dados, mes_ref_nome, ano_ref, mes_comp_nome, ano_comp, moeda)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem(f"Erro: {str(e)}")
    
    def exibir_comparativo(self, dados, mes_ref, ano_ref, mes_comp, ano_comp, moeda):
        """Exibe o comparativo mensal"""
        self.resultados_comparativo.clear_widgets()
        
        # Título
        tipo_texto = "RECEITAS" if dados['tipo'] == 'receita' else "DESPESAS"
        titulo = f"COMPARATIVO: {mes_ref}/{ano_ref} vs {mes_comp}/{ano_comp} - {tipo_texto}"
        if moeda != 'TODAS':
            titulo += f" - Moeda: {moeda}"
        lbl_titulo = Label(text=titulo, font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(40))
        self.resultados_comparativo.add_widget(lbl_titulo)
        
        # Cards de resumo
        totais = dados['totais']
        cards_layout = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(100), padding=[0, dp(10)])
        
        card_ref = self.criar_card(f"{mes_ref}/{ano_ref}", self.formatar_valor(totais['referencia'], moeda if moeda != 'TODAS' else 'USD'), (0.23, 0.51, 0.96, 1))
        card_comp = self.criar_card(f"{mes_comp}/{ano_comp}", self.formatar_valor(totais['comparacao'], moeda if moeda != 'TODAS' else 'USD'), (0.55, 0.36, 0.96, 1))
        
        sinal = "+" if totais['variacao'] > 0 else "-" if totais['variacao'] < 0 else "="
        var_text = f"{sinal} {abs(totais['variacao_percentual']):.1f}%"
        cor_var = (0.2, 0.8, 0.2, 1) if totais['variacao'] > 0 else (0.8, 0.2, 0.2, 1) if totais['variacao'] < 0 else (0.8, 0.8, 0.8, 1)
        card_var = self.criar_card("VARIAÇÃO", var_text, cor_var)
        
        cards_layout.add_widget(card_ref)
        cards_layout.add_widget(card_comp)
        cards_layout.add_widget(card_var)
        self.resultados_comparativo.add_widget(cards_layout)
        
        # Comparativo por categoria
        lbl_secao = Label(text="COMPARATIVO POR CATEGORIA", font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(45))
        self.resultados_comparativo.add_widget(lbl_secao)
        
        # Cabeçalho
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        header.add_widget(Label(text="CATEGORIA", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.4))
        header.add_widget(Label(text=f"{mes_ref}/{ano_ref}", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2, halign='right'))
        header.add_widget(Label(text=f"{mes_comp}/{ano_comp}", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2, halign='right'))
        header.add_widget(Label(text="VARIAÇÃO", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2, halign='right'))
        self.resultados_comparativo.add_widget(header)
        
        for categoria, cat_dados in dados['categorias'].items():
            # Linha da categoria
            linha_cat = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32), spacing=dp(5))
            
            lbl_cat = Label(text=categoria, font_size='13sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.4, halign='left')
            lbl_cat.bind(text_size=lbl_cat.setter('size'))
            
            val_ref = self.formatar_valor(cat_dados['total_ref'], moeda if moeda != 'TODAS' else 'USD')
            val_comp = self.formatar_valor(cat_dados['total_comp'], moeda if moeda != 'TODAS' else 'USD')
            
            sinal_cat = "+" if cat_dados['variacao'] > 0 else "-" if cat_dados['variacao'] < 0 else "="
            cor_var_cat = (0.2, 0.8, 0.2, 1) if cat_dados['variacao'] > 0 else (0.8, 0.2, 0.2, 1) if cat_dados['variacao'] < 0 else (0.8, 0.8, 0.8, 1)
            var_text_cat = f"{sinal_cat} {abs(cat_dados['variacao_percentual']):.1f}%"
            
            linha_cat.add_widget(lbl_cat)
            linha_cat.add_widget(Label(text=val_ref, font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.2, halign='right'))
            linha_cat.add_widget(Label(text=val_comp, font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.2, halign='right'))
            linha_cat.add_widget(Label(text=var_text_cat, font_size='12sp', bold=True, color=cor_var_cat, size_hint_x=0.2, halign='right'))
            self.resultados_comparativo.add_widget(linha_cat)
            
            # Contas específicas
            for conta, dados_conta in cat_dados['contas'].items():
                linha_conta = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28), spacing=dp(5))
                
                lbl_conta = Label(text=f" {conta}", font_size='11sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.4, halign='left')
                lbl_conta.bind(text_size=lbl_conta.setter('size'))
                
                val_ref_conta = self.formatar_valor(dados_conta['valor_ref'], moeda if moeda != 'TODAS' else 'USD')
                val_comp_conta = self.formatar_valor(dados_conta['valor_comp'], moeda if moeda != 'TODAS' else 'USD')
                
                sinal_conta = "+" if dados_conta['variacao'] > 0 else "-" if dados_conta['variacao'] < 0 else "="
                cor_var_conta = (0.2, 0.8, 0.2, 1) if dados_conta['variacao'] > 0 else (0.8, 0.2, 0.2, 1) if dados_conta['variacao'] < 0 else (0.8, 0.8, 0.8, 1)
                var_text_conta = f"{sinal_conta} {abs(dados_conta['variacao_percentual']):.1f}%"
                
                linha_conta.add_widget(lbl_conta)
                linha_conta.add_widget(Label(text=val_ref_conta, font_size='10sp', color=(0.70, 0.74, 0.78, 1), size_hint_x=0.2, halign='right'))
                linha_conta.add_widget(Label(text=val_comp_conta, font_size='10sp', color=(0.70, 0.74, 0.78, 1), size_hint_x=0.2, halign='right'))
                linha_conta.add_widget(Label(text=var_text_conta, font_size='10sp', color=cor_var_conta, size_hint_x=0.2, halign='right'))
                self.resultados_comparativo.add_widget(linha_conta)
    
    # ==================== ABA 3: EVOLUÇÃO ANUAL ====================
    
    def construir_aba_anual(self):
        """Constrói a aba de evolução anual"""
        # Painel de controles
        painel_controles = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(10),
            padding=[dp(15), dp(10)]
        )
        
        with painel_controles.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            painel_controles.rect = RoundedRectangle(pos=painel_controles.pos, size=painel_controles.size, radius=[8,])
        painel_controles.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        # Linha Ano e Tipo
        linha_ano = BoxLayout(orientation='horizontal', size_hint_y=0.5, spacing=dp(20))
        lbl_ano = Label(text='ANO:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.1)
        self.spinner_ano_anual = Spinner(text=str(self.ano_atual), values=[str(a) for a in range(2020, self.ano_atual + 2)], size_hint_x=0.3, font_size='12sp')
        
        lbl_tipo = Label(text='TIPO:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.1)
        self.btn_anual_receitas = ToggleButton(text='RECEITAS', group='tipo_anual', size_hint_x=0.2, font_size='12sp', background_normal='', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        self.btn_anual_despesas = ToggleButton(text='DESPESAS', group='tipo_anual', size_hint_x=0.2, font_size='12sp', background_normal='', background_color=(0.30, 0.35, 0.43, 1), color=(1,1,1,1))
        self.btn_anual_receitas.bind(on_press=lambda x: self.mudar_tipo_anual('receita'))
        self.btn_anual_despesas.bind(on_press=lambda x: self.mudar_tipo_anual('despesa'))
        
        linha_ano.add_widget(lbl_ano)
        linha_ano.add_widget(self.spinner_ano_anual)
        linha_ano.add_widget(lbl_tipo)
        linha_ano.add_widget(self.btn_anual_receitas)
        linha_ano.add_widget(self.btn_anual_despesas)
        
        # Linha Moeda e Botão
        linha_moeda = BoxLayout(orientation='horizontal', size_hint_y=0.5, spacing=dp(20))
        lbl_moeda = Label(text='MOEDA:', font_size='12sp', color=(1,1,1,1), size_hint_x=0.1)
        self.spinner_moeda_anual = Spinner(text='TODAS', values=['TODAS', 'USD', 'EUR', 'GBP', 'BRL'], size_hint_x=0.3, font_size='12sp')
        btn_gerar = Button(text='GERAR EVOLUÇÃO', size_hint_x=0.4, font_size='12sp', background_color=(0.23, 0.51, 0.96, 1), color=(1,1,1,1))
        btn_gerar.bind(on_press=self.gerar_evolucao_anual)
        
        linha_moeda.add_widget(lbl_moeda)
        linha_moeda.add_widget(self.spinner_moeda_anual)
        linha_moeda.add_widget(btn_gerar)
        
        painel_controles.add_widget(linha_ano)
        painel_controles.add_widget(linha_moeda)
        
        self.layout_anual.add_widget(painel_controles)
        
        # Área de resultados
        self.scroll_anual = ScrollView(size_hint_y=1, do_scroll_x=False)
        self.resultados_anual = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.resultados_anual.bind(minimum_height=self.resultados_anual.setter('height'))
        self.scroll_anual.add_widget(self.resultados_anual)
        self.layout_anual.add_widget(self.scroll_anual)
    
    def mudar_tipo_anual(self, tipo):
        """Muda o tipo na evolução anual"""
        self.tipo_anual_atual = tipo
        if tipo == 'receita':
            self.btn_anual_receitas.background_color = (0.23, 0.51, 0.96, 1)
            self.btn_anual_despesas.background_color = (0.30, 0.35, 0.43, 1)
        else:
            self.btn_anual_receitas.background_color = (0.30, 0.35, 0.43, 1)
            self.btn_anual_despesas.background_color = (0.23, 0.51, 0.96, 1)
    
    def gerar_evolucao_anual(self, instance):
        """Gera a evolução anual"""
        try:
            ano = int(self.spinner_ano_anual.text)
            moeda = self.spinner_moeda_anual.text
            tipo = self.tipo_anual_atual
            
            print(f"Gerando evolução anual: {tipo} - {ano} - Moeda: {moeda}")
            
            sistema = App.get_running_app().sistema
            dados = sistema.buscar_evolucao_anual(ano, tipo, moeda)
            
            if not dados or not dados.get('meses'):
                self.mostrar_mensagem("Nenhum dado encontrado para o ano selecionado")
                self.resultados_anual.clear_widgets()
                return
            
            self.dados_anual = dados
            self.exibir_evolucao_anual(dados, ano, moeda, tipo)
            
        except Exception as e:
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem(f"Erro: {str(e)}")
    
    def exibir_evolucao_anual(self, dados, ano, moeda, tipo):
        """Exibe a evolução anual"""
        self.resultados_anual.clear_widgets()
        
        # Título
        tipo_texto = "RECEITAS" if tipo == 'receita' else "DESPESAS"
        titulo = f"EVOLUÇÃO ANUAL - {tipo_texto} - {ano}"
        if moeda != 'TODAS':
            titulo += f" - Moeda: {moeda}"
        lbl_titulo = Label(text=titulo, font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(40))
        self.resultados_anual.add_widget(lbl_titulo)
        
        # Cards de resumo
        totais = dados['totais']
        cards_layout = GridLayout(cols=4, spacing=dp(10), size_hint_y=None, height=dp(100), padding=[0, dp(10)])
        
        card_total = self.criar_card("TOTAL ANO", self.formatar_valor(totais['total_ano'], moeda if moeda != 'TODAS' else 'USD'), (0.23, 0.51, 0.96, 1))
        card_media = self.criar_card("MÉDIA MENSAL", self.formatar_valor(totais['media_mensal'], moeda if moeda != 'TODAS' else 'USD'), (0.55, 0.36, 0.96, 1))
        card_melhor = self.criar_card("MELHOR MÊS", f"{totais['melhor_mes']['mes']}\n{self.formatar_valor(totais['melhor_mes']['valor'], moeda if moeda != 'TODAS' else 'USD')}", (0.2, 0.8, 0.2, 1), height=dp(90))
        card_pior = self.criar_card("PIOR MÊS", f"{totais['pior_mes']['mes']}\n{self.formatar_valor(totais['pior_mes']['valor'], moeda if moeda != 'TODAS' else 'USD')}", (0.8, 0.2, 0.2, 1), height=dp(90))
        
        cards_layout.add_widget(card_total)
        cards_layout.add_widget(card_media)
        cards_layout.add_widget(card_melhor)
        cards_layout.add_widget(card_pior)
        self.resultados_anual.add_widget(cards_layout)
        
        # Tabela de evolução mensal
        lbl_secao = Label(text="EVOLUÇÃO MENSAL", font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(45))
        self.resultados_anual.add_widget(lbl_secao)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        header.add_widget(Label(text="MÊS", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2))
        header.add_widget(Label(text="VALOR", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.25, halign='right'))
        header.add_widget(Label(text="VARIAÇÃO MENSAL", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.3, halign='right'))
        header.add_widget(Label(text="ACUMULADO", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.25, halign='right'))
        self.resultados_anual.add_widget(header)
        
        for mes_dados in dados['meses']:
            linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32), spacing=dp(5))
            
            linha.add_widget(Label(text=mes_dados['mes'], font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.2, halign='left'))
            linha.add_widget(Label(text=self.formatar_valor(mes_dados['valor'], moeda if moeda != 'TODAS' else 'USD'), font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.25, halign='right'))
            
            sinal = "+" if mes_dados['variacao_mensal'] > 0 else "-" if mes_dados['variacao_mensal'] < 0 else "="
            cor_var = (0.2, 0.8, 0.2, 1) if mes_dados['variacao_mensal'] > 0 else (0.8, 0.2, 0.2, 1) if mes_dados['variacao_mensal'] < 0 else (0.8, 0.8, 0.8, 1)
            var_text = f"{sinal} {abs(mes_dados['variacao_mensal']):.1f}%" if mes_dados['variacao_mensal'] != 0 else "="
            linha.add_widget(Label(text=var_text, font_size='12sp', color=cor_var, size_hint_x=0.3, halign='right'))
            linha.add_widget(Label(text=self.formatar_valor(mes_dados['acumulado'], moeda if moeda != 'TODAS' else 'USD'), font_size='12sp', color=(0.23, 0.51, 0.96, 1), size_hint_x=0.25, halign='right'))
            
            self.resultados_anual.add_widget(linha)
        
        # Barra de progresso visual
        if dados['meses']:
            lbl_secao2 = Label(text="DISTRIBUIÇÃO MENSAL", font_size='14sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(35))
            self.resultados_anual.add_widget(lbl_secao2)
            
            max_valor = max([m['valor'] for m in dados['meses']])
            if max_valor > 0:
                for mes_dados in dados['meses']:
                    percentual = (mes_dados['valor'] / max_valor * 100) if max_valor > 0 else 0
                    barra_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), spacing=dp(5))
                    
                    lbl_mes = Label(text=mes_dados['mes'][:3], font_size='10sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.1, halign='right')
                    barra = BoxLayout(size_hint_x=percentual/100, size_hint_y=None, height=dp(15))
                    with barra.canvas.before:
                        Color(0.23, 0.51, 0.96, 1)
                        barra.rect = RoundedRectangle(pos=barra.pos, size=barra.size, radius=[3,])
                    barra.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
                    
                    barra_layout.add_widget(lbl_mes)
                    barra_layout.add_widget(barra)
                    barra_layout.add_widget(Label(text=f"{percentual:.0f}%", font_size='9sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.15, halign='left'))
                    
                    self.resultados_anual.add_widget(barra_layout)
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _atualizar_rect(self, instance, value):
        """Atualiza o retângulo de fundo"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def formatar_valor(self, valor, moeda):
        """Formata valor com a moeda"""
        if moeda == 'USD':
            return f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'EUR':
            return f"€{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'GBP':
            return f"£{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'BRL':
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def criar_card(self, titulo, valor, cor, height=dp(80)):
        """Cria um card de resumo"""
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=height, padding=[dp(10), dp(5)], spacing=dp(5))
        with card.canvas.before:
            Color(*cor)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[8,])
        card.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        card.add_widget(Label(text=titulo, font_size='12sp', color=(1,1,1,1), size_hint_y=0.4))
        card.add_widget(Label(text=valor, font_size='16sp', bold=True, color=(1,1,1,1), size_hint_y=0.6))
        return card
    
    def exibir_cards_resumo(self, container, dados, moeda_padrao, taxas_conversao=None):
        """Exibe os cards de resumo com conversão para USD se necessário"""
        cards_layout = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(100), padding=[0, dp(10)])
        
        total_geral = dados.get('total_geral', 0)
        quantidade = dados.get('quantidade_transacoes', 0)
        media = total_geral / quantidade if quantidade > 0 else 0
        
        # Se moeda_padrao é TODAS, mostrar total em USD convertido
        if moeda_padrao == 'TODAS' and taxas_conversao:
            total_geral_usd = dados.get('total_geral_usd', total_geral)
            card1 = self.criar_card("TOTAL (USD)", self.formatar_valor(total_geral_usd, 'USD'), (0.23, 0.51, 0.96, 1))
        else:
            card1 = self.criar_card("TOTAL", self.formatar_valor(total_geral, moeda_padrao if moeda_padrao != 'TODAS' else 'USD'), (0.23, 0.51, 0.96, 1))
        
        card2 = self.criar_card("TRANSAÇÕES", str(quantidade), (0.55, 0.36, 0.96, 1))
        card3 = self.criar_card("MÉDIA", self.formatar_valor(media, moeda_padrao if moeda_padrao != 'TODAS' else 'USD'), (0.96, 0.55, 0.36, 1))
        
        cards_layout.add_widget(card1)
        cards_layout.add_widget(card2)
        cards_layout.add_widget(card3)
        container.add_widget(cards_layout)
        
        # Breakdown por moeda se TODAS
        if moeda_padrao == 'TODAS' and dados.get('total_por_moeda'):
            breakdown = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
            breakdown.bind(minimum_height=breakdown.setter('height'))
            
            lbl_break = Label(
                text="DETALHAMENTO POR MOEDA:",
                font_size='13sp',  # 🔥 AUMENTADO
                bold=True,
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(30)  # 🔥 AUMENTADO
            )
            breakdown.add_widget(lbl_break)
            
            # Layout para os cards das moedas
            linha_moedas = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(85), spacing=dp(10))  # 🔥 AUMENTADO altura
            
            for moeda, valor in dados['total_por_moeda'].items():
                # Card para cada moeda
                card_moeda = BoxLayout(orientation='vertical', size_hint_x=1, height=dp(80), padding=[dp(8), dp(5)], spacing=dp(3))  # 🔥 AUMENTADO
                with card_moeda.canvas.before:
                    Color(0.30, 0.35, 0.43, 1)
                    card_moeda.rect = RoundedRectangle(pos=card_moeda.pos, size=card_moeda.size, radius=[5,])
                card_moeda.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
                
                # Moeda (sigla)
                lbl_moeda = Label(
                    text=f"{moeda}",
                    font_size='13sp',  # 🔥 AUMENTADO (antes 10sp)
                    bold=True,
                    color=(0.23, 0.51, 0.96, 1),
                    size_hint_y=0.35
                )
                
                # Valor original
                lbl_valor = Label(
                    text=self.formatar_valor(valor, moeda),
                    font_size='14sp',  # 🔥 AUMENTADO (antes 11sp)
                    bold=True,
                    color=(1, 1, 1, 1),
                    size_hint_y=0.35
                )
                
                card_moeda.add_widget(lbl_moeda)
                card_moeda.add_widget(lbl_valor)
                
                # Valor em USD se tiver taxas
                if taxas_conversao and moeda != 'USD':
                    taxa = taxas_conversao.get(moeda, 1)
                    valor_usd = valor / taxa if taxa > 0 else 0
                    lbl_usd = Label(
                        text=f"≈ {self.formatar_valor(valor_usd, 'USD')}",
                        font_size='11sp',  # 🔥 AUMENTADO (antes 9sp)
                        color=(0.80, 0.84, 0.88, 1),
                        size_hint_y=0.30
                    )
                    card_moeda.add_widget(lbl_usd)
                elif moeda == 'USD':
                    # Para USD, mostrar que é a base
                    lbl_usd = Label(
                        text="(base)",
                        font_size='11sp',  # 🔥 AUMENTADO
                        color=(0.80, 0.84, 0.88, 1),
                        size_hint_y=0.30
                    )
                    card_moeda.add_widget(lbl_usd)
                
                linha_moedas.add_widget(card_moeda)
            
            breakdown.add_widget(linha_moedas)
            container.add_widget(breakdown)
    
    def exibir_agrupamento_categorias(self, container, dados, tipo):
        """Exibe o agrupamento por categoria"""
        categorias = dados.get('categorias', {})
        moeda_padrao = dados.get('moeda_padrao', 'USD')
        
        if not categorias:
            container.add_widget(Label(text="Nenhuma categoria encontrada", color=(0.80, 0.84, 0.88, 1), size_hint_y=None, height=dp(40)))
            return
        
        lbl_secao = Label(text="DETALHAMENTO POR CATEGORIA", font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(45))
        container.add_widget(lbl_secao)
        
        for categoria, cat_dados in sorted(categorias.items()):
            cat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
            cat_layout.bind(minimum_height=cat_layout.setter('height'))
            with cat_layout.canvas.before:
                Color(0.15, 0.20, 0.27, 1)
                cat_layout.rect = RoundedRectangle(pos=cat_layout.pos, size=cat_layout.size, radius=[5,])
            cat_layout.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
            
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), padding=[dp(10), dp(5)])
            lbl_cat = Label(text=categoria, font_size='14sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.8, halign='left')
            lbl_cat.bind(text_size=lbl_cat.setter('size'))
            total_cat = cat_dados.get('total', 0)
            total_text = self.formatar_valor(total_cat, moeda_padrao if moeda_padrao != 'TODAS' else 'USD')
            lbl_total = Label(text=total_text, font_size='13sp', bold=True, color=(1,1,1,1), size_hint_x=0.2, halign='right')
            lbl_total.bind(text_size=lbl_total.setter('size'))
            header.add_widget(lbl_cat)
            header.add_widget(lbl_total)
            cat_layout.add_widget(header)
            
            contas = cat_dados.get('contas', {})
            for conta, conta_dados in sorted(contas.items(), key=lambda x: x[1]['total'], reverse=True):
                conta_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), padding=[dp(30), dp(2)])
                lbl_conta = Label(text=f" {conta}", font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.8, halign='left')
                lbl_conta.bind(text_size=lbl_conta.setter('size'))
                total_conta = conta_dados.get('total', 0)
                qtd = conta_dados.get('quantidade', 0)
                valor_text = self.formatar_valor(total_conta, moeda_padrao if moeda_padrao != 'TODAS' else 'USD')
                lbl_total_conta = Label(text=f"{valor_text} ({qtd} tx)", font_size='12sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.2, halign='right')
                lbl_total_conta.bind(text_size=lbl_total_conta.setter('size'))
                conta_layout.add_widget(lbl_conta)
                conta_layout.add_widget(lbl_total_conta)
                cat_layout.add_widget(conta_layout)
            
            container.add_widget(cat_layout)
    
    def exibir_lista_transacoes(self, container, dados, tipo):
        """Exibe a lista detalhada de transações"""
        transacoes = dados.get('transacoes', [])
        moeda_padrao = dados.get('moeda_padrao', 'USD')
        
        if not transacoes:
            return
        
        lbl_secao = Label(text="LISTA DE TRANSAÇÕES", font_size='16sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_y=None, height=dp(45))
        container.add_widget(lbl_secao)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        header.add_widget(Label(text="DATA", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.15))
        header.add_widget(Label(text="DESCRIÇÃO", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.5))
        header.add_widget(Label(text="CATEGORIA", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2))
        header.add_widget(Label(text="VALOR", font_size='12sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.15, halign='right'))
        container.add_widget(header)
        
        for trans in transacoes:
            linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
            data = trans.get('data', '')[:10]
            descricao = trans.get('descricao', '')[:50]
            categoria = trans.get('categoria', '')[:30]
            valor = self.formatar_valor(trans.get('valor', 0), trans.get('moeda', 'USD'))
            
            linha.add_widget(Label(text=data, font_size='11sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.15, halign='left'))
            linha.add_widget(Label(text=descricao, font_size='11sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.5, halign='left'))
            linha.add_widget(Label(text=categoria, font_size='11sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.2, halign='left'))
            linha.add_widget(Label(text=valor, font_size='11sp', color=(0.80, 0.84, 0.88, 1), size_hint_x=0.15, halign='right'))
            container.add_widget(linha)
        
        total_linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        total_linha.add_widget(Label(size_hint_x=0.65))
        lbl_total_text = Label(text="TOTAL GERAL:", font_size='13sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.2, halign='right')
        total_geral = dados.get('total_geral', 0)
        valor_total = self.formatar_valor(total_geral, moeda_padrao if moeda_padrao != 'TODAS' else 'USD')
        lbl_total_valor = Label(text=valor_total, font_size='13sp', bold=True, color=(0.23, 0.51, 0.96, 1), size_hint_x=0.15, halign='right')
        total_linha.add_widget(lbl_total_text)
        total_linha.add_widget(lbl_total_valor)
        container.add_widget(total_linha)
    
    def mostrar_mensagem(self, mensagem):
        """Mostra um popup com mensagem"""
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text=mensagem, font_size='14sp'))
        btn_ok = Button(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title='Mensagem', content=popup_layout, size_hint=(0.6, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn_ok)
        popup.open()
    
    def exportar_pdf(self, instance):
        """Exporta o relatório atual para PDF"""
        aba_atual = self.tab_panel.current_tab.text
        
        # 🔥 CORREÇÃO: Verificar partes do texto (ignorando emojis)
        if 'MENSAL' in aba_atual:
            self.exportar_pdf_mensal()
        elif 'COMPARATIVO' in aba_atual:
            self.exportar_pdf_comparativo()
        elif 'ANUAL' in aba_atual:
            self.exportar_pdf_anual()
        else:
            self.mostrar_mensagem(f"Aba não reconhecida: {aba_atual}")
    
    def exportar_pdf_mensal(self):
        """Exporta o relatório mensal para PDF"""
        try:
            if not self.dados_mensal:
                self.mostrar_mensagem("Gere um relatório mensal primeiro")
                return
            
            sistema = App.get_running_app().sistema
            mes_nome = self.spinner_mes.text
            ano = int(self.spinner_ano.text)
            mes = {v: k for k, v in self.meses.items()}[mes_nome]
            moeda = self.spinner_moeda.text
            tipo = self.tipo_atual
            
            from pdf_generator import PDFGenerator
            pdf_gen = PDFGenerator()
            
            nome_arquivo = f"relatorio_{tipo}_{ano}_{mes:02d}_{moeda}.pdf"
            caminho = pdf_gen.gerar_relatorio_financeiro(
                dados=self.dados_mensal,
                tipo=tipo,
                ano=ano,
                mes=mes,
                moeda=moeda,
                nome_arquivo=nome_arquivo
            )
            
            if caminho:
                self.mostrar_mensagem(f"✅ PDF exportado com sucesso!\n📁 {caminho}")
            else:
                self.mostrar_mensagem("❌ Erro ao gerar PDF")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.mostrar_mensagem(f"Erro: {str(e)}")

    def abrir_popup_taxas(self, callback):
        """Abre popup para inserir taxas de câmbio"""
        
        # Layout do popup
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Título
        lbl_titulo = Label(
            text='TAXAS DE CÂMBIO (USD BASE)',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(40)
        )
        popup_layout.add_widget(lbl_titulo)
        
        # Subtítulo
        lbl_sub = Label(
            text='Informe a cotação de cada moeda em relação ao USD:',
            font_size='12sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=None,
            height=dp(30)
        )
        popup_layout.add_widget(lbl_sub)
        
        # Container para os campos
        campos_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        campos_layout.bind(minimum_height=campos_layout.setter('height'))
        
        # Taxas padrão (buscar do sistema se disponível)
        sistema = App.get_running_app().sistema
        taxas_padrao = {
            'EUR': sistema.taxas_cambio.get('USD_EUR', 0.92),
            'GBP': sistema.taxas_cambio.get('USD_GBP', 0.79),
            'BRL': sistema.taxas_cambio.get('USD_BRL', 5.20),
        }
        
        # Dicionário para armazenar os inputs
        self.inputs_taxas = {}
        
        # Moedas disponíveis
        moedas = ['EUR', 'GBP', 'BRL']
        moedas_nomes = {'EUR': 'Euro (€)', 'GBP': 'Libra (£)', 'BRL': 'Real (R$)'}
        
        for moeda in moedas:
            # Label da moeda
            lbl_moeda = Label(
                text=f'1 USD = ? {moedas_nomes[moeda]}:',
                font_size='12sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(40),
                halign='right'
            )
            lbl_moeda.bind(text_size=lbl_moeda.setter('size'))
            
            # Input da taxa
            txt_taxa = TextInput(
                text=str(taxas_padrao[moeda]),
                font_size='12sp',
                size_hint_y=None,
                height=dp(40),
                multiline=False,
                input_filter='float',
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1)
            )
            
            campos_layout.add_widget(lbl_moeda)
            campos_layout.add_widget(txt_taxa)
            self.inputs_taxas[moeda] = txt_taxa
        
        popup_layout.add_widget(campos_layout)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        btn_cancelar = Button(
            text='CANCELAR',
            font_size='12sp',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='CONFIRMAR TAXAS',
            font_size='12sp',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        popup_layout.add_widget(botoes_layout)
        
        # Criar popup
        popup = Popup(
            title='Configurar Taxas de Câmbio',
            title_color=(0.23, 0.51, 0.96, 1),
            content=popup_layout,
            size_hint=(0.8, 0.6),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # Ações dos botões
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_confirmar.bind(on_press=lambda x: self.confirmar_taxas(popup, callback))
        
        popup.open()

    def confirmar_taxas(self, popup, callback):
        """Confirma as taxas e chama o callback"""
        try:
            taxas = {}
            for moeda, input_widget in self.inputs_taxas.items():
                valor = float(input_widget.text.replace(',', '.'))
                if valor <= 0:
                    self.mostrar_mensagem(f"Taxa para {moeda} deve ser maior que zero!")
                    return
                taxas[moeda] = valor
            
            popup.dismiss()
            callback(taxas)
            
        except ValueError:
            self.mostrar_mensagem("Por favor, insira valores numéricos válidos!")   

    def carregar_categorias_e_contas(self, tipo):
        """Carrega as categorias e contas disponíveis baseado no tipo"""
        try:
            sistema = App.get_running_app().sistema
            
            # Buscar categorias disponíveis
            if tipo == 'receita':
                query = sistema.supabase.client.table('contas_contabeis')\
                    .select('categoria, nome')\
                    .eq('tipo', 'receita')\
                    .execute()
            else:
                query = sistema.supabase.client.table('contas_contabeis')\
                    .select('categoria, nome')\
                    .eq('tipo', 'despesa')\
                    .execute()
            
            if query.data:
                # Extrair categorias únicas
                categorias = list(set([item['categoria'] for item in query.data]))
                categorias.sort()
                categorias.insert(0, 'TODAS')
                self.spinner_categoria.values = categorias
                
                # Guardar todas as contas por categoria para uso posterior
                self.contas_por_categoria = {}
                for item in query.data:
                    cat = item['categoria']
                    conta = item['nome']
                    if cat not in self.contas_por_categoria:
                        self.contas_por_categoria[cat] = []
                    if conta not in self.contas_por_categoria[cat]:
                        self.contas_por_categoria[cat].append(conta)
                
                # Resetar seleções
                self.spinner_categoria.text = 'TODAS'
                self.spinner_conta.text = 'TODAS'
                self.spinner_conta.values = ['TODAS']
                
        except Exception as e:
            print(f"❌ Erro ao carregar categorias: {e}")

    def on_categoria_changed(self, spinner, text):
        """Quando a categoria é alterada, atualiza a lista de contas"""
        if text == 'TODAS':
            self.spinner_conta.values = ['TODAS']
            self.spinner_conta.text = 'TODAS'
        else:
            contas = self.contas_por_categoria.get(text, [])
            contas.sort()
            contas.insert(0, 'TODAS')
            self.spinner_conta.values = contas
            self.spinner_conta.text = 'TODAS'                     

    def _atualizar_fundo(self, instance, value):
        """Atualiza o retângulo de fundo"""
        if hasattr(self, 'main_rect'):
            self.main_rect.pos = instance.pos
            self.main_rect.size = instance.size            
    
    def exportar_pdf_comparativo(self):
        """Exporta o comparativo para PDF"""
        self.mostrar_mensagem("Exportação para PDF do comparativo será implementada em breve")
    
    def exportar_pdf_anual(self):
        """Exporta a evolução anual para PDF"""
        self.mostrar_mensagem("Exportação para PDF da evolução anual será implementada em breve")
    
    def on_tab_changed(self, instance, value):
        """Quando a aba é alterada"""
        print(f"Aba alterada para: {value.text}")
    
    def voltar_dashboard(self, instance):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'