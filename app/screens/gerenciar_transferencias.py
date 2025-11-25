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
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import datetime

class ModalDetalhesTransferencia(Popup):
    """Modal para mostrar detalhes completos de uma transferência"""
    
    def __init__(self, transferencia, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Detalhes da Transferência'
        self.size_hint = (0.8, 0.8)
        self.background_color = (0.12, 0.16, 0.23, 1)
        self.transferencia = transferencia
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # ScrollView para conteúdo
        scroll = ScrollView()
        main_content = BoxLayout(orientation='vertical', size_hint_y=None)
        main_content.bind(minimum_height=main_content.setter('height'))
        
        self.preencher_detalhes(main_content, transferencia)
        
        scroll.add_widget(main_content)
        content.add_widget(scroll)
        
        # 🔥 BOTÃO PARA ACESSAR INVOICE - VERIFICAR SE EXISTE
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        # Verificar se existe invoice para esta transferência
        tem_invoice = self.verificar_invoice_existe(transferencia)
        
        if tem_invoice:
            btn_invoice = Button(
                text='Abrir Invoice',
                size_hint_x=0.5,
                background_color=(0.2, 0.7, 0.3, 1),  # Verde
                color=(1, 1, 1, 1)
            )
            btn_invoice.bind(on_press=self.abrir_invoice)
        else:
            btn_invoice = Button(
                text='Invoice Não Encontrada',
                size_hint_x=0.5,
                background_color=(0.7, 0.7, 0.7, 1),  # Cinza
                color=(0.5, 0.5, 0.5, 1),
                disabled=True
            )
        
        btn_fechar = Button(
            text='Fechar',
            size_hint_x=0.5,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_fechar.bind(on_press=self.dismiss)
        
        btn_layout.add_widget(btn_invoice)
        btn_layout.add_widget(btn_fechar)
        content.add_widget(btn_layout)
        
        self.content = content
    
    def verificar_invoice_existe(self, transferencia):
        """Verifica se existe um arquivo de invoice para esta transferência"""
        try:
            import os
            
            # Obter o ID da transferência
            transferencia_id = transferencia.get('id', '')
            if not transferencia_id:
                return False
            
            # 🔥 CAMINHO CORRETO: data/invoices
            pasta_invoices = "data/invoices"
            
            # Verificar se a pasta existe
            if not os.path.exists(pasta_invoices):
                print(f"⚠️ Pasta '{pasta_invoices}' não encontrada")
                return False
            
            # 🔥 PROCURAR POR QUALQUER ARQUIVO QUE CONTENHA O ID DA TRANSFERÊNCIA
            # Isso é mais flexível para diferentes padrões de nomeação
            arquivos_encontrados = []
            
            for nome_arquivo in os.listdir(pasta_invoices):
                if transferencia_id in nome_arquivo:
                    caminho_completo = os.path.join(pasta_invoices, nome_arquivo)
                    if os.path.isfile(caminho_completo):
                        arquivos_encontrados.append(caminho_completo)
            
            if arquivos_encontrados:
                print(f"✅ Invoice(s) encontrada(s) para transferência {transferencia_id}:")
                for arquivo in arquivos_encontrados:
                    print(f"   - {os.path.basename(arquivo)}")
                return True
            else:
                print(f"❌ Nenhuma invoice encontrada para transferência {transferencia_id}")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar invoice: {e}")
            return False
    
    def abrir_invoice(self, instance):
        """Abre o arquivo de invoice da transferência"""
        try:
            import os
            import subprocess
            import platform
            
            transferencia_id = self.transferencia.get('id', '')
            if not transferencia_id:
                self.mostrar_erro("ID da transferência não encontrado")
                return
            
            # 🔥 PROCURAR NA PASTA CORRETA: data/invoices
            pasta_invoices = "data/invoices"
            arquivos_encontrados = []
            
            # Listar todos os arquivos que contêm o ID da transferência
            for nome_arquivo in os.listdir(pasta_invoices):
                if transferencia_id in nome_arquivo:
                    caminho_completo = os.path.join(pasta_invoices, nome_arquivo)
                    if os.path.isfile(caminho_completo):
                        arquivos_encontrados.append(caminho_completo)
            
            if not arquivos_encontrados:
                self.mostrar_erro(f"Invoice não encontrada para a transferência {transferencia_id}")
                return
            
            # 🔥 SE HOUVER MÚLTIPLOS ARQUIVOS, ABRIR O PRIMEIRO
            # (Você pode modificar para mostrar uma lista se quiser escolher)
            arquivo_para_abrir = arquivos_encontrados[0]
            
            # 🔥 ABRIR O ARQUIVO COM O PROGRAMA PADRÃO DO SISTEMA
            sistema_operacional = platform.system()
            
            try:
                if sistema_operacional == "Windows":
                    os.startfile(arquivo_para_abrir)
                elif sistema_operacional == "Darwin":  # macOS
                    subprocess.run(["open", arquivo_para_abrir])
                else:  # Linux e outros
                    subprocess.run(["xdg-open", arquivo_para_abrir])
                
                self.mostrar_sucesso(f"Invoice aberta: {os.path.basename(arquivo_para_abrir)}")
                
            except Exception as e:
                self.mostrar_erro(f"Erro ao abrir arquivo: {str(e)}")
                # Tentar abrir o diretório como fallback
                try:
                    if sistema_operacional == "Windows":
                        os.startfile(pasta_invoices)
                    elif sistema_operacional == "Darwin":
                        subprocess.run(["open", pasta_invoices])
                    else:
                        subprocess.run(["xdg-open", pasta_invoices])
                    
                    self.mostrar_sucesso(f"Pasta invoices aberta. Arquivo: {os.path.basename(arquivo_para_abrir)}")
                except:
                    self.mostrar_erro(f"Arquivo encontrado mas não foi possível abrir: {arquivo_para_abrir}")
            
            # Fechar o modal após abrir a invoice
            self.dismiss()
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao acessar invoice: {str(e)}")
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.3, 0.8, 0.3, 1),
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
        
        content.add_widget(lbl_sucesso)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='✅ Sucesso',
            title_color=(0.3, 0.8, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def obter_data_transferencia(self, transferencia):
        """Obtém a data da transferência usando a MESMA LÓGICA DO EXTRATO"""
        # 🔥 MESMA LÓGICA DO EXTRATO - COPIADA DIRETAMENTE
        tipo = transferencia.get('tipo', 'transferencia_interna')
        status = transferencia.get('status', 'pending')
        
        # TRANSFERÊNCIA INTERNACIONAL
        if tipo == 'internacional':
            if status == 'rejected':
                return transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                # Para outros status: usar data_conclusao, data_aprovacao, data_solicitacao (nesta ordem)
                return transferencia.get('data_conclusao', 
                       transferencia.get('data_aprovacao', 
                       transferencia.get('data_solicitacao', 
                       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        # TRANSFERÊNCIA INTERNA
        elif tipo in ['transferencia_interna', 'transferencia']:
            if status == 'rejected':
                return transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # CÂMBIO
        elif tipo == 'cambio':
            return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # AJUSTE ADMINISTRATIVO
        elif tipo == 'ajuste_admin':
            return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # FALLBACK - usar data se existir, senão data atual
        return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def preencher_detalhes(self, container, transferencia):
        """Preenche os detalhes da transferência"""
        
        # 🔥 CORREÇÃO: Usar a mesma lógica do extrato para obter a data
        data_original = self.obter_data_transferencia(transferencia)
        data_formatada = self.formatar_data_br(data_original)
        
        # ID e Status
        self.adicionar_secao(container, 'Informações Gerais', [  # 🔥 REMOVER ÍCONE
            f"ID: {transferencia.get('id', 'N/A')}",
            f"Status: {self.formatar_status(transferencia.get('status', ''))}",
            f"Tipo: {transferencia.get('tipo', 'N/A')}",
            f"Data: {data_formatada}"
        ])
        
        # Valor e Moeda
        self.adicionar_secao(container, 'Valores', [  # 🔥 REMOVER ÍCONE
            f"Valor: {transferencia.get('valor', 0):,.2f} {transferencia.get('moeda', '')}",
            f"Taxa: {transferencia.get('taxa', 0):,.2f}",
            f"Total: {(transferencia.get('valor', 0) + transferencia.get('taxa', 0)):,.2f} {transferencia.get('moeda', '')}"
        ])
        
        # Remetente
        self.adicionar_secao(container, 'Remetente', [  # 🔥 REMOVER ÍCONE
            f"Conta: {transferencia.get('conta_remetente', 'N/A')}",
            f"Cliente: {transferencia.get('solicitado_por', transferencia.get('cliente_afetado', 'N/A'))}"
        ])
        
        # Destinatário/Beneficiário (se houver)
        if transferencia.get('conta_destinatario') or transferencia.get('beneficiario'):
            self.adicionar_secao(container, 'Destinatário', [  # 🔥 REMOVER ÍCONE
                f"Conta: {transferencia.get('conta_destinatario', 'N/A')}",
                f"Beneficiário: {transferencia.get('beneficiario', 'N/A')}",
                f"Banco: {transferencia.get('nome_banco', 'N/A')}",
                f"SWIFT: {transferencia.get('codigo_swift', 'N/A')}",
                f"IBAN: {transferencia.get('iban_account', 'N/A')}"
            ])
        
        # Informações adicionais
        if transferencia.get('finalidade'):
            self.adicionar_secao(container, 'Informações Adicionais', [  # 🔥 REMOVER ÍCONE
                f"Finalidade: {transferencia.get('finalidade', 'N/A')}",
                f"Descrição: {transferencia.get('descricao', 'N/A')}"
            ])
    
    def adicionar_secao(self, container, titulo, itens):
        """Adiciona uma seção de informações"""
        # Título da seção
        lbl_titulo = Label(
            text=titulo,
            font_size='14sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=30,
            text_size=(None, None),
            halign='left'
        )
        container.add_widget(lbl_titulo)
        
        # Itens
        for item in itens:
            lbl_item = Label(
                text=item,
                font_size='12sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=25,
                text_size=(None, None),
                halign='left'
            )
            container.add_widget(lbl_item)
        
        # Espaçamento
        container.add_widget(Label(size_hint_y=None, height=10))
    
    def formatar_status(self, status):
        """Formata o status sem ícones"""
        status_textos = {
            'completed': 'Concluída',
            'rejected': 'Rejeitada', 
            'processing': 'Processando',
            'pending': 'Pendente'
        }
        return status_textos.get(status, status)
    
    def formatar_data_br(self, data_original):
        """Converte data de AAAA-MM-DD para DD/MM/AAAA"""
        if not data_original:
            return 'Sem data'  # 🔥 MUDAR DE 'N/A' PARA 'Sem data'
        
        try:
            # Se a data estiver no formato "2025-11-01", vamos converter diretamente
            if len(data_original) == 10 and data_original.count('-') == 2:
                partes = data_original.split('-')
                if len(partes[0]) == 4:  # Primeira parte é o ano
                    ano = partes[0]
                    mes = partes[1]
                    dia = partes[2]
                    return f"{dia}/{mes}/{ano}"
            
            # Se tiver hora, como "2025-11-01 10:30:00"
            if ' ' in data_original:
                data_parte = data_original.split(' ')[0]
                if len(data_parte) == 10 and data_parte.count('-') == 2:
                    partes = data_parte.split('-')
                    if len(partes[0]) == 4:
                        ano = partes[0]
                        mes = partes[1]
                        dia = partes[2]
                        return f"{dia}/{mes}/{ano}"
            
            return data_original
                
        except Exception as e:
            print(f"Erro ao formatar data '{data_original}': {e}")
            return data_original

class CardTransferencia(BoxLayout):
    """Card para exibir uma transferência na lista"""
    
    def __init__(self, transferencia, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [10, 5, 10, 5]
        self.spacing = dp(5)
        self.transferencia = transferencia
        self.tela_pai = tela_pai
        
        # 🔥 CORREÇÃO: Garantir que o card comece vazio
        self.clear_widgets()
        
        # Cor baseada no status
        status = transferencia.get('status', 'pending')
        if status == 'completed':
            cor_fundo = (0.85, 0.95, 0.85, 1)  # Verde suave
        elif status == 'rejected':
            cor_fundo = (0.95, 0.85, 0.85, 1)  # Vermelho suave
        elif status == 'processing':
            cor_fundo = (0.85, 0.90, 0.95, 1)  # 🔥 AZUL SUAVE (novo)
        else:  # pending
            cor_fundo = (0.95, 0.92, 0.80, 1)  # 🔥 AMBER SUAVE (novo)
        
        # Background do card
        with self.canvas.before:
            Color(*cor_fundo)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        self.criar_conteudo(transferencia)
    
    def _atualizar_rect(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    
    def obter_data_transferencia(self, transferencia):
        """Obtém a data da transferência usando a MESMA LÓGICA DO EXTRATO"""
        # 🔥 MESMA LÓGICA DO EXTRATO - COPIADA DIRETAMENTE
        tipo = transferencia.get('tipo', 'transferencia_interna')
        status = transferencia.get('status', 'pending')
        
        # TRANSFERÊNCIA INTERNACIONAL
        if tipo == 'internacional':
            if status == 'rejected':
                return transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                # Para outros status: usar data_conclusao, data_aprovacao, data_solicitacao (nesta ordem)
                return transferencia.get('data_conclusao', 
                       transferencia.get('data_aprovacao', 
                       transferencia.get('data_solicitacao', 
                       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        # TRANSFERÊNCIA INTERNA
        elif tipo in ['transferencia_interna', 'transferencia']:
            if status == 'rejected':
                return transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # CÂMBIO
        elif tipo == 'cambio':
            return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # AJUSTE ADMINISTRATIVO
        elif tipo == 'ajuste_admin':
            return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # FALLBACK - usar data se existir, senão data atual
        return transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def criar_conteudo(self, transferencia):
        """Cria o conteúdo do card usando a MESMA LÓGICA DO EXTRATO"""
        
        # 🔥 USAR A MESMA LÓGICA DO EXTRATO PARA OBTER A DATA
        data_original = self.obter_data_transferencia(transferencia)
        
        # 🔥 FORMATAR DATA PARA DD/MM/AAAA (IGUAL AO EXTRATO)
        data_formatada = self.formatar_data_br(data_original)
        
        # Status texto completo (sem abreviações)
        status = transferencia.get('status', 'pending')
        if status == 'completed':
            status_texto = 'Completed'  # 🔥 PALAVRA COMPLETA
        elif status == 'rejected':
            status_texto = 'Rejected'   # 🔥 PALAVRA COMPLETA
        elif status == 'processing':
            status_texto = 'Processing' # 🔥 PALAVRA COMPLETA
        else:
            status_texto = 'Pending'    # 🔥 PALAVRA COMPLETA
        
        # Descrição resumida
        tipo = transferencia.get('tipo', 'transferencia')
        if tipo == 'internacional':
            descricao = f"{transferencia.get('beneficiario', 'N/A')}"
        elif tipo == 'cambio':
            descricao = "OPERACAO DE CAMBIO"
        elif tipo == 'ajuste_admin':
            descricao = "AJUSTE ADMINISTRATIVO"
        else:
            # Transferência interna - tentar obter nome do destinatário
            conta_destino = transferencia.get('conta_destinatario', '')
            descricao = f"Conta {conta_destino}" if conta_destino else "Transferencia Interna"
        
        # 🔥 CORREÇÃO: Limpar qualquer widget existente antes de adicionar novos
        self.clear_widgets()
        
        # Coluna 1: Data (15%)
        col_data = BoxLayout(orientation='vertical', size_hint_x=0.15)
        lbl_data = Label(
            text=data_formatada,
            font_size='11sp',
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        col_data.add_widget(lbl_data)
        
        # Coluna 2: Status (10%) - Ajustar tamanho da coluna para acomodar texto maior
        col_status = BoxLayout(orientation='vertical', size_hint_x=0.15)  # 🔥 AUMENTADO DE 0.1 PARA 0.15
        lbl_status = Label(
            text=status_texto,
            font_size='10sp',  # 🔥 FONTE UM POUCO MENOR PARA CABER
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        col_status.add_widget(lbl_status)
        
        # Coluna 3: Descrição (40%) - Ajustar proporção
        col_descricao = BoxLayout(orientation='vertical', size_hint_x=0.35)  # 🔥 REDUZIDO DE 0.4 PARA 0.35
        lbl_descricao = Label(
            text=descricao,
            font_size='11sp',
            color=(0.3, 0.3, 0.3, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        col_descricao.add_widget(lbl_descricao)
        
        # Coluna 4: Valor (20%)
        col_valor = BoxLayout(orientation='vertical', size_hint_x=0.2)
        valor = transferencia.get('valor', 0)
        moeda = transferencia.get('moeda', '')
        lbl_valor = Label(
            text=f"{valor:,.2f} {moeda}",
            font_size='11sp',
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        col_valor.add_widget(lbl_valor)
        
        # Coluna 5: Ações (25% - aumentada para 3 botões)
        col_acoes = BoxLayout(orientation='horizontal', size_hint_x=0.25, spacing=3)
        
        btn_detalhes = Button(
            text='Detalhes',  # Ícone para detalhes
            font_size='10sp',
            size_hint_x=0.33,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        btn_detalhes.bind(on_press=self.mostrar_detalhes)
        
        # 🔥 BOTÃO PARA INVOICE - VERIFICAR SE EXISTE
        tem_invoice = self.verificar_invoice_existe(transferencia)
        
        if tem_invoice:
            btn_invoice = Button(
                text='Invoice',  # Ícone para invoice
                font_size='10sp',
                size_hint_x=0.33,
                background_color=(0.2, 0.7, 0.3, 1),  # Verde
                color=(1, 1, 1, 1)
            )
            btn_invoice.bind(on_press=self.abrir_invoice_direto)
        else:
            btn_invoice = Button(
                text='Invoice',  # Ícone para invoice
                font_size='10sp',
                size_hint_x=0.33,
                background_color=(0.5, 0.5, 0.5, 0.5),  # Cinza transparente
                color=(0.7, 0.7, 0.7, 1),
                disabled=True
            )
        
        col_acoes.add_widget(btn_detalhes)
        col_acoes.add_widget(btn_invoice)
        
        # Adicionar todas as colunas
        self.add_widget(col_data)
        self.add_widget(col_status)
        self.add_widget(col_descricao)
        self.add_widget(col_valor)
        self.add_widget(col_acoes)
    
    def verificar_invoice_existe(self, transferencia):
        """Verifica se existe invoice na pasta data/invoices"""
        try:
            import os
            
            transferencia_id = transferencia.get('id', '')
            if not transferencia_id:
                return False
            
            # 🔥 CAMINHO CORRETO: data/invoices
            pasta_invoices = "data/invoices"
            
            if not os.path.exists(pasta_invoices):
                return False
            
            # 🔥 PROCURAR QUALQUER ARQUIVO QUE CONTENHA O ID
            for nome_arquivo in os.listdir(pasta_invoices):
                if transferencia_id in nome_arquivo:
                    caminho_completo = os.path.join(pasta_invoices, nome_arquivo)
                    if os.path.isfile(caminho_completo):
                        return True
            
            return False
            
        except:
            return False
    
    def abrir_invoice_direto(self, instance):
        """Abre a invoice diretamente do card (sem abrir modal)"""
        try:
            import os
            import subprocess
            import platform
            
            transferencia_id = self.transferencia.get('id', '')
            if not transferencia_id:
                return
            
            # 🔥 PROCURAR NA PASTA CORRETA: data/invoices
            pasta_invoices = "data/invoices"
            arquivos_encontrados = []
            
            # Listar arquivos que contêm o ID
            for nome_arquivo in os.listdir(pasta_invoices):
                if transferencia_id in nome_arquivo:
                    caminho_completo = os.path.join(pasta_invoices, nome_arquivo)
                    if os.path.isfile(caminho_completo):
                        arquivos_encontrados.append(caminho_completo)
            
            if not arquivos_encontrados:
                self.mostrar_erro("Invoice não encontrada")
                return
            
            # Abrir o primeiro arquivo encontrado
            arquivo_para_abrir = arquivos_encontrados[0]
            
            # Abrir arquivo
            sistema_operacional = platform.system()
            
            try:
                if sistema_operacional == "Windows":
                    os.startfile(arquivo_para_abrir)
                elif sistema_operacional == "Darwin":
                    subprocess.run(["open", arquivo_para_abrir])
                else:
                    subprocess.run(["xdg-open", arquivo_para_abrir])
                    
            except Exception as e:
                print(f"Erro ao abrir invoice: {e}")
                
        except Exception as e:
            print(f"Erro ao acessar invoice do card: {e}")
    
    def mostrar_erro(self, mensagem):
        """Mostra erro simples"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(None, None),
            size=(300, 150)
        )
        popup.open()

    def formatar_data_br(self, data_original):
        """Converte data de AAAA-MM-DD para DD/MM/AAAA - MESMA LÓGICA DO EXTRATO"""
        if not data_original:
            return 'Sem data'
        
        try:
            # Se a data estiver no formato "2025-11-01", vamos converter diretamente
            if len(data_original) == 10 and data_original.count('-') == 2:
                partes = data_original.split('-')
                if len(partes[0]) == 4:  # Primeira parte é o ano
                    ano = partes[0]
                    mes = partes[1]
                    dia = partes[2]
                    return f"{dia}/{mes}/{ano}"
            
            # Se tiver hora, como "2025-11-01 10:30:00"
            if ' ' in data_original:
                data_parte = data_original.split(' ')[0]
                if len(data_parte) == 10 and data_parte.count('-') == 2:
                    partes = data_parte.split('-')
                    if len(partes[0]) == 4:
                        ano = partes[0]
                        mes = partes[1]
                        dia = partes[2]
                        return f"{dia}/{mes}/{ano}"
            
            return data_original
                
        except Exception as e:
            print(f"Erro ao formatar data '{data_original}': {e}")
            return 'Sem data'
    
    def mostrar_detalhes(self, instance):
        """Mostra detalhes da transferência"""
        self.tela_pai.mostrar_detalhes_transferencia(self.transferencia)

class TelaGerenciarTransferencias(Screen):
    """Tela para gerenciar e visualizar transferências (Admin)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aba_atual = 'lista'  # lista, dashboard, relatorios
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1200, 900)
        self.carregar_dados_iniciais()
    
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("🌍 Tela Gerenciar Transferências carregada")
    
    def carregar_dados_iniciais(self):
        """Carrega todos os dados iniciais da tela"""
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Usar sistema.tipo_usuario_logado
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            self.voltar_dashboard()
            return
        
        # Carregar clientes para filtro
        self.carregar_clientes_filtro()
        
        # Carregar transferências
        self.carregar_transferencias()
    
    def carregar_clientes_filtro(self):
        """Carrega a lista de clientes para o filtro"""
        sistema = App.get_running_app().sistema
        
        clientes_opcoes = ['Todos os clientes']
        for username, dados in sistema.usuarios.items():
            if dados['tipo'] == 'cliente':
                clientes_opcoes.append(f"{username} - {dados['nome']}")
        
        if hasattr(self, 'ids'):
            self.ids.combo_cliente_filtro.values = clientes_opcoes
            self.ids.combo_cliente_filtro.text = clientes_opcoes[0]
    
    def carregar_transferencias(self, filtro_cliente=None, filtro_tipo=None, filtro_status=None, filtro_periodo=None, filtro_valor=None):
        """Carrega as transferências com filtros aplicados"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        container = self.ids.lista_transferencias
        container.clear_widgets()
        
        # Header das colunas
        header = self.criar_header_colunas()
        container.add_widget(header)
        
        # Coletar e filtrar transferências
        transferencias_filtradas = []
        
        for transferencia_id, dados in sistema.transferencias.items():
            # Aplicar filtros
            if filtro_cliente and filtro_cliente != 'Todos os clientes':
                cliente_filtro = filtro_cliente.split(' - ')[0]
                if dados.get('solicitado_por') != cliente_filtro and dados.get('cliente_afetado') != cliente_filtro:
                    continue
            
            if filtro_tipo and filtro_tipo != 'Todos os tipos':
                if dados.get('tipo') != filtro_tipo:
                    continue
            
            if filtro_status and filtro_status != 'Todos os status':
                if dados.get('status') != filtro_status:
                    continue
            
            # Aplicar filtro de período (simplificado)
            if filtro_periodo:
                try:
                    data_transf = datetime.datetime.strptime(dados.get('data', '').split(' ')[0], "%Y-%m-%d")
                    dias = int(filtro_periodo)
                    data_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
                    if data_transf < data_limite:
                        continue
                except:
                    pass
            
            # Aplicar filtro de valor
            if filtro_valor and filtro_valor != 'Todos os valores':
                valor = dados.get('valor', 0)
                if filtro_valor == '0 - 1.000' and valor > 1000:
                    continue
                elif filtro_valor == '1.000 - 10.000' and (valor <= 1000 or valor > 10000):
                    continue
                elif filtro_valor == '10.000 - 50.000' and (valor <= 10000 or valor > 50000):
                    continue
                elif filtro_valor == '50.000+' and valor <= 50000:
                    continue
            
            transferencias_filtradas.append(dados)
        
        self.atualizar_lista_transferencias(transferencias_filtradas)
    
    def atualizar_lista_transferencias(self, transferencias):
        """Atualiza a lista de transferências"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids'):
            return
        
        container = self.ids.lista_transferencias
        
        # Limpar cards antigos (mantendo o header)
        widgets_para_remover = []
        for widget in container.children:
            if not hasattr(widget, 'is_header'):
                widgets_para_remover.append(widget)
        
        for widget in widgets_para_remover:
            container.remove_widget(widget)
        
        # 🔥 CORREÇÃO: Usar a MESMA LÓGICA DO EXTRATO para obter e ordenar datas
        def obter_data_para_ordenacao(transferencia):
            """Obtém a data para ordenação usando a MESMA LÓGICA DO EXTRATO"""
            tipo = transferencia.get('tipo', 'transferencia_interna')
            status = transferencia.get('status', 'pending')
            
            # TRANSFERÊNCIA INTERNACIONAL
            if tipo == 'internacional':
                if status == 'rejected':
                    data_str = transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    # Para outros status: usar data_conclusao, data_aprovacao, data_solicitacao (nesta ordem)
                    data_str = transferencia.get('data_conclusao', 
                           transferencia.get('data_aprovacao', 
                           transferencia.get('data_solicitacao', 
                           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
            
            # TRANSFERÊNCIA INTERNA
            elif tipo in ['transferencia_interna', 'transferencia']:
                if status == 'rejected':
                    data_str = transferencia.get('data_recusa', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    data_str = transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # CÂMBIO
            elif tipo == 'cambio':
                data_str = transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # AJUSTE ADMINISTRATIVO
            elif tipo == 'ajuste_admin':
                data_str = transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # FALLBACK
            else:
                data_str = transferencia.get('data', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # 🔥 CONVERTER para datetime para ordenação (MESMA LÓGICA DO EXTRATO)
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
        
        # 🔥 ORDENAR por data (mais recente primeiro) - MESMA LÓGICA DO EXTRATO
        transferencias_ordenadas = sorted(transferencias, key=obter_data_para_ordenacao, reverse=True)
        
        # DEBUG: Verificar ordenação
        print("📅 DEBUG ORDENAÇÃO:")
        for i, transf in enumerate(transferencias_ordenadas[:5]):  # Mostrar apenas as 5 primeiras
            data_ordenacao = obter_data_para_ordenacao(transf)
            print(f"  {i+1}. ID={transf.get('id')} | Data={data_ordenacao} | Tipo={transf.get('tipo')} | Status={transf.get('status')}")
        
        # Adicionar cards
        for transferencia in transferencias_ordenadas:
            card = CardTransferencia(transferencia, self)
            container.add_widget(card)
        
        # Resto do código permanece igual...
        
        # Atualizar contador
        total_transferencias = len(sistema.transferencias)
        filtradas = len(transferencias_ordenadas)
        
        self.ids.lbl_contador.text = f"Mostrando {filtradas} de {total_transferencias} transferências"
        
        # Atualizar estatísticas
        self.atualizar_estatisticas(transferencias_ordenadas)
        self.atualizar_dashboard_avancado(transferencias_ordenadas)
    
    def criar_header_colunas(self):
        """Cria o header das colunas"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[10, 5, 10, 5],
            spacing=dp(5)
        )
        header.is_header = True  # Marcar como header
        
        # Background do header
        with header.canvas.before:
            Color(0.15, 0.20, 0.27, 1)
            header.rect = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[5,]
            )
        header.bind(pos=self._atualizar_header_rect, size=self._atualizar_header_rect)
        
        # Colunas (mesmas proporções do card)
        colunas = [
            ('Data', 0.15),
            ('Status', 0.1),
            ('Descrição', 0.4),
            ('Valor', 0.2),
            ('Ações', 0.15)
        ]
        
        for texto, largura in colunas:
            lbl = Label(
                text=texto,
                font_size='11sp',
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                text_size=(None, None),
                halign='center',
                valign='middle'
            )
            lbl.size_hint_x = largura
            header.add_widget(lbl)
        
        return header
    
    def _atualizar_header_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def atualizar_estatisticas(self, transferencias):
        """Atualiza o painel de estatísticas"""
        if not hasattr(self, 'ids'):
            return
        
        # Calcular estatísticas básicas
        total_valor = sum(t.get('valor', 0) for t in transferencias)
        por_status = {}
        por_moeda = {}
        
        for transf in transferencias:
            status = transf.get('status', 'pending')
            moeda = transf.get('moeda', '')
            
            if status not in por_status:
                por_status[status] = 0
            por_status[status] += 1
            
            if moeda not in por_moeda:
                por_moeda[moeda] = 0
            por_moeda[moeda] += transf.get('valor', 0)
        
        # Atualizar labels
        self.ids.lbl_total_valor.text = f"{total_valor:,.2f}"
        
        # Status
        status_text = ""
        for status, count in por_status.items():
            if status == 'completed':
                texto = 'CONCL'
            elif status == 'rejected':
                texto = 'REJCT'
            elif status == 'processing':
                texto = 'PROC'
            else:
                texto = 'PEND'
            status_text += f"{texto}: {count}  "
        
        self.ids.lbl_status.text = status_text
        
        # Moedas - dividir em 2 colunas
        moedas_items = list(por_moeda.items())
        metade = len(moedas_items) // 2
        
        # Coluna 1 (primeira metade)
        moedas_col1 = ""
        for moeda, valor in moedas_items[:metade]:
            if moeda:
                moedas_col1 += f"{moeda}: {valor:,.2f}\n"
        
        # Coluna 2 (segunda metade)  
        moedas_col2 = ""
        for moeda, valor in moedas_items[metade:]:
            if moeda:
                moedas_col2 += f"{moeda}: {valor:,.2f}\n"
        
        self.ids.lbl_moedas_col1.text = moedas_col1
        self.ids.lbl_moedas_col2.text = moedas_col2
    
    def atualizar_dashboard_avancado(self, transferencias):
        """Atualiza dashboard com métricas avançadas"""
        if not hasattr(self, 'ids'):
            return
        
        # Calcular métricas
        total_valor = sum(t.get('valor', 0) for t in transferencias)
        
        # Top clientes
        clientes_volume = {}
        for transf in transferencias:
            cliente = transf.get('solicitado_por') or transf.get('cliente_afetado', 'N/A')
            if cliente not in clientes_volume:
                clientes_volume[cliente] = 0
            clientes_volume[cliente] += transf.get('valor', 0)
        
        top_clientes = sorted(clientes_volume.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Distribuição por moeda
        por_moeda = {}
        for transf in transferencias:
            moeda = transf.get('moeda', '')
            if moeda not in por_moeda:
                por_moeda[moeda] = 0
            por_moeda[moeda] += transf.get('valor', 0)
        
        # Dividir moedas em 2 colunas
        moedas_items = list(por_moeda.items())
        metade = len(moedas_items) // 2
        
        # Coluna 1 (primeira metade)
        moedas_col1 = ""
        for moeda, valor in moedas_items[:metade]:
            if moeda:
                moedas_col1 += f"{moeda}: {valor:,.2f}\n"
        
        # Coluna 2 (segunda metade)  
        moedas_col2 = ""
        for moeda, valor in moedas_items[metade:]:
            if moeda:
                moedas_col2 += f"{moeda}: {valor:,.2f}\n"
        
        # Atualizar UI
        top_clientes_text = ""
        for i, (cliente, volume) in enumerate(top_clientes, 1):
            nome_cliente = cliente.split(' - ')[1] if ' - ' in cliente else cliente
            top_clientes_text += f"{i}. {nome_cliente}: {volume:,.2f}\n"
        
        self.ids.lbl_top_clientes.text = top_clientes_text
        self.ids.lbl_volume_total.text = f"{total_valor:,.2f}"
        
        # 🔥 CORREÇÃO: Atualizar as moedas do dashboard avançado
        self.ids.lbl_moedas_dashboard_col1.text = moedas_col1
        self.ids.lbl_moedas_dashboard_col2.text = moedas_col2
    
    def aplicar_filtros(self):
        """Aplica todos os filtros selecionados"""
        if not hasattr(self, 'ids'):
            return
        
        filtro_cliente = self.ids.combo_cliente_filtro.text
        filtro_tipo = self.ids.combo_tipo_filtro.text
        filtro_status = self.ids.combo_status_filtro.text
        filtro_periodo = self.ids.combo_periodo_filtro.text
        filtro_valor = self.ids.combo_valor_filtro.text
        
        # Converter período para dias
        periodo_dias = None
        if filtro_periodo == '7 dias':
            periodo_dias = '7'
        elif filtro_periodo == '30 dias':
            periodo_dias = '30'
        elif filtro_periodo == '90 dias':
            periodo_dias = '90'
        
        self.carregar_transferencias(filtro_cliente, filtro_tipo, filtro_status, periodo_dias, filtro_valor)
    
    def aplicar_busca(self):
        """Aplica busca por texto"""
        if not hasattr(self, 'ids'):
            return
        
        texto_busca = self.ids.input_busca.text.lower().strip()
        if not texto_busca:
            self.aplicar_filtros()
            return
        
        sistema = App.get_running_app().sistema
        transferencias_filtradas = []
        
        for transferencia_id, dados in sistema.transferencias.items():
            # Buscar em vários campos
            campos_busca = [
                dados.get('beneficiario', ''),
                dados.get('solicitado_por', ''),
                dados.get('cliente_afetado', ''),
                dados.get('descricao', ''),
                dados.get('finalidade', ''),
                dados.get('nome_banco', ''),
                str(dados.get('valor', ''))
            ]
            
            # Verificar se o texto está em algum campo
            encontrou = any(texto_busca in str(campo).lower() for campo in campos_busca)
            
            if encontrou:
                transferencias_filtradas.append(dados)
        
        self.atualizar_lista_transferencias(transferencias_filtradas)
    
    def limpar_filtros(self):
        """Limpa todos os filtros"""
        if hasattr(self, 'ids'):
            self.ids.combo_cliente_filtro.text = 'Todos os clientes'
            self.ids.combo_tipo_filtro.text = 'Todos os tipos'
            self.ids.combo_status_filtro.text = 'Todos os status'
            self.ids.combo_periodo_filtro.text = 'Todo período'
            self.ids.combo_valor_filtro.text = 'Todos os valores'
            self.ids.input_busca.text = ''
            self.carregar_transferencias()
    
    def mostrar_detalhes_transferencia(self, transferencia):
        """Mostra modal com detalhes da transferência"""
        modal = ModalDetalhesTransferencia(transferencia)
        modal.open()
    
    def exportar_relatorio(self):
        """Exporta relatório das transferências filtradas"""
        self.mostrar_sucesso("📊 Funcionalidade de exportação em desenvolvimento!")
    
    def exportar_relatorio_completo(self):
        """Exporta relatório completo em CSV"""
        sistema = App.get_running_app().sistema
        
        try:
            import csv
            from datetime import datetime
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_transferencias_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([
                    'ID', 'Data', 'Tipo', 'Status', 'Valor', 'Moeda',
                    'Remetente', 'Beneficiário', 'Banco', 'Finalidade'
                ])
                
                # Dados
                for transf_id, transf in sistema.transferencias.items():
                    writer.writerow([
                        transf_id,
                        transf.get('data', ''),
                        transf.get('tipo', ''),
                        transf.get('status', ''),
                        transf.get('valor', 0),
                        transf.get('moeda', ''),
                        transf.get('solicitado_por', ''),
                        transf.get('beneficiario', ''),
                        transf.get('nome_banco', ''),
                        transf.get('finalidade', '')
                    ])
            
            self.mostrar_sucesso(f"📊 Relatório exportado: {filename}")
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao exportar: {str(e)}")
    
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