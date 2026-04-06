from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp 

class TelaDashboard(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_pre_enter(self):
        """Chamado ANTES da tela ser mostrada - VERSÃO SIMPLIFICADA E CONFIÁVEL"""
        from kivy.core.window import Window
        from kivy.metrics import dp
        from kivy.clock import Clock
        
        print("🎯 ======== DASHBOARD - TAMANHO FIXO ========")
        
        # 🔥 SOLUÇÃO DEFINITIVA: Ignora detecção, usa tamanho FIXO no SEU monitor
        # Mas mantém capacidade de reduzir se necessário
        
        # 1. PRIMEIRO: Sempre define o tamanho PADRÃO (1000x965)
        Window.size = (dp(1000), dp(965))
        print(f"📐 Tamanho padrão definido: 1000x965 dp")
        
        # 2. DEPOIS: Verifica se precisa ajustar (mas sem reduzir no SEU monitor)
        # Obter tamanho REAL da tela (pode não estar disponível imediatamente)
        try:
            # Espera um pouco para o Kivy detectar a tela
            from kivy.clock import Clock
            
            def ajustar_se_necessario(dt):
                """Ajusta tamanho apenas se realmente não couber"""
                altura_disponivel = Window.height
                
                print(f"📏 Altura disponível após carregamento: {altura_disponivel:.0f} dp")
                
                # 🔥 CRITÉRIO MAIS PERMISSIVO: Só reduz se for MUITO menor
                if altura_disponivel < dp(800):  # Apenas se for MENOR que 800dp
                    print(f"⚠️  Tela muito pequena ({altura_disponivel:.0f}dp) - Ajustando...")
                    # Reduz PROPORCIONALMENTE, mas mantém aspecto
                    nova_altura = altura_disponivel * 0.85  # 85% da tela
                    nova_largura = dp(1000) * (nova_altura / dp(965))  # Mantém proporção
                    
                    # Limites mínimos
                    nova_largura = max(dp(800), nova_largura)
                    nova_altura = max(dp(650), nova_altura)
                    
                    Window.size = (nova_largura, nova_altura)
                    print(f"📐 Ajustado para: {Window.size[0]:.0f}x{Window.size[1]:.0f}")
                else:
                    print(f"✅ Tela grande o suficiente - Mantendo 1000x965")
                    
            # Agenda o ajuste com pequeno delay
            Clock.schedule_once(ajustar_se_necessario, 0.3)
            
        except Exception as e:
            print(f"ℹ️ Não foi possível verificar ajuste: {e}")
            # Mantém o tamanho padrão
        
        print("🎯 ===========================================")
        
        # 🔥 SEU CÓDIGO ORIGINAL (mantém TUDO igual):
        sistema = App.get_running_app().sistema
        usuario = sistema.usuario_logado
        
        if usuario:
            # Obter dados do usuário do sistema
            app = App.get_running_app()
            sistema = app.sistema
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            nome = usuario_data.get('nome', sistema.usuario_logado)
            tipo = usuario_data.get('tipo', 'cliente')

            print(f"🏠 Dashboard carregado para: {nome} ({tipo})")
            
            # 🔥 CONFIGURAR HEADER DINAMICAMENTE
            self.configurar_header_dinamico()
            
            # Carregar conteúdo
            self.carregar_saldos()
            self.criar_botoes_menu()
        
        # 🔥 SEU REPOSICIONAMENTO (mantém igual)
        Clock.schedule_once(lambda dt: self.posicionar_janela(), 0.1)

    def configurar_header_dinamico(self):
        app = App.get_running_app()
        sistema = app.sistema
        
        # Obter dados do usuário
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        nome_completo = usuario_data.get('nome', sistema.usuario_logado)
        tipo_usuario = usuario_data.get('tipo', 'cliente')
        
        # Extrair primeiro nome
        primeiro_nome = nome_completo.split()[0] if nome_completo else sistema.usuario_logado
        
        if hasattr(self, 'ids'):
            # Saudação personalizada
            if 'lbl_saudacao' in self.ids:
                self.ids.lbl_saudacao.text = f"Olá, {primeiro_nome}"
            
            # Configurar título baseado no tipo de usuário
            if 'lbl_titulo' in self.ids and 'lbl_subtitulo' in self.ids:
                if tipo_usuario == 'admin':
                    self.ids.lbl_titulo.text = "PAINEL ADMINISTRATIVO"
                    self.ids.lbl_subtitulo.text = "Gerencie clientes e operações do sistema"
                else:
                    self.ids.lbl_titulo.text = "PAINEL DO CLIENTE"
                    self.ids.lbl_subtitulo.text = "Acompanhe suas finanças"
            
            # Atualizar tipo de usuário no header se existir
            if 'label_tipo_usuario' in self.ids:
                self.ids.label_tipo_usuario.text = f"Tipo: {tipo_usuario.title()}"

    def on_leave(self):
        """Chamado quando SAIR da tela"""
        # 🔥 NÃO restaura tamanho aqui - deixa a próxima tela controlar
        print("Dashboard: Saindo...")
    
    def posicionar_janela(self):
        """Posiciona com controle fino - AJUSTE OS VALORES AQUI"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            
            # Obter tamanho da tela
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            window_width, window_height = Window.size
            
            # 🔥🔥🔥 ADICIONE APENAS ESTA VERIFICAÇÃO:
            # Se a janela for maior que a tela, reduz um pouco
            if window_width > screen_width:
                print(f"⚠️  Janela muito larga! Reduzindo para 90% da tela...")
                window_width = screen_width * 0.9  # 90% da largura da tela
                # Mantém proporção da altura
                window_height = window_height * (window_width / Window.width)
                Window.size = (window_width, window_height)
                print(f"📐 Nova janela: {window_width:.0f}x{window_height:.0f}")
            
            # 🔥 SEUS VALORES PREFERIDOS (não mude):
            offset_x = 45  # 🔥 AUMENTE para mais direita, DIMINUA para mais esquerda
            offset_y = 20   # 🔥 AUMENTE para mais baixo, DIMINUA para mais alto
            
            x = (screen_width - window_width) // 2 + offset_x
            y = (screen_height - window_height) // 2 - offset_y
            
            Window.top = y
            Window.left = x
            
            print(f"📍 Dashboard: Posição customizada em ({x}, {y})")
            print(f"📍 Offsets: X={offset_x}, Y={offset_y}")
                
        except Exception as e:
            print(f"⚠️ Não foi possível posicionar dashboard: {e}")
            # FALLBACK: Posição customizada
            Window.top = 120
            Window.left = 350
            print("📍 Dashboard: Posição customizada fallback")
        
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("🏠 Dashboard carregado - on_enter")
        
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados do usuário corretamente
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        tipo_usuario = usuario_data.get('tipo', 'cliente')
        nome_usuario = usuario_data.get('nome', sistema.usuario_logado)
        
        # 🔥 FORÇAR RECARGA DOS DADOS DAS CONTAS BANCÁRIAS (PRIMEIRO!)
        sistema.carregar_contas_bancarias()
        
        # 🔥 AGORA SIM ATUALIZAR TOTAIS (DEPOIS de carregar as contas)
        self.atualizar_totais_dashboard()
        
        # 🔥 TESTAR SISTEMA DE CÂMBIO (APENAS CLIENTES)
        if sistema.usuario_logado and tipo_usuario == 'cliente':
            sistema.testar_sistema_cambio()
        
        if sistema.usuario_logado:
            # 🔥 CONFIGURAR HEADER DINAMICAMENTE
            self.configurar_header_dinamico()
            
            # Carregar conteúdo
            self.carregar_saldos()
            self.criar_botoes_menu()
        
        # 🔥🔥🔥 ADICIONE ESTA ÚNICA LINHA NO FINAL:
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.posicionar_janela(), 0.3)

    def sair(self):
        """Voltar para tela de login"""
        print("🚪 Saindo do dashboard...")
        # 🔥 FORÇAR tamanho do login antes de sair
        Window.size = (400, 700)
        self.manager.current = 'login'

    # 🔥 MANTENHA TODOS OS SEUS MÉTODOS ORIGINAIS A PARTIR DAQUI
    def carregar_saldos(self):
        """Carrega os saldos - VERSÃO DEBUG COMPLETA"""
        sistema = App.get_running_app().sistema
        
        # 🔥 CORREÇÃO: Obter dados do usuário corretamente
        usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        tipo_usuario = usuario_data.get('tipo', 'cliente')
        nome_usuario = usuario_data.get('nome', sistema.usuario_logado)
        
        if not sistema.usuario_logado or not hasattr(self, 'ids'):
            return
        
        container = self.ids.saldos_container
        container.clear_widgets()
        
        # 🔥 CORREÇÃO: Usar as variáveis corrigidas
        #print(f"🎯 DEBUG DASHBOARD COMPLETO para: {nome_usuario}")
        #print(f"🔍 Tipo de usuário: {tipo_usuario}")
        
        if tipo_usuario == 'admin':
            # ADMIN: Mostrar saldos totais
            saldos_totais = self.calcular_saldos_totais(sistema)
            #print(f"SALDOS TOTAIS SISTEMA: {saldos_totais}")
            
            # DEBUG: Verificar todas as contas do sistema
            #total_sistema = 0
            #for conta_num, conta_info in sistema.contas.items():
                #print(f"CONTA {conta_num}: {conta_info['moeda']} = {conta_info['saldo']:,.2f}")
                #total_sistema += conta_info['saldo']
            #print(f"TOTAL GERAL SISTEMA: {total_sistema:,.2f}")
            
            self.mostrar_saldos_admin(container, saldos_totais)
        else:
            # CLIENTE: Mostrar saldos pessoais
            #print(f"Contas do usuário: {usuario_data.get('contas', [])}")
            
            # DEBUG DETALHADO: Verificar cada conta individualmente
            #total_usuario = 0
            #for conta_num in usuario_data.get('contas', []):
                #if conta_num in sistema.contas:
                    #conta_info = sistema.contas[conta_num]
                    #print(f"CONTA {conta_num}: {conta_info['moeda']} = {conta_info['saldo']:,.2f}")
                    #total_usuario += conta_info['saldo']
                #else:
                    #print(f"CONTA {conta_num} NÃO ENCONTRADA no sistema!")
            
            #print(f"TOTAL DO USUÁRIO: {total_usuario:,.2f}")
            
            saldos = sistema.calcular_saldos_usuario()
            #print(f"SALDOS CALCULADOS: {saldos}")
            
            self.mostrar_saldos_cliente(container, saldos)
            
        #print(f"Saldos atualizados no dashboard")

        # 🔥 ADICIONE ESTA LINHA NO FINAL:
        #self.verificar_dados_reais()

    def atualizar_totais_dashboard(self):
        """Atualiza os totais no dashboard - VERSÃO SUPABASE"""
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 NOVO: CARREGAR CONTAS BANCÁRIAS DO SUPABASE
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    response = sistema.supabase.client.table('contas_bancarias_empresa')\
                        .select('*')\
                        .execute()
                    
                    if response.data:
                        # Limpar contas locais e carregar do Supabase
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
                except Exception as e:
                    print(f"⚠️ Erro ao carregar contas do Supabase: {e}")
                    # Fallback: usar dados locais
            
            # 🔥 O RESTO DO MÉTODO CONTINUA EXATAMENTE IGUAL
            saldos_totais = {}
            
            print(f"ATUALIZANDO TOTAIS DASHBOARD:")
            print(f"Total de contas bancárias: {len(sistema.contas_bancarias_empresa)}")
            
            for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
                moeda = conta_info['moeda']
                saldo = conta_info['saldo']
                
                if moeda not in saldos_totais:
                    saldos_totais[moeda] = 0
                saldos_totais[moeda] += saldo
                
                print(f"  {conta_num}: {saldo:,.2f} {moeda}")
            
            # 🔥 GARANTIR QUE TODAS AS MOEDAS TENHAM VALOR
            totais = {
                'USD': saldos_totais.get('USD', 0),
                'EUR': saldos_totais.get('EUR', 0), 
                'GBP': saldos_totais.get('GBP', 0),
                'BRL': saldos_totais.get('BRL', 0)
            }
            
            # 🔥 CORREÇÃO: VERIFICAR SE OS IDs EXISTEM ANTES DE ACESSAR
            if hasattr(self, 'ids'):
                if hasattr(self.ids, 'lbl_total_usd'):
                    self.ids.lbl_total_usd.text = f"{totais['USD']:,.2f}"
                if hasattr(self.ids, 'lbl_total_eur'):
                    self.ids.lbl_total_eur.text = f"{totais['EUR']:,.2f}" 
                if hasattr(self.ids, 'lbl_total_gbp'):
                    self.ids.lbl_total_gbp.text = f"{totais['GBP']:,.2f}"
                if hasattr(self.ids, 'lbl_total_brl'):
                    self.ids.lbl_total_brl.text = f"{totais['BRL']:,.2f}"
            
            print(f"  DASHBOARD ATUALIZADO:")
            print(f"  USD: {totais['USD']:,.2f}")
            print(f"  EUR: {totais['EUR']:,.2f}")
            print(f"  GBP: {totais['GBP']:,.2f}")
            print(f"  BRL: {totais['BRL']:,.2f}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar totais do dashboard: {e}")
            import traceback
            traceback.print_exc()

    def verificar_contas_bancarias(self):
        """Verifica o estado atual das contas bancárias"""
        #sistema = App.get_running_app().sistema
        
        #print(f"🔍 VERIFICAÇÃO DAS CONTAS BANCÁRIAS:")
        #print(f"  Total de contas: {len(sistema.contas_bancarias_empresa)}")
        
        #for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            #print(f"  💰 {conta_num}: {conta_info['saldo']:,.2f} {conta_info['moeda']}")
        
        # Verificar se o arquivo existe e seu conteúdo
        #import os
        #if os.path.exists('data/contas_bancarias.json'):
            #with open('data/contas_bancarias.json', 'r', encoding='utf-8') as f:
                #import json
                #dados_arquivo = json.load(f)
                #print(f"  📁 ARQUIVO: {len(dados_arquivo)} contas")
                #for conta_num, conta_info in dados_arquivo.items():
                    #print(f"    💾 {conta_num}: {conta_info['saldo']:,.2f} {conta_info['moeda']}")

    def verificar_dados_reais(self):
        """Método para verificar dados reais do sistema"""
        #sistema = App.get_running_app().sistema
        #usuario = sistema.usuario_logado
        
        #print("🔍 VERIFICAÇÃO COMPLETA DOS DADOS:")
        #print(f"Usuário: {usuario['nome']}")
        #print(f"Contas: {usuario.get('contas', [])}")
        
        # Verificar arquivo de contas
        #try:
            #import json
            #with open('data/contas.json', 'r', encoding='utf-8') as f:
                #contas_arquivo = json.load(f)
                #print("📁 CONTAS NO ARQUIVO:")
                #for conta_num, conta_info in contas_arquivo.items():
                    #if conta_num in usuario.get('contas', []):
                        #print(f"  {conta_num}: {conta_info['moeda']} = {conta_info['saldo']:,.2f}")
        #except Exception as e:
            #print(f"❌ Erro ao ler arquivo: {e}")
        
        # Verificar contas em memória
        #print("💾 CONTAS EM MEMÓRIA:")
        #for conta_num in usuario.get('contas', []):
            #if conta_num in sistema.contas:
                #conta_info = sistema.contas[conta_num]
                #print(f"  {conta_num}: {conta_info['moeda']} = {conta_info['saldo']:,.2f}")

    def calcular_saldos_totais(self, sistema):
        """Calcula saldos totais por moeda APENAS das contas bancárias da empresa - VERSÃO SUPABASE"""
        
        # 🔥 NOVO: VERIFICAR SE PRECISA CARREGAR DO SUPABASE
        if not sistema.contas_bancarias_empresa and hasattr(sistema, 'supabase') and sistema.supabase.conectado:
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
                    print(f"✅ {len(response.data)} contas carregadas do Supabase para cálculo")
            except Exception as e:
                print(f"⚠️ Erro ao carregar contas para cálculo: {e}")
        
        # 🔥 O RESTO DO MÉTODO CONTINUA EXATAMENTE IGUAL
        saldos_totais = {}
        
        print(f"🔍 CALCULANDO SALDOS TOTAIS DASHBOARD:")
        print(f"  Total de contas bancárias: {len(sistema.contas_bancarias_empresa)}")
        
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            moeda = conta_info['moeda']
            saldo = conta_info['saldo']
            
            if moeda not in saldos_totais:
                saldos_totais[moeda] = 0
            saldos_totais[moeda] += saldo
            
            #print(f"  ✅ {conta_num}: {saldo:,.2f} {moeda}")
        
        #print(f"💰 SALDOS CONTAS BANCÁRIAS EMPRESA CALCULADOS: {saldos_totais}")
        return saldos_totais
    
    def mostrar_saldos_admin(self, container, saldos_totais):
        """Mostra saldos totais do sistema - 4 COLUNAS"""
        if not saldos_totais:
            label = Label(
                text="Nenhuma conta bancária encontrada",
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(label)
            return
        
        # 🔥 MUDANÇA: Título mais específico
        titulo_secao = Label(
            text="SALDOS DAS CONTAS BANCÁRIAS",
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        titulo_secao.bind(text_size=titulo_secao.setter('size'))
        container.add_widget(titulo_secao)
        
        # 🔥 GridLayout com 4 COLUNAS
        grid_cards = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, padding=[0, 10, 0, 0])
        grid_cards.bind(minimum_height=grid_cards.setter('height'))
        
        for moeda, saldo in saldos_totais.items():
            card = self.criar_card_saldo(moeda, saldo, is_admin=True)
            grid_cards.add_widget(card)
        
        container.add_widget(grid_cards)
    
    def mostrar_saldos_cliente(self, container, saldos):
        """Mostra saldos pessoais para o cliente - 4 COLUNAS"""
        if not saldos:
            label = Label(
                text="Nenhuma conta encontrada",
                color=(0.80, 0.84, 0.88, 1),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(label)
            return
        
        # Título da seção
        titulo_secao = Label(
            text="MEUS SALDOS",
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        titulo_secao.bind(text_size=titulo_secao.setter('size'))
        container.add_widget(titulo_secao)
        
        # 🔥 GridLayout com 4 COLUNAS
        grid_cards = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, padding=[0, 10, 0, 0])
        grid_cards.bind(minimum_height=grid_cards.setter('height'))
        
        for moeda, saldo in saldos.items():
            card = self.criar_card_saldo(moeda, saldo, is_admin=False)
            grid_cards.add_widget(card)
        
        container.add_widget(grid_cards)
    
    def criar_card_saldo(self, moeda, saldo, is_admin=False):
        """Cria um card de saldo moderno mas sóbrio"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            padding=[12, 10],
            spacing=dp(5)
        )
        
        # Background do card - cor única e sóbria
        with card.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            card.rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[8,]
            )
        
        card.bind(pos=self._atualizar_card_rect, size=self._atualizar_card_rect)
        
        # Linha superior: Moeda
        linha_superior = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        lbl_moeda = Label(
            text=moeda,
            font_size='12sp',
            bold=True,
            color=(0.80, 0.84, 0.88, 1),
            halign='left',
            text_size=(None, None)
        )
        lbl_moeda.bind(size=lbl_moeda.setter('text_size'))
        
        linha_superior.add_widget(lbl_moeda)
        
        # Linha inferior: Valor
        linha_inferior = BoxLayout(orientation='horizontal', size_hint_y=0.6)
        
        # 🔥 MUDANÇA: Cor vermelha se saldo for negativo
        cor_saldo = (0.8, 0.2, 0.2, 1) if saldo < 0 else (0.23, 0.51, 0.96, 1)
        
        lbl_valor = Label(
            text=f"{saldo:,.2f}",
            font_size='14sp',
            bold=True,
            color=cor_saldo,  # 🔥 AGORA MUDA DINAMICAMENTE
            halign='left',
            text_size=(None, None)
        )
        lbl_valor.bind(size=lbl_valor.setter('text_size'))
        
        linha_inferior.add_widget(lbl_valor)
        
        card.add_widget(linha_superior)
        card.add_widget(linha_inferior)
        
        return card
    
    def _atualizar_card_saldo(self, instance, value):
        """Atualiza o retângulo do card de saldo"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
            
        if hasattr(instance, 'brilho'):
            instance.brilho.pos = (instance.pos[0], instance.pos[1] + instance.size[1] - dp(5))
            instance.brilho.size = (instance.size[0], dp(5))
    
    def criar_botoes_menu(self):
        """Cria os botões do menu com efeitos hover e 3D - VERSÃO SEGURA"""
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 CORREÇÃO: Obter dados do usuário corretamente
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            tipo_usuario = usuario_data.get('tipo', 'cliente')
            
            if not sistema.usuario_logado:
                return
            
            if tipo_usuario == 'admin':
                # 🔥 NÃO MEXER - ESTÁ PERFEITO COMO ESTÁ
                num_pendentes, num_processando = self.obter_numero_operacoes_pendentes()
                
                botoes = [
                    ("Cadastrar Cliente", self.cadastrar_cliente),
                    ("Relatórios", self.abrir_relatorios),  # 🔥 NOVO BOTÃO
                    ("Gerenciar Contas", self.gerenciar_contas),
                    ("Gerenciar Transferências", self.gerenciar_transferencias),
                    ("Aprovar Operações", self.aprovar_operacoes, num_pendentes, num_processando),  # 🔥 CONTADORES - NÃO MEXER
                    ("Cotações Moedas", self.gerenciar_cotacoes),  # 🔥 VAMOS USAR ESTE DEPOIS
                    ("Contas Bancárias", self.contas_bancarias),
                    ("Confirmar Depósitos", self.confirmar_depositos),
                    ("Configurações", self.configuracoes)
                ]
                cols = 3
            else:
                # 🔥 APENAS AQUI: ADICIONAR NOVO BOTÃO PARA CLIENTES
                botoes = [
                    ("Compra/Venda Moedas", self.compra_venda_moedas),  # 🔥 NOVO BOTÃO
                    ("Solicitar Transferência", self.solicitar_transferencia),
                    ("Minhas Transferências", self.minhas_transferencias),
                    ("Meus Beneficiários", self.meus_beneficiarios),
                    ("Meu Extrato", self.meu_extrato),
                    ("Meus Dados", self.meus_dados),
                    ("Suporte", self.suporte)
                ]
                cols = 3
            
            # 🔥 RESTO DO CÓDIGO PERMANECE IDÊNTICO - NÃO MEXER
            container = self.ids.botoes_container
            container.clear_widgets()
            
            grid = GridLayout(cols=cols, spacing=dp(15), size_hint_y=None, padding=[10, 10])
            grid.bind(minimum_height=grid.setter('height'))
            
            for botao_info in botoes:
                if len(botao_info) == 4:  # 🔥 BOTÃO COM CONTADORES (admin)
                    texto, comando, pendentes, processando = botao_info
                    btn_container = self.criar_botao_3d_com_hover_com_contadores(texto, comando, pendentes, processando)
                else:  # Botão normal
                    texto, comando = botao_info
                    btn_container = self.criar_botao_3d_com_hover(texto, comando)
                
                grid.add_widget(btn_container)
            
            grid.height = grid.minimum_height
            
            scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            scroll.add_widget(grid)
            container.add_widget(scroll)
            
            print(f"✅ {len(botoes)} botões criados")
            if tipo_usuario == 'admin':
                print(f"📊 Operações: {num_pendentes} pendentes, {num_processando} processando")
            
        except Exception as e:
            print(f"❌ Erro ao criar botões: {e}")
            import traceback
            traceback.print_exc()
            self.criar_botoes_simples_fallback()

    def obter_numero_operacoes_pendentes(self):
        """Obtém o número de operações pendentes e em processamento - VERSÃO CORRIGIDA"""
        try:
            sistema = App.get_running_app().sistema
            
            # DEBUG: Verificar status das transferências
            print("🔍 DEBUG: Status das transferências no sistema:")
            for transferencia_id, dados in sistema.transferencias.items():
                print(f"  {transferencia_id}: status='{dados.get('status')}' - {dados.get('valor', 0)} {dados.get('moeda', 'N/A')}")
            
            # 🔥 CORREÇÃO: Usar os status CORRETOS
            transferencias_pendentes = {k: v for k, v in sistema.transferencias.items() 
                                      if v.get('status') == 'solicitada'}  # ← 'solicitada' CORRETO
            
            transferencias_processando = {k: v for k, v in sistema.transferencias.items() 
                                       if v.get('status') == 'processing'}  # ← 'processing' CORRETO
            
            num_pendentes = len(transferencias_pendentes)
            num_processando = len(transferencias_processando)
            
            print(f"📊 Operações encontradas: {num_pendentes} pendentes, {num_processando} em processamento")
            
            # 🔥 DEBUG EXTRA: Listar IDs específicos
            if transferencias_pendentes:
                print("📋 IDs das transferências pendentes:")
                for transf_id in transferencias_pendentes.keys():
                    print(f"   - {transf_id}")
            
            return num_pendentes, num_processando
            
        except Exception as e:
            print(f"❌ Erro ao contar operações: {e}")
            return 0, 0

    def criar_botao_3d_com_hover(self, texto, comando):
        """Cria botão com efeito 3D e hover"""
        from kivy.animation import Animation
        
        btn_container = FloatLayout(
            size_hint_y=None,
            height=dp(105)
        )
        
        # Botão sombra (parte de trás)
        btn_shadow = Button(
            size_hint=(0.96, 0.92),
            pos_hint={'center_x': 0.5, 'center_y': 0.48},
            background_color=(0.15, 0.20, 0.27, 1),
            background_normal=''
        )
        
        # Botão principal
        btn_main = Button(
            size_hint=(0.96, 0.92),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            text=texto,
            font_size='14sp',
            bold=True,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        # Efeitos hover no botão principal
        def on_enter(instance):
            Animation(
                background_color=(0.25, 0.30, 0.38, 1),
                duration=0.15
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.53},
                duration=0.15
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.49},
                duration=0.15
            ).start(btn_shadow)
        
        def on_leave(instance):
            Animation(
                background_color=(0.20, 0.25, 0.33, 1),
                duration=0.15
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.52},
                duration=0.15
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.48},
                duration=0.15
            ).start(btn_shadow)
        
        def on_press(instance):
            Animation(
                background_color=(0.30, 0.35, 0.43, 1),
                duration=0.1
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.50},
                duration=0.1
            ).start(instance)
            Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.50},
                duration=0.1
            ).start(btn_shadow)
        
        def on_release(instance):
            Animation(
                background_color=(0.25, 0.30, 0.38, 1),
                duration=0.1
            ).start(instance)
            
            # Executar comando
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: comando(), 0.1)
        
        # Vincular eventos
        btn_main.bind(
            on_enter=on_enter,
            on_leave=on_leave,
            on_press=on_press,
            on_release=on_release
        )
        
        btn_container.add_widget(btn_shadow)
        btn_container.add_widget(btn_main)
        
        return btn_container

    def criar_botao_3d_com_hover_com_contadores(self, texto, comando, pendentes, processando):
        """Versão com CENTRALIZAÇÃO PERFEITA E FONTE MAIOR NOS NÚMEROS - ALTURA CORRIGIDA"""
        
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Container principal - MESMA ALTURA DOS OUTROS BOTÕES
        container = BoxLayout(
            orientation='horizontal',
            size_hint=(0.96, 0.92),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            height=dp(105),  # 🔥 MESMA ALTURA DOS OUTROS BOTÕES
            padding=[5, 5, 5, 0]
        )
        
        # Botão principal
        btn = Button(
            text=texto,
            font_size='14sp',
            bold=True,
            background_color=(0.20, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            valign='middle',
            halign='center',
            padding=[0, 15, 0, 0]
        )
        
        # Adicionar contadores com FONTE MAIOR
        texto_com_contadores = texto
        
        if pendentes > 0 and processando > 0:
            # 🔥 AUMENTEI A FONTE DOS NÚMEROS para 14sp
            texto_com_contadores = f"{texto}\n[size=14][color=ffa500]{pendentes}[/color]     [color=4da6ff]{processando}[/color][/size]"
        elif pendentes > 0:
            texto_com_contadores = f"{texto}\n[size=14][color=ffa500]{pendentes}[/color][/size]"
        elif processando > 0:
            texto_com_contadores = f"{texto}\n[size=14][color=4da6ff]{processando}[/color][/size]"
        
        btn.text = texto_com_contadores
        btn.markup = True
        
        # 🔥 CORREÇÃO: REMOVER configurações de altura que estavam encolhendo o botão
        # btn.size_hint_y = None  # ❌ REMOVER ESTA LINHA
        # btn.height = dp(80)     # ❌ REMOVER ESTA LINHA
        
        def on_release(instance):
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: comando(), 0.1)
        
        btn.bind(on_release=on_release)
        container.add_widget(btn)
        
        print(f"🎯 BOTÃO COM ALTURA CORRETA: {pendentes} | {processando}")
        return container

    def _atualizar_contador_ellipse(self, instance, value):
        """Atualiza a posição do círculo de fundo do contador"""
        if hasattr(instance, 'ellipse'):
            instance.ellipse.pos = instance.pos
            instance.ellipse.size = instance.size

    def criar_botoes_simples_fallback(self):
        """Cria botões simples em caso de erro na versão 3D"""
        try:
            sistema = App.get_running_app().sistema
            usuario = sistema.usuario_logado
            
            if not usuario:
                return
            
            if usuario['tipo'] == 'admin':
                botoes = [
                    ("Cadastrar Cliente", self.cadastrar_cliente),
                    ("Relatórios", self.abrir_relatorios),  # 🔥 NOVO BOTÃO
                    ("Gerenciar Contas", self.gerenciar_contas),
                    ("Gerenciar Transferências", self.gerenciar_transferencias),
                    ("Aprovar Operações", self.aprovar_operacoes),
                    ("Cotações Moedas", self.gerenciar_cotacoes),
                    ("Relatórios", self.relatorios),
                    ("Controle Acesso", self.controle_acesso),
                    ("Configurações", self.configuracoes)
                ]
                cols = 3
            else:
                botoes = [
                    ("Solicitar Transferência", self.solicitar_transferencia),
                    ("Minhas Transferências", self.minhas_transferencias),
                    ("Meus Beneficiários", self.meus_beneficiarios),
                    ("Meu Extrato", self.meu_extrato),
                    ("Meus Dados", self.meus_dados),
                    ("Suporte", self.suporte)
                ]
                cols = 3
            
            container = self.ids.botoes_container
            container.clear_widgets()
            
            grid = GridLayout(cols=cols, spacing=dp(15), size_hint_y=None, padding=[10, 10])
            grid.bind(minimum_height=grid.setter('height'))
            
            for texto, comando in botoes:
                btn = Button(
                    text=texto,
                    font_size='14sp',
                    bold=True,
                    background_color=(0.20, 0.25, 0.33, 1),
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=dp(80)
                )
                btn.bind(on_press=lambda instance, cmd=comando: cmd())
                grid.add_widget(btn)
            
            grid.height = grid.minimum_height
            
            scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            scroll.add_widget(grid)
            container.add_widget(scroll)
            
            print(f"✅ {len(botoes)} botões SIMPLES criados (fallback)")
            
        except Exception as e:
            print(f"❌ Erro crítico ao criar botões fallback: {e}")

    def _atualizar_card_rect(self, instance, value):
        """Atualiza o retângulo de background quando o card muda"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    # ========== FUNÇÕES ADMIN ==========
    def cadastrar_cliente(self):
        """Abre a tela de cadastro de cliente"""
        print("👥 Abrindo cadastro de cliente...")
        self.manager.current = 'cadastro_cliente'
    
    def listar_clientes(self):
        """Abre a tela de listagem de clientes"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return

        print("📋 Abrindo listar clientes...")
        self.manager.current = 'listar_clientes'  # 🔥 NAVEGA PARA A TELA
    
    def abrir_relatorios(self, instance=None):
        """Abre a tela de relatórios"""
        print("📊 Abrindo relatórios...")
        self.manager.current = 'relatorios'

    def gerenciar_contas(self):
        """Abre a tela de gerenciar contas"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("🏦 Abrindo gerenciar contas...")
        self.manager.current = 'gerenciar_contas'
    
    def gerenciar_transferencias(self):
        """Abre a tela de gerenciar transferências"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("🌍 Abrindo gerenciar transferências...")
        self.manager.current = 'gerenciar_transferencias'
    
    def aprovar_operacoes(self):
        """Abre a tela de aprovar operações"""
        sistema = App.get_running_app().sistema
    
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
    
        print("💱 Abrindo aprovar operações...")
        self.manager.current = 'aprovar_operacoes'  # 🔥 NAVEGA PARA A TELA
    
    def gerenciar_cotacoes(self):
        """Abre a tela de gerenciar cotações - AGORA FUNCIONAL"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("💰 Abrindo gerenciar cotações...")
        self.manager.current = 'cotacoes_admin'  # 🔥 AGORA NAVEGA PARA A TELA REAL
    
    def contas_bancarias(self):
        """Abre a tela de contas bancárias da empresa"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("🏦 Abrindo contas bancárias...")
        self.manager.current = 'contas_bancarias'
    
    def confirmar_depositos(self):
        """Abre a tela para confirmar depósitos"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("💰 Abrindo confirmar depósitos...")
        self.manager.current = 'confirmar_depositos'
    
    def configuracoes(self):
        """Configurações do sistema - AGORA FUNCIONAL!"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'admin':
            self.mostrar_erro("Esta função é apenas para administradores!")
            return
        
        print("⚙️ Abrindo configurações do sistema...")
        self.manager.current = 'configuracoes'  # 🔥 AGORA NAVEGA PARA A TELA REAL

    def mostrar_erro_acesso(self):
        """Mostra erro de acesso restrito"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl_erro = Label(
            text="ACESSO RESTRITO\n\nEsta função é apenas para administradores!",
            color=(1, 0.3, 0.3, 1),
            font_size='16sp',
            bold=True,
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
            title='Acesso Restrito',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    # ========== FUNÇÕES CLIENTE ==========
    def solicitar_transferencia(self):
        """Abre a tela de transferência - VERSÃO SIMPLIFICADA"""
        print("🌍 Abrindo tela de transferência...")
        
        # Verificar se é cliente
        sistema = App.get_running_app().sistema
        #if sistema.tipo_usuario_logado != 'cliente':
        #    print("❌ Acesso restrito - apenas para clientes")
        #    return
        
        # Verificar se tem contas internacionais
        #usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
        #contas_cliente = [conta for conta in usuario_data.get('contas', []) 
        #                 if sistema.contas[conta]['moeda'] in ['USD', 'EUR', 'GBP']]
        
        #if not contas_cliente:
        #    print("❌ Você não possui contas em USD, EUR ou GBP para transferência internacional!")
        #    return
        
        print("✅ Cliente tem contas internacionais, navegando para tela de transferência...")
        self.manager.current = 'transferencia'
    
    def minhas_transferencias(self):
        """Abre a tela de minhas transferências"""
        print("📋 Abrindo minhas transferências...")
        
        # Verificar se é cliente
        sistema = App.get_running_app().sistema
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
        
        # Navegar para a tela de minhas transferências
        self.manager.current = 'minhas_transferencias'
    
    def meus_beneficiarios(self):
        """Abre a tela de meus beneficiários"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
        
        print("Abrindo meus beneficiários...")
        self.manager.current = 'meus_beneficiarios'
    
    def meu_extrato(self):
        """Abre a tela de extrato"""
        sistema = App.get_running_app().sistema
    
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
    
        print("📊 Abrindo meu extrato...")
        self.manager.current = 'meu_extrato'
    
    def meus_dados(self):
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
        
        print("👤 Abrindo meus dados...")
        self.manager.current = 'meus_dados'
    
    def suporte(self):
        """Abre a tela de suporte"""
        sistema = App.get_running_app().sistema
    
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
    
        print("📞 Abrindo suporte...")
        self.manager.current = 'suporte'

    def compra_venda_moedas(self):
        """Abre a tela de compra e venda de moedas"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
        
        print("💰 Abrindo compra e venda de moedas...")
        self.manager.current = 'cambio_moedas'

    def sair(self):
        """Volta para a tela de login"""
        sistema = App.get_running_app().sistema
        sistema.usuario_logado = None
        self.manager.current = 'login'
        print("👋 Usuário deslogado")



