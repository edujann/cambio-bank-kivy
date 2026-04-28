"""
Configuração do pytest - adiciona o caminho do projeto
"""
import sys
import os

# Adiciona a pasta 'web' (onde está o web_api.py)
pasta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pasta_web = os.path.join(pasta_raiz, 'web')

sys.path.insert(0, pasta_web)
sys.path.insert(0, pasta_raiz)

print(f"📂 Path adicionado: {pasta_web}")

# Verifica se encontrou
try:
    import web_api
    print("✅ web_api.py encontrado com sucesso!")
except ImportError as e:
    print(f"❌ web_api.py NÃO encontrado: {e}")