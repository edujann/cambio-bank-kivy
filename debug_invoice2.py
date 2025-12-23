import os
import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

print("🔍 PROCURANDO ARQUIVOS DA TRANSFERÊNCIA 943510...")
print("=" * 50)

try:
    # Conectar ao Supabase
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    
    # Listar todos os arquivos
    arquivos = supabase.storage.from_('invoices').list('transferencias')
    
    encontrados = []
    print("📁 ARQUIVOS ENCONTRADOS:")
    for arquivo in arquivos:
        nome = arquivo['name']
        print(f"   📄 {nome}")
        if '943510' in nome:
            encontrados.append(nome)
    
    print("\n" + "=" * 50)
    
    if encontrados:
        print(f"✅ ARQUIVOS COM '943510' ENCONTRADOS: {len(encontrados)}")
        for arq in encontrados:
            print(f"   🎯 {arq}")
        
        # Mostrar o mais recente (com data de hoje)
        hoje = datetime.datetime.now().strftime("%Y%m%d")
        
        for arq in encontrados:
            if hoje in arq:
                print(f"\n🔥 ARQUIVO DE HOJE ENCONTRADO: {arq}")
                caminho_correto = f"transferencias/{arq}"
                print(f"   Caminho correto: {caminho_correto}")
                break
            else:
                print(f"\n⚠️  Nenhum arquivo de hoje encontrado")
                print(f"   Último arquivo: {encontrados[-1]}")
    else:
        print("❌ Nenhum arquivo com '943510' encontrado!")
        
except Exception as e:
    print(f"❌ ERRO: {e}")

input("\nPressione Enter para sair...")