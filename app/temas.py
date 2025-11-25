# app/temas.py
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

class GerenciadorTemas:
    def __init__(self):
        self.temas = {
            'escuro': {
                'primaria': get_color_from_hex('#1a237e'),
                'secundaria': get_color_from_hex('#283593'),
                'fundo': get_color_from_hex('#0d1117'),
                'card': get_color_from_hex('#161b22'),
                'texto_primario': (1, 1, 1, 1),
                'texto_secundario': (0.8, 0.84, 0.88, 1),
                'destaque': get_color_from_hex('#3f51b5'),
                'sucesso': get_color_from_hex('#4caf50'),
                'erro': get_color_from_hex('#f44336'),
                'aviso': get_color_from_hex('#ff9800')
            },
            'claro': {
                'primaria': get_color_from_hex('#1976d2'),
                'secundaria': get_color_from_hex('#2196f3'),
                'fundo': get_color_from_hex('#f5f5f5'),
                'card': get_color_from_hex('#ffffff'),
                'texto_primario': (0.13, 0.13, 0.13, 1),
                'texto_secundario': (0.46, 0.46, 0.46, 1),
                'destaque': get_color_from_hex('#2196f3'),
                'sucesso': get_color_from_hex('#4caf50'),
                'erro': get_color_from_hex('#f44336'),
                'aviso': get_color_from_hex('#ff9800')
            },
            'azul': {
                'primaria': get_color_from_hex('#01579b'),
                'secundaria': get_color_from_hex('#0277bd'),
                'fundo': get_color_from_hex('#0a1f35'),
                'card': get_color_from_hex('#0f2b4a'),
                'texto_primario': (1, 1, 1, 1),
                'texto_secundario': (0.7, 0.84, 1, 1),
                'destaque': get_color_from_hex('#0288d1'),
                'sucesso': get_color_from_hex('#00e676'),
                'erro': get_color_from_hex('#ff5252'),
                'aviso': get_color_from_hex('#ffd740')
            },
            'verde': {
                'primaria': get_color_from_hex('#1b5e20'),
                'secundaria': get_color_from_hex('#2e7d32'),
                'fundo': get_color_from_hex('#0d1f0d'),
                'card': get_color_from_hex('#152a15'),
                'texto_primario': (1, 1, 1, 1),
                'texto_secundario': (0.8, 1, 0.8, 1),
                'destaque': get_color_from_hex('#4caf50'),
                'sucesso': get_color_from_hex('#69f0ae'),
                'erro': get_color_from_hex('#ff5252'),
                'aviso': get_color_from_hex('#ffd740')
            },
            'roxo': {
                'primaria': get_color_from_hex('#4a148c'),
                'secundaria': get_color_from_hex('#6a1b9a'),
                'fundo': get_color_from_hex('#1a0d2e'),
                'card': get_color_from_hex('#26143d'),
                'texto_primario': (1, 1, 1, 1),
                'texto_secundario': (0.9, 0.8, 1, 1),
                'destaque': get_color_from_hex('#9c27b0'),
                'sucesso': get_color_from_hex('#69f0ae'),
                'erro': get_color_from_hex('#ff5252'),
                'aviso': get_color_from_hex('#ffd740')
            }
        }
    
    def aplicar_tema(self, nome_tema, app):
        """Aplica um tema ao aplicativo"""
        if nome_tema not in self.temas:
            nome_tema = 'escuro'  # Fallback
        
        tema = self.temas[nome_tema]
        
        # Aplicar cores principais
        Window.clearcolor = tema['fundo']
        
        # Aqui você pode adicionar lógica para atualizar todas as telas
        # Por enquanto, vamos apenas salvar a preferência
        sistema = app.sistema
        sistema.configuracoes['interface']['tema'] = nome_tema
        sistema.salvar_configuracoes()
        
        print(f"🎨 Tema '{nome_tema}' aplicado com sucesso!")
        
        return tema
    
    def obter_tema_atual(self, app):
        """Retorna o tema atual do sistema"""
        sistema = app.sistema
        nome_tema = sistema.configuracoes['interface'].get('tema', 'escuro')
        return self.temas.get(nome_tema, self.temas['escuro'])