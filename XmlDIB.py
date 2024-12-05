import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import base64
import os

st.set_page_config(page_title="XmlDIB", layout="wide", page_icon="🌲")

##### Oculta o botão Deploy do Streamilit
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True
)

# Função para ler a imagem e convertê-la para base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string
# Obtém o diretório do script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho completo para a imagem
image_path = os.path.join(current_dir, "fundo_softdib.jpg")

# Codificação da imagem em base64
base64_image = get_base64_image(image_path)

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('data:image/png;base64,{base64_image}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
###### CSS para definir a imagem de fundo [Fim]

# Função para ler o XML
def ler_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root

# Função para encontrar todas as tags de interesse e preservar o conteúdo integral
def extrair_tags(root, tags_interessadas):
    data = {tag: [] for tag in tags_interessadas}

    # Determinar o maior número de elementos para normalizar as listas
    max_count = 0
    for tag in tags_interessadas:
        tag_count = sum(1 for _ in root.iter(tag))
        max_count = max(max_count, tag_count)

    # Preencher as listas com valores das tags ou None se ausentes
    for tag in tags_interessadas:
        for elem in root.iter(tag):
            conteudo = elem.text if elem.text else ""
            if tag == "descricaoMercadoria" and elem.tail:  # Inclui o tail se existir
                conteudo += elem.tail
            data[tag].append(conteudo.strip())

        # Adicionar valores `None` para normalizar o comprimento
        while len(data[tag]) < max_count:
            data[tag].append(None)

    return data

# Função para atualizar o XML com os novos valores
def atualizar_xml(tree, root, novos_valores, tags_interessadas):
    for tag in tags_interessadas:
        for elem, novo_valor in zip(root.iter(tag), novos_valores[tag]):
            # Atualiza o texto da tag
            if tag == "descricaoMercadoria":
                elem.text = f"{novo_valor.strip()} &#xD;" if novo_valor.strip() else "&#xD;"
            elif tag == "numeroDI":
                if pd.notna(novo_valor) and str(novo_valor).strip().isdigit():
                    elem.text = str(int(novo_valor))  # Atualiza como inteiro
            elif tag in ["dataDesembaraco", "dataRegistro"]:  # Tratamento específico para as novas tags
                if pd.notna(novo_valor):
                    elem.text = novo_valor.strip()  # Atualiza com o valor do CSV, se disponível
            else:
                elem.text = novo_valor.strip() if pd.notna(novo_valor) and novo_valor.strip() else elem.text
    return tree

# Função para exportar os valores de descricaoMercadoria para um arquivo CSV
def exportar_descricao_mercadoria(data):
    descricao_df = pd.DataFrame({"Atual descricaoMercadoria": data["descricaoMercadoria"]})
    csv = descricao_df.to_csv(index=False, sep=";").encode("utf-8")
    
    return csv

# Função principal
def main():

# Faixa no cabeçalho
    st.markdown("""
    <div style='display: flex; justify-content: flex-end; align-items: center; background-color: gainsboro; padding:2px 0;margin-top: -40px;'>
        <span style='color: black; margin-right:10px;'>Alterar Tags xml</span>
    </div>
    """, unsafe_allow_html=True)

    # Adicionar a logo ao topo
    # Obtém o diretório atual do script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Constrói o caminho da imagem dinamicamente
    logo_path = os.path.join(current_dir, "Logo_sd.png")
    # Exibe a logo
    st.image(logo_path, width=200)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div style='font-size: 25px; font-weight: bold; color: #1E90FF;margin-top: 30px'>Editar o XML Tags: descricaoMercadoria, numeroDI, fornecedorNome com Base no CSV</div>", unsafe_allow_html=True)
        #st.title("Editar o XML Tags: < descricaoMercadoria >, < numeroDI >, < fornecedorNome > com Base no CSV")
        st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p><strong>O objetivo de editar a TAG é possibilitar a utilização do programa de importação de XML , agilizando a transferência de dados para o registro da Declaração de Importação-DI.</p>
        <p>A funcionalidade de importação de XML da Declaração de Importação permite a transferência direta dos dados contidos nos arquivos XML gerados pelo SISCOMEX da Receita Federal para o Registro de Entradas, otimizando o processo e diminuindo a possibilidade de erros manuais.<strong></p>
        <p><strong> Nesse processo utilizaremos os arquivos (XMl DI, Itens.csv)<strong>.</p>
        <p> A estrutura do Itens.csv é composta por 4 colunas: Atual descricaoMercadoria;Novo numeroDI; Novo fornecedorNome; Novo descricaoMercadoria </p>
    
    
    </div>
    """, unsafe_allow_html=True)    

        # Tags de interesse
        tags_interessadas = ["descricaoMercadoria", "numeroDI", "fornecedorNome","dataDesembaraco","dataRegistro"]
    # Definir o CSS personalizado
        css = """
        <style>
            /* Estiliza o container do file_uploader */
            [data-testid='stFileUploader'] {
                width: max-content;
            }

            /* Estiliza a seção interna do file_uploader */
            [data-testid='stFileUploader'] section {
                padding: 0;
                float: left;
            }

            /* Esconde o ícone e o texto padrão do botão */
            [data-testid='stFileUploader'] section > input + div {
                display: none;
            }

            /* Estiliza a parte visível do botão */
            [data-testid='stFileUploader'] section + div {
                float: right;
                padding-top: 0;
            }

            /* Altera a cor de fundo do botão */
            [data-testid='stFileUploader'] label {
                background-color: #999999;  /* Cor de fundo do botão */
                color: white;  /* Cor do texto */
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }

            /* Altera a cor do botão ao passar o mouse (hover) */
            [data-testid='stFileUploader'] label:hover {
                background-color: #45a049; /* Cor do botão ao passar o mouse */
            }
        </style>
        """
    with col2:
        # Adicionar o CSS ao app Streamlit
        st.markdown(css, unsafe_allow_html=True)
        # Upload do arquivo XML
        uploaded_file = st.file_uploader("Envie o arquivo XML", type="xml")
        if uploaded_file:
            tree, root = ler_xml(uploaded_file)

            # Extração dos valores atuais das tags
            data = extrair_tags(root, tags_interessadas)
            df = pd.DataFrame(data)

            # Botão para exportar descricaoMercadoria
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; color: #1E90FF;'>Exportar Tag descricaoMercadoria</div>", unsafe_allow_html=True)
            if st.button("Exportar descricaoMercadoria"):
                csv_file = exportar_descricao_mercadoria(data)
                st.download_button(
                    label="Baixar descricaoMercadoria",
                    data=csv_file,
                    file_name="descricaoMercadoria.csv",
                    mime="text/csv",
                )
                st.success("Arquivo descricaoMercadoria.csv gerado com sucesso!")


            # Upload do arquivo CSV
            csv_file = st.file_uploader("Envie o arquivo itens.csv", type="csv")
            if csv_file:
                # Ler o CSV com separador ";"
                csv_data = pd.read_csv(csv_file, delimiter=";")

                # Verificação das colunas no CSV
                required_columns = [
                    "Atual descricaoMercadoria",
                    "Novo numeroDI",
                    "Novo fornecedorNome",
                    "Novo descricaoMercadoria",
                    "Novo dataDesembaraco",  # Novas colunas
                    "Novo dataRegistro"
                ]
                # Atualização no mapeamento de valores do CSV para o DataFrame
                if all(col in csv_data.columns for col in required_columns):
                    for tag in tags_interessadas:
                        nova_coluna = f"Novo {tag}"
                        if nova_coluna in csv_data.columns:
                            df[nova_coluna] = df["descricaoMercadoria"].map(
                                dict(zip(csv_data["Atual descricaoMercadoria"], csv_data[nova_coluna]))
                            )
                            if tag in ["numeroDI", "dataDesembaraco", "dataRegistro"]:
                                # Garantir formato correto para número e datas
                                df[nova_coluna] = df[nova_coluna].apply(lambda x: str(x).strip() if pd.notna(x) else None)

                    st.success("Novos conteúdos preenchidos com base no CSV!")
                else:
                    st.error(f"O arquivo CSV deve conter as colunas: {', '.join(required_columns)}")

            st.markdown(f"<div style='font-size: 30px; font-weight: bold; color: #1E90FF;margin-top: 30px'>Conteúdo das Tags</div>", unsafe_allow_html=True)
            # Exibição da tabela editável
            #st.subheader("Conteúdo das Tags")
            css = """
            <style>
                /* Altera o estilo do botão de download */
                [data-testid='stDownloadButton'] {
                    background-color: #28a745;  /* Cor de fundo do botão (verde) */
                    color: green;  /* Cor do texto */
                    padding: 12px 25px;  /* Aumenta o tamanho do botão */
                    border-radius: 10px;  /* Borda arredondada */
                    font-size: 18px;  /* Tamanho da fonte */
                    font-weight: bold;  /* Peso da fonte */
                    cursor: pointer;  /* Cursor de mão */
                    text-align: center;  /* Alinha o texto ao centro */
                    border: none;  /* Remove a borda padrão */
                }

                /* Efeito hover do botão */
                [data-testid='stDownloadButton']:hover {
                    background-color: #28a745;  /* Cor de fundo mais escura ao passar o mouse */
                }
            </style>
            """
            st.markdown("""<style>
        .stButton button {
            background-color: #999999;  /* Cor CINZA */
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 20px;  /* Ajustando o padding para maior altura */
            font-size: 16px;
            cursor: pointer;
            width: 100%;  /* Tamanho do botão */
            height: 50px;  /* Altura do botão */
        }
        .stButton button:hover {
            background-color: #999999;  /* CINZA mais escuro ao passar o mouse */
        }
    </style>""", unsafe_allow_html=True)


            # Adicionar o CSS ao app Streamlit
            st.markdown(css, unsafe_allow_html=True)
            edited_df = st.data_editor(df, num_rows="dynamic")

            # Substituir os valores no XML
            if st.button("Atualizar XML"):
                novos_valores = {
                    tag: edited_df[f"Novo {tag}"].fillna("").tolist() for tag in tags_interessadas
                }
                tree = atualizar_xml(tree, root, novos_valores, tags_interessadas)

                # Exportar XML atualizado
                xml_path = "xml_atualizado.xml"
                tree.write(xml_path, encoding="utf-8", xml_declaration=True)
                st.success(f"XML atualizado salvo como {xml_path}")
                with open(xml_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="Baixar XML Atualizado",
                        data=f,
                        file_name="xml_atualizado.xml",
                        mime="application/xml"
                    )

if __name__ == "__main__":
    main()
