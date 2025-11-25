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
import datetime

class TransferenciaCard(BoxLayout):
    """Card individual para cada transferência - CORES DO SISTEMA ESCURAS"""
    
    cor_status = ListProperty([0.8, 0.5, 0.0, 1])
    transferencia_id = StringProperty("")
    dados = ObjectProperty(None)
    
    def __init__(self, transferencia_id, dados, **kwargs):
        super().__init__(**kwargs)
        self.transferencia_id = transferencia_id
        self.dados = dados

        # CORES DO SISTEMA - VERSÕES MAIS ESCURAS
        self.COR_PRIMARIA = (0.15, 0.35, 0.75, 1)
        self.COR_SECUNDARIA = (0.4, 0.25, 0.75, 1)
        self.COR_SUCESSO = (0.1, 0.6, 0.1, 1)
        self.COR_AVISO = (0.8, 0.5, 0.0, 1)
        self.COR_ERRO = (0.7, 0.2, 0.2, 1)
        self.FUNDO_CARD = (0.15, 0.20, 0.28, 1)
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(250)
        self.padding = [4, 4]
        self.spacing = 0
        

        # 🔥 NOVOS VALORES PARA BORDAS ARREDONDADAS
        self.RAIO_BORDA_CARD = [dp(12)]  # Aumentado de 5 para 12
        self.RAIO_BORDA_HEADER = [dp(12), dp(12), 0, 0]  # Cantos superiores arredondados

        # Calcular cor do status
        self.cor_status = self.calcular_cor_status()
        
        # Adicionar fundo do card
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*self.FUNDO_CARD)
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

        # 🔥 CONFIGURAR BOTÕES IMEDIATAMENTE - SEM DELAY
        self.configurar_botoes_card()

    def calcular_cor_status(self):
        """Calcula a cor baseada no status da TRANSFERÊNCIA - CORES ESCURAS"""
        if not hasattr(self, 'dados') or not self.dados:
            return [0.8, 0.5, 0.0, 1]
        
        # 🔥 CORREÇÃO: TRATAR 'solicitada' COMO 'pending' TAMBÉM AQUI
        status = self.dados['status']
        if status == 'solicitada':
            status = 'pending'
            
        if status == 'pending':
            return [0.8, 0.5, 0.0, 1]  # 🟠 ÂMBAR/ LARANJA ESCURO
        elif status == 'processing':
            return [0.2, 0.5, 0.8, 1]  # 🔵 AZUL ESCURO
        elif status == 'completed':
            return [0.1, 0.6, 0.1, 1]  # 🟢 VERDE ESCURO
        else:  # rejected
            return [0.7, 0.2, 0.2, 1]  # 🔴 VERMELHO ESCURO

    def criar_card(self):
        """Cria o conteúdo do card"""
        if not hasattr(self, 'dados') or not self.dados:
            return
            
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados do usuário CORRETAMENTE
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        contas_usuario = usuario_data.get('contas', [])
        
        # 🔥 CORREÇÃO: TRATAR 'solicitada' COMO 'pending' (PADRÃO ANTERIOR)
        status = self.dados['status']
        if status == 'solicitada':
            status = 'pending'
        
        # Calcular a cor do status (MANTIDO COMO ANTES)
        self.cor_status = self.calcular_cor_status()
        
        # 🔥 PADRÃO ORIGINAL - TEXTOS EXATOS COMO ANTES
        if status == 'pending':
            texto_status = "PENDENTE"
        elif status == 'processing':
            texto_status = "PROCESSANDO"  # ✅ PADRÃO ORIGINAL
        elif status == 'completed':
            texto_status = "CONCLUÍDA"    # ✅ PADRÃO ORIGINAL
        else:  # rejected
            texto_status = "RECUSADA"     # ✅ PADRÃO ORIGINAL
        
        # 🔥 ATUALIZAR FUNDO DO CARD COM BORDAS MAIS ARREDONDADAS
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*self.FUNDO_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=self.RAIO_BORDA_CARD  # 🔥 USANDO NOVO RAIO
            )

        # 🔥🔥🔥 DEBUG: VERIFICAR DADOS DA TRANSFERÊNCIA
        print(f"🔍 DEBUG TIPO TRANSFERÊNCIA {self.dados.get('id')}:")
        print(f"   tipo = {self.dados.get('tipo')}")
        print(f"   pais = {self.dados.get('pais')}")
        print(f"   beneficiario = {self.dados.get('beneficiario')}")
        print(f"   nome_banco = {self.dados.get('nome_banco')}")
        print(f"   conta_remetente = {self.dados.get('conta_remetente')}")

        # Determinar tipo e informações
        if self.dados.get('tipo') in ['internacional', 'transferencia_internacional']:
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
            # 🔥 CORREÇÃO: Usar contas_usuario em vez de sistema.usuario_logado['contas']
            if self.dados['conta_remetente'] in contas_usuario:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_destinatario', 'N/A'))
                info_extra = " • Enviada"
            else:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_remetente', 'N/A'))
                info_extra = " • Recebida"
            texto_tipo += info_extra
            banco = "Banco Interno"
            swift = "N/A"
            iban = self.dados.get('conta_destinatario', 'N/A')

        # 🔥 PREENCHER DADOS IMEDIATAMENTE
        self._preencher_dados_card_sincrono(texto_status, texto_tipo, beneficiario, banco, swift, iban)

    def configurar_botoes_card(self):
        """Configura os botões do card UMA VEZ na inicialização - VERSÃO SÍNCRONA"""
        try:
            if not hasattr(self, 'ids'):
                return
                
            # 🔥 CORES DEFINITIVAS - MESMAS DO SISTEMA
            COR_AZUL_ESCURO = [0.2, 0.4, 0.5, 1]
            COR_VERDE_ESCURO = [0.3, 0.5, 0.4, 1]
            COR_ROXO_ESCURO = [0.4, 0.4, 0.45, 1]
            COR_BRANCO = [1, 1, 1, 1]
            COR_CINZA = [0.3, 0.3, 0.3, 1]
            
            # 🔥 CONFIGURAR BOTÕES IMEDIATAMENTE
            if 'btn_detalhes_card' in self.ids:
                btn = self.ids.btn_detalhes_card
                btn.background_color = COR_AZUL_ESCURO
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '11sp'
            
            # 🔥 VERIFICAR INVOICE DE FORMA SÍNCRONA
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            tem_invoice = info_invoice is not None
            
            if 'btn_visualizar_invoice_card' in self.ids:
                btn = self.ids.btn_visualizar_invoice_card
                if tem_invoice:
                    btn.background_color = COR_VERDE_ESCURO
                    btn.disabled = False
                else:
                    btn.background_color = COR_CINZA
                    btn.disabled = True
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '10sp'
            
            if 'btn_pdf_card' in self.ids:
                btn = self.ids.btn_pdf_card
                btn.background_color = COR_ROXO_ESCURO
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '10sp'
                
        except Exception as e:
            print(f"Erro rápido ao configurar botões: {e}")

    def _preencher_dados_card_sincrono(self, texto_status, texto_tipo, beneficiario, banco, swift, iban):
        """Preenche os dados do card sincronamente - SEM DELAY"""
        try:
            if not hasattr(self, 'ids'):
                return
                
            # Atualizar header IMEDIATAMENTE
            if 'lbl_status_transferencia' in self.ids:
                self.ids.lbl_status_transferencia.text = f"TRANSFERÊNCIA {texto_status}"
            
            if 'lbl_tipo_transferencia' in self.ids:
                self.ids.lbl_tipo_transferencia.text = texto_tipo
            
            # Atualizar informações bancárias IMEDIATAMENTE
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
            
            # Atualizar valor IMEDIATAMENTE
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
            
            # Atualizar data IMEDIATAMENTE
            if 'lbl_data' in self.ids:
                data_simples = self.dados.get('data_solicitacao', self.dados.get('data', '')).split(' ')[0]
                self.ids.lbl_data.text = data_simples
            
            # Atualizar ID IMEDIATAMENTE
            if 'lbl_id' in self.ids:
                self.ids.lbl_id.text = self.transferencia_id
            
            # 🔥 CONFIGURAR INVOICE IMEDIATAMENTE (sem Clock)
            self.adicionar_linha_invoice_se_necesario_sincrono()
                
        except Exception as e:
            print(f"Erro rápido no preenchimento: {e}")

    def adicionar_linha_invoice_se_necesario_sincrono(self):
        """Adiciona linha da invoice sincronamente - COM DEBUG ESPECÍFICO"""
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 DEBUG ESPECÍFICO PARA 841328
            if self.transferencia_id == "841328":
                print(f"🎯 DEBUG ESPECIAL 841328: Iniciando busca de invoice")
            
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            # 🔥 DEBUG ESPECÍFICO PARA 841328
            if self.transferencia_id == "841328":
                print(f"🎯 DEBUG ESPECIAL 841328: Info Invoice = {info_invoice}")
                print(f"🎯 DEBUG ESPECIAL 841328: Tem container? {'linha_invoice_container' in self.ids}")
            
            # 🔥 CONTROLAR BOTÃO VISUALIZAR INVOICE
            if hasattr(self, 'ids') and 'btn_visualizar_invoice_card' in self.ids:
                btn_invoice = self.ids.btn_visualizar_invoice_card
                if info_invoice:
                    print(f"✅ DEBUG: Tem invoice, habilitando botão")
                    # Habilitar botão se existe invoice
                    btn_invoice.background_color = (0.1, 0.5, 0.1, 1)  # Verde
                    btn_invoice.disabled = False
                else:
                    print(f"❌ DEBUG: Sem invoice, desabilitando botão")
                    # Desabilitar botão se não existe invoice
                    btn_invoice.background_color = (0.3, 0.3, 0.3, 1)  # Cinza
                    btn_invoice.disabled = True
            
            if not info_invoice:
                print(f"❌ DEBUG: Nenhuma invoice encontrada")
                if 'linha_invoice_container' in self.ids:
                    self.ids.linha_invoice_container.height = 0
                    self.ids.linha_invoice_container.opacity = 0
                return
            
            # 🔥 QUANDO HÁ INVOICE, MOSTRAR A LINHA E AJUSTAR ALTURA DO CARD
            print(f"✅ DEBUG: Invoice encontrada, criando linha...")
            container = self.ids.linha_invoice_container
            container.clear_widgets()
            container.height = dp(25)  # Altura fixa quando visível
            container.opacity = 1
            
            # 🔥 AJUSTAR ALTURA TOTAL DO CARD QUANDO TEM INVOICE
            self.height = dp(295)  # 270 + 25 da linha da invoice
            
            # CORES MAIS ESCURAS PARA CONTRASTE
            COR_TEXTO_ESCURO = (0.6, 0.6, 0.6, 1)
            COR_AMARELO_ESCURO = (0.7, 0.5, 0.1, 1)
            COR_VERDE_ESCURO = (0.08, 0.4, 0.08, 1)
            COR_VERMELHO_ESCURO = (0.5, 0.15, 0.15, 1)
            
            # Label do status da invoice
            self.lbl_status_invoice = Label(
                text='Invoice: Pendente',
                font_size='12sp',
                color=COR_AMARELO_ESCURO,
                size_hint_x=0.7,
                text_size=(None, None),
                halign='left'
            )
            
            # Botão reenviar
            self.btn_reenviar_invoice = Button(
                text='Reenviar',
                font_size='10sp',
                size_hint_x=0.3,
                background_color=COR_VERDE_ESCURO,
                background_normal='',
                color=(1, 1, 1, 1),
                on_press=self.reenviar_invoice,
                opacity=0
            )
            
            container.add_widget(self.lbl_status_invoice)
            container.add_widget(self.btn_reenviar_invoice)
            
            # Atualizar status com a cor correta
            self.atualizar_status_invoice_sincrono()
            
        except Exception as e:
            print(f"❌ DEBUG: Erro ao adicionar linha invoice: {e}")
            pass

    def atualizar_status_invoice_sincrono(self):
        """Atualiza o status da invoice sincronamente"""
        try:
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or 'linha_invoice_container' not in self.ids:
                return
            
            status = info_invoice['status']
            motivo_recusa = info_invoice.get('motivo_recusa', '')
            
            # 🔥 CORES MAIS VIVAS E DESTACADAS COM NEGRITO
            COR_AMARELO_DESTACADO = (1.0, 0.8, 0.0, 1)      # Amarelo vibrante
            COR_VERDE_DESTACADO = (0.2, 0.8, 0.2, 1)        # Verde vibrante
            COR_VERMELHO_DESTACADO = (0.9, 0.2, 0.2, 1)     # Vermelho vibrante
            
            # Definir texto e cor baseado no status
            if status == 'pending':
                texto = 'Invoice: Pendente'
                cor_texto = COR_AMARELO_DESTACADO
                mostrar_botao = False
            elif status == 'approved':
                texto = 'Invoice: Aprovado'
                cor_texto = COR_VERDE_DESTACADO
                mostrar_botao = False
            elif status == 'rejected':
                texto = 'Invoice: Recusado'
                cor_texto = COR_VERMELHO_DESTACADO
                mostrar_botao = True
            else:
                texto = 'Invoice: Pendente'
                cor_texto = COR_AMARELO_DESTACADO
                mostrar_botao = False
            
            # Adicionar motivo se existir
            if motivo_recusa and status == 'rejected':
                texto += f' - {motivo_recusa}'
            
            # 🔥 APLICAR FORMATAÇÃO DESTACADA
            if hasattr(self, 'lbl_status_invoice'):
                self.lbl_status_invoice.text = texto
                self.lbl_status_invoice.font_size = '13sp'  # 🔥 Tamanho maior
                self.lbl_status_invoice.color = cor_texto
                self.lbl_status_invoice.bold = True         # 🔥 NEGRITO
            
            # Atualizar botão
            if hasattr(self, 'btn_reenviar_invoice'):
                self.btn_reenviar_invoice.opacity = 1 if mostrar_botao else 0
                self.btn_reenviar_invoice.font_size = '11sp'
                self.btn_reenviar_invoice.background_color = COR_VERDE_DESTACADO
                self.btn_reenviar_invoice.bold = True       # 🔥 Botão também em negrito
            
        except Exception:
            pass

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
            sistema = App.get_running_app().sistema
            
            # Obter dados do cliente
            usuario_atual = sistema.usuario_logado['username']
            dados_cliente = sistema.usuarios[usuario_atual]
            
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
            self.mostrar_popup_erro_pdf(str(e))

    def reenviar_invoice(self, instance=None):
        """Abre modal SUPER SIMPLIFICADO para reenviar invoice - MESMA LÓGICA DA TELA TRANSFERENCIA"""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            import os
            
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or info_invoice['status'] != 'rejected':
                self.mostrar_erro("Não é possível reenviar invoice neste status!")
                return
            
            motivo_recusa = info_invoice.get('motivo_recusa', 'Motivo não especificado')
            
            # 🔥 USAR MESMA LÓGICA DA TELA TRANSFERENCIA - INTERFACE SIMPLIFICADA
            content = BoxLayout(orientation='vertical', spacing=15, padding=25)
            
            # Título amigável
            lbl_titulo = Label(
                text='[b]REENVIAR INVOICE[/b]',
                markup=True,
                color=(0.9, 0.9, 0.9, 1),
                font_size='18sp',
                size_hint_y=0.15,
                text_size=(400, None),
                halign='center'
            )
            
            # Motivo da recusa
            lbl_motivo = Label(
                text=f'[b]Motivo da recusa anterior:[/b]\n"{motivo_recusa}"',
                markup=True,
                color=(1, 0.5, 0.5, 1),  # Vermelho claro
                font_size='12sp',
                size_hint_y=0.25,
                text_size=(400, None),
                halign='center'
            )
            
            # Área de Drag & Drop (igual à tela transferência)
            area_drag_drop = Button(
                text='[b]SOLTE O NOVO INVOICE AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)',
                markup=True,
                background_color=(0.2, 0.3, 0.4, 0.3),
                background_normal='',
                color=(0.8, 0.8, 0.8, 1),
                font_size='14sp',
                size_hint_y=0.35,
                halign='center'
            )
            
            # Pastas rápidas
            pastas_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
            
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
            botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
            
            btn_limpar = Button(
                text='Limpar',
                background_color=(0.8, 0.3, 0.3, 1),
                font_size='12sp'
            )
            
            btn_cancelar = Button(
                text='CANCELAR',
                background_color=(0.5, 0.5, 0.5, 1),
                font_size='12sp'
            )
            
            btn_enviar = Button(
                text='ENVIAR NOVA INVOICE',
                background_color=(0.2, 0.7, 0.3, 1),
                font_size='14sp',
                bold=True
            )
            
            botoes_layout.add_widget(btn_limpar)
            botoes_layout.add_widget(btn_cancelar)
            botoes_layout.add_widget(btn_enviar)
            
            content.add_widget(lbl_titulo)
            content.add_widget(lbl_motivo)
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
                size_hint=(0.85, 0.75),  # Um pouco maior para acomodar o botão extra
                background_color=(0.12, 0.16, 0.23, 1),
                auto_dismiss=False
            )
            
            def atualizar_status(nome_arquivo, sucesso=True):
                """Atualiza o status visual"""
                nonlocal lbl_status
                
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                
                if sucesso:
                    texto = f'✅ [b]{nome_arquivo}[/b]\nPronto para enviar!'
                    cor = (0.2, 0.8, 0.2, 1)
                else:
                    texto = f'❌ {nome_arquivo}'
                    cor = (1, 0.3, 0.3, 1)
                
                lbl_status = Label(
                    text=texto,
                    markup=True,
                    color=cor,
                    font_size='12sp',
                    size_hint_y=0.1,
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
                from kivy.uix.filechooser import FileChooserListView
                
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
                    self.reenviar_invoice()  # Reabre o popup simples
                
                def escolher_arquivo(instance=None, selection=None, touch=None):
                    """Função corrigida para aceitar diferentes chamadas"""
                    if filechooser.selection:
                        caminho = filechooser.selection[0]
                        if processar_arquivo(caminho):
                            popup_avancado.dismiss()
                    else:
                        lbl_instrucao.text = '❌ Selecione um arquivo!'
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
                area_drag_drop.text = '[b]SOLTE O NOVO INVOICE AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)'
                area_drag_drop.background_color = (0.2, 0.3, 0.4, 0.3)
                
                # Remover status
                nonlocal lbl_status
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                    content.do_layout()
            
            def cancelar_upload(instance):
                """Fecha o popup e volta para minhas transferências"""
                popup.dismiss()
                # Não é necessário fazer nada mais, o usuário já está na tela Minhas Transferências
            
            def enviar_nova_invoice(instance):
                """Processa o envio da nova invoice - MESMA LÓGICA DA TELA TRANSFERENCIA"""
                if not arquivo_selecionado:
                    atualizar_status("Selecione um arquivo primeiro!", False)
                    return
                
                # 🔥 USAR MESMA LÓGICA: Copiar arquivo para o sistema
                caminho_destino = self.copiar_arquivo_invoice(
                    arquivo_selecionado, 
                    self.transferencia_id
                )
                
                if caminho_destino:
                    # Atualizar no sistema - MARCAR COMO PENDENTE NOVAMENTE
                    if sistema.adicionar_invoice_info_transferencia(self.transferencia_id, caminho_destino):
                        popup.dismiss()
                        
                        # 🔥 MOSTRAR MENSAGEM DE SUCESSO COM BOTÃO OK
                        self.mostrar_sucesso_com_botao(
                            "Nova invoice enviada com sucesso!\n\n" +
                            "Status: Pendente de análise\n" +
                            "Aguarde a revisão do administrador."
                        )
                        
                        # Atualizar o card - CORREÇÃO: usar o método correto
                        self.atualizar_status_invoice_sincrono()  # 🔥 NOME CORRETO
                    else:
                        atualizar_status("Erro ao enviar nova invoice!", False)
                else:
                    atualizar_status("Erro ao processar arquivo!", False)
            
            # Bind dos eventos
            area_drag_drop.bind(on_press=abrir_seletor_generico)
            btn_documentos.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Documents')))
            btn_downloads.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Downloads')))
            btn_desktop.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Desktop')))
            btn_limpar.bind(on_press=limpar_selecao)
            btn_cancelar.bind(on_press=cancelar_upload)  # 🔥 NOVO BOTÃO CANCELAR
            btn_enviar.bind(on_press=enviar_nova_invoice)
            
            # 🔥 ADICIONAR: Suporte a drag & drop real
            def on_drop_file(window, file_path, x, y):
                """Processa arquivo arrastado para a janela - VERSÃO CORRIGIDA"""
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
            print(f"❌ Erro ao reenviar invoice: {e}")
            self.mostrar_erro(f"Erro: {str(e)}")

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
import datetime

class TransferenciaCard(BoxLayout):
    """Card individual para cada transferência - CORES DO SISTEMA ESCURAS"""
    
    cor_status = ListProperty([0.8, 0.5, 0.0, 1])
    transferencia_id = StringProperty("")
    dados = ObjectProperty(None)
    
    def __init__(self, transferencia_id, dados, **kwargs):
        super().__init__(**kwargs)
        self.transferencia_id = transferencia_id
        self.dados = dados

        # CORES DO SISTEMA - VERSÕES MAIS ESCURAS
        self.COR_PRIMARIA = (0.15, 0.35, 0.75, 1)
        self.COR_SECUNDARIA = (0.4, 0.25, 0.75, 1)
        self.COR_SUCESSO = (0.1, 0.6, 0.1, 1)
        self.COR_AVISO = (0.8, 0.5, 0.0, 1)
        self.COR_ERRO = (0.7, 0.2, 0.2, 1)
        self.FUNDO_CARD = (0.15, 0.20, 0.28, 1)
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(250)
        self.padding = [4, 4]
        self.spacing = 0
        

        # 🔥 NOVOS VALORES PARA BORDAS ARREDONDADAS
        self.RAIO_BORDA_CARD = [dp(12)]  # Aumentado de 5 para 12
        self.RAIO_BORDA_HEADER = [dp(12), dp(12), 0, 0]  # Cantos superiores arredondados

        # Calcular cor do status
        self.cor_status = self.calcular_cor_status()
        
        # Adicionar fundo do card
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*self.FUNDO_CARD)
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

        # 🔥 CONFIGURAR BOTÕES IMEDIATAMENTE - SEM DELAY
        self.configurar_botoes_card()

    def calcular_cor_status(self):
        """Calcula a cor baseada no status da TRANSFERÊNCIA - CORES ESCURAS"""
        if not hasattr(self, 'dados') or not self.dados:
            return [0.8, 0.5, 0.0, 1]
        
        # 🔥 CORREÇÃO: TRATAR 'solicitada' COMO 'pending' TAMBÉM AQUI
        status = self.dados['status']
        if status == 'solicitada':
            status = 'pending'
            
        if status == 'pending':
            return [0.8, 0.5, 0.0, 1]  # 🟠 ÂMBAR/ LARANJA ESCURO
        elif status == 'processing':
            return [0.2, 0.5, 0.8, 1]  # 🔵 AZUL ESCURO
        elif status == 'completed':
            return [0.1, 0.6, 0.1, 1]  # 🟢 VERDE ESCURO
        else:  # rejected
            return [0.7, 0.2, 0.2, 1]  # 🔴 VERMELHO ESCURO

    def criar_card(self):
        """Cria o conteúdo do card"""
        if not hasattr(self, 'dados') or not self.dados:
            return
            
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados do usuário CORRETAMENTE
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        contas_usuario = usuario_data.get('contas', [])
        
        # 🔥 CORREÇÃO: TRATAR 'solicitada' COMO 'pending' (PADRÃO ANTERIOR)
        status = self.dados['status']
        if status == 'solicitada':
            status = 'pending'
        
        # Calcular a cor do status (MANTIDO COMO ANTES)
        self.cor_status = self.calcular_cor_status()
        
        # 🔥 PADRÃO ORIGINAL - TEXTOS EXATOS COMO ANTES
        if status == 'pending':
            texto_status = "PENDENTE"
        elif status == 'processing':
            texto_status = "PROCESSANDO"  # ✅ PADRÃO ORIGINAL
        elif status == 'completed':
            texto_status = "CONCLUÍDA"    # ✅ PADRÃO ORIGINAL
        else:  # rejected
            texto_status = "RECUSADA"     # ✅ PADRÃO ORIGINAL
        
        # 🔥 ATUALIZAR FUNDO DO CARD COM BORDAS MAIS ARREDONDADAS
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*self.FUNDO_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=self.RAIO_BORDA_CARD  # 🔥 USANDO NOVO RAIO
            )

        # 🔥🔥🔥 DEBUG: VERIFICAR DADOS DA TRANSFERÊNCIA
        print(f"🔍 DEBUG TIPO TRANSFERÊNCIA {self.dados.get('id')}:")
        print(f"   tipo = {self.dados.get('tipo')}")
        print(f"   pais = {self.dados.get('pais')}")
        print(f"   beneficiario = {self.dados.get('beneficiario')}")
        print(f"   nome_banco = {self.dados.get('nome_banco')}")
        print(f"   conta_remetente = {self.dados.get('conta_remetente')}")

        # Determinar tipo e informações
        if self.dados.get('tipo') in ['internacional', 'transferencia_internacional']:
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
            # 🔥 CORREÇÃO: Usar contas_usuario em vez de sistema.usuario_logado['contas']
            if self.dados['conta_remetente'] in contas_usuario:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_destinatario', 'N/A'))
                info_extra = " • Enviada"
            else:
                beneficiario = self.obter_nome_cliente(self.dados.get('conta_remetente', 'N/A'))
                info_extra = " • Recebida"
            texto_tipo += info_extra
            banco = "Banco Interno"
            swift = "N/A"
            iban = self.dados.get('conta_destinatario', 'N/A')

        # 🔥 PREENCHER DADOS IMEDIATAMENTE
        self._preencher_dados_card_sincrono(texto_status, texto_tipo, beneficiario, banco, swift, iban)

    def configurar_botoes_card(self):
        """Configura os botões do card UMA VEZ na inicialização - VERSÃO SÍNCRONA"""
        try:
            if not hasattr(self, 'ids'):
                return
                
            # 🔥 CORES DEFINITIVAS - MESMAS DO SISTEMA
            COR_AZUL_ESCURO = [0.2, 0.4, 0.5, 1]
            COR_VERDE_ESCURO = [0.3, 0.5, 0.4, 1]
            COR_ROXO_ESCURO = [0.4, 0.4, 0.45, 1]
            COR_BRANCO = [1, 1, 1, 1]
            COR_CINZA = [0.3, 0.3, 0.3, 1]
            
            # 🔥 CONFIGURAR BOTÕES IMEDIATAMENTE
            if 'btn_detalhes_card' in self.ids:
                btn = self.ids.btn_detalhes_card
                btn.background_color = COR_AZUL_ESCURO
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '11sp'
            
            # 🔥 VERIFICAR INVOICE DE FORMA SÍNCRONA
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            tem_invoice = info_invoice is not None
            
            if 'btn_visualizar_invoice_card' in self.ids:
                btn = self.ids.btn_visualizar_invoice_card
                if tem_invoice:
                    btn.background_color = COR_VERDE_ESCURO
                    btn.disabled = False
                else:
                    btn.background_color = COR_CINZA
                    btn.disabled = True
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '10sp'
            
            if 'btn_pdf_card' in self.ids:
                btn = self.ids.btn_pdf_card
                btn.background_color = COR_ROXO_ESCURO
                btn.color = COR_BRANCO
                btn.background_normal = ''
                btn.font_size = '10sp'
                
        except Exception as e:
            print(f"Erro rápido ao configurar botões: {e}")

    def _preencher_dados_card_sincrono(self, texto_status, texto_tipo, beneficiario, banco, swift, iban):
        """Preenche os dados do card sincronamente - SEM DELAY"""
        try:
            if not hasattr(self, 'ids'):
                return
                
            # Atualizar header IMEDIATAMENTE
            if 'lbl_status_transferencia' in self.ids:
                self.ids.lbl_status_transferencia.text = f"TRANSFERÊNCIA {texto_status}"
            
            if 'lbl_tipo_transferencia' in self.ids:
                self.ids.lbl_tipo_transferencia.text = texto_tipo
            
            # Atualizar informações bancárias IMEDIATAMENTE
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
            
            # Atualizar valor IMEDIATAMENTE
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
            
            # Atualizar data IMEDIATAMENTE
            if 'lbl_data' in self.ids:
                data_bruta = self.dados.get('data_solicitacao') or self.dados.get('data') or ''
                if data_bruta:
                    # Converte para string e remove a parte do tempo
                    data_str = str(data_bruta)
                    data_simples = data_str.split(' ')[0]  # Para formato "2025-11-21 18:04:25"
                    data_simples = data_simples.split('T')[0]  # Para formato "2025-11-21T18:04:25"
                else:
                    data_simples = ''
                self.ids.lbl_data.text = data_simples
            
            # Atualizar ID IMEDIATAMENTE
            if 'lbl_id' in self.ids:
                self.ids.lbl_id.text = self.transferencia_id
            
            # 🔥 CONFIGURAR INVOICE IMEDIATAMENTE (sem Clock)
            self.adicionar_linha_invoice_se_necesario_sincrono()
                
        except Exception as e:
            print(f"Erro rápido no preenchimento: {e}")

    def adicionar_linha_invoice_se_necesario_sincrono(self):
        """Adiciona linha da invoice sincronamente"""
        try:
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            # 🔥 CONTROLAR BOTÃO VISUALIZAR INVOICE
            if hasattr(self, 'ids') and 'btn_visualizar_invoice_card' in self.ids:
                btn_invoice = self.ids.btn_visualizar_invoice_card
                if info_invoice:
                    # Habilitar botão se existe invoice
                    btn_invoice.background_color = (0.1, 0.5, 0.1, 1)  # Verde
                    btn_invoice.disabled = False
                else:
                    # Desabilitar botão se não existe invoice
                    btn_invoice.background_color = (0.3, 0.3, 0.3, 1)  # Cinza
                    btn_invoice.disabled = True
            
            if not info_invoice:
                if 'linha_invoice_container' in self.ids:
                    self.ids.linha_invoice_container.height = 0
                    self.ids.linha_invoice_container.opacity = 0
                return
            
            # 🔥 QUANDO HÁ INVOICE, MOSTRAR A LINHA E AJUSTAR ALTURA DO CARD
            container = self.ids.linha_invoice_container
            container.clear_widgets()
            container.height = dp(25)  # Altura fixa quando visível
            container.opacity = 1
            
            # 🔥 AJUSTAR ALTURA TOTAL DO CARD QUANDO TEM INVOICE
            self.height = dp(295)  # 270 + 25 da linha da invoice

                
            container = self.ids.linha_invoice_container
            container.clear_widgets()
            container.height = dp(25)
            container.opacity = 1
            
            # CORES MAIS ESCURAS PARA CONTRASTE
            COR_TEXTO_ESCURO = (0.6, 0.6, 0.6, 1)
            COR_AMARELO_ESCURO = (0.7, 0.5, 0.1, 1)
            COR_VERDE_ESCURO = (0.08, 0.4, 0.08, 1)
            COR_VERMELHO_ESCURO = (0.5, 0.15, 0.15, 1)
            
            # Label do status da invoice
            self.lbl_status_invoice = Label(
                text='Invoice: Pendente',
                font_size='12sp',
                color=COR_AMARELO_ESCURO,
                size_hint_x=0.7,
                text_size=(None, None),
                halign='left'
            )
            
            # Botão reenviar
            self.btn_reenviar_invoice = Button(
                text='Reenviar',
                font_size='10sp',
                size_hint_x=0.3,
                background_color=COR_VERDE_ESCURO,
                background_normal='',
                color=(1, 1, 1, 1),
                on_press=self.reenviar_invoice,
                opacity=0
            )
            
            container.add_widget(self.lbl_status_invoice)
            container.add_widget(self.btn_reenviar_invoice)
            
            # Atualizar status com a cor correta
            self.atualizar_status_invoice_sincrono()
            
        except Exception:
            pass

    def atualizar_status_invoice_sincrono(self):
        """Atualiza o status da invoice sincronamente"""
        try:
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or 'linha_invoice_container' not in self.ids:
                return
            
            status = info_invoice['status']
            motivo_recusa = info_invoice.get('motivo_recusa', '')
            
            # 🔥 CORES MAIS VIVAS E DESTACADAS COM NEGRITO
            COR_AMARELO_DESTACADO = (1.0, 0.8, 0.0, 1)      # Amarelo vibrante
            COR_VERDE_DESTACADO = (0.2, 0.8, 0.2, 1)        # Verde vibrante
            COR_VERMELHO_DESTACADO = (0.9, 0.2, 0.2, 1)     # Vermelho vibrante
            
            # Definir texto e cor baseado no status
            if status == 'pending':
                texto = 'Invoice: Pendente'
                cor_texto = COR_AMARELO_DESTACADO
                mostrar_botao = False
            elif status == 'approved':
                texto = 'Invoice: Aprovado'
                cor_texto = COR_VERDE_DESTACADO
                mostrar_botao = False
            elif status == 'rejected':
                texto = 'Invoice: Recusado'
                cor_texto = COR_VERMELHO_DESTACADO
                mostrar_botao = True
            else:
                texto = 'Invoice: Pendente'
                cor_texto = COR_AMARELO_DESTACADO
                mostrar_botao = False
            
            # Adicionar motivo se existir
            if motivo_recusa and status == 'rejected':
                texto += f' - {motivo_recusa}'
            
            # 🔥 APLICAR FORMATAÇÃO DESTACADA
            if hasattr(self, 'lbl_status_invoice'):
                self.lbl_status_invoice.text = texto
                self.lbl_status_invoice.font_size = '13sp'  # 🔥 Tamanho maior
                self.lbl_status_invoice.color = cor_texto
                self.lbl_status_invoice.bold = True         # 🔥 NEGRITO
            
            # Atualizar botão
            if hasattr(self, 'btn_reenviar_invoice'):
                self.btn_reenviar_invoice.opacity = 1 if mostrar_botao else 0
                self.btn_reenviar_invoice.font_size = '11sp'
                self.btn_reenviar_invoice.background_color = COR_VERDE_DESTACADO
                self.btn_reenviar_invoice.bold = True       # 🔥 Botão também em negrito
            
        except Exception:
            pass

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
            sistema = App.get_running_app().sistema
            
            # Obter dados do cliente
            usuario_atual = sistema.usuario_logado['username']
            dados_cliente = sistema.usuarios[usuario_atual]
            
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
            self.mostrar_popup_erro_pdf(str(e))

    def reenviar_invoice(self, instance=None):
        """Abre modal SUPER SIMPLIFICADO para reenviar invoice - MESMA LÓGICA DA TELA TRANSFERENCIA"""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            import os
            
            sistema = App.get_running_app().sistema
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            
            if not info_invoice or info_invoice['status'] != 'rejected':
                self.mostrar_erro("Não é possível reenviar invoice neste status!")
                return
            
            motivo_recusa = info_invoice.get('motivo_recusa', 'Motivo não especificado')
            
            # 🔥 USAR MESMA LÓGICA DA TELA TRANSFERENCIA - INTERFACE SIMPLIFICADA
            content = BoxLayout(orientation='vertical', spacing=15, padding=25)
            
            # Título amigável
            lbl_titulo = Label(
                text='[b]REENVIAR INVOICE[/b]',
                markup=True,
                color=(0.9, 0.9, 0.9, 1),
                font_size='18sp',
                size_hint_y=0.15,
                text_size=(400, None),
                halign='center'
            )
            
            # Motivo da recusa
            lbl_motivo = Label(
                text=f'[b]Motivo da recusa anterior:[/b]\n"{motivo_recusa}"',
                markup=True,
                color=(1, 0.5, 0.5, 1),  # Vermelho claro
                font_size='12sp',
                size_hint_y=0.25,
                text_size=(400, None),
                halign='center'
            )
            
            # Área de Drag & Drop (igual à tela transferência)
            area_drag_drop = Button(
                text='[b]SOLTE O NOVO INVOICE AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)',
                markup=True,
                background_color=(0.2, 0.3, 0.4, 0.3),
                background_normal='',
                color=(0.8, 0.8, 0.8, 1),
                font_size='14sp',
                size_hint_y=0.35,
                halign='center'
            )
            
            # Pastas rápidas
            pastas_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
            
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
            botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
            
            btn_limpar = Button(
                text='Limpar',
                background_color=(0.8, 0.3, 0.3, 1),
                font_size='12sp'
            )
            
            btn_cancelar = Button(
                text='CANCELAR',
                background_color=(0.5, 0.5, 0.5, 1),
                font_size='12sp'
            )
            
            btn_enviar = Button(
                text='ENVIAR NOVA INVOICE',
                background_color=(0.2, 0.7, 0.3, 1),
                font_size='14sp',
                bold=True
            )
            
            botoes_layout.add_widget(btn_limpar)
            botoes_layout.add_widget(btn_cancelar)
            botoes_layout.add_widget(btn_enviar)
            
            content.add_widget(lbl_titulo)
            content.add_widget(lbl_motivo)
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
                size_hint=(0.85, 0.75),  # Um pouco maior para acomodar o botão extra
                background_color=(0.12, 0.16, 0.23, 1),
                auto_dismiss=False
            )
            
            def atualizar_status(nome_arquivo, sucesso=True):
                """Atualiza o status visual"""
                nonlocal lbl_status
                
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                
                if sucesso:
                    texto = f'✅ [b]{nome_arquivo}[/b]\nPronto para enviar!'
                    cor = (0.2, 0.8, 0.2, 1)
                else:
                    texto = f'❌ {nome_arquivo}'
                    cor = (1, 0.3, 0.3, 1)
                
                lbl_status = Label(
                    text=texto,
                    markup=True,
                    color=cor,
                    font_size='12sp',
                    size_hint_y=0.1,
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
                from kivy.uix.filechooser import FileChooserListView
                
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
                    self.reenviar_invoice()  # Reabre o popup simples
                
                def escolher_arquivo(instance=None, selection=None, touch=None):
                    """Função corrigida para aceitar diferentes chamadas"""
                    if filechooser.selection:
                        caminho = filechooser.selection[0]
                        if processar_arquivo(caminho):
                            popup_avancado.dismiss()
                    else:
                        lbl_instrucao.text = '❌ Selecione um arquivo!'
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
                area_drag_drop.text = '[b]SOLTE O NOVO INVOICE AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)'
                area_drag_drop.background_color = (0.2, 0.3, 0.4, 0.3)
                
                # Remover status
                nonlocal lbl_status
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                    content.do_layout()
            
            def cancelar_upload(instance):
                """Fecha o popup e volta para minhas transferências"""
                popup.dismiss()
                # Não é necessário fazer nada mais, o usuário já está na tela Minhas Transferências
            
            def enviar_nova_invoice(instance):
                """Processa o envio da nova invoice - MESMA LÓGICA DA TELA TRANSFERENCIA"""
                if not arquivo_selecionado:
                    atualizar_status("Selecione um arquivo primeiro!", False)
                    return
                
                # 🔥 USAR MESMA LÓGICA: Copiar arquivo para o sistema
                caminho_destino = self.copiar_arquivo_invoice(
                    arquivo_selecionado, 
                    self.transferencia_id
                )
                
                if caminho_destino:
                    # Atualizar no sistema - MARCAR COMO PENDENTE NOVAMENTE
                    if sistema.adicionar_invoice_info_transferencia(self.transferencia_id, caminho_destino):
                        popup.dismiss()
                        
                        # 🔥 MOSTRAR MENSAGEM DE SUCESSO COM BOTÃO OK
                        self.mostrar_sucesso_com_botao(
                            "Nova invoice enviada com sucesso!\n\n" +
                            "Status: Pendente de análise\n" +
                            "Aguarde a revisão do administrador."
                        )
                        
                        # Atualizar o card - CORREÇÃO: usar o método correto
                        self.atualizar_status_invoice_sincrono()  # 🔥 NOME CORRETO
                    else:
                        atualizar_status("Erro ao enviar nova invoice!", False)
                else:
                    atualizar_status("Erro ao processar arquivo!", False)
            
            # Bind dos eventos
            area_drag_drop.bind(on_press=abrir_seletor_generico)
            btn_documentos.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Documents')))
            btn_downloads.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Downloads')))
            btn_desktop.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Desktop')))
            btn_limpar.bind(on_press=limpar_selecao)
            btn_cancelar.bind(on_press=cancelar_upload)  # 🔥 NOVO BOTÃO CANCELAR
            btn_enviar.bind(on_press=enviar_nova_invoice)
            
            # 🔥 ADICIONAR: Suporte a drag & drop real
            def on_drop_file(window, file_path, x, y):
                """Processa arquivo arrastado para a janela - VERSÃO CORRIGIDA"""
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
            print(f"❌ Erro ao reenviar invoice: {e}")
            self.mostrar_erro(f"Erro: {str(e)}")

    def copiar_arquivo_invoice(self, caminho_origem, transferencia_id):
        """Copia o arquivo de invoice para o SUPABASE STORAGE - VERSÃO CORRIGIDA"""
        try:
            import os
            import shutil
            
            # 🔥 VERIFICAR SE SUPABASE ESTÁ DISPONÍVEL
            sistema = App.get_running_app().sistema
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                print("📤 Enviando invoice para Supabase Storage...")
                
                # Gerar nome único para o arquivo no Supabase
                nome_arquivo = os.path.basename(caminho_origem)
                nome_base, extensao = os.path.splitext(nome_arquivo)
                novo_nome = f"{transferencia_id}_{nome_base}{extensao}"
                
                # 🔥 CAMINHO NO SUPABASE STORAGE (com barras normais)
                caminho_supabase = f"transferencias/{novo_nome}"
                
                # 🔥 LER ARQUIVO E ENVIAR PARA SUPABASE STORAGE
                with open(caminho_origem, 'rb') as file:
                    file_data = file.read()
                
                response = sistema.supabase.client.storage.from_("invoices")\
                    .upload(caminho_supabase, file_data)
                
                if response:
                    print(f"✅ Invoice enviada para Supabase Storage: {caminho_supabase}")
                    
                    # 🔥 CORREÇÃO: Retornar caminho do SUPABASE (não local)
                    return caminho_supabase
                else:
                    print(f"❌ Erro ao enviar invoice para Supabase Storage")
                    # Fallback para local (mantendo lógica original)
                    return self._copiar_arquivo_local_fallback(caminho_origem, transferencia_id)
            else:
                print("⚠️ Supabase não disponível, usando armazenamento local")
                return self._copiar_arquivo_local_fallback(caminho_origem, transferencia_id)
                
        except Exception as e:
            print(f"❌ Erro ao copiar invoice para Supabase: {e}")
            # Fallback para local em caso de erro (mantendo compatibilidade)
            return self._copiar_arquivo_local_fallback(caminho_origem, transferencia_id)

    def criar_popup_detalhes(self):
        """Cria popup com detalhes completos da transferência - COM SCROLL QUANDO NECESSÁRIO"""
        from kivy.uix.scrollview import ScrollView
        
        sistema = App.get_running_app().sistema
        
        # 🔥 CORES DO POPUP MAIS ESCURAS
        COR_FUNDO_POPUP = (0.10, 0.14, 0.20, 1)
        COR_TEXTO_POPUP = (0.8, 0.8, 0.8, 1)
        COR_TITULO_POPUP = (0.15, 0.35, 0.75, 1)
        COR_DESTAQUE = (0.23, 0.51, 0.96, 1)
        
        content = BoxLayout(orientation='vertical', padding=[30, 25, 30, 25], spacing=20)
        
        # Título maior
        content.add_widget(Label(
            text="DETALHES COMPLETOS DA TRANSFERÊNCIA",
            bold=True,
            font_size='18sp',
            color=COR_TITULO_POPUP,
            size_hint_y=None,
            height=dp(40),
            text_size=(500, None),
            halign='center'
        ))
        
        # 🔥 SCROLLVIEW PARA CONTEÚDO
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=(0.3, 0.3, 0.3, 0.8),
            bar_inactive_color=(0.2, 0.2, 0.2, 0.5)
        )
        
        # Container principal para todos os detalhes (com altura dinâmica)
        detalhes_layout = BoxLayout(
            orientation='vertical', 
            spacing=12, 
            padding=[10, 0],
            size_hint_y=None
        )
        detalhes_layout.bind(minimum_height=detalhes_layout.setter('height'))
        
        # ========== INFORMAÇÕES BÁSICAS ==========
        info_basica = f"""
[b]INFORMAÇÕES BÁSICAS:[/b]
ID: {self.transferencia_id}
Status: {self.dados['status'].upper()}
Tipo: {'INTERNACIONAL' if self.dados.get('tipo') == 'internacional' else 'INTERNA'}
Valor: {self.dados['valor']:,.2f} {self.dados['moeda']}
Taxa: {self.dados.get('taxa', 0):,.2f}
Total: {(self.dados['valor'] + self.dados.get('taxa', 0)):,.2f} {self.dados['moeda']}
Data: {self.dados.get('data_solicitacao', self.dados.get('data', 'N/A'))}
        """.strip()
        
        lbl_basica = Label(
            text=info_basica,
            markup=True,
            font_size='14sp',
            color=COR_TEXTO_POPUP,
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=dp(160)
        )
        detalhes_layout.add_widget(lbl_basica)
        
        # ========== INFORMAÇÕES DO CLIENTE ==========
        cliente_nome = self.obter_nome_cliente(self.dados['conta_remetente'])
        info_cliente = f"""
[b]CLIENTE REMETENTE:[/b]
Nome: {cliente_nome}
Conta Origem: {self.dados['conta_remetente']}
Solicitado por: {self.dados.get('solicitado_por', 'N/A')}
        """.strip()
        
        lbl_cliente = Label(
            text=info_cliente,
            markup=True,
            font_size='14sp',
            color=COR_TEXTO_POPUP,
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=dp(100)
        )
        detalhes_layout.add_widget(lbl_cliente)
        
        # ========== INFORMAÇÕES DO BENEFICIÁRIO/DESTINATÁRIO ==========
        if self.dados.get('tipo') == 'internacional':
            info_beneficiario = f"""
[b]BENEFICIÁRIO INTERNACIONAL:[/b]
Nome: {self.dados.get('beneficiario', 'N/A')}
Endereço: {self.dados.get('endereco_beneficiario', 'N/A')}
Cidade: {self.dados.get('cidade_beneficiario', self.dados.get('cidade', 'N/A'))}
País: {self.dados.get('pais_beneficiario', self.dados.get('pais', 'N/A'))}
Banco: {self.dados.get('nome_banco', 'N/A')}
Código SWIFT: {self.dados.get('codigo_swift', 'N/A')}
IBAN/Conta: {self.dados.get('iban_account', 'N/A')}
            """.strip()
            altura_beneficiario = dp(200)
        else:
            conta_destino = self.dados.get('conta_destinatario', 'N/A')
            info_beneficiario = f"""
[b]DESTINATÁRIO INTERNO:[/b]
Nome: {self.obter_nome_cliente(conta_destino)}
Conta Destino: {conta_destino}
            """.strip()
            altura_beneficiario = dp(80)
        
        lbl_beneficiario = Label(
            text=info_beneficiario,
            markup=True,
            font_size='14sp',
            color=COR_TEXTO_POPUP,
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=altura_beneficiario
        )
        detalhes_layout.add_widget(lbl_beneficiario)
        
        # ========== INFORMAÇÕES ADICIONAIS ==========
        info_adicional = ""
        if 'finalidade' in self.dados:
            info_adicional += f"Finalidade: {self.dados['finalidade']}\n"
        if 'descricao' in self.dados:
            info_adicional += f"Descrição: {self.dados.get('descricao', 'Nenhuma')}\n"
        
        if info_adicional:
            lbl_adicional = Label(
                text=f"[b]INFORMAÇÕES ADICIONAIS:[/b]\n{info_adicional}",
                markup=True,
                font_size='14sp',
                color=COR_TEXTO_POPUP,
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=dp(80)
            )
            detalhes_layout.add_widget(lbl_adicional)
        
        # ========== INFORMAÇÕES DE PROCESSAMENTO ==========
        if self.dados.get('data_aprovacao'):
            info_processamento = f"""
[b]PROCESSAMENTO:[/b]
Aprovado por: {self.dados.get('executado_por', 'N/A')}
Data Aprovação: {self.dados.get('data_aprovacao', 'N/A')}
            """.strip()
            
            if self.dados.get('data_conclusao'):
                info_processamento += f"\nConcluído por: {self.dados.get('concluido_por', 'N/A')}"
                info_processamento += f"\nData Conclusão: {self.dados.get('data_conclusao', 'N/A')}"
            
            lbl_processamento = Label(
                text=info_processamento,
                markup=True,
                font_size='14sp',
                color=COR_TEXTO_POPUP,
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=dp(100)
            )
            detalhes_layout.add_widget(lbl_processamento)
        
        # ========== MOTIVO DA RECUSA ==========
        if self.dados.get('status') == 'rejected' and self.dados.get('motivo_recusa'):
            lbl_recusa = Label(
                text=f"[b]MOTIVO DA RECUSA:[/b]\n{self.dados['motivo_recusa']}",
                markup=True,
                font_size='14sp',
                color=(1, 0.5, 0.5, 1),
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=dp(80)
            )
            detalhes_layout.add_widget(lbl_recusa)
        
        # ========== DADOS SWIFT (se existirem) ==========
        if self.dados.get('dados_swift_pagamento'):
            swift_data = self.dados['dados_swift_pagamento']
            info_swift = "[b]DADOS SWIFT DO PAGAMENTO:[/b]\n"
            for key, value in swift_data.items():
                if value:  # Só mostrar campos preenchidos
                    # Formatar chave para melhor legibilidade
                    chave_formatada = key.replace('_', ' ').title()
                    info_swift += f"{chave_formatada}: {value}\n"
            
            lbl_swift = Label(
                text=info_swift,
                markup=True,
                font_size='12sp',
                color=(0.7, 0.8, 1.0, 1),
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=dp(180)
            )
            detalhes_layout.add_widget(lbl_swift)
        
        # ========== INFORMAÇÕES DA INVOICE ==========
        info_invoice = sistema.obter_info_invoice(self.transferencia_id)
        if info_invoice:
            status_invoice = info_invoice['status']
            if status_invoice == 'pending':
                texto_status = 'PENDENTE'
                cor_status = (1.0, 0.8, 0.0, 1)  # Amarelo
            elif status_invoice == 'approved':
                texto_status = 'APROVADA'
                cor_status = (0.2, 0.8, 0.2, 1)  # Verde
            elif status_invoice == 'rejected':
                texto_status = 'RECUSADA'
                cor_status = (1, 0.3, 0.3, 1)   # Vermelho
            else:
                texto_status = 'NÃO ENVIADA'
                cor_status = (0.7, 0.7, 0.7, 1)  # Cinza
            
            info_invoice_text = f"[b]STATUS DA INVOICE:[/b]\n{texto_status}"
            
            if info_invoice.get('motivo_recusa'):
                info_invoice_text += f"\nMotivo: {info_invoice['motivo_recusa']}"
            
            lbl_invoice = Label(
                text=info_invoice_text,
                markup=True,
                font_size='14sp',
                color=cor_status,
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=dp(80)
            )
            detalhes_layout.add_widget(lbl_invoice)
        
        # Adicionar detalhes_layout ao scroll
        scroll.add_widget(detalhes_layout)
        
        # Adicionar scroll ao content
        content.add_widget(scroll)
        
        # ========== BOTÃO FECHAR ==========
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.4, 0.25, 0.75, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            font_size='14sp',
            bold=True
        )
        
        content.add_widget(btn_fechar)
        
        # 🔥 TAMANHO FIXO DA JANELA - SCROLL LIDA COM CONTEÚDO LONGO
        popup = Popup(
            title=f'Transferência {self.transferencia_id}',
            title_color=COR_TITULO_POPUP,
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(650, 750),  # 🔥 TAMANHO FIXO - SCROLL ATIVO QUANDO NECESSÁRIO
            background_color=COR_FUNDO_POPUP,
            separator_color=COR_DESTAQUE,
            separator_height=dp(2),
            auto_dismiss=False
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        
        return popup

    def visualizar_invoice(self, instance=None):
        """Abre invoice do Supabase ou local - ÚNICA ALTERAÇÃO"""
        try:
            import os
            import subprocess
            import platform
            import tempfile
            
            sistema = App.get_running_app().sistema
            
            # 🔥 MESMA LÓGICA ATUAL - obter info da invoice
            info_invoice = sistema.obter_info_invoice(self.transferencia_id)
            if not info_invoice:
                self.mostrar_erro("Nenhuma invoice encontrada para esta transferência!")
                return
            
            caminho_arquivo = info_invoice.get('caminho_arquivo')
            if not caminho_arquivo:
                self.mostrar_erro("Caminho da invoice não encontrado!")
                return
            
            # ✅ VERIFICAR SE É CAMINHO DO SUPABASE
            if caminho_arquivo.startswith('transferencias/'):
                # 🔥 É DO SUPABASE - baixar e abrir
                if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                    self.mostrar_erro("Conexão com Supabase não disponível")
                    return
                
                # ✅ CÓDIGO CORRIGIDO:
                try:
                    response = sistema.supabase.client.storage.from_("invoices").download(caminho_arquivo)
                    
                    # 🔥 VERIFICAÇÃO CORRETA:
                    if isinstance(response, bytes):
                        # ✅ Download bem-sucedido - response são os bytes do arquivo
                        file_data = response
                    else:
                        self.mostrar_erro("Erro ao baixar invoice do Supabase")
                        return
                    
                    # Salvar temporariamente e abrir
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                        temp_file.write(file_data)
                        temp_path = temp_file.name
                    
                    arquivo_para_abrir = temp_path
                    
                except Exception as e:
                    self.mostrar_erro(f"Erro ao baixar invoice: {str(e)}")
                    return
                
                # Salvar temporariamente e abrir
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(response)
                    temp_path = temp_file.name
                
                arquivo_para_abrir = temp_path
                
            else:
                # 🔥 É CAMINHO LOCAL - usar lógica atual
                arquivo_para_abrir = caminho_arquivo
            
            # 🔥 MESMA LÓGICA ATUAL PARA ABRIR ARQUIVO
            sistema_operacional = platform.system()
            
            try:
                if sistema_operacional == "Windows":
                    os.startfile(arquivo_para_abrir)
                elif sistema_operacional == "Darwin":
                    subprocess.run(["open", arquivo_para_abrir])
                else:
                    subprocess.run(["xdg-open", arquivo_para_abrir])
                
                self.mostrar_sucesso("Invoice aberta com sucesso!")
                
            except Exception as e:
                self.mostrar_erro(f"Erro ao abrir arquivo: {str(e)}")
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao acessar invoice: {str(e)}")

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
            background_color=(0.23, 0.51, 0.96, 1),  # 🔥 AZUL da paleta
            color=(1, 1, 1, 1)
        )
        
        btn_ok = Button(
            text='OK',
            background_color=(0.55, 0.36, 0.96, 1),  # 🔥 ROXO da paleta
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
            background_color=(0.55, 0.36, 0.96, 1),  # 🔥 ROXO da paleta
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

    def mostrar_sucesso_com_botao(self, mensagem):
        """Mostra popup de sucesso com botão OK - VERSÃO CORRIGIDA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl = Label(
            text=mensagem, 
            color=(0.2, 0.8, 0.2, 1), 
            font_size='16sp',
            text_size=(350, None),
            halign='center'
        )
        
        # 🔥 BOTÃO OK
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

    def mostrar_erro(self, mensagem):
        """Mostra popup de erro - CORES DO SISTEMA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=mensagem,
            color=self.COR_ERRO,
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        ))
        
        # BOTÃO OK - Roxo secundário
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=self.COR_SECUNDARIA,
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Erro',
            title_color=self.COR_ERRO,
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso - CORES DO SISTEMA"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=mensagem,
            color=self.COR_SUCESSO,
            font_size='14sp',
            bold=True,
            text_size=(350, None),
            halign='center'
        ))
        
        # BOTÃO OK - Azul primário
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=self.COR_PRIMARIA,
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Sucesso',
            title_color=self.COR_SUCESSO,
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
        
        # PALETA DE CORES - VERSÕES ESCURAS DEFINITIVAS
        # Cores ativas (mais escuras)
        self.COR_PRIMARIA = (0.15, 0.35, 0.75, 1)
        self.COR_AVISO = (0.7, 0.45, 0.0, 1)
        self.COR_PROCESSANDO = (0.2, 0.5, 0.8, 1)
        self.COR_SUCESSO = (0.1, 0.5, 0.1, 1)
        self.COR_ERRO = (0.6, 0.2, 0.2, 1)
        
        # CORES INATIVAS - AINDA MAIS ESCURAS
        self.COR_PRIMARIA_ESCURA = (0.08, 0.15, 0.30, 1)
        self.COR_AVISO_ESCURA = (0.25, 0.18, 0.05, 1)
        self.COR_PROCESSANDO_ESCURA = (0.08, 0.20, 0.35, 1)
        self.COR_SUCESSO_ESCURA = (0.05, 0.20, 0.05, 1)
        self.COR_ERRO_ESCURA = (0.25, 0.08, 0.08, 1)
        
        self.FUNDO_ESCURO = (0.07, 0.10, 0.15, 1)
        self.FUNDO_CARD = (0.15, 0.20, 0.28, 1)
        
        # MAPEAMENTO ORGANIZADO
        self.CORES_CLARAS = {
            'all': self.COR_PRIMARIA,
            'pending': self.COR_AVISO, 
            'processing': self.COR_PROCESSANDO,
            'completed': self.COR_SUCESSO,
            'rejected': self.COR_ERRO
        }
        
        self.CORES_ESCURAS = {
            'all': self.COR_PRIMARIA_ESCURA,
            'pending': self.COR_AVISO_ESCURA,
            'processing': self.COR_PROCESSANDO_ESCURA, 
            'completed': self.COR_SUCESSO_ESCURA,
            'rejected': self.COR_ERRO_ESCURA
        }

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1000, 900)
        
        sistema = App.get_running_app().sistema
        if sistema.usuario_logado and sistema.tipo_usuario_logado == 'cliente':
            # Configurar cores dos botões inferiores
            self.configurar_cores_botoes_inferiores()
            
            # Inicializar filtro
            self.filtro_status = "all"
            self.forcar_cores_botoes()
            self.atualizar_filtro("all")

    def on_enter(self):
        """Chamado quando a tela é carregada - VERSÃO ULTRA-RÁPIDA"""
        from kivy.core.window import Window
        Window.size = (1000, 900)
        
        sistema = App.get_running_app().sistema
        if sistema.usuario_logado and sistema.tipo_usuario_logado == 'cliente':
            print("🎯 Iniciando Minhas Transferências (RÁPIDO)...")
            
            # 🔥 CONFIGURAÇÃO RÁPIDA
            self.filtro_status = "all"
            self.forcar_cores_botoes()
            
            # 🔥 CARREGAR VISUAL PRIMEIRO (rápido)
            self.carregar_transferencias_rapido("all")
            
            # 🔥 CONFIGURAR CORES DEPOIS
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.configurar_cores_botoes_inferiores(), 0.2)

        self.rolar_para_topo()

    def configurar_cores_botoes_inferiores(self):
        """Configura as cores dos botões inferiores - VERSÃO OTIMIZADA"""
        try:
            # 🔥 NOVAS CORES NEUTRAS E PROFISSIONAIS
            COR_CINZA_NEUTRO = (0.1, 0.2, 0.4, 1)     
            COR_CINZA_AZULADO = (0.22, 0.12, 0.4, 1)     
            COR_BRANCO = (1, 1, 1, 1)
            
            if hasattr(self, 'ids'):
                # 🔥 CONFIGURAÇÃO DIRETA SEM CLOCK
                if 'btn_atualizar' in self.ids:
                    btn = self.ids.btn_atualizar
                    btn.background_color = COR_CINZA_NEUTRO
                    btn.color = COR_BRANCO
                
                if 'btn_voltar_dashboard' in self.ids:
                    btn = self.ids.btn_voltar_dashboard
                    btn.background_color = COR_CINZA_AZULADO
                    btn.color = COR_BRANCO
                    
        except Exception:
            pass  # 🔥 SILENCIOSO - não travar a aplicação

    def forcar_cores_botoes(self):
        """Força as cores dos botões de filtro - CORES INDIVIDUAIS"""
        from kivy.clock import Clock
        
        def aplicar_cores(dt):
            try:
                # 🔥 CORES INDIVIDUAIS PARA CADA STATUS
                cores_ativas = {
                    'all': self.COR_PRIMARIA,           # Azul
                    'pending': self.COR_AVISO,          # Âmbar/Laranja  
                    'processing': self.COR_PROCESSANDO, # Azul processamento
                    'completed': self.COR_SUCESSO,      # Verde
                    'rejected': self.COR_ERRO           # Vermelho
                }
                
                cores_inativas = {
                    'all': self.COR_PRIMARIA_ESCURA,           # Azul escuro
                    'pending': self.COR_AVISO_ESCURA,          # Âmbar escuro
                    'processing': self.COR_PROCESSANDO_ESCURA, # Azul escuro
                    'completed': self.COR_SUCESSO_ESCURA,      # Verde escuro
                    'rejected': self.COR_ERRO_ESCURA           # Vermelho escuro
                }
                
                # 🔥 MAPEAMENTO BOTÕES
                mapeamento = {
                    'all': 'btn_todas',
                    'pending': 'btn_pendentes', 
                    'processing': 'btn_processamento',
                    'completed': 'btn_concluidas',
                    'rejected': 'btn_recusadas'
                }
                
                # 🔥 APLICAR CORES INDIVIDUAIS
                for status, botao_id in mapeamento.items():
                    if botao_id in self.ids:
                        btn = self.ids[botao_id]
                        if status == self.filtro_status:
                            # BOTÃO SELECIONADO - cor clara
                            btn.background_color = cores_ativas[status]
                            btn.color = (1, 1, 1, 1)  # Branco
                        else:
                            # BOTÃO NÃO SELECIONADO - cor escura individual
                            btn.background_color = cores_inativas[status]
                            btn.color = (0.8, 0.8, 0.8, 1)  # Cinza claro
                            
            except Exception as e:
                print(f"⚠️ Erro em forcar_cores_botoes: {e}")
        
        Clock.schedule_once(aplicar_cores, 0.05)

    def atualizar_filtro(self, filtro):
        """Atualiza o filtro e recarrega as transferências - VERSÃO OTIMIZADA"""
        self.filtro_status = filtro

        # FORÇAR CORES DOS BOTÕES DE FILTRO
        self.forcar_cores_botoes()
        
        # 🔥 USAR CARREGAMENTO OTIMIZADO
        self.carregar_transferencias_rapido(filtro)

    def carregar_transferencias_rapido(self, filtro_status="all"):
        """Versão OTIMIZADA do carregamento - carrega visual primeiro, dados depois"""
        sistema = App.get_running_app().sistema
        
        # 🔥 VERIFICAÇÃO RÁPIDA
        if not sistema.usuario_logado or not hasattr(self, 'ids') or 'scroll_container' not in self.ids:
            return
        
        container = self.ids.scroll_container
        container.clear_widgets()
        
        # 🔥 MOSTRAR LOADING IMEDIATAMENTE
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        
        loading_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(100),
            spacing=10,
            padding=20
        )
        
        loading_layout.add_widget(Label(
            text="🔄 Carregando transferências...",
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(40)
        ))
        
        container.add_widget(loading_layout)
        
        # 🔥 CARREGAR DADOS EM SEGUNDO PLANO
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._carregar_dados_em_segundo_plano(filtro_status), 0.1)

    def _carregar_dados_em_segundo_plano(self, filtro_status):
        """Carrega os dados pesados em segundo plano - APENAS TRANSFERÊNCIAS INTERNACIONAIS"""
        sistema = App.get_running_app().sistema
        
        # ✅✅✅ FORÇAR ATUALIZAÇÃO DO SUPABASE COM CONVERSÃO ROBUSTA
        try:
            from supabase import create_client
            import os
            import json
            from dotenv import load_dotenv
            
            load_dotenv()
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                supabase = create_client(supabase_url, supabase_key)
                
                # Buscar transferências ATUALIZADAS do Supabase
                response = supabase.table('transferencias').select('*').execute()
                
                if response.data:
                    # 🔥 CORREÇÃO CRÍTICA: CONVERSÃO ROBUSTA PARA DICIONÁRIOS
                    sistema.transferencias.clear()
                    transferencias_convertidas = 0
                    
                    for i, transferencia in enumerate(response.data):
                        # ✅ CONVERSÃO AGESSIVA: Tentar múltiplos métodos
                        dados_finais = None
                        
                        # Método 1: Já é dicionário
                        if isinstance(transferencia, dict):
                            dados_finais = transferencia
                        
                        # Método 2: É string JSON
                        elif isinstance(transferencia, str):
                            try:
                                dados_finais = json.loads(transferencia)
                                transferencias_convertidas += 1
                            except json.JSONDecodeError:
                                print(f"❌ Não consegui decodificar JSON: {transferencia[:100]}...")
                                continue
                        
                        # Método 3: Outro tipo estranho
                        else:
                            print(f"⚠️ Tipo inesperado: {type(transferencia)} - {str(transferencia)[:100]}...")
                            continue
                        
                        # Verificar se a conversão foi bem-sucedida
                        if dados_finais and 'id' in dados_finais:
                            sistema.transferencias[dados_finais['id']] = dados_finais
                        else:
                            print(f"❌ Dados inválidos após conversão: {dados_finais}")
                    
                    print(f"✅ {len(response.data)} transferências processadas, {transferencias_convertidas} convertidas de string")
                    
                    # 🔥 DEBUG DETALHADO DOS TIPOS
                    print(f"🔍 VERIFICAÇÃO FINAL DOS TIPOS:")
                    tipos = {}
                    for transferencia_id, dados in list(sistema.transferencias.items())[:10]:
                        tipo = type(dados).__name__
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                        if isinstance(dados, str):
                            print(f"   ❌ {transferencia_id}: AINDA É STRING! -> {dados[:100]}...")
                    
                    print(f"   📊 Distribuição de tipos: {tipos}")
                    
                else:
                    print("⚠️ Nenhuma transferência encontrada no Supabase")
            else:
                print("⚠️ Credenciais do Supabase não encontradas")
        except Exception as e:
            print(f"⚠️ Erro ao atualizar do Supabase: {e}")
            import traceback
            traceback.print_exc()
        
        # 🔥 DEBUG: Verificar tipos dos dados
        print(f"🔍 TIPOS DOS DADOS CARREGADOS:")
        for i, (transferencia_id, dados) in enumerate(list(sistema.transferencias.items())[:5]):
            print(f"   {i+1}. {transferencia_id}: tipo={type(dados)}")
            if isinstance(dados, str):
                print(f"      ⚠️ ATENÇÃO: Dados são string, não dicionário!")
        
        # 🔥 CORREÇÃO: Obter dados do usuário corretamente
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        contas_usuario = usuario_data.get('contas', [])
        
        # ✅ BUSCAR APENAS TRANSFERÊNCIAS INTERNACIONAIS DO CLIENTE
        transferencias_cliente = {}
        
        print(f"🔍 FILTRO: Verificando {len(sistema.transferencias)} transferências totais")
        print(f"🔍 FILTRO INTERNACIONAL: Aplicando filtro para mostrar apenas transferências internacionais")
        
        for transferencia_id, dados in sistema.transferencias.items():
            # ✅ VERIFICAÇÃO 1: É DO USUÁRIO?
            conta_remetente = dados.get('conta_remetente')
            conta_destinatario = dados.get('conta_destinatario')
            
            if conta_remetente not in contas_usuario and conta_destinatario not in contas_usuario:
                continue  # Ignorar transferências que não são do usuário
            
            # ✅ VERIFICAÇÃO 2: É TRANSFERÊNCIA INTERNACIONAL?
            tipo_transferencia = dados.get('tipo', '')
            
            # 🔥 FILTRO: APENAS transferências internacionais
            if tipo_transferencia not in ['internacional', 'transferencia_internacional']:
                print(f"❌ FILTRO INTERNACIONAL: {transferencia_id} - EXCLUÍDO (tipo: {tipo_transferencia})")
                continue  # Ignorar transferências que não são internacionais
            
            # ✅ SE CHEGOU AQUI, É UMA TRANSFERÊNCIA INTERNACIONAL DO USUÁRIO
            print(f"✅ FILTRO INTERNACIONAL: {transferencia_id} - INCLUÍDO (tipo: {tipo_transferencia})")
            transferencias_cliente[transferencia_id] = dados
        
        print(f"🔍 FILTRO: {len(transferencias_cliente)} transferências do usuário")
        print(f"🔍 FILTRO: Contas do usuário = {contas_usuario}")


        print(f"🔍 FILTRO: {len(transferencias_cliente)} transferências do usuário")
        print(f"🔍 FILTRO: Contas do usuário = {contas_usuario}")

        # 🔥 DEBUG DOS STATUS EXISTENTES (MOVido para ANTES do filtro)
        print(f"🔍 STATUS EXISTENTES nas {len(transferencias_cliente)} transferências:")
        status_count = {}
        for transferencia_id, dados in transferencias_cliente.items():
            status = dados.get('status', 'NO_STATUS')
            status_count[status] = status_count.get(status, 0) + 1
        
        for status, count in status_count.items():
            print(f"   📊 {status}: {count} transferências")

        # 🔥 APLICAR FILTRO DE STATUS (COMPATÍVEL COM ANTIGO E NOVO)
        print(f"🔍 FILTRO STATUS: Aplicando filtro '{filtro_status}' em {len(transferencias_cliente)} transferências")
        
        if filtro_status != "all":
            if filtro_status == "pending":
                # ✅ ACEITAR 'pending' (novo) E 'solicitada' (antigo)
                transferencias_cliente = {k: v for k, v in transferencias_cliente.items() 
                                        if v.get('status') in ['pending', 'solicitada']}
            else:
                transferencias_cliente = {k: v for k, v in transferencias_cliente.items() 
                                        if v.get('status') == filtro_status}
            
            print(f"🔍 FILTRO STATUS: {len(transferencias_cliente)} transferências após filtro '{filtro_status}'")

        # 🔥 DEBUG DOS STATUS EXISTENTES (ADICIONE AQUI)
        print(f"🔍 STATUS EXISTENTES nas {len(transferencias_cliente)} transferências:")
        status_count = {}
        for transferencia_id, dados in transferencias_cliente.items():
            status = dados.get('status', 'NO_STATUS')
            status_count[status] = status_count.get(status, 0) + 1
        
        for status, count in status_count.items():
            print(f"   📊 {status}: {count} transferências")


        # 🔥 DEBUG DAS DATAS DAS TRANSFERÊNCIAS
        #print(f"🔍 DATAS DAS TRANSFERÊNCIAS INCLUÍDAS:")
        #for transferencia_id, dados in transferencias_cliente.items():
        #    data_solicitacao = dados.get('data_solicitacao', 'N/A')
        #    data = dados.get('data', 'N/A')
        #    created_at = dados.get('created_at', 'N/A')
        #    print(f"   📅 {transferencia_id}: data_solicitacao={data_solicitacao}, data={data}, created_at={created_at}")
        
        # 🔥 APLICAR FILTRO DE STATUS (COMPATÍVEL COM ANTIGO E NOVO)
        if filtro_status != "all":
            if filtro_status == "pending":
                # ✅ ACEITAR 'pending' (novo) E 'solicitada' (antigo)
                transferencias_cliente = {k: v for k, v in transferencias_cliente.items() 
                                        if v.get('status') in ['pending', 'solicitada']}
            else:
                transferencias_cliente = {k: v for k, v in transferencias_cliente.items() 
                                        if v.get('status') == filtro_status}
        
        # 🔥 DEBUG CRÍTICO: Verificar as transferências ANTES da ordenação (ADICIONE AQUI)
        print(f"🔍 TRANSFERÊNCIAS ANTES DA ORDENAÇÃO ({len(transferencias_cliente)}):")
        for transferencia_id, dados in list(transferencias_cliente.items())[:3]:  # Mostrar só 3
            status = dados.get('status', 'NO_STATUS')
            tipo = dados.get('tipo', 'NO_TIPO')
            print(f"   📋 {transferencia_id}: status={status}, tipo={tipo}")

        # 🔥 CORREÇÃO CRÍTICA: ORDENAÇÃO SEGURA
        def get_data_ordenacao(dados):
            """Função segura para obter data de ordenação"""
            # Priorizar data_solicitacao, depois data, depois created_at
            data = (dados.get('data_solicitacao') or 
                   dados.get('data') or 
                   dados.get('created_at') or '1900-01-01')
            return data
        
        try:
            print(f"🔍 ORDENAÇÃO: Tentando ordenar {len(transferencias_cliente)} transferências")
            transferencias_ordenadas = sorted(
                transferencias_cliente.items(), 
                key=lambda x: get_data_ordenacao(x[1]), 
                reverse=True
            )
            print(f"🔍 ORDENAÇÃO: {len(transferencias_ordenadas)} transferências ordenadas com sucesso")
        except Exception as e:
            print(f"❌ ERRO NA ORDENAÇÃO: {e}")
            # Fallback: ordenar por ID se a ordenação por data falhar
            transferencias_ordenadas = sorted(
                transferencias_cliente.items(), 
                key=lambda x: x[0],  # Ordenar por ID
                reverse=True
            )
            print(f"🔍 ORDENAÇÃO FALLBACK: {len(transferencias_ordenadas)} transferências ordenadas por ID")
        print(f"🔍 ORDENAÇÃO: {len(transferencias_ordenadas)} transferências após ordenação")
        
        print(f"🔍 TRANSFERÊNCIAS ORDENADAS (primeiras 5):")
        for i, (transferencia_id, dados) in enumerate(transferencias_ordenadas[:5]):
            data_solicitacao = dados.get('data_solicitacao', 'N/A')
            print(f"   {i+1}. {transferencia_id} - {data_solicitacao}")
        
        # 🔥 ATUALIZAR INTERFACE COM OS DADOS
        self._atualizar_interface_com_dados(transferencias_ordenadas, filtro_status)

    def _atualizar_interface_com_dados(self, transferencias_ordenadas, filtro_status):
        """Atualiza a interface com os dados carregados"""
        container = self.ids.scroll_container
        container.clear_widgets()
        
        print(f"🔍 DEBUG INTERFACE: {len(transferencias_ordenadas)} transferências para exibir")
        
        # 🔥 LIMITE INICIAL PARA PERFORMANCE (carrega só 10 primeiros)
        limite_cards = min(10, len(transferencias_ordenadas))
        
        cards = []
        for i, (transferencia_id, dados) in enumerate(transferencias_ordenadas):
            if i >= limite_cards:
                break
                
            try:
                print(f"🔍 DEBUG CRIANDO CARD: {transferencia_id}")
                
                # 🔥🔥🔥 DEBUG CRÍTICO: Verificar estrutura dos dados problemáticos
                if transferencia_id in ['279581', '765195', '256062', '514735', '527343']:
                    print(f"   🚨 DADOS PROBLEMÁTICOS {transferencia_id}:")
                    for key, value in list(dados.items())[:5]:  # Mostra primeiros 5 campos
                        print(f"      {key}: {type(value)} = {str(value)[:50]}...")
                
                card = TransferenciaCard(transferencia_id, dados)
                card.size_hint_y = None
                card.height = dp(230)
                cards.append(card)
                print(f"✅ CARD CRIADO: {transferencia_id}")
            except Exception as e:
                print(f"❌ ERRO AO CRIAR CARD {transferencia_id}: {e}")
                import traceback
                traceback.print_exc()  # 🔥 MOSTRA A LINHA EXATA DO ERRO
                continue
        
        print(f"🔍 DEBUG: {len(cards)} cards criados com sucesso")
        
        # 🔥 ADICIONAR CARDS PRINCIPAIS
        for card in cards:
            container.add_widget(card)
            print(f"✅ CARD ADICIONADO NA INTERFACE: {card.transferencia_id}")
        
        print(f"🔍 DEBUG: {len(container.children)} widgets no container")
        
        # 🔥 SE HOUVER MAIS CARDS, MOSTRAR BOTÃO "CARREGAR MAIS"
        if len(transferencias_ordenadas) > limite_cards:
            from kivy.uix.button import Button
            
            btn_carregar_mais = Button(
                text=f'📥 Carregar mais {len(transferencias_ordenadas) - limite_cards} transferências',
                size_hint_y=None,
                height=dp(50),
                background_color=(0.23, 0.51, 0.96, 1),
                color=(1, 1, 1, 1),
                on_press=lambda x: self._carregar_restante(transferencias_ordenadas, limite_cards)
            )
            
            container.add_widget(btn_carregar_mais)
            print("✅ BOTÃO 'CARREGAR MAIS' ADICIONADO")
        
        # 🔥 MENSAGEM VAZIO
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
            
            container.add_widget(vazio_layout)
            print("✅ MENSAGEM 'VAZIO' ADICIONADA")
        
        print(f"🎯 INTERFACE ATUALIZADA: {len(container.children)} elementos visíveis")

    def _carregar_restante(self, transferencias_ordenadas, inicio):
        """Carrega o restante das transferências"""
        container = self.ids.scroll_container
        
        # 🔥 REMOVER BOTÃO "CARREGAR MAIS"
        if container.children and hasattr(container.children[0], 'text') and 'Carregar mais' in container.children[0].text:
            container.remove_widget(container.children[0])
        
        # 🔥 CARREGAR RESTANTE
        cards = []
        for i, (transferencia_id, dados) in enumerate(transferencias_ordenadas[inicio:], start=inicio):
            try:
                card = TransferenciaCard(transferencia_id, dados)
                card.size_hint_y = None
                card.height = dp(230)
                cards.append(card)
            except Exception:
                continue
        
        # 🔥 ADICIONAR NO FINAL
        for card in reversed(cards):  # Reversed para manter ordem correta
            container.add_widget(card, index=0)

    def rolar_para_topo(self):
        """Rola a ScrollView para o topo"""
        try:
            from kivy.clock import Clock
            Clock.schedule_once(self._executar_rolagem, 0.1)
        except Exception:
            pass

    def _executar_rolagem(self, dt):
        """Executa a rolagem para o topo"""
        try:
            # Método 1: Buscar por ID específico
            if hasattr(self, 'ids'):
                if 'scroll_principal' in self.ids:
                    self.ids.scroll_principal.scroll_y = 1.0
                    return
                
                # Método 2: Buscar qualquer ScrollView nos IDs
                for widget_id, widget in self.ids.items():
                    if hasattr(widget, 'scroll_y'):
                        widget.scroll_y = 1.0
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
                
        except Exception:
            pass

    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'