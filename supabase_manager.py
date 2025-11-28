# supabase_manager.py
import os
from supabase import create_client, Client
#from config_supabase import SupabaseConfig

class SupabaseManager:
    def __init__(self):
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if url and key:
            self.client: Client = create_client(url, key)
            self.conectado = True
            print("✅ Conectado ao Supabase via variáveis de ambiente!")
        else:
            self.client = None
            self.conectado = False
            print("⚠️ Supabase não configurado - usando JSON local")
    
    # 👤 MÉTODOS DE USUÁRIOS
    def obter_usuarios(self):
        """Obtém todos os usuários do Supabase"""
        try:
            response = self.client.table('usuarios').select('*').execute()
            return {user['username']: user for user in response.data}
        except Exception as e:
            print(f"❌ Erro ao obter usuários: {e}")
            return {}
    
    def obter_usuario(self, username):
        """Obtém um usuário pelo username - VERSÃO CORRIGIDA"""
        try:
            response = self.client.table('usuarios')\
                .select('*')\
                .eq('username', username)\
                .execute()
            
            if response.data:
                usuario = response.data[0]
                # 🔥 CORREÇÃO: Mapear TODAS as colunas corretas
                if 'senha_hash' in usuario:
                    usuario['senha'] = usuario['senha_hash']
                if 'documento_hash' in usuario:
                    usuario['documento'] = usuario['documento_hash']
                if 'contas' in usuario:
                    usuario['moedas_selecionadas'] = usuario['contas']
                # Mapear outras colunas se necessário
                return usuario
            return None
        except Exception as e:
            print(f"❌ Erro ao obter usuário: {e}")
            return None

    def salvar_usuario(self, dados_usuario):
        """Salva/atualiza usuário no Supabase - VERSÃO CORRIGIDA"""
        try:
            import hashlib
            from datetime import datetime
            
            # 🔥 CORREÇÃO: Sempre fazer hash da senha
            senha_original = dados_usuario['senha']
            senha_hash = hashlib.sha256(senha_original.encode()).hexdigest()
            
            # 🔥 CORREÇÃO CRÍTICA: Não salvar moedas na coluna 'contas'
            # A coluna 'contas' deve armazenar IDs de contas, não moedas!
            usuario_data = {
                'username': dados_usuario['username'],
                'senha_hash': senha_hash,
                'nome': dados_usuario['nome'],
                'email': dados_usuario['email'],
                'documento_hash': dados_usuario['documento'],
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': '',
                'cidade': '',
                'cep': '',
                'estado': '',
                'pais': '',
                'tipo': 'cliente',
                'contas': [],  # 🔥 CORREÇÃO: Array vazio - serão preenchidas depois
                'data_cadastro': datetime.now().isoformat()
            }
            
            # Verificar se usuário já existe
            usuario_existente = self.obter_usuario(dados_usuario['username'])
            
            if usuario_existente:
                # Atualizar usuário existente
                response = self.client.table('usuarios')\
                    .update(usuario_data)\
                    .eq('username', dados_usuario['username'])\
                    .execute()
            else:
                # Criar novo usuário
                response = self.client.table('usuarios')\
                    .insert(usuario_data)\
                    .execute()
            
            # 🔥 CORREÇÃO: Criar contas e atualizar usuário com IDs reais
            if response.data:
                sistema = App.get_running_app().sistema
                moedas_selecionadas = dados_usuario.get('moedas_selecionadas', [])
                
                # Criar contas no Supabase
                ids_contas = sistema.criar_contas_supabase(
                    dados_usuario['username'], 
                    moedas_selecionadas
                )
                
                # Atualizar usuário com IDs das contas
                if ids_contas:
                    usuario_data['contas'] = ids_contas
                    response_update = self.client.table('usuarios')\
                        .update({'contas': ids_contas})\
                        .eq('username', dados_usuario['username'])\
                        .execute()
                    print(f"✅ Usuário atualizado com IDs das contas: {ids_contas}")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar usuário: {e}")
            return False
    
    def atualizar_usuario(self, username, dados_atualizados):
        """Atualiza usuário no Supabase"""
        try:
            response = self.client.table('usuarios')\
                .update(dados_atualizados)\
                .eq('username', username)\
                .execute()
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar usuário: {e}")
            return False



    # 🔐 MÉTODOS DE AUTENTICAÇÃO (para depois)
    def cadastrar_usuario_auth(self, email, senha, dados_usuario):
        """Cadastra usuário com autenticação"""
        try:
            # Criar usuário no sistema de auth
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": senha
            })
            
            if auth_response.user:
                # Salvar dados adicionais
                usuario_data = {
                    "id": auth_response.user.id,
                    "username": dados_usuario['username'],
                    "senha_hash": dados_usuario['senha_hash'],
                    "nome": dados_usuario['nome'],
                    "email": email,
                    "tipo": 'cliente'
                }
                
                self.salvar_usuario(usuario_data)
                return True, "Usuário cadastrado com sucesso!"
            
            return False, "Erro ao criar usuário"
        except Exception as e:
            return False, f"Erro: {str(e)}"


    # 👇 ADICIONAR ESTES MÉTODOS NO FINAL DA CLASSE SupabaseManager (dentro da classe)

    def obter_config_cotacoes(self, tipo_config=None, cliente_username=None):
        """Obtém configurações de cotações do Supabase"""
        try:
            query = self.client.table('config_cotacoes').select('*')
            
            # Filtrar por tipo de configuração se especificado
            if tipo_config:
                query = query.eq('tipo_config', tipo_config)
            
            # Filtrar por cliente se especificado
            if cliente_username:
                query = query.eq('cliente_username', cliente_username)
            
            response = query.execute()
            
            print(f"✅ {len(response.data)} configurações de cotações carregadas do Supabase")
            return response.data
            
        except Exception as e:
            print(f"❌ Erro ao obter configurações de cotações: {e}")
            return []

    def salvar_config_cotacoes(self, tipo_config, cliente_username, valor_config, par_moeda=None):
        """Salva uma configuração de cotações no Supabase"""
        try:
            dados = {
                'tipo_config': tipo_config,
                'cliente_username': cliente_username,
                'valor_config': valor_config,
                'data_atualizacao': 'now()'
            }
            
            if par_moeda:
                dados['par_moeda'] = par_moeda
            
            # Verificar se já existe configuração para este tipo e cliente
            existing = self.client.table('config_cotacoes')\
                .select('id')\
                .eq('tipo_config', tipo_config)\
                .eq('cliente_username', cliente_username)\
                .execute()
            
            if existing.data:
                # Atualizar existente
                response = self.client.table('config_cotacoes')\
                    .update(dados)\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
                print(f"✅ Configuração {tipo_config} atualizada para {cliente_username}")
            else:
                # Criar nova
                response = self.client.table('config_cotacoes')\
                    .insert(dados)\
                    .execute()
                print(f"✅ Nova configuração {tipo_config} criada para {cliente_username}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar configuração de cotações: {e}")
            return False

    def obter_spreads_clientes(self):
        """Obtém todos os spreads dos clientes"""
        try:
            spreads_config = self.obter_config_cotacoes(tipo_config='spreads')
            spreads_clientes = {}
            
            for config in spreads_config:
                username = config['cliente_username']
                spreads_clientes[username] = config['valor_config']
            
            print(f"✅ {len(spreads_clientes)} clientes com spreads carregados")
            return spreads_clientes
            
        except Exception as e:
            print(f"❌ Erro ao obter spreads: {e}")
            return {}

    def salvar_spreads_cliente(self, cliente_username, spreads):
        """Salva spreads de um cliente específico"""
        try:
            return self.salvar_config_cotacoes(
                tipo_config='spreads',
                cliente_username=cliente_username,
                valor_config=spreads
            )
        except Exception as e:
            print(f"❌ Erro ao salvar spreads: {e}")
            return False
        
    def obter_permissoes_cambio(self):
        """Obtém todas as permissões de câmbio"""
        try:
            permissoes_config = self.obter_config_cotacoes(tipo_config='permissoes')
            permissoes_cambio = {}
            
            for config in permissoes_config:
                username = config['cliente_username']
                permissoes_cambio[username] = config['valor_config']
            
            print(f"✅ {len(permissoes_cambio)} permissões de câmbio carregadas")
            return permissoes_cambio
            
        except Exception as e:
            print(f"❌ Erro ao obter permissões: {e}")
            return {}

    def salvar_permissao_cambio(self, cliente_username, permitido):
        """Salva permissão de câmbio de um cliente"""
        try:
            return self.salvar_config_cotacoes(
                tipo_config='permissoes',
                cliente_username=cliente_username,
                valor_config=permitido
            )
        except Exception as e:
            print(f"❌ Erro ao salvar permissão: {e}")
            return False

    def obter_limites_operacionais(self):
        """Obtém todos os limites operacionais"""
        try:
            limites_config = self.obter_config_cotacoes(tipo_config='limites')
            limites_operacionais = {}
            
            for config in limites_config:
                username = config['cliente_username']
                limites_operacionais[username] = config['valor_config']
            
            print(f"✅ {len(limites_operacionais)} limites operacionais carregados")
            return limites_operacionais
            
        except Exception as e:
            print(f"❌ Erro ao obter limites: {e}")
            return {}

    def salvar_limite_operacional(self, cliente_username, limite):
        """Salva limite operacional de um cliente"""
        try:
            return self.salvar_config_cotacoes(
                tipo_config='limites',
                cliente_username=cliente_username,
                valor_config=limite
            )
        except Exception as e:
            print(f"❌ Erro ao salvar limite: {e}")
            return False

    def obter_horarios_clientes(self):
        """Obtém todos os horários personalizados dos clientes"""
        try:
            horarios_config = self.obter_config_cotacoes(tipo_config='horarios')
            horarios_clientes = {}
            
            for config in horarios_config:
                username = config['cliente_username']
                horarios_clientes[username] = config['valor_config']
            
            print(f"✅ {len(horarios_clientes)} horários de clientes carregados")
            return horarios_clientes
            
        except Exception as e:
            print(f"❌ Erro ao obter horários: {e}")
            return {}

    def salvar_horario_cliente(self, cliente_username, horario_data):
        """Salva horário personalizado de um cliente - aceita None para remover"""
        try:
            if horario_data is None:
                # Remover horário - deletar registro
                response = self.client.table('config_cotacoes')\
                    .delete()\
                    .eq('tipo_config', 'horarios')\
                    .eq('cliente_username', cliente_username)\
                    .execute()
                print(f"✅ Horário removido do Supabase para {cliente_username}")
                return True
            else:
                # Salvar horário
                return self.salvar_config_cotacoes(
                    tipo_config='horarios',
                    cliente_username=cliente_username,
                    valor_config=horario_data
                )
        except Exception as e:
            print(f"❌ Erro ao salvar horário: {e}")
            return False

    def obter_horario_comercial_padrao(self):
        """Obtém o horário comercial padrão"""
        try:
            horario_config = self.obter_config_cotacoes(tipo_config='horario_padrao')
            
            if horario_config:
                return horario_config[0]['valor_config']
            else:
                print("ℹ️ Nenhum horário padrão encontrado, usando padrão do sistema")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter horário padrão: {e}")
            return None

    def salvar_horario_comercial_padrao(self, horario_data):
        """Salva o horário comercial padrão"""
        try:
            return self.salvar_config_cotacoes(
                tipo_config='horario_padrao',
                cliente_username='sistema',  # Usar 'sistema' para configurações globais
                valor_config=horario_data
            )
        except Exception as e:
            print(f"❌ Erro ao salvar horário padrão: {e}")
            return False



    def criar_contas_supabase(self, username, nome_cliente, moedas):
        """Cria contas para um cliente no Supabase"""
        try:
            import random
            from datetime import datetime
            
            contas_criadas = []
            
            for moeda in moedas:
                # Gerar número de conta único (usar como ID)
                numero_conta = str(random.randint(100000000, 999999999))
                
                conta_data = {
                    'id': numero_conta,  # ✅ COLUNA CORRETA: 'id'
                    'moeda': moeda,      # ✅ COLUNA CORRETA: 'moeda'
                    'saldo': 0.0,        # ✅ COLUNA CORRETA: 'saldo'
                    'cliente_username': username,    # ✅ COLUNA CORRETA
                    'cliente_nome': nome_cliente,    # ✅ COLUNA CORRETA
                    'data_criacao': datetime.now().date().isoformat(),  # ✅ Formato DATE
                    'ativa': True,       # ✅ COLUNA CORRETA: 'ativa'
                    'created_at': datetime.now().isoformat()  # ✅ COLUNA CORRETA
                }
                
                # Inserir conta no Supabase
                response = self.client.table('contas')\
                    .insert(conta_data)\
                    .execute()
                
                if response.data:
                    contas_criadas.append(numero_conta)
                    print(f"✅ Conta {numero_conta} criada no Supabase em {moeda} para {username}")
                else:
                    print(f"❌ Erro ao criar conta {numero_conta} no Supabase")
            
            # 🔥🔥🔥 CORREÇÃO CRÍTICA: ATUALIZAR USUÁRIO COM IDs DAS CONTAS
            if contas_criadas:
                print(f"🔄 Atualizando usuário {username} com IDs das contas: {contas_criadas}")
                
                response_usuario = self.client.table('usuarios')\
                    .update({'contas': contas_criadas})\
                    .eq('username', username)\
                    .execute()
                
                if response_usuario.data:
                    print(f"✅✅✅ USUÁRIO ATUALIZADO: {username} com contas: {contas_criadas}")
                else:
                    print(f"❌❌❌ FALHA CRÍTICA: Não foi possível atualizar usuário no Supabase")
            
            return contas_criadas
            
        except Exception as e:
            print(f"❌ Erro ao criar contas no Supabase: {e}")
            return []
        
    def obter_conta(self, numero_conta):
        """Obtém uma conta pelo número (id)"""
        try:
            response = self.client.table('contas')\
                .select('*')\
                .eq('id', numero_conta)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Erro ao obter conta: {e}")
            return None

    def salvar_transacao_cambio(self, dados_transacao):
        """Salva transação de câmbio no Supabase"""
        try:
            response = self.client.table('transferencias')\
                .insert(dados_transacao)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"❌ Erro ao salvar transação de câmbio: {e}")
            return False

    def salvar_transacao(self, dados_transacao):
        """Salva qualquer tipo de transação no Supabase (transferência, câmbio, etc)"""
        try:
            response = self.client.table('transferencias')\
                .insert(dados_transacao)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"❌ Erro ao salvar transação: {e}")
            return False
        
    def salvar_beneficiario(self, username, dados_beneficiario):
        """Salva beneficiário no Supabase"""
        try:
            from datetime import datetime
            
            dados_supabase = {
                'usuario': username,
                'nome': dados_beneficiario['nome'],
                'endereco': dados_beneficiario['endereco'],
                'cidade': dados_beneficiario['cidade'],
                'pais': dados_beneficiario['pais'],
                'banco': dados_beneficiario['banco'],
                'endereco_banco': dados_beneficiario.get('endereco_banco', ''),
                'swift': dados_beneficiario['swift'],
                'iban': dados_beneficiario['iban'],
                'aba': dados_beneficiario.get('aba', ''),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.client.table('beneficiarios')\
                .insert(dados_supabase)\
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            print(f"❌ Erro ao salvar beneficiário: {e}")
            return False

    def obter_transferencia(self, transferencia_id):
        """Obtém uma transferência específica do Supabase"""
        try:
            response = self.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            # 🔍 DEBUG: VER O QUE ESTÁ VINDO DO SUPABASE
            if response.data:
                print(f"🔍 DEBUG SUPABASE - Transferência {transferencia_id}:")
                print(f"   Data: {response.data[0].get('data')}")
                print(f"   Status: {response.data[0].get('status')}")
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter transferência: {e}")
            return None

    def atualizar_status_transferencia(self, transferencia_id, dados_atualizacao):
        """Atualiza status de uma transferência no Supabase"""
        try:
            response = self.client.table('transferencias')\
                .update(dados_atualizacao)\
                .eq('id', transferencia_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"❌ Erro ao atualizar status da transferência: {e}")
            return False

    def atualizar_saldo_conta_empresa(self, conta_numero, novo_saldo):
        """Atualiza saldo de conta bancária da empresa no Supabase - MESMO PADRÃO"""
        try:
            response = self.client.table('contas_bancarias_empresa')\
                .update({'saldo': novo_saldo})\
                .eq('numero', conta_numero)\
                .execute()
            
            if response.data:
                print(f"✅ Saldo empresa atualizado no Supabase: {conta_numero} = {novo_saldo:.2f}")
                return True
            else:
                print(f"❌ Erro ao atualizar saldo empresa no Supabase: {conta_numero}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar saldo empresa no Supabase: {e}")
            return False

    def atualizar_saldo_conta(self, conta_id, novo_saldo):
        """Atualiza saldo de uma conta no Supabase"""
        try:
            response = self.client.table('contas')\
                .update({'saldo': novo_saldo})\
                .eq('id', conta_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"❌ Erro ao atualizar saldo da conta: {e}")
            return False

    def obter_saldo_conta(self, conta_id):
        """Obtém saldo de uma conta do Supabase"""
        try:
            response = self.client.table('contas')\
                .select('saldo')\
                .eq('id', conta_id)\
                .execute()
            return float(response.data[0]['saldo']) if response.data else 0.0
        except Exception as e:
            print(f"❌ Erro ao obter saldo da conta: {e}")
            return 0.0

    def obter_clientes(self):
        """Obtém todos os clientes do Supabase - MESMO PADRÃO DAS OUTRAS TELAS"""
        try:
            response = self.client.table('usuarios').select('*').eq('tipo', 'cliente').execute()
            
            clientes = []
            for user in response.data:
                cliente = {
                    'username': user['username'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'documento': user.get('documento_hash', ''),
                    'telefone': user.get('telefone', ''),
                    'tipo': user.get('tipo', 'cliente'),
                    'data_cadastro': user.get('data_cadastro', ''),
                    'contas': user.get('contas', [])
                }
                clientes.append(cliente)
            
            print(f"✅ {len(clientes)} clientes carregados do Supabase")
            return clientes
            
        except Exception as e:
            print(f"❌ Erro ao obter clientes do Supabase: {e}")
            return None

    def obter_contas_bancarias_empresa(self):
        """Obtém contas bancárias da empresa do Supabase - MESMO PADRÃO DAS OUTRAS TELAS"""
        try:
            response = self.client.table('contas_bancarias_empresa').select('*').execute()
            
            contas = {}
            for conta in response.data:
                contas[conta['numero']] = {
                    'numero': conta['numero'],
                    'banco': conta['banco'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo']),
                    'tipo': conta.get('tipo', 'empresa'),
                    'agencia': conta.get('agencia', ''),
                    'data_criacao': conta.get('data_criacao', ''),
                    'saldo_inicial': float(conta.get('saldo_inicial', conta['saldo']))
                }
            
            print(f"✅ {len(contas)} contas empresa carregadas do Supabase")
            return contas
            
        except Exception as e:
            print(f"❌ Erro ao obter contas empresa do Supabase: {e}")
            return None

    def obter_transferencias_por_status(self, status):
        """Obtém transferências por status - PADRÃO ESTABELECIDO"""
        try:
            response = self.client.table('transferencias')\
                .select('*')\
                .eq('status', status)\
                .execute()
            
            transferencias = {}
            for transf in response.data:
                transferencias[transf['id']] = transf
            
            print(f"✅ {len(transferencias)} transferências com status '{status}' carregadas do Supabase")
            return transferencias
            
        except Exception as e:
            print(f"❌ Erro ao obter transferências {status}: {e}")
            return {}

    def obter_transferencia(self, transferencia_id):
        """Obtém uma transferência específica - PADRÃO ESTABELECIDO"""
        try:
            response = self.client.table('transferencias')\
                .select('*')\
                .eq('id', transferencia_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter transferência {transferencia_id}: {e}")
            return None

    def atualizar_status_transferencia(self, transferencia_id, update_data):
        """Atualiza status da transferência - PADRÃO ESTABELECIDO"""
        try:
            response = self.client.table('transferencias')\
                .update(update_data)\
                .eq('id', transferencia_id)\
                .execute()
            
            success = bool(response.data)
            if success:
                print(f"✅ Status da transferência {transferencia_id} atualizado no Supabase")
            else:
                print(f"❌ Erro ao atualizar transferência {transferencia_id}")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro ao atualizar transferência {transferencia_id}: {e}")
            return False





# Teste rápido
if __name__ == "__main__":
    sb = SupabaseManager()
    if sb.conectado:
        usuarios = sb.obter_usuarios()
        print(f"📊 {len(usuarios)} usuários no Supabase")