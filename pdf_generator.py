import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from kivy.app import App
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import HRFlowable

class PDFGenerator:
    def __init__(self):
        self.caminho_downloads = os.path.expanduser("~/Downloads")
        print(f"🔍 PDFGenerator: Pasta Downloads = {self.caminho_downloads}")
        
        if not os.path.exists(self.caminho_downloads):
            print("⚠️ PDFGenerator: Pasta Downloads não existe, criando...")
            os.makedirs(self.caminho_downloads)

    def gerar_comprovante_transferencia(self, transferencia_id, dados_transferencia, dados_cliente):
        """Gera comprovante de transferência em PDF - VERSÃO CORRIGIDA"""
        
        try:
            print(f"🔍 PDFGenerator: Iniciando geração para {transferencia_id}")
            
            # Nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"comprovante_{transferencia_id}_{timestamp}.pdf"
            caminho_completo = os.path.join(self.caminho_downloads, nome_arquivo)
            
            print(f"🔍 PDFGenerator: Caminho completo = {caminho_completo}")
            
            # Criar PDF
            print("🔍 PDFGenerator: Criando canvas PDF...")
            pdf = canvas.Canvas(caminho_completo, pagesize=A4)
            width, height = A4
            
            print("🔍 PDFGenerator: Configurando PDF...")
            pdf.setTitle(f"Comprovante {transferencia_id}")
            
            # CABEÇALHO
            print("🔍 PDFGenerator: Adicionando cabeçalho...")
            self._adicionar_cabecalho(pdf, width, height, transferencia_id)
            
            # DADOS DA TRANSFERÊNCIA
            print("🔍 PDFGenerator: Adicionando dados transferência...")
            y_pos = self._adicionar_dados_transferencia(pdf, width, height, dados_transferencia)
            
            # 🔥 CORREÇÃO: REMOVIDA CHAMADA PARA _adicionar_dados_remetente
            # ESSA FUNÇÃO FOI REMOVIDA DO CÓDIGO
            
            # DADOS DO BENEFICIÁRIO
            print("🔍 PDFGenerator: Adicionando dados beneficiário...")
            y_pos = self._adicionar_dados_beneficiario(pdf, width, height, y_pos, dados_transferencia)
            
            # INFORMAÇÕES BANCÁRIAS
            print("🔍 PDFGenerator: Adicionando dados bancários...")
            y_pos = self._adicionar_dados_bancarios(pdf, width, height, y_pos, dados_transferencia)
            
            # DADOS SWIFT DO PAGAMENTO (apenas para transferências internacionais concluídas)
            if dados_transferencia.get('status') == 'completed' and dados_transferencia.get('dados_swift_pagamento'):
                print("🔍 PDFGenerator: Adicionando dados SWIFT pagamento...")
                y_pos = self._adicionar_dados_swift_pagamento(pdf, width, height, y_pos, dados_transferencia['dados_swift_pagamento'])
            
            # RODAPÉ
            print("🔍 PDFGenerator: Adicionando rodapé...")
            self._adicionar_rodape(pdf, width, height, dados_transferencia)
            
            # SALVAR
            print("🔍 PDFGenerator: Salvando PDF...")
            pdf.save()
            
            # Verificar se arquivo foi criado
            if os.path.exists(caminho_completo):
                tamanho = os.path.getsize(caminho_completo)
                print(f"✅ PDFGenerator: PDF criado com sucesso! Tamanho: {tamanho} bytes")
                print(f"📍 PDFGenerator: Local: {caminho_completo}")
            else:
                print("❌ PDFGenerator: Arquivo não foi criado!")
                raise Exception("Arquivo PDF não foi criado")
            
            return caminho_completo
            
        except Exception as e:
            print(f"❌ PDFGenerator: Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _adicionar_cabecalho(self, pdf, width, height, transferencia_id):
        """Cabeçalho elegante com informações completas em inglês"""
        # Azul escuro elegante
        pdf.setFillColorRGB(0.08, 0.18, 0.32)  # Azul marinho escuro
        pdf.rect(0, height-100, width, 100, fill=1)  # 🔥 AUMENTADO PARA 100px
        
        # Logo em branco
        pdf.setFillColorRGB(1, 1, 1)  # Branco puro
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height-35, "CÂMBIO BANK")  # 🔥 NOME CORRETO
        
        # Subtítulo
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, height-55, "Wire Transfer Receipt")
        
        # Informações de contato
        pdf.setFillColorRGB(0.8, 0.8, 0.8)  # Cinza claro
        pdf.setFont("Helvetica", 7)
        
        
        # ID da transferência
        pdf.setFillColorRGB(0.9, 0.9, 0.1)  # Amarelo discreto
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(width-50, height-35, f"ID: {transferencia_id}")
        
        # Data
        pdf.setFillColorRGB(0.8, 0.8, 0.8)
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(width-50, height-50, datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        # Linha divisória fina
        pdf.setStrokeColorRGB(0.4, 0.4, 0.4)
        pdf.setLineWidth(0.5)
        pdf.line(30, height-105, width-30, height-105)

    def _adicionar_dados_transferencia(self, pdf, width, height, dados):
        """Seção de dados da transferência em inglês"""
        y_pos = height - 120  # 🔥 AJUSTADO PARA CABEÇALHO MAIOR
        
        # Status em inglês
        status = dados['status'].upper()
        status_colors = {
            "COMPLETED": (0.15, 0.55, 0.15),   # Verde escuro
            "PENDING": (0.75, 0.55, 0.1),      # Âmbar escuro  
            "PROCESSING": (0.2, 0.4, 0.7),     # Azul escuro
            "REJECTED": (0.7, 0.2, 0.2)        # Vermelho escuro
        }
        
        cor = status_colors.get(status, (0.4, 0.4, 0.4))
        pdf.setFillColorRGB(*cor)
        box_width = 100
        box_height = 22
        box_x = 40
        box_y = y_pos - 18
        pdf.roundRect(box_x, box_y, box_width, box_height, 3, fill=1)
        
        # Texto do status em inglês
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 9)
        
        status_display = {
            "COMPLETED": "COMPLETED",
            "PENDING": "PENDING", 
            "PROCESSING": "PROCESSING",
            "REJECTED": "REJECTED"
        }.get(status, status)
        
        text_width = pdf.stringWidth(status_display, "Helvetica-Bold", 9)
        text_x = box_x + (box_width - text_width) / 2
        text_y = box_y + (box_height - 9) / 2 + 2
        pdf.drawString(text_x, text_y, status_display)
        y_pos -= 35
        
        # Valor
        pdf.setFillColorRGB(0.97, 0.97, 0.97)
        pdf.roundRect(30, y_pos-32, width-60, 35, 4, fill=1)
        
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(50, y_pos-10, "TRANSFER AMOUNT")  # 🔥 EM INGLÊS
        
        pdf.setFillColorRGB(0.08, 0.18, 0.32)
        pdf.setFont("Helvetica-Bold", 14)
        valor_text = f"{dados['valor']:,.2f} {dados['moeda']}"
        pdf.drawCentredString(width/2, y_pos-25, valor_text)
        y_pos -= 50
        
        # Informações gerais em inglês
        col1_x, col2_x = 50, width/2 + 20
        
        pdf.setFillColorRGB(0.4, 0.4, 0.4)
        pdf.setFont("Helvetica", 7)
        
        # Coluna 1
        pdf.drawString(col1_x, y_pos, "Request Date:")  # 🔥 EM INGLÊS
        pdf.setFont("Helvetica-Bold", 7)
        # 🔥 CORREÇÃO: Usar created_at formatado corretamente
        data_bruta = dados.get('created_at') or dados.get('data_solicitacao') or dados.get('data') or 'N/A'
        if data_bruta != 'N/A':
            # Formatar: "2025-11-28T18:28:59.123456" → "2025-11-28 18:28:59"
            data_texto = str(data_bruta).replace('T', ' ').split('.')[0]
        else:
            data_texto = 'N/A'
        pdf.drawString(col1_x, y_pos-10, data_texto)
        
        pdf.setFont("Helvetica", 7)
        pdf.drawString(col1_x, y_pos-22, "Type:")  # 🔥 EM INGLÊS
        pdf.setFont("Helvetica-Bold", 7) 
        # 🔥 CORREÇÃO MÍNIMA: Incluir 'transferencia_internacional' como International
        tipo = dados.get('tipo', '')
        tipo_text = 'International' if tipo in ['internacional', 'transferencia_internacional'] else 'Internal'
        pdf.drawString(col1_x, y_pos-32, tipo_text)
        
        # Coluna 2  
        pdf.setFont("Helvetica", 7)
        pdf.drawString(col2_x, y_pos, "Purpose:")  # 🔥 EM INGLÊS
        pdf.setFont("Helvetica-Bold", 7)
        finalidade = dados.get('finalidade', 'Not informed')  # 🔥 EM INGLÊS
        if len(finalidade) > 28:
            finalidade1 = finalidade[:28]
            finalidade2 = finalidade[28:56] if len(finalidade) > 56 else finalidade[28:]
            pdf.drawString(col2_x, y_pos-10, finalidade1)
            if finalidade2:
                pdf.drawString(col2_x, y_pos-22, finalidade2)
            y_pos -= 12
        else:
            pdf.drawString(col2_x, y_pos-10, finalidade)
        
        return y_pos - 40

    def _adicionar_secao_titulo(self, pdf, width, y_pos, titulo):
        """Título de seção em inglês"""
        # Desenha o box primeiro
        pdf.setFillColorRGB(0.98, 0.98, 0.98)
        box_height = 120
        pdf.roundRect(40, y_pos - box_height, width-80, box_height, 3, fill=1)
        
        # Título em inglês
        pdf.setFillColorRGB(0.08, 0.18, 0.32)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y_pos - 20, titulo)
        
        # Linha fina
        text_width = pdf.stringWidth(titulo, "Helvetica-Bold", 10)
        pdf.setStrokeColorRGB(0.08, 0.18, 0.32)
        pdf.setLineWidth(0.8)
        pdf.line(50, y_pos - 23, 50 + text_width, y_pos - 23)
        
        return y_pos - 35

    def _adicionar_dados_beneficiario(self, pdf, width, height, y_pos, dados):
        """Dados do beneficiário em inglês"""
        # Título em inglês
        y_pos = self._adicionar_secao_titulo(pdf, width, y_pos, "BENEFICIARY DETAILS")  # 🔥 EM INGLÊS
        
        pdf.setFillColorRGB(0.2, 0.2, 0.2)
        col1_x, col2_x = 60, width/2 + 10
        
        # 🔥 CORREÇÃO MÍNIMA: Incluir 'transferencia_internacional' como internacional
        if dados.get('tipo') in ['internacional', 'transferencia_internacional']:
            # Nome em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_pos - 12, "Name:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            beneficiario = dados.get('beneficiario', 'N/A')
            if len(beneficiario) > 35:
                pdf.drawString(col1_x, y_pos - 22, beneficiario[:35])
                pdf.drawString(col1_x, y_pos - 32, beneficiario[35:70] if len(beneficiario) > 70 else beneficiario[35:])
                y_pos_adjust = 20
            else:
                pdf.drawString(col1_x, y_pos - 22, beneficiario)
                y_pos_adjust = 10
            
            # Endereço em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_pos - 34 - y_pos_adjust, "Address:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            endereco = dados.get('endereco_beneficiario', 'N/A')
            if len(endereco) > 35:
                pdf.drawString(col1_x, y_pos - 44 - y_pos_adjust, endereco[:35])
                pdf.drawString(col1_x, y_pos - 54 - y_pos_adjust, endereco[35:70] if len(endereco) > 70 else endereco[35:])
                y_pos_adjust += 20
            else:
                pdf.drawString(col1_x, y_pos - 44 - y_pos_adjust, endereco)
                y_pos_adjust += 10
            
            # Cidade e País em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_pos - 12, "City:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(col2_x, y_pos - 22, dados.get('cidade', 'N/A'))
            
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_pos - 34, "Country:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(col2_x, y_pos - 44, dados.get('pais', 'N/A'))
            
            return y_pos - 70 - y_pos_adjust
            
        else:
            # Para transferências internas em inglês
            sistema = App.get_running_app().sistema
            conta_destino = dados.get('conta_destinatario', 'N/A')
            
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_pos - 12, "Recipient:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            
            if conta_destino in sistema.contas:
                nome_destino = sistema.contas[conta_destino].get('cliente_nome', 'N/A')
                pdf.drawString(col1_x, y_pos - 22, nome_destino)
            else:
                pdf.drawString(col1_x, y_pos - 22, "Client not found")  # 🔥 EM INGLÊS
            
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_pos - 34, "Destination Account:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(col1_x, y_pos - 44, str(conta_destino or 'N/A'))
            
            return y_pos - 60

    def _adicionar_dados_bancarios(self, pdf, width, height, y_pos, dados):
        """Informações bancárias em inglês"""
        # 🔥 CORREÇÃO MÍNIMA: Incluir 'transferencia_internacional' como internacional
        if dados.get('tipo') in ['internacional', 'transferencia_internacional']:
            # Título em inglês
            y_pos = self._adicionar_secao_titulo(pdf, width, y_pos, "BANKING INFORMATION")  # 🔥 EM INGLÊS
            
            pdf.setFillColorRGB(0.2, 0.2, 0.2)
            col1_x, col2_x = 60, width/2 + 10
            
            # Banco em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_pos - 12, "Beneficiary Bank:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            banco = dados.get('nome_banco', 'N/A')
            if len(banco) > 35:
                pdf.drawString(col1_x, y_pos - 22, banco[:35])
                pdf.drawString(col1_x, y_pos - 32, banco[35:70] if len(banco) > 70 else banco[35:])
                y_pos_adjust = 20
            else:
                pdf.drawString(col1_x, y_pos - 22, banco)
                y_pos_adjust = 10
            
            # Endereço do Banco em inglês
            if dados.get('endereco_banco'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col1_x, y_pos - 34 - y_pos_adjust, "Bank Address:")  # 🔥 EM INGLÊS
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                endereco_banco = dados['endereco_banco']
                if len(endereco_banco) > 35:
                    pdf.drawString(col1_x, y_pos - 44 - y_pos_adjust, endereco_banco[:35])
                    pdf.drawString(col1_x, y_pos - 54 - y_pos_adjust, endereco_banco[35:70] if len(endereco_banco) > 70 else endereco_banco[35:])
                    y_pos_adjust += 20
                else:
                    pdf.drawString(col1_x, y_pos - 44 - y_pos_adjust, endereco_banco)
                    y_pos_adjust += 10
            
            # SWIFT/BIC em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_pos - 12, "SWIFT/BIC Code:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(col2_x, y_pos - 22, dados.get('codigo_swift', 'N/A'))
            
            # IBAN/Account em inglês
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_pos - 34, "IBAN/Account:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            iban = dados.get('iban_account', 'N/A')
            if len(iban) > 25:
                pdf.drawString(col2_x, y_pos - 44, iban[:25])
                pdf.drawString(col2_x, y_pos - 54, iban[25:50] if len(iban) > 50 else iban[25:])
                y_pos_adjust += 10
            else:
                pdf.drawString(col2_x, y_pos - 44, iban)
            
            # ABA/Routing em inglês
            if dados.get('aba'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col2_x, y_pos - 59, "ABA/Routing Code:")  # 🔥 EM INGLÊS
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(col2_x, y_pos - 69, dados['aba'])
                y_pos_adjust += 15
                
            return y_pos - 60 - y_pos_adjust
            
        return y_pos

    def _adicionar_dados_swift_pagamento(self, pdf, width, height, y_pos, dados_swift):
        """Dados SWIFT em inglês"""
        if dados_swift:
            y_pos = y_pos - 20
            
            # Desenha o box
            pdf.setFillColorRGB(0.98, 0.98, 0.98)
            box_height = 160
            pdf.roundRect(40, y_pos - box_height, width-80, box_height, 3, fill=1)
            
            # Título em inglês
            pdf.setFillColorRGB(0.08, 0.18, 0.32)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(50, y_pos - 20, "SWIFT PAYMENT DETAILS")  # 🔥 EM INGLÊS
            
            # Linha fina
            text_width = pdf.stringWidth("SWIFT PAYMENT DETAILS", "Helvetica-Bold", 10)
            pdf.setStrokeColorRGB(0.08, 0.18, 0.32)
            pdf.setLineWidth(0.8)
            pdf.line(50, y_pos - 23, 50 + text_width, y_pos - 23)
            
            # Conteúdo (os campos SWIFT permanecem os mesmos)
            y_pos_content = y_pos - 35
            pdf.setFillColorRGB(0.2, 0.2, 0.2)
            x_pos = 50
            valor_x_pos = 90
            
            # Linha 1: UETR#
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 12, "UETR#:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 12, dados_swift.get('linha1_uetr', 'N/A'))
            
            # Linha 2: :20:
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 24, ":20:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 24, dados_swift.get('linha2_20', 'N/A'))
            
            # Linha 3: :32A:
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 36, ":32A:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 36, dados_swift.get('linha3_32a', 'N/A'))
            
            # Linha 4: :50K:
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 48, ":50K:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 48, dados_swift.get('linha4_50k', 'N/A'))
            
            # Linha 5: :57A:
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 60, ":57A:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 60, dados_swift.get('linha5_57a', 'N/A'))
            
            # Linha 6: :59:
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 72, ":59:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(valor_x_pos, y_pos_content - 72, dados_swift.get('linha6_59', 'N/A'))
            
            # Linha 7: Benef.
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(x_pos, y_pos_content - 84, "Benef.:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            beneficiario = dados_swift.get('linha7_beneficiario', 'N/A')
            
            if len(beneficiario) > 60:
                pdf.drawString(valor_x_pos, y_pos_content - 84, beneficiario[:60])
                pdf.drawString(valor_x_pos, y_pos_content - 96, beneficiario[60:120] if len(beneficiario) > 120 else beneficiario[60:])
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(x_pos, y_pos_content - 108, ":70:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(valor_x_pos, y_pos_content - 108, dados_swift.get('linha8_70', 'N/A'))
                
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(x_pos, y_pos_content - 120, ":71A:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(valor_x_pos, y_pos_content - 120, dados_swift.get('linha9_71a', 'N/A'))
                
                return y_pos - 145
            else:
                pdf.drawString(valor_x_pos, y_pos_content - 84, beneficiario)
                
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(x_pos, y_pos_content - 96, ":70:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(valor_x_pos, y_pos_content - 96, dados_swift.get('linha8_70', 'N/A'))
                
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(x_pos, y_pos_content - 108, ":71A:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(valor_x_pos, y_pos_content - 108, dados_swift.get('linha9_71a', 'N/A'))
                
                return y_pos - 130
        
        return y_pos

    def _adicionar_rodape(self, pdf, width, height, dados):
        """Rodapé em inglês"""
        # Linha divisória fina
        pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
        pdf.setLineWidth(0.5)
        pdf.line(30, 100, width-30, 100)
        
        # Status final em inglês
        pdf.setFillColorRGB(0.97, 0.97, 0.97)
        pdf.roundRect(30, 65, width-60, 25, 2, fill=1)
        
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(50, 78, "STATUS:")  # 🔥 EM INGLÊS
        
        status = dados['status'].upper()
        status_color = {
            "COMPLETED": (0.15, 0.55, 0.15),
            "PENDING": (0.75, 0.55, 0.1),
            "PROCESSING": (0.2, 0.4, 0.7),
            "REJECTED": (0.7, 0.2, 0.2)
        }.get(status, (0.4, 0.4, 0.4))
        
        pdf.setFillColorRGB(*status_color)
        status_display = {
            "COMPLETED": "COMPLETED",  # 🔥 EM INGLÊS
            "PENDING": "PENDING",      # 🔥 EM INGLÊS
            "PROCESSING": "PROCESSING", # 🔥 EM INGLÊS
            "REJECTED": "REJECTED"     # 🔥 EM INGLÊS
        }.get(status, status)
        
        pdf.drawString(100, 78, status_display)
        
        # Informações institucionais em inglês
        pdf.setFillColorRGB(0.5, 0.5, 0.5)
        pdf.setFont("Helvetica", 7)
        pdf.drawString(50, 55, "Câmbio Bank - International Transfers")  # 🔥 NOME CORRETO
        pdf.drawString(50, 45, "Automatically generated document")  # 🔥 EM INGLÊS
        
        # Data em inglês
        pdf.drawRightString(width-50, 55, f"Issued: {datetime.now().strftime('%d/%m/%Y %H:%M')}")  # 🔥 EM INGLÊS
        pdf.drawRightString(width-50, 45, "Page 1 of 1")  # 🔥 EM INGLÊS

    def _formatar_endereco(self, dados_cliente):

        """Formata endereço completo"""
        partes = []
        if dados_cliente.get('endereco'):
            partes.append(dados_cliente['endereco'])
        if dados_cliente.get('cidade'):
            partes.append(dados_cliente['cidade'])
        if dados_cliente.get('estado'):
            partes.append(dados_cliente['estado'])
        if dados_cliente.get('cep'):
            partes.append(f"CEP: {dados_cliente['cep']}")
        if dados_cliente.get('pais'):
            partes.append(dados_cliente['pais'])
        
        return ', '.join(partes) if partes else ''



    def gerar_extrato(self, transacoes, dados_conta, dados_resumo):
        """Gera um PDF com o extrato da conta - VERSÃO COM CABEÇALHO MELHORADO"""
        try:
            from datetime import datetime
            import os
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate
            
            # Cria o nome do arquivo
            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"bank_statement_{dados_conta['numero']}_{data_atual}.pdf"  # 🔥 NOME MAIS PROFISSIONAL
            
            # Obtém o caminho da pasta Downloads
            caminho_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            caminho_completo = os.path.join(caminho_downloads, nome_arquivo)
            
            print(f"🔍 PDFGenerator: Pasta Downloads = {caminho_downloads}")
            print(f"🔍 PDFGenerator: Caminho completo = {caminho_completo}")
            
            # Ordenar transações cronologicamente
            transacoes_ordenadas = sorted(
                transacoes, 
                key=lambda x: x.get('data', ''),
                reverse=False
            )
            
            # 🔥 CORREÇÃO: MARGEM SUPERIOR MAIOR PARA CABEÇALHO EXPANDIDO
            doc = SimpleDocTemplate(
                caminho_completo,
                pagesize=letter,
                topMargin=50,    # 🔥 AUMENTADO DE 40 PARA 50
                bottomMargin=50,
                leftMargin=30,
                rightMargin=30
            )
            
            # Lista de elementos do PDF (conteúdo principal)
            story = []
            
            # Adiciona cabeçalho MELHORADO
            story.extend(self._adicionar_cabecalho_extrato(dados_conta))
            
            # Adiciona resumo
            story.extend(self._adicionar_resumo_extrato_elementos(dados_resumo))
            
            # Adiciona transações
            story.extend(self._adicionar_transacoes_extrato(transacoes_ordenadas))
            
            # 🔥 FUNÇÃO PARA CRIAR RODAPÉ EM TODAS AS PÁGINAS
            def add_footer(canvas, doc):
                canvas.saveState()
                
                # Configurar fonte e cor do rodapé
                canvas.setFont('Helvetica', 7)
                canvas.setFillColor(colors.gray)
                
                # Texto do rodapé
                footer_text = f"Bank Statement generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')} | Câmbio Bank - Banking System"
                
                # Posicionar rodapé no final da página
                page_width = letter[0]
                page_height = letter[1]
                
                # Centralizar horizontalmente, 15 pontos da borda inferior
                text_width = canvas.stringWidth(footer_text, 'Helvetica', 7)
                x_position = (page_width - text_width) / 2
                y_position = 20
                
                canvas.drawString(x_position, y_position, footer_text)
                
                # Número da página
                page_num_text = f"Page {doc.page}"
                page_num_width = canvas.stringWidth(page_num_text, 'Helvetica', 7)
                page_num_x = page_width - page_num_width - 30
                canvas.drawString(page_num_x, y_position, page_num_text)
                
                canvas.restoreState()
            
            # Gera o PDF com rodapé em todas as páginas
            doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
            
            print(f"✅ PDF gerado com sucesso: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar extrato PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
    def _adicionar_cabecalho_extrato(self, dados_conta):
        """Adiciona cabeçalho do extrato - VERSÃO MELHORADA E PROFISSIONAL"""
        try:
            elementos = []
            
            # 🔥 CABEÇALHO PRINCIPAL COM DESIGN MELHORADO
            estilo_titulo_principal = ParagraphStyle(
                'TituloPrincipal',
                fontName='Helvetica-Bold',
                fontSize=18,  # 🔥 AUMENTADO
                alignment=TA_CENTER,
                spaceAfter=15,
                textColor=colors.HexColor("#1E3A8A"),
                spaceBefore=10
            )
            titulo_principal = Paragraph("CÂMBIO BANK - BANK STATEMENT", estilo_titulo_principal)  # 🔥 NOME + TÍTULO
            elementos.append(titulo_principal)
            
            # 🔥 LINHA DIVISÓRIA FINA NO TOPO
            elementos.append(HRFlowable(
                color=colors.HexColor("#1E3A8A"),
                thickness=1,
                spaceAfter=10,
                spaceBefore=5
            ))
            
            # 🔥 INFORMAÇÕES DA CONTA EM LAYOUT DE DUAS COLUNAS
            estilo_info_titulo = ParagraphStyle(
                'InfoTitulo',
                fontName='Helvetica-Bold',
                fontSize=9,
                textColor=colors.HexColor("#1E3A8A"),
                leftIndent=0,
                spaceAfter=2
            )
            
            estilo_info_valor = ParagraphStyle(
                'InfoValor',
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.black,
                leftIndent=0,
                spaceAfter=8
            )
            
            # Criar tabela para informações em duas colunas
            info_data = [
                [
                    Paragraph("<b>Account Number:</b>", estilo_info_titulo),
                    Paragraph(dados_conta['numero'], estilo_info_valor),
                    Paragraph("<b>Currency:</b>", estilo_info_titulo),
                    Paragraph(dados_conta['moeda'], estilo_info_valor)
                ],
                [
                    Paragraph("<b>Account Holder:</b>", estilo_info_titulo),
                    Paragraph(dados_conta['titular'], estilo_info_valor),
                    Paragraph("<b>Current Balance:</b>", estilo_info_titulo),
                    Paragraph(f"{dados_conta['saldo']:,.2f}", estilo_info_valor)
                ],
                [
                    Paragraph("<b>Statement Date:</b>", estilo_info_titulo),
                    Paragraph(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), estilo_info_valor),
                    Paragraph("<b>Document Type:</b>", estilo_info_titulo),
                    Paragraph("Bank Statement", estilo_info_valor)
                ]
            ]
            
            info_table = Table(
                info_data,
                colWidths=[80, 120, 80, 120],  # Larguras das colunas
                style=[
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]
            )
            
            elementos.append(info_table)
            elementos.append(Spacer(1, 15))
            
            # 🔥 INFORMAÇÕES DE CONTATO DO BANCO
            estilo_contato = ParagraphStyle(
                'Contato',
                fontName='Helvetica',
                fontSize=7,
                alignment=TA_CENTER,
                textColor=colors.gray,
                spaceAfter=5
            )
            
            contato_texto = """
            <b>Câmbio Bank</b> • www.cambiobank.com • +55 (11) 4004-5000 • Av. Paulista 364, suite 1254, São Paulo - SP
            """
            
            contato = Paragraph(contato_texto, estilo_contato)
            elementos.append(contato)
            
            # 🔥 LINHA DIVISÓRIA PRINCIPAL
            elementos.append(Spacer(1, 10))
            elementos.append(HRFlowable(
                color=colors.HexColor("#1E3A8A"),
                thickness=2,
                spaceAfter=20,
                spaceBefore=5
            ))
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar cabeçalho: {str(e)}")
            return []

    def _adicionar_resumo_extrato_elementos(self, dados_resumo):
        """Adiciona resumo do extrato - VERSÃO EM INGLÊS"""
        try:
            elementos = []
            
            # Título do resumo em inglês
            estilo_titulo = ParagraphStyle(
                'ResumoTitulo',
                fontName='Helvetica-Bold',
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor("#1E3A8A")
            )
            titulo = Paragraph("STATEMENT SUMMARY", estilo_titulo)  # 🔥 EM INGLÊS
            elementos.append(titulo)
            
            estilo_dados = ParagraphStyle(
                'ResumoDados',
                fontName='Helvetica',
                fontSize=9,
                spaceAfter=4,
                leftIndent=8
            )
            
            # 🔥 TEXTO DO RESUMO COMPLETAMENTE EM INGLÊS
            resumo_texto = f"""
            <b>Ending Balance:</b> {dados_resumo.get('saldo_final', 0):,.2f}<br/>
            <b>Total Deposits:</b> {dados_resumo.get('entradas', 0):,.2f}<br/>
            <b>Total Withdrawals:</b> {dados_resumo.get('saidas', 0):,.2f}<br/>
            <b>Total Transactions:</b> {dados_resumo.get('total_transacoes', 0)}<br/>
            <b>Period:</b> {dados_resumo.get('periodo', 'Not specified')}
            """
            
            resumo = Paragraph(resumo_texto, estilo_dados)
            elementos.append(resumo)
            
            elementos.append(Spacer(1, 15))
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar resumo: {str(e)}")
            return []

    def _adicionar_transacoes_extrato(self, transacoes):
        """Adiciona transações ao extrato - VERSÃO COM VALOR TOTAL VERMELHO APENAS SE NEGATIVO"""
        try:
            elementos = []
            
            # Título das transações em inglês - 🔥 ALINHADO À ESQUERDA
            estilo_titulo = ParagraphStyle(
                'TransacoesTitulo',
                fontName='Helvetica-Bold',
                fontSize=11,
                spaceAfter=12,
                textColor=colors.HexColor("#1E3A8A"),
                leftIndent=25,
                alignment=TA_LEFT
            )
            titulo = Paragraph("TRANSACTIONS", estilo_titulo)
            elementos.append(titulo)
            
            if not transacoes:
                estilo_vazio = ParagraphStyle(
                    'Vazio',
                    fontName='Helvetica',
                    fontSize=9,
                    alignment=TA_CENTER,
                    textColor=colors.gray
                )
                vazio = Paragraph("No transactions in this period", estilo_vazio)
                elementos.append(vazio)
                return elementos
            
            # 🔥 CABEÇALHO DAS COLUNAS EM INGLÊS
            cabecalho_dados = [
                'Date',
                'Description', 
                'Credit',
                'Debit',
                'Balance'
            ]
            
            # Dados da tabela
            dados_tabela = [cabecalho_dados]
            
            for transacao in transacoes:
                # Formatar data para DD/MM/AAAA
                data_original = transacao.get('data', '')
                data_formatada = self._formatar_data_para_pdf(data_original)
                
                # Formatar descrição - TRADUZIR TERMOS COMUNS
                descricao_original = transacao.get('descricao', '')
                descricao = self._traduzir_descricao_para_ingles(descricao_original)
                
                # Valores formatados
                credito = transacao.get('credito', 0)
                debito = transacao.get('debito', 0)
                saldo = transacao.get('saldo_apos', 0)
                
                # Apenas os valores numéricos
                credito_str = f"{credito:,.2f}" if credito > 0 else ""
                debito_str = f"{debito:,.2f}" if debito > 0 else ""
                saldo_str = f"{saldo:,.2f}"
                
                linha = [
                    data_formatada,
                    descricao,
                    credito_str,
                    debito_str,
                    saldo_str
                ]
                
                dados_tabela.append(linha)
            
            # 🔥 LINHA DE TOTAL
            if transacoes:
                ultimo_saldo = transacoes[-1].get('saldo_apos', 0)
                linha_total = [
                    "",           # Data vazia
                    "TOTAL",      # 🔥 "TOTAL" na coluna Description
                    "",           # Credit vazio  
                    "",           # Debit vazio
                    f"{ultimo_saldo:,.2f}"  # Saldo final
                ]
                dados_tabela.append(linha_total)
            
            # Larguras otimizadas
            col_widths = [35, 300, 50, 50, 55]
            
            # Criar tabela
            tabela = Table(
                dados_tabela, 
                colWidths=col_widths,
                repeatRows=1
            )
            
            # Estilo da tabela
            estilo_tabela = TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Linhas de dados (até penúltima linha)
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 6.5),
                ('ALIGN', (0, 1), (0, -2), 'LEFT'),
                ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -2), 'RIGHT'),
                
                # 🔥 ESTILO ESPECIAL PARA A LINHA DE TOTAL (última linha)
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E5E7EB")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 7),
                ('TEXTCOLOR', (0, -1), (3, -1), colors.HexColor("#1E3A8A")),  # 🔥 "TOTAL" em azul
                ('ALIGN', (1, -1), (1, -1), 'RIGHT'),  # 🔥 "TOTAL" alinhado à DIREITA
                ('ALIGN', (4, -1), (4, -1), 'RIGHT'),  # Valor alinhado à direita
                
                # 🔥 BORDAS EM NEGRITO COMPLETAS PARA A ÚLTIMA LINHA
                ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
                ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
                ('LINELEFT', (0, -1), (0, -1), 1.5, colors.HexColor("#1E3A8A")),    # 🔥 EXTREMIDADE ESQUERDA
                ('LINERIGHT', (-1, -1), (-1, -1), 1.5, colors.HexColor("#1E3A8A")), # 🔥 EXTREMIDADE DIREITA
                
                # Bordas normais para o resto da tabela
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
                
                # Alternar cores das linhas (exceto última)
                ('ROWBACKGROUNDS', (0, 1), (-2, -2), [colors.white, colors.HexColor("#F8FAFC")]),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                
                # Quebra de texto automática
                ('WORDWRAP', (1, 1), (1, -1), True),
            ])
            
            # 🔥 COR DA FONTA DO TOTAL CONDICIONAL (VERMELHO APENAS SE NEGATIVO)
            if transacoes:
                ultimo_saldo = transacoes[-1].get('saldo_apos', 0)
                if ultimo_saldo < 0:
                    estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.red)  # 🔥 VERMELHO SE NEGATIVO
                else:
                    estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.HexColor("#1E3A8A"))  # 🔥 AZUL SE POSITIVO
            
            tabela.setStyle(estilo_tabela)
            elementos.append(tabela)
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar transações: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
    def _traduzir_descricao_para_ingles(self, descricao):
        """Traduz termos comuns das descrições para inglês"""
        try:
            if not descricao:
                return ""
            
            # 🔥 DICIONÁRIO DE TRADUÇÕES
            traducoes = {
                # Termos gerais
                'SALDO INICIAL': 'OPENING BALANCE',
                'SALDO INICIAL DO PERÍODO': 'PERIOD OPENING BALANCE',
                'CRÉDITO ADMINISTRATIVO': 'ADMINISTRATIVE CREDIT',
                'DÉBITO ADMINISTRATIVO': 'ADMINISTRATIVE DEBIT',
                'ACCOUNT MONTHLY FEE': 'ACCOUNT MAINTENANCE FEE',
                
                # Transferências
                'TRANSFERÊNCIA': 'TRANSFER',
                'TRANSFERÊNCIA INTERNA': 'INTERNAL TRANSFER',
                'TRANSFERÊNCIA INTERNACIONAL': 'INTERNATIONAL TRANSFER',
                'SOLICITADA': 'REQUESTED',
                'EM PROCESSAMENTO': 'PROCESSING',
                'CONCLUÍDA': 'COMPLETED',
                'RECUSADA': 'REJECTED',
                'RECEBIDA': 'RECEIVED',
                
                # Câmbio - 🔥 CORREÇÃO: "FX OPERATION" EM VEZ DE "FOREIGN EXCHANGE OPERATION"
                'OPERAÇÃO DE CÂMBIO': 'FX OPERATION',
                'COMPRA': 'PURCHASE',
                'VENDA': 'SALE',
                'TAXA DE CÂMBIO': 'EXCHANGE RATE',
                
                # Estornos
                'ESTORNO': 'REVERSAL',
                'ESTORNO TRANSFERÊNCIA': 'TRANSFER REVERSAL',
                'ESTORNO TRANSF. INTERNACIONAL': 'INTERNATIONAL TRANSFER REVERSAL',
                
                # Beneficiários comuns
                'SHELL': 'SHELL',
                'TIM S.A.': 'TIM S.A.',
                'JINAN BCAMCN MACHINERY CO., LTD.': 'JINAN BCAMCN MACHINERY CO., LTD.',
            }
            
            # Aplicar traduções (case insensitive)
            descricao_traduzida = descricao.upper()
            for pt, en in traducoes.items():
                descricao_traduzida = descricao_traduzida.replace(pt.upper(), en)
            
            # Limitar tamanho se necessário
            descricao_limpa = ' '.join(descricao_traduzida.split())
            if len(descricao_limpa) > 80:
                return descricao_limpa[:77] + "..."
            
            return descricao_limpa
            
        except:
            return descricao
        
    def _adicionar_resumo_extrato_elementos(self, dados_resumo):
        """Adiciona resumo do extrato - VERSÃO COM MARGEM IGUAL À TABELA"""
        try:
            elementos = []
            
            # Título do resumo em inglês - 🔥 COM MARGEM ESPECÍFICA
            estilo_titulo = ParagraphStyle(
                'ResumoTitulo',
                fontName='Helvetica-Bold',
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor("#1E3A8A"),
                leftIndent=25,  # 🔥 MESMA MARGEM DA TABELA (LEFTPADDING=2)
                alignment=TA_LEFT
            )
            titulo = Paragraph("STATEMENT SUMMARY", estilo_titulo)
            elementos.append(titulo)
            
            estilo_dados = ParagraphStyle(
                'ResumoDados',
                fontName='Helvetica',
                fontSize=9,
                spaceAfter=4,
                leftIndent=26,  # 🔥 MESMA MARGEM DA TABELA (LEFTPADDING=2)
                alignment=TA_LEFT
            )
            
            # Traduzir o período para inglês
            periodo_ingles = self._traduzir_periodo_para_ingles(dados_resumo.get('periodo', 'Not specified'))
            
            # Texto do resumo completamente em inglês
            resumo_texto = f"""
            <b>Ending Balance:</b> {dados_resumo.get('saldo_final', 0):,.2f}<br/>
            <b>Total Deposits:</b> {dados_resumo.get('entradas', 0):,.2f}<br/>
            <b>Total Withdrawals:</b> {dados_resumo.get('saidas', 0):,.2f}<br/>
            <b>Total Transactions:</b> {dados_resumo.get('total_transacoes', 0)}<br/>
            <b>Period:</b> {periodo_ingles}
            """
            
            resumo = Paragraph(resumo_texto, estilo_dados)
            elementos.append(resumo)
            
            elementos.append(Spacer(1, 15))
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar resumo: {str(e)}")
            return []

    def _traduzir_periodo_para_ingles(self, periodo_pt):
        """Traduz o período do extrato para inglês"""
        try:
            if not periodo_pt:
                return "Not specified"
            
            # 🔥 DICIONÁRIO DE TRADUÇÕES DE PERÍODOS
            traducoes_periodo = {
                'Todo período': 'All Period',
                'Todo o período': 'All Period',
                'Últimos 30 dias': 'Last 30 Days',
                'Últimos 7 dias': 'Last 7 Days', 
                'Últimos 90 dias': 'Last 90 Days',
                'Este mês': 'This Month',
                'Mês anterior': 'Previous Month',
                'Este ano': 'This Year',
                'Ano anterior': 'Previous Year',
                'Personalizado': 'Custom Period',
                'Não especificado': 'Not specified'
            }
            
            # Verificar se é um período personalizado (com datas)
            if 'a' in periodo_pt and '/' in periodo_pt:
                try:
                    # Formato: "DD/MM/AAAA a DD/MM/AAAA"
                    partes = periodo_pt.split(' a ')
                    if len(partes) == 2:
                        data_inicio = partes[0].strip()
                        data_fim = partes[1].strip()
                        return f"{data_inicio} to {data_fim}"
                except:
                    pass
            
            # Verificar se é um período conhecido
            for pt, en in traducoes_periodo.items():
                if pt.lower() in periodo_pt.lower():
                    return en
            
            # Se não encontrar tradução, retorna o original
            return periodo_pt
            
        except:
            return periodo_pt

    def _formatar_descricao_para_pdf(self, descricao):
        """Formata a descrição para caber melhor no PDF (agora usando a versão traduzida)"""
        try:
            if not descricao:
                return ""
            
            # Usar a descrição já traduzida
            descricao_traduzida = self._traduzir_descricao_para_ingles(descricao)
            
            # Remover espaços extras
            descricao_limpa = ' '.join(descricao_traduzida.split())
            
            # Se for muito longa, truncar e adicionar "..."
            if len(descricao_limpa) > 80:
                return descricao_limpa[:77] + "..."
            
            return descricao_limpa
            
        except:
            return descricao
        
    def _formatar_data_para_pdf(self, data_iso):
        """Formata data para o formato DD/MM/YYYY no PDF (mantido para consistência)"""
        try:
            if not data_iso:
                return ""
            
            # Extrair apenas a parte da data (YYYY-MM-DD)
            data_parte = data_iso.split(' ')[0] if ' ' in data_iso else data_iso
            
            # Converter de YYYY-MM-DD para DD/MM/YYYY (formato internacional)
            partes = data_parte.split('-')
            if len(partes) == 3:
                return f"{partes[2]}/{partes[1]}/{partes[0]}"
            else:
                return data_parte
                
        except:
            return data_iso

    def _adicionar_rodape_extrato(self):
        """Rodapé do extrato - VERSÃO SIMPLIFICADA"""
        try:
            elementos = []
            
            # Linha divisória
            elementos.append(HRFlowable(
                color=colors.HexColor("#CCCCCC"),
                thickness=1,
                spaceBefore=20,
                spaceAfter=10
            ))
            
            # Informações da empresa
            estilo_rodape = ParagraphStyle(
                'Rodape',
                fontName='Helvetica',
                fontSize=8,
                textColor=colors.HexColor("#808080"),
                alignment=TA_CENTER
            )
            
            rodape_texto = f"""
            Cambió Bank - Sistema Bancário Internacional<br/>
            Documento gerado automaticamente - Válido como extrato oficial<br/>
            Página 1 de 1 | Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """
            
            rodape = Paragraph(rodape_texto, estilo_rodape)
            elementos.append(rodape)
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar rodapé: {str(e)}")
            return []