"""
Executador de testes simples - não requer pytest
"""
import sys
import traceback

def run_tests():
    """Executa todos os testes manualmente"""
    
    # Importa os testes
    sys.path.insert(0, '.')
    
    # Lista de testes a executar
    testes = []
    
    # Coleta todas as funções que começam com 'test_'
    try:
        # Tenta importar o arquivo de testes
        import test_regras_negocio
        
        for nome in dir(test_regras_negocio):
            if nome.startswith('test_'):
                testes.append(nome)
            
            # Também pega métodos das classes
            for cls_name in dir(test_regras_negocio):
                cls = getattr(test_regras_negocio, cls_name)
                if isinstance(cls, type) and cls.__name__.startswith('Test'):
                    for method_name in dir(cls):
                        if method_name.startswith('test_'):
                            testes.append(f"{cls_name}.{method_name}")
    except ImportError as e:
        print(f"❌ Erro ao importar test_regras_negocio: {e}")
        return
    
    if not testes:
        print("❌ Nenhum teste encontrado")
        return
    
    print("=" * 60)
    print("🧪 EXECUTANDO TESTES")
    print("=" * 60)
    
    passou = 0
    falhou = 0
    
    for teste in testes:
        try:
            # Executa o teste
            if '.' in teste:
                classe, metodo = teste.split('.')
                cls = getattr(test_regras_negocio, classe)
                obj = cls()
                getattr(obj, metodo)()
            else:
                func = getattr(test_regras_negocio, teste)
                func()
            
            print(f"✅ {teste} - PASSED")
            passou += 1
        except AssertionError as e:
            print(f"❌ {teste} - FAILED: {e}")
            falhou += 1
        except Exception as e:
            print(f"❌ {teste} - ERROR: {e}")
            traceback.print_exc()
            falhou += 1
    
    print("=" * 60)
    print(f"📊 RESULTADO: {passou} aprovados, {falhou} falhados")
    print("=" * 60)
    
    return falhou == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)