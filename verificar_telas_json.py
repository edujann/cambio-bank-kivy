import os
import re

def encontrar_telas_json():
    """Encontra todas as telas que ainda usam arquivos JSON"""
    
    print("🔍 PROCURANDO TELAS QUE USAM JSON...")
    
    problemas = []
    
    # Procurar em todos os arquivos .py
    for root, dirs, files in os.walk('app/screens'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Padrões que indicam uso de JSON
                    padroes_json = [
                        'with open.*\.json',
                        'json\.load',
                        'json\.dump',
                        'data/.*\.json',
                        'transferencias\.json',
                        'contas\.json',
                        'beneficiarios\.json'
                    ]
                    
                    for padrao in padroes_json:
                        if re.search(padrao, content):
                            problemas.append({
                                'arquivo': filepath,
                                'padrao': padrao,
                                'linhas': []
                            })
                            print(f"❌ {filepath} - usa {padrao}")
                            
                except Exception as e:
                    print(f"⚠️ Erro ao ler {filepath}: {e}")
    
    return problemas

def verificar_extrato():
    """Verifica especificamente a tela de extrato"""
    print("\n🔍 VERIFICANDO TELA EXTRATO...")
    
    extrato_path = 'app/screens/extrato.py'
    if os.path.exists(extrato_path):
        with open(extrato_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'transferencias.json' in content:
            print("❌ Tela extrato ainda lê transferencias.json")
            # Mostrar as linhas problemáticas
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'transferencias.json' in line:
                    print(f"   Linha {i}: {line.strip()}")
        else:
            print("✅ Tela extrato parece OK")
    else:
        print("❌ Arquivo extrato.py não encontrado")

if __name__ == "__main__":
    problemas = encontrar_telas_json()
    verificar_extrato()
    
    print(f"\n📊 RESUMO: {len(problemas)} telas precisam de correção")