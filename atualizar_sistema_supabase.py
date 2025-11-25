import re

def atualizar_sistema_py():
    """Atualiza o arquivo sistema.py para usar Supabase em vez de JSON"""
    
    with open('app/sistema.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Adicionar import do Supabase no topo (se não existir)
    if 'from supabase import create_client' not in content:
        imports_supabase = '''
import os
from dotenv import load_dotenv
from supabase import create_client

# Configurar Supabase
load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)
'''
        # Inserir após os outros imports
        content = content.replace(
            'import json', 
            'import json\n' + imports_supabase
        )
    
    # 2. Substituir carregamento de contas
    old_contas_code = '''contas_path = 'data/contas.json'
        with open(contas_path, 'r', encoding='utf-8') as f:
            self.contas = json.load(f)'''
    
    new_contas_code = '''# Carregar contas do Supabase
        try:
            response = supabase.table('contas').select('*').execute()
            self.contas = {}
            for conta in response.data:
                self.contas[conta['id']] = {
                    'moeda': conta['moeda'],
                    'saldo': float(conta['saldo']),
                    'cliente': conta['cliente_username'],
                    'cliente_nome': conta['cliente_nome'],
                    'data_criacao': conta['data_criacao']
                }
            print(f"✅ {len(self.contas)} contas carregadas do Supabase")
        except Exception as e:
            print(f"❌ Erro ao carregar contas do Supabase: {e}")
            self.contas = {}'''
    
    content = content.replace(old_contas_code, new_contas_code)
    
    # 3. Salvar arquivo atualizado
    with open('app/sistema.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ sistema.py atualizado para usar Supabase!")

if __name__ == "__main__":
    print("🔄 Atualizando sistema.py para usar Supabase...")
    atualizar_sistema_py()