from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button

class TelaListaClientes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - carrega clientes"""
        self.carregar_clientes()
    
    def carregar_clientes(self):
        """Carrega e exibe a lista de clientes"""
        sistema = App.get_running_app().sistema
        clientes = sistema.listar_clientes()
        
        if hasattr(self, 'ids') and 'clientes_container' in self.ids:
            container = self.ids.clientes_container
            container.clear_widgets()
            
            if not clientes:
                label = Label(
                    text="Nenhum cliente cadastrado",
                    color=(0.80, 0.84, 0.88, 1),
                    size_hint_y=None,
                    height=40
                )
                container.add_widget(label)
                return
            
            # Título
            titulo = Label(
                text=f"📋 CLIENTES CADASTRADOS ({len(clientes)})",
                font_size='14sp',
                bold=True,
                color=(0.23, 0.51, 0.96, 1),
                size_hint_y=None,
                height=40
            )
            container.add_widget(titulo)
            
            # Cabeçalho
            cabecalho = GridLayout(cols=4, size_hint_y=None, height=30, spacing=5)
            cabecalho.add_widget(Label(text='USUÁRIO', bold=True, font_size='10sp'))
            cabecalho.add_widget(Label(text='NOME', bold=True, font_size='10sp'))
            cabecalho.add_widget(Label(text='CONTAS', bold=True, font_size='10sp'))
            cabecalho.add_widget(Label(text='CADASTRO', bold=True, font_size='10sp'))
            container.add_widget(cabecalho)
            
            # Lista de clientes
            for cliente in clientes:
                cliente_row = GridLayout(cols=4, size_hint_y=None, height=40, spacing=5)
                
                cliente_row.add_widget(Label(
                    text=cliente['username'],
                    font_size='10sp',
                    text_size=(80, None),
                    halign='left'
                ))
                
                cliente_row.add_widget(Label(
                    text=cliente['nome'][:20] + ('...' if len(cliente['nome']) > 20 else ''),
                    font_size='10sp',
                    text_size=(120, None),
                    halign='left'
                ))
                
                cliente_row.add_widget(Label(
                    text=str(cliente['quantidade_contas']),
                    font_size='10sp',
                    text_size=(40, None),
                    halign='center'
                ))
                
                cliente_row.add_widget(Label(
                    text=cliente.get('data_cadastro', 'N/A'),
                    font_size='9sp',
                    text_size=(70, None),
                    halign='center'
                ))
                
                container.add_widget(cliente_row)
            
            container.height = container.minimum_height
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'