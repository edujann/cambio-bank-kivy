# supabase_manager.py
import os
import hashlib
import bcrypt
import datetime
from supabase import create_client, Client

def _hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(rounds=12)).decode()
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
        """Salva/atualiza usuário no Supabase - VERSÃO PARA CADASTRO PENDENTE"""
        try:
            from datetime import datetime

            # Dados para cadastro inicial (pendente)
            usuario_data = {
                'username': dados_usuario['username'],
                'senha_hash': _hash_senha(dados_usuario['senha']),
                'nome': dados_usuario['nome'],
                'email': dados_usuario['email'],
                'documento_hash': hashlib.sha256(dados_usuario['documento'].encode()).hexdigest() if dados_usuario['documento'] else '',
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': '',
                'cidade': '',
                'cep': '',
                'estado': '',
                'pais': '',
                'tipo': 'cliente',
                'contas': [],  # 🔥 VAZIO inicialmente - contas serão criadas após verificação
                'data_cadastro': datetime.now().isoformat(),
                'status': 'pendente',  # 🔥 NOVO CAMPO
                'verificado': False,   # 🔥 NOVO CAMPO
                'codigo_verificacao': ''  # Será preenchido separadamente
            }
            
            # Verificar se usuário já existe
            usuario_existente = self.obter_usuario(dados_usuario['username'])
            
            if usuario_existente:
                print(f"⚠️ Usuário {dados_usuario['username']} já existe")
                return False
            
            # Criar novo usuário
            response = self.client.table('usuarios')\
                .insert(usuario_data)\
                .execute()
            
            if response.data:
                print(f"✅ Usuário {dados_usuario['username']} salvo no Supabase (pendente)")
                return True
            else:
                print(f"❌ Falha ao salvar usuário no Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar usuário: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def salvar_usuario_pendente(self, dados_usuario):
        """Salva usuário como pendente (sem criar contas ainda)"""
        try:
            from datetime import datetime

            # Hash do documento
            documento_hash = ''
            if dados_usuario.get('documento'):
                documento_hash = hashlib.sha256(dados_usuario['documento'].encode()).hexdigest()

            # Dados para cadastro inicial (pendente)
            usuario_data = {
                'username': dados_usuario['username'],
                'email': dados_usuario['email'],
                'senha_hash': _hash_senha(dados_usuario['senha']),
                'nome': dados_usuario['nome'],
                'documento_hash': documento_hash,
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': dados_usuario.get('endereco', ''),
                'cidade': dados_usuario.get('cidade', ''),
                'cep': dados_usuario.get('cep', ''),
                'estado': dados_usuario.get('estado', ''),
                'pais': dados_usuario.get('pais', ''),
                'tipo': 'cliente',
                'contas': [],  # VAZIO inicialmente
                'status': 'pendente',
                'verificado': False,
                'data_cadastro': datetime.now().isoformat()
            }
            
            # Verificar se usuário já existe
            existing = self.client.table('usuarios')\
                .select('id')\
                .or_(f'username.eq.{dados_usuario["username"]},email.eq.{dados_usuario["email"]}')\
                .execute()
            
            if existing.data:
                print(f"⚠️ Usuário ou email já existe: {dados_usuario['username']}")
                return False
            
            # Inserir novo usuário
            response = self.client.table('usuarios')\
                .insert(usuario_data)\
                .execute()
            
            if response.data:
                print(f"✅ Usuário {dados_usuario['username']} salvo como pendente no Supabase")
                return True
            else:
                print(f"❌ Falha ao salvar usuário")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar usuário pendente: {e}")
            import traceback
            traceback.print_exc()
            return False

    # No arquivo supabase_manager.py, dentro da classe SupabaseManager:

    def salvar_usuario_com_verificacao(self, dados_usuario):
        """Salva usuário com código de verificação - VERSÃO CORRIGIDA"""
        try:
            print(f"📤 SALVAR_USUARIO_COM_VERIFICACAO: {dados_usuario['username']}")
            
            # Preparar dados para o Supabase - APENAS as colunas que EXISTEM
            dados_supabase = {
                'username': dados_usuario['username'],
                'email': dados_usuario['email'],
                'senha_hash': dados_usuario['senha_hash'],
                'nome': dados_usuario['nome'],
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': dados_usuario.get('endereco', ''),
                'cidade': dados_usuario.get('cidade', ''),
                'cep': dados_usuario.get('cep', ''),
                'estado': dados_usuario.get('estado', ''),
                'pais': dados_usuario.get('pais', ''),
                'tipo': 'cliente',
                'status': dados_usuario.get('status', 'pendente'),
                'verificado': dados_usuario.get('verificado', False),
                'codigo_verificacao': dados_usuario.get('codigo_verificacao', ''),
                'cambio_liberado': dados_usuario.get('cambio_liberado', False),
                'data_cadastro': datetime.datetime.now().isoformat()
            }
            
            # Se tiver documento, criar hash
            if 'documento' in dados_usuario and dados_usuario['documento']:
                import hashlib
                documento_hash = hashlib.sha256(dados_usuario['documento'].encode()).hexdigest()
                dados_supabase['documento_hash'] = documento_hash
            
            # 🔥 REMOVER: Não incluir moedas_selecionadas - elas vão para a tabela contas depois
            # 'moedas_selecionadas': dados_usuario.get('moedas_selecionadas', [])  # ← REMOVER
            
            print(f"📤 Dados para inserir no Supabase:")
            for key, value in dados_supabase.items():
                print(f"   {key}: {value}")
            
            # Verificar se já existe
            response_existe = self.client.table('usuarios')\
                .select('id')\
                .or_(f"username.eq.{dados_usuario['username']},email.eq.{dados_usuario['email']}")\
                .execute()
            
            if response_existe.data:
                print(f"⚠️ Usuário ou email já existe: {dados_usuario['username']}")
                return False
            
            # Inserir usuário
            response = self.client.table('usuarios')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅ Usuário {dados_usuario['username']} salvo com sucesso no Supabase!")
                print(f"   ID: {response.data[0]['id']}")
                print(f"   Email: {response.data[0].get('email')}")
                return True
            else:
                print(f"❌ Erro ao inserir usuário: {response.error if hasattr(response, 'error') else 'Erro desconhecido'}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar usuário com verificação: {e}")
            import traceback
            traceback.print_exc()
            return False

    def salvar_usuario_completo(self, dados_usuario):
        """Salva usuário com todos os dados (endereço completo)"""
        try:
            print(f"📤 Salvando usuário completo: {dados_usuario['username']}")
            
            # Preparar dados para o Supabase
            dados_supabase = {
                'username': dados_usuario['username'],
                'email': dados_usuario['email'],
                'senha_hash': dados_usuario['senha_hash'],
                'nome': dados_usuario['nome'],
                'telefone': dados_usuario.get('telefone', ''),
                'endereco': dados_usuario.get('endereco', ''),           # 🔥
                'cidade': dados_usuario.get('cidade', ''),               # 🔥
                'cep': dados_usuario.get('cep', ''),                     # 🔥
                'estado': dados_usuario.get('estado', ''),               # 🔥
                'pais': dados_usuario.get('pais', ''),                   # 🔥
                'tipo': 'cliente',
                'status': dados_usuario.get('status', 'pendente'),
                'verificado': dados_usuario.get('verificado', False),
                'codigo_verificacao': dados_usuario.get('codigo_verificacao', ''),
                'cambio_liberado': dados_usuario.get('cambio_liberado', False),  # 🔥
                'data_cadastro': datetime.datetime.now().isoformat()
            }
            
            # Se tiver documento, criar hash
            if 'documento' in dados_usuario and dados_usuario['documento']:
                import hashlib
                documento_hash = hashlib.sha256(dados_usuario['documento'].encode()).hexdigest()
                dados_supabase['documento_hash'] = documento_hash
            
            # Se tiver moedas selecionadas, converter para array
            if 'moedas_selecionadas' in dados_usuario and dados_usuario['moedas_selecionadas']:
                dados_supabase['moedas_selecionadas'] = dados_usuario['moedas_selecionadas']
            
            # Verificar se já existe
            response_existe = self.client.table('usuarios')\
                .select('id')\
                .or_(f"username.eq.{dados_usuario['username']},email.eq.{dados_usuario['email']}")\
                .execute()
            
            if response_existe.data:
                print(f"⚠️ Usuário ou email já existe: {dados_usuario['username']}")
                return False
            
            # Inserir usuário
            response = self.client.table('usuarios')\
                .insert(dados_supabase)\
                .execute()
            
            if response.data:
                print(f"✅ Usuário {dados_usuario['username']} salvo com sucesso!")
                print(f"   ID: {response.data[0]['id']}")
                return True
            else:
                print(f"❌ Erro ao inserir usuário: {response.error}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar usuário completo: {e}")
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
        """Cria contas para um cliente no Supabase - VERSÃO MELHORADA"""
        try:
            import random
            from datetime import datetime
            
            contas_criadas = []
            
            for moeda in moedas:
                # Gerar número de conta único (usar como ID)
                numero_conta = str(random.randint(100000000, 999999999))
                
                conta_data = {
                    'id': numero_conta,
                    'moeda': moeda,
                    'saldo': 0.0,
                    'cliente_username': username,
                    'cliente_nome': nome_cliente,
                    'data_criacao': datetime.now().date().isoformat(),
                    'ativa': True,
                    'created_at': datetime.now().isoformat()
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
            
            # 🔥 AGORA: Atualizar usuário com IDs das contas
            if contas_criadas:
                self.atualizar_contas_usuario_supabase(username)
            
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
                'cidade_banco': dados_beneficiario.get('cidade_banco', ''),  # 🔥 NOVO
                'pais_banco': dados_beneficiario.get('pais_banco', ''),      # 🔥 NOVO
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

    def obter_contas_cliente(self, username_cliente):
        """Obtém contas de um cliente específico - PADRÃO ESTABELECIDO"""
        try:
            response = self.client.table('contas')\
                .select('*')\
                .eq('cliente_username', username_cliente)\
                .execute()
            
            contas = {}
            for conta in response.data:
                contas[conta['id']] = conta
            
            print(f"✅ {len(contas)} contas do cliente {username_cliente} carregadas do Supabase")
            return contas
            
        except Exception as e:
            print(f"❌ Erro ao obter contas do cliente {username_cliente}: {e}")
            return {}

    def obter_beneficiarios_cliente(self, username_cliente):
        """Obtém beneficiários de um cliente específico - PADRÃO ESTABELECIDO"""
        try:
            response = self.client.table('beneficiarios')\
                .select('*')\
                .eq('cliente_username', username_cliente)\
                .execute()
            
            beneficiarios = []
            for benef in response.data:
                beneficiarios.append(benef)
            
            print(f"✅ {len(beneficiarios)} beneficiários do cliente {username_cliente} carregados do Supabase")
            return beneficiarios
            
        except Exception as e:
            print(f"❌ Erro ao obter beneficiários do cliente {username_cliente}: {e}")
            return []

    # No arquivo supabase_manager.py, adicione estes métodos NO FINAL DA CLASSE SupabaseManager:

    def atualizar_contas_usuario_supabase(self, username, conta_id_remover=None):
        """Atualiza a lista de contas do usuário no Supabase (remove uma conta se especificada)"""
        try:
            # Buscar todas as contas atuais do usuário
            response = self.client.table('contas')\
                .select('id')\
                .eq('cliente_username', username)\
                .eq('ativa', True)\
                .execute()
            
            if response.data:
                # Filtrar contas ativas (exceto a que está sendo removida)
                contas_ativas = [conta['id'] for conta in response.data 
                            if conta['id'] != conta_id_remover]
                
                # Atualizar campo 'contas' do usuário
                response_update = self.client.table('usuarios')\
                    .update({'contas': contas_ativas})\
                    .eq('username', username)\
                    .execute()
                
                if response_update.data:
                    print(f"✅ Lista de contas atualizada para {username}: {len(contas_ativas)} contas")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro ao atualizar contas do usuário no Supabase: {e}")
            return False

    def excluir_usuario_completo_supabase(self, username):
        """Exclui usuário e dados relacionados MAS PRESERVA TRANSFERÊNCIAS"""
        try:
            print(f"\n{'='*60}")
            print(f"🗑️  INICIANDO EXCLUSÃO SEGURA DE: {username}")
            print(f"{'='*60}")
            print(f"⚠️  ATENÇÃO: Transferências NÃO serão excluídas para preservar histórico!")
            
            # 1. Verificar se usuário existe
            response_usuario = self.client.table('usuarios')\
                .select('id, email, nome, status')\
                .eq('username', username)\
                .execute()
            
            if not response_usuario.data:
                print(f"❌ Usuário '{username}' não encontrado no Supabase")
                return False
            
            usuario_data = response_usuario.data[0]
            usuario_id = usuario_data['id']
            usuario_email = usuario_data.get('email', '')
            usuario_nome = usuario_data.get('nome', username)
            usuario_status = usuario_data.get('status', 'ativo')
            
            print(f"   Dados do usuário encontrados:")
            print(f"   ID: {usuario_id}")
            print(f"   Nome: {usuario_nome}")
            print(f"   Email: {usuario_email}")
            print(f"   Status atual: {usuario_status}")
            
            # 2. Desativar contas do usuário (soft delete)
            sucesso_contas = self.desativar_contas_usuario_supabase(username)
            
            # 3. Excluir beneficiários
            print(f"\n Excluindo beneficiários...")
            try:
                response_benef = self.client.table('beneficiarios')\
                    .delete()\
                    .eq('cliente_username', username)\
                    .execute()
                
                count_benef = len(response_benef.data) if response_benef.data else 0
                print(f" {count_benef} beneficiários excluídos")
            except Exception as e:
                print(f" Erro ao excluir beneficiários: {e}")
            
            # 4. Excluir configurações de cotações
            print(f"\n Excluindo configurações de cotações...")
            try:
                response_config = self.client.table('config_cotacoes')\
                    .delete()\
                    .eq('cliente_username', username)\
                    .execute()
                
                count_config = len(response_config.data) if response_config.data else 0
                print(f" {count_config} configurações excluídas")
            except Exception as e:
                print(f" Erro ao excluir configurações: {e}")
            
            # 5. Marcar usuário como excluído (soft delete)
            print(f"\n Marcando usuário como excluído (soft delete)...")
            
            # Criar novo username/email para evitar conflitos
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            novo_username = f"excluido_{timestamp}_{username[:10]}"
            
            # Tratamento especial para email
            if usuario_email and '@' in usuario_email:
                # Preservar domínio original
                dominio = usuario_email.split('@')[1]
                novo_email = f"excluido_{timestamp}@{dominio}"
            elif usuario_email:
                novo_email = f"excluido_{timestamp}_{usuario_email}"
            else:
                novo_email = f"excluido_{timestamp}@excluido.com"
            
            # 🔥 USANDO APENAS COLUNAS QUE EXISTEM NA TABELA 'usuarios':
            update_data = {
                'username': novo_username,          # ✅ EXISTE
                'email': novo_email,                # ✅ EXISTE
                'status': 'excluido',               # ✅ EXISTE
                'nome': f"[EXCLUÍDO] {usuario_nome}",  # ✅ EXISTE
                'documento_hash': '',               # ✅ EXISTE
                'telefone': '',                     # ✅ EXISTE
                'endereco': '',                     # ✅ EXISTE
                'cidade': '',                       # ✅ EXISTE
                'cep': '',                          # ✅ EXISTE
                'estado': '',                       # ✅ EXISTE
                'pais': '',                         # ✅ EXISTE
                'tipo': 'excluido',                 # ✅ EXISTE
                'contas': [],                       # ✅ EXISTE
                'verificado': False,                # ✅ EXISTE
                'codigo_verificacao': '',           # ✅ EXISTE
                'cambio_liberado': False            # ✅ EXISTE
                # 🔥 NÃO INCLUIR: 'ativo' - não existe
                # 🔥 NÃO INCLUIR: 'updated_at' - pode ser automático
                # 🔥 'data_cadastro' e 'created_at' mantemos como estão
            }
            
            response_update = self.client.table('usuarios')\
                .update(update_data)\
                .eq('id', usuario_id)\
                .execute()
            
            if response_update.data:
                print(f"\n{''*20}")
                print(f" EXCLUSÃO SEGURA CONCLUÍDA!")
                print(f"{''*20}")
                print(f"\n RESUMO DA EXCLUSÃO:")
                print(f"    Cliente: {username}")
                print(f"    Nome original: {usuario_nome}")
                print(f"    Novo username: {novo_username}")
                print(f"    Novo email: {novo_email}")
                print(f"    Contas desativadas: {'Sim' if sucesso_contas else 'Não'}")
                print(f"    Transferências: PRESERVADAS")
                print(f"    Histórico contábil: INTACTO")
                print(f"\n  IMPORTANTE:")
                print(f"   • O usuário não pode mais fazer login")
                print(f"   • Contas estão desativadas")
                print(f"   • Transferências permanecem para auditoria")
                print(f"   • Dados sensíveis foram removidos")
                
                return True
            else:
                print(f" Erro ao marcar usuário como excluído")
                return False
                
        except Exception as e:
            print(f"\n{''*20}")
            print(f" ERRO NA EXCLUSÃO!")
            print(f"{''*20}")
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            return False

    def desativar_contas_usuario_supabase(self, username):
        """Desativa contas de um usuário (soft delete)"""
        try:
            response = self.client.table('contas')\
                .update({
                    'ativa': False,
                    'cliente_nome': f"[EXCLUÍDO] {self.obter_nome_cliente(username)}"
                })\
                .eq('cliente_username', username)\
                .execute()
            
            if response.data:
                print(f"✅ Contas de {username} desativadas no Supabase")
                return True
            else:
                print(f"⚠️ Nenhuma conta encontrada para {username}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao desativar contas: {e}")
            return False

    def obter_nome_cliente(self, username):
        """Obtém nome do cliente para usar no soft delete"""
        try:
            response = self.client.table('usuarios')\
                .select('nome')\
                .eq('username', username)\
                .execute()
            
            if response.data:
                return response.data[0].get('nome', username)
            return username
        except:
            return username

    def obter_contas_cliente_supabase(self, username):
        """Obtém contas de um cliente específico do Supabase"""
        try:
            response = self.client.table('contas')\
                .select('*')\
                .eq('cliente_username', username)\
                .execute()
            
            contas = []
            for conta in response.data:
                contas.append({
                    'id': conta['id'],
                    'numero': conta['id'],
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo']),
                    'cliente_username': conta['cliente_username'],
                    'cliente_nome': conta.get('cliente_nome', ''),
                    'data_criacao': conta.get('data_criacao', ''),
                    'ativa': conta.get('ativa', True)
                })
            
            print(f"✅ {len(contas)} contas obtidas do Supabase para {username}")
            return contas
            
        except Exception as e:
            print(f"❌ Erro ao obter contas do cliente do Supabase: {e}")
            return []

    def atualizar_dados_cliente_supabase(self, username, dados_atualizados):
        """Atualiza dados do cliente no Supabase"""
        try:
            # Preparar dados para atualização
            dados_supabase = {}
            
            # Mapear campos que podem ser atualizados
            campos_permitidos = [
                'nome', 'email', 'telefone', 'endereco', 'cidade', 
                'cep', 'estado', 'pais', 'status', 'cambio_liberado'
            ]
            
            for campo in campos_permitidos:
                if campo in dados_atualizados:
                    dados_supabase[campo] = dados_atualizados[campo]
            
            # Atualizar no Supabase
            response = self.client.table('usuarios')\
                .update(dados_supabase)\
                .eq('username', username)\
                .execute()
            
            if response.data:
                print(f"✅ Dados do cliente {username} atualizados no Supabase")
                return True
            else:
                print(f"❌ Erro ao atualizar dados do cliente no Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar dados do cliente no Supabase: {e}")
            return False
        
    def obter_transferencias_cliente(self, username):
        """Obtém transferências relacionadas a um cliente (para auditoria)"""
        try:
            # Primeiro, buscar contas do cliente
            contas_response = self.client.table('contas')\
                .select('id')\
                .eq('cliente_username', username)\
                .execute()
            
            if not contas_response.data:
                return []
            
            contas_ids = [conta['id'] for conta in contas_response.data]
            
            # Buscar transferências onde o cliente está envolvido
            transferencias = []
            
            # Buscar como remetente
            for conta_id in contas_ids:
                response = self.client.table('transferencias')\
                    .select('*')\
                    .eq('conta_remetente', conta_id)\
                    .execute()
                
                transferencias.extend(response.data)
            
            # Buscar como destinatário
            for conta_id in contas_ids:
                response = self.client.table('transferencias')\
                    .select('*')\
                    .eq('conta_destinatario', conta_id)\
                    .execute()
                
                transferencias.extend(response.data)
            
            # Buscar por nome do cliente em outros campos
            response_cliente = self.client.table('transferencias')\
                .select('*')\
                .or_(f"cliente.eq.{username},solicitado_por.eq.{username},executado_por.eq.{username}")\
                .execute()
            
            transferencias.extend(response_cliente.data)
            
            # Remover duplicatas
            ids_vistos = set()
            transferencias_unicas = []
            
            for transf in transferencias:
                if transf['id'] not in ids_vistos:
                    ids_vistos.add(transf['id'])
                    transferencias_unicas.append(transf)
            
            print(f"✅ {len(transferencias_unicas)} transferências encontradas para {username}")
            return transferencias_unicas
            
        except Exception as e:
            print(f"❌ Erro ao buscar transferências do cliente: {e}")
            return []

    # Adicione estes métodos na classe SupabaseManager:

    def verificar_invoice_transferencia(self, transferencia_id):
        """Verifica se existe invoice para uma transferência - VERSÃO ADAPTADA À ESTRUTURA REAL"""
        try:
            if not self.client:
                print(f"❌ Cliente Supabase não conectado")
                return False
            
            # 🔍 PRIMEIRO: Verificar se existe a pasta da transferência
            prefix = f"transferencias/{transferencia_id}/"
            
            try:
                # Listar arquivos na pasta da transferência
                files = self.client.storage.from_("invoices").list(prefix)
                
                if files:
                    print(f"✅ Pasta encontrada para {transferencia_id}: {len(files)} arquivo(s)")
                    for file in files:
                        print(f"   - {file['name']}")
                    return True
                else:
                    print(f"❌ Nenhum arquivo na pasta {transferencia_id}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao listar arquivos: {e}")
            
            # 🔍 SEGUNDO: Tentar encontrar arquivos com ID no nome (caso a pasta não exista)
            print(f"🔍 Buscando arquivos que contenham ID {transferencia_id}...")
            all_files = self.client.storage.from_("invoices").list("transferencias/")
            
            for file in all_files:
                if transferencia_id in file['name']:
                    print(f"✅ Arquivo encontrado: {file['name']}")
                    return True
            
            # 🔍 TERCEIRO: Verificar IDs com problemas de nomenclatura
            # Alguns IDs estão incorretos: "108684_INVOICE - GAYUR INTERNATIONAL.pdf"
            # Extrair o ID real (antes do primeiro underscore)
            if '_' in transferencia_id:
                id_base = transferencia_id.split('_')[0]
                if id_base.isdigit():
                    print(f"🔍 Tentando ID base: {id_base}")
                    return self.verificar_invoice_transferencia(id_base)
            
            print(f"❌ Nenhum arquivo encontrado para transferência {transferencia_id}")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar invoice: {e}")
            return False

    def baixar_invoice_transferencia(self, transferencia_id, local_dir="data/invoices"):
        """Baixa invoice de uma transferência - VERSÃO ADAPTADA"""
        try:
            import os
            
            if not self.client:
                return None
            
            # 🔍 1. Tentar listar arquivos na pasta da transferência
            prefix = f"transferencias/{transferencia_id}/"
            
            try:
                files = self.client.storage.from_("invoices").list(prefix)
                
                if files:
                    # Baixar o primeiro arquivo (ou poderia mostrar opção)
                    first_file = files[0]['name']
                    print(f"📥 Baixando: {first_file}")
                    
                    response = self.client.storage.from_("invoices").download(first_file)
                    
                    if response:
                        # Criar diretório local
                        os.makedirs(local_dir, exist_ok=True)
                        
                        # Salvar arquivo
                        nome_arquivo = os.path.basename(first_file)
                        local_path = os.path.join(local_dir, nome_arquivo)
                        
                        with open(local_path, 'wb') as f:
                            f.write(response)
                        
                        print(f"✅ Invoice baixada: {local_path}")
                        return local_path
            
            except Exception as e:
                print(f"⚠️ Erro ao listar pasta: {e}")
            
            # 🔍 2. Buscar arquivos que contenham o ID no nome
            print(f"🔍 Buscando arquivos com ID {transferencia_id} no nome...")
            all_files = self.client.storage.from_("invoices").list("transferencias/")
            
            arquivos_encontrados = []
            for file in all_files:
                if transferencia_id in file['name']:
                    arquivos_encontrados.append(file['name'])
            
            if arquivos_encontrados:
                print(f"✅ {len(arquivos_encontrados)} arquivo(s) encontrado(s):")
                for arquivo in arquivos_encontrados:
                    print(f"   - {arquivo}")
                
                # Baixar o primeiro arquivo encontrado
                first_file = arquivos_encontrados[0]
                response = self.client.storage.from_("invoices").download(first_file)
                
                if response:
                    os.makedirs(local_dir, exist_ok=True)
                    nome_arquivo = os.path.basename(first_file)
                    local_path = os.path.join(local_dir, nome_arquivo)
                    
                    with open(local_path, 'wb') as f:
                        f.write(response)
                    
                    print(f"✅ Invoice baixada: {local_path}")
                    return local_path
            
            # 🔍 3. Tentar IDs com problemas de nomenclatura
            if '_' in transferencia_id:
                id_base = transferencia_id.split('_')[0]
                if id_base.isdigit():
                    print(f"🔍 Tentando ID base: {id_base}")
                    return self.baixar_invoice_transferencia(id_base, local_dir)
            
            print(f"❌ Nenhum arquivo encontrado para baixar")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao baixar invoice: {e}")
            return None

    def listar_invoices_transferencia(self, transferencia_id):
        """Lista todas as invoices disponíveis para uma transferência"""
        try:
            if not self.client:
                return []
            
            invoices = []
            
            # 🔍 Buscar na pasta da transferência
            prefix = f"transferencias/{transferencia_id}/"
            
            try:
                files = self.client.storage.from_("invoices").list(prefix)
                for file in files:
                    invoices.append({
                        'caminho': file['name'],
                        'nome': os.path.basename(file['name']),
                        'tamanho': file.get('metadata', {}).get('size', 0)
                    })
            except:
                pass
            
            # 🔍 Buscar arquivos com ID no nome
            all_files = self.client.storage.from_("invoices").list("transferencias/")
            
            for file in all_files:
                if transferencia_id in file['name'] and file['name'] not in [i['caminho'] for i in invoices]:
                    invoices.append({
                        'caminho': file['name'],
                        'nome': os.path.basename(file['name']),
                        'tamanho': file.get('metadata', {}).get('size', 0)
                    })
            
            print(f"📄 {len(invoices)} invoice(s) encontrada(s) para {transferencia_id}")
            return invoices
            
        except Exception as e:
            print(f"❌ Erro ao listar invoices: {e}")
            return []

# Teste rápido
if __name__ == "__main__":
    sb = SupabaseManager()
    if sb.conectado:
        usuarios = sb.obter_usuarios()
        print(f"📊 {len(usuarios)} usuários no Supabase")