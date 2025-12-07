# teste_supabase.py
import os
from supabase import create_client

# Use as MESMAS credenciais do Render
SUPABASE_URL = "https://rpljjewsxsnbrsagsuoh.supabase.co"
SUPABASE_KEY = "sb_secret_COUaaMh8Bj0PbfxkhlrTMQ_xu1H_d9e"  # sua secret key

try:
    print("Testando conexão com Supabase...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Testa uma query simples
    response = supabase.table('usuarios').select('count', count='exact').execute()
    
    print(f"✅ CONEXÃO BEM-SUCEDIDA!")
    print(f"Contagem de usuários: {response.count}")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()