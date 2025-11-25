from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.popup import Popup
import datetime
import random

class TelaGerenciarClienteDetalhe(Screen):
    """Tela para gerenciamento detalhado de um cliente"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username_cliente = None
        self.dados_cliente = None

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1000, 800)
    
    def carregar_contas_cliente(self, contas):
        """Carrega a seção de contas do cliente"""
        container = self.ids.contas_container
        container.clear_widgets()
        
        # 🔥 GARANTIR ALTURA MÍNIMA
        altura_minima = dp(60)  # Altura mínima quando vazio
        
        if not contas:
            lbl_vazio = Label(
                text="Nenhuma conta cadastrada",
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(lbl_vazio)
            container.height = altura_minima
            return
        
        # Calcular altura total baseada no número de contas
        altura_por_conta = dp(60)
        altura_total = len(contas) * altura_por_conta
        container.height = max(altura_minima, altura_total)
        
        for conta in contas:
            card = CardContaCliente(conta, self)
            container.add_widget(card)
    
    def carregar_dados_pessoais(self, username, dados_cliente):
        """Carrega a seção de dados pessoais - VERSÃO 4 COLUNAS"""
        container = self.ids.dados_pessoais_container
        container.clear_widgets()
        
        
        # Obter informações adicionais do sistema
        sistema = App.get_running_app().sistema
        contas_cliente = self.obter_contas_cliente(username)
        total_contas = len(contas_cliente)
        saldo_total = sum(conta['saldo'] for conta in contas_cliente)
        tem_beneficiarios = username in sistema.beneficiarios and len(sistema.beneficiarios[username]) > 0
        
        dados = [
            # Linha 1 - Dados principais
            ('USUÁRIO', username, (0.23, 0.51, 0.96, 1)),
            ('NOME', dados_cliente['nome'], (0.23, 0.51, 0.96, 1)),
            ('EMAIL', dados_cliente.get('email', 'N/A'), (0.55, 0.36, 0.96, 1)),
            ('TELEFONE', dados_cliente.get('telefone', 'N/A'), (0.55, 0.36, 0.96, 1)),
            
            # Linha 2 - Documentos e status
            ('DOCUMENTO', dados_cliente.get('documento', 'N/A'), (0.2, 0.8, 0.2, 1)),
            ('TIPO', dados_cliente.get('tipo', 'cliente').upper(), (0.96, 0.36, 0.36, 1)),
            ('DATA CADASTRO', dados_cliente.get('data_cadastro', 'N/A'), (0.9, 0.7, 0.3, 1)),
            ('ÚLTIMO ACESSO', dados_cliente.get('ultimo_acesso', 'N/A'), (0.7, 0.5, 0.9, 1)),
            
            # Linha 3 - Informações financeiras
            ('TOTAL CONTAS', str(total_contas), (0.3, 0.7, 0.9, 1)),
            ('SALDO TOTAL', f"{saldo_total:,.2f}", (0.2, 0.8, 0.2, 1)),
            ('STATUS', self.obter_status_cliente(dados_cliente), (0.3, 0.7, 0.9, 1)),
            ('BENEFICIÁRIOS', 'SIM' if tem_beneficiarios else 'NÃO', (0.9, 0.5, 0.3, 1))
        ]
        
        for chave, valor, cor in dados:
            card = self.criar_card_dado_4colunas(chave, valor, cor)
            container.add_widget(card)
    
    def criar_card_dado_4colunas(self, chave, valor, cor_titulo):
        """Cria um card individual para layout de 4 colunas"""
        card = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(60),  # 🔥 REDUZIDO de 70 para 60
            padding=dp(4),  # 🔥 REDUZIDO
            spacing=dp(1)   # 🔥 REDUZIDO
        )
        
        # Background do card
        with card.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(4),])  # 🔥 REDUZIDO radius
            Color(0.12, 0.16, 0.23, 0.8)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(4)), width=0.8)
        
        # Label da chave (título)
        lbl_chave = Label(
            text=chave,
            font_size='12sp',  # 🔥 REDUZIDO
            bold=True,
            color=cor_titulo,
            size_hint_y=0.4,
            text_size=(None, None),
            halign='center'
        )
        
        # Label do valor
        lbl_valor = Label(
            text=str(valor),
            font_size='12sp',  # 🔥 REDUZIDO
            color=(1, 1, 1, 1),
            size_hint_y=0.6,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        card.add_widget(lbl_chave)
        card.add_widget(lbl_valor)
        
        return card
    
    def obter_status_cliente(self, dados_cliente):
        """Determina o status do cliente baseado nas contas"""
        sistema = App.get_running_app().sistema
        username = self.username_cliente
        
        if username not in sistema.usuarios:
            return "NÃO ENCONTRADO"
        
        contas = sistema.usuarios[username].get('contas', [])
        
        if not contas:
            return "SEM CONTAS"
        
        # Verificar se tem saldo em alguma conta
        tem_saldo = False
        for conta_num in contas:
            if conta_num in sistema.contas and sistema.contas[conta_num]['saldo'] > 0:
                tem_saldo = True
                break
        
        if tem_saldo:
            return "ATIVO COM SALDO"
        else:
            return "ATIVO SEM SALDO"
    
    def carregar_dados_cliente(self, username, dados_cliente):
        """Método principal para carregar todos os dados do cliente"""
        self.username_cliente = username
        self.dados_cliente = dados_cliente
        
        # Carregar dados pessoais
        self.carregar_dados_pessoais(username, dados_cliente)
        
        # Carregar contas do cliente
        contas = self.obter_contas_cliente(username)
        self.carregar_contas_cliente(contas)
    
    def obter_contas_cliente(self, username):
        """Obtém as contas de um cliente formatadas - MÉTODO TEMPORÁRIO"""
        print(f"DEBUG: obter_contas_cliente chamado para {username}")
        
        try:
            sistema = App.get_running_app().sistema
            contas = []
            
            if username not in sistema.usuarios:
                print(f"DEBUG: Usuário {username} não encontrado")
                return contas
            
            contas_usuario = sistema.usuarios[username].get('contas', [])
            print(f"DEBUG: Contas do usuário: {contas_usuario}")
            
            for conta_num in contas_usuario:
                if conta_num in sistema.contas:
                    dados_conta = sistema.contas[conta_num]
                    contas.append({
                        'numero': conta_num,
                        'moeda': dados_conta['moeda'],
                        'saldo': dados_conta['saldo'],
                        'data_criacao': dados_conta.get('data_criacao', 'N/A')
                    })
            
            print(f"DEBUG: {len(contas)} contas formatadas encontradas")
            return contas
            
        except Exception as e:
            print(f"ERRO em obter_contas_cliente: {e}")
            return []
    
    def obter_moedas_disponiveis(self):
        """Retorna as moedas que o cliente ainda não possui"""
        sistema = App.get_running_app().sistema
        contas_existentes = self.obter_contas_cliente(self.username_cliente)
        moedas_existentes = [conta['moeda'] for conta in contas_existentes]
        
        todas_moedas = ['USD', 'EUR', 'GBP', 'BRL', 'ARS', 'CLP', 'JPY', 'CAD', 'AUD', 'CHF']
        moedas_disponiveis = [moeda for moeda in todas_moedas if moeda not in moedas_existentes]
        
        return moedas_disponiveis
    
    def adicionar_conta(self):
        """Abre popup para adicionar nova conta"""
        moedas_disponiveis = self.obter_moedas_disponiveis()
        
        if not moedas_disponiveis:
            self.mostrar_erro("Este cliente já possui todas as moedas disponíveis!")
            return
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_titulo = Label(
            text='ADICIONAR NOVA CONTA',
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(400, None),
            halign='center'
        )
        
        # Campo para digitar a moeda
        box_moeda = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        lbl_moeda = Label(
            text='Digite a moeda (3 letras):',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.4,
            halign='left'
        )
        
        input_moeda = TextInput(
            text='USD',
            font_size='14sp',
            size_hint_y=0.6,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10],
            multiline=False
        )
        
        # Label informativa
        lbl_info = Label(
            text=f"Moedas disponíveis: {', '.join(moedas_disponiveis)}",
            font_size='10sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        
        box_moeda.add_widget(lbl_moeda)
        box_moeda.add_widget(input_moeda)
        
        # Botões
        box_botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_adicionar = Button(
            text='Adicionar Conta',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        box_botoes.add_widget(btn_cancelar)
        box_botoes.add_widget(btn_adicionar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(box_moeda)
        content.add_widget(lbl_info)
        content.add_widget(box_botoes)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 280),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def validar_e_adicionar(instance):
            moeda = input_moeda.text.strip().upper()
            
            # Validar moeda
            if len(moeda) != 3 or not moeda.isalpha():
                self.mostrar_erro("Moeda deve ter exatamente 3 letras!")
                return
            
            if moeda not in moedas_disponiveis:
                self.mostrar_erro(f"Moeda {moeda} não disponível ou já existe para este cliente!")
                return
            
            self._executar_adicionar_conta(moeda)
            popup.dismiss()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_adicionar.bind(on_press=validar_e_adicionar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()
    
    def _executar_adicionar_conta(self, moeda):
        """Executa a adição de nova conta"""
        sistema = App.get_running_app().sistema
        
        try:
            # Gerar número único para conta
            conta_numero = str(random.randint(100000000, 999999999))
            while conta_numero in sistema.contas:
                conta_numero = str(random.randint(100000000, 999999999))
            
            # Criar conta
            sistema.contas[conta_numero] = {
                'moeda': moeda,
                'saldo': 0.00,
                'cliente': self.username_cliente,
                'cliente_nome': sistema.usuarios[self.username_cliente]['nome'],
                'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Adicionar conta ao usuário
            if 'contas' not in sistema.usuarios[self.username_cliente]:
                sistema.usuarios[self.username_cliente]['contas'] = []
            sistema.usuarios[self.username_cliente]['contas'].append(conta_numero)
            
            # Salvar dados
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            
            self.mostrar_sucesso(
                f"✅ Conta adicionada com sucesso!\n\n"
                f"🏦 Nova conta: {conta_numero}\n"
                f"💰 Moeda: {moeda}\n"
                f"💵 Saldo inicial: 0.00"
            )
            
            # Recarregar contas
            self.carregar_contas_cliente(self.obter_contas_cliente(self.username_cliente))
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao adicionar conta: {str(e)}")
    
    def resetar_senha(self):
        """Reseta a senha do cliente"""
        self.mostrar_confirmacao(
            "Resetar Senha",
            f"Deseja resetar a senha do cliente {self.username_cliente}?\n\n"
            f"A nova senha será: cliente123\n"
            f"O cliente deverá alterar esta senha no primeiro acesso.",
            self._executar_reset_senha
        )
    
    def _executar_reset_senha(self):
        """Executa o reset da senha"""
        sistema = App.get_running_app().sistema
        
        try:
            # Resetar para senha padrão
            nova_senha = "cliente123"
            sistema.usuarios[self.username_cliente]['senha'] = sistema.hash_senha(nova_senha)
            sistema.salvar_usuarios()
            
            self.mostrar_sucesso(
                f"✅ Senha resetada com sucesso!\n\n"
                f"🔑 Nova senha: {nova_senha}\n\n"
                f"Informe ao cliente a nova senha."
            )
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao resetar senha: {str(e)}")
    
    def excluir_cliente(self):
        """Exclui completamente o cliente"""
        sistema = App.get_running_app().sistema
        contas = self.obter_contas_cliente(self.username_cliente)
        total_contas = len(contas)
        total_saldo = sum(conta['saldo'] for conta in contas)
        
        self.mostrar_confirmacao(
            "EXCLUIR CLIENTE COMPLETAMENTE",
            f"⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\n"
            f"👤 Cliente: {self.username_cliente}\n"
            f"📝 Nome: {self.dados_cliente['nome']}\n"
            f"🏦 Contas: {total_contas}\n"
            f"💰 Saldo total: {total_saldo:,.2f}\n\n"
            f"Serão excluídos:\n"
            f"• Todas as contas do cliente\n"
            f"• Todas as transferências relacionadas\n"
            f"• Todos os dados pessoais\n\n"
            f"Confirma a exclusão completa?",
            self._executar_exclusao_cliente
        )
    
    def _executar_exclusao_cliente(self):
        """Executa a exclusão completa do cliente"""
        sistema = App.get_running_app().sistema
        
        try:
            contas = self.obter_contas_cliente(self.username_cliente)
            
            # 1. Remover todas as contas do sistema
            for conta in contas:
                if conta['numero'] in sistema.contas:
                    del sistema.contas[conta['numero']]
            
            # 2. Remover usuário
            if self.username_cliente in sistema.usuarios:
                del sistema.usuarios[self.username_cliente]
            
            # 3. Remover transferências relacionadas ao cliente
            transferencias_para_remover = []
            for transacao_id, dados in sistema.transferencias.items():
                # Verificar se a transação envolve alguma conta do cliente
                conta_envolvida = (
                    dados.get('conta_remetente') in [conta['numero'] for conta in contas] or
                    dados.get('conta_destinatario') in [conta['numero'] for conta in contas] or
                    dados.get('cliente_afetado') == self.username_cliente or
                    dados.get('solicitado_por') == self.username_cliente
                )
                
                if conta_envolvida:
                    transferencias_para_remover.append(transacao_id)
            
            # Remover transferências
            for transacao_id in transferencias_para_remover:
                del sistema.transferencias[transacao_id]
            
            # 4. Remover beneficiários do cliente
            if self.username_cliente in sistema.beneficiarios:
                del sistema.beneficiarios[self.username_cliente]
            
            # 5. Salvar todos os dados
            sistema.salvar_usuarios()
            sistema.salvar_contas()
            sistema.salvar_transferencias()
            sistema.salvar_beneficiarios()
            
            self.mostrar_sucesso(
                f"✅ Cliente excluído completamente!\n\n"
                f"👤 Cliente: {self.username_cliente}\n"
                f"🏦 Contas removidas: {len(contas)}\n"
                f"📊 Transferências removidas: {len(transferencias_para_remover)}"
            )
            
            # Voltar para tela anterior
            self.voltar()
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao excluir cliente: {str(e)}")
    
    def voltar(self):
        """Volta para a tela de gerenciar contas"""
        self.manager.current = 'gerenciar_contas'
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
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
    
    def mostrar_confirmacao(self, titulo, mensagem, callback_confirmar):
        """Mostra popup de confirmação"""
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
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center'
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
            size=(450, 300),
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

class CardContaCliente(BoxLayout):
    """Card para exibir uma conta do cliente com ações"""
    
    def __init__(self, conta, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [15, 10, 15, 10]
        self.spacing = 10
        
        self.conta = conta
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
        
        self.criar_conteudo()
    
    def _atualizar_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def criar_conteudo(self):
        # Informações da conta
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        lbl_numero = Label(
            text=f"Conta: {self.conta['numero']}",
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left'
        )
        
        lbl_detalhes = Label(
            text=f"Moeda: {self.conta['moeda']} | Saldo: {self.conta['saldo']:,.2f}",
            font_size='10sp',
            color=(0.80, 0.84, 0.88, 1),
            halign='left'
        )
        
        info_layout.add_widget(lbl_numero)
        info_layout.add_widget(lbl_detalhes)
        
        # Botão remover
        btn_remover = Button(
            text='Remover',
            font_size='10sp',
            size_hint_x=0.3,
            background_color=(0.96, 0.36, 0.36, 1),
            color=(1, 1, 1, 1)
        )
        btn_remover.bind(on_press=self.remover_conta)
        
        self.add_widget(info_layout)
        self.add_widget(btn_remover)
    
    def remover_conta(self, instance):
        """Remove a conta do cliente"""
        if self.conta['saldo'] > 0:
            self.tela_pai.mostrar_confirmacao(
                "Conta com Saldo",
                f"A conta {self.conta['numero']} possui saldo: {self.conta['saldo']:,.2f}\n\n"
                f"Deseja realmente remover esta conta?\n"
                f"O saldo será perdido!",
                lambda: self._executar_remocao_conta()
            )
        else:
            self._executar_remocao_conta()
    
    def _executar_remocao_conta(self):
        """Executa a remoção da conta"""
        sistema = App.get_running_app().sistema
        
        try:
            # Remover conta do sistema
            if self.conta['numero'] in sistema.contas:
                del sistema.contas[self.conta['numero']]
            
            # Remover conta do usuário
            username = self.tela_pai.username_cliente
            if username in sistema.usuarios and 'contas' in sistema.usuarios[username]:
                sistema.usuarios[username]['contas'] = [
                    conta for conta in sistema.usuarios[username]['contas'] 
                    if conta != self.conta['numero']
                ]
            
            # Salvar dados
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            
            self.tela_pai.mostrar_sucesso(
                f"✅ Conta removida com sucesso!\n\n"
                f"🏦 Conta: {self.conta['numero']}\n"
                f"💰 Moeda: {self.conta['moeda']}"
            )
            
            # Recarregar contas
            self.tela_pai.carregar_contas_cliente(
                self.tela_pai.obter_contas_cliente(username)
            )
            
        except Exception as e:
            self.tela_pai.mostrar_erro(f"Erro ao remover conta: {str(e)}")
        """Executa a remoção da conta"""
        sistema = App.get_running_app().sistema
        
        try:
            # Remover conta do sistema
            if self.conta['numero'] in sistema.contas:
                del sistema.contas[self.conta['numero']]
            
            # Remover conta do usuário
            username = self.tela_pai.username_cliente
            if username in sistema.usuarios and 'contas' in sistema.usuarios[username]:
                sistema.usuarios[username]['contas'] = [
                    conta for conta in sistema.usuarios[username]['contas'] 
                    if conta != self.conta['numero']
                ]
            
            # Salvar dados
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            
            self.tela_pai.mostrar_sucesso(
                f"✅ Conta removida com sucesso!\n\n"
                f"🏦 Conta: {self.conta['numero']}\n"
                f"💰 Moeda: {self.conta['moeda']}\n"
                f"💵 Saldo perdido: {self.conta['saldo']:,.2f}"
            )
            
            # Recarregar contas
            contas = self.tela_pai.obter_contas_cliente(username)
            self.tela_pai.carregar_contas_cliente(contas)
            
        except Exception as e:
            self.tela_pai.mostrar_erro(f"Erro ao remover conta: {str(e)}")