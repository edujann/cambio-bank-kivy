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
        self.campo_outro_banco = None
        self.spinner_banco_origem = None  # 🔥 CORREÇÃO: Guardar referência separada

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        print("🎬 TelaConfirmarDepositos.on_pre_enter()")
        self.carregar_dados()
        
        # Tentativa alternativa: usar on_key_down
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

    def proximo_campo(self):
        """Navega para o próximo campo de forma simples e direta"""
        print("🔄 proximo_campo chamado!")
        
        if not hasattr(self, 'ids'):
            print("❌ IDs não disponíveis")
            return
        
        # Ordem dos campos
        campos = [
            'spinner_cliente',
            'spinner_conta_cliente', 
            'spinner_conta_empresa',
            'spinner_banco_origem',
            'entry_remetente',
            'entry_valor'
        ]
        
        print(f"📋 Campos na ordem: {campos}")
        
        # Incluir campo "Outro Banco" se existir
        if self.campo_outro_banco and self.campo_outro_banco.parent:
            print("✅ Campo 'Outro Banco' encontrado, incluindo na navegação")
            # Inserir após spinner_banco_origem
            index_banco = campos.index('spinner_banco_origem')
            campos.insert(index_banco + 1, 'campo_outro_banco')
        
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
                
                # 🔥 CORREÇÃO: Pequeno delay para evitar conflito de foco
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
        """Retorna o campo pelo ID, tratando casos especiais"""
        if campo_id == 'campo_outro_banco':
            return self.campo_outro_banco
        elif campo_id == 'spinner_banco_origem' and self.spinner_banco_origem:  # 🔥 CORREÇÃO
            return self.spinner_banco_origem
        elif hasattr(self, 'ids') and campo_id in self.ids:
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
        """Carrega clientes e contas - VERSÃO PADRONIZADA COM SUPABASE"""
        sistema = App.get_running_app().sistema
        
        # 🔥 PADRÃO: Carregar clientes do Supabase primeiro
        self.clientes = self.carregar_clientes_hibrido(sistema)
        
        # 🔥 PADRÃO: Carregar contas da empresa do Supabase primeiro  
        self.contas_empresa = self.carregar_contas_empresa_hibrido(sistema)
        
        # Resto do código permanece igual
        if hasattr(self, 'ids'):
            self.atualizar_spinners()
        
        if hasattr(self, 'ids') and 'entry_valor' in self.ids:
            self.configurar_campo_valor()
            
        if self.spinner_banco_origem:
            self.on_banco_selecionado(None, "Outro Banco")

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
        """Atualiza os spinners com dados carregados"""
        if not hasattr(self, 'ids') or 'spinner_cliente' not in self.ids:
            return  # Aguardar o KV carregar
            
        # Spinner de clientes
        opcoes_clientes = [f"{cliente['nome']} ({cliente['username']})" for cliente in self.clientes]
        self.ids.spinner_cliente.values = opcoes_clientes
        if opcoes_clientes:
            self.ids.spinner_cliente.text = opcoes_clientes[0]
            self.on_cliente_selecionado(opcoes_clientes[0])
        
        # 🔥 CORREÇÃO: Usar referência direta para o spinner de banco
        bancos = [
            "Outro Banco",  # Primeira opção
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
        
        # 🔥 CORREÇÃO: Buscar o spinner de banco de forma segura
        if hasattr(self, 'ids') and 'spinner_banco_origem' in self.ids:
            self.spinner_banco_origem = self.ids.spinner_banco_origem  # 🔥 Guardar referência
            self.spinner_banco_origem.values = bancos
            self.spinner_banco_origem.text = "Outro Banco"  # Valor padrão
            # Vincular evento de seleção
            self.spinner_banco_origem.bind(text=self.on_banco_selecionado)
            print("✅ Spinner de banco configurado com sucesso")
        else:
            print("⚠️ spinner_banco_origem não encontrado nos ids")
    
    def on_banco_selecionado(self, spinner, texto):
        """Quando um banco é selecionado, mostra campo para digitar se for 'Outro Banco'"""
        if not hasattr(self, 'ids') or 'layout_banco' not in self.ids:
            print("⚠️ layout_banco não encontrado nos ids")
            return
        
        print(f"🔧 Banco selecionado: {texto}")
        
        # Remover campo anterior se existir
        if self.campo_outro_banco and self.campo_outro_banco.parent:
            self.ids.layout_banco.remove_widget(self.campo_outro_banco)
            self.campo_outro_banco = None
        
        # Se selecionou "Outro Banco", mostrar campo para digitar
        if texto == "Outro Banco":
            print("🔧 Criando campo para 'Outro Banco'")
            self.campo_outro_banco = TextInput(
                hint_text="Digite o nome do banco...",
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                background_color=(0.2, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1),
                padding=dp(10),
                hint_text_color=(0.7, 0.7, 0.7, 1),
                halign='center'
            )
            # Inserir após o spinner de banco
            try:
                # Adicionar o campo abaixo do spinner
                self.ids.layout_banco.add_widget(self.campo_outro_banco)
                
                # Ajustar a altura do layout para acomodar o novo campo
                self.ids.layout_banco.height = dp(120)  # Aumenta a altura do layout
                
                print("✅ Campo 'Outro Banco' adicionado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao adicionar campo: {e}")
        else:
            print("🔧 Banco da lista selecionado, removendo campo extra se existir")
            # Ajustar a altura do layout de volta ao normal
            self.ids.layout_banco.height = dp(80)
    
    def on_cliente_selecionado(self, cliente_selecionado):
        """Quando um cliente é selecionado, carrega suas contas"""
        if not cliente_selecionado or cliente_selecionado == "Selecione o cliente":
            return
        
        # Extrair username do cliente
        username = cliente_selecionado.split('(')[-1].replace(')', '')
        
        sistema = App.get_running_app().sistema
        cliente_info = sistema.usuarios.get(username)
        
        if not cliente_info:
            return
        
        # Carregar contas do cliente
        contas_cliente = []
        for conta_num in cliente_info.get('contas', []):
            if conta_num in sistema.contas:
                conta_info = sistema.contas[conta_num]
                contas_cliente.append({
                    'numero': conta_num,
                    'moeda': conta_info['moeda'],
                    'saldo': conta_info['saldo']
                })
        
        # Atualizar spinner de contas do cliente
        if hasattr(self, 'ids') and 'spinner_conta_cliente' in self.ids:
            opcoes_contas_cliente = [f"{conta['numero']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})" 
                                   for conta in contas_cliente]
            self.ids.spinner_conta_cliente.values = opcoes_contas_cliente
            if opcoes_contas_cliente:
                self.ids.spinner_conta_cliente.text = opcoes_contas_cliente[0]
    
    def on_conta_cliente_selecionada(self, conta_cliente_selecionada):
        """Quando uma conta do cliente é selecionada, filtra contas da empresa pela mesma moeda"""
        if not conta_cliente_selecionada or conta_cliente_selecionada == "Selecione a conta do cliente":
            return
        
        # Extrair moeda da conta do cliente
        moeda_cliente = conta_cliente_selecionada.split(' - ')[1].split(' ')[0]
        
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
        
        # Atualizar spinner de contas da empresa
        if hasattr(self, 'ids') and 'spinner_conta_empresa' in self.ids:
            opcoes_contas_empresa = [f"{conta['numero']} - {conta['banco']} - {conta['moeda']} (Saldo: {conta['saldo']:,.2f})" 
                                   for conta in contas_empresa_filtradas]
            self.ids.spinner_conta_empresa.values = opcoes_contas_empresa
            if opcoes_contas_empresa:
                self.ids.spinner_conta_empresa.text = opcoes_contas_empresa[0]
            else:
                self.ids.spinner_conta_empresa.text = "Nenhuma conta disponível"
    
    def obter_banco_origem(self):
        """Obtém o nome do banco de origem, seja do spinner ou do campo 'Outro Banco'"""
        # 🔥 CORREÇÃO: Usar referência direta em vez de self.ids
        if not self.spinner_banco_origem:
            return ""
        
        banco_selecionado = self.spinner_banco_origem.text
        
        # Se selecionou "Outro Banco" e tem campo para digitar
        if banco_selecionado == "Outro Banco" and self.campo_outro_banco:
            outro_banco = self.campo_outro_banco.text.strip()
            if outro_banco:
                return outro_banco
            else:
                return "Outro Banco"  # Fallback se não digitou nada
        
        return banco_selecionado
    
    def validar_dados(self):
        """Valida os dados - ATUALIZADO PARA CAMPO VALOR EXISTENTE"""
        if not hasattr(self, 'ids'):
            return False
            
        # Validar banco de origem
        banco_origem = self.obter_banco_origem()
        if not banco_origem or banco_origem == "Outro Banco":
            self.mostrar_erro("Informe o banco de origem")
            return False
        
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
        
        # 🔥 VALIDAR VALOR USANDO MÉTODO DO CAMPO EXISTENTE
        try:
            valor = self.get_valor_numerico()  # 🔥 Já usa get_float_value
            if valor <= 0:
                self.mostrar_erro("O valor deve ser maior que zero")
                return False
        except ValueError:
            self.mostrar_erro("Valor inválido")
            return False
        
        return True
    
    def confirmar_deposito(self):
        """Confirma o depósito - VERSÃO SUPABASE-FIRST - MODIFICADA PARA MANTER CLIENTE/CONTAS"""
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
        """Limpa apenas os campos do depósito atual, mantendo cliente e contas"""
        if hasattr(self, 'ids'):
            # 🔥 MANTÉM: spinner_cliente, spinner_conta_cliente, spinner_conta_empresa
            
            # 🔥 LIMPA APENAS:
            # Banco de origem
            if self.spinner_banco_origem:
                self.spinner_banco_origem.text = "Outro Banco"
                
            # Remetente
            self.ids.entry_remetente.text = ""
            
            # Valor
            self.ids.entry_valor.text = "0.00"
            
            # Campo "Outro Banco" se existir
            if self.campo_outro_banco:
                if self.campo_outro_banco.parent:
                    self.ids.layout_banco.remove_widget(self.campo_outro_banco)
                self.campo_outro_banco = None
            
            # Resetar altura do layout do banco
            if 'layout_banco' in self.ids:
                self.ids.layout_banco.height = dp(80)
            
            # 🔥 FOCAR NO PRÓXIMO CAMPO QUE SERÁ PREENCHIDO (BANCO DE ORIGEM)
            # Pequeno delay para garantir que a tela está pronta
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
        """Limpa TODOS os campos do formulário (para uso quando necessário)"""
        if hasattr(self, 'ids'):
            self.ids.spinner_cliente.text = "Selecione o cliente"
            self.ids.spinner_conta_cliente.values = []
            self.ids.spinner_conta_cliente.text = "Selecione a conta do cliente"
            self.ids.spinner_conta_empresa.values = []
            self.ids.spinner_conta_empresa.text = "Selecione a conta da empresa"
            
            # 🔥 CORREÇÃO: Usar referência direta
            if self.spinner_banco_origem:
                self.spinner_banco_origem.text = "Outro Banco"
                
            self.ids.entry_remetente.text = ""
            self.ids.entry_valor.text = ""
            
            # Limpar campo "Outro Banco" se existir
            if self.campo_outro_banco:
                if self.campo_outro_banco.parent:
                    self.ids.layout_banco.remove_widget(self.campo_outro_banco)
                self.campo_outro_banco = None
            
            # Resetar altura do layout do banco
            if 'layout_banco' in self.ids:
                self.ids.layout_banco.height = dp(80)
    
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
