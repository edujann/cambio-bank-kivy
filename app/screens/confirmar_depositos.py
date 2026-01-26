from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
import datetime

class TelaConfirmarDepositos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner_banco_origem = None  # 🔥 CORREÇÃO: Guardar referência separada

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - VERSÃO ATUALIZADA"""
        print("🎬 TelaConfirmarDepositos.on_pre_enter() - FORÇANDO RECARGA")
        
        # 🔥 FORÇAR RECARGA COMPLETA (CARREGA NOVAS CONTAS DO SUPABASE)
        self.forcar_recarga_tela()
        
        # 🔥 MANTER O DEBUG DOS SALDOS (OPCIONAL, MAS ÚTIL)
        self.debug_saldos_contas()
        
        # 🔥 MANTEM O KEYBOARD HANDLING
        from kivy.core.window import Window
        Window.unbind(on_key_down=self.on_key_down_alt)
        Window.bind(on_key_down=self.on_key_down_alt)

    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("🎬 TelaConfirmarDepositos.on_enter() - Vincular teclado")
        # Já vinculamos no on_pre_enter, então só confirmar
        pass

    def on_leave(self):
        """Chamado quando sai da tela"""
        print("🚪 TelaConfirmarDepositos.on_leave() - Desvincular teclado")
        from kivy.core.window import Window
        Window.unbind(on_key_down=self.on_key_down_alt)

    def on_keyboard(self, window, key, scancode, codepoint, modifiers):
        """Captura teclas pressionadas"""
        print(f"🔑 on_keyboard: key={key}, scancode={scancode}")
        
        # Tab key
        if key == 9:  # Tab
            print("✅ Tab capturado!")
            # Pequeno delay para evitar conflitos
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.proximo_campo(), 0.05)
            return True
        
        # Enter no último campo
        elif key == 13:  # Enter
            # Verificar se está no campo valor
            if hasattr(self, 'ids') and 'entry_valor' in self.ids and self.ids.entry_valor.focus:
                print("✅ Enter no campo valor!")
                self.confirmar_deposito()
                return True
        
        return False

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        """Captura teclas pressionadas - MÉTODO ORIGINAL DO KIVY"""
        print(f"🔑 on_key_down: key={key}, scancode={scancode}, modifiers={modifiers}")
        
        # Tab key
        if key == 9:  # Tab
            print("✅ Tab capturado via on_key_down!")
            self.proximo_campo()
            return True
        
        # Enter no último campo
        elif key == 13:  # Enter
            # Verificar se está no campo valor
            if hasattr(self, 'ids') and 'entry_valor' in self.ids and self.ids.entry_valor.focus:
                print("✅ Enter no campo valor!")
                self.confirmar_deposito()
                return True
            # Verificar se está em outros campos que podem usar Enter para avançar
            elif hasattr(self, 'ids') and 'entry_remetente' in self.ids and self.ids.entry_remetente.focus:
                print("✅ Enter no campo remetente - avançando para valor")
                self.proximo_campo()
                return True
        
        print(f"❌ Tecla {key} não tratada")
        return False

    def on_key_down_alt(self, window, key, scancode, codepoint, modifiers):
        """Alternativa usando on_key_down"""
        print(f"🔑 on_key_down_alt: key={key}, scancode={scancode}")
        
        # Tab key
        if key == 9:  # Tab
            print("✅ Tab capturado via on_key_down_alt!")
            self.proximo_campo()
            return True
        
        # Enter no último campo
        elif key == 13 and hasattr(self, 'ids') and 'entry_valor' in self.ids and self.ids.entry_valor.focus:
            print("✅ Enter no campo valor!")
            self.confirmar_deposito()
            return True
        
        print(f"❌ Tecla {key} não tratada")
        return False

    def on_focus_banco_origem(self, instance, focused):
        """Quando o campo banco ganha foco, atualiza dados"""
        if focused:
            # Pequeno delay para evitar muitos updates
            Clock.schedule_once(lambda dt: self.atualizar_dados_em_tempo_real(), 0.2)

    def proximo_campo(self):
        """Navega para o próximo campo de forma simples e direta - VERSÃO CORRIGIDA"""
        print("🔄 proximo_campo chamado!")
        
        if not hasattr(self, 'ids'):
            print("❌ IDs não disponíveis")
            return
        
        # Ordem dos campos - 🔥 REMOVER 'campo_outro_banco' da lista
        campos = [
            'spinner_cliente',
            'spinner_conta_cliente', 
            'spinner_conta_empresa',
            'spinner_banco_origem',
            'campo_outro_banco',  # 🔥 AGORA É UM ID DIRETO NOS self.ids
            'entry_remetente',
            'entry_valor'
        ]
        
        print(f"📋 Campos na ordem: {campos}")
        
        # Encontrar campo atual com foco
        campo_atual = None
        for campo_id in campos:
            campo = self.get_campo_por_id(campo_id)
            if campo and hasattr(campo, 'focus') and campo.focus:
                campo_atual = campo_id
                print(f"🎯 Campo atual com foco: {campo_id}")
                break
        
        if campo_atual is None:
            # Se nenhum campo tem foco, focar no primeiro
            primeiro_campo = self.get_campo_por_id(campos[0])
            if primeiro_campo:
                print(f"🔍 Nenhum campo com foco, focando no primeiro: {campos[0]}")
                primeiro_campo.focus = True
            else:
                print("❌ Primeiro campo não encontrado")
        else:
            # Encontrar próximo campo
            index_atual = campos.index(campo_atual)
            proximo_index = (index_atual + 1) % len(campos)
            proximo_campo_id = campos[proximo_index]
            proximo_campo = self.get_campo_por_id(proximo_campo_id)
            
            if proximo_campo:
                print(f"➡️ Navegando de {campo_atual} para {proximo_campo_id}")
                
                # 🔥 CORREÇÃO: Verificar se o campo está habilitado
                if hasattr(proximo_campo, 'disabled') and proximo_campo.disabled:
                    # Pular para o próximo campo
                    print(f"⏭️ Campo {proximo_campo_id} desabilitado, pulando...")
                    self.proximo_campo()  # Recursão para pular
                    return
                    
                # Pequeno delay para evitar conflito de foco
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.mudar_foco_seguro(proximo_campo), 0.05)
                        
            else:
                print(f"❌ Próximo campo {proximo_campo_id} não encontrado")

    def mudar_foco_seguro(self, campo):
        """Muda o foco para um campo com segurança"""
        try:
            campo.focus = True
            print(f"✅ Foco mudado com segurança para {campo.id if hasattr(campo, 'id') else 'campo'}")
        except Exception as e:
            print(f"❌ Erro ao mudar foco: {e}")

    def fechar_spinner_simples(self, campo_atual_id):
        """Fecha apenas o spinner atual de forma simples"""
        if campo_atual_id.startswith('spinner_'):
            spinner = self.get_campo_por_id(campo_atual_id)
            if spinner and hasattr(spinner, 'is_open'):
                try:
                    spinner.is_open = False
                    print(f"✅ Spinner {campo_atual_id} fechado")
                except:
                    print(f"⚠️ Não foi possível fechar spinner {campo_atual_id}")

    def fechar_outros_spinners(self, spinner_id_abrir):
        """Fecha todos os spinners exceto o que vai ser aberto"""
        spinners = [
            'spinner_cliente',
            'spinner_conta_cliente', 
            'spinner_conta_empresa',
            'spinner_banco_origem'
        ]
        
        for spinner_id in spinners:
            if spinner_id != spinner_id_abrir:
                spinner = self.get_campo_por_id(spinner_id)
                if spinner and hasattr(spinner, 'is_open') and spinner.is_open:
                    try:
                        spinner.is_open = False
                        print(f"✅ Fechando spinner: {spinner_id}")
                    except:
                        print(f"⚠️ Não foi possível fechar spinner {spinner_id}")

    def fechar_todos_spinners(self):
        """Fecha todos os spinners abertos"""
        spinners = [
            'spinner_cliente',
            'spinner_conta_cliente', 
            'spinner_conta_empresa',
            'spinner_banco_origem'
        ]
        
        for spinner_id in spinners:
            spinner = self.get_campo_por_id(spinner_id)
            if spinner and hasattr(spinner, 'is_open'):
                try:
                    spinner.is_open = False
                    print(f"✅ Spinner {spinner_id} fechado")
                except:
                    print(f"⚠️ Não foi possível fechar spinner {spinner_id}")

    def abrir_spinner_seguro(self, spinner):
        """Abre um spinner com segurança"""
        try:
            # Fechar todos os outros primeiro
            self.fechar_todos_spinners()
            # Depois abrir este
            spinner.is_open = True
            print(f"✅ Spinner aberto com segurança")
        except Exception as e:
            print(f"❌ Erro ao abrir spinner: {e}")
            spinner.focus = True

    def get_campo_por_id(self, campo_id):
        """Retorna o campo pelo ID - VERSÃO CORRIGIDA"""
        # 🔥 AGORA 'campo_outro_banco' está em self.ids, não em self.campo_outro_banco
        if hasattr(self, 'ids') and campo_id in self.ids:
            return self.ids[campo_id]
        return None

    def configurar_campo_valor(self):
        """Configura o campo valor como TextInput normal"""
        if hasattr(self, 'ids') and 'entry_valor' in self.ids:
            # Configurar como TextInput normal
            self.ids.entry_valor.text = "0.00"
            self.ids.entry_valor.input_filter = 'float'
            self.ids.entry_valor.halign = 'right'
            # Vincular a formatação
            self.ids.entry_valor.bind(text=self.formatar_valor_deposito)
            print("✅ Campo valor configurado como TextInput")

    def get_valor_numerico(self):
        """Obtém o valor numérico do campo"""
        if hasattr(self.ids.entry_valor, 'get_float_value'):
            return self.ids.entry_valor.get_float_value()
        else:
            # Fallback
            try:
                texto_limpo = self.ids.entry_valor.text.replace(',', '')
                return float(texto_limpo) if texto_limpo else 0.0
            except (ValueError, AttributeError):
                return 0.0
    
    def carregar_dados(self):
        """Carrega clientes e contas - VERSÃO ATUALIZADA"""
        sistema = App.get_running_app().sistema
        
        print("🔄 CARREGANDO DADOS PARA TELA CONFIRMAR DEPÓSITO...")
        
        # 🔥 CRÍTICO: FORÇAR ATUALIZAÇÃO DIRETA DO SUPABASE
        self.atualizar_dados_diretamente_do_supabase(sistema)
        
        # 🔥 AGORA CARREGAR DOS DADOS ATUALIZADOS DO SISTEMA
        self.clientes = self.carregar_clientes_hibrido(sistema)
        
        # 🔥 IMPORTANTE: Usar contas direto do sistema (que já foram atualizadas)
        self.contas_empresa = {}
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            self.contas_empresa[conta_num] = {
                'numero': conta_num,
                'banco': conta_info.get('banco', ''),
                'moeda': conta_info.get('moeda', 'BRL'),
                'saldo': conta_info.get('saldo', 0.0)
            }
        
        print(f"✅ Dados carregados: {len(self.clientes)} clientes, {len(self.contas_empresa)} contas empresa")
        
        # 🔥 DEBUG: Verificar contas carregadas
        print("📋 Contas empresa carregadas:")
        for conta_num, conta_info in self.contas_empresa.items():
            print(f"   📄 {conta_num}: {conta_info['banco']} - {conta_info['moeda']} - {conta_info['saldo']:,.2f}")
        
        if hasattr(self, 'ids'):
            self.atualizar_spinners()
        
        if hasattr(self, 'ids') and 'entry_valor' in self.ids:
            self.configurar_campo_valor()
            
        if self.spinner_banco_origem:
            self.on_banco_selecionado(None, "Outro Banco")

    def atualizar_dados_diretamente_do_supabase(self, sistema):
        """Atualiza dados diretamente do Supabase - FORÇADO"""
        try:
            print("🔥 ATUALIZAÇÃO DIRETA DO SUPABASE...")
            
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("⚠️ Supabase não disponível")
                return
            
            # 1. ATUALIZAR CONTAS BANCÁRIAS DA EMPRESA DIRETAMENTE
            print("📡 Buscando contas bancárias da empresa no Supabase...")
            response = sistema.supabase.client.table('contas_bancarias_empresa')\
                .select('*')\
                .execute()
            
            if response.data:
                print(f"📊 {len(response.data)} contas encontradas no Supabase")
                
                # 🔥 LIMPAR E RECARREGAR CACHE LOCAL DO SISTEMA
                sistema.contas_bancarias_empresa.clear()
                
                for conta in response.data:
                    conta_num = conta['numero']  # 🔥 IMPORTANTE: usar 'numero' não 'id'
                    sistema.contas_bancarias_empresa[conta_num] = {
                        'numero': conta_num,
                        'banco': conta['banco'],
                        'moeda': conta['moeda'],
                        'saldo': float(conta['saldo']),
                        'tipo': conta.get('tipo', 'empresa'),
                        'agencia': conta.get('agencia', ''),
                        'data_criacao': conta.get('data_criacao', ''),
                        'saldo_inicial': float(conta.get('saldo_inicial', 0.0))
                    }
                
                print(f"✅ {len(response.data)} contas bancárias atualizadas do Supabase")
                
                # 🔥 DEBUG: Mostrar todas as contas carregadas
                for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
                    print(f"   🆕 {conta_num}: {conta_info['banco']} - {conta_info['moeda']} - {conta_info['saldo']:,.2f}")
            
            # 2. ATUALIZAR CONTAS DOS CLIENTES
            print("📡 Buscando contas dos clientes no Supabase...")
            response_contas = sistema.supabase.client.table('contas')\
                .select('*')\
                .execute()
            
            if response_contas.data:
                contas_atualizadas = 0
                for conta in response_contas.data:
                    conta_num = conta['id']  # 🔥 IMPORTANTE: usar 'id' aqui
                    if conta_num not in sistema.contas:
                        contas_atualizadas += 1
                    
                    sistema.contas[conta_num] = {
                        'moeda': conta['moeda'],
                        'saldo': float(conta['saldo']),
                        'cliente': conta['cliente_username'],
                        'cliente_nome': conta.get('cliente_nome', ''),
                        'data_criacao': conta.get('data_criacao', ''),
                        'ativa': conta.get('ativa', True)
                    }
                
                if contas_atualizadas > 0:
                    print(f"✅ {contas_atualizadas} novas contas de clientes carregadas")
            
            print("🎯 Atualização direta do Supabase concluída!")
            
        except Exception as e:
            print(f"❌ Erro na atualização direta do Supabase: {e}")
            import traceback
            traceback.print_exc()

    def atualizar_contas_clientes_com_saldos_reais(self, sistema):
        """Atualiza as contas dos clientes com saldos reais do sistema"""
        print("🔄 Atualizando contas dos clientes com saldos reais...")
        
        for cliente in self.clientes:
            username = cliente.get('username')
            if username and username in sistema.usuarios:
                # Atualizar lista de contas do cliente
                cliente['contas'] = sistema.usuarios[username].get('contas', [])
                
                # Debug: mostrar contas e saldos
                print(f"👤 Cliente {username}: {len(cliente['contas'])} contas")
                for conta_num in cliente['contas']:
                    if conta_num in sistema.contas:
                        saldo = sistema.contas[conta_num].get('saldo', 0)
                        moeda = sistema.contas[conta_num].get('moeda', 'USD')
                        print(f"   💳 {conta_num}: {moeda} {saldo:,.2f}")

    def carregar_clientes_hibrido(self, sistema):
        """Carrega clientes - SUPABASE FIRST, igual outras telas"""
        if sistema.supabase.conectado:
            try:
                clientes_supabase = sistema.supabase.obter_clientes()
                if clientes_supabase:
                    print(f"✅ {len(clientes_supabase)} clientes carregados do Supabase")
                    return clientes_supabase
            except Exception as e:
                print(f"⚠️ Erro ao carregar clientes do Supabase: {e}")
        
        # 🔥 FALLBACK: Carregar do JSON (mesmo padrão das outras telas)
        print("🔄 Carregando clientes do JSON (fallback)")
        return sistema.listar_clientes()

    def carregar_contas_empresa_hibrido(self, sistema):
        """Carrega contas da empresa - SUPABASE FIRST, igual outras telas"""
        if sistema.supabase.conectado:
            try:
                contas_supabase = sistema.supabase.obter_contas_bancarias_empresa()
                if contas_supabase:
                    print(f"✅ {len(contas_supabase)} contas empresa carregadas do Supabase")
                    return contas_supabase
            except Exception as e:
                print(f"⚠️ Erro ao carregar contas empresa do Supabase: {e}")
        
        # 🔥 FALLBACK: Carregar do JSON (mesmo padrão das outras telas)
        print("🔄 Carregando contas empresa do JSON (fallback)")
        return sistema.contas_bancarias_empresa
  
    def carregar_contas_empresa_atualizadas(self, sistema):
        """Carrega contas da empresa COM SALDOS ATUAIS do sistema"""
        contas_atualizadas = {}
        
        # Buscar direto do sistema (que já está atualizado)
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            contas_atualizadas[conta_num] = {
                'numero': conta_num,
                'banco': conta_info['banco'],
                'moeda': conta_info['moeda'],
                'saldo': conta_info['saldo']  # 🔥 SALDO ATUALIZADO
            }
        
        print(f"✅ {len(contas_atualizadas)} contas empresa carregadas com saldos atuais")
        return contas_atualizadas

    def on_campo_valor_focado(self, instance, focused):
        """Quando o campo valor ganha foco, coloca cursor no final"""
        if focused:
            from kivy.clock import Clock
            # Pequeno delay para garantir que o foco está estabelecido
            Clock.schedule_once(lambda dt: self.forcar_cursor_final(instance), 0.05)
    
    def forcar_cursor_final(self, instance):
        """Força o cursor para o final do campo"""
        instance.cursor = (len(instance.text), 0)
    
    def formatar_valor_deposito(self, instance, text):
        """Formata o valor automaticamente no formato 1,234.56 - USANDO LÓGICA DO CampoValor"""
        import re
        
        # Se texto vazio, definir como 0.00
        if not text:
            instance.text = "0.00"
            instance.cursor = (len("0.00"), 0)
            return
        
        # Obter apenas os números atuais (remover formatação)
        numeros_atuais = re.sub(r'[^\d]', '', text)
        
        # Se for zero inicial, começar do zero
        if numeros_atuais == "000":
            numeros_atuais = ""
        
        # Se não há dígitos, definir como 0.00
        if not numeros_atuais:
            instance.text = "0.00"
            instance.cursor = (len("0.00"), 0)
            return
        
        # Limitar a 11 dígitos (999,999,999.99)
        if len(numeros_atuais) > 11:
            numeros_atuais = numeros_atuais[-11:]
        
        # Garantir que tenha pelo menos 3 dígitos (para os centavos)
        while len(numeros_atuais) < 3:
            numeros_atuais = "0" + numeros_atuais
        
        # Separar parte inteira e decimal
        parte_inteira = numeros_atuais[:-2]
        parte_decimal = numeros_atuais[-2:]
        
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
        
        valor_formatado = f"{parte_inteira_formatada}.{parte_decimal}"
        
        # Atualizar sem disparar evento
        instance.unbind(text=self.formatar_valor_deposito)
        instance.text = valor_formatado
        instance.bind(text=self.formatar_valor_deposito)
        
        # Cursor sempre no final
        instance.cursor = (len(valor_formatado), 0)
        
        print(f"🔧 Formatação: '{text}' -> '{valor_formatado}'")

    def atualizar_spinners(self):
        """Atualiza os spinners com dados carregados - VERSÃO SIMPLIFICADA"""
        if not hasattr(self, 'ids') or 'spinner_cliente' not in self.ids:
            return
        
        print("🔄 Atualizando spinners...")
        
        # Spinner de clientes
        opcoes_clientes = [f"{cliente['nome']} ({cliente['username']})" for cliente in self.clientes]
        self.ids.spinner_cliente.values = opcoes_clientes
        if opcoes_clientes:
            self.ids.spinner_cliente.text = opcoes_clientes[0]
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.on_cliente_selecionado(opcoes_clientes[0]), 0.1)
        
        # 🔥 CONFIGURAR SPINNER DE BANCO (SIMPLES)
        bancos = [
            "Outro Banco",
            "BANCO DO BRASIL",
            "ITAÚ", 
            "HSBC",
            "SANTANDER",
            "BRADESCO",
            "CAIXA ECONÔMICA FEDERAL",
            "SICREDI",
            "SICOOB",
            "C6 BANK",
            "NUBANK",
            "PAGBANK",
            "BANCO INTER"
        ]
        
        if hasattr(self, 'ids') and 'spinner_banco_origem' in self.ids:
            self.spinner_banco_origem = self.ids.spinner_banco_origem
            self.spinner_banco_origem.values = bancos
            self.spinner_banco_origem.text = "Outro Banco"
            self.spinner_banco_origem.bind(text=self.on_banco_selecionado)
            print("✅ Spinner de banco configurado")
    
    def on_banco_selecionado(self, spinner, texto):
        """Controla visibilidade do campo 'Outro Banco' - VERSÃO SIMPLIFICADA"""
        if not hasattr(self, 'ids') or 'campo_outro_banco' not in self.ids:
            print("⚠️ Campo 'Outro Banco' não encontrado nos ids")
            return
        
        print(f"🔧 Banco selecionado: {texto}")
        
        if texto == "Outro Banco":
            # Mostrar e habilitar campo
            self.ids.campo_outro_banco.opacity = 1
            self.ids.campo_outro_banco.disabled = False
            self.ids.layout_banco.height = dp(120)
            print("✅ Campo 'Outro Banco' visível e habilitado")
            
            # 🔥 OPÇÃO: Focar automaticamente no campo
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.ids.campo_outro_banco, 'focus', True), 0.1)
        else:
            # Ocultar e desabilitar campo
            self.ids.campo_outro_banco.opacity = 0
            self.ids.campo_outro_banco.disabled = True
            self.ids.layout_banco.height = dp(80)
            print("❌ Campo 'Outro Banco' oculto e desabilitado")
    
    def on_cliente_selecionado(self, cliente_selecionado):
        """Quando um cliente é selecionado, carrega suas contas ATUALIZADAS"""
        if not cliente_selecionado or cliente_selecionado == "Selecione o cliente":
            return
        
        # Extrair username do cliente
        username = cliente_selecionado.split('(')[-1].replace(')', '')
        
        sistema = App.get_running_app().sistema
        
        print(f"🔍 Buscando contas atualizadas para cliente: {username}")
        
        # 🔥 CRÍTICO: Buscar cliente ATUALIZADO do sistema
        cliente_atualizado = None
        for cliente in self.clientes:
            if cliente.get('username') == username:
                cliente_atualizado = cliente
                break
        
        if not cliente_atualizado:
            # Fallback: buscar do sistema
            cliente_atualizado = sistema.usuarios.get(username)
        
        if not cliente_atualizado:
            print(f"❌ Cliente {username} não encontrado")
            return
        
        # 🔥 ATUALIZAR: Carregar contas do cliente COM SALDOS ATUAIS DO SISTEMA
        contas_cliente_atualizadas = []
        for conta_num in cliente_atualizado.get('contas', []):
            if conta_num in sistema.contas:
                conta_info = sistema.contas[conta_num]
                # 🔥 Buscar saldo ATUALIZADO direto do sistema
                saldo_atual = sistema.contas[conta_num]['saldo']
                
                contas_cliente_atualizadas.append({
                    'numero': conta_num,
                    'moeda': conta_info['moeda'],
                    'saldo': saldo_atual  # 🔥 SALDO ATUALIZADO
                })
                print(f"  ✅ Conta {conta_num}: R$ {saldo_atual:,.2f}")
        
        # Atualizar spinner de contas do cliente
        if hasattr(self, 'ids') and 'spinner_conta_cliente' in self.ids:
            if contas_cliente_atualizadas:
                opcoes_contas_cliente = [
                    f"{conta['numero']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})" 
                    for conta in contas_cliente_atualizadas
                ]
                self.ids.spinner_conta_cliente.values = opcoes_contas_cliente
                
                # Manter seleção atual se possível
                conta_atual = self.ids.spinner_conta_cliente.text
                if conta_atual and any(conta_atual.startswith(c['numero']) for c in contas_cliente_atualizadas):
                    # Encontrar a conta correspondente
                    for conta in contas_cliente_atualizadas:
                        if conta_atual.startswith(conta['numero']):
                            nova_opcao = f"{conta['numero']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})"
                            self.ids.spinner_conta_cliente.text = nova_opcao
                            break
                else:
                    self.ids.spinner_conta_cliente.text = opcoes_contas_cliente[0]
                
                # 🔥 FORÇAR ATUALIZAÇÃO DAS CONTAS DA EMPRESA
                self.on_conta_cliente_selecionada(self.ids.spinner_conta_cliente.text)
            else:
                self.ids.spinner_conta_cliente.values = []
                self.ids.spinner_conta_cliente.text = "Nenhuma conta disponível"
                print(f"⚠️ Cliente {username} não tem contas")

    def atualizar_dados_em_tempo_real(self):
        """Atualiza todos os dados com informações em tempo real"""
        sistema = App.get_running_app().sistema
        
        print("🔄 Atualizando dados em tempo real...")
        
        try:
            # 1. Buscar dados atualizados do sistema
            self.clientes = self.carregar_clientes_hibrido(sistema)
            
            # 2. Buscar contas da empresa atualizadas
            self.contas_empresa = {}
            if hasattr(sistema, 'contas_bancarias_empresa'):
                for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
                    self.contas_empresa[conta_num] = {
                        'numero': conta_num,
                        'banco': conta_info.get('banco', ''),
                        'moeda': conta_info.get('moeda', 'BRL'),
                        'saldo': conta_info.get('saldo', 0.0)
                    }
            
            # 3. Atualizar spinners visuais
            self.atualizar_spinners_com_dados_reais()
            
            print(f"✅ Dados atualizados: {len(self.clientes)} clientes, {len(self.contas_empresa)} contas empresa")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar dados em tempo real: {e}")
            import traceback
            traceback.print_exc()

    def atualizar_spinners_com_dados_reais(self):
        """Atualiza os spinners com dados ATUAIS do sistema - VERSÃO CORRIGIDA"""
        if not hasattr(self, 'ids') or 'spinner_cliente' not in self.ids:
            return
        
        sistema = App.get_running_app().sistema
        
        print("🔄 Atualizando spinners com dados reais...")
        
        # 🔥 ATUALIZAR: Spinner de clientes
        cliente_selecionado_atual = self.ids.spinner_cliente.text
        
        # Reconstruir opções com dados atualizados
        opcoes_clientes = [
            f"{cliente['nome']} ({cliente['username']})" 
            for cliente in self.clientes
        ]
        
        self.ids.spinner_cliente.values = opcoes_clientes
        
        # Manter seleção atual ou selecionar primeiro
        if cliente_selecionado_atual in opcoes_clientes:
            # 🔥 MANTER seleção atual mas FORÇAR atualização das contas
            self.ids.spinner_cliente.text = cliente_selecionado_atual
            self.on_cliente_selecionado(cliente_selecionado_atual)
        elif opcoes_clientes:
            self.ids.spinner_cliente.text = opcoes_clientes[0]
            self.on_cliente_selecionado(opcoes_clientes[0])
        else:
            self.ids.spinner_cliente.text = "Nenhum cliente disponível"
        
        print("✅ Spinners atualizados com dados reais")

    def forcar_atualizacao_completa(self):
        """Força uma atualização completa de todos os dados - VERSÃO SIMPLIFICADA"""
        print("🔧 FORÇANDO ATUALIZAÇÃO COMPLETA...")
        
        sistema = App.get_running_app().sistema
        
        # 1. Atualizar dados do sistema (se necessário)
        if hasattr(sistema, 'atualizar_dados'):
            sistema.atualizar_dados()
        elif hasattr(sistema, 'carregar_dados'):
            sistema.carregar_dados()
        
        # 2. Atualizar listas locais
        print("  🔄 Atualizando lista de clientes...")
        self.clientes = self.carregar_clientes_hibrido(sistema)
        
        print("  🔄 Atualizando contas da empresa...")
        self.contas_empresa = self.carregar_contas_empresa_atualizadas(sistema)
        
        # 3. Mostrar status atual
        print(f"  📊 Status atual:")
        print(f"    • Clientes: {len(self.clientes)}")
        print(f"    • Contas empresa: {len(self.contas_empresa)}")
        
        if hasattr(sistema, 'contas'):
            print(f"    • Contas no sistema: {len(sistema.contas)}")
            # Mostrar algumas contas como exemplo
            for i, (conta_num, conta_info) in enumerate(list(sistema.contas.items())[:3]):
                print(f"      - {conta_num}: R$ {conta_info.get('saldo', 0):,.2f}")
        
        # 4. Atualizar spinners
        self.atualizar_spinners_com_dados_reais()
        
        print("✅ Atualização completa concluída")

    def on_conta_cliente_selecionada(self, conta_cliente_selecionada):
        """Quando uma conta do cliente é selecionada, filtra contas da empresa pela mesma moeda"""
        if not conta_cliente_selecionada or conta_cliente_selecionada == "Selecione a conta do cliente":
            return
        
        # Extrair moeda da conta do cliente
        try:
            partes = conta_cliente_selecionada.split(' - ')
            if len(partes) >= 2:
                moeda_cliente = partes[1].split(' ')[0]
            else:
                print(f"⚠️ Formato inválido da conta: {conta_cliente_selecionada}")
                return
        except Exception as e:
            print(f"❌ Erro ao extrair moeda: {e}")
            return
        
        # 🔥 ATUALIZAR: Verificar contas da empresa disponíveis
        print(f"🔍 Filtrando contas empresa pela moeda: {moeda_cliente}")
        print(f"   Total de contas empresa disponíveis: {len(self.contas_empresa)}")
        
        # Filtrar contas da empresa pela mesma moeda
        contas_empresa_filtradas = []
        for conta_num, conta_info in self.contas_empresa.items():
            if conta_info['moeda'] == moeda_cliente:
                contas_empresa_filtradas.append({
                    'numero': conta_num,
                    'banco': conta_info['banco'],
                    'moeda': conta_info['moeda'],
                    'saldo': conta_info['saldo']
                })
                print(f"   ✅ {conta_num} - {conta_info['banco']} - {moeda_cliente}")
        
        print(f"   🎯 {len(contas_empresa_filtradas)} contas empresa na moeda {moeda_cliente}")
        
        # Atualizar spinner de contas da empresa
        if hasattr(self, 'ids') and 'spinner_conta_empresa' in self.ids:
            if contas_empresa_filtradas:
                opcoes_contas_empresa = [f"{conta['numero']} - {conta['banco']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})" 
                                    for conta in contas_empresa_filtradas]
                self.ids.spinner_conta_empresa.values = opcoes_contas_empresa
                
                # Tentar manter seleção anterior se possível
                conta_atual = self.ids.spinner_conta_empresa.text
                if conta_atual and any(conta_atual.startswith(str(c['numero'])) for c in contas_empresa_filtradas):
                    # Encontrar a conta correspondente
                    for conta in contas_empresa_filtradas:
                        if conta_atual.startswith(str(conta['numero'])):
                            nova_opcao = f"{conta['numero']} - {conta['banco']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})"
                            self.ids.spinner_conta_empresa.text = nova_opcao
                            break
                else:
                    self.ids.spinner_conta_empresa.text = opcoes_contas_empresa[0]
            else:
                self.ids.spinner_conta_empresa.values = []
                self.ids.spinner_conta_empresa.text = f"Nenhuma conta empresa em {moeda_cliente}"
                print(f"⚠️ Nenhuma conta empresa encontrada na moeda {moeda_cliente}")
    
    def forcar_recarga_tela(self):
        """Força a recarga completa da tela"""
        print("🔄 FORÇANDO RECARGA COMPLETA DA TELA...")
        
        sistema = App.get_running_app().sistema
        
        # 🔥 ATUALIZAR DIRETAMENTE DO SUPABASE
        self.atualizar_dados_diretamente_do_supabase(sistema)
        
        # 🔥 RECARREGAR CLIENTES
        self.clientes = self.carregar_clientes_hibrido(sistema)
        
        # 🔥 RECARREGAR CONTAS DA EMPRESA
        self.contas_empresa = {}
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            self.contas_empresa[conta_num] = {
                'numero': conta_num,
                'banco': conta_info.get('banco', ''),
                'moeda': conta_info.get('moeda', 'BRL'),
                'saldo': conta_info.get('saldo', 0.0)
            }
        
        # 🔥 ATUALIZAR SPINNERS
        if hasattr(self, 'ids'):
            self.atualizar_spinners()
        
        print(f"✅ Tela recarregada: {len(self.contas_empresa)} contas empresa disponíveis")
        
        # 🔥 Mostrar mensagem de sucesso
        self.mostrar_sucesso(f"Dados atualizados!\n{len(self.contas_empresa)} contas empresa carregadas.")

    def obter_banco_origem(self):
        """Obtém o nome do banco de origem - VERSÃO CORRIGIDA"""
        if not self.spinner_banco_origem:
            return ""
        
        banco_selecionado = self.spinner_banco_origem.text
        
        # Se selecionou "Outro Banco", pegar do campo de texto
        if banco_selecionado == "Outro Banco":
            if hasattr(self, 'ids') and 'campo_outro_banco' in self.ids:
                outro_banco = self.ids.campo_outro_banco.text.strip()
                if outro_banco:
                    return outro_banco
        
        return banco_selecionado
    
    def validar_dados(self):
        """Valida os dados - COM ATUALIZAÇÃO EM TEMPO REAL"""
        if not hasattr(self, 'ids'):
            return False
        
        # 🔥 CRÍTICO: ATUALIZAR DADOS ANTES DE VALIDAR
        self.atualizar_dados_em_tempo_real()
        
        # Validar banco de origem - 🔥 AGORA usa obter_banco_origem()
        banco_origem = self.obter_banco_origem()
        if not banco_origem:
            self.mostrar_erro("Informe o banco de origem")
            return False
        
        # 🔥 CORREÇÃO: Se for "Outro Banco", verificar se foi digitado algo
        if banco_origem == "Outro Banco":
            # Agora verifica se tem conteúdo no campo
            if hasattr(self, 'ids') and 'campo_outro_banco' in self.ids:
                outro_banco = self.ids.campo_outro_banco.text.strip()
                if not outro_banco:
                    self.mostrar_erro("Digite o nome do 'Outro Banco'")
                    return False
        
        # Resto da validação permanece igual
        campos_obrigatorios = [
            (self.ids.spinner_cliente.text, "Selecione o cliente"),
            (self.ids.spinner_conta_cliente.text, "Selecione a conta do cliente"),
            (self.ids.spinner_conta_empresa.text, "Selecione a conta da empresa"),
            (self.ids.entry_remetente.text, "Informe o nome do remetente")
        ]
        
        for campo, mensagem in campos_obrigatorios:
            if not campo or campo.startswith("Selecione") or campo == "Nenhuma conta disponível":
                self.mostrar_erro(mensagem)
                return False
        
        # Validar valor
        try:
            valor = self.get_valor_numerico()
            if valor <= 0:
                self.mostrar_erro("O valor deve ser maior que zero")
                return False
        except ValueError:
            self.mostrar_erro("Valor inválido")
            return False
        
        return True
    
    def confirmar_deposito(self):
        """Confirma o depósito - VERSÃO CORRIGIDA"""
        print("🔍 Iniciando confirmação de depósito...")
        
        # 🔥 CORREÇÃO: REMOVER esta verificação antiga
        # if self.campo_outro_banco and not self.campo_outro_banco.parent:  # ❌ REMOVER!
        #    print("⚠️ Campo 'Outro Banco' inválido - resetando")
        #    self.campo_outro_banco = None
        
        # 🔥 VERIFICAÇÃO FINAL: Atualizar dados ANTES de validar
        print("🔍 VERIFICAÇÃO FINAL: Atualizando dados antes do depósito...")
        
        # Versão mais simples e segura:
        self.atualizar_dados_em_tempo_real()
        
        # Pequeno delay para garantir que os dados foram atualizados
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.processar_confirmacao_deposito(), 0.1)

    def processar_confirmacao_deposito(self):
        """Processa a confirmação do depósito após atualizar dados"""
        # 🔥 VERIFICAÇÃO SIMPLES: usar apenas self.validar_dados()
        if not self.validar_dados():
            return
        
        if not self.validar_dados():
            return
        
        try:
            sistema = App.get_running_app().sistema
            
            # 🔥 GUARDAR AS SELEÇÕES ATUAIS ANTES DE PROCESSAR
            cliente_selecionado_texto = self.ids.spinner_cliente.text
            conta_cliente_selecionada_texto = self.ids.spinner_conta_cliente.text
            conta_empresa_selecionada_texto = self.ids.spinner_conta_empresa.text
            
            # Extrair dados para processamento
            username = cliente_selecionado_texto.split('(')[-1].replace(')', '')
            
            numero_conta_cliente = conta_cliente_selecionada_texto.split(' - ')[0]
            moeda = conta_cliente_selecionada_texto.split(' - ')[1].split(' ')[0]
            
            if ' - ' in conta_empresa_selecionada_texto:
                numero_conta_empresa = conta_empresa_selecionada_texto.split(' - ')[0]
            else:
                self.mostrar_erro("Conta da empresa inválida!")
                return
            
            banco_origem = self.obter_banco_origem()
            remetente = self.ids.entry_remetente.text
            
            # Converter valor
            try:
                valor_texto = self.ids.entry_valor.text.replace(',', '')
                valor = float(valor_texto)
            except ValueError:
                self.mostrar_erro("Valor inválido!")
                return
            
            print(f"🔍 PROCESSANDO DEPÓSITO COM SUPABASE-FIRST:")
            print(f"  Valor: {valor:,.2f}")
            print(f"  Cliente: {username}")
            print(f"  Conta Cliente: {numero_conta_cliente} ({moeda})")
            print(f"  Conta Empresa: {numero_conta_empresa}")
            
            # Verificar se contas existem
            if numero_conta_empresa not in sistema.contas_bancarias_empresa:
                self.mostrar_erro("Conta da empresa não encontrada!")
                return
            
            if numero_conta_cliente not in sistema.contas:
                self.mostrar_erro("Conta do cliente não encontrada!")
                return
            
            saldo_empresa_antes = sistema.contas_bancarias_empresa[numero_conta_empresa]['saldo']
            saldo_cliente_antes = sistema.contas[numero_conta_cliente]['saldo']
            
            print(f"  Saldo empresa antes: {saldo_empresa_antes:,.2f}")
            print(f"  Saldo cliente antes: {saldo_cliente_antes:,.2f}")
            
            # Obter usuário logado
            if isinstance(sistema.usuario_logado, dict):
                executado_por = sistema.usuario_logado.get('username', 'sistema')
            else:
                executado_por = sistema.usuario_logado
            
            # 🔥🔥🔥 SUPABASE FIRST - TENTAR SALVAR NO SUPABASE PRIMEIRO
            supabase_sucesso = False
            transacao_id = str(int(datetime.datetime.now().timestamp()))
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    print("🚀 SALVANDO NO SUPABASE PRIMEIRO...")
                    
                    # 1. CRIAR TRANSAÇÃO NO SUPABASE
                    descricao = f"Depósito confirmado - Banco: {banco_origem} - Remetente: {remetente}"
                    
                    dados_transacao = {
                        'id': transacao_id,
                        'tipo': 'deposito',
                        'conta_remetente': numero_conta_cliente,
                        'conta_destinatario': numero_conta_empresa,
                        'valor': valor,
                        'moeda': moeda,
                        'banco_origem': banco_origem,
                        'remetente': remetente,
                        'descricao': descricao,
                        'status': 'completed',
                        'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'executado_por': executado_por,
                        'cliente': username
                    }
                    
                    # SALVAR TRANSAÇÃO NO SUPABASE
                    transacao_sucesso = sistema.supabase.salvar_transacao(dados_transacao)
                    
                    if transacao_sucesso:
                        print("✅ Transação salva no Supabase")
                        
                        # 2. ATUALIZAR SALDOS NO SUPABASE
                        novo_saldo_cliente = saldo_cliente_antes + valor
                        novo_saldo_empresa = saldo_empresa_antes + valor
                        
                        print(f"🔍 DEBUG ATUALIZAÇÃO SALDOS SUPABASE:")
                        print(f"  Conta cliente: {numero_conta_cliente} → {novo_saldo_cliente:.2f}")
                        print(f"  Conta empresa: {numero_conta_empresa} → {novo_saldo_empresa:.2f}")
                        
                        cliente_sucesso = sistema.supabase.atualizar_saldo_conta(
                            numero_conta_cliente, 
                            novo_saldo_cliente
                        )
                        
                        empresa_sucesso = sistema.supabase.atualizar_saldo_conta_empresa(
                            numero_conta_empresa, 
                            novo_saldo_empresa
                        )
                        
                        print(f"🔍 RESULTADO ATUALIZAÇÃO:")
                        print(f"  Cliente: {'✅' if cliente_sucesso else '❌'}")
                        print(f"  Empresa: {'✅' if empresa_sucesso else '❌'}")
                        
                        if cliente_sucesso and empresa_sucesso:
                            supabase_sucesso = True
                            print("✅ Saldos atualizados no Supabase")
                        else:
                            print("❌ Falha ao atualizar saldos no Supabase - Transação mantida para debug")
                            supabase_sucesso = False
                        
                except Exception as e:
                    print(f"❌ Erro crítico no Supabase: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 🔥 ATUALIZAR CACHE LOCAL
            if supabase_sucesso:
                # Atualizar saldos locais
                sistema.contas[numero_conta_cliente]['saldo'] += valor
                saldo_cliente_depois = sistema.contas[numero_conta_cliente]['saldo']
                
                sistema.contas_bancarias_empresa[numero_conta_empresa]['saldo'] += valor
                saldo_empresa_depois = sistema.contas_bancarias_empresa[numero_conta_empresa]['saldo']
                
                # Salvar transação localmente
                sistema.transferencias[transacao_id] = dados_transacao
                
                print(f"  ✅ CLIENTE (CRÉDITO): {saldo_cliente_antes:,.2f} → {saldo_cliente_depois:,.2f} (+{valor:,.2f})")
                print(f"  ✅ EMPRESA (DÉBITO): {saldo_empresa_antes:,.2f} → {saldo_empresa_depois:,.2f} (+{valor:,.2f})")
                
                # 🔥 SALVAR ARQUIVOS LOCAIS (APENAS BACKUP)
                sistema.salvar_contas_bancarias()
                sistema.salvar_contas()
                sistema.salvar_transferencias()
                
                status_supabase = "✅ Sincronizado com Supabase"
            else:
                # 🔥 FALLBACK: Salvar apenas localmente se Supabase falhar
                print("⚠️ Usando fallback local (Supabase falhou)")
                
                sistema.contas[numero_conta_cliente]['saldo'] += valor
                saldo_cliente_depois = sistema.contas[numero_conta_cliente]['saldo']
                
                sistema.contas_bancarias_empresa[numero_conta_empresa]['saldo'] += valor
                saldo_empresa_depois = sistema.contas_bancarias_empresa[numero_conta_empresa]['saldo']
                
                # Criar transação local
                descricao = f"Depósito confirmado - Banco: {banco_origem} - Remetente: {remetente}"
                dados_transacao = {
                    'id': transacao_id,
                    'tipo': 'deposito',
                    'conta_remetente': numero_conta_cliente,
                    'conta_destinatario': numero_conta_empresa,
                    'valor': valor,
                    'moeda': moeda,
                    'banco_origem': banco_origem,
                    'remetente': remetente,
                    'descricao': descricao,
                    'status': 'completed',
                    'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'executado_por': executado_por,
                    'cliente': username
                }
                
                sistema.transferencias[transacao_id] = dados_transacao
                
                # Salvar arquivos locais
                sistema.salvar_contas_bancarias()
                sistema.salvar_contas()
                sistema.salvar_transferencias()
                
                status_supabase = "⚠️ Salvo apenas localmente (erro Supabase)"
            
            print("✅ Depósito confirmado com sucesso!")
            
            # MENSAGEM DE CONFIRMAÇÃO
            self.mostrar_sucesso(
                f"Depósito confirmado!\n\n"
                f"Valor: {valor:,.2f} {moeda}\n"
                f"Cliente: {username}\n"
                f"Conta: {numero_conta_cliente}\n"
                f"Banco: {banco_origem}\n\n"
                f"Saldo anterior: {saldo_cliente_antes:,.2f}\n"
                f"Novo saldo: {saldo_cliente_depois:,.2f}\n\n"
                f"{status_supabase}"
            )
            
            # 🔥🔥🔥 MODIFICAÇÃO PRINCIPAL: ATUALIZAR SPINNERS COM NOVOS SALDOS
            # Pequeno delay para garantir que o popup não interfira
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.atualizar_spinners_apos_deposito(
                cliente_selecionado_texto,
                conta_cliente_selecionada_texto,
                conta_empresa_selecionada_texto,
                saldo_cliente_depois,
                saldo_empresa_depois
            ), 0.2)
            
            # Limpar campos do depósito atual
            Clock.schedule_once(lambda dt: self.limpar_campos_parcial(), 0.3)
            
        except Exception as e:
            print(f"❌ Erro ao confirmar depósito: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_erro(f"Erro ao processar depósito: {str(e)}")


    def atualizar_spinners_apos_deposito(self, cliente_texto, conta_cliente_texto, 
                                        conta_empresa_texto, novo_saldo_cliente, novo_saldo_empresa):
        """Atualiza os spinners com os novos saldos após o depósito"""
        print("🔄 Atualizando spinners com novos saldos...")
        
        if not hasattr(self, 'ids'):
            return
        
        # 1. ATUALIZAR CONTA DO CLIENTE
        if conta_cliente_texto and ' - ' in conta_cliente_texto:
            partes = conta_cliente_texto.split(' - ')
            if len(partes) >= 2:
                # Extrair número da conta e moeda
                numero_conta = partes[0]
                moeda = partes[1].split(' ')[0]
                
                # Criar novo texto com saldo atualizado
                novo_texto_conta_cliente = f"{numero_conta} - {moeda} (Saldo: {novo_saldo_cliente:,.2f})"
                
                # Atualizar o texto do spinner
                self.ids.spinner_conta_cliente.text = novo_texto_conta_cliente
                
                # Atualizar também nos values para manter consistência
                if self.ids.spinner_conta_cliente.values:
                    # Encontrar e substituir o item nos values
                    novos_values = []
                    for value in self.ids.spinner_conta_cliente.values:
                        if value.startswith(f"{numero_conta} -"):
                            novos_values.append(novo_texto_conta_cliente)
                        else:
                            novos_values.append(value)
                    
                    self.ids.spinner_conta_cliente.values = novos_values
                
                print(f"✅ Conta cliente atualizada: {novo_texto_conta_cliente}")
        
        # 2. ATUALIZAR CONTA DA EMPRESA
        if conta_empresa_texto and ' - ' in conta_empresa_texto:
            partes = conta_empresa_texto.split(' - ')
            if len(partes) >= 3:
                # Extrair número da conta, banco e moeda
                numero_conta = partes[0]
                banco = partes[1]
                moeda = partes[2].split(' ')[0]
                
                # Criar novo texto com saldo atualizado
                novo_texto_conta_empresa = f"{numero_conta} - {banco} - {moeda} (Saldo: {novo_saldo_empresa:,.2f})"
                
                # Atualizar o texto do spinner
                self.ids.spinner_conta_empresa.text = novo_texto_conta_empresa
                
                # Atualizar também nos values
                if self.ids.spinner_conta_empresa.values:
                    # Encontrar e substituir o item nos values
                    novos_values = []
                    for value in self.ids.spinner_conta_empresa.values:
                        if value.startswith(f"{numero_conta} -"):
                            novos_values.append(novo_texto_conta_empresa)
                        else:
                            novos_values.append(value)
                    
                    self.ids.spinner_conta_empresa.values = novos_values
                
                print(f"✅ Conta empresa atualizada: {novo_texto_conta_empresa}")
        
        print("✅ Spinners atualizados com sucesso!")


    def limpar_campos_parcial(self):
        """Limpa apenas os campos do depósito atual - VERSÃO FINAL"""
        if not hasattr(self, 'ids'):
            return
        
        print("🧹 Limpando campos parciais...")
        
        # 🔥 RESETAR SPINNER DE BANCO
        if self.spinner_banco_origem:
            self.spinner_banco_origem.text = "Outro Banco"
        
        # 🔥 LIMPAR O TEXTO DO CAMPO "OUTRO BANCO" (agora em self.ids)
        if 'campo_outro_banco' in self.ids:
            self.ids.campo_outro_banco.text = ""
        
        # Limpar outros campos
        self.ids.entry_remetente.text = ""
        self.ids.entry_valor.text = "0.00"
        
        print("✅ Campos limpos")
        
        # Focar no banco de origem
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.focar_banco_origem(), 0.1)


    def focar_banco_origem(self):
        """Foca no campo de banco de origem para o próximo depósito"""
        if self.spinner_banco_origem:
            try:
                self.spinner_banco_origem.focus = True
                print("✅ Foco movido para banco de origem")
            except:
                print("⚠️ Não foi possível focar no spinner de banco")


    # Mantenha o método limpar_campos original para quando precisar limpar tudo
    def limpar_campos(self):
        """Limpa TODOS os campos do formulário - VERSÃO ATUALIZADA (opção #6)"""
        if not hasattr(self, 'ids'):
            return
        
        print("🧹🧹🧹 LIMPANDO TODOS OS CAMPOS...")
        
        # Resetar spinner de cliente
        self.ids.spinner_cliente.text = "Selecione o cliente"
        self.ids.spinner_cliente.values = []
        
        # Resetar conta do cliente
        self.ids.spinner_conta_cliente.values = []
        self.ids.spinner_conta_cliente.text = "Selecione a conta do cliente"
        
        # Resetar conta da empresa
        self.ids.spinner_conta_empresa.values = []
        self.ids.spinner_conta_empresa.text = "Selecione a conta da empresa"
        
        # 🔥 CORREÇÃO: Resetar spinner de banco
        if self.spinner_banco_origem:
            self.spinner_banco_origem.text = "Outro Banco"
            # O evento on_banco_selecionado será chamado automaticamente
            # e garantirá que o campo "Outro Banco" esteja visível
        
        # 🔥 CORREÇÃO: Limpar campo "Outro Banco" (agora em self.ids)
        if 'campo_outro_banco' in self.ids:
            self.ids.campo_outro_banco.text = ""
            # Garantir que está visível (porque "Outro Banco" é selecionado)
            self.ids.campo_outro_banco.opacity = 1
            self.ids.campo_outro_banco.disabled = False
        
        # 🔥 CORREÇÃO: Limpar outros campos
        self.ids.entry_remetente.text = ""
        self.ids.entry_valor.text = "0.00"
        
        # 🔥 CORREÇÃO: Ajustar altura do layout (120 quando "Outro Banco" está visível)
        if 'layout_banco' in self.ids:
            self.ids.layout_banco.height = dp(120)
        
        print("✅✅✅ TODOS os campos limpos e resetados")
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=mensagem, color=(1, 0.3, 0.3, 1)))
        
        btn_ok = Button(text='OK', size_hint_y=None, height=40)
        popup = Popup(title='Erro', content=content, size_hint=(None, None), size=(400, 150))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso - VERSÃO MAIOR PARA CABER TODAS INFORMAÇÕES"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Label com altura maior para caber todo o texto
        lbl_mensagem = Label(
            text=mensagem, 
            color=(0.2, 0.8, 0.2, 1),
            text_size=(400, None),  # 🔥 LARGURA FIXA PARA QUEBRAR TEXTO
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=150  # 🔥 ALTURA MAIOR PARA CABER TUDO
        )
        lbl_mensagem.bind(size=lbl_mensagem.setter('text_size'))
        
        btn_ok = Button(
            text='OK', 
            size_hint_y=None, 
            height=40,
            background_color=(0.2, 0.7, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_mensagem)
        content.add_widget(btn_ok)
        
        # 🔥 AUMENTAR TAMANHO DO POPUP
        popup = Popup(
            title='Sucesso', 
            content=content, 
            size_hint=(None, None), 
            size=(450, 250),  # 🔥 MAIOR: 450x250 (era 450x200)
            auto_dismiss=False,
            title_color=(0.2, 0.8, 0.2, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'

    def debug_saldos_contas(self):
        """Debug para verificar saldos das contas"""
        sistema = App.get_running_app().sistema
        
        print("=== 🔍 DEBUG SALDOS DE CONTAS ===")
        
        # Verificar contas da empresa
        print("🏦 CONTAS DA EMPRESA:")
        for conta_num, conta_info in sistema.contas_bancarias_empresa.items():
            print(f"  💼 {conta_num}: {conta_info.get('moeda', '')} {conta_info.get('saldo', 0):,.2f}")
        
        # Verificar algumas contas de clientes
        print("👤 CONTAS DE CLIENTES (amostra):")
        contas_amostra = 0
        for conta_num, conta_info in sistema.contas.items():
            if contas_amostra < 5:  # Mostrar apenas 5 para não poluir
                print(f"  👤 {conta_num}: {conta_info.get('cliente', '')} - {conta_info.get('moeda', '')} {conta_info.get('saldo', 0):,.2f}")
                contas_amostra += 1
        
        print("=== 🎯 FIM DEBUG ===")
