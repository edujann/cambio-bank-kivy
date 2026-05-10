import bcrypt
import os
import sys
import getpass
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# Aceita a senha via argumento CLI, variável de ambiente, ou prompt seguro
if len(sys.argv) > 1:
    nova_senha = sys.argv[1]
elif os.getenv('ADMIN_PASSWORD'):
    nova_senha = os.getenv('ADMIN_PASSWORD')
else:
    nova_senha = getpass.getpass("Nova senha do admin: ")

if not nova_senha:
    print("❌ Senha não pode ser vazia.")
    sys.exit(1)

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