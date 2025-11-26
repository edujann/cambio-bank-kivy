from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import hashlib

class TelaMeusDados(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.campos_tab_order = [
            'entry_nome', 'entry_documento', 'entry_email', 'entry_telefone',
            'entry_endereco', 'entry_cidade', 'entry_cep', 'entry_estado',
            'entry_pais', 'entry_senha_atual', 'entry_nova_senha', 'entry_confirmar_senha'
        ]
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (700, 900)
        print("📥 Preparando tela Meus Dados...")
        self.carregar_dados_usuario()
    
    def on_enter(self):
        """Chamado quando a tela é carregada"""
        print("👤 Tela Meus Dados carregada")
        
        # Configurar evento de teclado
        from kivy.core.window import Window
        Window.bind(on_key_down=self._on_keyboard_down)
        
        # Garantir foco no primeiro campo
        from kivy.clock import Clock
        Clock.schedule_once(self.set_focus_nome, 0.3)
        
        # 🔥 Rolar para o topo
        self.rolar_para_topo()
    
    def rolar_para_topo(self):
        """Rola a ScrollView para o topo - MÉTODO CORRIGIDO"""
        try:
            from kivy.clock import Clock
            # Múltiplas tentativas para garantir
            Clock.schedule_once(self._executar_rolagem, 0.1)
            Clock.schedule_once(self._executar_rolagem, 0.5)  # Backup
        except Exception as e:
            print(f"⚠️ Erro ao agendar rolagem: {e}")
    
    def _executar_rolagem(self, dt):
        """Executa a rolagem para o topo - MÉTODO CORRIGIDO"""
        try:
            print("🔄 Tentando rolar para o topo...")
            
            # Método 1: Buscar por ID específico
            if hasattr(self, 'ids'):
                if 'scroll_principal' in self.ids:
                    self.ids.scroll_principal.scroll_y = 1.0
                    print("✅ ScrollView rolada para o topo (via ID 'scroll_principal')")
                    return
                
                # Método 2: Buscar qualquer ScrollView nos IDs
                for widget_id, widget in self.ids.items():
                    if hasattr(widget, 'scroll_y'):
                        widget.scroll_y = 1.0
                        print(f"✅ ScrollView encontrada por ID '{widget_id}' e rolada para o topo")
                        return
            
            # Método 3: Buscar na hierarquia completa
            def encontrar_scrollview(widget):
                if hasattr(widget, 'scroll_y'):
                    return widget
                if hasattr(widget, 'children'):
                    for child in widget.children:
                        result = encontrar_scrollview(child)
                        if result:
                            return result
                return None
            
            scrollview = encontrar_scrollview(self)
            if scrollview:
                scrollview.scroll_y = 1.0
                print("✅ ScrollView encontrada na hierarquia e rolada para o topo")
            else:
                print("❌ ScrollView não encontrada de nenhuma forma")
                
        except Exception as e:
            print(f"❌ Erro ao executar rolagem: {e}")
    
    def _on_keyboard_down(self, window, key, scancode, codepoint, modifier):
        """Captura eventos de teclado - VERSÃO DEFINITIVA"""
        # Verificar apenas TAB pelo keycode E scancode
        is_tab_key = (key == 9) or (scancode == 43)  # TAB keycode e scancode
        
        if is_tab_key:
            print(f"🎹 Tab detectado! (key: {key}, scancode: {scancode})")
            self.proximo_campo_tab()
            return True  # Consumir apenas TAB
        
        # Para TODAS as outras teclas (incluindo "2", "a", "enter", etc)
        # Deixar o Kivy processar normalmente
        return False
    
    def proximo_campo_tab(self):
        """Navega para o próximo campo"""
        if not hasattr(self, 'ids'):
            return
        
        # Encontrar campo atual com foco
        campo_atual = None
        for campo_id in self.campos_tab_order:
            if (campo_id in self.ids and 
                hasattr(self.ids[campo_id], 'focus') and 
                self.ids[campo_id].focus):
                campo_atual = campo_id
                break
        
        if campo_atual:
            try:
                indice_atual = self.campos_tab_order.index(campo_atual)
                proximo_indice = (indice_atual + 1) % len(self.campos_tab_order)
                proximo_campo = self.campos_tab_order[proximo_indice]
                
                if proximo_campo in self.ids:
                    self.ids[proximo_campo].focus = True
                    print(f"✅ Tab: {campo_atual} → {proximo_campo}")
            except ValueError:
                if self.campos_tab_order and self.campos_tab_order[0] in self.ids:
                    self.ids[self.campos_tab_order[0]].focus = True
        else:
            if self.campos_tab_order and self.campos_tab_order[0] in self.ids:
                self.ids[self.campos_tab_order[0]].focus = True
    
    def set_focus_nome(self, dt):
        """Define o foco no campo nome"""
        if hasattr(self, 'ids') and 'entry_nome' in self.ids:
            self.ids.entry_nome.focus = True
            print("✅ Foco definido no campo Nome")
    
    def focus_next_field(self, next_field_id):
        """Muda o foco para o próximo campo quando Enter é pressionado"""
        if hasattr(self, 'ids') and next_field_id in self.ids:
            self.ids[next_field_id].focus = True
            print(f"🔍 Enter: Indo para {next_field_id}")
    
    def on_leave(self):
        """Chamado quando sai da tela"""
        from kivy.core.window import Window
        Window.unbind(on_key_down=self._on_keyboard_down)
        print("🚪 Saindo da tela Meus Dados...")
    
    def carregar_dados_usuario(self):
        """Carrega os dados do usuário - VERSÃO COM SUPABASE"""
        sistema = App.get_running_app().sistema
        
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            self.voltar_dashboard()
            return
        
        print(f"📊 Carregando dados para: {sistema.usuario_logado}")
        
        # 🔥🔥🔥 NOVO: TENTAR CARREGAR DO SUPABASE PRIMEIRO
        usuario_atual = None
        
        if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
            try:
                print("🔍 Buscando dados atualizados no Supabase...")
                usuario_supabase = sistema.supabase.obter_usuario(sistema.usuario_logado)
                
                if usuario_supabase:
                    print("✅ Dados encontrados no Supabase, atualizando localmente...")
                    # Atualizar dados locais com informações do Supabase
                    sistema.usuarios[sistema.usuario_logado].update({
                        'email': usuario_supabase.get('email', ''),
                        'telefone': usuario_supabase.get('telefone', ''),
                        'endereco': usuario_supabase.get('endereco', ''),
                        'cidade': usuario_supabase.get('cidade', ''),
                        'cep': usuario_supabase.get('cep', ''),
                        'estado': usuario_supabase.get('estado', ''),
                        'pais': usuario_supabase.get('pais', '')
                    })
                    sistema.salvar_usuarios()
            except Exception as e:
                print(f"⚠️ Erro ao buscar dados no Supabase: {e}")
        
        # Usar dados atualizados (locais ou do Supabase)
        usuario_atual = sistema.usuarios[sistema.usuario_logado]
        print(f"📝 Dados carregados: {usuario_atual}")
        
        # Preencher campos com dados do usuário
        if hasattr(self, 'ids'):
            # Dados pessoais (não editáveis nesta tela)
            self.ids.entry_nome.text = usuario_atual.get('nome') or ''
            self.ids.entry_documento.text = usuario_atual.get('documento') or ''
            
            # Dados editáveis
            self.ids.entry_email.text = usuario_atual.get('email') or ''
            self.ids.entry_telefone.text = usuario_atual.get('telefone') or ''
            
            # Campos de endereço
            self.ids.entry_endereco.text = usuario_atual.get('endereco') or ''
            self.ids.entry_cidade.text = usuario_atual.get('cidade') or ''
            self.ids.entry_cep.text = usuario_atual.get('cep') or ''
            self.ids.entry_estado.text = usuario_atual.get('estado') or ''
            self.ids.entry_pais.text = usuario_atual.get('pais') or ''
            
            # Limpar campos de senha
            self.ids.entry_senha_atual.text = ''
            self.ids.entry_nova_senha.text = ''
            self.ids.entry_confirmar_senha.text = ''
            
            print("✅ Dados carregados com sucesso!")
        else:
            print("❌ IDs não disponíveis para carregar dados")
    
    def criar_card_conta(self, conta_num, dados_conta):
        """Cria um card para cada conta"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=[15, 10],
            spacing=5
        )
        
        # Background do card
        with card.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            card.rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[6,]
            )
        
        card.bind(pos=self._atualizar_card_rect, size=self._atualizar_card_rect)
        
        # Linha 1: Número da conta e moeda
        linha1 = BoxLayout(orientation='horizontal', size_hint_y=0.6)
        
        lbl_info = Label(
            text=f"Conta: {conta_num} | Moeda: {dados_conta['moeda']}",
            font_size='13sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            text_size=(None, None)
        )
        lbl_info.bind(size=lbl_info.setter('text_size'))
        
        lbl_saldo = Label(
            text=f"{dados_conta['saldo']:,.2f}",
            font_size='13sp',
            bold=True,
            color=(0.23, 0.51, 0.96, 1),
            halign='right'
        )
        
        linha1.add_widget(lbl_info)
        linha1.add_widget(lbl_saldo)
        
        # Linha 2: Data de criação
        linha2 = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        lbl_data = Label(
            text=f"{dados_conta.get('data_criacao', 'N/A')}",
            font_size='11sp',
            color=(0.80, 0.84, 0.88, 1),
            halign='left',
            text_size=(None, None)
        )
        lbl_data.bind(size=lbl_data.setter('text_size'))
        
        linha2.add_widget(lbl_data)
        linha2.add_widget(Label())  # Espaço vazio para alinhamento
        
        card.add_widget(linha1)
        card.add_widget(linha2)
        
        return card
    
    def _atualizar_card_rect(self, instance, value):
        """Atualiza o retângulo de background do card"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def salvar_alteracoes(self):
        """Salva as alterações nos dados do usuário - VERSÃO COM SUPABASE"""
        sistema = App.get_running_app().sistema
        
        try:
            # Validar campos obrigatórios
            email = self.ids.entry_email.text.strip()
            telefone = self.ids.entry_telefone.text.strip()
            
            if not email or not telefone:
                self.mostrar_erro("Preencha todos os campos obrigatórios!")
                return
            
            usuario_atual = sistema.usuarios[sistema.usuario_logado]
            
            # Verificar alteração de senha
            senha_atual = self.ids.entry_senha_atual.text
            nova_senha = self.ids.entry_nova_senha.text
            confirmar_senha = self.ids.entry_confirmar_senha.text
            
            senha_alterada = False
            nova_senha_hash = None
            
            if senha_atual or nova_senha or confirmar_senha:
                # Validar alteração de senha
                if not all([senha_atual, nova_senha, confirmar_senha]):
                    self.mostrar_erro("Para alterar a senha, preencha todos os campos de senha!")
                    return
                
                # Verificar senha atual
                if self.hash_senha(senha_atual) != usuario_atual['senha']:
                    self.mostrar_erro("Senha atual incorreta!")
                    return
                
                # Verificar se novas senhas coincidem
                if nova_senha != confirmar_senha:
                    self.mostrar_erro("As novas senhas não coincidem!")
                    return
                
                # Verificar força da senha
                if len(nova_senha) < 6:
                    self.mostrar_erro("A nova senha deve ter pelo menos 6 caracteres!")
                    return
                
                # Preparar nova senha hash
                nova_senha_hash = self.hash_senha(nova_senha)
                senha_alterada = True
            
            # Preparar dados atualizados
            dados_atualizados = {
                'username': sistema.usuario_logado,
                'nome': usuario_atual.get('nome', ''),
                'email': email,
                'documento': usuario_atual.get('documento', ''),
                'telefone': telefone,
                'endereco': self.ids.entry_endereco.text.strip(),
                'cidade': self.ids.entry_cidade.text.strip(),
                'cep': self.ids.entry_cep.text.strip(),
                'estado': self.ids.entry_estado.text.strip(),
                'pais': self.ids.entry_pais.text.strip(),
                'moedas_selecionadas': usuario_atual.get('moedas_selecionadas', [])
            }
            
            # 🔥🔥🔥 NOVO: ATUALIZAR NO SUPABASE PRIMEIRO
            print("💾 Tentando salvar alterações no Supabase...")
            sucesso_supabase = False
            
            if hasattr(sistema, 'supabase') and sistema.supabase.conectado:
                try:
                    # Se senha foi alterada, incluir nos dados do Supabase
                    if senha_alterada:
                        dados_atualizados['senha'] = nova_senha
                    
                    sucesso_supabase = sistema.supabase.salvar_usuario(dados_atualizados)
                    if sucesso_supabase:
                        print("✅ Dados atualizados no Supabase!")
                    else:
                        print("❌ Falha ao atualizar no Supabase")
                except Exception as e:
                    print(f"⚠️ Erro no Supabase: {e}")
            else:
                print("⚠️ Supabase não disponível, salvando apenas localmente")
            
            # 🔥 CONTINUAR: ATUALIZAR LOCALMENTE (fallback)
            sistema.usuarios[sistema.usuario_logado]['email'] = email
            sistema.usuarios[sistema.usuario_logado]['telefone'] = telefone
            sistema.usuarios[sistema.usuario_logado]['endereco'] = dados_atualizados['endereco']
            sistema.usuarios[sistema.usuario_logado]['cidade'] = dados_atualizados['cidade']
            sistema.usuarios[sistema.usuario_logado]['cep'] = dados_atualizados['cep']
            sistema.usuarios[sistema.usuario_logado]['estado'] = dados_atualizados['estado']
            sistema.usuarios[sistema.usuario_logado]['pais'] = dados_atualizados['pais']
            
            # Atualizar senha localmente se alterada
            if senha_alterada:
                sistema.usuarios[sistema.usuario_logado]['senha'] = nova_senha_hash

            # Salvar alterações locais
            sistema.salvar_usuarios()
            
            # Mostrar mensagem apropriada
            if sucesso_supabase:
                self.mostrar_sucesso("✅ Dados atualizados com sucesso!\n(Sincronizado na nuvem)")
            else:
                self.mostrar_sucesso("✅ Dados atualizados localmente!\n(Modo offline)")
            
            self.voltar_dashboard()
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar alterações: {str(e)}")
    
    def hash_senha(self, senha):
        """Faz o hash da senha (igual ao sistema)"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def voltar_dashboard(self):
        """Volta para o dashboard"""
        self.manager.current = 'dashboard'
    
    def mostrar_erro(self, mensagem):
        """Mostra popup de erro"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp'
        )
        
        btn_ok = Button(
            text='TENTAR NOVAMENTE',
            size_hint_y=None,
            height=40,
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(lbl_erro)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Erro',
            title_color=(1, 0.3, 0.3, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra popup de sucesso"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_sucesso = Label(
            text=mensagem,
            color=(0.2, 0.8, 0.2, 1),
            font_size='14sp'
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
            title='Sucesso',
            title_color=(0.2, 0.8, 0.2, 1),
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            background_color=(0.12, 0.16, 0.23, 1)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()