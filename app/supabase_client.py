# app/supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"🔧 Inicializando Supabase Client...")
print(f"   URL: {SUPABASE_URL}")
print(f"   KEY: {'✅ Configurada' if SUPABASE_KEY else '❌ Não configurada'}")

# Inicializar cliente Supabase
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase Client criado com sucesso!")
        
        # Testar conexão
        try:
            response = supabase.table('usuarios').select('count', count='exact').execute()
            print(f"✅ Conexão testada: {response.count} usuários na tabela")
        except Exception as e:
            print(f"⚠️ Erro ao testar conexão: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao criar cliente Supabase: {e}")
        import traceback
        traceback.print_exc()
        supabase = None
else:
    print("⚠️ Variáveis de ambiente do Supabase não configuradas corretamente")
    print("   Certifique-se que .env tem SUPABASE_URL e SUPABASE_KEY")
    supabase = None

# Exportar
__all__ = ['supabase']