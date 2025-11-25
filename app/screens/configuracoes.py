from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import json
import os

class TelaConfiguracoes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.carregar_configuracoes()
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (1000, 800)
        print("⚙️ Tela de configurações carregada")
        self.carregar_configuracoes_interface()
    
    def carregar_configuracoes(self):
        """Carrega as configurações do sistema"""
        sistema = App.get_running_app().sistema
        self.configuracoes = sistema.configuracoes
    
    def salvar_configuracoes(self):
        """Salva as configurações no sistema"""
        sistema = App.get_running_app().sistema
        sistema.configuracoes = self.configuracoes
        return sistema.salvar_configuracoes()
    
    def carregar_configuracoes_interface(self):
        """Carrega as configurações na interface"""
        if not hasattr(self, 'ids'):
            return
        
        try:
            # Configurações do Sistema
            if 'input_horario_abertura' in self.ids:
                self.ids.input_horario_abertura.text = self.configuracoes['sistema']['horario_abertura']
            
            if 'input_horario_fechamento' in self.ids:
                self.ids.input_horario_fechamento.text = self.configuracoes['sistema']['horario_fechamento']
            
            # Configurações Financeiras
            if 'input_limite_diario' in self.ids:
                self.ids.input_limite_diario.text = str(self.configuracoes['financeiras']['limite_transferencia_diario'])
            
            if 'input_limite_mensal' in self.ids:
                self.ids.input_limite_mensal.text = str(self.configuracoes['financeiras']['limite_transferencia_mensal'])
            
            if 'input_taxa_internacional' in self.ids:
                self.ids.input_taxa_internacional.text = str(self.configuracoes['financeiras']['taxa_transferencia_internacional'] * 100)
            
            if 'input_comissao_minima' in self.ids:
                self.ids.input_comissao_minima.text = str(self.configuracoes['financeiras']['comissao_minima'])
            
            # Configurações de Segurança
            if 'input_tamanho_senha' in self.ids:
                self.ids.input_tamanho_senha.text = str(self.configuracoes['seguranca']['tamanho_minimo_senha'])
            
            if 'input_expiracao_senha' in self.ids:
                self.ids.input_expiracao_senha.text = str(self.configuracoes['seguranca']['expiracao_senha_dias'])
            
            if 'input_tentativas_login' in self.ids:
                self.ids.input_tentativas_login.text = str(self.configuracoes['seguranca']['tentativas_login'])
            
            if 'toggle_2fa' in self.ids:
                self.ids.toggle_2fa.active = self.configuracoes['seguranca']['requer_2fa']
            
            if 'toggle_notificacao_email' in self.ids:
                self.ids.toggle_notificacao_email.active = self.configuracoes['seguranca']['notificacao_email']
            
            # Configurações de Interface
            if 'combo_tema' in self.ids:
                # 🔥 CARREGAR TEMAS DISPONÍVEIS
                temas_disponiveis = self.configuracoes['interface'].get(
                    'temas_disponiveis', 
                    ['escuro', 'claro', 'azul', 'verde', 'roxo']
                )
                self.ids.combo_tema.values = temas_disponiveis
                self.ids.combo_tema.text = self.configuracoes['interface']['tema']
            
            print("✅ Configurações carregadas na interface")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações na interface: {e}")
    
    def salvar_configuracoes_sistema(self):
        """Salva as configurações do sistema"""
        try:
            # Sistema
            self.configuracoes['sistema']['horario_abertura'] = self.ids.input_horario_abertura.text
            self.configuracoes['sistema']['horario_fechamento'] = self.ids.input_horario_fechamento.text
            
            # Financeiras
            self.configuracoes['financeiras']['limite_transferencia_diario'] = float(self.ids.input_limite_diario.text)
            self.configuracoes['financeiras']['limite_transferencia_mensal'] = float(self.ids.input_limite_mensal.text)
            self.configuracoes['financeiras']['taxa_transferencia_internacional'] = float(self.ids.input_taxa_internacional.text) / 100
            self.configuracoes['financeiras']['comissao_minima'] = float(self.ids.input_comissao_minima.text)
            
            # Segurança
            self.configuracoes['seguranca']['tamanho_minimo_senha'] = int(self.ids.input_tamanho_senha.text)
            self.configuracoes['seguranca']['expiracao_senha_dias'] = int(self.ids.input_expiracao_senha.text)
            self.configuracoes['seguranca']['tentativas_login'] = int(self.ids.input_tentativas_login.text)
            self.configuracoes['seguranca']['requer_2fa'] = self.ids.toggle_2fa.active
            self.configuracoes['seguranca']['notificacao_email'] = self.ids.toggle_notificacao_email.active
            
            # Interface
            tema_anterior = self.configuracoes['interface']['tema']
            self.configuracoes['interface']['tema'] = self.ids.combo_tema.text
            self.configuracoes['interface']['idioma'] = self.ids.combo_idioma.text
            self.configuracoes['interface']['moeda_padrao'] = self.ids.combo_moeda_padrao.text
            
            # 🔥 APLICAR TEMA SE MUDOU
            app = App.get_running_app()
            if tema_anterior != self.ids.combo_tema.text:
                app.gerenciador_temas.aplicar_tema(self.ids.combo_tema.text, app)
            
            if self.salvar_configuracoes():
                self.mostrar_sucesso("Configurações salvas com sucesso!\n\nTema aplicado: " + self.ids.combo_tema.text)
            else:
                self.mostrar_erro("Erro ao salvar configurações!")
                
        except ValueError as e:
            self.mostrar_erro("Verifique os valores informados!")
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar: {str(e)}")

    def mostrar_preview_tema(self):
        """Mostra um preview rápido do tema selecionado"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        tema_selecionado = self.ids.combo_tema.text
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_titulo = Label(
            text=f"Preview do Tema: {tema_selecionado.upper()}",
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(300, None),
            halign='center'
        )
        
        # Cards de exemplo com cores do tema
        app = App.get_running_app()
        tema = app.gerenciador_temas.temas.get(tema_selecionado, app.gerenciador_temas.temas['escuro'])
        
        card_exemplo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=10
        )
        with card_exemplo.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*tema['card'])
            RoundedRectangle(pos=card_exemplo.pos, size=card_exemplo.size, radius=[8,])
        
        lbl_exemplo = Label(
            text="Este é um exemplo do tema selecionado",
            color=tema['texto_primario'],
            font_size='14sp'
        )
        
        card_exemplo.add_widget(lbl_exemplo)
        
        btn_fechar = Button(
            text='Fechar Preview',
            size_hint_y=None,
            height=40,
            background_color=tema['destaque'],
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_titulo)
        content.add_widget(card_exemplo)
        content.add_widget(btn_fechar)
        
        popup = Popup(
            title=f'Preview - Tema {tema_selecionado}',
            title_color=tema['destaque'],
            content=content,
            size_hint=(None, None),
            size=(350, 250),
            background_color=tema['fundo'],
            auto_dismiss=True
        )
        
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

    def restaurar_padroes(self):
        """Restaura as configurações padrão"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_confirmacao = Label(
            text="Tem certeza que deseja restaurar todas as configurações para os valores padrão?\n\nEsta ação não pode ser desfeita.",
            font_size='14sp',
            color=(1, 1, 1, 1),
            text_size=(400, None),
            halign='center'
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Restaurar Padrões',
            background_color=(0.96, 0.36, 0.36, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        
        content.add_widget(lbl_confirmacao)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Restaurar Configurações Padrão',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(450, 250),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar(instance):
            sistema = App.get_running_app().sistema
            self.configuracoes = sistema.configuracoes_padrao()
            self.carregar_configuracoes_interface()
            self.salvar_configuracoes()
            popup.dismiss()
            self.mostrar_sucesso("Configurações restauradas para os valores padrão!")
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()
    
    def gerenciar_taxas_cambio(self):
        """Abre o gerenciador de taxas de câmbio"""
        self.mostrar_popup_taxas_cambio()
    
    def mostrar_popup_taxas_cambio(self):
        """Mostra popup para gerenciar taxas de câmbio"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.scrollview import ScrollView
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_titulo = Label(
            text="GERENCIAR TAXAS DE CÂMBIO",
            font_size='16sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            text_size=(400, None),
            halign='center'
        )
        
        scroll = ScrollView()
        grid_taxas = GridLayout(cols=3, spacing=10, size_hint_y=None, padding=[10, 10])
        grid_taxas.bind(minimum_height=grid_taxas.setter('height'))
        
        # Header
        grid_taxas.add_widget(Label(text='Par de Moedas', font_size='12sp', bold=True, color=(1,1,1,1)))
        grid_taxas.add_widget(Label(text='Taxa Atual', font_size='12sp', bold=True, color=(1,1,1,1)))
        grid_taxas.add_widget(Label(text='Nova Taxa', font_size='12sp', bold=True, color=(1,1,1,1)))
        
        # Taxas existentes
        taxas = self.configuracoes['financeiras']['taxas_cambio']
        self.campos_taxas = {}
        
        for par, taxa in taxas.items():
            grid_taxas.add_widget(Label(text=par, font_size='11sp', color=(0.9,0.9,0.9,1)))
            grid_taxas.add_widget(Label(text=f"{taxa:.4f}", font_size='11sp', color=(0.9,0.9,0.9,1)))
            
            input_taxa = TextInput(
                text=str(taxa),
                font_size='11sp',
                size_hint_y=None,
                height=40,
                multiline=False,
                background_color=(0.20, 0.25, 0.33, 1),
                foreground_color=(1, 1, 1, 1)
            )
            self.campos_taxas[par] = input_taxa
            grid_taxas.add_widget(input_taxa)
        
        grid_taxas.height = len(taxas) * 50 + 60  # Ajustar altura
        
        scroll.add_widget(grid_taxas)
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_salvar = Button(
            text='Salvar Taxas',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_cancelar = Button(
            text='Fechar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_salvar)
        botoes_layout.add_widget(btn_cancelar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(scroll)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='Taxas de Câmbio',
            title_color=(0.23, 0.51, 0.96, 1),
            content=content,
            size_hint=(None, None),
            size=(500, 400),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def salvar_taxas(instance):
            try:
                for par, input_taxa in self.campos_taxas.items():
                    nova_taxa = float(input_taxa.text)
                    self.configuracoes['financeiras']['taxas_cambio'][par] = nova_taxa
                
                # Atualizar no sistema também
                sistema = App.get_running_app().sistema
                sistema.taxas_cambio = self.configuracoes['financeiras']['taxas_cambio']
                
                self.salvar_configuracoes()
                popup.dismiss()
                self.mostrar_sucesso("Taxas de câmbio atualizadas com sucesso!")
                
            except ValueError:
                self.mostrar_erro("Verifique os valores das taxas!")
        
        def cancelar(instance):
            popup.dismiss()
        
        btn_salvar.bind(on_press=salvar_taxas)
        btn_cancelar.bind(on_press=cancelar)
        
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_sucesso)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='✅ Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp',
            text_size=(350, None),
            halign='center'
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='❌ Erro',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'