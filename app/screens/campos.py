from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.app import App
import re 
import datetime


class CampoValor(TextInput):
    """Campo de texto especializado para valores monetários com comportamento de centavos"""
    
    valor = StringProperty("0.00")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_type = 'number'
        self.multiline = False
        self.hint_text = "0.00"
        self.text = "0.00"
        self.halign = 'right'
        
        # Bind para quando o campo ganhar foco
        self.bind(focus=self.on_focus)
        
    def on_focus(self, instance, value):
        """Quando o campo ganha foco, move o cursor para o final"""
        if value:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.mover_cursor_final(), 0.1)
    
    def mover_cursor_final(self):
        """Move o cursor para o final do texto"""
        self.cursor = (len(self.text), 0)
    
    def processar_digito(self, digito):
        """Processa um dígito com comportamento de deslocamento"""
        # Obter apenas os números atuais (remover formatação)
        numeros_atuais = re.sub(r'[^\d]', '', self.text)
        
        # Se for zero inicial, começar do zero
        if numeros_atuais == "000":
            numeros_atuais = ""
        
        # Adicionar o novo dígito no final
        novos_numeros = (numeros_atuais + digito)
        
        # Limitar a 11 dígitos (999,999,999.99)
        if len(novos_numeros) > 11:
            novos_numeros = novos_numeros[-11:]
        
        # Garantir que tenha pelo menos 3 dígitos (para os centavos)
        while len(novos_numeros) < 3:
            novos_numeros = "0" + novos_numeros
        
        # Separar parte inteira e decimal
        parte_inteira = novos_numeros[:-2]
        parte_decimal = novos_numeros[-2:]
        
        # 🔥 CORREÇÃO: Remover zeros à esquerda da parte inteira
        if parte_inteira:
            parte_inteira = str(int(parte_inteira))  # Isso remove zeros à esquerda
        else:
            parte_inteira = "0"
        
        # 🔥 CORREÇÃO: Formatar parte inteira apenas se tiver mais de 3 dígitos
        if len(parte_inteira) > 3:
            parte_inteira_formatada = ""
            for i, char in enumerate(reversed(parte_inteira)):
                if i > 0 and i % 3 == 0:
                    parte_inteira_formatada = "," + parte_inteira_formatada
                parte_inteira_formatada = char + parte_inteira_formatada
        else:
            parte_inteira_formatada = parte_inteira
        
        return f"{parte_inteira_formatada}.{parte_decimal}"
    
    def insert_text(self, substring, from_undo=False):
        # Permitir apenas números
        digitos = re.sub(r'[^\d]', '', substring)
        
        if not digitos:
            return
        
        # Processar cada dígito
        for digito in digitos:
            novo_texto = self.processar_digito(digito)
            self.text = novo_texto
        
        self.mover_cursor_final()
    
    def on_text(self, instance, value):
        # Garantir que sempre tenha o formato correto
        if not value or not re.match(r'^[\d,]+\.\d{2}$', value):
            self.text = "0.00"
        
        self.mover_cursor_final()
    
    def on_touch_down(self, touch):
        """Quando clica no campo, move o cursor para o final"""
        if self.collide_point(*touch.pos):
            result = super().on_touch_down(touch)
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.mover_cursor_final(), 0.1)
            return result
        return super().on_touch_down(touch)
    
    def get_float_value(self):
        """Retorna o valor como float"""
        try:
            # Remover vírgulas e converter para float
            valor_limpo = self.text.replace(',', '')
            return float(valor_limpo)
        except:
            return 0.0
    
    def set_float_value(self, valor):
        """Define o valor a partir de um float"""
        try:
            # Converter para string com 2 casas decimais
            valor_str = f"{valor:.2f}"
            
            # Separar parte inteira e decimal
            if '.' in valor_str:
                parte_inteira, parte_decimal = valor_str.split('.')
            else:
                parte_inteira, parte_decimal = valor_str, "00"
            
            # Formatar parte inteira com separadores de milhar
            parte_inteira_formatada = ""
            for i, char in enumerate(reversed(parte_inteira)):
                if i > 0 and i % 3 == 0:
                    parte_inteira_formatada = "," + parte_inteira_formatada
                parte_inteira_formatada = char + parte_inteira_formatada
            
            self.text = f"{parte_inteira_formatada}.{parte_decimal}"
            self.mover_cursor_final()
        except:
            self.text = "0.00"
            self.mover_cursor_final()

class TransferenciaCard(BoxLayout):
    """Card individual para cada transferência - VERSÃO CORRIGIDA"""
    
    cor_status = ListProperty([1.0, 0.65, 0.0, 1])
    transferencia_id = StringProperty("")
    dados = ObjectProperty(None)
    
    def __init__(self, transferencia_id, dados, **kwargs):
        super().__init__(**kwargs)
        self.transferencia_id = transferencia_id
        self.dados = dados
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(230)
        self.padding = [4, 4]
        self.spacing = 0
        
        # Calcular cor do status
        self.cor_status = self.calcular_cor_status()
        
        # Adicionar fundo do card
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.20, 0.25, 0.33, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[5]
            )
        
        def update_bg_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        
        self.bind(pos=update_bg_rect, size=update_bg_rect)
        
        self.criar_card()

    def calcular_cor_status(self):
        """Calcula a cor baseada no status da TRANSFERÊNCIA"""
        if not hasattr(self, 'dados') or not self.dados:
            return [1.0, 0.65, 0.0, 1]  # Âmbar como fallback
            
        if self.dados['status'] == 'pending':
            return [1.0, 0.65, 0.0, 1]  # Âmbar
        elif self.dados['status'] == 'processing':
            return [0.3, 0.7, 1.0, 1]   # Azul
        elif self.dados['status'] == 'completed':
            return [0.2, 0.8, 0.2, 1]   # Verde
        else:  # rejected
            return [0.9, 0.2, 0.2, 1]   # Vermelho

    def criar_card(self):
        """Cria o conteúdo do card"""
        if not hasattr(self, 'dados') or not self.dados:
            print(f"❌ Dados não disponíveis para transferência {self.transferencia_id}")
            return
            
        sistema = App.get_running_app().sistema
        
        # Calcular a cor do status
        self.cor_status = self.calcular_cor_status()
        
        # Determinar texto do status
        if self.dados['status'] == 'pending':
            texto_status = "PENDENTE"
        elif self.dados['status'] == 'processing':
            texto_status = "PROCESSANDO"
        elif self.dados['status'] == 'completed':
            texto_status = "CONCLUÍDA"
        else:  # rejected
            texto_status = "RECUSADA"

        # Determinar tipo e informações
        if self.dados.get('tipo') == 'internacional':
            texto_tipo = "INTERNACIONAL"
            pais = self.dados.get('pais', '')
            if pais:
                texto_tipo += f" • {pais}"
            beneficiario = self.dados.get('beneficiario', 'N/A')
            banco = self.dados.get('nome_banco', 'N/A')
            swift = self.dados.get('codigo_swift', 'N/A')
            iban = self.dados.get('iban_account', 'N/A')
        else:
            texto_tipo = "INTERNA"
            if self.dados['conta_remetente'] in sistema.usuario_logado['contas']:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_destinatario', 'N/A'))
                info_extra = " • Enviada"
            else:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_remetente', 'N/A'))
                info_extra = " • Recebida"
            texto_tipo += info_extra
            banco = "Banco Interno"
            swift = "N/A"
            iban = self.dados.get('conta_destinatario', 'N/A')

        # Preencher dados do card
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._preencher_dados_card(
            texto_status, texto_tipo, beneficiario, banco, swift, iban
        ), 0.1)

    def _preencher_dados_card(self, texto_status, texto_tipo, beneficiario, banco, swift, iban):
        """Preenche os dados do card após garantir que os IDs estão disponíveis"""
        try:
            if not hasattr(self, 'ids'):
                return
                
            # Atualizar header
            if 'lbl_status_transferencia' in self.ids:
                self.ids.lbl_status_transferencia.text = f"TRANSFERÊNCIA {texto_status}"
            
            if 'lbl_tipo_transferencia' in self.ids:
                self.ids.lbl_tipo_transferencia.text = texto_tipo
            
            # Atualizar informações bancárias
            if 'lbl_beneficiario' in self.ids:
                self.ids.lbl_beneficiario.text = beneficiario
            
            if 'lbl_banco' in self.ids:
                self.ids.lbl_banco.text = banco
            
            if 'lbl_swift' in self.ids:
                self.ids.lbl_swift.text = swift
            
            # Atualizar tipo de conta (IBAN/Conta)
            if 'lbl_tipo_conta' in self.ids:
                if self.dados.get('tipo') == 'internacional':
                    self.ids.lbl_tipo_conta.text = "IBAN:"
                else:
                    self.ids.lbl_tipo_conta.text = "Conta:"
            
            if 'lbl_conta' in self.ids:
                self.ids.lbl_conta.text = iban
            
            # Atualizar valor
            if 'lbl_valor' in self.ids:
                moeda = self.dados['moeda']
                if moeda == 'USD':
                    simbolo = "US$"
                elif moeda == 'EUR':
                    simbolo = "€"
                elif moeda == 'GBP':
                    simbolo = "£"
                else:
                    simbolo = moeda
                    
                self.ids.lbl_valor.text = f"{simbolo} {self.dados['valor']:,.2f}"
            
            # Atualizar data
            if 'lbl_data' in self.ids:
                data_simples = self.dados.get('data_solicitacao', self.dados.get('data', '')).split(' ')[0]
                self.ids.lbl_data.text = data_simples
            
            # Atualizar ID
            if 'lbl_id' in self.ids:
                self.ids.lbl_id.text = self.transferencia_id
            
            # Adicionar linha da invoice se necessário
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.adicionar_linha_invoice_se_necesario(), 0.3)
                
            print(f"✅ Card {self.transferencia_id} preenchido: {texto_status} | {texto_tipo}")
            
        except Exception as e:
            print(f"❌ Erro ao preencher card {self.transferencia_id}: {e}")

    def adicionar_linha_invoice_se_necesario(self):
        """Adiciona a linha da invoice SEM faixa de fundo - VERSÃO CORRIGIDA"""
        try:
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            print(f"🔍 DEBUG INVOICE: Verificando invoice para {self.transferencia_id}")
            
            if not info_invoice:
                print(f"❌ DEBUG INVOICE: Nenhuma invoice encontrada para {self.transferencia_id}")
                if 'linha_invoice_container' in self.ids:
                    self.ids.linha_invoice_container.height = 0
                    self.ids.linha_invoice_container.opacity = 0
                return
                
            print(f"✅ DEBUG INVOICE: Invoice encontrada para {self.transferencia_id} - Status: {info_invoice['status']}")
            
            container = self.ids.linha_invoice_container
            container.clear_widgets()
            container.height = dp(25)
            container.opacity = 1
            
            # Label do status da invoice
            self.lbl_status_invoice = Label(
                text='Invoice: Pendente',
                font_size='12sp',
                color=(1.0, 0.65, 0.0, 1),  # Cor inicial âmbar
                size_hint_x=0.7,
                text_size=(None, None),
                halign='left'
            )
            
            # Botão reenviar
            self.btn_reenviar_invoice = Button(
                text='Reenviar',
                font_size='10sp',
                size_hint_x=0.3,
                background_color=(0.55, 0.36, 0.96, 1),
                background_normal='',
                color=(1, 1, 1, 1),
                on_press=self.reenviar_invoice,
                opacity=0
            )
            
            container.add_widget(self.lbl_status_invoice)
            container.add_widget(self.btn_reenviar_invoice)
            
            # Atualizar status com a cor correta
            self.atualizar_status_invoice()
            
            print(f"✅ Linha de invoice adicionada (SEM FAIXA) para {self.transferencia_id}")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar linha invoice: {e}")

    def atualizar_status_invoice(self):
        """Atualiza o display do status da invoice com cores apenas no texto"""
        try:
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or 'linha_invoice_container' not in self.ids:
                return
            
            status = info_invoice['status']
            motivo_recusa = info_invoice.get('motivo_recusa', '')
            
            print(f"🎨 DEBUG COR INVOICE: Status = {status}, Motivo = {motivo_recusa}")
            
            # Definir texto e cor baseado no status (APENAS COR DO TEXTO)
            if status == 'pending':
                texto = 'Invoice: Pendente'
                cor_texto = (1.0, 0.65, 0.0, 1)  # Âmbar apenas no texto
                mostrar_botao = False
            elif status == 'approved':
                texto = 'Invoice: Aprovado'
                cor_texto = (0.2, 0.8, 0.2, 1)   # Verde apenas no texto
                mostrar_botao = False
            elif status == 'rejected':
                texto = 'Invoice: Recusado'
                cor_texto = (0.9, 0.2, 0.2, 1)   # Vermelho apenas no texto
                mostrar_botao = True
            else:
                texto = 'Invoice: Pendente'
                cor_texto = (1.0, 0.65, 0.0, 1)
                mostrar_botao = False
            
            # Adicionar motivo se existir
            if motivo_recusa and status == 'rejected':
                texto += f' - {motivo_recusa}'
            
            # Apenas atualizar COR DO TEXTO, não o fundo
            if hasattr(self, 'lbl_status_invoice'):
                self.lbl_status_invoice.text = texto
                self.lbl_status_invoice.font_size = '12sp'
                self.lbl_status_invoice.color = cor_texto  # COR DO TEXTO muda
            
            # Atualizar botão
            if hasattr(self, 'btn_reenviar_invoice'):
                self.btn_reenviar_invoice.opacity = 1 if mostrar_botao else 0
                self.btn_reenviar_invoice.font_size = '10sp'
            
            print(f"✅ Status da invoice atualizado: {self.transferencia_id} -> {status} (cor texto: {cor_texto})")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar status da invoice: {e}")

    def debug_sistema_invoices(self):
        """Método de debug para verificar invoices no sistema"""
        try:
            sistema = App.get_running_app().sistema
            print(f"🔍 DEBUG SISTEMA INVOICES:")
            print(f"📁 Transferência: {self.transferencia_id}")
            
            # Verificar se existe info de invoice
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            print(f"📄 Info Invoice: {info_invoice}")
            
            # Verificar todas as invoices do sistema
            if hasattr(sistema, 'invoices'):
                print(f"📚 Todas as invoices no sistema:")
                for transfer_id, invoice_data in sistema.invoices.items():
                    if transfer_id == self.transferencia_id:
                        print(f"   🎯 {transfer_id}: {invoice_data}")
            
        except Exception as e:
            print(f"❌ Erro no debug: {e}")

    def obter_nome_cliente(self, conta_numero):
        """Obtém o nome do cliente a partir do número da conta"""
        sistema = App.get_running_app().sistema
        if conta_numero in sistema.contas:
            return sistema.contas[conta_numero].get('cliente_nome', 'Cliente não encontrado')
        return 'Conta não encontrada'

    def ver_detalhes(self, instance=None):
        """Mostra detalhes da transferência"""
        popup = self.criar_popup_detalhes()
        popup.open()

    def gerar_pdf(self, instance=None):
        """Gera PDF da transferência"""
        try:
            print(f"🔍 DEBUG: Iniciando gerar_pdf para {self.transferencia_id}")
            
            sistema = App.get_running_app().sistema
            
            # Obter dados do cliente
            usuario_atual = sistema.usuario_logado['username']
            dados_cliente = sistema.usuarios[usuario_atual]
            
            print(f"🔄 Gerando comprovante para: {self.transferencia_id}")
            print(f"📊 Status atual: {self.dados['status']}")
            
            # Gerar PDF
            from pdf_generator import PDFGenerator
            pdf_generator = PDFGenerator()
            caminho_pdf = pdf_generator.gerar_comprovante_transferencia(
                self.transferencia_id, 
                self.dados, 
                dados_cliente
            )
            
            # Mostrar popup de sucesso
            self.mostrar_popup_sucesso_pdf(caminho_pdf)
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            self.mostrar_popup_erro_pdf(str(e))

    def reenviar_invoice(self, instance=None):
        """Abre modal para reenviar invoice quando a anterior foi recusada"""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or info_invoice['status'] != 'rejected':
                self.mostrar_erro("Não é possível reenviar invoice neste status!")
                return
            
            motivo_recusa = info_invoice.get('motivo_recusa', 'Motivo não especificado')
            
            # Criar conteúdo do modal
            content = BoxLayout(orientation='vertical', padding=20, spacing=15)
            content.size_hint_y = None
            content.height = 350
            
            # Título
            lbl_titulo = Label(
                text='REENVIAR INVOICE',
                font_size='18sp',
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                size_hint_y=None,
                height=40,
                text_size=(400, None),
                halign='center'
            )
            
            # Motivo da recusa anterior
            lbl_motivo = Label(
                text=f'Motivo da recusa anterior:\n"{motivo_recusa}"',
                font_size='12sp',
                color=(1, 0.5, 0.5, 1),
                size_hint_y=None,
                height=60,
                text_size=(400, None),
                halign='center'
            )
            
            # Instruções
            lbl_instrucoes = Label(
                text='Selecione a nova invoice corrigida:',
                font_size='14sp',
                color=(0.9, 0.9, 0.9, 1),
                size_hint_y=None,
                height=30,
                text_size=(400, None),
                halign='center'
            )
            
            # Botões
            botoes_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=50,
                spacing=10
            )
            
            btn_selecionar = Button(
                text='SELECIONAR NOVA INVOICE',
                background_color=(0.23, 0.51, 0.96, 1),
                color=(1, 1, 1, 1)
            )
            
            btn_cancelar = Button(
                text='CANCELAR',
                background_color=(0.55, 0.36, 0.96, 1),
                color=(1, 1, 1, 1)
            )
            
            botoes_layout.add_widget(btn_selecionar)
            botoes_layout.add_widget(btn_cancelar)
            
            # Label do arquivo selecionado
            self.lbl_arquivo_selecionado = Label(
                text='Nenhum arquivo selecionado',
                font_size='10sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=30,
                text_size=(400, None),
                halign='center'
            )
            
            content.add_widget(lbl_titulo)
            content.add_widget(lbl_motivo)
            content.add_widget(lbl_instrucoes)
            content.add_widget(self.lbl_arquivo_selecionado)
            content.add_widget(botoes_layout)
            
            # Criar popup
            popup = Popup(
                title='Reenviar Invoice',
                title_color=(0.23, 0.51, 0.96, 1),
                content=content,
                size_hint=(None, None),
                size=(450, 350),
                background_color=(0.12, 0.16, 0.23, 1),
                auto_dismiss=False
            )
            
            def selecionar_arquivo(instance):
                """Abre o seletor de arquivos"""
                from kivy.uix.filechooser import FileChooserListView
                
                # Criar popup de seleção de arquivo
                content_arquivo = BoxLayout(orientation='vertical', spacing=10, padding=10)
                
                filechooser = FileChooserListView(
                    filters=['*.pdf', '*.jpg', '*.jpeg', '*.png'],
                    size_hint_y=0.8
                )
                
                botoes_arquivo = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
                
                btn_confirmar = Button(
                    text='SELECIONAR',
                    background_color=(0.23, 0.51, 0.96, 1)
                )
                
                btn_voltar = Button(
                    text='VOLTAR',
                    background_color=(0.55, 0.36, 0.96, 1)
                )
                
                botoes_arquivo.add_widget(btn_confirmar)
                botoes_arquivo.add_widget(btn_voltar)
                
                content_arquivo.add_widget(filechooser)
                content_arquivo.add_widget(botoes_arquivo)
                
                popup_arquivo = Popup(
                    title='Selecionar Nova Invoice',
                    content=content_arquivo,
                    size_hint=(0.9, 0.8),
                    background_color=(0.12, 0.16, 0.23, 1)
                )
                
                def confirmar_selecao(instance):
                    if filechooser.selection:
                        arquivo_selecionado = filechooser.selection[0]
                        nome_arquivo = arquivo_selecionado.split('/')[-1]  # Para Linux/Mac
                        nome_arquivo = nome_arquivo.split('\\')[-1]  # Para Windows
                        
                        self.lbl_arquivo_selecionado.text = f"{nome_arquivo}"
                        self.novo_arquivo_invoice = arquivo_selecionado
                        popup_arquivo.dismiss()
                    else:
                        self.mostrar_erro("Selecione um arquivo!")
                
                def voltar(instance):
                    popup_arquivo.dismiss()
                
                btn_confirmar.bind(on_press=confirmar_selecao)
                btn_voltar.bind(on_press=voltar)
                
                popup_arquivo.open()
            
            def enviar_nova_invoice(instance):
                """Processa o envio da nova invoice"""
                if not hasattr(self, 'novo_arquivo_invoice'):
                    self.mostrar_erro("Selecione um arquivo primeiro!")
                    return
                
                # Copiar arquivo para o sistema
                from tela_transferencia import TelaTransferencia
                tela_transferencia = TelaTransferencia()
                caminho_destino = tela_transferencia.copiar_arquivo_invoice(
                    self.novo_arquivo_invoice, 
                    self.transferencia_id
                )
                
                if caminho_destino:
                    # Atualizar no sistema
                    if sistema.adicionar_invoice_info_transferencia(self.transferencia_id, caminho_destino):
                        popup.dismiss()
                        self.mostrar_sucesso("Nova invoice enviada com sucesso!\nAguarde a análise do administrador.")
                        # Atualizar o card
                        self.atualizar_status_invoice()
                    else:
                        self.mostrar_erro("Erro ao enviar nova invoice!")
                else:
                    self.mostrar_erro("Erro ao copiar arquivo!")
            
            def cancelar(instance):
                popup.dismiss()
            
            # Vincular eventos
            btn_selecionar.bind(on_press=selecionar_arquivo)
            btn_cancelar.bind(on_press=cancelar)
            
            # Para enviar, vamos usar um botão adicional
            btn_enviar_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=50,
                spacing=10
            )
            
            btn_enviar = Button(
                text='ENVIAR NOVA INVOICE',
                background_color=(0.2, 0.8, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            
            btn_enviar.bind(on_press=enviar_nova_invoice)
            btn_enviar_layout.add_widget(btn_enviar)
            content.add_widget(btn_enviar_layout)
            
            popup.open()
            
        except Exception as e:
            print(f"❌ Erro ao reenviar invoice: {e}")
            self.mostrar_erro(f"Erro: {str(e)}")

    def criar_popup_detalhes(self):
        """Cria popup com detalhes completos da transferência"""
        from kivy.uix.scrollview import ScrollView
        
        sistema = App.get_running_app().sistema
        content = BoxLayout(orientation='vertical', padding=[25, 20, 25, 20], spacing=15)
        
        # Título
        content.add_widget(Label(
            text="DETALHES DA TRANSFERÊNCIA",
            bold=True,
            font_size='16sp',
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Scroll para conteúdo
        scroll = ScrollView()
        detalhes_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[0, 0, 10, 0])
        detalhes_layout.bind(minimum_height=detalhes_layout.setter('height'))
        
        # Informações básicas
        info_basica = f"""
ID: {self.transferencia_id}
Status: {self.dados['status'].title()}
Tipo: {'Internacional' if self.dados.get('tipo') == 'internacional' else 'Interna'}
Valor: {self.dados['valor']:,.2f} {self.dados['moeda']}
Data: {self.dados.get('data_solicitacao', self.dados.get('data', 'N/A'))}
        """.strip()
        
        detalhes_layout.add_widget(Label(
            text=info_basica,
            font_size='14sp',
            text_size=(380, None),
            halign='left',
            size_hint_y=None,
            height=dp(120)
        ))
        
        # Informações do beneficiário
        if self.dados.get('tipo') == 'internacional':
            info_beneficiario = f"""
Beneficiário: {self.dados.get('beneficiario', 'N/A')}
Endereço: {self.dados.get('endereco_beneficiario', 'N/A')}
Cidade: {self.dados.get('cidade', 'N/A')}
País: {self.dados.get('pais', 'N/A')}
Banco: {self.dados.get('nome_banco', 'N/A')}
SWIFT: {self.dados.get('codigo_swift', 'N/A')}
IBAN: {self.dados.get('iban_account', 'N/A')}
            """.strip()
        else:
            conta_destino = self.dados.get('conta_destinatario', 'N/A')
            info_beneficiario = f"""
Destinatário: {self.obter_nome_cliente(conta_destino)}
Conta: {conta_destino}
            """.strip()
        
        detalhes_layout.add_widget(Label(
            text=info_beneficiario,
            font_size='14sp',
            text_size=(380, None),
            halign='left',
            size_hint_y=None,
            height=dp(180) if self.dados.get('tipo') == 'internacional' else dp(80)
        ))
        
        # Finalidade
        if 'finalidade' in self.dados:
            info_finalidade = f"""
Finalidade: {self.dados['finalidade']}
Descrição: {self.dados.get('descricao', 'Nenhuma')}
            """.strip()
            
            detalhes_layout.add_widget(Label(
                text=info_finalidade,
                font_size='14sp',
                text_size=(380, None),
                halign='left',
                size_hint_y=None,
                height=dp(80)
            ))
        
        scroll.add_widget(detalhes_layout)
        content.add_widget(scroll)
        
        # Botão fechar
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=dp(45),
            background_color=(0.55, 0.36, 0.96, 1)
        )
        
        popup = Popup(
            title=f'Transferência {self.transferencia_id}',
            content=content,
            size_hint=(None, None),
            size=(480, 500)
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        content.add_widget(btn_fechar)
        
        return popup

    def mostrar_popup_sucesso_pdf(self, caminho_pdf):
        """Mostra popup quando PDF é gerado com sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        import os
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text="COMPROVANTE GERADO!",
            font_size='18sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            text_size=(400, None),
            halign='center'
        ))
        
        nome_arquivo = os.path.basename(caminho_pdf)
        content.add_widget(Label(
            text=f"{nome_arquivo}\n\nPasta: Downloads\n\nStatus: {self.dados['status'].upper()}",
            font_size='14sp',
            text_size=(400, None),
            halign='center'
        ))
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_abrir = Button(
            text='ABRIR PASTA',
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
            title='Comprovante Gerado',
            content=content,
            size_hint=(None, None),
            size=(500, 320),
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

    def mostrar_popup_erro_pdf(self, mensagem_erro):
        """Mostra popup de erro na geração do PDF"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text="ERRO AO GERAR COMPROVANTE",
            font_size='18sp',
            bold=True,
            color=(1, 0.3, 0.3, 1),
            text_size=(400, None),
            halign='center'
        ))
        
        content.add_widget(Label(
            text=f"Detalhes: {mensagem_erro}",
            font_size='14sp',
            text_size=(400, None),
            halign='center'
        ))
        
        btn_ok = Button(
            text='TENTAR NOVAMENTE',
            size_hint_y=None,
            height=50,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Erro no PDF',
            content=content,
            size_hint=(None, None),
            size=(450, 250),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        ))
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Erro',
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
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            bold=True,
            text_size=(350, None),
            halign='center'
        ))
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

class TelaMinhasTransferencias(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filtro_status = "all"

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1000, 700)
        print("📋 Tela de minhas transferências carregada")
        
        # VERIFICAR SE USUÁRIO ESTÁ LOGADO ANTES DE CARREGAR
        sistema = App.get_running_app().sistema
        if sistema.usuario_logado and sistema.usuario_logado['tipo'] == 'cliente':
            self.carregar_transferencias()
        else:
            print("⚠️ Usuário não está logado como cliente, não é possível carregar transferências")

    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("💸 Tela Minhas Transferências totalmente carregada")
        self.rolar_para_topo()

    def rolar_para_topo(self):
        """Rola a ScrollView para o topo"""
        try:
            from kivy.clock import Clock
            Clock.schedule_once(self._executar_rolagem, 0.1)
            Clock.schedule_once(self._executar_rolagem, 0.5)
        except Exception as e:
            print(f"⚠️ Erro ao agendar rolagem: {e}")

    def _executar_rolagem(self, dt):
        """Executa a rolagem para o topo"""
        try:
            print("🔄 Tentando rolar para o topo (Minhas Transferências)...")
            
            # Método 1: Buscar por ID específico
            if hasattr(self, 'ids'):
                if 'scroll_principal' in self.ids:
                    self.ids.scroll_principal.scroll_y = 1.0
                    print("✅ ScrollView rolada para o topo (via ID 'scroll_principal')")
                    return
                
                # Método 2: Buscar qualquer ScrollView nos IDs
                for widget_id, widget in self.ids.items():
                    if hasattr(widget, 'scroll_y'):
                        widget.scroll_y = 1.0
                        print(f"✅ ScrollView encontrada por ID '{widget_id}' e rolada para o topo")
                        return
            
            # Método 3: Buscar na hierarquia completa
            def encontrar_scrollview(widget):
                if hasattr(widget, 'scroll_y'):
                    return widget
                if hasattr(widget, 'children'):
                    for child in widget.children:
                        result = encontrar_scrollview(child)
                        if result:
                            return result
                return None
            
            scrollview = encontrar_scrollview(self)
            if scrollview:
                scrollview.scroll_y = 1.0
                print("✅ ScrollView encontrada na hierarquia e rolada para o topo")
            else:
                print("❌ ScrollView não encontrada de nenhuma forma")
                
        except Exception as e:
            print(f"❌ Erro ao executar rolagem: {e}")

    def carregar_transferencias(self, filtro_status="all"):
        """Carrega as transferências"""
        sistema = App.get_running_app().sistema
        
        # VERIFICAR SE USUÁRIO ESTÁ LOGADO
        if not sistema.usuario_logado:
            print("❌ Usuário não está logado, não é possível carregar transferências")
            return
        
        if not hasattr(self, 'ids') or 'scroll_container' not in self.ids:
            return
        
        # Limpar container
        container = self.ids.scroll_container
        container.clear_widgets()
        container.bind(minimum_height=container.setter('height'))
        
        # Encontrar todas as transferências do cliente
        transferencias_cliente = {}
        for transferencia_id, dados in sistema.transferencias.items():
            # VERIFICAR SE 'contas' EXISTE NO USUÁRIO LOGADO
            if ('contas' in sistema.usuario_logado and 
                dados['conta_remetente'] in sistema.usuario_logado['contas']):
                transferencias_cliente[transferencia_id] = dados
            # Também incluir transferências onde o cliente é destinatário (internas)
            elif (dados.get('conta_destinatario') and 
                  'contas' in sistema.usuario_logado and
                  dados['conta_destinatario'] in sistema.usuario_logado['contas'] and
                  dados.get('tipo') != 'internacional'):
                transferencias_cliente[transferencia_id] = dados
        
        # Aplicar filtro de status se não for "all"
        if filtro_status != "all":
            transferencias_cliente = {k: v for k, v in transferencias_cliente.items() 
                                    if v['status'] == filtro_status}
        
        # Ordenar por data (mais recente primeiro)
        transferencias_ordenadas = sorted(transferencias_cliente.items(), 
                                        key=lambda x: x[1].get('data_solicitacao', x[1].get('data', '')), 
                                        reverse=True)
        
        print(f"📊 Carregando {len(transferencias_ordenadas)} transferências com filtro: {filtro_status}")
        
        # Criar cards para cada transferência
        for transferencia_id, dados in transferencias_ordenadas:
            try:
                card = TransferenciaCard(transferencia_id, dados)
                card.size_hint_y = None
                card.height = dp(230)
                container.add_widget(card)
                print(f"✅ Card criado para transferência {transferencia_id}")
            except Exception as e:
                print(f"❌ Erro ao criar card para {transferencia_id}: {e}")
        
        # ATUALIZAR STATUS DAS INVOICES NOS CARDS
        for child in container.children:
            if hasattr(child, 'atualizar_status_invoice'):
                try:
                    child.atualizar_status_invoice()
                except Exception as e:
                    print(f"❌ Erro ao atualizar invoice no card: {e}")
        
        # Mensagem se não houver transferências
        if not transferencias_ordenadas:
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            
            vazio_layout = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height=dp(200),
                spacing=10,
                padding=20
            )
            
            status_text = "com este status" if filtro_status != "all" else ""
            vazio_layout.add_widget(Label(
                text=f"Nenhuma transferência {status_text} encontrada",
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            
            vazio_layout.add_widget(Label(
                text="Use os filtros ou faça uma nova transferência",
                font_size='14sp',
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=dp(30)
            ))
            
            container.add_widget(vazio_layout)
        
        print(f"🎯 Total de {len(container.children)} widgets no container")

    def atualizar_filtro(self, filtro):
        """Atualiza o filtro e recarrega as transferências"""
        self.filtro_status = filtro
        self.carregar_transferencias(filtro)

    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'