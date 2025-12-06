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
    """Tela para gerenciamento detalhado de um cliente - SINCRONIZADO COM SUPABASE"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username_cliente = None
        self.dados_cliente = None
        self.supabase_manager = None

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1000, 800)
        
        # Inicializar SupabaseManager se ainda não foi
        if not self.supabase_manager:
            try:
                self.supabase_manager = App.get_running_app().sistema.supabase
            except:
                # Fallback - tentar criar instância
                from supabase_manager import SupabaseManager
                self.supabase_manager = SupabaseManager()

    def on_pre_leave(self):
        """Limpa dados ao sair da tela"""
        self.username_cliente = None
        self.dados_cliente = None

    def carregar_dados_cliente(self, username, dados_cliente):
        """Método principal para carregar todos os dados do cliente"""
        self.username_cliente = username
        self.dados_cliente = dados_cliente
        
        # Carregar dados pessoais (prioridade Supabase)
        self.carregar_dados_pessoais(username, dados_cliente)
        
        # Carregar contas do cliente (prioridade Supabase)
        self.carregar_contas_cliente_supabase(username)

    def carregar_dados_pessoais(self, username, dados_cliente):
        """Carrega a seção de dados pessoais - VERSÃO SUPABASE"""
        container = self.ids.dados_pessoais_container
        container.clear_widgets()
        
        try:
            # 1. PRIORIDADE: Buscar dados atualizados do Supabase
            dados_supabase = self.obter_dados_cliente_supabase(username)
            
            # Usar dados do Supabase se disponíveis, senão usar os passados
            if dados_supabase:
                dados_para_exibir = dados_supabase
                fonte_dados = "SUPABASE"
            else:
                dados_para_exibir = dados_cliente
                fonte_dados = "CACHE"
            
            print(f"📊 Dados carregados de: {fonte_dados} para {username}")
            
            # 2. Buscar informações adicionais do sistema
            sistema = App.get_running_app().sistema
            contas_cliente = self.obter_contas_cliente_supabase_ou_local(username)
            total_contas = len(contas_cliente)
            saldo_total = sum(conta['saldo'] for conta in contas_cliente)
            
            # 3. Verificar beneficiários no Supabase
            tem_beneficiarios = False
            if self.supabase_manager and self.supabase_manager.conectado:
                try:
                    response = self.supabase_manager.client.table('beneficiarios')\
                        .select('id')\
                        .eq('cliente_username', username)\
                        .execute()
                    tem_beneficiarios = len(response.data) > 0
                except:
                    tem_beneficiarios = username in sistema.beneficiarios and len(sistema.beneficiarios[username]) > 0
            
            # 4. Preparar dados para exibição
            dados = [
                # Linha 1 - Dados principais
                ('USUÁRIO', username, (0.23, 0.51, 0.96, 1)),
                ('NOME', dados_para_exibir.get('nome', 'N/A'), (0.23, 0.51, 0.96, 1)),
                ('EMAIL', dados_para_exibir.get('email', 'N/A'), (0.55, 0.36, 0.96, 1)),
                ('TELEFONE', dados_para_exibir.get('telefone', 'N/A'), (0.55, 0.36, 0.96, 1)),
                
                # Linha 2 - Documentos e status
                ('DOCUMENTO', dados_para_exibir.get('documento', 'N/A'), (0.2, 0.8, 0.2, 1)),
                ('TIPO', dados_para_exibir.get('tipo', 'cliente').upper(), (0.96, 0.36, 0.36, 1)),
                ('DATA CADASTRO', dados_para_exibir.get('data_cadastro', 'N/A'), (0.9, 0.7, 0.3, 1)),
                ('STATUS', dados_para_exibir.get('status', 'ativo').upper(), (0.7, 0.5, 0.9, 1)),
                
                # Linha 3 - Informações financeiras
                ('TOTAL CONTAS', str(total_contas), (0.3, 0.7, 0.9, 1)),
                ('SALDO TOTAL', f"{saldo_total:,.2f}", (0.2, 0.8, 0.2, 1)),
                ('PERM. CÂMBIO', 'SIM' if dados_para_exibir.get('cambio_liberado', False) else 'NÃO', (0.3, 0.7, 0.9, 1)),
                ('BENEFICIÁRIOS', 'SIM' if tem_beneficiarios else 'NÃO', (0.9, 0.5, 0.3, 1))
            ]
            
            # 5. Criar cards
            for chave, valor, cor in dados:
                card = self.criar_card_dado_4colunas(chave, valor, cor)
                container.add_widget(card)
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados pessoais: {e}")
            self.mostrar_erro_simples("Erro ao carregar dados do cliente")

    def obter_dados_cliente_supabase(self, username):
        """Obtém dados atualizados do cliente do Supabase"""
        try:
            if self.supabase_manager and self.supabase_manager.conectado:
                response = self.supabase_manager.client.table('usuarios')\
                    .select('*')\
                    .eq('username', username)\
                    .execute()
                
                if response.data:
                    usuario = response.data[0]
                    
                    # Mapear campos do Supabase para o formato local
                    dados_formatados = {
                        'username': usuario.get('username', ''),
                        'nome': usuario.get('nome', ''),
                        'email': usuario.get('email', ''),
                        'telefone': usuario.get('telefone', ''),
                        'tipo': usuario.get('tipo', 'cliente'),
                        'data_cadastro': usuario.get('data_cadastro', ''),
                        'status': usuario.get('status', 'ativo'),
                        'cambio_liberado': usuario.get('cambio_liberado', False),
                        'verificado': usuario.get('verificado', False)
                    }
                    
                    # Adicionar contas se existirem
                    if 'contas' in usuario:
                        dados_formatados['contas'] = usuario['contas']
                    
                    print(f"✅ Dados do Supabase obtidos para {username}")
                    return dados_formatados
                    
        except Exception as e:
            print(f"⚠️ Erro ao buscar dados do Supabase: {e}")
        
        return None

    def carregar_contas_cliente_supabase(self, username):
        """Carrega contas do cliente do Supabase"""
        container = self.ids.contas_container
        container.clear_widgets()
        
        # 🔥 GARANTIR ALTURA MÍNIMA
        altura_minima = dp(60)
        
        try:
            # 1. PRIORIDADE: Buscar contas do Supabase
            contas = self.obter_contas_cliente_supabase_ou_local(username)
            
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
            
            # Calcular altura total
            altura_por_conta = dp(60)
            altura_total = len(contas) * altura_por_conta
            container.height = max(altura_minima, altura_total)
            
            # Adicionar cards das contas
            for conta in contas:
                card = CardContaClienteSupabase(conta, self)
                container.add_widget(card)
                
        except Exception as e:
            print(f"❌ Erro ao carregar contas: {e}")
            lbl_erro = Label(
                text="Erro ao carregar contas",
                color=(1, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(lbl_erro)

    def obter_contas_cliente_supabase_ou_local(self, username):
        """Obtém contas do Supabase (prioridade) ou local (fallback)"""
        contas = []
        
        try:
            # 1. PRIORIDADE SUPABASE
            if self.supabase_manager and self.supabase_manager.conectado:
                print(f"🔍 Buscando contas do Supabase para {username}")
                
                response = self.supabase_manager.client.table('contas')\
                    .select('*')\
                    .eq('cliente_username', username)\
                    .execute()
                
                if response.data:
                    for conta in response.data:
                        contas.append({
                            'id': conta['id'],
                            'numero': conta['id'],  # ID é o número da conta
                            'moeda': conta['moeda'],
                            'saldo': float(conta['saldo']),
                            'cliente_username': conta['cliente_username'],
                            'cliente_nome': conta.get('cliente_nome', ''),
                            'data_criacao': conta.get('data_criacao', ''),
                            'ativa': conta.get('ativa', True)
                        })
                    
                    print(f"✅ {len(contas)} contas encontradas no Supabase")
                    return contas
            
            # 2. FALLBACK: Buscar localmente
            print(f"🔄 Fallback para dados locais de {username}")
            sistema = App.get_running_app().sistema
            
            if username in sistema.usuarios:
                contas_usuario = sistema.usuarios[username].get('contas', [])
                print(f"🔍 Contas locais: {contas_usuario}")
                
                for conta_num in contas_usuario:
                    if conta_num in sistema.contas:
                        dados_conta = sistema.contas[conta_num]
                        contas.append({
                            'id': conta_num,
                            'numero': conta_num,
                            'moeda': dados_conta['moeda'],
                            'saldo': dados_conta['saldo'],
                            'cliente_username': username,
                            'cliente_nome': dados_conta.get('cliente_nome', ''),
                            'data_criacao': dados_conta.get('data_criacao', 'N/A')
                        })
                
                print(f"✅ {len(contas)} contas encontradas localmente")
                
        except Exception as e:
            print(f"❌ Erro ao obter contas: {e}")
        
        return contas

    def criar_card_dado_4colunas(self, chave, valor, cor_titulo):
        """Cria um card individual para layout de 4 colunas"""
        card = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(60),
            padding=dp(4),
            spacing=dp(1)
        )
        
        # Background do card
        with card.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(4),])
            Color(0.12, 0.16, 0.23, 0.8)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(4)), width=0.8)
        
        # Label da chave (título)
        lbl_chave = Label(
            text=chave,
            font_size='12sp',
            bold=True,
            color=cor_titulo,
            size_hint_y=0.4,
            text_size=(None, None),
            halign='center'
        )
        
        # Label do valor
        lbl_valor = Label(
            text=str(valor),
            font_size='12sp',
            color=(1, 1, 1, 1),
            size_hint_y=0.6,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        card.add_widget(lbl_chave)
        card.add_widget(lbl_valor)
        
        return card

    def adicionar_conta(self):
        """Abre popup para adicionar nova conta - VERSÃO SIMPLIFICADA"""
        moedas_principais = ['USD', 'GBP', 'EUR', 'BRL']
        
        # Obter moedas que o cliente JÁ TEM
        contas_cliente = self.obter_contas_cliente_supabase_ou_local(self.username_cliente)
        moedas_existentes = [conta['moeda'] for conta in contas_cliente]
        
        # Moedas principais disponíveis
        moedas_disponiveis = [moeda for moeda in moedas_principais if moeda not in moedas_existentes]
        
        # Se não tem moedas disponíveis, só pode adicionar personalizada
        pode_adicionar_principal = len(moedas_disponiveis) > 0
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Título
        lbl_titulo = Label(
            text='ADICIONAR NOVA CONTA',
            font_size='18sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        
        # Container para seleção de tipo
        box_tipo = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        lbl_tipo = Label(
            text='Selecione o tipo de moeda:',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        
        # Criar opções para o spinner de tipo
        valores_tipo = []
        if pode_adicionar_principal:
            valores_tipo.append('Moeda Principal')
        valores_tipo.append('Moeda Personalizada')
        
        spinner_tipo = Spinner(
            text=valores_tipo[0],
            values=valores_tipo,
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        
        box_tipo.add_widget(lbl_tipo)
        box_tipo.add_widget(spinner_tipo)
        
        # Container para moeda principal (SPINNER)
        box_moeda_principal = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        lbl_moeda_principal = Label(
            text='Selecione a moeda:',
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        
        spinner_moeda = Spinner(
            text=moedas_disponiveis[0] if moedas_disponiveis else '',
            values=moedas_disponiveis,
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1)
        )
        
        box_moeda_principal.add_widget(lbl_moeda_principal)
        box_moeda_principal.add_widget(spinner_moeda)
        
        # Container para moeda personalizada (TEXTINPUT)
        box_moeda_personalizada = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        lbl_moeda_personalizada = Label(
            text='Digite o código (3 letras):',
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        
        input_moeda = TextInput(
            text='',
            hint_text='Ex: JPY, CAD, AUD, CHF...',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[dp(10), dp(10)],
            multiline=False
        )
        
        box_moeda_personalizada.add_widget(lbl_moeda_personalizada)
        box_moeda_personalizada.add_widget(input_moeda)
        
        # Saldo inicial
        box_saldo = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        lbl_saldo = Label(
            text='Saldo inicial:',
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        
        input_saldo = TextInput(
            text='0.00',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.20, 0.25, 0.33, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[dp(10), dp(10)],
            multiline=False,
            input_filter='float'
        )
        
        box_saldo.add_widget(lbl_saldo)
        box_saldo.add_widget(input_saldo)
        
        # Info
        lbl_info = Label(
            text="",
            font_size='12sp',
            color=(0.80, 0.84, 0.88, 1),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        
        # Botões
        box_botoes = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_adicionar = Button(
            text='Adicionar',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        box_botoes.add_widget(btn_cancelar)
        box_botoes.add_widget(btn_adicionar)
        
        # Adicionar widgets ao layout principal
        main_layout.add_widget(lbl_titulo)
        main_layout.add_widget(box_tipo)
        
        # Configurar visibilidade inicial
        if pode_adicionar_principal:
            main_layout.add_widget(box_moeda_principal)
            box_moeda_personalizada.opacity = 0
            box_moeda_personalizada.height = 0
            lbl_info.text = f"Moedas disponíveis: {', '.join(moedas_disponiveis)}"
        else:
            main_layout.add_widget(box_moeda_personalizada)
            box_moeda_principal.opacity = 0
            box_moeda_principal.height = 0
            spinner_tipo.values = ['Moeda Personalizada']
            spinner_tipo.text = 'Moeda Personalizada'
            lbl_info.text = "Digite o código da moeda (ex: JPY, CAD, AUD)"
        
        main_layout.add_widget(box_saldo)
        main_layout.add_widget(lbl_info)
        main_layout.add_widget(box_botoes)
        
        # Função para alternar
        def alternar_tipo(spinner, texto):
            if texto == 'Moeda Principal' and pode_adicionar_principal:
                # Remover personalizada se existir
                if box_moeda_personalizada in main_layout.children:
                    main_layout.remove_widget(box_moeda_personalizada)
                
                # Adicionar principal se não existir
                if box_moeda_principal not in main_layout.children:
                    # Encontrar posição correta (após box_tipo)
                    children = list(main_layout.children)
                    tipo_index = children.index(box_tipo)
                    main_layout.add_widget(box_moeda_principal, len(children) - tipo_index - 1)
                
                box_moeda_principal.opacity = 1
                box_moeda_principal.height = dp(80)
                lbl_info.text = f"Moedas disponíveis: {', '.join(moedas_disponiveis)}"
                
            elif texto == 'Moeda Personalizada':
                # Remover principal se existir
                if box_moeda_principal in main_layout.children:
                    main_layout.remove_widget(box_moeda_principal)
                
                # Adicionar personalizada se não existir
                if box_moeda_personalizada not in main_layout.children:
                    # Encontrar posição correta (após box_tipo)
                    children = list(main_layout.children)
                    tipo_index = children.index(box_tipo)
                    main_layout.add_widget(box_moeda_personalizada, len(children) - tipo_index - 1)
                
                box_moeda_personalizada.opacity = 1
                box_moeda_personalizada.height = dp(80)
                lbl_info.text = "Digite o código da moeda (ex: JPY, CAD, AUD)"
        
        # Conectar evento
        spinner_tipo.bind(text=alternar_tipo)
        
        # Popup
        popup = Popup(
            title='',
            content=main_layout,
            size_hint=(None, None),
            size=(dp(450), dp(450) if pode_adicionar_principal else dp(420)),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def validar_e_adicionar(instance):
            tipo = spinner_tipo.text
            
            if tipo == 'Moeda Principal':
                moeda = spinner_moeda.text.strip().upper()
                if not moeda or moeda not in moedas_disponiveis:
                    self.mostrar_erro("Selecione uma moeda válida!")
                    return
            else:
                moeda = input_moeda.text.strip().upper()
                if not moeda:
                    self.mostrar_erro("Digite o código da moeda!")
                    return
            
            # Validações comuns
            if len(moeda) != 3 or not moeda.isalpha():
                self.mostrar_erro("Moeda deve ter 3 letras (ex: USD, EUR, JPY)")
                return
            
            # Verificação aprimorada para moeda já existente
            if moeda in moedas_existentes:
                # Buscar detalhes da conta existente
                conta_existente = None
                for conta in contas_cliente:
                    if conta['moeda'] == moeda:
                        conta_existente = conta
                        break
                
                # Construir mensagem detalhada
                if conta_existente:
                    saldo = conta_existente.get('saldo', 0)
                    data_criacao = conta_existente.get('data_criacao', 'data desconhecida')
                    
                    mensagem_erro = (
                        f" CONTA JÁ EXISTE!\n\n"
                        f" Moeda: {moeda}\n"
                        f" Saldo atual: {saldo:,.2f}\n"
                        f" Criada em: {data_criacao}\n\n"
                        f" Não é possível ter duas contas na mesma moeda."
                    )
                else:
                    mensagem_erro = f" O cliente já possui uma conta em {moeda}!"
                
                self.mostrar_erro(mensagem_erro)
                return
            
            # Verificação extra: moeda principal como personalizada
            if tipo == 'Moeda Personalizada' and moeda in moedas_principais:
                if moeda not in moedas_disponiveis:
                    self.mostrar_erro(
                        f" {moeda} é uma moeda principal!\n\n"
                        f"Esta moeda não está disponível porque:\n"
                        f"• O cliente já possui conta em {moeda}, OU\n"
                        f"• Use a opção 'Moeda Principal' para adicioná-la"
                    )
                    return
            
            # Validar saldo
            try:
                saldo = float(input_saldo.text)
                if saldo < 0:
                    raise ValueError("Saldo não pode ser negativo")
            except ValueError as e:
                self.mostrar_erro(f" Saldo inválido!\n\n{e}\n\nDigite um número positivo (ex: 1000.00)")
                return
            except Exception:
                self.mostrar_erro(" Saldo inválido!\n\nDigite um número válido (ex: 1000.00)")
                return
            
            # Tudo validado, adicionar conta
            self._executar_adicionar_conta_supabase(moeda, saldo)
            popup.dismiss()

        def cancelar(instance):
            popup.dismiss()

        btn_adicionar.bind(on_press=validar_e_adicionar)
        btn_cancelar.bind(on_press=cancelar)

        popup.open()

    def _executar_adicionar_conta_supabase(self, moeda, saldo_inicial):
        """Executa a adição de nova conta no Supabase - VERSÃO FINAL"""
        try:
            sistema = App.get_running_app().sistema
            username = self.username_cliente
            nome_cliente = self.dados_cliente.get('nome', username)
            
            print(f" ADIÇÃO DE CONTA - Iniciando...")
            print(f"    Usuário: {username}")
            print(f"    Moeda: {moeda}")
            print(f"    Saldo inicial: {saldo_inicial:,.2f}")
            
            conta_numero = None
            
            # 🔥 ETAPA 1: Tentar criar no Supabase primeiro
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print(f" ETAPA 1 - Criando conta no Supabase...")
                    
                    # Usar método do sistema se existir
                    if hasattr(sistema, 'criar_conta_supabase_direta'):
                        conta_numero = sistema.criar_conta_supabase_direta(
                            username,
                            nome_cliente,
                            moeda,
                            saldo_inicial
                        )
                    
                    if conta_numero:
                        print(f"    Conta {conta_numero} criada no Supabase")
                    else:
                        print(f"    Método criar_conta_supabase_direta não disponível ou falhou")
                        
                except Exception as e:
                    print(f" Erro ao criar conta no Supabase: {e}")
            
            # 🔥 ETAPA 2: Se Supabase falhou, criar localmente
            if not conta_numero:
                print(f" ETAPA 2 - Criando conta localmente (fallback)...")
                conta_numero = self._executar_adicionar_conta_local(
                    moeda, 
                    saldo_inicial, 
                    return_id=True
                )
            
            if conta_numero:
                # 🔥 ETAPA 3: Atualizar cache local
                print(f" ETAPA 3 - Atualizando cache local...")
                self._atualizar_cache_local_apos_criacao(
                    sistema, username, conta_numero, 
                    moeda, saldo_inicial, nome_cliente
                )
                
                # 🔥 Mensagem de sucesso
                fonte = "no Supabase" if hasattr(sistema, 'supabase') and sistema.supabase.conectado else "localmente"
                self.mostrar_sucesso(
                    f" Conta criada com sucesso!\n\n"
                    f" Nova conta: {conta_numero}\n"
                    f" Moeda: {moeda}\n"
                    f" Saldo inicial: {saldo_inicial:,.2f}\n\n"
                    f" Criada {fonte}"
                )
                
                # 🔥 ETAPA 4: Recarregar lista
                print(f" ETAPA 4 - Recarregando lista de contas...")
                self.carregar_contas_cliente_supabase(username)
            else:
                self.mostrar_erro(" Falha ao criar conta no sistema")
                    
        except Exception as e:
            print(f" ERRO CRÍTICO ao adicionar conta: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao adicionar conta: {str(e)}")

    def _executar_adicionar_conta_local(self, moeda, saldo_inicial, return_id=False):
        """Fallback: adiciona conta localmente"""
        sistema = App.get_running_app().sistema
        
        try:
            # Gerar número único para conta
            conta_numero = str(random.randint(100000000, 999999999))
            while conta_numero in sistema.contas:
                conta_numero = str(random.randint(100000000, 999999999))
            
            # Criar conta localmente
            sistema.contas[conta_numero] = {
                'moeda': moeda,
                'saldo': saldo_inicial,
                'cliente': self.username_cliente,
                'cliente_nome': sistema.usuarios[self.username_cliente]['nome'],
                'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            
            # Adicionar conta ao usuário
            if 'contas' not in sistema.usuarios[self.username_cliente]:
                sistema.usuarios[self.username_cliente]['contas'] = []
            
            if conta_numero not in sistema.usuarios[self.username_cliente]['contas']:
                sistema.usuarios[self.username_cliente]['contas'].append(conta_numero)
            
            # Salvar dados localmente
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            
            print(f" Conta {conta_numero} criada localmente")
            
            if return_id:
                return conta_numero
            else:
                self.mostrar_sucesso(
                    f" Conta adicionada LOCALMENTE!\n\n"
                    f" Nova conta: {conta_numero}\n"
                    f" Moeda: {moeda}\n"
                    f" Saldo inicial: {saldo_inicial:,.2f}\n\n"
                    f" Atenção: Criado apenas localmente (Supabase offline)"
                )
                
                # Recarregar contas
                self.carregar_contas_cliente_supabase(self.username_cliente)
                
        except Exception as e:
            print(f" Erro ao adicionar conta local: {e}")
            if return_id:
                return None
            else:
                self.mostrar_erro(f"Erro ao adicionar conta local: {str(e)}")

    def _atualizar_cache_local_apos_criacao(self, sistema, username, conta_numero, moeda, saldo_inicial, nome_cliente):
        """Atualiza cache local após criar conta"""
        try:
            # Atualizar cache de contas
            if conta_numero not in sistema.contas:
                sistema.contas[conta_numero] = {
                    'moeda': moeda,
                    'saldo': saldo_inicial,
                    'cliente': username,
                    'cliente_nome': nome_cliente,
                    'data_criacao': datetime.datetime.now().strftime('%Y-%m-%d')
                }
            
            # Atualizar lista de contas do usuário
            if username in sistema.usuarios:
                if 'contas' not in sistema.usuarios[username]:
                    sistema.usuarios[username]['contas'] = []
                
                if conta_numero not in sistema.usuarios[username]['contas']:
                    sistema.usuarios[username]['contas'].append(conta_numero)
            
            # Salvar localmente
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            
            print(f" Cache local atualizado para conta {conta_numero}")
            
        except Exception as e:
            print(f" Erro ao atualizar cache local: {e}")

    def obter_moedas_disponiveis(self):
        """Retorna as moedas que o cliente ainda não possui"""
        contas_existentes = self.obter_contas_cliente_supabase_ou_local(self.username_cliente)
        moedas_existentes = [conta['moeda'] for conta in contas_existentes]
        
        # Moedas suportadas pelo sistema
        sistema = App.get_running_app().sistema
        todas_moedas = sistema.configuracoes.get('sistema', {}).get('moedas_suportadas', ['USD', 'EUR', 'GBP', 'BRL'])
        
        moedas_disponiveis = [moeda for moeda in todas_moedas if moeda not in moedas_existentes]
        
        return moedas_disponiveis

    def resetar_senha(self):
        """Reseta a senha do cliente no Supabase"""
        self.mostrar_confirmacao(
            "Resetar Senha",
            f"Deseja resetar a senha do cliente {self.username_cliente}?\n\n"
            f"A nova senha será: cliente123\n"
            f"O cliente deverá alterar esta senha no primeiro acesso.",
            self._executar_reset_senha_supabase
        )

    def _executar_reset_senha_supabase(self):
        """Executa o reset da senha no Supabase"""
        try:
            sistema = App.get_running_app().sistema
            
            # Nova senha
            nova_senha = "cliente123"
            senha_hash = sistema.hash_senha(nova_senha)
            
            # 🔥 PRIORIDADE: Atualizar no Supabase
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                response = sistema.supabase.client.table('usuarios')\
                    .update({'senha_hash': senha_hash})\
                    .eq('username', self.username_cliente)\
                    .execute()
                
                if response.data:
                    print(f"Senha resetada no Supabase para {self.username_cliente}")
            
            # 🔥 FALLBACK: Atualizar localmente também
            if self.username_cliente in sistema.usuarios:
                sistema.usuarios[self.username_cliente]['senha'] = senha_hash
                sistema.salvar_usuarios()
            
            self.mostrar_sucesso(
                f" Senha resetada com sucesso!\n\n"
                f" Nova senha: {nova_senha}\n\n"
                f"Informe ao cliente a nova senha."
            )
            
        except Exception as e:
            print(f" Erro ao resetar senha: {e}")
            self.mostrar_erro(f"Erro ao resetar senha: {str(e)}")

    def excluir_cliente(self):
        """Exclui completamente o cliente (PRESERVANDO TRANSFERÊNCIAS)"""
        contas = self.obter_contas_cliente_supabase_ou_local(self.username_cliente)
        total_contas = len(contas)
        total_saldo = sum(conta['saldo'] for conta in contas)
        
        self.mostrar_confirmacao(
            "EXCLUIR CLIENTE - PRESERVAR HISTÓRICO",
            f"ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\n"
            f"Cliente: {self.username_cliente}\n"
            f"Nome: {self.dados_cliente['nome']}\n"
            f"Contas: {total_contas}\n"
            f"Saldo total: {total_saldo:,.2f}\n\n"
            f"SERÃO EXCLUÍDOS:\n"
            f"- Todos os dados pessoais do cliente\n"
            f"- Acesso do cliente ao sistema\n"
            f"- Beneficiários cadastrados\n"
            f"- Configurações personalizadas\n\n"
            f"SERÃO PRESERVADOS:\n"
            f"- Todas as transferências (histórico contábil)\n"
            f"- Contas marcadas como inativas\n"
            f"- Registros de auditoria\n\n"
            f"Confirma a exclusão?",
            self._executar_exclusao_cliente_supabase
        )

    def _executar_exclusao_cliente_supabase(self):
        """Executa a exclusão completa do cliente PRESERVANDO TRANSFERÊNCIAS"""
        try:
            sistema = App.get_running_app().sistema
            
            # Usar o novo método que preserva transferências
            sucesso, mensagem = sistema.excluir_cliente_preservando_transferencias(
                self.username_cliente
            )
            
            if sucesso:
                self.mostrar_sucesso(
                    f" Cliente excluído com sucesso!\n\n"
                    f" Cliente: {self.username_cliente}\n"
                    f" Nome: {self.dados_cliente['nome']}\n\n"
                    f" ATENÇÃO IMPORTANTE:\n"
                    f"• Contas foram desativadas\n"
                    f"• Dados pessoais foram removidos\n"
                    f"• Transferências FORAM PRESERVADAS\n"
                    f"  (para histórico contábil e auditoria)"
                )
                
                # Voltar para tela anterior
                self.voltar()
            else:
                self.mostrar_erro(mensagem)
                
        except Exception as e:
            print(f" Erro ao excluir cliente: {e}")
            self.mostrar_erro(f"Erro ao excluir cliente: {str(e)}")

    def _executar_exclusao_cliente_local(self, sistema):
        """Fallback: exclui cliente localmente"""
        try:
            contas = self.obter_contas_cliente_supabase_ou_local(self.username_cliente)
            
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
                conta_envolvida = (
                    dados.get('conta_remetente') in [conta['numero'] for conta in contas] or
                    dados.get('conta_destinatario') in [conta['numero'] for conta in contas] or
                    dados.get('cliente_afetado') == self.username_cliente or
                    dados.get('solicitado_por') == self.username_cliente
                )
                
                if conta_envolvida:
                    transferencias_para_remover.append(transacao_id)
            
            for transacao_id in transferencias_para_remover:
                del sistema.transferencias[transacao_id]
            
            # 4. Remover beneficiários do cliente
            if self.username_cliente in sistema.beneficiarios:
                del sistema.beneficiarios[self.username_cliente]
            
            # 5. Salvar todos os dados localmente
            sistema.salvar_usuarios()
            sistema.salvar_contas()
            sistema.salvar_transferencias()
            sistema.salvar_beneficiarios()
            
        except Exception as e:
            print(f" Erro ao excluir localmente: {e}")
            raise e

    def mostrar_confirmacao_exclusao(self, username, nome_cliente, total_contas, total_saldo):
        """Popup especial para confirmação de exclusão com muitas informações"""
        mensagem = f"""
        ATENÇÃO: Esta ação é IRREVERSÍVEL!

        CLIENTE: {username}
        NOME: {nome_cliente}
        CONTAS: {total_contas}
        SALDO TOTAL: {total_saldo:,.2f}

        SERÃO EXCLUÍDOS:
        • Todos os dados pessoais do cliente
        • Acesso do cliente ao sistema
        • Beneficiários cadastrados
        • Configurações personalizadas

        SERÃO PRESERVADOS:
        • Todas as transferências (histórico contábil)
        • Contas marcadas como inativas
        • Registros de auditoria

        Esta ação segue as melhores práticas de sistemas financeiros,
        preservando o histórico contábil para fins de auditoria e conformidade.

        Confirma a exclusão segura deste cliente?
        """
        
        self.mostrar_confirmacao(
            "EXCLUSÃO SEGURA DE CLIENTE",
            mensagem,
            self._executar_exclusao_cliente_supabase
        )

    def voltar(self):
        """Volta para a tela de gerenciar contas"""
        self.manager.current = 'gerenciar_contas'

    # ========== MÉTODOS AUXILIARES DE UI ==========

    # Na classe TelaGerenciarClienteDetalhe, substitua os métodos de popup:

    def mostrar_erro(self, mensagem):
        """Mostra popup de erro - versão simples sem Clock"""
        # Layout
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        lbl_titulo = Label(
            text='ERRO',
            font_size='18sp',
            bold=True,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=40
        )
        
        # Mensagem
        lbl_mensagem = Label(
            text=mensagem,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=1,
            text_size=(400, None),
            halign='center',
            valign='middle'
        )
        
        # Botão
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_mensagem)
        content.add_widget(btn_ok)
        
        # Popup com altura fixa (suficiente para maioria das mensagens)
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 350),  # Altura fixa de 350px
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso com altura dinâmica"""
        # Calcular altura baseada no número de linhas
        linhas = len(mensagem.split('\n'))
        altura_base = 150  # Altura base
        altura_extra = linhas * 20  # 20px por linha extra
        altura_total = min(500, altura_base + altura_extra)  # Máximo 500px
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Título
        lbl_titulo = Label(
            text='SUCESSO',
            font_size='16sp',
            bold=True,
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=None,
            height=dp(30),
            text_size=(400, None),
            halign='center'
        )
        
        # ScrollView para mensagem longa
        scroll = ScrollView(size_hint=(1, 1))
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.9, 0.9, 0.9, 1),
            font_size='14sp',
            text_size=(400, None),
            halign='center',
            valign='top',
            size_hint_y=None
        )
        
        # Ajustar altura do label baseada no conteúdo
        lbl_sucesso.bind(texture_size=lbl_sucesso.setter('size'))
        lbl_sucesso.height = max(dp(60), len(mensagem.split('\n')) * dp(20))
        
        scroll.add_widget(lbl_sucesso)
        
        # Botão OK
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(scroll)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(450), dp(altura_total)),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def mostrar_confirmacao(self, titulo, mensagem, callback_confirmar):
        """Mostra popup de confirmação com altura dinâmica"""
        # Calcular altura baseada no número de linhas
        linhas_titulo = len(titulo.split('\n'))
        linhas_mensagem = len(mensagem.split('\n'))
        altura_base = 200  # Altura base (título + botões)
        altura_extra = (linhas_titulo + linhas_mensagem) * 18  # 18px por linha
        altura_total = min(600, altura_base + altura_extra)  # Máximo 600px
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Título
        lbl_titulo = Label(
            text=titulo,
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),
            text_size=(450, None),
            halign='center'
        )
        
        # ScrollView para mensagem longa
        scroll = ScrollView(size_hint=(1, 1))
        
        lbl_mensagem = Label(
            text=mensagem,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(450, None),
            halign='center',
            valign='top',
            size_hint_y=None
        )
        
        # Ajustar altura do label baseada no conteúdo
        lbl_mensagem.bind(texture_size=lbl_mensagem.setter('size'))
        lbl_mensagem.height = max(dp(80), len(mensagem.split('\n')) * dp(20))
        
        scroll.add_widget(lbl_mensagem)
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
        
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
        content.add_widget(scroll)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(altura_total)),
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

class CardContaClienteSupabase(BoxLayout):
    """Card para exibir uma conta do cliente com ações - VERSÃO SUPABASE"""
    
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
        """Remove a conta do cliente no Supabase"""
        if self.conta['saldo'] > 0:
            self.tela_pai.mostrar_confirmacao(
                "Conta com Saldo",
                f"A conta {self.conta['numero']} possui saldo: {self.conta['saldo']:,.2f}\n\n"
                f"Deseja realmente remover esta conta?\n"
                f"O saldo será perdido!",
                lambda: self._executar_remocao_conta_supabase()
            )
        else:
            self._executar_remocao_conta_supabase()
    
    def _executar_remocao_conta_supabase(self):
        """Executa a remoção da conta no Supabase - VERSÃO FINAL CORRIGIDA"""
        try:
            sistema = App.get_running_app().sistema
            username = self.tela_pai.username_cliente
            
            # 🔥 CORREÇÃO CRÍTICA: Usar o ID correto
            # O campo 'id' na tabela 'contas' é o número da conta
            conta_id = self.conta.get('id') or self.conta.get('numero')
            
            if not conta_id:
                self.tela_pai.mostrar_erro("Erro: ID da conta não encontrado!")
                return
            
            print(f" REMOÇÃO DE CONTA - Iniciando...")
            print(f"    Usuário: {username}")
            print(f"    Conta ID: {conta_id}")
            print(f"    Moeda: {self.conta.get('moeda', 'N/A')}")
            print(f"    Saldo: {self.conta.get('saldo', 0):,.2f}")
            
            # 🔥 ETAPA 1: Remover do Supabase
            sucesso_supabase = False
            mensagem_supabase = ""
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print(f"📤 ETAPA 1 - Excluindo conta {conta_id} do Supabase...")
                    
                    # 1. Excluir a conta da tabela 'contas'
                    response_delete = sistema.supabase.client.table('contas')\
                        .delete()\
                        .eq('id', conta_id)\
                        .execute()
                    
                    if response_delete.data:
                        print(f"    Conta {conta_id} excluída da tabela 'contas'")
                        
                        # 2. Atualizar lista de contas do usuário
                        print(f"    ETAPA 2 - Atualizando lista de contas do usuário...")
                        sucesso_atualizacao = sistema.supabase.atualizar_contas_usuario_supabase(username, conta_id)
                        
                        if sucesso_atualizacao:
                            sucesso_supabase = True
                            mensagem_supabase = "do Supabase"
                            print(f"    Lista de contas atualizada no Supabase")
                        else:
                            mensagem_supabase = "do Supabase (mas falha na atualização da lista)"
                            print(f"    Conta excluída, mas falha ao atualizar lista de contas")
                    else:
                        print(f"    Nenhuma conta encontrada para excluir (pode já ter sido excluída)")
                        
                except Exception as e:
                    print(f" Erro ao remover conta do Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    mensagem_supabase = "apenas localmente (erro no Supabase)"
            else:
                mensagem_supabase = "apenas localmente (Supabase offline)"
                print(f" Supabase não disponível, removendo apenas localmente")
            
            # 🔥 ETAPA 2: Sempre remover localmente
            print(f" ETAPA 3 - Removendo conta localmente...")
            self._executar_remocao_conta_local(sistema)
            
            # 🔥 Mensagem final
            mensagem = f" Conta removida com sucesso!\n\n"
            mensagem += f" Conta: {conta_id}\n"
            mensagem += f" Moeda: {self.conta.get('moeda', 'N/A')}\n"
            mensagem += f" Saldo perdido: {self.conta.get('saldo', 0):,.2f}\n\n"
            
            if sucesso_supabase:
                mensagem += f" Status: Removida {mensagem_supabase}"
            else:
                mensagem += f" Status: {mensagem_supabase}"
            
            self.tela_pai.mostrar_sucesso(mensagem)
            
            # 🔥 ETAPA 4: Recarregar a lista de contas
            print(f" ETAPA 4 - Recarregando lista de contas...")
            self.tela_pai.carregar_contas_cliente_supabase(username)
            
        except Exception as e:
            print(f" ERRO CRÍTICO ao remover conta: {e}")
            import traceback
            traceback.print_exc()
            self.tela_pai.mostrar_erro(f"Erro crítico ao remover conta: {str(e)}")

    def _executar_remocao_conta_local(self, sistema):
        """Fallback: remove conta localmente - VERSÃO CORRIGIDA"""
        try:
            username = self.tela_pai.username_cliente
            
            # 🔥 CORREÇÃO: Usar o mesmo ID em todos os lugares
            conta_id = self.conta.get('id') or self.conta['numero']
            
            print(f" Removendo conta localmente: {conta_id}")
            
            # Remover conta do sistema local
            if conta_id in sistema.contas:
                del sistema.contas[conta_id]
                print(f" Conta {conta_id} removida do cache local")
            else:
                print(f" Conta {conta_id} não encontrada no cache local")
            
            # Remover conta do usuário local
            if username in sistema.usuarios and 'contas' in sistema.usuarios[username]:
                contas_antes = len(sistema.usuarios[username]['contas'])
                sistema.usuarios[username]['contas'] = [
                    conta for conta in sistema.usuarios[username]['contas'] 
                    if conta != conta_id  # 🔥 Usar conta_id aqui também
                ]
                contas_depois = len(sistema.usuarios[username]['contas'])
                print(f" Conta removida do usuário: {contas_antes} → {contas_depois} contas")
            
            # Salvar dados localmente
            sistema.salvar_contas()
            sistema.salvar_usuarios()
            print(f" Dados locais salvos")
            
        except Exception as e:
            print(f" Erro ao remover conta local: {e}")
            raise e

    def _atualizar_contas_usuario_supabase_direto(self, supabase_manager, username, conta_id_remover=None):
        """Atualiza lista de contas do usuário diretamente (fallback)"""
        try:
            print(f" Atualizando contas do usuário {username} no Supabase...")
            
            # Buscar todas as contas atuais do usuário
            response = supabase_manager.client.table('contas')\
                .select('id')\
                .eq('cliente_username', username)\
                .execute()
            
            if response.data:
                # Filtrar contas (exceto a que está sendo removida)
                contas_ativas = [conta['id'] for conta in response.data 
                            if conta['id'] != conta_id_remover]
                
                print(f" Usuário {username} tem {len(contas_ativas)} contas ativas: {contas_ativas}")
                
                # Atualizar campo 'contas' do usuário
                response_update = supabase_manager.client.table('usuarios')\
                    .update({'contas': contas_ativas})\
                    .eq('username', username)\
                    .execute()
                
                if response_update.data:
                    print(f" Lista de contas atualizada no Supabase para {username}")
                else:
                    print(f" Nenhum dado retornado ao atualizar contas do usuário")
            else:
                print(f" Nenhuma conta encontrada para {username}, atualizando com lista vazia")
                
                # Atualizar com lista vazia
                supabase_manager.client.table('usuarios')\
                    .update({'contas': []})\
                    .eq('username', username)\
                    .execute()
                    
        except Exception as e:
            print(f" Erro ao atualizar contas do usuário no Supabase: {e}")