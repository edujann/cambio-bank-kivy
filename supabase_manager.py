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

# Teste rápido
if __name__ == "__main__":
    sb = SupabaseManager()
    if sb.conectado:
        usuarios = sb.obter_usuarios()
        print(f"📊 {len(usuarios)} usuários no Supabase")