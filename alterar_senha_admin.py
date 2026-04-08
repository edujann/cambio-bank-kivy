import hashlib
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# NOVA SENHA - MUDE AQUI!
nova_senha = "Admin@2026!"

# Gerar hash
nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

print(f"Nova senha: {nova_senha}")
print(f"Hash: {nova_senha_hash}")

# Atualizar no Supabase
response = supabase.table('usuarios')\
    .update({'senha_hash': nova_senha_hash})\
    .eq('username', 'admin')\
    .execute()

if response.data:
    print(f"✅ Senha do admin alterada com sucesso!")
    print(f"⚠️ Guarde bem a nova senha: {nova_senha}")
else:
    print(f"❌ Erro ao alterar senha")