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
    
    def salvar_usuario(self, usuario_data):
        """Salva usuário no Supabase - VERSÃO CORRIGIDA"""
        try:
            # 🔥 MAPEAMENTO CORRETO DOS CAMPOS
            dados_supabase = {
                'username': usuario_data['username'],
                'senha_hash': usuario_data.get('senha', usuario_data.get('senha_hash', '')),
                'nome': usuario_data.get('nome', ''),
                'email': usuario_data.get('email', ''),
                'documento_hash': usuario_data.get('documento_hash', ''),
                'telefone': usuario_data.get('telefone', ''),
                'tipo': usuario_data.get('tipo', 'cliente'),
                'data_cadastro': usuario_data.get('data_cadastro', '2024-01-01')
            }
            
            # 🔥 REMOVER CAMPOS QUE NÃO EXISTEM NA TABELA
            campos_nao_existem = ['contas', 'documento', 'endereco', 'cidade', 'cep', 'estado', 'pais']
            for campo in campos_nao_existem:
                if campo in dados_supabase:
                    del dados_supabase[campo]
            
            response = self.client.table('usuarios').insert(dados_supabase).execute()
            print(f"✅ Usuário {usuario_data['username']} salvo no Supabase")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar usuário {usuario_data.get('username', '')}: {e}")
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



# Teste rápido
if __name__ == "__main__":
    sb = SupabaseManager()
    if sb.conectado:
        usuarios = sb.obter_usuarios()
        print(f"📊 {len(usuarios)} usuários no Supabase")