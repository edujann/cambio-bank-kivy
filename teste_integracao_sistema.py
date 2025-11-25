#!/usr/bin/env python3
"""
Teste de integração do Sistema com Supabase para cotações
"""
#!/usr/bin/env python3
"""
Teste de integração do Sistema com Supabase para cotações
"""

import os
import sys

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🔥 CORREÇÃO: Importar do arquivo sistema.py
from sistema import SistemaCambioPremium

def testar_integracao_sistema():
    """Testa se o sistema carrega cotações do Supabase corretamente"""
    
    print("🧪 INICIANDO TESTE DE INTEGRAÇÃO SISTEMA")
    print("=" * 50)
    
    # Inicializar sistema (isso já deve carregar do Supabase)
    sistema = SistemaCambioPremium()
    
    print("✅ Sistema inicializado")
    
    # Verificar se os dados foram carregados do Supabase
    print("\n📊 VERIFICANDO DADOS CARREGADOS:")
    
    # 1. Verificar spreads
    print(f"1. 📈 Spreads carregados: {len(sistema.spreads_clientes)} clientes")
    for cliente, spreads in list(sistema.spreads_clientes.items())[:3]:  # Mostrar apenas 3
        print(f"   👤 {cliente}: {len(spreads)} pares de moeda")
    
    # 2. Verificar permissões
    print(f"2. 🔐 Permissões carregadas: {len(sistema.permissoes_cambio)} clientes")
    if sistema.permissoes_cambio:
        for cliente, permissao in list(sistema.permissoes_cambio.items())[:3]:
            print(f"   👤 {cliente}: {permissao}")
    else:
        print("   ℹ️ Nenhuma permissão carregada (pode estar vazio no Supabase)")
    
    # 3. Verificar limites
    print(f"3. 💰 Limites carregados: {len(sistema.limites_operacionais)} clientes")
    if sistema.limites_operacionais:
        for cliente, limite in list(sistema.limites_operacionais.items())[:3]:
            print(f"   👤 {cliente}: {limite}")
    else:
        print("   ℹ️ Nenhum limite carregado (pode estar vazio no Supabase)")
    
    # 4. Verificar horários
    print(f"4. ⏰ Horários carregados: {len(sistema.horarios_clientes)} clientes")
    if sistema.horarios_clientes:
        for cliente, horario in list(sistema.horarios_clientes.items())[:3]:
            print(f"   👤 {cliente}: {horario.get('inicio', 'N/A')} - {horario.get('fim', 'N/A')}")
    else:
        print("   ℹ️ Nenhum horário carregado (pode estar vazio no Supabase)")
    
    # 5. Testar salvamento
    print("\n5. 💾 TESTANDO SALVAMENTO NO SUPABASE...")
    try:
        sucesso = sistema.salvar_cotacoes_supabase()
        print(f"   ✅ Salvamento: {'SUCESSO' if sucesso else 'FALHA'}")
    except Exception as e:
        print(f"   ❌ Erro no salvamento: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE DE INTEGRAÇÃO CONCLUÍDO!")
    
    # Resumo final
    print("\n📋 RESUMO FINAL:")
    print(f"   📈 Spreads: {len(sistema.spreads_clientes)} clientes")
    print(f"   🔐 Permissões: {len(sistema.permissoes_cambio)} clientes") 
    print(f"   💰 Limites: {len(sistema.limites_operacionais)} clientes")
    print(f"   ⏰ Horários: {len(sistema.horarios_clientes)} clientes")
    
    return True

if __name__ == "__main__":
    testar_integracao_sistema()