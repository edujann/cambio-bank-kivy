from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from .campos import CampoValor
import datetime
import random



class TelaTransferencia(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.campos = {}
        self.beneficiario_preenchido = False
        self._scroll_view = None  # 🔥 NOVA VARIÁVEL para referência da ScrollView
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (550, 1000)
        print("📋 Tela de transferência carregada")
        print(f"🔍 DEBUG: beneficiario_preenchido = {self.beneficiario_preenchido}")
        
        # 🔥 CORREÇÃO: Só carregar contas - NUNCA limpar aqui
        self.carregar_contas_origem()
        self.carregar_beneficiarios()
        
        # 🔥 CORREÇÃO: Só limpar se NÃO veio de beneficiário
        if not self.beneficiario_preenchido:
            self.limpar_formulario()
        else:
            # Se veio de beneficiário, resetar a flag mas NÃO limpar
            self.beneficiario_preenchido = False
        
        # 🔥 NOVO: SEMPRE limpar campo valor e invoice, independente de como chegou na tela
        self.limpar_campos_transitorios()
        
        # 🔥 NOVO: Rolar para o topo após um pequeno delay
        self.rolar_para_topo()
    
    def on_enter(self):
        """Chamado quando a tela é carregada - CORRIGIDO"""
        print("📋 Carregando dados da transferência...")
        
        # 🔥 CORREÇÃO: Só recarregar se não veio de beneficiário
        if not self.beneficiario_preenchido:
            self.carregar_contas_origem()
            self.carregar_beneficiarios()
        
        # 🔥 GARANTIR que campos transitorios estão limpos
        self.limpar_campos_transitorios()
        
        # 🔥 NOVO: Garantir que está no topo
        self.rolar_para_topo()
    
    def rolar_para_topo(self):
        """Rola a ScrollView para o topo - VERSÃO ROBUSTA"""
        try:
            from kivy.clock import Clock
            
            def rolar(dt):
                try:
                    # Método 1: Buscar por ID específico
                    if hasattr(self, 'ids'):
                        if 'scroll_view_transferencia' in self.ids:
                            self.ids.scroll_view_transferencia.scroll_y = 1.0
                            print("✅ ScrollView rolada para o topo (via ID)")
                            return
                        
                        # Método 2: Tentar outros IDs possíveis
                        for id_name, widget in self.ids.items():
                            if 'scroll' in id_name.lower():
                                widget.scroll_y = 1.0
                                print(f"✅ ScrollView encontrada por '{id_name}' e rolada para o topo")
                                return
                    
                    # Método 3: Buscar na hierarquia
                    def encontrar_scrollview(widget):
                        if widget.__class__.__name__ == 'ScrollView':
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
                    print(f"❌ Erro durante rolagem: {e}")
            
            # Agendar múltiplas tentativas
            Clock.schedule_once(rolar, 0.1)  # Primeira tentativa
            Clock.schedule_once(rolar, 0.3)  # Segunda tentativa (backup)
            
        except Exception as e:
            print(f"⚠️ Erro ao agendar rolagem: {e}")
    
    def _rolar_para_topo_delay(self, dt):
        """Função auxiliar para rolar com delay"""
        try:
            # Encontrar a ScrollView na hierarquia
            if hasattr(self, 'ids'):
                # Procura por qualquer ScrollView nos filhos
                for child in self.children:
                    if child.__class__.__name__ == 'ScrollView':
                        child.scroll_y = 1.0  # 1.0 = topo, 0.0 = base
                        print("✅ ScrollView rolada para o topo")
                        return
                
                # Se não encontrou, tenta pelo ID (se existir)
                if 'scroll_view' in self.ids:
                    self.ids.scroll_view.scroll_y = 1.0
                    print("✅ ScrollView (por ID) rolada para o topo")
                else:
                    print("⚠️ ScrollView não encontrada para rolar ao topo")
                    
        except Exception as e:
            print(f"⚠️ Erro ao rolar para o topo: {e}")

    def on_leave(self):
        """Chamado quando sai da tela - prepara para próxima entrada"""
        # Garantir que ao voltar estará no topo
        self.rolar_para_topo()

    def preencher_dados_manual(self, dados_beneficiario):
        """Preenche os campos manualmente com dados do beneficiário"""
        print(f"🔍 DEBUG: Preenchendo dados manualmente para: {dados_beneficiario['nome']}")
        
        try:
            # 🔥 SETAR FLAG para evitar limpeza
            self.beneficiario_preenchido = True
            
            # Preencher todos os campos manualmente
            self.ids.entry_beneficiario.text = dados_beneficiario['nome']
            self.ids.entry_endereco.text = dados_beneficiario['endereco']
            self.ids.entry_cidade.text = dados_beneficiario['cidade']
            self.ids.entry_pais.text = dados_beneficiario['pais']
            self.ids.entry_banco.text = dados_beneficiario['banco']
            self.ids.endereco_banco.text = dados_beneficiario.get('endereco_banco', '')
            self.ids.cidade_banco.text = dados_beneficiario.get('cidade_banco', '')  # 🔥 NOVO
            self.ids.pais_banco.text = dados_beneficiario.get('pais_banco', '')      # 🔥 NOVO
            self.ids.entry_swift.text = dados_beneficiario['swift']
            self.ids.entry_iban.text = dados_beneficiario['iban']
            self.ids.entry_aba.text = dados_beneficiario.get('aba', '')
            
            print(f"✅ Dados preenchidos manualmente com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao preencher dados manualmente: {e}")

    def carregar_beneficiarios(self):
        """Carrega a lista de beneficiários salvos do usuário"""
        sistema = App.get_running_app().sistema
        
        print(f"🔍 DEBUG: Iniciando carregar_beneficiarios")
        print(f"🔍 DEBUG: Sistema tem beneficiarios? {hasattr(sistema, 'beneficiarios')}")
        
        if hasattr(self, 'ids') and 'combo_beneficiarios' in self.ids:
            try:
                # Obter beneficiários do usuário logado
                usuario_atual = sistema.usuario_logado
                print(f"🔍 DEBUG: Usuário atual: {usuario_atual}")
                
                # Verificar se o sistema tem a estrutura de beneficiários
                if not hasattr(sistema, 'beneficiarios'):
                    print("❌ DEBUG: Sistema não tem atributo 'beneficiarios'")
                    self.ids.combo_beneficiarios.values = [""]
                    self.ids.combo_beneficiarios.text = ""
                    return
                
                # 🔥 CORREÇÃO: DEFINIR a variável beneficiarios
                beneficiarios = sistema.beneficiarios.get(usuario_atual, [])
                print(f"🔍 DEBUG: Beneficiários encontrados: {len(beneficiarios)}")
                print(f"🔍 DEBUG: Beneficiários: {beneficiarios}")
                
                if not beneficiarios:
                    self.ids.combo_beneficiarios.values = [""]
                    self.ids.combo_beneficiarios.text = ""
                    print("Nenhum beneficiário salvo encontrado")
                    # 🔥 REMOVER binding antigo se existir
                    self.ids.combo_beneficiarios.unbind(text=self.preencher_dados_beneficiario)
                    # 🔥 ADICIONAR binding
                    self.ids.combo_beneficiarios.bind(text=self.preencher_dados_beneficiario)
                    
                else:
                    # Formatar lista de beneficiários
                    valores = [""]  # Opção vazia
                    for benef in beneficiarios:
                        nome_formatado = f"{benef['nome']} | {benef['banco']} | {benef['pais']}"
                        valores.append(nome_formatado)
                        print(f"🔍 DEBUG: Adicionando beneficiário: {nome_formatado}")
                    
                    self.ids.combo_beneficiarios.values = valores
                    self.ids.combo_beneficiarios.text = ""
                    print(f"✅ {len(beneficiarios)} beneficiários carregados no combo")
                    
                    # 🔥 ADICIONAR binding APÓS carregar os valores
                    self.ids.combo_beneficiarios.unbind(text=self.preencher_dados_beneficiario)
                    self.ids.combo_beneficiarios.bind(text=self.preencher_dados_beneficiario)
                    print("🔍 DEBUG: Binding adicionado ao combo_beneficiarios")
                    
            except Exception as e:
                print(f"❌ Erro ao carregar beneficiários: {e}")
                import traceback
                traceback.print_exc()
                # Fallback: inicializar com valor vazio
                self.ids.combo_beneficiarios.values = [""]
                self.ids.combo_beneficiarios.text = ""
    
    def carregar_contas_origem(self):
        """Carrega apenas contas USD, EUR, GBP - mesma lógica do Tkinter"""
        sistema = App.get_running_app().sistema
        
        if hasattr(self, 'ids') and 'conta_origem' in self.ids:
            # 🔥 CORREÇÃO: Obter dados do usuário corretamente
            usuario_data = sistema.usuarios.get(sistema.usuario_logado, {})
            
            # FILTRAR APENAS CONTAS USD, EUR, GBP - igual ao Tkinter
            contas_cliente = [conta for conta in usuario_data.get('contas', []) 
                            if sistema.contas[conta]['moeda'] in ['USD', 'EUR', 'GBP']]
            
            if not contas_cliente:
                self.ids.conta_origem.values = ["Nenhuma conta internacional disponível"]
                self.ids.conta_origem.text = "Nenhuma conta internacional disponível"
                return
            
            # Formatar como no Tkinter: "conta | moeda | Saldo: valor"
            valores = []
            for conta in contas_cliente:
                dados = sistema.contas[conta]
                texto = f"{conta} | {dados['moeda']} | Saldo: {dados['saldo']:,.2f}"
                valores.append(texto)
            
            self.ids.conta_origem.values = valores
            self.ids.conta_origem.text = valores[0]  # Seleciona o primeiro
            self.atualizar_info_conta()
    
    def atualizar_info_conta(self):
        """Atualiza informações da conta selecionada - igual ao Tkinter"""
        sistema = App.get_running_app().sistema
        
        if hasattr(self, 'ids') and 'conta_origem' in self.ids:
            conta_texto = self.ids.conta_origem.text
            if ' | ' in conta_texto:
                conta_selecionada = conta_texto.split(' | ')[0].strip()
                
                if conta_selecionada in sistema.contas:
                    dados = sistema.contas[conta_selecionada]
                    self.ids.info_conta_label.text = f"Saldo disponível: {dados['saldo']:,.2f} {dados['moeda']} | Moeda: {dados['moeda']}"
                    
                    # Atualiza label da moeda no campo valor
                    if 'moeda_label' in self.ids:
                        self.ids.moeda_label.text = dados['moeda']
    
    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        print("🧹 Limpando formulário completo")
        
        campos_para_limpar = [
            'entry_beneficiario', 'entry_endereco', 'entry_cidade', 'entry_pais',
            'entry_banco', 'endereco_banco', 'entry_swift', 'entry_iban', 'entry_aba',
            'text_descricao',
            'cidade_banco', 'pais_banco'  # 🔥 AQUI ADICIONE OS DOIS NOVOS CAMPOS
        ]
        
        for campo_id in campos_para_limpar:
            if hasattr(self, 'ids') and campo_id in self.ids:
                self.ids[campo_id].text = ''
        
        # 🔥 TRATAMENTO ESPECIAL para o campo de valor
        if hasattr(self, 'ids') and 'entry_valor_transferencia' in self.ids:
            self.ids.entry_valor_transferencia.text = "0.00"
            # Forçar o cursor para o final
            self.ids.entry_valor_transferencia.cursor = (4, 0)
        
        # 🔥 LIMPAR CAMPO INVOICE
        if hasattr(self, 'ids') and 'label_arquivo_invoice' in self.ids:
            self.ids.label_arquivo_invoice.text = "Nenhum arquivo selecionado"
            self.ids.label_arquivo_invoice.color = (0.7, 0.7, 0.7, 1)  # Cinza
        
        # 🔥 LIMPAR VARIÁVEL INTERNA DO INVOICE
        if hasattr(self, 'arquivo_invoice_selecionado'):
            self.arquivo_invoice_selecionado = None
        
        # Resetar combos
        if hasattr(self, 'ids'):
            if 'combo_finalidade' in self.ids:
                self.ids.combo_finalidade.text = "Pagamento de Serviços"
            
            if 'combo_beneficiarios' in self.ids:
                self.ids.combo_beneficiarios.text = ""
            
            if 'check_salvar_beneficiario' in self.ids:
                self.ids.check_salvar_beneficiario.active = False
            
            if 'conta_origem' in self.ids and self.ids.conta_origem.values:
                self.ids.conta_origem.text = self.ids.conta_origem.values[0]
                self.atualizar_info_conta()
        
        print("✅ Formulário limpo completamente")

    def limpar_campos_transitorios(self):
        """Limpa APENAS os campos que devem ser resetados a cada nova transferência"""
        print("🧹 Limpando campos transitorios (valor e invoice)")
        
        # 🔥 LIMPAR CAMPO VALOR
        if hasattr(self, 'ids') and 'entry_valor_transferencia' in self.ids:
            self.ids.entry_valor_transferencia.text = "0.00"
            # Forçar o cursor para o final
            self.ids.entry_valor_transferencia.cursor = (4, 0)
            print("✅ Campo valor resetado para '0.00'")
        
        # 🔥 LIMPAR CAMPO INVOICE
        if hasattr(self, 'ids') and 'label_arquivo_invoice' in self.ids:
            self.ids.label_arquivo_invoice.text = "Nenhum arquivo selecionado"
            self.ids.label_arquivo_invoice.color = (0.7, 0.7, 0.7, 1)  # Cinza
            print("✅ Campo invoice resetado")
        
        # 🔥 LIMPAR VARIÁVEL INTERNA DO INVOICE
        if hasattr(self, 'arquivo_invoice_selecionado'):
            self.arquivo_invoice_selecionado = None
            print("✅ Variável invoice resetada")
    
    def validar_formulario(self):
        """Valida todos os campos - VERSÃO SIMPLIFICADA"""
        sistema = App.get_running_app().sistema
        
        # Validar conta de origem
        if not self.ids.conta_origem.text or "Nenhuma conta" in self.ids.conta_origem.text:
            return False, "Selecione uma conta de origem válida"
        
        # Validar valor - usando o método get_valor_numerico
        try:
            valor = self.get_valor_numerico()
            
            if valor <= 0:
                return False, "Valor deve ser maior que zero"
            if valor < 0.01:
                return False, "Valor mínimo: 0.01"
                
            # Verificar saldo
            conta_texto = self.ids.conta_origem.text
            if ' | ' in conta_texto:
                conta_origem = conta_texto.split(' | ')[0].strip()
                saldo_atual = sistema.contas[conta_origem]['saldo']
                if valor > saldo_atual:
                    return False, f"Saldo insuficiente. Disponível: {saldo_atual:,.2f}"
                
        except ValueError:
            return False, "Valor inválido! Use apenas números"
        
        # Validar campos obrigatórios do beneficiário
        campos_obrigatorios = {
            'entry_beneficiario': 'Nome Completo do Beneficiário',
            'entry_endereco': 'Endereço Completo', 
            'entry_cidade': 'Cidade',
            'entry_pais': 'País',
            'entry_banco': 'Nome do Banco Destinatário',
            'cidade_banco': 'Cidade do Banco',  # 🔥 NOVO
            'pais_banco': 'País do Banco',      # 🔥 NOVO
            'entry_swift': 'Código SWIFT/BIC',
            'entry_iban': 'Código IBAN / Account #'
        }
        
        for campo_id, nome_campo in campos_obrigatorios.items():
            if not self.ids[campo_id].text.strip():
                return False, f"Preencha o campo: {nome_campo}"
        
        # Validar finalidade
        if not self.ids.combo_finalidade.text:
            return False, "Selecione a finalidade da transferência"
        
        return True, ""

    def get_valor_numerico(self):
        """Retorna o valor do campo como float usando o método da classe CampoValor"""
        print("🔍 DEBUG: get_valor_numerico CHAMADO!")
        
        if hasattr(self.ids.entry_valor_transferencia, 'get_valor_numerico'):
            print("🔍 DEBUG: Usando get_valor_numerico do CampoValor")
            return self.ids.entry_valor_transferencia.get_valor_numerico()
        else:
            print("🔍 DEBUG: Usando fallback")
            # Fallback caso o método não esteja disponível
            if not self.ids.entry_valor_transferencia.text:
                return 0.0
            
            try:
                texto_limpo = ''.join(filter(str.isdigit, self.ids.entry_valor_transferencia.text))
                if texto_limpo:
                    return float(texto_limpo) / 100.0
                return 0.0
            except (ValueError, AttributeError):
                return 0.0

    def solicitar_transferencia(self):
        """Processa a solicitação de transferência - ATUALIZADO COM SUPABASE"""
        sistema = App.get_running_app().sistema
        
        print("🌍 Processando solicitação de transferência...")
        
        # Validar formulário
        valido, mensagem = self.validar_formulario()
        if not valido:
            print(f"❌ {mensagem}")
            self.mostrar_erro_transferencia(mensagem)
            return
        
        try:
            # Extrair dados da conta de origem
            conta_texto = self.ids.conta_origem.text
            if ' | ' not in conta_texto:
                self.mostrar_erro_transferencia("Conta de origem inválida")
                return
                
            conta_origem = conta_texto.split(' | ')[0].strip()
            moeda_origem = sistema.contas[conta_origem]['moeda']
            
            # ✅ USAR MÉTODO get_valor_numerico PARA OBTER O VALOR
            valor = self.get_valor_numerico()
            print(f"💰 Valor processado: {valor}")
            
            # Preparar dados para o sistema
            dados_transferencia = {
                'conta_origem': conta_origem,
                'valor': valor,
                'finalidade': self.ids.combo_finalidade.text,
                'descricao': self.ids.text_descricao.text,
                'beneficiario': self.ids.entry_beneficiario.text.strip(),
                'endereco': self.ids.entry_endereco.text.strip(),
                'cidade': self.ids.entry_cidade.text.strip(),
                'pais': self.ids.entry_pais.text.strip(),
                'banco': self.ids.entry_banco.text.strip(),
                'endereco_banco': self.ids.endereco_banco.text.strip(),
                'cidade_banco': self.ids.cidade_banco.text.strip(),  # 🔥 NOVO
                'pais_banco': self.ids.pais_banco.text.strip(),      # 🔥 NOVO
                'swift': self.ids.entry_swift.text.strip(),
                'iban': self.ids.entry_iban.text.strip(),
                'aba': self.ids.entry_aba.text.strip()
            }
            
            # 🔥 ADICIONAR: Verificar se tem invoice selecionado
            tem_invoice = hasattr(self, 'arquivo_invoice_selecionado') and self.arquivo_invoice_selecionado
            
            # 🔥 ANEXAR INVOICE ANTES DE PROCESSAR A TRANSFERÊNCIA
            if tem_invoice:
                print("📎 Invoice detectado, anexando...")
                # Primeiro processa a transferência para obter o ID
                sucesso, resultado = sistema.solicitar_transferencia_internacional(dados_transferencia)
                
                if sucesso:
                    transferencia_id = resultado
                    print(f"✅ Transferência criada com ID: {transferencia_id}")
                    
                    # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
                    self.salvar_transferencia_supabase(dados_transferencia, transferencia_id, valor, moeda_origem)
                    
                    # Agora anexa a invoice
                    if self.anexar_invoice_transferencia(transferencia_id):
                        print(f"✅ Invoice anexado com sucesso à transferência {transferencia_id}")
                    else:
                        print(f"⚠️ Invoice não pôde ser anexado à transferência {transferencia_id}")
                    
                    # Continuar com o processo normal
                    conta_origem = dados_transferencia['conta_origem']
                    novo_saldo = sistema.contas[conta_origem]['saldo']
                    
                    beneficiario_salvo = False
                    if self.ids.check_salvar_beneficiario.active:
                        dados_beneficiario = {
                            'nome': dados_transferencia['beneficiario'],
                            'endereco': dados_transferencia['endereco'],
                            'cidade': dados_transferencia['cidade'],
                            'pais': dados_transferencia['pais'],
                            'banco': dados_transferencia['banco'],
                            'endereco_banco': dados_transferencia['endereco_banco'],
                            'cidade_banco': dados_transferencia['cidade_banco'],  # 🔥 NOVO
                            'pais_banco': dados_transferencia['pais_banco'],      # 🔥 NOVO
                            'swift': dados_transferencia['swift'],
                            'iban': dados_transferencia['iban'],
                            'aba': dados_transferencia['aba']
                        }
                        sistema.salvar_beneficiario(dados_beneficiario)
                        beneficiario_salvo = True
                    
                    # MOSTRAR POPUP DE SUCESSO
                    self.mostrar_sucesso_transferencia(
                        dados_transferencia, 
                        transferencia_id, 
                        valor, 
                        moeda_origem, 
                        novo_saldo,
                        beneficiario_salvo
                    )
                    
                else:
                    print(f"❌ Erro na transferência: {resultado}")
                    self.mostrar_erro_transferencia(resultado)
            else:
                # Processamento normal sem invoice
                print("ℹ️ Nenhum invoice selecionado, processando transferência normalmente")
                sucesso, resultado = sistema.solicitar_transferencia_internacional(dados_transferencia)
                
                if sucesso:
                    transferencia_id = resultado
                    
                    # 🔥🔥🔥 NOVO: SALVAR NO SUPABASE APÓS SUCESSO NO SISTEMA ATUAL
                    self.salvar_transferencia_supabase(dados_transferencia, transferencia_id, valor, moeda_origem)
                    
                    conta_origem = dados_transferencia['conta_origem']
                    novo_saldo = sistema.contas[conta_origem]['saldo']
                    
                    beneficiario_salvo = False
                    if self.ids.check_salvar_beneficiario.active:
                        dados_beneficiario = {
                            'nome': dados_transferencia['beneficiario'],
                            'endereco': dados_transferencia['endereco'],
                            'cidade': dados_transferencia['cidade'],
                            'pais': dados_transferencia['pais'],
                            'banco': dados_transferencia['banco'],
                            'endereco_banco': dados_transferencia['endereco_banco'],
                            'cidade_banco': dados_transferencia['cidade_banco'],  # 🔥 NOVO
                            'pais_banco': dados_transferencia['pais_banco'],      # 🔥 NOVO
                            'swift': dados_transferencia['swift'],
                            'iban': dados_transferencia['iban'],
                            'aba': dados_transferencia['aba']
                        }
                        sistema.salvar_beneficiario(dados_beneficiario)
                        beneficiario_salvo = True
                    
                    # MOSTRAR POPUP DE SUCESSO
                    self.mostrar_sucesso_transferencia(
                        dados_transferencia, 
                        transferencia_id, 
                        valor, 
                        moeda_origem, 
                        novo_saldo,
                        beneficiario_salvo
                    )
                else:
                    print(f"❌ Erro na transferência: {resultado}")
                    self.mostrar_erro_transferencia(resultado)
            
        except Exception as e:
            print(f"❌ Erro ao processar transferência: {e}")
            self.mostrar_erro_transferencia(f"Erro interno: {str(e)}")

    def salvar_transferencia_supabase(self, dados_transferencia, transferencia_id, valor, moeda_origem):
        """Salva a transferência no Supabase - VERSÃO CORRIGIDA SEM DUPLICAÇÃO"""
        try:
            from datetime import datetime
            
            sistema = App.get_running_app().sistema
            
            print(f"🔥 SALVAR_TRANSFERENCIA_SUPABASE (VERSÃO CORRIGIDA)")
            print(f"   ID: {transferencia_id}")
            print(f"   Valor: {valor} {moeda_origem}")
            print(f"   Usuário: {sistema.usuario_logado}")
            
            # 🔥 CORREÇÃO: Usar SupabaseManager em vez de serviço antigo
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # 🔥 NOVO: VERIFICAR SE JÁ EXISTE ANTES DE SALVAR
                    print(f"🔍 Verificando se transferência {transferencia_id} já existe no Supabase...")
                    response_existente = sistema.supabase.client.table('transferencias')\
                        .select('id')\
                        .eq('id', transferencia_id)\
                        .execute()
                    
                    if response_existente.data:
                        print(f"✅ Transferência {transferencia_id} JÁ EXISTE no Supabase (evitando duplicação)")
                        return True
                    
                    print(f"🔍 Transferência {transferencia_id} não existe, prosseguindo com salvamento...")
                    
                    # 🔥 PREPARAR DADOS COM MESMO PADRÃO DAS OUTRAS TELAS
                    dados_supabase = {
                        'id': transferencia_id,
                        'tipo': 'transferencia_internacional',
                        'status': 'solicitada',
                        'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'moeda': moeda_origem,
                        'valor': valor,
                        'conta_remetente': dados_transferencia['conta_origem'],
                        'descricao': dados_transferencia.get('descricao', ''),
                        'usuario': sistema.usuario_logado,
                        'cliente': sistema.usuario_logado,
                        'beneficiario': dados_transferencia['beneficiario'],
                        'endereco_beneficiario': dados_transferencia['endereco'],
                        'cidade': dados_transferencia['cidade'],
                        'pais': dados_transferencia['pais'],
                        'nome_banco': dados_transferencia['banco'],
                        'endereco_banco': dados_transferencia.get('endereco_banco', ''),
                        'cidade_banco': dados_transferencia.get('cidade_banco', ''),  # 🔥 NOVO
                        'pais_banco': dados_transferencia.get('pais_banco', ''),      # 🔥 NOVO
                        'codigo_swift': dados_transferencia['swift'],
                        'iban_account': dados_transferencia['iban'],
                        'aba_routing': dados_transferencia.get('aba', ''),
                        'finalidade': dados_transferencia['finalidade'],
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    print(f"🔥 Dados preparados para Supabase:")
                    print(f"   ID: {dados_supabase['id']}")
                    print(f"   Tipo: {dados_supabase['tipo']}")
                    print(f"   Beneficiário: {dados_supabase['beneficiario']}")
                    
                    # 🔥 CORREÇÃO: Usar método do SupabaseManager
                    sucesso = sistema.supabase.salvar_transacao(dados_supabase)
                    
                    if sucesso:
                        print(f"✅✅✅ TRANSFERÊNCIA SALVA NO SUPABASE: {transferencia_id}")
                        return True
                    else:
                        print(f"❌❌❌ FALHA: Transferência NÃO salva no Supabase")
                        return False
                        
                except Exception as e:
                    print(f"❌ Erro ao salvar transferência no Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("❌ Supabase não disponível - transferência salva apenas localmente")
                return False
                
        except Exception as e:
            print(f"❌ Erro geral em salvar_transferencia_supabase: {e}")
            import traceback
            traceback.print_exc()
            return False

# === CORREÇÃO NO MÉTODO mostrar_confirmacao_transferencia ===

    def mostrar_confirmacao_transferencia(self, dados_transferencia, valor, moeda_origem, tem_invoice=False):
        """Mostra popup de confirmação antes de processar a transferência - VERSÃO CORRIGIDA"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Título
        lbl_titulo = Label(
            text='🔍 CONFIRMAR TRANSFERÊNCIA',
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True,
            text_size=(400, None),
            halign='center'
        )
        
        # Detalhes da transferência - INCLUINDO INFO DO INVOICE
        detalhes = f"""
 VALOR: {valor:,.2f} {moeda_origem}
 BENEFICIÁRIO: {dados_transferencia['beneficiario']}
 BANCO: {dados_transferencia['banco']}
 PAÍS: {dados_transferencia['pais']}
 FINALIDADE: {dados_transferencia['finalidade']}
 CONTA ORIGEM: {dados_transferencia['conta_origem']}
        """.strip()
        
        # Adicionar informação do invoice se existir
        if tem_invoice:
            detalhes += "\n📎 INVOICE:  ANEXADO"
        else:
            detalhes += "\n📎 INVOICE:  NÃO ANEXADO"
        
        detalhes += "\n\n Esta operação não pode ser desfeita."
        
        lbl_detalhes = Label(
            text=detalhes,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            text_size=(400, None),
            halign='left'
        )
        
        # Botões
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text=' CANCELAR',
            background_color=(0.96, 0.36, 0.36, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text=' CONFIRMAR',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_detalhes)
        content.add_widget(botoes_layout)
        
        # Criar popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 380 if tem_invoice else 350),  # Ajusta altura se tem invoice
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            """Chamado quando confirma a transferência"""
            popup.dismiss()
            self.processar_transferencia_apos_confirmacao(dados_transferencia, valor, moeda_origem)
        
        def cancelar(instance):
            """Chamado quando cancela"""
            popup.dismiss()
            print(" Transferência cancelada pelo usuário")
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        # Mostrar popup
        popup.open()

    def processar_transferencia_apos_confirmacao(self, dados_transferencia, valor, moeda_origem):
        """Processa a transferência após confirmação do usuário"""
        sistema = App.get_running_app().sistema
        
        print(" Processando transferência após confirmação...")
        
        try:
            beneficiario_salvo = False
            
            # SALVAR BENEFICIÁRIO SE SOLICITADO
            if self.ids.check_salvar_beneficiario.active:
                dados_beneficiario = {
                    'nome': dados_transferencia['beneficiario'],
                    'endereco': dados_transferencia['endereco'],
                    'cidade': dados_transferencia['cidade'],
                    'pais': dados_transferencia['pais'],
                    'banco': dados_transferencia['banco'],
                    'endereco_banco': dados_transferencia.get('endereco_banco', ''),
                    'cidade_banco': dados_transferencia.get('cidade_banco', ''),  # 🔥 NOVO
                    'pais_banco': dados_transferencia.get('pais_banco', ''),      # 🔥 NOVO
                    'swift': dados_transferencia['swift'],
                    'iban': dados_transferencia['iban'],
                    'aba': dados_transferencia.get('aba', '')
                }
                sistema.salvar_beneficiario(dados_beneficiario)
                beneficiario_salvo = True
                print(f" Beneficiário '{dados_transferencia['beneficiario']}' salvo!")
            
            # SOLICITAR TRANSFERÊNCIA NO SISTEMA
            sucesso, resultado = sistema.solicitar_transferencia_internacional(dados_transferencia)
            
            if sucesso:
                transferencia_id = resultado
                conta_origem = dados_transferencia['conta_origem']
                novo_saldo = sistema.contas[conta_origem]['saldo']
                
                print(f" TRANSFERÊNCIA SOLICITADA COM SUCESSO!")
                print(f"    ID: {transferencia_id}")
                
                # MOSTRAR POPUP DE SUCESSO
                self.mostrar_sucesso_transferencia(
                    dados_transferencia, 
                    transferencia_id, 
                    valor, 
                    moeda_origem, 
                    novo_saldo,
                    beneficiario_salvo
                )
                
            else:
                print(f" Erro na transferência: {resultado}")
                self.mostrar_erro_transferencia(resultado)
            
        except Exception as e:
            print(f" Erro ao processar transferência: {e}")
            self.mostrar_erro_transferencia(f"Erro interno: {str(e)}")

    def cancelar_transferencia(self):
        """Cancela e volta ao dashboard"""
        print(" Transferência cancelada")
        self.manager.current = 'dashboard'

    def preencher_dados_beneficiario(self, instance, value):
        """Preenche automaticamente os campos quando um beneficiário é selecionado"""
        print(f"🔍 DEBUG: preencher_dados_beneficiario chamado - valor: '{value}'")
        
        if not value or value == "":  # Se selecionou a opção vazia
            # Limpar campos se selecionou opção vazia
            print("🔍 DEBUG: Opção vazia selecionada, limpando campos")
            self.limpar_campos_beneficiario()
            return
        
        sistema = App.get_running_app().sistema
        usuario_atual = sistema.usuario_logado
        
        try:
            # Encontrar o beneficiário selecionado
            beneficiarios = sistema.beneficiarios.get(usuario_atual, [])
            print(f"🔍 DEBUG: {len(beneficiarios)} beneficiários encontrados para {usuario_atual}")
            
            # Extrair o nome do beneficiário do texto formatado
            nome_beneficiario = value.split(' | ')[0]
            print(f"🔍 DEBUG: Buscando beneficiário: '{nome_beneficiario}'")
            
            for benef in beneficiarios:
                print(f"🔍 DEBUG: Comparando com: '{benef['nome']}'")
                if benef['nome'] == nome_beneficiario:
                    # Preencher todos os campos com os dados do beneficiário
                    self.ids.entry_beneficiario.text = benef['nome']
                    self.ids.entry_endereco.text = benef['endereco']
                    self.ids.entry_cidade.text = benef['cidade']
                    self.ids.entry_pais.text = benef['pais']
                    self.ids.entry_banco.text = benef['banco']
                    self.ids.endereco_banco.text = benef.get('endereco_banco', '')
                    self.ids.cidade_banco.text = benef.get('cidade_banco', '')  # 🔥 NOVO
                    self.ids.pais_banco.text = benef.get('pais_banco', '')      # 🔥 NOVO
                    self.ids.entry_swift.text = benef['swift']
                    self.ids.entry_iban.text = benef['iban']
                    self.ids.entry_aba.text = benef.get('aba', '')
                    
                    print(f" Dados do beneficiário '{benef['nome']}' preenchidos automaticamente")
                    print(f" DEBUG: Campo beneficiário preenchido: '{self.ids.entry_beneficiario.text}'")
                    break
            else:
                print(f" DEBUG: Beneficiário '{nome_beneficiario}' não encontrado na lista")
                    
        except Exception as e:
            print(f" Erro ao preencher dados do beneficiário: {e}")
            import traceback
            traceback.print_exc()

    def limpar_campos_beneficiario(self):
        """Limpa apenas os campos do beneficiário"""
        campos_beneficiario = [
            'entry_beneficiario', 'entry_endereco', 'entry_cidade', 'entry_pais',
            'entry_banco', 'endereco_banco', 'cidade_banco', 'pais_banco',  # 🔥 ATUALIZADO
            'entry_swift', 'entry_iban', 'entry_aba'
        ]
        
        for campo_id in campos_beneficiario:
            if hasattr(self, 'ids') and campo_id in self.ids:
                self.ids[campo_id].text = ''

    def mostrar_sucesso_transferencia(self, dados_transferencia, transferencia_id, valor, moeda_origem, novo_saldo, beneficiario_salvo=False):
        """Mostra popup de sucesso quando transferência é solicitada"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Mensagem de sucesso
        lbl_sucesso = Label(
            text=' TRANSFERÊNCIA SOLICITADA COM SUCESSO!',
            color=(0.2, 0.8, 0.2, 1),  # Verde para sucesso
            font_size='16sp',
            bold=True,
            text_size=(400, None),
            halign='center'
        )
        
        # Detalhes da transferência
        detalhes = f"""
 ID: {transferencia_id}
 Valor: {valor:,.2f} {moeda_origem}
 Beneficiário: {dados_transferencia['beneficiario']}
 Banco: {dados_transferencia['banco']}
 Status: Aguardando processamento
 Novo saldo: {novo_saldo:,.2f} {moeda_origem}
        """.strip()
        
        # Adicionar mensagem do beneficiário se foi salvo
        if beneficiario_salvo:
            detalhes += "\n\n✅ BENEFICIÁRIO SALVO COM SUCESSO!"
        
        lbl_detalhes = Label(
            text=detalhes,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            text_size=(400, None),
            halign='left'
        )
        
        # Botão OK
        btn_ok = Button(
            text='VOLTAR AO DASHBOARD',
            size_hint_y=None,
            height=45,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(lbl_detalhes)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title=' Transferência Solicitada',
            title_color=(0.2, 0.8, 0.2, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(450, 400 if beneficiario_salvo else 350),
            background_color=(0.12, 0.16, 0.23, 1),
            separator_color=(0.55, 0.36, 0.96, 1),
            auto_dismiss=False
        )
        
        # Fechar popup e voltar ao dashboard
        def voltar_dashboard(instance):
            popup.dismiss()
            self.manager.current = 'dashboard'
        
        btn_ok.bind(on_press=voltar_dashboard)
        
        # Mostrar popup
        popup.open()

    def mostrar_erro_transferencia(self, mensagem):
        """Mostra popup de erro para transferência falha"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensagem de erro
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        # Botão OK
        btn_ok = Button(
            text='TENTAR NOVAMENTE',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title=' Erro na Transferência',
            title_color=(1, 0.3, 0.3, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # Fechar popup ao clicar OK
        btn_ok.bind(on_press=popup.dismiss)
        
        # Mostrar popup
        popup.open()

    def mostrar_sucesso_beneficiario(self, nome_beneficiario):
        """Mostra popup de sucesso quando beneficiário é salvo"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Criar conteúdo do popup
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Mensagem de sucesso
        lbl_sucesso = Label(
            text=' BENEFICIÁRIO SALVO COM SUCESSO!',
            color=(0.2, 0.8, 0.2, 1),
            font_size='16sp',
            bold=True,
            text_size=(400, None),
            halign='center'
        )
        
        # Detalhes do beneficiário
        detalhes = f"""
 Nome: {nome_beneficiario}
 Status: Salvo na sua lista
 Uso: Disponível para futuras transferências
        """.strip()
        
        lbl_detalhes = Label(
            text=detalhes,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            text_size=(400, None),
            halign='center'
        )
        
        # Botão OK
        btn_ok = Button(
            text='CONTINUAR',
            size_hint_y=None,
            height=40,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(lbl_detalhes)
        content.add_widget(btn_ok)
        
        # Criar popup
        popup = Popup(
            title='👤 Beneficiário Salvo',
            title_color=(0.2, 0.8, 0.2, 1),
            title_size='16sp',
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        # Fechar popup
        btn_ok.bind(on_press=popup.dismiss)
        
        # Mostrar popup
        popup.open()

    def cancelar_transferencia(self):
        """Volta para o dashboard"""
        print(" Transferência cancelada")
        self.manager.current = 'dashboard'

# === MÉTODOS PARA TelaTransferencia ===

    def selecionar_invoice(self):
        """Abre seletor SUPER simplificado com drag & drop"""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            from kivy.uix.label import Label
            from kivy.uix.filechooser import FileChooserListView
            import os
            
            # Criar popup minimalista
            content = BoxLayout(orientation='vertical', spacing=15, padding=25)
            
            # Título amigável
            lbl_titulo = Label(
                text='[b]ANEXAR INVOICE[/b]',
                markup=True,
                color=(0.9, 0.9, 0.9, 1),
                font_size='18sp',
                size_hint_y=0.2,
                text_size=(400, None),
                halign='center'
            )
            
            # Área de Drag & Drop
            area_drag_drop = Button(
                text='[b]SOLTE O ARQUIVO AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)',
                markup=True,
                background_color=(0.2, 0.3, 0.4, 0.3),
                background_normal='',
                color=(0.8, 0.8, 0.8, 1),
                font_size='14sp',
                size_hint_y=0.4,
                halign='center'
            )
            
            # Pastas rápidas
            pastas_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
            
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
            botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
            
            btn_limpar = Button(
                text='Limpar',
                background_color=(0.8, 0.3, 0.3, 1),
                font_size='12sp'
            )
            
            btn_fechar = Button(
                text='Concluir',
                background_color=(0.2, 0.7, 0.3, 1),
                font_size='14sp',
                bold=True
            )
            
            botoes_layout.add_widget(btn_limpar)
            botoes_layout.add_widget(btn_fechar)
            
            content.add_widget(lbl_titulo)
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
                size_hint=(0.85, 0.6),
                background_color=(0.12, 0.16, 0.23, 1),
                auto_dismiss=False
            )
            
            def atualizar_status(nome_arquivo, sucesso=True):
                """Atualiza o status visual"""
                nonlocal lbl_status
                
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                
                if sucesso:
                    texto = f'✅ [b]{nome_arquivo}[/b]\nPronto para anexar!'
                    cor = (0.2, 0.8, 0.2, 1)
                else:
                    texto = f'❌ {nome_arquivo}'
                    cor = (1, 0.3, 0.3, 1)
                
                lbl_status = Label(
                    text=texto,
                    markup=True,
                    color=cor,
                    font_size='12sp',
                    size_hint_y=0.15,
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
                    self.selecionar_invoice()  # Reabre o popup simples
                
                def escolher_arquivo(instance=None, selection=None, touch=None):
                    """Função corrigida para aceitar diferentes chamadas"""
                    if filechooser.selection:
                        caminho = filechooser.selection[0]
                        if processar_arquivo(caminho):
                            popup_avancado.dismiss()
                    else:
                        lbl_instrucao.text = 'Selecione um arquivo!'
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
                area_drag_drop.text = '[b]SOLTE O ARQUIVO AQUI[/b]\n\nou clique para procurar\n\n📄 PDF, JPG, PNG (até 5MB)'
                area_drag_drop.background_color = (0.2, 0.3, 0.4, 0.3)
                
                # Remover status
                nonlocal lbl_status
                if lbl_status and lbl_status in content.children:
                    content.remove_widget(lbl_status)
                    content.do_layout()
            
            def finalizar(instance):
                """Finaliza o processo"""
                if arquivo_selecionado:
                    self.processar_arquivo_selecionado(arquivo_selecionado)
                    popup.dismiss()
                    self.mostrar_mensagem_sucesso("Invoice anexado com sucesso!")
                else:
                    atualizar_status("Nenhum arquivo selecionado!", False)
            
            # Bind dos eventos
            area_drag_drop.bind(on_press=abrir_seletor_generico)
            btn_documentos.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Documents')))
            btn_downloads.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Downloads')))
            btn_desktop.bind(on_press=lambda x: abrir_seletor_pasta(os.path.expanduser('~/Desktop')))
            btn_limpar.bind(on_press=limpar_selecao)
            btn_fechar.bind(on_press=finalizar)
            
            # 🔥 CORREÇÃO: Suporte a drag & drop real - função corrigida
            def on_dropfile(window, file_path, *args):
                """Processa arquivo arrastado para a janela - VERSÃO COMPATÍVEL"""
                try:
                    file_path_str = file_path.decode('utf-8') if isinstance(file_path, bytes) else str(file_path)
                    if processar_arquivo(file_path_str):
                        print(f"✅ Arquivo arrastado processado: {file_path_str}")
                except Exception as e:
                    print(f"❌ Erro ao processar arquivo arrastado: {e}")

            # ✅ ADICIONAR: Binding do evento ORIGINAL
            from kivy.core.window import Window
            Window.bind(on_dropfile=on_dropfile)    # ✅ ORIGINAL QUE FUNCIONA

            # Limpar binding quando popup fechar
            def on_dismiss(instance):
                from kivy.core.window import Window
                Window.unbind(on_dropfile=on_dropfile)  # ✅ ORIGINAL QUE FUNCIONA
            
            popup.bind(on_dismiss=on_dismiss)
            
            # Abrir popup
            popup.open()
            
        except Exception as e:
            print(f"❌ Erro ao abrir seletor de arquivos: {e}")
            self.mostrar_erro_simples("Erro ao abrir seletor de arquivos")

    # Manter estas funções auxiliares (elas já estão boas)
    def mostrar_mensagem_sucesso(self, mensagem):
        """Mostra mensagem de sucesso simples - VERSÃO COM BOTÃO"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl = Label(
            text=mensagem, 
            color=(0.2, 0.8, 0.2, 1), 
            font_size='16sp',
            text_size=(350, None),
            halign='center'
        )
        
        # 🔥 ADICIONAR BOTÃO OK
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
        content.add_widget(btn_ok)  # 🔥 ADICIONAR BOTÃO
        
        popup = Popup(
            title='Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(0.7, 0.4),  # 🔥 AUMENTAR ALTURA PARA O BOTÃO
            auto_dismiss=False,    # 🔥 NÃO FECHAR SOZINHO
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        # 🔥 ADICIONAR FUNÇÃO PARA FECHAR
        def fechar_popup(instance):
            popup.dismiss()
        
        btn_ok.bind(on_press=fechar_popup)
        
        popup.open()

    def mostrar_erro_simples(self, mensagem):
        """Mostra mensagem de erro simples"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20)
        lbl = Label(text=mensagem, color=(1, 0.3, 0.3, 1), font_size='16sp')
        content.add_widget(lbl)
        
        popup = Popup(
            title=' Erro',
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=True,
            background_color=(0.12, 0.16, 0.23, 1)
        )
        popup.open()

    def processar_arquivo_selecionado(self, caminho_arquivo):
        """Processa o arquivo de invoice selecionado - VERSÃO SIMPLIFICADA"""
        try:
            import os
            
            # Verificar tamanho do arquivo (máx 5MB)
            tamanho_arquivo = os.path.getsize(caminho_arquivo) / (1024 * 1024)  # MB
            if tamanho_arquivo > 5:
                self.mostrar_erro_simples("Arquivo muito grande! Escolha um arquivo menor que 5MB.")
                return
            
            # Obter nome do arquivo
            nome_arquivo = os.path.basename(caminho_arquivo)
            
            # Atualizar interface de forma mais amigável
            self.ids.label_arquivo_invoice.text = f"📎 {nome_arquivo} ({tamanho_arquivo:.1f} MB)"
            self.ids.label_arquivo_invoice.color = (0.2, 0.8, 0.2, 1)  # Verde
            self.arquivo_invoice_selecionado = caminho_arquivo
            
            print(f" Invoice selecionado: {nome_arquivo}")
            
        except Exception as e:
            print(f" Erro ao processar arquivo: {e}")
            self.mostrar_erro_simples("Erro ao processar arquivo. Tente novamente.")

    def copiar_arquivo_invoice(self, caminho_origem, transferencia_id):
        """Copia o arquivo para Supabase Storage - ÚNICA ALTERAÇÃO"""
        try:
            import os
            from datetime import datetime
            
            # 🔥 USAR SEU SUPABASEMANAGER EXISTENTE
            sistema = App.get_running_app().sistema
            if not hasattr(sistema, 'supabase') or not sistema.supabase.conectado:
                print("❌ Supabase não disponível - usando fallback local")
                # Fallback: copiar para pasta local (compatibilidade)
                pasta_invoices = 'data/invoices'
                if not os.path.exists(pasta_invoices):
                    os.makedirs(pasta_invoices)
                
                nome_arquivo = os.path.basename(caminho_origem)
                nome_base, extensao = os.path.splitext(nome_arquivo)
                novo_nome = f"{transferencia_id}_{nome_base}{extensao}"
                caminho_destino = os.path.join(pasta_invoices, novo_nome)
                
                import shutil
                shutil.copy2(caminho_origem, caminho_destino)
                return caminho_destino
            
            # ✅ SUPABASE: Gerar nome único
            nome_arquivo = os.path.basename(caminho_origem)
            nome_base, extensao = os.path.splitext(nome_arquivo)
            timestamp = int(datetime.now().timestamp() * 1000)
            novo_nome = f"{timestamp}_{nome_base}{extensao}"
            
            # Caminho no Supabase
            caminho_supabase = f"transferencias/{transferencia_id}/{novo_nome}"
            
            # Fazer upload
            with open(caminho_origem, 'rb') as file:
                file_data = file.read()
            
            try:
                response = sistema.supabase.client.storage.from_("invoices").upload(
                    caminho_supabase, 
                    file_data
                )
                
                # ✅ SE CHEGOU AQUI, UPLOAD FOI BEM-SUCEDIDO
                print(f"✅ Upload Supabase bem-sucedido: {caminho_supabase}")
                return caminho_supabase
                
            except Exception as e:
                print(f"❌ Erro no upload Supabase: {e}")
                # Continuar para fallback local
                # Fallback para local se Supabase falhar
                pasta_invoices = 'data/invoices'
                if not os.path.exists(pasta_invoices):
                    os.makedirs(pasta_invoices)
                
                nome_arquivo = os.path.basename(caminho_origem)
                nome_base, extensao = os.path.splitext(nome_arquivo)
                novo_nome = f"{transferencia_id}_{nome_base}{extensao}"
                caminho_destino = os.path.join(pasta_invoices, novo_nome)
                
                import shutil
                shutil.copy2(caminho_origem, caminho_destino)
                return caminho_destino
            
            print(f"✅ Invoice salvo no Supabase: {caminho_supabase}")
            return caminho_supabase
            
        except Exception as e:
            print(f"❌ Erro ao copiar invoice: {e}")
            return None

    def anexar_invoice_transferencia(self, transferencia_id):
        """Anexa o invoice selecionado à transferência - VERSÃO COM DEBUG"""
        try:
            print(f"🔍 DEBUG ANEXAR INVOICE: Iniciando anexação para {transferencia_id}")
            
            if not hasattr(self, 'arquivo_invoice_selecionado') or not self.arquivo_invoice_selecionado:
                print(" Nenhum invoice selecionado para anexar")
                return True  # Não é obrigatório, então retorna sucesso
            
            sistema = App.get_running_app().sistema
            
            print(f"🔍 DEBUG ANEXAR INVOICE: Copiando arquivo...")
            # Copiar arquivo para pasta do sistema
            caminho_destino = self.copiar_arquivo_invoice(self.arquivo_invoice_selecionado, transferencia_id)
            
            if caminho_destino:
                print(f"🔍 DEBUG ANEXAR INVOICE: Arquivo copiado, adicionando ao sistema...")
                # Adicionar informações ao sistema
                sucesso = sistema.adicionar_invoice_info_transferencia(transferencia_id, caminho_destino)
                
                if sucesso:
                    print(f"Invoice anexado à transferência {transferencia_id}")
                    return True
                else:
                    print(f"Erro ao anexar invoice à transferência")
                    return False
            else:
                print(f"Erro ao copiar arquivo de invoice")
                return False
                
        except Exception as e:
            print(f"Erro ao anexar invoice: {e}")
            return False

    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
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