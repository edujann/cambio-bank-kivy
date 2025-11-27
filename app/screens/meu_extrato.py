from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
import datetime

# 🔥 MANTENHA TODO O RESTO DO CÓDIGO IGUAL
# A classe TelaMeuExtrato e CardTransacaoExtrato permanecem exatamente as mesmas
from kivy.clock import Clock

class CardTransacaoExtrato(BoxLayout):
    def __init__(self, transacao, **kwargs):
        # 🔥 DEFINIR CORES PRIMEIRO
        self.COR_FUNDO_CARD = (0.15, 0.20, 0.28, 1)
        self.COR_BORDA = (0.25, 0.35, 0.55, 0.3)
        self.COR_TEXTO_PRIMARIO = (0.95, 0.96, 0.98, 1)
        self.COR_TEXTO_SECUNDARIO = (0.70, 0.75, 0.85, 1)
        self.COR_CREDITO = (0.18, 0.80, 0.44, 1)
        self.COR_DEBITO = (0.91, 0.30, 0.24, 1)
        self.COR_SALDO_POSITIVO = (0.20, 0.60, 0.86, 1)
        self.COR_SALDO_NEGATIVO = (0.91, 0.30, 0.24, 1)
        
        super().__init__(**kwargs)
        
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)  # 🔥 Altura moderna
        self.padding = [15, 8, 15, 8]  # 🔥 Padding moderno
        self.spacing = dp(10)
        self.transacao = transacao
        
        self._setup_background()
        self.criar_conteudo_moderno(transacao)
    
    def _setup_background(self):
        """Configura o background do card"""
        with self.canvas.before:
            # Fundo principal
            Color(*self.COR_FUNDO_CARD)
            self.rect_bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]  # 🔥 Bordas arredondadas modernas
            )
            # Borda sutil
            Color(*self.COR_BORDA)
            self.rect_border = RoundedRectangle(
                pos=[self.pos[0]-1, self.pos[1]-1],
                size=[self.size[0]+2, self.size[1]+2],
                radius=[9,]
            )
        
        # Vincular atualização de posição/tamanho
        self.bind(pos=self._update_background, size=self._update_background)
    
    def _update_background(self, *args):
        """Atualiza o background quando o widget muda"""
        if hasattr(self, 'rect_bg'):
            self.rect_bg.pos = self.pos
            self.rect_bg.size = self.size
        
        if hasattr(self, 'rect_border'):
            self.rect_border.pos = [self.pos[0]-1, self.pos[1]-1]
            self.rect_border.size = [self.size[0]+2, self.size[1]+2]
    
    def formatar_data_apenas_dia_mes_ano(self, data_string):
        """Formata a data para mostrar apenas DD/MM/AAAA, removendo o horário"""
        # 🔥 CORREÇÃO: Se data é None ou vazia, retornar string vazia
        if not data_string or data_string == 'None' or data_string is None:
            return ""  # 🔥 RETORNAR STRING VAZIA EM VEZ DE None
        
        try:
            # 🔥🔥🔥 CORREÇÃO CRÍTICA: FORMATO CORROMPIDO "26T15:22:51/11/2025"
            # Este formato aparece quando transferências vão para "processing"
            if 'T' in data_string and '/' in data_string:
                try:
                    # Formato: "26T15:22:51/11/2025"
                    dia = data_string.split('T')[0]  # "26"
                    resto = data_string.split('T')[1]  # "15:22:51/11/2025"
                    mes_ano = resto.split('/')  # ["15:22:51", "11", "2025"]
                    if len(mes_ano) >= 3:
                        mes = mes_ano[1]  # "11"
                        ano = mes_ano[2]  # "2025"
                        data_corrigida = f"{dia}/{mes}/{ano}"
                        print(f"🔧 DATA CORRIGIDA: '{data_string}' -> '{data_corrigida}'")
                        return data_corrigida
                except Exception as e:
                    print(f"⚠️ Erro ao corrigir formato corrompido '{data_string}': {e}")
            
            # Se for formato com 'T' (ISO): 2025-11-15T17:15:24
            if 'T' in data_string:
                data_parte = data_string.split('T')[0]
                partes = data_parte.split('-')
                if len(partes) == 3:
                    return f"{partes[2]}/{partes[1]}/{partes[0]}"
            
            # Se for formato com espaço: 2025-11-15 17:15:24
            elif ' ' in data_string:
                data_parte = data_string.split(' ')[0]
                partes = data_parte.split('-')
                if len(partes) == 3:
                    return f"{partes[2]}/{partes[1]}/{partes[0]}"
            
            # Se já estiver no formato correto ou outro formato
            return data_string
            
        except Exception as e:
            print(f"⚠️ Erro ao formatar data '{data_string}': {e}")
            return data_string

    def criar_conteudo_moderno(self, transacao):
        """Cria conteúdo moderno para o card - APENAS LARGURAS AJUSTADAS"""
        
        # 🔥🔧 CORREÇÃO: FORMATAR DATA CORRETAMENTE - APENAS DIA/MÊS/ANO
        data_original = transacao.get('data', '')
        data_formatada = self.formatar_data_apenas_dia_mes_ano(data_original)
        
        # 🔥 NOVAS LARGURAS AJUSTADAS:
        # Data: 12% (era 15%) - Reduzida para dar mais espaço à descrição
        # Descrição: 48% (era 35%) - AUMENTADA significativamente
        # Crédito: 10% (era 12.5%) - Reduzida
        # Débito: 10% (era 12.5%) - Reduzida 
        # Saldo: 12% (era 15%) - Reduzida
        # Detalhes: 8% (era 10%) - Reduzida
        
        # 🔥 COLUNA 1: DATA (12%) - ESTILO MODERNO (SEM ÍCONE)
        col_data = BoxLayout(orientation='vertical', size_hint_x=0.12, padding=[0, 2])
        lbl_data_dia = Label(
            text=data_formatada.split('/')[0] if data_formatada and '/' in data_formatada else '',
            font_size='16sp',
            bold=True,
            color=self.COR_TEXTO_PRIMARIO,
            text_size=(None, None),
            halign='center'
        )
        lbl_data_mes = Label(
            text=f"{data_formatada.split('/')[1]}/{data_formatada.split('/')[2][-2:]}" if data_formatada and '/' in data_formatada and len(data_formatada.split('/')) >= 3 else '',
            font_size='11sp',
            color=self.COR_TEXTO_SECUNDARIO,
            text_size=(None, None),
            halign='center'
        )
        col_data.add_widget(lbl_data_dia)
        col_data.add_widget(lbl_data_mes)
        
        # 🔥 COLUNA 2: DESCRIÇÃO (48%) - MUITO MAIS LARGA (SEM ÍCONE)
        col_descricao = BoxLayout(orientation='vertical', size_hint_x=0.48)
        lbl_descricao = Label(
            text=transacao.get('descricao', ''),
            font_size='12sp',
            color=self.COR_TEXTO_PRIMARIO,
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        col_descricao.add_widget(lbl_descricao)
        
        # 🔥 COLUNA 3: CRÉDITO (10%) - DESTAQUE VERDE
        col_credito = BoxLayout(orientation='vertical', size_hint_x=0.10)
        credito = transacao.get('credito', 0)
        lbl_credito = Label(
            text=f"+{credito:,.2f}" if credito > 0 else "",
            font_size='13sp',
            bold=True if credito > 0 else False,
            color=self.COR_CREDITO if credito > 0 else self.COR_TEXTO_SECUNDARIO,
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_credito.add_widget(lbl_credito)
        
        # 🔥 COLUNA 4: DÉBITO (10%) - DESTAQUE VERMELHO
        col_debito = BoxLayout(orientation='vertical', size_hint_x=0.10)
        debito = transacao.get('debito', 0)
        lbl_debito = Label(
            text=f"-{debito:,.2f}" if debito > 0 else "",
            font_size='13sp',
            bold=True if debito > 0 else False,
            color=self.COR_DEBITO if debito > 0 else self.COR_TEXTO_SECUNDARIO,
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_debito.add_widget(lbl_debito)
        
        # 🔥 COLUNA 5: SALDO (12%) - AZUL DO RESUMO PARA POSITIVO, VERMELHO PARA NEGATIVO
        col_saldo = BoxLayout(orientation='vertical', size_hint_x=0.12)
        saldo_apos = transacao.get('saldo_apos', 0)
        
        # 🔥 NOVA COR PARA SALDO - Azul do resumo para positivo, Vermelho para negativo
        # Azul do resumo: (0.23, 0.51, 0.96, 1) - mesma cor do "Saldo Total" no resumo
        cor_saldo = self.COR_DEBITO if saldo_apos < 0 else (0.20, 0.70, 0.95, 1)
        
        lbl_saldo = Label(
            text=f"{saldo_apos:,.2f}",  # 🔥 SEM ÍCONE
            font_size='12sp',
            bold=True,
            color=cor_saldo,
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_saldo.add_widget(lbl_saldo)
        
        # 🔥 COLUNA 6: BOTÃO DETALHES (8%) - ESTILO MODERNO E CENTRALIZADO
        col_detalhes = BoxLayout(orientation='vertical', size_hint_x=0.08, padding=[0, 15, 0, 0])
        
        btn_detalhes = Button(
            text='Detalhes',
            font_size='14sp',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.25, 0.35, 0.55, 0.3),
            background_normal='',
            color=self.COR_TEXTO_PRIMARIO,
            on_press=self.mostrar_detalhes_transacao
        )
        
        col_detalhes.add_widget(btn_detalhes)
        
        # Adicionar todas as colunas
        self.add_widget(col_data)
        self.add_widget(col_descricao)
        self.add_widget(col_credito)
        self.add_widget(col_debito)
        self.add_widget(col_saldo)
        self.add_widget(col_detalhes)
        
    def obter_icone_por_tipo(self, tipo):
        """Retorna ícone baseado no tipo de transação"""
        icones = {
            'Transferência': '💸',
            'Câmbio': '🔄', 
            'Crédito Admin': '📥',
            'Débito Admin': '📤',
            'Estorno': '↩️',
            'Taxa/Despesa': '💳',
            'Saldo Inicial': '🏦'
        }
        return icones.get(tipo, '📄')
    
    def mostrar_detalhes_transacao(self, instance):
        """Mostra popup com todos os detalhes da transação"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        lbl_titulo = Label(
            text='DETALHES DA TRANSAÇÃO',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(450, None),
            halign='center',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Container para os detalhes
        detalhes_container = BoxLayout(orientation='vertical', spacing=10, padding=[10, 10])
        
        # 🔥 FORMATAR TODOS OS DETALHES DA TRANSAÇÃO
        detalhes = self.formatar_detalhes_transacao()
        
        for chave, valor in detalhes.items():
            linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            
            lbl_chave = Label(
                text=f"{chave}:",
                font_size='14sp',
                bold=True,
                color=(0.8, 0.8, 0.8, 1),
                text_size=(180, None),
                halign='left',
                valign='middle'
            )
            
            lbl_valor = Label(
                text=str(valor),
                font_size='14sp',
                color=(1, 1, 1, 1),
                text_size=(250, None),
                halign='left',
                valign='middle'
            )
            
            linha.add_widget(lbl_chave)
            linha.add_widget(lbl_valor)
            detalhes_container.add_widget(linha)
        
        # Botão fechar
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=dp(45),
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(detalhes_container)
        content.add_widget(btn_fechar)
        
        # Criar popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(550, 600),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()
    
    def formatar_detalhes_transacao(self):
        """Formata todos os detalhes da transação para exibição"""
        transacao = self.transacao
        
        detalhes = {
            'Data': transacao.get('data', 'N/A'),
            'Descrição': transacao.get('descricao', 'N/A'),
            'Tipo': transacao.get('tipo', 'N/A'),
            'Moeda': transacao.get('moeda', 'N/A'),
            'Valor Crédito': f"{transacao.get('credito', 0):,.2f}" if transacao.get('credito', 0) > 0 else '0.00',
            'Valor Débito': f"{transacao.get('debito', 0):,.2f}" if transacao.get('debito', 0) > 0 else '0.00',
            'Saldo Após': f"{transacao.get('saldo_apos', 0):,.2f}",
            'ID Transação': transacao.get('id', 'N/A')
        }
        
        # 🔥 ADICIONAR INFORMAÇÕES ESPECÍFICAS BASEADAS NO TIPO
        tipo = transacao.get('tipo', '')
        
        if 'Transferência' in tipo:
            detalhes['Status'] = self.extrair_status_da_descricao(transacao.get('descricao', ''))
            detalhes['Tipo Transferência'] = 'Internacional' if 'INTERNACIONAL' in transacao.get('descricao', '').upper() else 'Interna'
        
        elif 'Câmbio' in tipo:
            detalhes['Operação'] = 'Compra' if transacao.get('credito', 0) > 0 else 'Venda'
        
        elif 'Estorno' in tipo:
            detalhes['Motivo'] = 'Transferência Rejeitada'
        
        elif 'Admin' in tipo:
            detalhes['Tipo Ajuste'] = 'Crédito' if transacao.get('credito', 0) > 0 else 'Débito'
        
        return detalhes
    
    def extrair_status_da_descricao(self, descricao):
        """Extrai o status da transferência da descrição"""
        desc_upper = descricao.upper()
        if 'SOLICITADA' in desc_upper:
            return 'Solicitada'
        elif 'EM PROCESSAMENTO' in desc_upper:
            return 'Em Processamento'
        elif 'CONCLUÍDA' in desc_upper:
            return 'Concluída'
        elif 'RECUSADA' in desc_upper:
            return 'Recusada'
        else:
            return 'Status Desconhecido'


class TelaMeuExtrato(Screen):
    """Tela de extrato do cliente - MESMA LÓGICA DO Tkinter"""
    
    def __init__(self, **kwargs):
        # 🔥 INICIALIZAR CORES PRIMEIRO (ANTES do super())
        self.COR_PRIMARIA = (0.20, 0.36, 0.80, 1)      # Azul vibrante
        self.COR_SECUNDARIA = (0.4, 0.4, 0.45, 1)    # Roxo
        self.COR_SUCESSO = (0.18, 0.80, 0.44, 1)       # Verde moderno
        self.COR_ERRO = (0.91, 0.30, 0.24, 1)          # Vermelho moderno
        self.COR_AVISO = (0.95, 0.61, 0.07, 1)         # Laranja
        self.COR_FUNDO = (0.05, 0.08, 0.13, 1)         # Preto azulado escuro
        self.COR_CARD = (0.12, 0.16, 0.23, 1)          # Card escuro
        self.COR_TEXTO = (0.93, 0.94, 0.95, 1)         # Texto branco suave
        self.COR_TEXTO_SECUNDARIO = (0.70, 0.73, 0.78, 1)  # Texto cinza
        
        # 🔥 AGORA CHAMAR SUPER()
        super().__init__(**kwargs)
        
        # Resto do código existente...
        self.transacoes_carregadas = []
        self.periodo_var = "30"
        self.saldo_final = 0
        self.total_entradas = 0
        self.total_saidas = 0
        self.transacoes_filtradas = []
        self.pdf_generator = None
    
    def get_pdf_generator(self):
        """Obtém o PDF Generator - cria se não existir"""
        if self.pdf_generator is None:
            try:
                import sys
                import os
                
                # 🔥 FORÇAR O CAMINHO ABSOLUTO
                project_root = r"C:\Users\Usuário\Desktop\cambio_bank_kivy"
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)  # 🔥 COLOCAR NO INÍCIO
                
                print(f"🔍 Tentando importar de: {project_root}")
                print(f"🔍 Arquivos no diretório: {os.listdir(project_root)}")
                
                # 🔥 CORREÇÃO: O arquivo se chama pdf_generator.py (minúsculo)
                from pdf_generator import PDFGenerator
                self.pdf_generator = PDFGenerator()
                print("✅ PDF Generator inicializado com sucesso!")
            except ImportError as e:
                print(f"❌ Erro ao importar PDFGenerator: {e}")
                print(f"🔍 sys.path: {sys.path}")
                return None
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                return None
        
        return self.pdf_generator
    
    def formatar_data_para_br(self, data_iso):
        """Converte data de AAAA-MM-DD para DD/MM/AAAA"""
        try:
            partes = data_iso.split('-')
            if len(partes) == 3:
                return f"{partes[2]}/{partes[1]}/{partes[0]}"
        except:
            pass
        return data_iso

    def formatar_data_para_iso(self, data_br):
        """Converte data de DD/MM/AAAA para AAAA-MM-DD"""
        try:
            partes = data_br.split('/')
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
        except:
            pass
        return data_br

    def aplicar_mascara_data(self, instance, value):
        """Aplica máscara de data DD/MM/AAAA - VERSÃO SIMPLIFICADA"""
        # Evitar loop
        if getattr(instance, '_processing', False):
            return
            
        instance._processing = True
        
        try:
            # Remover qualquer caractere que não seja número e barras
            texto_limpo = ''.join(c for c in value if c.isdigit())
            
            # Limitar a 8 dígitos
            if len(texto_limpo) > 8:
                texto_limpo = texto_limpo[:8]
            
            # Aplicar formatação
            texto_formatado = ""
            if len(texto_limpo) > 0:
                texto_formatado = texto_limpo[0:2]
            if len(texto_limpo) > 2:
                texto_formatado += '/' + texto_limpo[2:4]
            if len(texto_limpo) > 4:
                texto_formatado += '/' + texto_limpo[4:8]
            
            # Só atualizar se mudou
            if texto_formatado != instance.text:
                instance.unbind(text=self.aplicar_mascara_data)
                instance.text = texto_formatado
                instance.bind(text=self.aplicar_mascara_data)
                
                # 🔥 SOLUÇÃO: SEMPRE colocar cursor no FINAL
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
                
            # Converter para inteiros
            dia_int, mes_int, ano_int = int(dia), int(mes), int(ano)
            
            # Validar ranges básicos
            if mes_int < 1 or mes_int > 12:
                return False
            if dia_int < 1 or dia_int > 31:
                return False
            if ano_int < 1900 or ano_int > 2100:
                return False
                
            return True
        except:
            return False

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1400, 1000)
        
        # 🔥 AGENDAR POSICIONAMENTO
        from kivy.clock import Clock
        Clock.schedule_once(self._reposicionar_janela, 0.1)
        
        self.carregar_dados_iniciais()
    
    def _reposicionar_janela(self, dt):
        """Reposiciona a janela após um pequeno delay"""
        from kivy.core.window import Window
        Window.left = 300
        Window.top = 70
        print("✅ Janela de extrato reposicionada para esquerda")
    
    def on_enter(self):
        """Chamado quando a tela é carregada - AGORA CARREGA EXTRATO AUTOMATICAMENTE"""
        from kivy.core.window import Window
        from kivy.clock import Clock
        
        print("📊 Tela Meu Extrato carregada")
        
        # 🔥 GARANTIR POSIÇÃO NOVAMENTE
        Window.left = 300
        Window.top = 70
        
        # 🔥 PRIMEIRO GARANTIR QUE OS DADOS INICIAIS ESTÃO CARREGADOS
        self.carregar_dados_iniciais()
        
        # 🔥 DEPOIS CARREGAR EXTRATO COM UM PEQUENO DELAY
        Clock.schedule_once(lambda dt: self.carregar_extrato(), 0.8)
        
        # 🔥 NOVO: Rolar para o topo quando a tela é aberta
        Clock.schedule_once(lambda dt: self.scroll_para_topo(), 1.0)

    def atualizar_saldo_superior(self):
        """Atualiza o saldo mostrado na parte superior da tela"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or not self.ids.combo_contas.text:
            return
            
        try:
            conta_filtro = self.ids.combo_contas.text
            conta_numero = conta_filtro.split(' - ')[0].strip()
            
            if conta_numero in sistema.contas:
                dados_conta = sistema.contas[conta_numero]
                saldo = dados_conta['saldo']
                moeda = dados_conta['moeda']
                
                # 🔥 ATUALIZAR O LABEL DO SALDO SUPERIOR
                self.ids.lbl_saldo_total.text = f"{saldo:,.2f} {moeda}"
                
                # 🔥 INICIALIZAR ENTRADAS E SAÍDAS COM ZERO
                self.ids.lbl_total_entradas.text = f"0.00 {moeda}"
                self.ids.lbl_total_saidas.text = f"0.00 {moeda}"
                self.ids.lbl_total_transacoes.text = "0"
                self.ids.lbl_periodo.text = "Últimos 30 dias"
                
                print(f"✅ Saldo superior atualizado: {saldo:,.2f} {moeda}")
                
        except Exception as e:
            print(f"Erro ao atualizar saldo superior: {e}")

    def carregar_dados_iniciais(self):
        """Carrega dados iniciais da tela"""
        sistema = App.get_running_app().sistema
        
        # Verificar se é cliente
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            self.voltar_dashboard()
            return
        
        # Carregar contas do cliente
        self.carregar_contas_cliente()
        
        # Configurar período padrão
        if hasattr(self, 'ids'):
            self.periodo_var = "30"  # 30 dias padrão
            
            # 🔥 MUDANÇA AQUI: Setar data atual no formato BR
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
            self.ids.entry_data_fim.text = data_atual  # 🔥 DATA ATUAL
            self.ids.entry_data_inicio.text = "01/01/2024"
            
            # 🔥 CONFIGURAR MÁSCARAS NOS CAMPOS DE DATA
            self.ids.entry_data_inicio.bind(text=self.aplicar_mascara_data)
            self.ids.entry_data_fim.bind(text=self.aplicar_mascara_data)
            
            # 🔥 CONFIGURAR EVENTOS DE FOCO CORRETOS
            self.ids.entry_data_inicio.bind(focus=self.on_focus_data_inicio)
            self.ids.entry_data_fim.bind(focus=self.on_focus_data_fim)
            
            # 🔥 ATUALIZAR SALDO NA PARTE SUPERIOR DA TELA
            self.atualizar_saldo_superior()
    
    def carregar_contas_cliente(self):
        """Carrega as contas do cliente no combo"""
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados do usuário corretamente
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        
        contas_opcoes = []
        for conta_num in usuario_data.get('contas', []):
            if conta_num in sistema.contas:
                dados_conta = sistema.contas[conta_num]
                contas_opcoes.append(f"{conta_num} - {dados_conta['moeda']} (Saldo: {dados_conta['saldo']:,.2f})")
        
        if not contas_opcoes:
            self.mostrar_erro("Você não possui contas cadastradas!")
            return
        
        if hasattr(self, 'ids'):
            self.ids.combo_contas.values = contas_opcoes
            self.ids.combo_contas.text = contas_opcoes[0]
    
    def definir_periodo(self, periodo):
        """Define o período selecionado - VERSÃO CORRIGIDA"""
        self.periodo_var = periodo
        print(f"🔧 Período definido para: {periodo}")  # DEBUG
        
        # 🔥 DESMARCAR TODOS OS BOTÕES DE PERÍODO RÁPIDO SE FOR PERSONALIZADO
        if periodo == "personalizado":
            # Não fazer nada - manter personalizado ativo
            pass
    
    def usar_periodo_personalizado(self, forcar_validacao=False):
        """Define o período como personalizado - VERSÃO CORRIGIDA QUE RECARREGA O EXTRATO"""
        print("🔧 Usando período personalizado...")  # DEBUG
        
        # 🔥 DEFINIR EXPLICITAMENTE COMO PERSONALIZADO
        self.definir_periodo("personalizado")
        
        # 🔥 SÓ VALIDAR SE FOR EXPLICITAMENTE SOLICITADO (botão "Usar")
        if forcar_validacao:
            # Validar as datas atuais
            data_inicio_br = self.ids.entry_data_inicio.text
            data_fim_br = self.ids.entry_data_fim.text
            
            print(f"🔧 Datas: {data_inicio_br} até {data_fim_br}")  # DEBUG
            
            if not self.validar_data_br(data_inicio_br):
                self.mostrar_erro("Data inicial inválida! Use DD/MM/AAAA")
                return
                
            if not self.validar_data_br(data_fim_br):
                self.mostrar_erro("Data final inválida! Use DD/MM/AAAA")
                return
            
            # 🔥 AGORA RECARREGAR O EXTRATO AUTOMATICAMENTE
            self.mostrar_sucesso(f"Período personalizado definido: {data_inicio_br} a {data_fim_br}")
            
            # 🔥 RECARREGAR EXTRATO COM UM PEQUENO DELAY PARA O POPUP FECHAR
            Clock.schedule_once(lambda dt: self.carregar_extrato(), 0.5)

    def on_focus_data_inicio(self, instance, value):
        """Manipula o foco no campo data início - VERSÃO CORRIGIDA"""
        if value:  # Quando ganha foco
            print("🔧 Foco no campo data início")
            # 🔥 NÃO CHAMAR usar_periodo_personalizado AUTOMATICAMENTE
            # Apenas definir como personalizado sem validação
            self.definir_periodo("personalizado")

    def on_focus_data_fim(self, instance, value):
        """Manipula o foco no campo data fim - VERSÃO CORRIGIDA"""
        if value:  # Quando ganha foco
            print("🔧 Foco no campo data fim")
            # 🔥 NÃO CHAMAR usar_periodo_personalizado AUTOMATICAMENTE
            # Apenas definir como personalizado sem validação
            self.definir_periodo("personalizado")

    def limpar_extrato(self):
        """Limpa a visualização do extrato"""
        if hasattr(self, 'ids'):
            container = self.ids.lista_transacoes
            container.clear_widgets()
            
            # Mostrar mensagem de carregamento
            from kivy.uix.label import Label
            lbl_carregando = Label(
                text="Carregando extrato...",
                font_size='14sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(lbl_carregando)

    def processar_cambio_nova_tela(self, dados, conta_num, transacoes, transacoes_ids_utilizados, parse_data):
        """Processa operações de câmbio da nova tela - igual ao cliente"""
        
        # Verificar se é uma operação de câmbio da nova tela
        if dados.get('tipo') != 'cambio' or 'conta_origem' not in dados:
            return False
        
        # Verificar se envolve nossa conta
        if dados.get('conta_origem') != conta_num and dados.get('conta_destino') != conta_num:
            return False
        
        sistema = App.get_running_app().sistema
        moeda = sistema.contas[conta_num]['moeda']
        
        try:
            # CLIENTE É ORIGEM (SAÍDA/DÉBITO)
            if dados.get('conta_origem') == conta_num:
                descricao = f"CÂMBIO ENVIADO - {dados.get('moeda_origem', 'N/A')} → {dados.get('moeda_destino', 'N/A')}"
                
                nova_transacao = {
                    'data': dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'descricao': descricao,
                    'credito': 0.00,
                    'debito': dados.get('valor_origem', 0),
                    'tipo': "Câmbio",
                    'moeda': dados.get('moeda_origem', moeda),
                    'timestamp': parse_data(dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    'id': dados.get('id', '')  # 🔥 CORREÇÃO AQUI
                }
                
                transacoes.append(nova_transacao)
                transacoes_ids_utilizados.add(dados.get('id', ''))  # 🔥 CORREÇÃO AQUI
                return True
            
            # CLIENTE É DESTINO (ENTRADA/CRÉDITO)
            elif dados.get('conta_destino') == conta_num:
                descricao = f"CÂMBIO RECEBIDO - {dados.get('moeda_origem', 'N/A')} → {dados.get('moeda_destino', 'N/A')}"
                
                nova_transacao = {
                    'data': dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'descricao': descricao,
                    'credito': dados.get('valor_destino', 0),
                    'debito': 0.00,
                    'tipo': "Câmbio",
                    'moeda': dados.get('moeda_destino', moeda),
                    'timestamp': parse_data(dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    'id': dados.get('id', '')  # 🔥 CORREÇÃO AQUI
                }
                
                transacoes.append(nova_transacao)
                transacoes_ids_utilizados.add(dados.get('id', ''))  # 🔥 CORREÇÃO AQUI
                return True
                
        except Exception as e:
            print(f"⚠️ Erro ao processar câmbio nova tela: {e}")
        
        return False

    def carregar_extrato(self):
        """Carrega o extrato - VERSÃO CORRIGIDA COM RECEITAS E SALDO INICIAL"""
        
        # ========== 🔍 DEBUG CRÍTICO - COLOCAR AQUI ==========
        sistema = App.get_running_app().sistema
        
        print("=== 🔍 HISTÓRICO COMPLETO DO AJUSTE ===")
        
        # 1. Verificar logs do sistema durante o ajuste
        print("📋 Buscando por logs do ajuste...")
        for trans_id, dados in sistema.transferencias.items():
            if (dados.get('valor') == 10000 and 
                dados.get('tipo_ajuste') == 'CREDITO' and
                'ajuste' in str(dados).lower()):
                print(f"💰 POSSÍVEL AJUSTE: {trans_id}")
                print(f"   Conta: {dados.get('conta_remetente')}")
                print(f"   Data: {dados.get('data')}")
                print(f"   Executado por: {dados.get('executado_por')}")
                print(f"   Sincronizado: {dados.get('sincronizado_supabase', 'N/A')}")
        
        # 2. Verificar se há transações "fantasma"
        print("\n=== 🔍 TRANSAÇÕES RECENTES DA CONTA 607906288 ===")
        for trans_id, dados in sistema.transferencias.items():
            if (dados.get('conta_remetente') == '607906288' or 
                dados.get('conta_destinatario') == '607906288'):
                data = dados.get('data', '')
                if '2025-11-21' in data:  # Transações de hoje
                    print(f"📅 {data} | {dados.get('tipo')} | Valor: {dados.get('valor')} | Status: {dados.get('status')}")
        # ========== FIM DO DEBUG ==========
        print("🔄 INICIANDO carregar_extrato...")  
        
        # 🔥 LIMPAR EXTRATO ANTES DE CARREGAR NOVOS DADOS
        self.limpar_extrato()
        
        sistema = App.get_running_app().sistema
        
        # ✅ DEBUG CRÍTICO - VERIFICAR DE ONDE VÊM AS TRANSAÇÕES
        print(f"🔍 DEBUG: Sistema tem {len(sistema.transferencias)} transferências totais")
        
        # 🔥 DEBUG: Verificar qual período está ativo
        print(f"🔧 Período ativo: {getattr(self, 'periodo_var', 'N/A')}")
        
        # Validar seleção de conta
        if not hasattr(self, 'ids') or not self.ids.combo_contas.text:
            self.mostrar_erro("Selecione uma conta!")
            return
        
        conta_filtro = self.ids.combo_contas.text
        conta_num = conta_filtro.split(' - ')[0].strip()  # 🔥 ESTA É A VARIÁVEL CORRETA
        
        print(f"🔍 DEBUG: Conta selecionada: {conta_num}")
        
        if conta_num not in sistema.contas:
            self.mostrar_erro("Conta não encontrada!")
            return
        
        dados_conta = sistema.contas[conta_num]
        moeda = dados_conta['moeda']
        saldo_atual = dados_conta['saldo']


        # ========== 🔥 🔥 🔥 AQUI COLOCA O DEBUG NOVO! ==========
        # ✅ DEBUG CRÍTICO - VERIFICAR SE O AJUSTE ESTÁ SENDO PROCESSADO
        print("=== 🔍 DEBUG PROCESSAMENTO DO AJUSTE ===")
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
        
        # 🔥 DETERMINAR PERÍODO DO FILTRO - USAR self.periodo_var
        periodo = getattr(self, 'periodo_var', '30')
        data_inicio_filtro = None
        data_fim_filtro = None
        
        print(f"🔧 Aplicando filtro do período: {periodo}")
        
        # 🔥 VARIÁVEL: Saldo inicial do período (para TODOS os períodos)
        saldo_inicial_periodo = 0.0
        
        if periodo == "personalizado":
            try:
                # Converter de DD/MM/AAAA para AAAA-MM-DD
                data_inicio_br = self.ids.entry_data_inicio.text
                data_fim_br = self.ids.entry_data_fim.text
                
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
                saldo_inicial_periodo = self.calcular_saldo_ate_data(conta_num, data_dia_anterior)
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
                
                # 🔍 DEBUG ESPECÍFICO PARA A TRANSFERÊNCIA NOVA
                if transferencia_id == "520676":
                    print(f"🔍 DEBUG 520676: Data='{dados.get('data')}' | Tipo='{dados.get('tipo')}' | Status='{dados.get('status')}'")
                    print(f"🔍 DEBUG 520676: Estrutura completa: {dados}")
                
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
                        # 🔍 DEBUG TEMPORÁRIO PARA RASTREAR TRANSFERÊNCIA 520676
                        if transferencia_id == "520676":
                            print(f"✅✅✅ TRANSFERÊNCIA 520676 PASSOU NO FILTRO PRINCIPAL!")
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
                        if transferencia_id == "520676":
                            print(f"🚫 TRANSFERÊNCIA 520676 NÃO PASSOU NO FILTRO: valor_valido={valor_valido}, dados_validos={dados_validos}, nao_e_cambio_zerado={nao_e_cambio_zerado}")
                        # DEBUG opcional para ver o que está sendo filtrado
                        # print(f"🚫 FILTRADA: ID {transferencia_id} - Valor: {valor}, Descrição: {dados.get('descricao')}, Tipo: {dados.get('tipo')}")
            
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
                
                saldo_inicial_periodo = self.calcular_saldo_ate_data(conta_num, data_dia_anterior)
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




        # 🔥 🔥 🔥 DEBUG ESPECÍFICO PARA A TRANSAÇÃO 408044_nt
        print("=== 🚨 DEBUG ESPECÍFICO 408044_nt ===")
        if "408044_nt" in sistema.transferencias:
            dados_408044 = sistema.transferencias["408044_nt"]
            print(f"🔍 TRANSAÇÃO 408044_nt ENCONTRADA:")
            print(f"   Tipo: {dados_408044.get('tipo')}")
            print(f"   Conta remetente: {dados_408044.get('conta_remetente')}") 
            print(f"   Conta destinatario: {dados_408044.get('conta_destinatario')}")
            print(f"   Moeda: {dados_408044.get('moeda')}")
            print(f"   Valor: {dados_408044.get('valor')}")
            print(f"   Tem conta_origem? {'conta_origem' in dados_408044}")
            if 'conta_origem' in dados_408044:
                print(f"   Conta origem: {dados_408044.get('conta_origem')}")
                print(f"   Conta destino: {dados_408044.get('conta_destino')}")
        else:
            print("❌ 408044_nt NÃO ENCONTRADA NO SISTEMA")

        # 🔥 🔥 🔥 NOVO: PROCESSAR OPERACOES DE CAMBIO DA NOVA TELA PRIMEIRO
        for transferencia_id, dados in sistema.transferencias.items():
            if not dados or not isinstance(dados, dict):
                continue
                
            # 🔥 DEBUG: RASTREAR PROCESSAMENTO DA 408044_nt
            if transferencia_id == "408044_nt":
                print(f"🎯🎯🎯 408044_nt NO PRIMEIRO LOOP")
                print(f"   Passa no filtro '_nt'? {('_nt' in transferencia_id or '_novatela' in transferencia_id)}")
                print(f"   Já processada? {transferencia_id in transacoes_ids_utilizados}")
                print(f"   Tem conta_origem? {'conta_origem' in dados}")
                print(f"   Vai chamar processar_cambio_nova_tela? {('conta_origem' in dados)}")


                
            # Tentar processar APENAS operacoes da nova tela
            if self.processar_cambio_nova_tela(dados, conta_num, transacoes_todas, transacoes_ids_utilizados, parse_data):
                # Se processou, já foi adicionada às transacoes_todas
                pass

        # 🔥 PASSO 2: CRIAR TODAS AS TRANSAÇÕES COM PROCESSAMENTO DE RECEITAS
        for transferencia_id, dados in sistema.transferencias.items():
            
            # 🔥 DEBUG: RASTREAR PROCESSAMENTO DA 408044_nt
            if transferencia_id == "408044_nt":
                print(f"🎯🎯🎯 408044_nt NO SEGUNDO LOOP")
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
            
            # 🔥 🔥 🔥 CORREÇÃO CRÍTICA: PROCESSAR RECEITAS PRIMEIRO (MESMA LÓGICA DO ADMIN)
            if tipo == 'receita' or 'receita' in str(tipo).lower():
                print(f"✅ ENCONTRADA RECEITA NO MEU EXTRATO: {transferencia_id}")
                
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
                
                print(f"💰 RECEITA DEBUG: remetente='{conta_remetente}', destinatario='{conta_destinatario}', conta_num='{conta_num}'")
                print(f"💰 DESCRIÇÃO FINAL: '{descricao_receita}'")
                
                # 🔥 CORREÇÃO: Se a conta remetente é a nossa conta, é um DÉBITO (saída)
                if conta_remetente == conta_num:
                    nova_transacao = {
                        'data': data_receita,
                        'descricao': descricao_receita,  # 🔥 APENAS A DESCRIÇÃO LIMPA
                        'credito': 0.00,
                        'debito': valor_receita,
                        'tipo': "Taxa/Despesa",  # 🔥 TIPO CORRETO PARA CLIENTE
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
                        'tipo': "Taxa/Despesa",  # 🔥 TIPO CORRETO PARA CLIENTE
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
            
            # 🔍 DEBUG 2: VERIFICAR CONTA ANTES DO FILTRO
            if transferencia_id == "520676":
                print(f"🎯🎯🎯 DEBUG 520676 - ANTES DO FILTRO DE CONTA")
                print(f"🎯🎯🎯 Conta remetente: {dados.get('conta_remetente')}, Conta destinatario: {dados.get('conta_destinatario')}")
                print(f"🎯🎯🎯 Nossa conta: {conta_num}, Conta envolvida: {dados['conta_remetente'] == conta_num or dados.get('conta_destinatario') == conta_num}")

            # Verificar se a transação envolve nossa conta
            conta_envolvida = (
                dados['conta_remetente'] == conta_num or 
                dados.get('conta_destinatario') == conta_num
            )
            
            if not conta_envolvida:
                continue
            
            # Verificar filtro de data (apenas para períodos rápidos)
            #if periodo != "0" and data_inicio_filtro:
            #    try:
            #        data_transacao = datetime.datetime.strptime(dados['data'].split(' ')[0], "%Y-%m-%d")
            #        if data_transacao < data_inicio_filtro or data_transacao > data_fim_filtro:
            #            continue
            #    except:
            #        pass
            
            # MESMA LÓGICA DE DECISÃO DO TKINTER
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
            
            # 🔥 CONTINUAR COM A LÓGICA ORIGINAL DE CRIAÇÃO DAS TRANSAÇÕES
            
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
                    # 🔍 DEBUG 3: PROCESSAMENTO DE TRANSFERÊNCIA INTERNACIONAL
                    if transferencia_id == "520676":
                        print(f"🎯🎯🎯 DEBUG 520676 - PROCESSANDO COMO TRANSFERÊNCIA INTERNACIONAL")
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
                            print(f"🔧🔧🔧 CORREÇÃO CRÍTICA: Data None para {transferencia_id} -> {data_transacao}")
                        
                        # 🔥 GARANTIR que a data está no formato correto
                        try:
                            if data_transacao and 'T' in data_transacao:
                                # Converter de ISO para formato com espaço
                                data_obj = datetime.datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
                                data_transacao = data_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            # Fallback para data atual
                            data_transacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
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
                        data_estorno = dados.get('data_recusa', dados.get('data_processing', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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

                        # 🔍 DEBUG 4: ANTES DE ADICIONAR AO EXTRATO
                        if transferencia_id == "520676":
                            print(f"🎯🎯🎯 DEBUG 520676 - CRIANDO TRANSAÇÃO FINAL")
                            print(f"🎯🎯🎯 Nova transação: {nova_transacao}")


                        transacoes_todas.append(nova_transacao)
                        transacoes_ids_utilizados.add(transferencia_id)
                
                # CÂMBIO (quando cliente vende moeda)
                elif tipo == 'cambio':
                    data_cambio = dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    # 🔥 MUDANÇA: Usar descrição_origem se disponível, senão criar
                    descricao = dados.get('descricao_origem', 
                        f"OPERAÇÃO DE CÂMBIO - VENDA - {dados['moeda']} {dados['valor']:,.2f} - {dados.get('taxa_cambio', 1)} - {dados.get('moeda_destino', 'N/A')} {dados.get('valor_destino', dados['valor']):,.2f}")
                    
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
                
                    
                    # TRANSFERENICA INTERNA REJEITADA
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
                        data_estorno = dados.get('data_recusa', dados.get('data_processing', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
                        data_transferencia = dados.get('data_recusa', dados.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        nova_transacao = {
                            'data': data_transferencia,
                            'descricao': f"TRANSFERÊNCIA {status_text} - {self.obter_nome_cliente_por_conta(sistema, dados.get('conta_destinatario', 'N/A'))}",
                            'credito': 0.00,
                            'debito': dados['valor'],
                            'tipo': "Transferência",
                            'moeda': dados['moeda'],
                            'timestamp': parse_data(data_transferencia),
                            'id': transferencia_id
                        }
                        
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
                    print(f"💰 DEPÓSITO ADICIONADO NO EXTRATO CLIENTE: {descricao}")
                
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
                        f"OPERAÇÃO DE CÂMBIO - COMPRA - {dados['moeda']} {dados['valor']:,.2f} - {dados.get('taxa_cambio', 1)} - {dados.get('moeda_destino', 'N/A')} {dados.get('valor_destino', dados['valor']):,.2f}")
                    
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
                        if transacao.get('id') == "520676":
                            print(f"🎯🎯🎯 DEBUG 520676 - PROCESSADA COMO TRANSFERÊNCIA SOLICITADA")
                            print(f"🎯🎯🎯 Descrição: {transacao['descricao']}")
                            print(f"🎯🎯🎯 Débito: {transacao['debito']}")


        # ✅ DEBUG FINAL - VERIFICAR SE O AJUSTE ESTÁ NA LISTA FINAL
        print("=== 🔍 DEBUG LISTA FINAL DE TRANSAÇÕES ===")
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
            
            # 🔍 DEBUG ESPECÍFICO PARA 520676
            if transacao.get('id') == "520676":
                print(f"🎯🎯🎯 DEBUG 520676 NO PROCESSAMENTO FINAL")
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
        print(f"🔍 FILTRO FINAL: {len(transacoes_todas)} transações antes do filtro")
        
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
        print(f"✅ FILTRO FINAL: {len(transacoes_todas)} transações após filtro")

        # 🔍 DEBUG CRÍTICO - VERIFICAR ONDE AS TRANSAÇÕES SÃO ADICIONADAS
        print(f"🔍 DEBUG FINAL: transacoes_todas tem {len(transacoes_todas)} itens")
        
        # Verificar a estrutura real das transações
        if transacoes_todas:
            print("🔍 ESTRUTURA DA PRIMEIRA TRANSAÇÃO:")
            print(f"   Tipo: {type(transacoes_todas[0])}")
            print(f"   Conteúdo: {transacoes_todas[0]}")
            if isinstance(transacoes_todas[0], dict):
                print(f"   Chaves: {transacoes_todas[0].keys()}")
        print(f"📊 TRANSAÇÕES APÓS FILTRO: {len(transacoes_filtradas)}")
        
        # 🔥🔥🔥 CORREÇÃO CRÍTICA: VERIFICAR E CORRIGIR DATAS None ANTES DO FILTRO
        for trans in transacoes_filtradas:
            if trans.get('data') is None or trans.get('data') == 'None':
                # Tentar obter data do timestamp
                timestamp = trans.get('timestamp')
                if timestamp:
                    trans['data'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔧 CORREÇÃO PÓS-PROCESSAMENTO: Data None corrigida para {trans.get('id')} -> {trans['data']}")
                else:
                    # Data fallback
                    trans['data'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔧 CORREÇÃO PÓS-PROCESSAMENTO: Data None com fallback para {trans.get('id')}")

        # ✅ FILTRO FINAL DEFINITIVO - REMOVER TRANSAÇÕES ZERADAS
        print(f"🔍 FILTRO FINAL DEFINITIVO: {len(transacoes_filtradas)} transações antes do filtro")

        # 🔍 DEBUG ESPECÍFICO PARA 520676
        for trans in transacoes_filtradas:
            if trans.get('id') == "520676":
                print(f"🔍 DEBUG 520676 NO FILTRO FINAL: {trans}")
                print(f"🔍 DEBUG 520676 - credito: {trans.get('credito')}, debito: {trans.get('debito')}, descricao: '{trans.get('descricao')}'")

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
                print(f"🚫 FILTRO FINAL REMOVIDA: {trans.get('id', 'N/A')} - '{descricao}'")
        
        print(f"✅ FILTRO FINAL DEFINITIVO: {len(transacoes_finais)} transações após filtro")
        
        # 🔥 DEFINIR transacoes FINALMENTE
        transacoes = transacoes_finais
        
        # 🔥 DEBUG CRÍTICO DA ORDENAÇÃO
        print("=== 🚨 DEBUG CRÍTICO DA ORDENAÇÃO ===")
        for i, trans in enumerate(transacoes[:10]):  # Mostrar primeiras 10
            timestamp = trans.get('timestamp')
            data = trans.get('data', '')
            print(f"{i}. Data: {data} | Timestamp: {timestamp} | Tipo: {type(timestamp)}")
        
        # 4. CALCULAR SALDO SEQUENCIAL CORRETAMENTE
        # Ordenar por timestamp (mais antiga primeiro) para cálculo
        transacoes_ordenadas_calculo = sorted(transacoes, key=lambda x: x.get('timestamp', datetime.datetime(2000, 1, 1)))
        
        # 🔥 VERIFICAR SE ORDENOU CORRETAMENTE
        print("=== ✅ VERIFICAÇÃO DA ORDENAÇÃO ===")
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
        print("=== DEBUG TRANSAÇÕES DETALHADO ===")
        for i, t in enumerate(transacoes_ordenadas_calculo):
            print(f"{i+1}. {t.get('data', '')} | {t.get('descricao', '')} | Crédito: {t.get('credito', 0):,.2f} | Débito: {t.get('debito', 0):,.2f} | Saldo: {t.get('saldo_apos', 0):,.2f}")

        print(f"💰 DEBUG SALDO: Atual={saldo_atual:,.2f} | Calculado={saldo_calculado_final:,.2f} | Diferença={saldo_atual - saldo_calculado_final:,.2f}")

        diferenca = saldo_atual - saldo_calculado_final
        
        # 6. ORDENAR PARA EXIBIÇÃO (mais antiga primeiro) - CORREÇÃO
        transacoes_exibicao = transacoes_ordenadas_calculo  # Já está ordenada do mais antigo para o mais recente
        
        # 7. 🔥 CALCULAR TOTAIS FINAIS (APÓS todas as correções)
        total_entradas = sum(t.get('credito', 0) for t in transacoes_exibicao)
        total_saidas = sum(t.get('debito', 0) for t in transacoes_exibicao)
        
        print(f"💰 TOTAIS CALCULADOS: Entradas={total_entradas:,.2f}, Saídas={total_saidas:,.2f}")  # DEBUG
        
        # 8. ATUALIZAR A INTERFACE
        self.atualizar_interface_extrato(transacoes_exibicao, saldo_atual, total_entradas, total_saidas, moeda, periodo)
        
        print("✅ Extrato carregado com sucesso!")



    # 🔥 🔥 🔥 ADICIONAR ESTA NOVA FUNÇÃO AUXILIAR:

    def scroll_para_topo(self):
        """Rola automaticamente para o topo da lista de transações"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'scroll_extrato'):
            # Agendar o scroll para depois que a interface for atualizada
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_extrato, 'scroll_y', 1), 0.1)

    def calcular_saldo_ate_data(self, conta_num, data_limite):
        """Calcula o saldo da conta até uma data específica (até o FINAL do dia anterior ao período)"""
        sistema = App.get_running_app().sistema
        
        if conta_num not in sistema.contas:
            return 0.0
        
        # Iniciar saldo como zero
        saldo_acumulado = 0.0
        moeda = sistema.contas[conta_num]['moeda']
        
        # Coletar TODAS as transações da conta (sem filtro de data)
        todas_transacoes = []
        
        # 🔥 ADICIONAR LÓGICA PARA COLETAR TRANSAÇÕES (SIMILAR À ORIGINAL, MAS SEM FILTRO)
        # Esta é uma versão simplificada apenas para cálculo do saldo
        
        # Adicionar saldo inicial zero
        todas_transacoes.append({
                'data': sistema.contas[conta_num].get('data_criacao', '2024-01-01 00:00:00'),
                'credito': 0.00,
                'debito': 0.00,
                'timestamp': self.parse_data_simples(sistema.contas[conta_num].get('data_criacao', '2024-01-01 00:00:00'))
            })
        
        # Coletar transações de transferências
        for transferencia_id, dados in sistema.transferencias.items():
                # 🔥 CORREÇÃO: Verificar se a transferência tem a estrutura básica necessária
                if 'conta_remetente' not in dados:
                        print(f"⚠️ Transferência {transferencia_id} sem conta_remetente, pulando...")
                        continue
                
                # Verificar se a transação envolve nossa conta
                conta_envolvida = (
                        dados['conta_remetente'] == conta_num or 
                        dados.get('conta_destinatario') == conta_num
                    )
                
                if not conta_envolvida:
                        continue
                
                # Apenas incluir transações completadas ou em processamento
                if dados['status'] not in ['completed', 'processing']:
                        continue
                
                # Determinar data da transação
                data_transacao = dados.get('data_conclusao', dados.get('data_aprovacao', dados.get('data_solicitacao', dados.get('data', '2024-01-01 00:00:00'))))
                timestamp = self.parse_data_simples(data_transacao)
                
                # ✅ CORREÇÃO: DEFINIR 'tipo' ANTES DE USAR
                tipo = dados.get('tipo', '')
                

                # CLIENTE É REMETENTE (SAÍDA)
                if dados['conta_remetente'] == conta_num:
                        if dados.get('tipo') == 'ajuste_admin':
                                tipo_ajuste = dados.get('tipo_ajuste', 'DÉBITO')
                                if tipo_ajuste and (tipo_ajuste.upper() == 'CREDITO' or tipo_ajuste == 'credito'):
                                        todas_transacoes.append({
                                                'data': dados['data'],
                                                'credito': dados['valor'],
                                                'debito': 0.00,
                                                'timestamp': timestamp
                                            })
                                else:
                                        todas_transacoes.append({
                                                'data': dados['data'],
                                                'credito': 0.00,
                                                'debito': dados['valor'],
                                                'timestamp': timestamp
                                            })
                        else:
                                # Transferências normais (débito)
                                todas_transacoes.append({
                                        'data': dados['data'],
                                        'credito': 0.00,
                                        'debito': dados['valor'],
                                        'timestamp': timestamp
                                    })
                
                # CLIENTE É DESTINATÁRIO (ENTRADA)
                elif dados.get('conta_destinatario') == conta_num:
                        if dados.get('tipo') == 'ajuste_admin' and dados.get('tipo_ajuste') == 'CREDITO':
                                todas_transacoes.append({
                                        'data': dados['data'],
                                        'credito': dados['valor'],
                                        'debito': 0.00,
                                        'timestamp': timestamp
                                    })
                        elif dados.get('tipo') == 'cambio':
                                # Câmbio como crédito
                                valor_credito = dados.get('valor_destino', dados['valor'])
                                todas_transacoes.append({
                                        'data': dados['data'],
                                        'credito': valor_credito,
                                        'debito': 0.00,
                                        'timestamp': timestamp
                                    })
                        else:
                                # Transferências recebidas (crédito)
                                todas_transacoes.append({
                                        'data': dados['data'],
                                        'credito': dados['valor'],
                                        'debito': 0.00,
                                        'timestamp': timestamp
                                    })
        
        # Ordenar transações por data (mais antigas primeiro)
        todas_transacoes_ordenadas = sorted(todas_transacoes, key=lambda x: x['timestamp'])
        
        # 🔥 🔥 🔥 CORREÇÃO: Calcular saldo acumulado até o FINAL do dia anterior
        # A data_limite é o início do período (ex: 05/11/2025 00:00:00)
        # Queremos incluir todas as transações até o FINAL do dia anterior (04/11/2025 23:59:59)
        data_fim_calculo = data_limite.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"🔧 CALCULANDO SALDO ATÉ: {data_fim_calculo}")  # DEBUG
        
        # Calcular saldo acumulado até a data limite (FINAL do dia anterior)
        for transacao in todas_transacoes_ordenadas:
                # Só incluir transações até o FINAL do dia anterior
                if transacao['timestamp'] <= data_fim_calculo:
                        saldo_acumulado += transacao['credito'] - transacao['debito']
                        print(f"  ✅ INCLUÍDA: {transacao['timestamp']} | Crédito: {transacao['credito']:,.2f} | Débito: {transacao['debito']:,.2f} | Saldo: {saldo_acumulado:,.2f}")
                else:
                        print(f"  🔧 EXCLUÍDA (após limite): {transacao['timestamp']}")
                        break  # Parar quando encontrar transação após a data limite
        
        print(f"💰 SALDO FINAL CALCULADO: {saldo_acumulado:,.2f}")
        
        return saldo_acumulado

    def parse_data_simples(self, data_str):
        """Versão simplificada do parse_data para uso no cálculo de saldo"""
        if not data_str:
            return datetime.datetime.now()
            
        try:
            # Tentar formato com hora (YYYY-MM-DD HH:MM:SS)
            if ' ' in data_str and ':' in data_str:
                return datetime.datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            # Tentar formato apenas com data (YYYY-MM-DD)
            elif ' ' in data_str:
                return datetime.datetime.strptime(data_str.split(' ')[0], "%Y-%m-%d")
            else:
                # Apenas data
                return datetime.datetime.strptime(data_str, "%Y-%m-%d")
        except:
            # Fallback para data atual se não conseguir parse
            return datetime.datetime.now()
    
    def obter_nome_cliente_por_conta(self, sistema, conta_num):
        """Obtém o nome do cliente por número da conta"""
        if conta_num in sistema.contas:
            return sistema.contas[conta_num].get('cliente_nome', 'N/A')
        return 'N/A'
    
        
    def atualizar_interface_extrato_admin(self, transacoes, saldo_atual, total_entradas, total_saidas, moeda, periodo, username):
        """Atualiza a interface com os dados do extrato admin - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'ids'):
            return
        
        # 🔥 CORREÇÃO: SALVAR AS TRANSAÇÕES FILTRADAS E TOTAIS
        self.transacoes_filtradas_admin = transacoes
        self.saldo_final_admin = saldo_atual
        self.total_entradas_admin = total_entradas
        self.total_saidas_admin = total_saidas
        
        # Limpar transações anteriores
        container = self.ids.container_extrato_admin
        container.clear_widgets()
        
        # 🔥🔥🔥 CORREÇÃO CRÍTICA: INVERTER A ORDEM DAS TRANSAÇÕES (IGUAL AO CLIENTE)
        # As mais recentes primeiro (no topo), as mais antigas por último (embaixo)
        transacoes_invertidas = list(reversed(transacoes))
        
        # Adicionar cabeçalho
        cabecalho = ExtratoTableHeaderAdmin()
        container.add_widget(cabecalho)
        
        # Adicionar transações na ordem invertida (MAIS RECENTES NO TOPO)
        for transacao in transacoes_invertidas:
            # Sua lógica para criar os cards de transação admin
            card = CardTransacaoExtratoAdmin(transacao)  # Ou seja qual for o seu widget
            container.add_widget(card)
        
        # Resto do código (atualizar totais, etc.)
        print(f"✅ Interface admin atualizada: {len(transacoes)} transações (mais recentes no topo)")

    def atualizar_resumo(self, saldo_atual, total_entradas, total_saidas, total_transacoes, moeda, periodo):
        """Atualiza o painel de resumo"""
        if not hasattr(self, 'ids'):
            print("❌ DEBUG: Não tem ids!")  # DEBUG
            return
        
        print(f"🔥 DEBUG RESUMO: Entradas={total_entradas:,.2f}, Saídas={total_saidas:,.2f}, Transações={total_transacoes}")  # DEBUG
        
        # Atualizar labels de resumo
        self.ids.lbl_saldo_total.text = f"{saldo_atual:,.2f} {moeda}"
        self.ids.lbl_total_entradas.text = f"{total_entradas:,.2f} {moeda}"
        self.ids.lbl_total_saidas.text = f"{total_saidas:,.2f} {moeda}"
        self.ids.lbl_total_transacoes.text = f"{total_transacoes}"
        
        # Atualizar informação do período
        if periodo == "0":
            periodo_texto = "Todo período"
        elif periodo == "personalizado":
            # 🔥 FORMATAR DATAS PARA DD/MM/AAAA
            data_inicio_br = self.formatar_data_br(self.ids.entry_data_inicio.text)
            data_fim_br = self.formatar_data_br(self.ids.entry_data_fim.text)
            periodo_texto = f"{data_inicio_br} a {data_fim_br}"
        else:
            periodo_texto = f"Últimos {periodo} dias"
        
        self.ids.lbl_periodo.text = periodo_texto
    
    def formatar_data_br(self, data_iso):
        """Converte data de AAAA-MM-DD para DD/MM/AAAA"""
        try:
            partes = data_iso.split('-')
            if len(partes) == 3:
                return f"{partes[2]}/{partes[1]}/{partes[0]}"
        except:
            pass
        return data_iso
    
    def exportar_extrato_pdf(self):
        """Exporta o extrato para PDF - VERSÃO CORRIGIDA"""
        try:
            print("🔍 Iniciando exportação do PDF...")
            
            # 🔥 CORREÇÃO: PRIMEIRO GARANTIR QUE O EXTRATO ESTÁ CARREGADO
            if not hasattr(self, 'transacoes_filtradas') or len(self.transacoes_filtradas) == 0:
                print("🔍 Carregando extrato automaticamente para PDF...")
                self.carregar_extrato()
                
                # 🔥 AGORA PRECISAMOS ESPERAR O CARREGAMENTO COMPLETO
                # Vamos usar um approach diferente: recarregar e depois exportar
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._exportar_apos_carregamento(), 1.5)
                return
            
            self._exportar_apos_carregamento()
                
        except Exception as e:
            print(f"❌ Erro ao exportar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao exportar PDF: {str(e)}")

    def _exportar_apos_carregamento(self):
        """Exporta o PDF após garantir que o extrato está carregado - VERSÃO CORRIGIDA"""
        try:
            print("🔍 Exportando após carregamento...")
            
            conta_selecionada = self.ids.combo_contas.text
            if not conta_selecionada or conta_selecionada == 'Selecione uma conta':
                self.mostrar_erro("Selecione uma conta primeiro")
                return
            
            # Obtém os dados do sistema
            app = App.get_running_app()
            sistema = app.sistema
            usuario_atual = sistema.usuario_logado
            
            if not usuario_atual:
                self.mostrar_erro("Usuário não logado")
                return
            
            # EXTRAIR APENAS O NÚMERO DA CONTA
            conta_num = conta_selecionada.split(' - ')[0].strip()
            
            print(f"🔍 DEBUG: Texto selecionado: '{conta_selecionada}'")
            print(f"🔍 DEBUG: Número extraído: '{conta_num}'")
            print(f"🔍 DEBUG: Buscando conta {conta_num}")
            
            # Busca a conta
            conta_encontrada = sistema.contas.get(conta_num)
            
            if not conta_encontrada:
                print(f"❌ CONTA NÃO ENCONTRADA: {conta_num}")
                self.mostrar_erro("Conta não encontrada no sistema")
                return
            
            print(f"✅ CONTA ENCONTRADA: {conta_encontrada}")
            
            # 🔥 CORREÇÃO: AGORA PRECISAMOS OBTER AS TRANSAÇÕES FILTRADAS ATUAIS
            # Vamos coletar as transações diretamente da interface
            transacoes_para_pdf = self._obter_transacoes_da_interface()
            
            if not transacoes_para_pdf:
                self.mostrar_erro("Nenhuma transação encontrada para exportar")
                return
            
            print(f"🔍 DEBUG: {len(transacoes_para_pdf)} transações coletadas para PDF")
            
            # Prepara os dados para o PDF
            dados_conta = {
                'numero': conta_num,
                'moeda': conta_encontrada.get('moeda', 'USD'),
                'saldo': conta_encontrada.get('saldo', 0),
                'titular': usuario_atual.get('nome', 'Cliente')
            }
            
            # 🔥 CORREÇÃO: CALCULAR OS TOTAIS CORRETAMENTE
            total_entradas = sum(t.get('credito', 0) for t in transacoes_para_pdf)
            total_saidas = sum(t.get('debito', 0) for t in transacoes_para_pdf)
            
            # 🔥 CORREÇÃO: USAR O SALDO FINAL REAL DA CONTA
            saldo_final = dados_conta['saldo']
            
            # Prepara os dados do resumo
            dados_resumo = {
                'saldo_final': saldo_final,
                'entradas': total_entradas,
                'saidas': total_saidas,
                'total_transacoes': len(transacoes_para_pdf),
                'periodo': self.ids.lbl_periodo.text,
                'moeda': dados_conta['moeda']
            }
            
            print(f"🔍 DADOS CONTA PARA PDF: {dados_conta}")
            print(f"🔍 DADOS RESUMO PARA PDF: {dados_resumo}")
            print(f"🔍 DEBUG TRANSAÇÕES: {len(transacoes_para_pdf)} transações para PDF")
            
            # Gera o PDF
            pdf_generator = self.get_pdf_generator()
            if not pdf_generator:
                self.mostrar_erro("PDF Generator não disponível")
                return

            pdf_path = pdf_generator.gerar_extrato(
                transacoes_para_pdf,
                dados_conta,
                dados_resumo
            )
            
            if pdf_path:
                self.mostrar_sucesso(f"PDF gerado com sucesso!\nSalvo em: {pdf_path}")
            else:
                self.mostrar_erro("Erro ao gerar PDF")
                
        except Exception as e:
            print(f"❌ Erro ao gerar PDF do extrato: {str(e)}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao gerar PDF: {str(e)}")

    def _obter_transacoes_da_interface(self):
        """Obtém as transações atualmente exibidas na interface - VERSÃO CORRIGIDA"""
        try:
            transacoes = []
            
            # Percorre os widgets do container de transações
            container = self.ids.lista_transacoes
            for widget in container.children:
                if hasattr(widget, 'transacao'):
                    # Inverte a ordem para ficar cronológica no PDF
                    transacoes.insert(0, widget.transacao)
            
            print(f"🔍 Coletadas {len(transacoes)} transações da interface")
            return transacoes
            
        except Exception as e:
            print(f"❌ Erro ao obter transações da interface: {e}")
            return []
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'
    
    # ========== MÉTODOS AUXILIARES ==========

    def mostrar_popup_sucesso_pdf(self, caminho_pdf):
        """Mostra popup quando PDF é gerado com sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        import os
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text="✅ EXTRATO GERADO!",
            font_size='18sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            text_size=(400, None),
            halign='center'
        ))
        
        nome_arquivo = os.path.basename(caminho_pdf)
        content.add_widget(Label(
            text=f"📄 {nome_arquivo}\n\n"
                 f"📍 Pasta: Downloads\n\n"
                 f"📊 Período: {getattr(self, 'periodo_var', '30')} dias",
            font_size='14sp',
            text_size=(400, None),
            halign='center'
        ))
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_abrir = Button(
            text='📂 ABRIR PASTA',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_ok = Button(
            text='OK',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_abrir)
        botoes_layout.add_widget(btn_ok)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Extrato Gerado',
            content=content,
            size_hint=(None, None),
            size=(500, 300),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        def abrir_pasta(instance):
            import subprocess
            import platform
            import os
            
            try:
                pasta = os.path.dirname(caminho_pdf)
                if platform.system() == "Windows":
                    os.startfile(pasta)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", pasta])
                else:  # Linux
                    subprocess.Popen(["xdg-open", pasta])
            except Exception as e:
                print(f"❌ Erro ao abrir pasta: {e}")
        
        def fechar_popup(instance):
            popup.dismiss()
        
        btn_abrir.bind(on_press=abrir_pasta)
        btn_ok.bind(on_press=fechar_popup)
        
        popup.open()

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

