import bcrypt
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# NOVA SENHA - MUDE AQUI!
nova_senha = "Admin@2026!"

# Gerar hash bcrypt
nova_senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt(rounds=12)).decode()

# Atualizar no Supabase
response = supabase.table('usuarios')\
    .update({'senha_hash': nova_senha_hash})\
    .eq('username', 'admin')\
    .execute()

if response.data:
    print("✅ Senha do admin alterada com sucesso!")
else:
    print("❌ Erro ao alterar senha")