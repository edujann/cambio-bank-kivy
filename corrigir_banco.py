import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print('🔍 VERIFICANDO CONTEÚDO DA PASTA 846749...')

try:
    arquivos = supabase.storage.from_('invoices').list('transferencias/846749')
    
    if arquivos:
        print(f'📁 Conteúdo da pasta 846749:')
        for i, arquivo in enumerate(arquivos):
            print(f'   {i+1}. {arquivo[\"name\"]}')
    else:
        print('❌ Pasta vazia!')
        
except Exception as e:
    print(f'❌ Erro: {e}')
"