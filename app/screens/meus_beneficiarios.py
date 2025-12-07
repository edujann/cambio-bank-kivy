from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import datetime


    
class CardBeneficiario(BoxLayout):
    """Card individual para cada beneficiário"""
    
    def __init__(self, nome_beneficiario, dados, tela_pai, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(190)  # 🔥 VOLTEI para 190 (meio termo)
        self.padding = [15, 15, 15, 15]  # 🔥 AJUSTEI o padding
        self.spacing = 6  # 🔥 VOLTEI para 8
        
        self.nome_beneficiario = nome_beneficiario
        self.dados = dados
        self.tela_pai = tela_pai
        
        # Background do card
        with self.canvas.before:
            Color(0.20, 0.25, 0.33, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[6,]  # 🔥 VOLTEI para 8
            )
        self.bind(pos=self._atualizar_rect, size=self._atualizar_rect)
        
        self.criar_conteudo()

    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada"""
        from kivy.core.window import Window
        Window.size = (900, 700)
        print(f"🔍 DEBUG: on_pre_enter chamado - Carregando beneficiários...")
        self.carregar_beneficiarios()
    
    def _atualizar_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def criar_conteudo(self):
        # Linha 1: Nome do beneficiário (AGORA OCUPA A LARGURA TOTAL)
        linha1 = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        
        lbl_nome = Label(
            text=f"{self.nome_beneficiario}",
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            text_size=(None, None)
        )
        lbl_nome.bind(size=lbl_nome.setter('text_size'))
        
        linha1.add_widget(lbl_nome)
        
        # Linha 2: Informações básicas
        info_basica = f"{self.dados.get('banco', 'N/A')} |  {self.dados.get('pais', 'N/A')} |  {self.dados.get('cidade', 'N/A')}"
        lbl_info = Label(
            text=info_basica,
            font_size='13sp',
            color=(0.80, 0.84, 0.88, 1),
            halign='left',
            text_size=(None, None),
            size_hint_y=0.2
        )
        lbl_info.bind(size=lbl_info.setter('text_size'))
        
        # 🔥 NOVA LINHA: Dados do banco (cidade e país)
        info_banco = []
        if self.dados.get('cidade_banco'):
            info_banco.append(f"Banco Cidade: {self.dados['cidade_banco']}")
        if self.dados.get('pais_banco'):
            info_banco.append(f"Banco País: {self.dados['pais_banco']}")
        
        if info_banco:
            lbl_info_banco = Label(
                text=" | ".join(info_banco),
                font_size='12sp',
                color=(0.70, 0.84, 0.96, 1),  # Azul mais claro para diferenciar
                halign='left',
                text_size=(None, None),
                size_hint_y=0.15  # 🔥 AJUSTEI: de 0.2 para 0.15 para caber nova linha
            )
            lbl_info_banco.bind(size=lbl_info_banco.setter('text_size'))
        else:
            lbl_info_banco = Label(
                text="",
                size_hint_y=0.15
            )
        
        # Linha 3: Dados bancários (SWIFT, IBAN, ABA) - 🔥 AJUSTEI: de 0.2 para 0.15
        dados_bancarios = f"SWIFT: {self.dados.get('swift', 'N/A')} |  IBAN: {self.dados.get('iban', 'N/A')}"
        if self.dados.get('aba'):
            dados_bancarios += f" |  ABA: {self.dados['aba']}"
        
        lbl_bancarios = Label(
            text=dados_bancarios,
            font_size='12sp',
            color=(0.80, 0.84, 0.88, 1),
            halign='left',
            text_size=(None, None),
            size_hint_y=0.15  # 🔥 AJUSTEI: de 0.2 para 0.15
        )
        lbl_bancarios.bind(size=lbl_bancarios.setter('text_size'))
        
        # Linha 4: Botões de ação - 🔥 AJUSTEI: de 0.35 para 0.3 para compensar
        linha4 = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=12)
        
        btn_usar = Button(
            text='Usar em Transferência',
            font_size='13sp',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            on_press=self.usar_beneficiario
        )
        
        btn_editar = Button(
            text='Editar',
            font_size='13sp',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            on_press=self.editar_beneficiario
        )
        
        btn_excluir = Button(
            text='Excluir',
            font_size='13sp',
            background_color=(0.96, 0.36, 0.36, 1),
            color=(1, 1, 1, 1),
            on_press=self.excluir_beneficiario
        )
        
        linha4.add_widget(btn_usar)
        linha4.add_widget(btn_editar)
        linha4.add_widget(btn_excluir)
        
        # Adicionar todos os widgets
        self.add_widget(linha1)
        self.add_widget(lbl_info)
        self.add_widget(lbl_info_banco)  # 🔥 NOVA LINHA
        self.add_widget(lbl_bancarios)
        self.add_widget(linha4)
    
    def usar_beneficiario(self, instance):  # 🔥 CORREÇÃO: usar_beneficiario (sem 'r' extra)
        """Usa este beneficiário em uma nova transferência"""
        self.tela_pai.usar_beneficiario_em_transferencia(self.nome_beneficiario)

    
    def editar_beneficiario(self, instance):
        self.tela_pai.editar_beneficiario(self.nome_beneficiario, self.dados)
    
    def excluir_beneficiario(self, instance):
        self.tela_pai.excluir_beneficiario(self.nome_beneficiario, self.dados)


class TelaMeusBeneficiarios(Screen):
    """Tela principal para gerenciar beneficiários"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        """Chamado antes da tela ser mostrada - VERSÃO RESPONSIVA"""
        from kivy.core.window import Window
        from kivy.metrics import dp
        
        # 🔥 TAMANHO PREFERIDO PARA BENEFICIÁRIOS
        largura_preferida = dp(900)
        altura_preferida = dp(700)
        
        print(f"📐 Meus Beneficiários: {largura_preferida/dp(1)}x{altura_preferida/dp(1)}")
        
        # 1. Define tamanho preferido
        Window.size = (largura_preferida, altura_preferida)
        
        # 2. Ajusta automaticamente se não couber
        def ajustar_se_necessario(dt):
            altura_disponivel = Window.height
            largura_disponivel = Window.width
            
            print(f"📏 Tela disponível: {largura_disponivel:.0f}x{altura_disponivel:.0f}")
            
            precisa_ajustar = False
            
            # Se LARGURA muito estreita (<850px)
            if largura_disponivel < dp(850):
                print(f"⚠️  Tela estreita! Ajustando largura...")
                nova_largura = largura_disponivel * 0.95
                nova_altura = altura_preferida * (nova_largura / largura_preferida)
                Window.size = (nova_largura, nova_altura)
                precisa_ajustar = True
            
            # Se ALTURA não couber (700px > 90% da tela)
            if altura_preferida > altura_disponivel * 0.9:
                print(f"⚠️  Tela baixa! Ajustando altura...")
                nova_altura = altura_disponivel * 0.85
                if not precisa_ajustar:  # Só ajusta largura se já não tiver ajustado
                    nova_largura = largura_preferida * (nova_altura / altura_preferida)
                    Window.size = (nova_largura, nova_altura)
                precisa_ajustar = True
            
            if precisa_ajustar:
                print(f"📐 Tamanho ajustado: {Window.size[0]/dp(1):.0f}x{Window.size[1]/dp(1):.0f}")
            else:
                print(f"✅ Tela adequada - Mantendo {largura_preferida/dp(1)}x{altura_preferida/dp(1)}")
            
            # 🔥 POSICIONAMENTO PERSONALIZADO (Windows)
            try:
                import ctypes
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
                
                window_width, window_height = Window.size
                
                # Offset personalizado (ajuste se quiser)
                offset_x = 80  # 🔥 Mais à direita que outras telas
                offset_y = 50  # 🔥 Ajuste vertical
                
                x = (screen_width - window_width) // 2 + offset_x
                y = (screen_height - window_height) // 2 - offset_y
                
                Window.left = max(10, x)
                Window.top = max(10, y)
                
                print(f"📍 Beneficiários posicionada em: ({Window.left:.0f}, {Window.top:.0f})")
                
            except Exception as e:
                print(f"⚠️  Não foi possível posicionar: {e}")
                Window.center()
        
        from kivy.clock import Clock
        Clock.schedule_once(ajustar_se_necessario, 0.3)
        
        # 🔥 SEU CÓDIGO ORIGINAL (mantém)
        self.carregar_beneficiarios()
    
    def on_enter(self):
        """Chamado quando a tela é carregada - COM PROTEÇÃO"""
        from kivy.core.window import Window
        from kivy.metrics import dp
        
        # 🔥 PROTEÇÃO: Se por algum motivo ficou muito pequena
        if Window.width < dp(800) or Window.height < dp(600):
            print(f"⚠️  Janela muito pequena detectada! Restaurando tamanho mínimo...")
            Window.size = (dp(900), dp(700))
        
        print("👥 Tela Meus Beneficiários carregada")
        self.carregar_beneficiarios()
        
        # 🔥 NOVO: Rolar para o topo
        self.rolar_para_topo()

    def rolar_para_topo(self):
        """Rola a ScrollView para o topo - MESMA LÓGICA DAS OUTRAS TELAS"""
        try:
            from kivy.clock import Clock
            # Múltiplas tentativas para garantir
            Clock.schedule_once(self._executar_rolagem, 0.1)
            Clock.schedule_once(self._executar_rolagem, 0.5)  # Backup
        except Exception as e:
            print(f"⚠️ Erro ao agendar rolagem: {e}")

    def _executar_rolagem(self, dt):
        """Executa a rolagem para o topo - MESMA LÓGICA DAS OUTRAS TELAS"""
        try:
            print("🔄 Tentando rolar para o topo (Meus Beneficiários)...")
            
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

    # 🔥 MANTER TODOS OS MÉTODOS EXISTENTES SEM MODIFICAÇÕES
    def carregar_beneficiarios(self):
        """Método existente - NÃO MODIFICAR"""
        sistema = App.get_running_app().sistema
        
        if not hasattr(self, 'ids') or 'lista_beneficiarios' not in self.ids:
            return
        
        container = self.ids.lista_beneficiarios
        container.clear_widgets()
        
        if sistema.tipo_usuario_logado != 'cliente':
            self.mostrar_erro("Esta função é apenas para clientes!")
            return
        
        usuario_atual = sistema.usuario_logado
        # 🔥 CORREÇÃO: Beneficiários são uma LISTA, não um dicionário
        lista_beneficiarios = sistema.beneficiarios.get(usuario_atual, [])
        
        if not lista_beneficiarios:
            vazio_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
            vazio_box.padding = [20, 20, 20, 20]
            
            lbl_vazio = Label(
                text="📭 Nenhum beneficiário cadastrado",
                font_size='16sp',
                color=(0.80, 0.84, 0.88, 1)
            )
            
            lbl_instrucao = Label(
                text="Clique em 'Cadastrar Novo Beneficiário' para adicionar",
                font_size='12sp',
                color=(0.80, 0.84, 0.88, 1)
            )
            
            vazio_box.add_widget(lbl_vazio)
            vazio_box.add_widget(lbl_instrucao)
            container.add_widget(vazio_box)
            return
        
        # 🔥 CORREÇÃO: Iterar sobre a lista de beneficiários
        for beneficiario in lista_beneficiarios:
            nome_beneficiario = beneficiario['nome']
            card = CardBeneficiario(nome_beneficiario, beneficiario, self)
            container.add_widget(card)
        
        print(f"✅ {len(lista_beneficiarios)} beneficiários carregados")

    def cadastrar_novo_beneficiario(self):
        """Método existente - NÃO MODIFICAR"""
        from app.screens.cadastro_beneficiario import TelaCadastroBeneficiario
        
        if 'cadastro_beneficiario' not in self.manager.screen_names:
            self.manager.add_widget(TelaCadastroBeneficiario(name='cadastro_beneficiario'))
        
        self.manager.current = 'cadastro_beneficiario'

    def usar_beneficiario_em_transferencia(self, nome_beneficiario):
        """Método existente - NÃO MODIFICAR"""
        sistema = App.get_running_app().sistema
        print(f"🔍 DEBUG: Iniciando usar_beneficiario_em_transferencia para: {nome_beneficiario}")
        
        if 'transferencia' in self.manager.screen_names:
            tela_transferencia = self.manager.get_screen('transferencia')
            
            usuario_atual = sistema.usuario_logado
            lista_beneficiarios = sistema.beneficiarios.get(usuario_atual, [])
            
            # Encontrar o beneficiário pelo nome
            beneficiario_encontrado = None
            for benef in lista_beneficiarios:
                if benef['nome'] == nome_beneficiario:
                    beneficiario_encontrado = benef
                    break
            
            if beneficiario_encontrado:
                print(f"🔍 DEBUG: Beneficiário encontrado: {beneficiario_encontrado['nome']}")
                
                # 🔥 USAR O MÉTODO ESPECIAL que seta a flag
                if hasattr(tela_transferencia, 'preencher_dados_manual'):
                    tela_transferencia.preencher_dados_manual(beneficiario_encontrado)
                else:
                    # Fallback: preencher manualmente e setar flag
                    tela_transferencia.beneficiario_preenchido = True
                    tela_transferencia.ids.entry_beneficiario.text = beneficiario_encontrado['nome']
                    tela_transferencia.ids.entry_endereco.text = beneficiario_encontrado['endereco']
                    tela_transferencia.ids.entry_cidade.text = beneficiario_encontrado['cidade']
                    tela_transferencia.ids.entry_pais.text = beneficiario_encontrado['pais']
                    tela_transferencia.ids.entry_banco.text = beneficiario_encontrado['banco']
                    tela_transferencia.ids.endereco_banco.text = beneficiario_encontrado.get('endereco_banco', '')
                    tela_transferencia.ids.cidade_banco.text = beneficiario_encontrado.get('cidade_banco', '')  # 🔥 NOVO
                    tela_transferencia.ids.pais_banco.text = beneficiario_encontrado.get('pais_banco', '')      # 🔥 NOVO
                    tela_transferencia.ids.entry_swift.text = beneficiario_encontrado['swift']
                    tela_transferencia.ids.entry_iban.text = beneficiario_encontrado['iban']
                    tela_transferencia.ids.entry_aba.text = beneficiario_encontrado.get('aba', '')
                    
                    print(f"✅ Dados do beneficiário '{beneficiario_encontrado['nome']}' preenchidos na transferência")
            
            # Navegar para tela de transferência
            print(f"🔍 DEBUG: Navegando para tela de transferência")
            self.manager.current = 'transferencia'
        else:
            print(f"❌ Tela de transferência não encontrada no manager")

    # 🔥 MANTER TODOS OS OUTROS MÉTODOS EXISTENTES (editar_beneficiario, excluir_beneficiario, mostrar_erro, mostrar_sucesso, etc.)
    def editar_beneficiario(self, nome_beneficiario, dados):
        """Método existente - NÃO MODIFICAR"""
        from app.screens.cadastro_beneficiario import TelaCadastroBeneficiario
        
        if 'editar_beneficiario' not in self.manager.screen_names:
            tela_edicao = TelaCadastroBeneficiario(name='editar_beneficiario')
            tela_edicao.modo_edicao = True
            self.manager.add_widget(tela_edicao)
        
        tela_edicao = self.manager.get_screen('editar_beneficiario')
        tela_edicao.carregar_dados_edicao(nome_beneficiario, dados)
        self.manager.current = 'editar_beneficiario'

    def excluir_beneficiario(self, nome_beneficiario, dados):
        """Método existente - NÃO MODIFICAR"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        lbl_titulo = Label(
            text='🗑️ Confirmar Exclusão',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        detalhes = f"Tem certeza que deseja excluir o beneficiário?\n\n👤 Nome: {nome_beneficiario}\n🏦 Banco: {dados.get('banco', 'N/A')}\n\nEsta ação não pode ser desfeita."
        
        lbl_detalhes = Label(
            text=detalhes,
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        btn_cancelar = Button(
            text='Cancelar',
            background_color=(0.55, 0.36, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_confirmar = Button(
            text='Confirmar Exclusão',
            background_color=(0.96, 0.36, 0.36, 1),
            color=(1, 1, 1, 1)
        )
        
        botoes_layout.add_widget(btn_cancelar)
        botoes_layout.add_widget(btn_confirmar)
        
        content.add_widget(lbl_titulo)
        content.add_widget(lbl_detalhes)
        content.add_widget(botoes_layout)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(450, 300),
            background_color=(0.12, 0.16, 0.23, 1),
            auto_dismiss=False
        )
        
        def confirmar_exclusao(instance):
            sistema = App.get_running_app().sistema
            usuario_atual = sistema.usuario_logado
            
            # 🔥 CORREÇÃO: Remover da lista de beneficiários
            if usuario_atual in sistema.beneficiarios:
                lista_beneficiarios = sistema.beneficiarios[usuario_atual]
                
                # Encontrar e remover o beneficiário
                for i, benef in enumerate(lista_beneficiarios):
                    if benef['nome'] == nome_beneficiario:
                        del lista_beneficiarios[i]
                        sistema.salvar_beneficiarios()
                        
                        popup.dismiss()
                        self.mostrar_sucesso(f"✅ Beneficiário '{nome_beneficiario}' excluído com sucesso!")
                        self.carregar_beneficiarios()
                        return
                
                # Se não encontrou
                popup.dismiss()
                self.mostrar_erro("❌ Beneficiário não encontrado!")
            else:
                popup.dismiss()
                self.mostrar_erro("❌ Erro ao excluir beneficiário!")
        
        def cancelar_exclusao(instance):
            popup.dismiss()
        
        btn_confirmar.bind(on_press=confirmar_exclusao)
        btn_cancelar.bind(on_press=cancelar_exclusao)
        
        popup.open()

    def mostrar_erro(self, mensagem):
        """Método existente - NÃO MODIFICAR"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl_erro = Label(
            text=mensagem,
            color=(1, 0.3, 0.3, 1),
            font_size='14sp'
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
        """Método existente - NÃO MODIFICAR"""
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

    def voltar_dashboard(self):
        """Método existente - NÃO MODIFICAR"""
        self.manager.current = 'dashboard'