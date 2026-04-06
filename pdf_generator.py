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
        y_pos = height - 120
        
        # 🔥 AJUSTE: Converter "solicitada" para "PENDING"
        status_original = dados['status'].upper()
        status = "PENDING" if status_original == "SOLICITADA" else status_original
        
        status_colors = {
            "COMPLETED": (0.15, 0.55, 0.15),   # Verde escuro
            "PENDING": (1.0, 0.65, 0.0),      # Âmbar escuro (AJUSTADO)  
            "PROCESSING": (0.25, 0.45, 0.85),     # Azul escuro
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
        
        # 🔥 NOVO: Adicionar Completed Date apenas para status completed
        if dados['status'].upper() == 'COMPLETED':
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.4, 0.4, 0.4)
            pdf.drawString(col2_x, y_pos-22, "Completed Date:")  # 🔥 EM INGLÊS
            pdf.setFont("Helvetica-Bold", 7)
            # Usar data de conclusão se disponível, senão usar data atual
            data_conclusao = dados.get('data_conclusao') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if data_conclusao != 'N/A':
                # Formatar: "2025-11-28T18:28:59.123456" → "2025-11-28 18:28:59"
                data_conclusao_texto = str(data_conclusao).replace('T', ' ').split('.')[0]
            else:
                data_conclusao_texto = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pdf.drawString(col2_x, y_pos-32, data_conclusao_texto)
            y_pos -= 22  # 🔥 Ajustar posição vertical para acomodar nova linha
        
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
            
            # 🔥🔥🔥 AJUSTE FINAL: "Country:" alinhado com "Address:" - SUBIR UM POUCO
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_pos - 34 - (y_pos_adjust // 2), "Country:")  # 🔥 AJUSTE: usar metade do ajuste
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(col2_x, y_pos - 44 - (y_pos_adjust // 2), dados.get('pais', 'N/A'))  # 🔥 AJUSTE: usar metade do ajuste
            
            return y_pos - 70 - y_pos_adjust - 10
            
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
        if dados.get('tipo') in ['internacional', 'transferencia_internacional']:
            # Título em inglês
            y_pos = self._adicionar_secao_titulo(pdf, width, y_pos, "BANKING INFORMATION")
            
            pdf.setFillColorRGB(0.2, 0.2, 0.2)
            col1_x, col2_x = 60, width/2 + 10
            
            # 🔥 MESMOS VALORES PARA AMBAS COLUNAS
            linha_normal = 14    # Campos superiores
            linha_meio = 20      # 🔥 NOVO: para Bank Country (direita tinha 16-20)
            linha_final = 22     # Campos inferiores
            
            # COLUNA ESQUERDA ============================================
            y_esquerda = y_pos - 12
            
            # Banco em inglês (superior - igual SWIFT/BIC da direita)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col1_x, y_esquerda, "Beneficiary Bank:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            banco = dados.get('nome_banco', 'N/A')
            if len(banco) > 35:
                pdf.drawString(col1_x, y_esquerda - 10, banco[:35])
                pdf.drawString(col1_x, y_esquerda - 20, banco[35:70] if len(banco) > 70 else banco[35:])
                y_esquerda -= 25  # Igual SWIFT/BIC com 2 linhas
            else:
                pdf.drawString(col1_x, y_esquerda - 10, banco)
                y_esquerda -= linha_normal  # 14px igual SWIFT/BIC
            
            # Endereço do Banco (meio - igual Bank Country da direita)
            if dados.get('endereco_banco'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col1_x, y_esquerda - 12, "Bank Address:")  # 🔥 ERA -8 (igual a Bank Country -12)
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                endereco_banco = dados['endereco_banco']
                if len(endereco_banco) > 35:
                    pdf.drawString(col1_x, y_esquerda - 22, endereco_banco[:35])  # 🔥 ERA -18 (igual a Bank Country -22)
                    pdf.drawString(col1_x, y_esquerda - 32, endereco_banco[35:70] if len(endereco_banco) > 70 else endereco_banco[35:])  # 🔥 ERA -28 (igual -32)
                    y_esquerda -= 32  # 🔥 ERA 25 (igual Bank Country 2 linhas: 32)
                else:
                    pdf.drawString(col1_x, y_esquerda - 22, endereco_banco)  # 🔥 ERA -18 (igual -22)
                    y_esquerda -= linha_meio  # 🔥 NOVO: 20px igual Bank Country (tinha 16-20)
            
            # Cidade do Banco (inferior - igual IBAN/Account da direita)
            if dados.get('cidade_banco'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col1_x, y_esquerda - 16, "Bank City:")  # 🔥 ERA -14 (igual IBAN -16)
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                cidade_banco = dados['cidade_banco']
                if len(cidade_banco) > 35:
                    pdf.drawString(col1_x, y_esquerda - 26, cidade_banco[:35])  # 🔥 ERA -24 (igual IBAN -26)
                    pdf.drawString(col1_x, y_esquerda - 36, cidade_banco[35:70] if len(cidade_banco) > 70 else cidade_banco[35:])  # 🔥 ERA -34 (igual IBAN -36)
                    y_esquerda -= 38  # 🔥 ERA 35 (igual IBAN 2 linhas: 38)
                else:
                    pdf.drawString(col1_x, y_esquerda - 26, cidade_banco)  # 🔥 ERA -24 (igual IBAN -26)
                    y_esquerda -= linha_final  # 🔥 22px igual IBAN
            
            # COLUNA DIREITA =============================================
            # 🔥 NÃO MEXER - JÁ ESTÁ PERFEITA
            y_direita = y_pos - 12
            
            # SWIFT/BIC (superior - compacto)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_direita, "SWIFT/BIC Code:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            swift = dados.get('codigo_swift', 'N/A')
            pdf.drawString(col2_x, y_direita - 10, swift)
            y_direita -= linha_normal
            
            # País do Banco (meio)
            if dados.get('pais_banco'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col2_x, y_direita - 12, "Bank Country:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pais_banco = dados['pais_banco']
                if len(pais_banco) > 25:
                    pdf.drawString(col2_x, y_direita - 22, pais_banco[:25])
                    pdf.drawString(col2_x, y_direita - 32, pais_banco[25:50] if len(pais_banco) > 50 else pais_banco[25:])
                    y_direita -= 32
                else:
                    pdf.drawString(col2_x, y_direita - 22, pais_banco)
                    y_direita -= 20
            
            # IBAN/Account (inferior)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(col2_x, y_direita - 16, "IBAN/Account:")
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            iban = dados.get('iban_account', 'N/A')
            if len(iban) > 25:
                pdf.drawString(col2_x, y_direita - 26, iban[:25])
                pdf.drawString(col2_x, y_direita - 36, iban[25:50] if len(iban) > 50 else iban[25:])
                y_direita -= 38
            else:
                pdf.drawString(col2_x, y_direita - 26, iban)
                y_direita -= linha_final
            
            # ABA/Routing (extra inferior)
            if dados.get('aba'):
                pdf.setFont("Helvetica-Bold", 7)
                pdf.setFillColorRGB(0.5, 0.5, 0.5)
                pdf.drawString(col2_x, y_direita - 16, "ABA/Routing Code:")
                pdf.setFont("Helvetica", 7)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
                pdf.drawString(col2_x, y_direita - 26, dados['aba'])
                y_direita -= linha_final
            
            # Encontra qual coluna terminou mais abaixo
            if y_esquerda < y_direita:
                y_mais_baixa = y_esquerda
            else:
                y_mais_baixa = y_direita
            
            return y_mais_baixa - 12
            
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
        box_height = 25
        box_y = 65
        pdf.roundRect(30, box_y, width-60, box_height, 2, fill=1)
        
        # 🔥 CENTRALIZAR VERTICALMENTE o texto dentro da caixa
        text_y = box_y + (box_height - 9) / 2 + 2
        
        # 🔥 "STATUS:" na cor original (cinza escuro)
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(50, text_y, "STATUS:")
        
        # 🔥 Status específico na cor correspondente
        status_original = dados['status'].upper()
        status = "PENDING" if status_original == "SOLICITADA" else status_original
        status_color = {
            "COMPLETED": (0.15, 0.55, 0.15),
            "PENDING": (1.0, 0.65, 0.0),
            "PROCESSING": (0.25, 0.45, 0.85),
            "REJECTED": (0.7, 0.2, 0.2)
        }.get(status, (0.4, 0.4, 0.4))
        
        pdf.setFillColorRGB(*status_color)
        status_display = {
            "COMPLETED": "COMPLETED",
            "PENDING": "PENDING",
            "PROCESSING": "PROCESSING",
            "REJECTED": "REJECTED"
        }.get(status, status)
        
        # 🔥 Calcular posição do status (depois da palavra "STATUS:")
        status_x = 50 + pdf.stringWidth("STATUS: ", "Helvetica-Bold", 9)
        pdf.drawString(status_x, text_y, status_display)
        
        # Informações institucionais em inglês
        pdf.setFillColorRGB(0.5, 0.5, 0.5)
        pdf.setFont("Helvetica", 7)
        pdf.drawString(50, 55, "Câmbio Bank - International Transfers")
        pdf.drawString(50, 45, "Automatically generated document")
        
        # Data em inglês
        pdf.drawRightString(width-50, 55, f"Issued: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        pdf.drawRightString(width-50, 45, "Page 1 of 1")

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
            from reportlab.lib import colors  # 🔥 CORREÇÃO: IMPORT FALTANDO
            
            # Cria o nome do arquivo
            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"bank_statement_{dados_conta['numero']}_{data_atual}.pdf"
            
            # Obtém o caminho da pasta Downloads
            caminho_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            caminho_completo = os.path.join(caminho_downloads, nome_arquivo)
            
            print(f"🔍 PDFGenerator: Pasta Downloads = {caminho_downloads}")
            print(f"🔍 PDFGenerator: Caminho completo = {caminho_completo}")
            
            # 🔥 CORREÇÃO CRÍTICA: NÃO ORDENAR - MANTER A ORDEM ORIGINAL
            # As transações já vêm na ordem correta (mais antigas primeiro)
            transacoes_ordenadas = transacoes  # 🔥 MUDANÇA AQUI: Não ordenar novamente
            
            # 🔥 DEBUG: Ver ordem no PDFGenerator
            print("🔍 DEBUG ORDEM NO PDFGenerator:")
            for i, t in enumerate(transacoes_ordenadas):
                descricao = t.get('descricao', '')[:50]
                data = t.get('data', '')
                print(f"   PDF Transação {i}: {data} | {descricao}...")
            
            # 🔥 CORREÇÃO: MARGEM SUPERIOR MAIOR PARA CABEÇALHO EXPANDIDO
            doc = SimpleDocTemplate(
                caminho_completo,
                pagesize=letter,
                topMargin=50,
                bottomMargin=50,
                leftMargin=30,
                rightMargin=30
            )
            
            # Lista de elementos do PDF (conteúdo principal)
            story = []
            
            # Adiciona cabeçalho MELHORADO
            story.extend(self._adicionar_cabecalho_extrato(dados_conta, dados_resumo))
            
            
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
        
    def _adicionar_cabecalho_extrato(self, dados_conta, dados_resumo):
        """Adiciona cabeçalho do extrato - VERSÃO COM LINHAS COLADAS"""
        try:
            elementos = []
            
            # 🔥 CABEÇALHO PRINCIPAL COMPACTO
            estilo_titulo_principal = ParagraphStyle(
                'TituloPrincipal',
                fontName='Helvetica-Bold',
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=4,
                textColor=colors.HexColor("#1E3A8A"),
                spaceBefore=5
            )
            titulo_principal = Paragraph("CÂMBIO BANK - BANK STATEMENT", estilo_titulo_principal)
            elementos.append(titulo_principal)
            
            # 🔥 INFORMAÇÕES DO BANCO LOGO ABAIXO DO TÍTULO
            estilo_contato = ParagraphStyle(
                'Contato',
                fontName='Helvetica',
                fontSize=7,
                alignment=TA_CENTER,
                textColor=colors.gray,
                spaceAfter=6,
                spaceBefore=2
            )
            
            contato_texto = "www.cambiobank.com • +55 (11) 4004-5000 • São Paulo - SP"
            contato = Paragraph(contato_texto, estilo_contato)
            elementos.append(contato)
            
            # 🔥 LINHA DIVISÓRIA SUPERIOR - COLADA NO TOPO DA TABELA
            linha_superior = Table(
                [['']],
                colWidths=[490],
                style=[
                    ('LINEABOVE', (0, 0), (0, 0), 1.5, colors.HexColor("#1E3A8A")),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (0, 0), (0, 0), 0),
                    ('BOTTOMPADDING', (0, 0), (0, 0), 0),  # 🔥 ZERO - COLADA
                ]
            )
            elementos.append(linha_superior)
            
            # 🔥 ESTILOS PARA AS INFORMAÇÕES
            estilo_info_titulo = ParagraphStyle(
                'InfoTitulo',
                fontName='Helvetica-Bold',
                fontSize=8,
                textColor=colors.HexColor("#1E3A8A"),
                leftIndent=0,
                spaceAfter=1
            )
            
            estilo_info_valor = ParagraphStyle(
                'InfoValor',
                fontName='Helvetica',
                fontSize=8,
                textColor=colors.black,
                leftIndent=0,
                spaceAfter=4
            )
            
            # 🔥 TABELA COM 4 COLUNAS - MESMA LARGURA DA TABELA DE TRANSAÇÕES (490)
            info_data = [
                [
                    # CABEÇALHO DAS 4 COLUNAS
                    Paragraph("<b>ACCOUNT INFO</b>", estilo_info_titulo),
                    Paragraph("<b>BALANCE</b>", estilo_info_titulo),
                    Paragraph("<b>TRANSACTIONS</b>", estilo_info_titulo),
                    Paragraph("<b>PERIOD</b>", estilo_info_titulo)
                ],
                [
                    # COLUNA 1: INFORMAÇÕES DA CONTA (122.5 de largura)
                    Table([
                        [Paragraph("<b>Number:</b>", estilo_info_titulo), Paragraph(dados_conta['numero'], estilo_info_valor)],
                        [Paragraph("<b>Holder:</b>", estilo_info_titulo), Paragraph(dados_conta['titular'], estilo_info_valor)],
                        [Paragraph("<b>Currency:</b>", estilo_info_titulo), Paragraph(dados_conta['moeda'], estilo_info_valor)]
                    ], colWidths=[50, 70], style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ]),
                    
                    # COLUNA 2: SALDOS (122.5 de largura)
                    Table([
                        [Paragraph("<b>Current:</b>", estilo_info_titulo), Paragraph(f"{dados_conta['saldo']:,.2f}", estilo_info_valor)],
                        [Paragraph("<b>End Bal:</b>", estilo_info_titulo), Paragraph(f"{dados_resumo.get('saldo_final', 0):,.2f}", estilo_info_valor)],
                        [Paragraph("<b>Currency:</b>", estilo_info_titulo), Paragraph(dados_conta['moeda'], estilo_info_valor)]
                    ], colWidths=[50, 70], style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ]),
                    
                    # COLUNA 3: TRANSAÇÕES (122.5 de largura)
                    Table([
                        [Paragraph("<b>Total:</b>", estilo_info_titulo), Paragraph(str(dados_resumo.get('total_transacoes', 0)), estilo_info_valor)],
                        [Paragraph("<b>Deposits:</b>", estilo_info_titulo), Paragraph(f"{dados_resumo.get('entradas', 0):,.2f}", estilo_info_valor)],
                        [Paragraph("<b>Withdrawals:</b>", estilo_info_titulo), Paragraph(f"{dados_resumo.get('saidas', 0):,.2f}", estilo_info_valor)]
                    ], colWidths=[55, 65], style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ]),
                    
                    # COLUNA 4: PERÍODO (122.5 de largura)
                    Table([
                        [Paragraph("<b>Period:</b>", estilo_info_titulo), Paragraph(dados_resumo.get('periodo', 'N/A'), estilo_info_valor)],
                        [Paragraph("<b>Generated:</b>", estilo_info_titulo), Paragraph(datetime.now().strftime('%d/%m/%Y'), estilo_info_valor)],
                        [Paragraph("<b>Time:</b>", estilo_info_titulo), Paragraph(datetime.now().strftime('%H:%M'), estilo_info_valor)]
                    ], colWidths=[55, 65], style=[
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ])
                ]
            ]
            
            # 🔥 LARGURAS EXATAS: 4 colunas de 122.5 = 490
            larguras_colunas = [122.5, 122.5, 122.5, 122.5]
            
            info_table = Table(
                info_data,
                colWidths=larguras_colunas,
                style=[
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # 🔥 ZERO - SEM ESPAÇO INTERNO
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F4FF")),
                    ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor("#1E3A8A")),
                ]
            )
            
            elementos.append(info_table)
            
            # 🔥 LINHA DIVISÓRIA INFERIOR - COLADA NA BASE DA TABELA
            linha_inferior = Table(
                [['']],
                colWidths=[490],
                style=[
                    ('LINEBELOW', (0, 0), (0, 0), 1.5, colors.HexColor("#1E3A8A")),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (0, 0), (0, 0), 0),
                    ('TOPPADDING', (0, 0), (0, 0), 0),  # 🔥 ZERO - COLADA
                ]
            )
            elementos.append(linha_inferior)
            
            # 🔥 ESPAÇO ENTRE CABEÇALHO E TÍTULO "TRANSACTIONS"
            elementos.append(Spacer(1, 15))  # 🔥 ESPAÇO ADICIONADO AQUI
            
            return elementos
            
        except Exception as e:
            print(f"❌ Erro ao adicionar cabeçalho: {str(e)}")
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
                'Debit',
                'Credit',
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

            # 🔥 ADICIONE ESTAS 3 LINHAS AQUI:
            # 1. Credit (coluna 2) - VERMELHO para todas as linhas de dados
            estilo_tabela.add('TEXTCOLOR', (2, 1), (2, -2), colors.red)

            # 2. Debit (coluna 3) - AZUL para todas as linhas de dados  
            estilo_tabela.add('TEXTCOLOR', (3, 1), (3, -2), colors.blue)

            # 3. Balance (coluna 4) - LÓGICA CONDICIONAL (azul para positivo/zero, vermelho para negativo)
            for i in range(1, len(dados_tabela) - 1):  # Pula cabeçalho (0) e última linha (TOTAL)
                try:
                    # Pega o valor do saldo da transação original
                    saldo_valor = transacoes[i-1].get('saldo_apos', 0)
                    if saldo_valor < 0:
                        estilo_tabela.add('TEXTCOLOR', (4, i), (4, i), colors.red)
                    else:
                        estilo_tabela.add('TEXTCOLOR', (4, i), (4, i), colors.blue)
                except:
                    pass

            # 🔥 COR DA FONTA DO TOTAL CONDICIONAL (VERMELHO APENAS SE NEGATIVO)
            if transacoes:
                ultimo_saldo = transacoes[-1].get('saldo_apos', 0)
                if ultimo_saldo < 0:
                    estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.red)  # 🔥 VERMELHO SE NEGATIVO
                else:
                    estilo_tabela.add('TEXTCOLOR', (4, -1), (4, -1), colors.HexColor("#1E3A8A"))  # 🔥 AZUL SE POSITIVO

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
        """Formata data para o formato DD/MM/YY no PDF - APENAS DATA, SEM HORA"""
        try:
            if not data_iso:
                return ""
            
            # 🔥 EXTRAIR APENAS A PARTE DA DATA (ignorar hora)
            # Pode vir como: "2025-12-22T19:14:34" ou "2025-12-22 19:14:34"
            data_limpa = data_iso
            
            # Remover 'T' se existir
            if 'T' in data_limpa:
                data_limpa = data_limpa.split('T')[0]
            # Remover hora se tiver espaço
            elif ' ' in data_limpa:
                data_limpa = data_limpa.split(' ')[0]
            
            # 🔥 CONVERTER DE YYYY-MM-DD PARA DD/MM/YY
            partes = data_limpa.split('-')
            if len(partes) == 3:
                ano = partes[0][2:]  # Últimos 2 dígitos do ano (YY)
                mes = partes[1]
                dia = partes[2]
                return f"{dia}/{mes}/{ano}"  # 🔥 FORMATO DD/MM/YY
            else:
                return data_limpa
                
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
        
    def gerar_relatorio_financeiro(self, dados, tipo, ano, mes, moeda, nome_arquivo):
        """
        Gera relatório financeiro de receitas/despesas
        dados: dicionário com transacoes, categorias, totais
        tipo: 'receita' ou 'despesa'
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from datetime import datetime
            
            caminho_completo = os.path.join(self.caminho_downloads, nome_arquivo)
            print(f"🔍 PDFGenerator: Gerando relatório financeiro: {caminho_completo}")
            
            # Configurar documento
            doc = SimpleDocTemplate(
                caminho_completo,
                pagesize=A4,
                topMargin=2*cm,
                bottomMargin=2*cm,
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            
            # Estilos
            styles = getSampleStyleSheet()
            
            titulo_style = ParagraphStyle(
                'Titulo',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=10,
                textColor=colors.HexColor('#1E3A8A')
            )
            
            subtitulo_style = ParagraphStyle(
                'Subtitulo',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=colors.HexColor('#4B5563')
            )
            
            secao_style = ParagraphStyle(
                'Secao',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#1E3A8A')
            )
            
            subsecao_style = ParagraphStyle(
                'Subsecao',
                parent=styles['Heading3'],
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor('#3B82F6')
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=9,
                spaceAfter=4
            )
            
            # Conteúdo
            elementos = []
            
            # 1. TÍTULO
            tipo_texto = "RECEITAS" if tipo == 'receita' else "DESPESAS"
            titulo = f"RELATÓRIO DE {tipo_texto}"
            elementos.append(Paragraph(titulo, titulo_style))
            
            # 2. PERÍODO
            meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            mes_nome = meses[mes]
            subtitulo = f"{mes_nome}/{ano}"
            if moeda != 'TODAS':
                subtitulo += f" - Moeda: {moeda}"
            elementos.append(Paragraph(subtitulo, subtitulo_style))
            
            # 3. CARDS DE RESUMO
            total_geral = dados.get('total_geral', 0)
            quantidade = dados.get('quantidade_transacoes', 0)
            media = total_geral / quantidade if quantidade > 0 else 0
            
            resumo_data = [
                ['TOTAL', 'TRANSAÇÕES', 'MÉDIA'],
                [
                    self._formatar_valor_relatorio(total_geral, moeda),
                    str(quantidade),
                    self._formatar_valor_relatorio(media, moeda)
                ]
            ]
            
            resumo_table = Table(resumo_data, colWidths=[5*cm, 5*cm, 5*cm])
            resumo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ]))
            elementos.append(resumo_table)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 4. BREAKDOWN POR MOEDA (se TODAS)
            if moeda == 'TODAS' and dados.get('total_por_moeda'):
                elementos.append(Paragraph("DETALHAMENTO POR MOEDA", secao_style))
                elementos.append(Spacer(1, 0.3*cm))
                
                moedas_data = [['MOEDA', 'VALOR TOTAL', 'PERCENTUAL']]
                for moeda_nome, valor in dados['total_por_moeda'].items():
                    percentual = (valor / total_geral * 100) if total_geral > 0 else 0
                    moedas_data.append([
                        moeda_nome,
                        self._formatar_valor_relatorio(valor, moeda_nome),
                        f"{percentual:.1f}%"
                    ])
                
                moedas_table = Table(moedas_data, colWidths=[4*cm, 5*cm, 4*cm])
                moedas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ]))
                elementos.append(moedas_table)
                elementos.append(Spacer(1, 0.5*cm))
            
            # 5. DETALHAMENTO POR CATEGORIA
            elementos.append(Paragraph("DETALHAMENTO POR CATEGORIA", secao_style))
            elementos.append(Spacer(1, 0.3*cm))
            
            categorias = dados.get('categorias', {})
            for categoria, cat_dados in categorias.items():
                cat_total = cat_dados.get('total', 0)
                cat_text = f"<b>{categoria}</b> - Total: {self._formatar_valor_relatorio(cat_total, moeda)}"
                elementos.append(Paragraph(cat_text, subsecao_style))
                
                # Contas da categoria
                contas_data = [['CONTA ESPECÍFICA', 'VALOR', 'QUANTIDADE']]
                for conta, conta_dados in cat_dados['contas'].items():
                    contas_data.append([
                        conta,
                        self._formatar_valor_relatorio(conta_dados['total'], moeda),
                        str(conta_dados['quantidade'])
                    ])
                
                if len(contas_data) > 1:
                    contas_table = Table(contas_data, colWidths=[8*cm, 4*cm, 3*cm])
                    contas_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6B7280')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                    ]))
                    elementos.append(contas_table)
                    elementos.append(Spacer(1, 0.2*cm))
            
            elementos.append(PageBreak())
            
            # 6. LISTA DE TRANSAÇÕES
            elementos.append(Paragraph("LISTA DE TRANSAÇÕES", secao_style))
            elementos.append(Spacer(1, 0.3*cm))
            
            transacoes_data = [['DATA', 'DESCRIÇÃO', 'CATEGORIA', 'VALOR']]
            
            for trans in dados.get('transacoes', []):
                data = trans.get('data', '')[:10]
                descricao = trans.get('descricao', '')[:60]
                categoria = trans.get('categoria', '')[:35]
                valor = self._formatar_valor_relatorio(trans.get('valor', 0), trans.get('moeda', 'USD'))
                
                transacoes_data.append([data, descricao, categoria, valor])
            
            # Ajustar larguras
            transacoes_table = Table(transacoes_data, colWidths=[2.5*cm, 7.5*cm, 4*cm, 3*cm])
            transacoes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elementos.append(transacoes_table)
            
            # 7. RODAPÉ COM TOTAL
            elementos.append(Spacer(1, 0.5*cm))
            total_text = f"<b>TOTAL GERAL: {self._formatar_valor_relatorio(total_geral, moeda if moeda != 'TODAS' else 'USD')}</b>"
            total_style = ParagraphStyle(
                'Total',
                parent=normal_style,
                fontSize=10,
                alignment=TA_RIGHT,
                textColor=colors.HexColor('#1E3A8A')
            )
            elementos.append(Paragraph(total_text, total_style))
            
            # 8. DATA DE GERAÇÃO
            elementos.append(Spacer(1, 0.5*cm))
            data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
            rodape_style = ParagraphStyle(
                'Rodape',
                parent=normal_style,
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#9CA3AF')
            )
            elementos.append(Paragraph(f"Documento gerado em {data_geracao}", rodape_style))
            
            # Gerar PDF
            doc.build(elementos)
            
            print(f"✅ PDF gerado com sucesso: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _formatar_valor_relatorio(self, valor, moeda):
        """Formata valor para exibição no relatório"""
        if moeda == 'USD':
            return f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'EUR':
            return f"€{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'GBP':
            return f"£{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif moeda == 'BRL':
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')        