from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ListProperty 
import datetime

class TelaAprovarOperacoes(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1200, 900)
        
        print("📋 Tela de aprovar operações carregada")
        
        # 🔥 AGENDAR POSICIONAMENTO
        from kivy.clock import Clock
        Clock.schedule_once(self._reposicionar_janela, 0.1)
        
        # 🔥 CARREGAR DADOS PRIMEIRO
        self.carregar_dados()
        
        # 🔥 AGENDAR SELEÇÃO DA ABA APÓS UM PEQUENO DELAY
        Clock.schedule_once(lambda dt: self.selecionar_aba_pendentes(), 0.3)
    
    def _reposicionar_janela(self, dt):
        """Reposiciona a janela após um pequeno delay"""
        from kivy.core.window import Window
        Window.left = 300
        Window.top = 70
        print("✅ Janela de aprovação reposicionada para esquerda")
        
    def carregar_dados(self):
        """Carrega os dados das transferências - 100% SUPABASE"""
        sistema = App.get_running_app().sistema
        
        # Verificar se é admin
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro_acesso()
            return
        
        try:
            self.transferencias_pendentes = {}
            self.transferencias_processing = {}
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível")
                self.atualizar_estatisticas()
                return
            
            print("📡 Buscando transferências pendentes no Supabase...")
            
            # 🔥 BUSCAR APENAS NO SUPABASE - status 'solicitada'
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('status', 'solicitada')\
                .execute()
            
            print(f"🔍 RESPOSTA SUPABASE: {len(response.data)} transferências")
            
            if response.data:
                for transf in response.data:
                    transf_id = transf['id']
                    # 🔥 MANTER OS CAMPOS ORIGINAIS DO SUPABASE
                    self.transferencias_pendentes[transf_id] = transf
                
                print(f"✅ {len(self.transferencias_pendentes)} transferências pendentes carregadas do Supabase")
            
            # 🔥🔥🔥 CORREÇÃO: BUSCAR TRANSFERÊNCIAS EM PROCESSAMENTO
            print("📡 Buscando transferências em PROCESSAMENTO no Supabase...")
            
            response_processing = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('status', 'processing')\
                .execute()
            
            print(f"🔍 RESPOSTA PROCESSING: {len(response_processing.data)} transferências")
            
            if response_processing.data:
                for transf in response_processing.data:
                    transf_id = transf['id']
                    self.transferencias_processing[transf_id] = transf
                
                print(f"✅ {len(self.transferencias_processing)} transferências em processamento carregadas do Supabase")
            
            # 🔥 DEBUG: Mostrar IDs das transferências carregadas
            if self.transferencias_pendentes:
                print("🔍 IDs das transferências pendentes carregadas:")
                for transf_id in self.transferencias_pendentes.keys():
                    print(f"   📋 {transf_id}")
            else:
                print("ℹ️ Nenhuma transferência pendente encontrada no Supabase")
            
            if self.transferencias_processing:
                print("🔍 IDs das transferências em processamento carregadas:")
                for transf_id in self.transferencias_processing.keys():
                    print(f"   🔄 {transf_id}")
            else:
                print("ℹ️ Nenhuma transferência em processamento encontrada no Supabase")
            
            # 🔥 CORREÇÃO CRÍTICA: ATUALIZAR AS DUAS TABELAS
            self.atualizar_tabela_pendentes()
            self.atualizar_tabela_processamento()  # 🔥 ATUALIZAR TABELA DE PROCESSAMENTO TAMBÉM
            
            # Atualizar estatísticas nos botões grandes
            self.atualizar_estatisticas()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados do Supabase: {e}")
            import traceback
            traceback.print_exc()
            self.transferencias_pendentes = {}
            self.transferencias_processing = {}
            self.atualizar_estatisticas()
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas nos botões grandes"""
        total_pendentes = len(self.transferencias_pendentes)
        total_processing = len(self.transferencias_processing)
        
        if hasattr(self, 'ids'):
            if 'btn_aprovar_pendentes' in self.ids:
                self.ids.btn_aprovar_pendentes.text = f"APROVAR PENDENTES\n\n{total_pendentes} operações"
            
            if 'btn_concluir_processamento' in self.ids:
                self.ids.btn_concluir_processamento.text = f"CONCLUIR PROCESSAMENTO\n\n{total_processing} operações"
    
    def mostrar_erro_acesso(self):
        """Mostra popup de erro de acesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_erro = Label(
            text="❌ ACESSO RESTRITO\n\nEsta função é apenas para administradores!",
            color=(1, 0.3, 0.3, 1),
            font_size='16sp',
            bold=True,
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='VOLTAR',
            size_hint_y=None,
            height=45,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Acesso Restrito',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def voltar_dashboard(instance):
            popup.dismiss()
            self.manager.current = 'dashboard'
        
        btn_ok.bind(on_press=voltar_dashboard)
        popup.open()
    
    def selecionar_aba_pendentes(self):
        """Seleciona a aba de pendentes e atualiza cores dos botões"""
        if hasattr(self, 'ids') and 'abas' in self.ids:
            self.ids.abas.switch_to(self.ids.aba_pendentes)
            self.atualizar_cores_botoes_por_aba('pendentes')

    def selecionar_aba_processamento(self):
        """Seleciona a aba de processamento e atualiza cores dos botões"""
        if hasattr(self, 'ids') and 'abas' in self.ids:
            self.ids.abas.switch_to(self.ids.aba_processamento)
            self.atualizar_cores_botoes_por_aba('processamento')

    def atualizar_cores_botoes_por_aba(self, aba_atual):
        """Atualiza as cores dos botões baseado na aba selecionada"""
        if not hasattr(self, 'ids'):
            return
        
        # 🔥 CORES PARA BOTÃO ATIVO (aba atual)
        cor_ativa_pendentes = (1.0, 0.65, 0.0, 1)  # ÂMBAR
        cor_ativa_processamento = (0.3, 0.7, 1.0, 1)  # AZUL CLARO
        
        # 🔥 COR PARA BOTÃO INATIVO (aba não selecionada)
        cor_inativa = (0.5, 0.5, 0.5, 1)  # CINZA
        
        if aba_atual == 'pendentes':
            # Aba PENDENTES ativa
            if 'btn_aprovar_pendentes' in self.ids:
                self.ids.btn_aprovar_pendentes.background_color = cor_ativa_pendentes
                self.ids.btn_aprovar_pendentes.color = (0, 0, 0, 1)  # Texto preto
            if 'btn_concluir_processamento' in self.ids:
                self.ids.btn_concluir_processamento.background_color = cor_inativa
                self.ids.btn_concluir_processamento.color = (0.8, 0.8, 0.8, 1)  # Texto cinza claro
                
        elif aba_atual == 'processamento':
            # Aba PROCESSAMENTO ativa
            if 'btn_aprovar_pendentes' in self.ids:
                self.ids.btn_aprovar_pendentes.background_color = cor_inativa
                self.ids.btn_aprovar_pendentes.color = (0.8, 0.8, 0.8, 1)  # Texto cinza claro
            if 'btn_concluir_processamento' in self.ids:
                self.ids.btn_concluir_processamento.background_color = cor_ativa_processamento
                self.ids.btn_concluir_processamento.color = (1, 1, 1, 1)  # Texto branco
    
    def aprovar_transferencia(self, transferencia_id):
        """Aprova uma transferência pendente - VERSÃO CORRIGIDA COM PADRÃO SUPABASEMANAGER"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 CORREÇÃO: Usar SupabaseManager em vez de chamada direta
            transferencia = sistema.supabase.obter_transferencia(transferencia_id)
            
            if not transferencia:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return False
            
            # 🔥 VALIDAÇÃO DA INVOICE - Só aprovar se invoice estiver aprovada
            info_invoice = sistema.obter_info_invoice(transferencia_id)
            
            if info_invoice:
                # Tem invoice - verificar status
                if info_invoice['status'] != 'approved':
                    if info_invoice['status'] == 'pending':
                        self.mostrar_erro("❌ IMPOSSÍVEL APROVAR TRANSFERÊNCIA\n\nA invoice desta transferência ainda está PENDENTE de aprovação!\n\nPor favor, analise e aprove a invoice primeiro.")
                    elif info_invoice['status'] == 'rejected':
                        self.mostrar_erro("❌ IMPOSSÍVEL APROVAR TRANSFERÊNCIA\n\nA invoice desta transferência foi RECUSADA!\n\nO cliente precisa enviar uma nova invoice aprovada.")
                    else:
                        self.mostrar_erro("❌ IMPOSSÍVEL APROVAR TRANSFERÊNCIA\n\nStatus da invoice inválido!")
                    return False
            else:
                # Não tem invoice - verificar se é obrigatório
                if transferencia.get('tipo') == 'transferencia_internacional':
                    self.mostrar_erro("❌ IMPOSSÍVEL APROVAR TRANSFERÊNCIA\n\nTransferências INTERNACIONAIS exigem invoice aprovada!\n\nEsta transferência não possui invoice anexada.")
                    return False
                # Para transferências internas, invoice não é obrigatório
                print("⚠️  Transferência interna sem invoice - permitindo aprovação")
            
            # 🔥 CORREÇÃO: Atualizar status usando SupabaseManager
            data_aprovacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                'status': 'processing',
                'executado_por': sistema.usuario_logado,
                'data_aprovacao': data_aprovacao,
                'data_processing': data_aprovacao
                # 🔥🔥🔥 CORREÇÃO CRÍTICA: NÃO ATUALIZAR 'data' PRINCIPAL!
            }
            
            # 🔍 DEBUG: VER O QUE ESTÁ SENDO ENVIADO
            print(f"🔍 DEBUG APROVAÇÃO - Dados sendo enviados: {update_data}")
            
            # 🔥 CORREÇÃO: Usar método do SupabaseManager
            sucesso = sistema.supabase.atualizar_status_transferencia(transferencia_id, update_data)
            
            if sucesso:
                print(f"✅✅✅ Transferência {transferencia_id} aprovada no Supabase!")
                
                
                # 🔥 CORREÇÃO: Atualizar também localmente para sincronização
                if transferencia_id in sistema.transferencias:
                    # 🔍 DEBUG: VER SINCRONIZAÇÃO LOCAL
                    print(f"🔍 DEBUG SINCRONIZAÇÃO - ANTES:")
                    print(f"   Data local ANTES: {sistema.transferencias[transferencia_id].get('data')}")
                    print(f"   Status local ANTES: {sistema.transferencias[transferencia_id].get('status')}")
                    
                    sistema.transferencias[transferencia_id].update(update_data)
                    
                    print(f"🔍 DEBUG SINCRONIZAÇÃO - DEPOIS:")
                    print(f"   Data local DEPOIS: {sistema.transferencias[transferencia_id].get('data')}")
                    print(f"   Status local DEPOIS: {sistema.transferencias[transferencia_id].get('status')}")
                    
                sistema.salvar_transferencias()
                
                # 🔥 MOSTRAR MENSAGEM DE SUCESSO
                self.mostrar_sucesso(f"Transferência {transferencia_id} aprovada com sucesso!\n\nStatus alterado para: PROCESSANDO")
                
                # 🔥 ATUALIZAR A LISTA NA TELA
                self.carregar_dados()
                
                return True
            else:
                print(f"❌❌❌ Erro ao aprovar transferência no Supabase")
                self.mostrar_erro("Erro ao aprovar transferência no sistema!")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao aprovar transferência: {e}")
            self.mostrar_erro(f"Erro ao aprovar: {str(e)}")
            return False

    def transferencia_exige_invoice(self, transferencia_id):
        """Verifica se uma transferência exige invoice obrigatória"""
        sistema = App.get_running_app().sistema
        dados = sistema.transferencias[transferencia_id]
        
        # Transferências internacionais sempre exigem invoice
        if dados.get('tipo') == 'internacional':
            return True
        
        # Transferências acima de determinado valor podem exigir invoice
        # (adicione suas regras de negócio aqui)
        valor_limite = 10  # Exemplo: acima de 10.000 exige invoice
        if dados['valor'] > valor_limite:
            return True
            
        return False

    def recusar_transferencia(self, transferencia_id, motivo):
        """Recusa uma transferência pendente - VERSÃO CORRIGIDA COM PADRÃO"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 CORREÇÃO: Usar SupabaseManager
            transferencia = sistema.supabase.obter_transferencia(transferencia_id)
            
            if not transferencia:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return False
            
            # ✅ PRESERVAR DATA ORIGINAL
            data_original = transferencia.get('data')
            
            # 🔥 CORREÇÃO: Estornar valor usando SupabaseManager
            conta_origem = None
            valor_estorno = 0
            
            if transferencia.get('tipo') == 'transferencia_internacional':
                conta_origem = transferencia['conta_remetente']
                valor_estorno = transferencia['valor']
                
                # 🔥 CORREÇÃO: Usar métodos do SupabaseManager
                saldo_atual = sistema.supabase.obter_saldo_conta(conta_origem)
                novo_saldo = saldo_atual + valor_estorno
                
                sucesso_estorno = sistema.supabase.atualizar_saldo_conta(conta_origem, novo_saldo)
                
                if sucesso_estorno:
                    print(f"💰 Estornado {valor_estorno} para conta {conta_origem} no Supabase")
            
            # 🔥 CORREÇÃO: Atualizar status usando SupabaseManager
            data_recusa = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                'status': 'rejected',
                'executado_por': sistema.usuario_logado,
                'data_recusa': data_recusa,
                'motivo_recusa': motivo
                # 🔥 NÃO ATUALIZAR 'data' PRINCIPAL - PRESERVAR ORDEM CRONOLÓGICA
            }
            
            # 🔍 DEBUG: VER O QUE ESTÁ SENDO ENVIADO
            print(f"🔍 DEBUG RECUSA - Dados sendo enviados: {update_data}")
            
            sucesso = sistema.supabase.atualizar_status_transferencia(transferencia_id, update_data)
            
            if sucesso:
                print(f"✅ Transferência {transferencia_id} recusada no Supabase!")
                
                # 🔥 SINCRONIZAR LOCALMENTE
                if transferencia_id in sistema.transferencias:
                    sistema.transferencias[transferencia_id].update(update_data)
                sistema.salvar_transferencias()
                
                # ✅ CORREÇÃO CRÍTICA: ATUALIZAR MEMÓRIA LOCAL
                if conta_origem and conta_origem in sistema.contas:
                    sistema.contas[conta_origem]['saldo'] += valor_estorno
                    print(f"✅ Saldo em memória atualizado: {conta_origem} = {sistema.contas[conta_origem]['saldo']}")
                    
                    # ✅ FORÇAR DASHBOARD A RECARREGAR
                    dashboard = self.manager.get_screen('dashboard')
                    if hasattr(dashboard, 'carregar_dados'):
                        dashboard.carregar_dados()
                        print("✅ Dashboard atualizado após estorno!")
                
                return True
            else:
                print(f"❌ Erro ao recusar transferência no Supabase")
                self.mostrar_erro("Erro ao recusar transferência no sistema!")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao recusar transferência: {e}")
            self.mostrar_erro(f"Erro ao recusar: {str(e)}")
            return False
    
    def concluir_processamento(self, transferencia_id):
        """Abre modal para selecionar conta bancária antes de concluir - VERSÃO SUPABASE"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 CORREÇÃO: Buscar dados do Supabase
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return False
            
            dados = response.data[0]
            
            # 🔥 VERIFICAR SE É TRANSFERÊNCIA INTERNACIONAL
            if dados.get('tipo') != 'transferencia_internacional':
                # Para transferências internas, usar modal com seleção de conta bancária
                self.mostrar_modal_conta_bancaria(transferencia_id)
                return True
            else:
                # Para internacionais, abrir modal SWIFT COM seleção de conta bancária
                self.mostrar_modal_swift_com_conta_bancaria(transferencia_id)
                return True
                
        except Exception as e:
            print(f"❌ Erro ao concluir transferência: {e}")
            self.mostrar_erro(f"Erro ao concluir: {str(e)}")
            return False

    def _concluir_sem_swift(self, transferencia_id):
        """Conclui transferência sem dados SWIFT (internas) - VERSÃO SUPABASE"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 CORREÇÃO: Atualizar no Supabase
            update_data = {
                'status': 'completed',
                'data_conclusao': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'concluido_por': sistema.usuario_logado
            }
            
            response = sistema.supabase.client.table('transferencias')\
                .update(update_data)\
                .eq('id', transferencia_id)\
                .execute()
            
            if response.data:
                print(f"✅ Transferência {transferencia_id} concluída no Supabase!")
                
                # 🔥 CORREÇÃO: Sincronizar dados locais
                if transferencia_id in sistema.transferencias:
                    sistema.transferencias[transferencia_id].update(update_data)
                sistema.salvar_transferencias()
                
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída!")
                self.carregar_dados()
                return True
            else:
                print(f"❌ Erro ao concluir transferência no Supabase: {response.error}")
                self.mostrar_erro("Erro ao concluir transferência no sistema!")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao concluir transferência: {e}")
            self.mostrar_erro(f"Erro ao concluir: {str(e)}")
            return False

    def mostrar_modal_swift(self, transferencia_id):
        """Modal para inserir dados SWIFT no formato específico"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from kivy.uix.gridlayout import GridLayout
        
        sistema = App.get_running_app().sistema
        dados = sistema.transferencias[transferencia_id]
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.size_hint_y = None
        content.height = 800  # 🔥 AUMENTEI A ALTURA
        
        # Título
        lbl_titulo = Label(
            text="DADOS SWIFT DO PAGAMENTO",
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=40
        )
        
        # Informações da transferência
        info_text = f"ID: {transferencia_id}\nCliente: {self.obter_nome_cliente(dados['conta_remetente'])}\nValor: {dados['valor']:,.2f} {dados['moeda']}"
        
        lbl_info = Label(
            text=info_text,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=60
        )
        
        # Grid para campos SWIFT específicos
        grid_campos = GridLayout(
            cols=1,
            spacing=8,
            padding=[0, 10, 0, 10],
            size_hint_y=None,
            height=550  # 🔥 AUMENTEI A ALTURA DO GRID
        )
        grid_campos.bind(minimum_height=grid_campos.setter('height'))

        # Campos SWIFT específicos - 🔥 COM "Benef." ABREVIADO        
        campos_swift = [
            ("LINHA 1: UETR#", ""),
            ("LINHA 2: :20:", ""),
            ("LINHA 3: :32A:", ""),
            ("LINHA 4: :50K:", ""),
            ("LINHA 5: :57A:", ""),
            ("LINHA 6: :59:", ""),
            ("LINHA 7: Benef.", ""),  # 🔥 "Benef." ABREVIADO
            ("LINHA 8: :70:", ""),
            ("LINHA 9: :71A:", "")
        ]
        
        self.campos_swift = {}
        
        for label, valor_padrao in campos_swift:
            # Container para cada linha
            linha_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=45,  # 🔥 AUMENTEI A ALTURA DAS LINHAS
                spacing=10
            )
            
            # Label
            lbl = Label(
                text=label,
                font_size='11sp',
                bold=True,
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.3,
                text_size=(None, None),
                halign='left'
            )
            linha_layout.add_widget(lbl)
            
            # Campo de entrada - 🔥 AGORA EM BRANCO
            campo = TextInput(
                text=valor_padrao,  # 🔥 VAZIO
                hint_text=f'Digite {label}...',
                size_hint_x=0.7,
                multiline=False,
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
                padding=[10, 10],  # 🔥 MAIS PADDING
                font_size='11sp'
            )
            
            self.campos_swift[label] = campo
            linha_layout.add_widget(campo)
            grid_campos.add_widget(linha_layout)
        
        # Botões
        botoes_layout = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=50, 
            spacing=10
        )
        
        btn_confirmar = Button(
            text='CONCLUIR COM DADOS SWIFT',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        # Adicionar tudo ao content
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_info)
        content.add_widget(grid_campos)
        content.add_widget(botoes_layout)
        
        # Criar popup
        popup = Popup(
            title='Dados SWIFT - Concluir Processamento',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(700, 850),  # 🔥 AUMENTEI A ALTURA DO POPUP
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            # Validar campos obrigatórios
            campos_obrigatorios = [
                "LINHA 1: UETR#",
                "LINHA 2: :20:", 
                "LINHA 3: :32A:",
                "LINHA 4: :50K:",
                "LINHA 5: :57A:",
                "LINHA 6: :59:"
            ]
            
            for campo in campos_obrigatorios:
                if campo in self.campos_swift and not self.campos_swift[campo].text.strip():
                    self.mostrar_erro(f"Campo '{campo}' é obrigatório!")
                    return
            
            # Coletar dados SWIFT no formato específico - 🔥 COM "Benef." ABREVIADO
            dados_swift = {
                'linha1_uetr': self.campos_swift["LINHA 1: UETR#"].text.strip(),
                'linha2_20': self.campos_swift["LINHA 2: :20:"].text.strip(),
                'linha3_32a': self.campos_swift["LINHA 3: :32A:"].text.strip(),
                'linha4_50k': self.campos_swift["LINHA 4: :50K:"].text.strip(),
                'linha5_57a': self.campos_swift["LINHA 5: :57A:"].text.strip(),
                'linha6_59': self.campos_swift["LINHA 6: :59:"].text.strip(),
                'linha7_beneficiario': self.campos_swift["LINHA 7: Benef."].text.strip(),  # 🔥 "Benef." ABREVIADO
                'linha8_70': self.campos_swift["LINHA 8: :70:"].text.strip(),
                'linha9_71a': self.campos_swift["LINHA 9: :71A:"].text.strip()
            }
            
            # Concluir com dados SWIFT
            if self._concluir_com_swift(transferencia_id, dados_swift):
                popup.dismiss()
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída com dados SWIFT!")
                self.carregar_dados()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    def _concluir_com_swift(self, transferencia_id, dados_swift):
        """Conclui transferência internacional com dados SWIFT - VERSÃO CORRIGIDA COM PADRÃO"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 CORREÇÃO: Atualizar usando SupabaseManager
            data_conclusao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            update_data = {
                'status': 'completed',
                'data_conclusao': data_conclusao,
                'concluido_por': sistema.usuario_logado,
                'dados_swift_pagamento': dados_swift
                # 🔥 NÃO ATUALIZAR 'data' PRINCIPAL!
            }
            
            # 🔍 DEBUG: VER O QUE ESTÁ SENDO ENVIADO
            print(f"🔍 DEBUG CONCLUSÃO - Dados sendo enviados: {update_data}")
            
            # 🔥 CORREÇÃO: Usar método do SupabaseManager
            sucesso = sistema.supabase.atualizar_status_transferencia(transferencia_id, update_data)
            
            if sucesso:
                print(f"✅✅✅ Transferência {transferencia_id} concluída no Supabase com SWIFT!")
                
                # 🔥 SINCRONIZAR LOCALMENTE
                sistema.transferencias[transferencia_id].update(update_data)
                sistema.salvar_transferencias()
                
                # 🔥 MOSTRAR SUCESSO
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída com sucesso!\n\nDados SWIFT registrados.")
                
                # 🔥 ATUALIZAR A LISTA
                self.carregar_dados()
                
                print(f"Dados SWIFT: {dados_swift}")
                return True
            else:
                print(f"❌❌❌ Erro ao concluir transferência no Supabase")
                self.mostrar_erro("Erro ao concluir transferência no sistema!")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao concluir transferência com SWIFT: {e}")
            self.mostrar_erro(f"Erro ao concluir: {str(e)}")
            return False
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro genérico"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
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
            height=45,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
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
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        print("↩Voltando ao dashboard")
        self.manager.current = 'dashboard'
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas nos botões e labels"""
        total_pendentes = len(self.transferencias_pendentes)
        total_processing = len(self.transferencias_processing)
        
        total_valor_pendentes = sum(t['valor'] for t in self.transferencias_pendentes.values())
        total_valor_processing = sum(t['valor'] for t in self.transferencias_processing.values())
        
        if hasattr(self, 'ids'):
            # 🔥 ATUALIZAR APENAS OS TEXTOS, AS CORES SERÃO CONTROLADAS POR atualizar_cores_botoes_por_aba
            if 'btn_aprovar_pendentes' in self.ids:
                self.ids.btn_aprovar_pendentes.text = f"APROVAR PENDENTES\n\n{total_pendentes} operações"
                # ❌ NÃO definir background_color aqui
            
            if 'btn_concluir_processamento' in self.ids:
                self.ids.btn_concluir_processamento.text = f"CONCLUIR PROCESSAMENTO\n\n{total_processing} operações"
                # ❌ NÃO definir background_color aqui
            
            # Labels de estatísticas mantêm suas cores
            if 'stats_pendentes' in self.ids:
                self.ids.stats_pendentes.text = f"{total_pendentes} Operações Pendentes • Valor Total: {total_valor_pendentes:,.2f}"
                self.ids.stats_pendentes.color = (1.0, 0.65, 0.0, 1)  # ✅ MANTER cor do label
            
            if 'stats_processamento' in self.ids:
                self.ids.stats_processamento.text = f"{total_processing} Transferências em Processamento • Valor Total: {total_valor_processing:,.2f}"
                self.ids.stats_processamento.color = (0.3, 0.7, 1.0, 1)  # ✅ MANTER cor do label

    def atualizar_tabela_pendentes(self):
        """Atualiza a tabela de transferências pendentes - VERSÃO SUPABASE"""
        if not hasattr(self, 'ids') or 'grid_pendentes' not in self.ids:
            return
        
        sistema = App.get_running_app().sistema
        grid = self.ids.grid_pendentes
        grid.clear_widgets()
        grid.bind(minimum_height=grid.setter('height'))
        
        if not hasattr(self, 'transferencias_pendentes') or not self.transferencias_pendentes:
            print("ℹ️ Nenhuma transferência pendente para exibir")
            sem_dados = Label(
                text="Nenhuma transferência pendente",
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=50
            )
            grid.add_widget(sem_dados)
            return
        
        print(f"🎯 Atualizando tabela com {len(self.transferencias_pendentes)} transferências")
        
        for transferencia_id, dados in self.transferencias_pendentes.items():
            try:
                # 🔥 USAR CAMPOS DO SUPABASE
                info_invoice = sistema.obter_info_invoice(transferencia_id)
                tem_invoice = info_invoice is not None and isinstance(info_invoice, dict)
                status_invoice = info_invoice.get('status', 'no_invoice') if tem_invoice else 'no_invoice'
                
                # Status da invoice
                if status_invoice == 'pending':
                    texto_invoice = "Invoice: Pendente"
                    cor_invoice = "FFA500"
                elif status_invoice == 'approved':
                    texto_invoice = "Invoice: Aprovada" 
                    cor_invoice = "32CD32"
                elif status_invoice == 'rejected':
                    texto_invoice = "Invoice: Recusada"
                    cor_invoice = "FF4500"
                else:
                    texto_invoice = "Sem Invoice"
                    cor_invoice = "B0B0B0"
                
                # 🔥 CAMPOS DO SUPABASE
                conta_remetente = dados.get('conta_remetente', 'N/A')
                cliente_nome = self.obter_nome_cliente(conta_remetente)
                
                # Tipo e beneficiário
                if dados.get('tipo') == 'transferencia_internacional':
                    tipo = "INTERNACIONAL"
                    beneficiario = dados.get('beneficiario', 'N/A')
                else:
                    tipo = "INTERNA" 
                    beneficiario = cliente_nome
                
                # Limitar beneficiário
                if len(beneficiario) > 25:
                    beneficiario = beneficiario[:22] + "..."
                
                # 🔥 DATA DO SUPABASE
                data_raw = dados.get('data') or dados.get('created_at', '')
                if data_raw and 'T' in data_raw:
                    data_simples = data_raw.split('T')[0]
                else:
                    data_simples = data_raw.split(' ')[0] if data_raw else 'Data N/A'
                
                # Valor
                valor = dados.get('valor', 0)
                moeda = dados.get('moeda', 'USD')
                valor_formatado = f"{float(valor):,.2f} {moeda}"
                
                # Criar botão
                item = Button(
                    size_hint_y=None,
                    height=110,
                    background_color=(0.20, 0.25, 0.33, 1),
                    background_normal='',
                    color=(0.9, 0.9, 0.9, 1),
                    font_size='12sp',
                    halign='left',
                    valign='top',
                    padding=[10, 5]
                )
                
                # Texto com markup
                texto_completo = f"ID: {transferencia_id} | {tipo}\n"
                texto_completo += f"[b][color={cor_invoice}]{texto_invoice}[/color][/b]\n"
                texto_completo += f"Cliente: {cliente_nome}\n"
                texto_completo += f"Beneficiário: {beneficiario}\n"
                texto_completo += f"Valor: {valor_formatado} | Data: {data_simples}"
                
                item.text = texto_completo
                item.markup = True
                item.transferencia_id = transferencia_id
                item.dados = dados
                item.bind(on_press=self.selecionar_item_pendentes)
                
                grid.add_widget(item)
                
            except Exception as e:
                print(f"❌ Erro ao processar transferência {transferencia_id}: {e}")
                continue

    def selecionar_item_pendentes(self, instance):
        """Seleciona um item na tabela de pendentes - VERSÃO CORRIGIDA"""
        try:
            self.item_selecionado_pendentes = instance
            self.transferencia_selecionada_id = instance.transferencia_id
            self.dados_selecionados = instance.dados
            
            # 🔥 DESTACAR ITEM SELECIONADO
            for child in self.ids.grid_pendentes.children:
                if hasattr(child, 'background_color'):
                    child.background_color = (0.20, 0.25, 0.33, 1)  # Cor normal
            
            instance.background_color = (0.23, 0.51, 0.96, 0.8)  # 🔥 AZUL MAIS FORTE
            
            print(f"✅ Item selecionado: {instance.transferencia_id}")
            
        except Exception as e:
            print(f"❌ Erro ao selecionar item: {e}")

    def atualizar_tabela_processamento(self):
        """Atualiza a tabela de transferências em processamento - VERSÃO SUPABASE"""
        if not hasattr(self, 'ids') or 'grid_processamento' not in self.ids:
            return
        
        sistema = App.get_running_app().sistema
        grid = self.ids.grid_processamento
        grid.clear_widgets()
        grid.bind(minimum_height=grid.setter('height'))
        
        if not hasattr(self, 'transferencias_processing') or not self.transferencias_processing:
            print("ℹ️ Nenhuma transferência em processamento")
            sem_dados = Label(
                text="Nenhuma transferência em processamento",
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=50
            )
            grid.add_widget(sem_dados)
            return
        
        print(f"🔄 Atualizando tabela processamento com {len(self.transferencias_processing)} transferências")
        
        for transferencia_id, dados in self.transferencias_processing.items():
            try:
                # 🔥 CAMPOS DO SUPABASE
                conta_remetente = dados.get('conta_remetente', 'N/A')
                cliente_nome = self.obter_nome_cliente(conta_remetente)
                
                # 🔥 TIPO CORRETO DO SUPABASE
                if dados.get('tipo') == 'transferencia_internacional':
                    beneficiario = dados.get('beneficiario', 'N/A')
                    tipo_display = "INTERNACIONAL"
                else:
                    conta_destino = dados.get('conta_destinatario', 'N/A')
                    beneficiario = self.obter_nome_cliente(conta_destino)
                    tipo_display = "INTERNA"
                
                # 🔥 DATA DO SUPABASE (pode vir como 'data' ou 'created_at')
                data_raw = dados.get('data_aprovacao') or dados.get('data') or dados.get('created_at', '')
                if data_raw and 'T' in data_raw:
                    data_simples = data_raw.split('T')[0]
                elif data_raw and ' ' in data_raw:
                    data_simples = data_raw.split(' ')[0]
                else:
                    data_simples = data_raw if data_raw else 'Data N/A'
                
                # Valor
                valor = dados.get('valor', 0)
                moeda = dados.get('moeda', 'USD')
                valor_formatado = f"{float(valor):,.2f} {moeda}"
                
                # Criar botão
                item = Button(
                    size_hint_y=None,
                    height=100,
                    background_color=(0.20, 0.25, 0.33, 1),
                    background_normal='',
                    color=(0.9, 0.9, 0.9, 1),
                    font_size='12sp',
                    halign='left',
                    valign='top',
                    padding=[10, 5]
                )
                
                item.text = f"ID: {transferencia_id} | {tipo_display}\nCliente: {cliente_nome}\nBeneficiário: {beneficiario}\nValor: {valor_formatado} | Data: {data_simples}"
                item.transferencia_id = transferencia_id
                item.dados = dados
                item.bind(on_press=self.selecionar_item_processamento)
                
                grid.add_widget(item)
                
            except Exception as e:
                print(f"❌ Erro ao processar transferência {transferencia_id}: {e}")
                continue
    
    def obter_nome_cliente(self, conta_numero):
        """Obtém o nome do cliente a partir do número da conta - VERSÃO SUPABASE"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 PRIMEIRO: Buscar no Supabase
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                response = sistema.supabase.client.table('contas')\
                    .select('cliente_nome, cliente_username')\
                    .eq('id', conta_numero)\
                    .execute()
                
                if response.data and len(response.data) > 0:
                    nome = response.data[0].get('cliente_nome') or response.data[0].get('cliente_username', 'Cliente')
                    print(f"✅ Nome do cliente encontrado no Supabase: {nome}")
                    return nome
            
            # 🔥 FALLBACK: Buscar localmente (durante transição)
            if conta_numero in sistema.contas:
                return sistema.contas[conta_numero].get('cliente_nome', 'Cliente')
            
            return 'Cliente não encontrado'
            
        except Exception as e:
            print(f"❌ Erro ao buscar nome do cliente: {e}")
            # Fallback
            if conta_numero in sistema.contas:
                return sistema.contas[conta_numero].get('cliente_nome', 'Cliente')
            return 'Cliente'

    def selecionar_item_processamento(self, instance):
        """Seleciona um item na tabela de processamento"""
        self.item_selecionado_processamento = instance
        self.transferencia_selecionada_id = instance.transferencia_id
        self.dados_selecionados = instance.dados
        
        # 🔥 MELHOR CONTRASTE - Cor mais destacada
        for child in self.ids.grid_processamento.children:
            child.background_color = (0.20, 0.25, 0.33, 1)  # Cor normal
        
        instance.background_color = (0.23, 0.51, 0.96, 0.8)  # 🔥 AZUL MAIS FORTE  
        instance.color = (1, 1, 1, 1)  # 🔥 TEXTO BRANCO quando selecionado
    
    def aprovar_selecionado(self):
        """Aprova a transferência selecionada"""
        if not hasattr(self, 'transferencia_selecionada_id'):
            self.mostrar_erro("Selecione uma transferência para aprovar!")
            return
        
        sistema = App.get_running_app().sistema
        transferencia_id = self.transferencia_selecionada_id
        
        # Confirmação
        self.mostrar_confirmacao_aprovacao(transferencia_id)
    
    def recusar_selecionado(self):
        """Recusa a transferência selecionada"""
        if not hasattr(self, 'transferencia_selecionada_id'):
            self.mostrar_erro("Selecione uma transferência para recusar!")
            return
        
        self.mostrar_popup_motivo_recusa()
    
    def concluir_selecionado(self):
        """Conclui o processamento da transferência selecionada - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'transferencia_selecionada_id'):
            self.mostrar_erro("Selecione uma transferência para concluir!")
            return
        
        sistema = App.get_running_app().sistema
        transferencia_id = self.transferencia_selecionada_id
        
        # 🔥 CHAMAR DIRETAMENTE O MÉTODO PRINCIPAL
        self.concluir_processamento(transferencia_id)
    
    def ver_detalhes(self):
        """Mostra detalhes da transferência selecionada"""
        if not hasattr(self, 'transferencia_selecionada_id'):
            self.mostrar_erro("Selecione uma transferência para ver detalhes!")
            return
        
        self.mostrar_popup_detalhes()

    def mostrar_modal_conta_bancaria(self, transferencia_id):
        """Modal para selecionar conta bancária antes de concluir transferência"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner
        
        sistema = App.get_running_app().sistema
        dados = sistema.transferencias[transferencia_id]
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        lbl_titulo = Label(
            text="SELECIONE CONTA BANCÁRIA",
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=40
        )
        
        # Informações da transferência
        cliente_nome = self.obter_nome_cliente(dados['conta_remetente'])
        info_text = f"ID: {transferencia_id}\nCliente: {cliente_nome}\nValor: {dados['valor']:,.2f} {dados['moeda']}"
        
        lbl_info = Label(
            text=info_text,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=60
        )
        
        # Seleção de conta bancária
        lbl_conta = Label(
            text="Conta Bancária para Crédito:",
            font_size='14sp',
            bold=True,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=30
        )
        
        # 🔥 CARREGAR CONTAS BANCÁRIAS DA EMPRESA
        opcoes_contas = []
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            if conta_info['moeda'] == dados['moeda']:  # 🔥 APENAS CONTAS NA MESMA MOEDA
                opcoes_contas.append(f"{conta_num} - {conta_info['banco']} - Saldo: {conta_info['saldo']:,.2f}")
        
        if not opcoes_contas:
            self.mostrar_erro(f"Nenhuma conta bancária encontrada em {dados['moeda']}!")
            return
        
        self.spinner_conta_bancaria = Spinner(
            text=opcoes_contas[0],
            values=opcoes_contas,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_confirmar = Button(
            text='CONCLUIR TRANSFERÊNCIA',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_info)
        content.add_widget(lbl_conta)
        content.add_widget(self.spinner_conta_bancaria)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Concluir Transferência',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(500, 350),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            conta_selecionada = self.spinner_conta_bancaria.text
            conta_numero = conta_selecionada.split(' - ')[0].strip()
            
            if self._concluir_com_credito_bancario(transferencia_id, conta_numero):
                popup.dismiss()
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída!\nValor creditado na conta {conta_numero}")
                self.carregar_dados()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    def mostrar_modal_swift_com_conta_bancaria(self, transferencia_id):
        """Modal SWIFT com seleção de conta bancária para transferências internacionais"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.spinner import Spinner
        
        sistema = App.get_running_app().sistema
        dados = sistema.transferencias[transferencia_id]
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.size_hint_y = None
        content.height = 900  # 🔥 AUMENTEI A ALTURA PARA CABER A CONTA BANCÁRIA
        
        # Título
        lbl_titulo = Label(
            text="DADOS SWIFT DO PAGAMENTO",
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=40
        )
        
        # Informações da transferência
        info_text = f"ID: {transferencia_id}\nCliente: {self.obter_nome_cliente(dados['conta_remetente'])}\nValor: {dados['valor']:,.2f} {dados['moeda']}"
        
        lbl_info = Label(
            text=info_text,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center',
            size_hint_y=None,
            height=60
        )
        
        # 🔥 SELEÇÃO DE CONTA BANCÁRIA (NOVO)
        lbl_conta = Label(
            text="Conta Bancária para Crédito:",
            font_size='14sp',
            bold=True,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=30
        )
        
        # 🔥 CARREGAR CONTAS BANCÁRIAS DA EMPRESA
        opcoes_contas = []
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            if conta_info['moeda'] == dados['moeda']:  # 🔥 APENAS CONTAS NA MESMA MOEDA
                opcoes_contas.append(f"{conta_num} - {conta_info['banco']} - Saldo: {conta_info['saldo']:,.2f}")
        
        if not opcoes_contas:
            self.mostrar_erro(f"Nenhuma conta bancária encontrada em {dados['moeda']}!")
            return
        
        self.spinner_conta_bancaria_swift = Spinner(
            text=opcoes_contas[0],
            values=opcoes_contas,
            size_hint_y=None,
            height=45,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        
        # Grid para campos SWIFT específicos
        grid_campos = GridLayout(
            cols=1,
            spacing=8,
            padding=[0, 10, 0, 10],
            size_hint_y=None,
            height=550
        )
        grid_campos.bind(minimum_height=grid_campos.setter('height'))

        # Campos SWIFT específicos - 🔥 COM "Benef." ABREVIADO        
        campos_swift = [
            ("LINHA 1: UETR#", ""),
            ("LINHA 2: :20:", ""),
            ("LINHA 3: :32A:", ""),
            ("LINHA 4: :50K:", ""),
            ("LINHA 5: :57A:", ""),
            ("LINHA 6: :59:", ""),
            ("LINHA 7: Benef.", ""),  # 🔥 "Benef." ABREVIADO
            ("LINHA 8: :70:", ""),
            ("LINHA 9: :71A:", "")
        ]
        
        self.campos_swift = {}
        
        for label, valor_padrao in campos_swift:
            # Container para cada linha
            linha_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=45,
                spacing=10
            )
            
            # Label
            lbl = Label(
                text=label,
                font_size='11sp',
                bold=True,
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.3,
                text_size=(None, None),
                halign='left'
            )
            linha_layout.add_widget(lbl)
            
            # Campo de entrada - 🔥 AGORA EM BRANCO
            campo = TextInput(
                text=valor_padrao,  # 🔥 VAZIO
                hint_text=f'Digite {label}...',
                size_hint_x=0.7,
                multiline=False,
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
                padding=[10, 10],
                font_size='11sp'
            )
            
            self.campos_swift[label] = campo
            linha_layout.add_widget(campo)
            grid_campos.add_widget(linha_layout)
        
        # Botões
        botoes_layout = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=50, 
            spacing=10
        )
        
        btn_confirmar = Button(
            text='CONCLUIR COM DADOS SWIFT',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        # 🔥 ADICIONAR TUDO AO CONTENT NA ORDEM CORRETA
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_info)
        content.add_widget(lbl_conta)  # 🔥 NOVO: CONTA BANCÁRIA
        content.add_widget(self.spinner_conta_bancaria_swift)  # 🔥 NOVO: SPINNER CONTA
        content.add_widget(grid_campos)
        content.add_widget(botoes_layout)
        
        # Criar popup
        popup = Popup(
            title='Dados SWIFT - Concluir Processamento',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(700, 950),  # 🔥 AUMENTEI A ALTURA DO POPUP
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            # 🔥 OBTER CONTA BANCÁRIA SELECIONADA
            conta_selecionada = self.spinner_conta_bancaria_swift.text
            conta_numero = conta_selecionada.split(' - ')[0].strip()
            
            # Validar campos obrigatórios SWIFT
            campos_obrigatorios = [
                "LINHA 1: UETR#",
                "LINHA 2: :20:", 
                "LINHA 3: :32A:",
                "LINHA 4: :50K:",
                "LINHA 5: :57A:",
                "LINHA 6: :59:"
            ]
            
            for campo in campos_obrigatorios:
                if campo in self.campos_swift and not self.campos_swift[campo].text.strip():
                    self.mostrar_erro(f"Campo '{campo}' é obrigatório!")
                    return
            
            # Coletar dados SWIFT no formato específico - 🔥 COM "Benef." ABREVIADO
            dados_swift = {
                'linha1_uetr': self.campos_swift["LINHA 1: UETR#"].text.strip(),
                'linha2_20': self.campos_swift["LINHA 2: :20:"].text.strip(),
                'linha3_32a': self.campos_swift["LINHA 3: :32A:"].text.strip(),
                'linha4_50k': self.campos_swift["LINHA 4: :50K:"].text.strip(),
                'linha5_57a': self.campos_swift["LINHA 5: :57A:"].text.strip(),
                'linha6_59': self.campos_swift["LINHA 6: :59:"].text.strip(),
                'linha7_beneficiario': self.campos_swift["LINHA 7: Benef."].text.strip(),  # 🔥 "Benef." ABREVIADO
                'linha8_70': self.campos_swift["LINHA 8: :70:"].text.strip(),
                'linha9_71a': self.campos_swift["LINHA 9: :71A:"].text.strip()
            }
            
            # 🔥 CONCLUIR COM DADOS SWIFT E CRÉDITO BANCÁRIO
            if self._concluir_com_swift_e_credito(transferencia_id, dados_swift, conta_numero):
                popup.dismiss()
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída com dados SWIFT!\nValor creditado na conta {conta_numero}")
                self.carregar_dados()
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    def _concluir_com_credito_bancario(self, transferencia_id, conta_bancaria_numero):
        """Conclui transferência e DEBITA valor da conta bancária da empresa - VERSÃO CORRIGIDA"""
        sistema = App.get_running_app().sistema
        
        try:
            if transferencia_id not in sistema.transferencias:
                self.mostrar_erro("Transferência não encontrada!")
                return False
            
            dados = sistema.transferencias[transferencia_id]
            valor = dados['valor']
            moeda = dados['moeda']
            
            # 🔥 VERIFICAR SE A CONTA BANCÁRIA EXISTE E É DA MESMA MOEDA
            if conta_bancaria_numero not in sistema.contas_bancarias_empresa:
                self.mostrar_erro(f"Conta bancária {conta_bancaria_numero} não encontrada!")
                return False
            
            conta_info = sistema.contas_bancarias_empresa[conta_bancaria_numero]
            if conta_info['moeda'] != moeda:
                self.mostrar_erro(f"A conta bancária selecionada é em {conta_info['moeda']}, mas a transferência é em {moeda}!")
                return False
            
            # 🔥 VERIFICAR SE TEM SALDO SUFICIENTE NA CONTA BANCÁRIA
            if conta_info['saldo'] < valor:
                self.mostrar_erro(f"Saldo insuficiente na conta bancária!\nSaldo atual: {conta_info['saldo']:,.2f} {moeda}\nValor necessário: {valor:,.2f} {moeda}")
                return False
            
            # 🔥 DEBUG: Mostrar saldo antes
            saldo_antes = conta_info['saldo']
            print(f"💰 CRÉDITO BANCÁRIO - ANTES: {conta_bancaria_numero} = {saldo_antes:,.2f} {moeda}")
            
            # 🔥 🔥 🔥 CORREÇÃO: CRÉDITO NA CONTA BANCÁRIA (DIMINUI SALDO) - DINHEIRO SAI DA NOSSA CONTA
            sistema.contas_bancarias_empresa[conta_bancaria_numero]['saldo'] -= valor  # 🔥 CRÉDITO = - (DINHEIRO SAI)
            
            # 🔥 DEBUG: Mostrar saldo depois
            saldo_depois = sistema.contas_bancarias_empresa[conta_bancaria_numero]['saldo']
            print(f"💰 CRÉDITO BANCÁRIO - DEPOIS: {conta_bancaria_numero} = {saldo_depois:,.2f} {moeda} (-{valor:,.2f} {moeda})")
            
            # 🔥 CORREÇÃO: Atualizar status da transferência
            data_conclusao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 🔥 DEFINIR A VARIÁVEL
            sistema.transferencias[transferencia_id]['status'] = 'completed'
            sistema.transferencias[transferencia_id]['data_conclusao'] = data_conclusao
            sistema.transferencias[transferencia_id]['concluido_por'] = sistema.usuario_logado
            sistema.transferencias[transferencia_id]['conta_bancaria_credito'] = conta_bancaria_numero
            sistema.transferencias[transferencia_id]['data'] = data_conclusao  # 🔥🔥🔥 AGORA FUNCIONA
            
            # 🔥 SALVAR TUDO
            sistema.salvar_contas_bancarias()
            sistema.salvar_transferencias()
            
            print(f"Transferência {transferencia_id} concluída e valor DEBITADO da conta bancária {conta_bancaria_numero}")
            return True
            
        except Exception as e:
            print(f"Erro ao concluir transferência: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao concluir: {str(e)}")
            return False
        
    def _concluir_com_swift_e_credito(self, transferencia_id, dados_swift, conta_bancaria_numero):
        """Conclui transferência internacional com dados SWIFT - CRÉDITO DIMINUI SALDO DA EMPRESA"""
        sistema = App.get_running_app().sistema
        
        try:
            # 🔥 Buscar dados da transferência do Supabase
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return False
            
            dados = response.data[0]
            valor = dados['valor']
            moeda = dados['moeda']
            
            # 🔥 Buscar conta bancária da empresa no Supabase (COLUNA CORRETA: 'numero')
            print(f"💰 Buscando conta bancária {conta_bancaria_numero} no Supabase...")
            
            response_conta = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('*')\
                .eq('numero', conta_bancaria_numero)\
                .execute()
            
            if not response_conta.data:
                self.mostrar_erro(f"Conta bancária {conta_bancaria_numero} não encontrada no Supabase!")
                return False
            
            conta_info = response_conta.data[0]
            
            # Verificar moeda
            if conta_info['moeda'] != moeda:
                self.mostrar_erro(f"A conta bancária selecionada é em {conta_info['moeda']}, mas a transferência é em {moeda}!")
                return False
            
            # 🔥 CRÉDITO NA CONTA DA EMPRESA = DIMINUI SALDO
            saldo_antes = float(conta_info['saldo'])
            novo_saldo = saldo_antes - valor  # 🔥 CRÉDITO = - (DINHEIRO SAI DA EMPRESA)
            
            print(f"💰 CRÉDITO BANCÁRIO: {conta_bancaria_numero} = {saldo_antes:,.2f} → {novo_saldo:,.2f} (-{valor:,.2f} {moeda})")
            
            # Verificar saldo suficiente
            if novo_saldo < 0:
                self.mostrar_erro(f"Saldo insuficiente na conta da empresa!\nSaldo atual: {saldo_antes:,.2f} {moeda}\nValor do crédito: {valor:,.2f} {moeda}")
                return False
            
            # 🔥 ATUALIZAR SALDO NO SUPABASE
            update_saldo_response = sistema.supabase.client.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo})\
                .eq('numero', conta_bancaria_numero)\
                .execute()
            
            if not update_saldo_response.data:
                self.mostrar_erro("Erro ao atualizar saldo no Supabase!")
                return False
            
            # 🔥 ATUALIZAR TRANSFERÊNCIA NO SUPABASE
            data_conclusao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data_transferencia = {
                'status': 'completed',
                'data_conclusao': data_conclusao,
                'data': data_conclusao,  # 🔥🔥🔥 CORREÇÃO CRÍTICA: ATUALIZAR DATA PRINCIPAL
                'concluido_por': sistema.usuario_logado,
                'dados_swift_pagamento': dados_swift,
                'conta_bancaria_credito': conta_bancaria_numero
            }
            
            response_update = sistema.supabase.client.table('transferencias')\
                .update(update_data_transferencia)\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response_update.data:
                self.mostrar_erro("Erro ao atualizar transferência no Supabase!")
                return False
            
            # 🔥 SINCRONIZAR DADOS LOCAIS
            if transferencia_id in sistema.transferencias:
                sistema.transferencias[transferencia_id].update(update_data_transferencia)
                sistema.salvar_transferencias()
            
            print(f"✅ Transferência internacional {transferencia_id} concluída com SWIFT!")
            print(f"📋 Dados SWIFT registrados")
            print(f"🏦 Crédito lançado na conta: {conta_bancaria_numero}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao concluir transferência internacional: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao concluir: {str(e)}")
            return False

    def obter_nome_cliente_por_conta(self, sistema, conta_numero):
        """Obtém o nome do cliente por número da conta"""
        if conta_numero in sistema.contas:
            return sistema.contas[conta_numero].get('cliente_nome', 'Cliente')
        return 'Conta Externa'

    def mostrar_confirmacao_aprovacao(self, transferencia_id):
        """Mostra popup de confirmação para aprovação - VERSÃO SUPABASE"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Buscar dados do Supabase
        try:
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                self.mostrar_erro("Transferência não encontrada!")
                return
            
            dados = response.data[0]
            cliente_nome = self.obter_nome_cliente(dados['conta_remetente'])
            info_invoice = sistema.obter_info_invoice(transferencia_id)
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar dados: {e}")
            return
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_titulo = Label(
            text="CONFIRMAR APROVAÇÃO",
            font_size='16sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            text_size=(400, None),
            halign='center'
        )
        
        # 🔥 ADICIONAR INFORMAÇÃO DA INVOICE
        status_invoice = "N/A"
        cor_invoice = (0.8, 0.8, 0.8, 1)
        
        if info_invoice:
            if info_invoice['status'] == 'approved':
                status_invoice = "APROVADA"
                cor_invoice = (0.2, 0.8, 0.2, 1)
            elif info_invoice['status'] == 'pending':
                status_invoice = "PENDENTE"
                cor_invoice = (1.0, 0.65, 0.0, 1)
            elif info_invoice['status'] == 'rejected':
                status_invoice = "RECUSADA"
                cor_invoice = (1, 0.3, 0.3, 1)
        else:
            status_invoice = "NÃO EXIGIDA" if dados.get('tipo') != 'internacional' else "❌ AUSENTE"
        
        detalhes = f"""
ID: {transferencia_id}
Cliente: {cliente_nome}
Valor: {dados['valor']:,.2f} {dados['moeda']}
Status Invoice: {status_invoice}
        """.strip()
        
        if dados.get('tipo') == 'transferencia_internacional':
            detalhes += f"\nBeneficiário: {dados.get('beneficiario', 'N/A')}"
            detalhes += f"\nTipo: Transferência Internacional"
        else:
            conta_destino = dados.get('conta_destinatario', 'N/A')
            destinatario = self.obter_nome_cliente(conta_destino)
            detalhes += f"\nDestinatário: {destinatario}"
            detalhes += f"\nTipo: Transferência Interna"
        
        lbl_detalhes = Label(
            text=detalhes,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center'
        )
        
        # 🔥 MENSAGEM CONDICIONAL BASEADA NO STATUS DA INVOICE
        if info_invoice and info_invoice['status'] == 'approved':
            mensagem_confirmacao = "Invoice APROVADA \nDeseja aprovar esta transferência?"
        elif info_invoice and info_invoice['status'] == 'pending':
            mensagem_confirmacao = "Invoice PENDENTE \nAprovação BLOQUEADA até invoice ser aprovada!"
        elif info_invoice and info_invoice['status'] == 'rejected':
            mensagem_confirmacao = "Invoice RECUSADA \nAprovação BLOQUEADA!"
        else:
            if dados.get('tipo') == 'transferencia_internacional':
                mensagem_confirmacao = "Invoice AUSENTE \nTransferência internacional exige invoice!"
            else:
                mensagem_confirmacao = "Deseja aprovar esta transferência?"
        
        lbl_confirmacao = Label(
            text=mensagem_confirmacao,
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(400, None),
            halign='center'
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_confirmar = Button(
            text='CONFIRMAR APROVAÇÃO',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        # 🔥 DESABILITAR BOTÃO SE INVOICE NÃO ESTIVER APROVADA
        if info_invoice and info_invoice['status'] != 'approved':
            btn_confirmar.disabled = True
            btn_confirmar.background_color = (0.5, 0.5, 0.5, 1)
            btn_confirmar.text = 'APROVAÇÃO BLOQUEADA'
        elif not info_invoice and dados.get('tipo') == 'transferencia_internacional':
            btn_confirmar.disabled = True
            btn_confirmar.background_color = (0.5, 0.5, 0.5, 1)
            btn_confirmar.text = 'INVOICE OBRIGATÓRIA'
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_detalhes)
        content.add_widget(lbl_confirmacao)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Aprovar Transferência',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(450, 350),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            # 🔥 VERIFICAR se aprovar_transferencia atualiza no Supabase
            if self.aprovar_transferencia(transferencia_id):
                popup.dismiss()
                self.carregar_dados()
                self.mostrar_sucesso(f"Transferência {transferencia_id} aprovada!")
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()

    
    def mostrar_popup_motivo_recusa(self):
        """Mostra popup para informar motivo da recusa - VERSÃO SUPABASE"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        
        sistema = App.get_running_app().sistema
        transferencia_id = self.transferencia_selecionada_id
        
        # 🔥 CORREÇÃO: Buscar dados do Supabase
        try:
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return
            
            dados = response.data[0]
            cliente_nome = self.obter_nome_cliente(dados['conta_remetente'])
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar dados: {e}")
            return
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_titulo = Label(
            text="MOTIVO DA RECUSA",
            font_size='16sp',
            bold=True,
            color=(1, 0.3, 0.3, 1),
            text_size=(400, None),
            halign='center'
        )
        
        info_text = f"ID: {transferencia_id}\nCliente: {cliente_nome}\nValor: {dados['valor']:,.2f} {dados['moeda']}"
        
        lbl_info = Label(
            text=info_text,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center'
        )
        
        lbl_motivo = Label(
            text="Motivo da Recusa:*",
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(400, None),
            halign='left'
        )
        
        text_motivo = TextInput(
            hint_text='Digite o motivo da recusa...',
            size_hint_y=0.6,  # 🔥 MAIOR ALTURA (60% do popup)
            multiline=True,    # 🔥 PERMITIR MÚLTIPLAS LINHAS
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10],
            font_size='14sp'   # 🔥 FONTE MAIOR
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_confirmar = Button(
            text='CONFIRMAR RECUSA',
            background_color=(0.96, 0.51, 0.23, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_info)
        content.add_widget(lbl_motivo)
        content.add_widget(text_motivo)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Recusar Transferência',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(500, 500),  # 🔥 POPUP MAIOR (500x500)
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            motivo = text_motivo.text.strip()
            if not motivo:
                self.mostrar_erro("Informe o motivo da recusa!")
                return
            
            # 🔥 CORREÇÃO: Já corrigimos recusar_transferencia() para usar Supabase
            if self.recusar_transferencia(transferencia_id, motivo):
                popup.dismiss()
                self.carregar_dados()
                self.mostrar_sucesso(f"Transferência {transferencia_id} recusada!")
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()
    
    def mostrar_confirmacao_conclusao(self, transferencia_id):
        """Mostra popup de confirmação para conclusão"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        sistema = App.get_running_app().sistema
        dados = sistema.transferencias[transferencia_id]
        cliente_nome = self.obter_nome_cliente(dados['conta_remetente'])
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_titulo = Label(
            text="CONFIRMAR CONCLUSÃO",
            font_size='16sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            text_size=(400, None),
            halign='center'
        )
        
        detalhes = f"""
ID: {transferencia_id}
Cliente: {cliente_nome}
Valor: {dados['valor']:,.2f} {dados['moeda']}
Status: {dados['status'].title()}
        """.strip()
        
        lbl_detalhes = Label(
            text=detalhes,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(400, None),
            halign='center'
        )
        
        lbl_confirmacao = Label(
            text="Marcar transferência como CONCLUÍDA?\nEsta ação não pode ser desfeita.",
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(400, None),
            halign='center'
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_confirmar = Button(
            text='CONFIRMAR CONCLUSÃO',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_confirmar)
        botoes_layout.add_widget(btn_cancelar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_detalhes)
        content.add_widget(lbl_confirmacao)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Concluir Processamento',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(450, 300),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            if self.concluir_processamento(transferencia_id):
                popup.dismiss()
                self.carregar_dados()
                self.mostrar_sucesso(f"Transferência {transferencia_id} concluída!")
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()
    
    def mostrar_popup_detalhes(self):
        """Mostra popup com detalhes completos da transferência - VERSÃO MAIOR SEM SCROLL"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        sistema = App.get_running_app().sistema
        transferencia_id = self.transferencia_selecionada_id
        dados = sistema.transferencias[transferencia_id]
        
        content = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        lbl_titulo = Label(
            text="DETALHES COMPLETOS DA TRANSFERÊNCIA",
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(500, None),
            halign='center',
            size_hint_y=None,
            height=40
        )
        
        # Criar layout para todos os detalhes sem scroll
        detalhes_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 0])
        
        # Informações básicas
        info_basica = f"""
ID: {transferencia_id}
Status: {dados['status'].title()}
Tipo: {'Internacional' if dados.get('tipo') == 'internacional' else 'Interna'}
Valor: {dados['valor']:,.2f} {dados['moeda']}
Taxa: {dados.get('taxa', 0):,.2f}
Total: {(dados['valor'] + dados.get('taxa', 0)):,.2f} {dados['moeda']}
Data Solicitação: {dados.get('data_solicitacao', dados.get('data', 'N/A'))}
        """.strip()
        
        lbl_basica = Label(
            text=info_basica,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=140
        )
        detalhes_layout.add_widget(lbl_basica)
        
        # Informações do cliente
        cliente_nome = self.obter_nome_cliente(dados['conta_remetente'])
        info_cliente = f"""
CLIENTE REMETENTE:
Nome: {cliente_nome}
Conta Origem: {dados['conta_remetente']}
Solicitado por: {dados.get('solicitado_por', 'N/A')}
        """.strip()
        
        lbl_cliente = Label(
            text=info_cliente,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=80
        )
        detalhes_layout.add_widget(lbl_cliente)
        
        # Informações do beneficiário/destinatário
        if dados.get('tipo') == 'internacional':
            info_beneficiario = f"""
BENEFICIÁRIO INTERNACIONAL:
Nome: {dados.get('beneficiario', 'N/A')}
Endereço: {dados.get('endereco_beneficiario', 'N/A')}
Banco: {dados.get('nome_banco', 'N/A')}
Código SWIFT: {dados.get('codigo_swift', 'N/A')}
IBAN/Conta: {dados.get('iban_account', 'N/A')}
País: {dados.get('pais_beneficiario', 'N/A')}
            """.strip()
            altura_beneficiario = 160
        else:
            conta_destino = dados.get('conta_destinatario', 'N/A')
            info_beneficiario = f"""
DESTINATÁRIO INTERNO:
Nome: {self.obter_nome_cliente(conta_destino)}
Conta Destino: {conta_destino}
            """.strip()
            altura_beneficiario = 60
        
        lbl_beneficiario = Label(
            text=info_beneficiario,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(480, None),
            halign='left',
            size_hint_y=None,
            height=altura_beneficiario
        )
        detalhes_layout.add_widget(lbl_beneficiario)
        
        # Informações adicionais
        info_adicional = ""
        if 'finalidade' in dados:
            info_adicional += f"Finalidade: {dados['finalidade']}\n"
        if 'descricao' in dados:
            info_adicional += f"Descrição: {dados.get('descricao', 'Nenhuma')}\n"
        
        if info_adicional:
            lbl_adicional = Label(
                text=f"INFORMAÇÕES ADICIONAIS:\n{info_adicional}",
                font_size='14sp',
                color=(0.9, 0.9, 0.9, 1),
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=80
            )
            detalhes_layout.add_widget(lbl_adicional)
        
        # Informações de processamento (se disponíveis)
        if dados.get('data_aprovacao'):
            info_processamento = f"""
PROCESSAMENTO:
Aprovado por: {dados.get('executado_por', 'N/A')}
Data Aprovação: {dados.get('data_aprovacao', 'N/A')}
            """.strip()
            
            if dados.get('data_conclusao'):
                info_processamento += f"\nConcluído por: {dados.get('concluido_por', 'N/A')}"
                info_processamento += f"\nData Conclusão: {dados.get('data_conclusao', 'N/A')}"
            
            lbl_processamento = Label(
                text=info_processamento,
                font_size='14sp',
                color=(0.9, 0.9, 0.9, 1),
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=80
            )
            detalhes_layout.add_widget(lbl_processamento)
        
        # Motivo da recusa (se aplicável)
        if dados.get('status') == 'rejected' and dados.get('motivo_recusa'):
            lbl_recusa = Label(
                text=f"MOTIVO DA RECUSA:\n{dados['motivo_recusa']}",
                font_size='14sp',
                color=(1, 0.5, 0.5, 1),
                text_size=(480, None),
                halign='left',
                size_hint_y=None,
                height=60
            )
            detalhes_layout.add_widget(lbl_recusa)
        
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=50,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(detalhes_layout)
        content.add_widget(btn_fechar)
        
        # Calcular altura total baseada no conteúdo
        altura_total = 600  # Altura base
        
        # Ajustar altura baseada no tipo de transferência
        if dados.get('tipo') == 'internacional':
            altura_total += 100  # Mais espaço para informações internacionais
        if dados.get('data_aprovacao'):
            altura_total += 80   # Mais espaço para informações de processamento
        if dados.get('status') == 'rejected':
            altura_total += 60   # Mais espaço para motivo da recusa
        
        popup = Popup(
            title='Detalhes da Transferência',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(550, altura_total),  # Largura fixa, altura dinâmica
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            bold=True,
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
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

# === MÉTODOS PARA TelaAprovarOperacoes ===

    def analisar_invoice_selecionado(self):
        """Abre o modal para análise da invoice - NÃO afeta status da transferência"""
        if not hasattr(self, 'transferencia_selecionada_id'):
            self.mostrar_erro("Selecione uma transferência para analisar a invoice!")
            return
        
        sistema = App.get_running_app().sistema
        transferencia_id = self.transferencia_selecionada_id
        
        # Verificar se a transferência tem invoice
        if not sistema.transferencia_tem_invoice(transferencia_id):
            self.mostrar_erro("Esta transferência não tem invoice anexada!")
            return
        
        # Abrir modal de análise
        self.mostrar_modal_analise_invoice(transferencia_id)

    def mostrar_modal_analise_invoice(self, transferencia_id):
        """Modal ESPECÍFICO para análise de invoice - NÃO afeta status da transferência"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Buscar dados do Supabase
        try:
            # Buscar transferência no Supabase
            response = sistema.supabase.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if not response.data:
                self.mostrar_erro("Transferência não encontrada no Supabase!")
                return
            
            dados_transferencia = response.data[0]
            info_invoice = sistema.obter_info_invoice(transferencia_id)
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao buscar dados: {e}")
            return
        
        # Criar conteúdo do modal
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.size_hint_y = None
        content.height = 500  # Altura inicial
        
        # Título
        lbl_titulo = Label(
            text='ANÁLISE DE INVOICE',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=40,
            text_size=(400, None),
            halign='center'
        )
        
        # Informações da transferência
        info_text = f"ID: {transferencia_id}\nCliente: {self.obter_nome_cliente(dados_transferencia['conta_remetente'])}\nValor: {dados_transferencia['valor']:,.2f} {dados_transferencia['moeda']}"
        
        lbl_info = Label(
            text=info_text,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=80,
            text_size=(400, None),
            halign='center'
        )
        
        # Status atual da invoice
        status_invoice = info_invoice['status']
        cor_status = (1.0, 0.65, 0.0, 1) if status_invoice == 'pending' else (
            (0.2, 0.8, 0.2, 1) if status_invoice == 'approved' else (1, 0.3, 0.3, 1)
        )
        texto_status = 'PENDENTE' if status_invoice == 'pending' else (
            'APROVADA' if status_invoice == 'approved' else 'RECUSADA'
        )
        
        lbl_status = Label(
            text=f"Status da Invoice: {texto_status}",
            font_size='14sp',
            bold=True,
            color=cor_status,
            size_hint_y=None,
            height=30,
            text_size=(400, None),
            halign='center'
        )
        
        # Motivo da recusa (se existir)
        motivo_recusa = info_invoice.get('motivo_recusa', '')
        if motivo_recusa:
            lbl_motivo = Label(
                text=f"Motivo da recusa anterior: {motivo_recusa}",
                font_size='12sp',
                color=(1, 0.5, 0.5, 1),
                size_hint_y=None,
                height=40,
                text_size=(400, None),
                halign='center'
            )
            content.add_widget(lbl_motivo)
        
        # Botões de ação para a invoice
        botoes_invoice_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        btn_ver_arquivo = Button(
            text='VISUALIZAR INV.',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_aprovar_invoice = Button(
            text='APROVAR INV.',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_recusar_invoice = Button(
            text='RECUSAR INV.',
            background_color=(0.96, 0.51, 0.23, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_invoice_layout.add_widget(btn_ver_arquivo)
        botoes_invoice_layout.add_widget(btn_aprovar_invoice)
        botoes_invoice_layout.add_widget(btn_recusar_invoice)
        
        # Variável para controlar se o modo recusa está ativo
        self.modo_recusa_ativo = False
        
        # Campo para motivo da recusa (inicialmente invisível)
        self.text_motivo_recusa_invoice = TextInput(
            hint_text='Digite o motivo da recusa da invoice...',
            size_hint_y=None,
            height=80,
            multiline=True,
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10],
            font_size='12sp',
            opacity=0,  # Inicialmente invisível
            size_hint_x=1
        )
        
        # Botão para confirmar recusa (inicialmente invisível)
        btn_confirmar_recusa = Button(
            text='CONFIRMAR RECUSA DA INVOICE',
            size_hint_y=None,
            height=45,
            background_color=(0.96, 0.51, 0.23, 1),
            color=(1, 1, 1, 1),
            opacity=0  # Inicialmente invisível
        )
        
        # Botão fechar
        btn_fechar = Button(
            text='FECHAR',
            size_hint_y=None,
            height=45,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        # Adicionar widgets ao conteúdo
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_info)
        content.add_widget(lbl_status)
        content.add_widget(botoes_invoice_layout)
        content.add_widget(self.text_motivo_recusa_invoice)
        content.add_widget(btn_confirmar_recusa)
        content.add_widget(btn_fechar)
        
        # Criar popup
        popup = Popup(
            title='Análise de Invoice',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(500, 500),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def visualizar_invoice(instance):
            """Abre o arquivo da invoice do Supabase Storage"""
            try:
                import webbrowser
                import tempfile
                import os
                
                caminho_arquivo = info_invoice['caminho_arquivo']
                
                # 🔥 CORREÇÃO CRÍTICA: Normalizar caminho
                caminho_normalizado = caminho_arquivo.replace('\\', '/')
                print(f"📥 Baixando invoice: {caminho_normalizado}")
                
                # 🔥 DEBUG: Verificar se o arquivo existe no storage
                try:
                    lista_arquivos = sistema.supabase.client.storage.from_("invoices").list()
                    print(f"🔍 Arquivos disponíveis no storage:")
                    for arquivo in lista_arquivos:
                        print(f"   📄 {arquivo['name']}")
                    
                    # Verificar se nosso arquivo está na lista
                    nome_arquivo = caminho_normalizado.split('/')[-1]  # Pega apenas o nome do arquivo
                    arquivo_encontrado = any(arquivo['name'] == nome_arquivo for arquivo in lista_arquivos)
                    print(f"🔍 Arquivo '{nome_arquivo}' encontrado: {arquivo_encontrado}")
                    
                except Exception as list_error:
                    print(f"⚠️ Erro ao listar arquivos: {list_error}")
                
                # Tentar baixar
                response = sistema.supabase.client.storage.from_("invoices")\
                    .download(caminho_normalizado)
                
                if isinstance(response, bytes) and len(response) > 0:
                    # Salvar temporariamente
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                        temp_file.write(response)
                        temp_path = temp_file.name
                    
                    print(f"✅ Invoice baixada com sucesso! ({len(response)} bytes)")
                    webbrowser.open(temp_path)
                else:
                    print(f"❌ Falha no download - resposta: {type(response)}")
                    self.mostrar_erro("Não foi possível baixar a invoice. Arquivo pode não existir no storage.")
                
            except Exception as e:
                print(f"❌ Erro ao abrir invoice: {e}")
                import traceback
                traceback.print_exc()
                self.mostrar_erro(f"Erro técnico ao abrir invoice: {str(e)}")
        
        def aprovar_invoice(instance):
            """Aprova a invoice - NÃO altera status da transferência"""
            if sistema.aprovar_invoice(transferencia_id):
                popup.dismiss()
                self.mostrar_sucesso(f"Invoice da transferência {transferencia_id} aprovada!")
                self.carregar_dados()
            else:
                self.mostrar_erro("Erro ao aprovar invoice!")
        
        def ativar_modo_recusa(instance):
            """Ativa o modo recusa - mostra campo e botão de confirmação"""
            self.modo_recusa_ativo = True
            self.text_motivo_recusa_invoice.opacity = 1
            self.text_motivo_recusa_invoice.height = 80
            btn_confirmar_recusa.opacity = 1
            btn_confirmar_recusa.height = 45
            # Ajustar altura do popup
            popup.height = 600
            content.height = 600
        
        def confirmar_recusa_invoice(instance):
            """Confirma a recusa da invoice"""
            if not self.modo_recusa_ativo:
                self.mostrar_erro("Clique primeiro em 'RECUSAR INVOICE' para ativar o modo recusa!")
                return
                
            motivo = self.text_motivo_recusa_invoice.text.strip()
            if not motivo:
                self.mostrar_erro("Informe o motivo da recusa da invoice!")
                return
            
            if sistema.recusar_invoice(transferencia_id, motivo):
                popup.dismiss()
                self.mostrar_sucesso(f"Invoice da transferência {transferencia_id} recusada!\nO cliente poderá enviar uma nova invoice.")
                self.carregar_dados()
            else:
                self.mostrar_erro("Erro ao recusar invoice!")
        
        def fechar_modal(instance):
            popup.dismiss()
        
        # Vincular eventos CORRETAMENTE
        btn_ver_arquivo.bind(on_press=visualizar_invoice)
        btn_aprovar_invoice.bind(on_press=aprovar_invoice)
        btn_recusar_invoice.bind(on_press=ativar_modo_recusa)
        btn_confirmar_recusa.bind(on_press=confirmar_recusa_invoice)
        btn_fechar.bind(on_press=fechar_modal)
        
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            bold=True,
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
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


