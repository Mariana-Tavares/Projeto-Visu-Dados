'''
Dashboard de Vendas - Projeto Final

Este script cria um dashboard interativo com Streamlit para analisar dados de vendas.
Ele carrega dados de 5 arquivos CSV, realiza transformações e apresenta
visualizações em abas, com filtros interativos.
'''
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# Configuração da Página
st.set_page_config(page_title="Painel de Vendas", page_icon="💰", layout="wide")

# Carregamento de Dados
@st.cache_data # Usar cache para otimizar o carregamento
def load_data(): # Remover base_path ou usar um default que indique o diretório atual
    try:
        # Usar caminhos relativos. Os CSVs devem estar na mesma pasta que este script.
        produtos_df = pd.read_csv('produtos.csv')
        clientes_df = pd.read_csv('clientes.csv')
        vendedores_df = pd.read_csv('vendedores.csv')
        vendas_df = pd.read_csv('vendas.csv')
        # fornecedores_df = pd.read_csv('fornecedores.csv') # Carregar se for usar

        # Converter colunas de data
        vendas_df['data_venda'] = pd.to_datetime(vendas_df['data_venda'])
        clientes_df['data_cadastro'] = pd.to_datetime(clientes_df['data_cadastro'])
        
        return produtos_df, clientes_df, vendedores_df, vendas_df
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar os arquivos CSV: {e}. Verifique os caminhos e se os arquivos existem.")
        return None, None, None, None

produtos_df, clientes_df, vendedores_df, vendas_df = load_data()

if produtos_df is None:
    st.stop() # Interrompe a execução se os dados não puderem ser carregados

# Transformação e Regras de Negócio
# Merge dos DataFrames para criar uma visão unificada
if vendas_df is not None and produtos_df is not None and clientes_df is not None and vendedores_df is not None:
    df_merged = pd.merge(vendas_df, produtos_df, on='id_produto', how='left')
    df_merged = pd.merge(df_merged, clientes_df, on='id_cliente', how='left')
    df_merged = pd.merge(df_merged, vendedores_df, on='id_vendedor', how='left')

    # Colunas Calculadas (Regras de Negócio)
    df_merged['lucro_venda'] = (df_merged['preco_venda_unitario'] - df_merged['preco_custo']) * df_merged['quantidade_vendida']
    df_merged['margem_lucro_percentual'] = (df_merged['lucro_venda'] / df_merged['valor_total_venda']) * 100
    df_merged['margem_lucro_percentual'] = df_merged['margem_lucro_percentual'].fillna(0) # Tratar NaNs se valor_total_venda for 0
    df_merged['ano_mes_venda'] = df_merged['data_venda'].dt.to_period('M').astype(str) # Para agrupamento mensal
    df_merged['ano_venda'] = df_merged['data_venda'].dt.year
else:
    st.warning("Não foi possível realizar o merge dos dataframes. Verifique os arquivos de entrada.")
    df_merged = pd.DataFrame() # Cria um DF vazio para evitar erros subsequentes

# Layout do Dashboard
st.title("💰 Painel Analítico de Vendas")

# Filtros na Sidebar
st.sidebar.header("Filtros")

if not df_merged.empty:
    # Filtro de Período (data da venda)
    min_date = df_merged['data_venda'].min().date()
    max_date = df_merged['data_venda'].max().date()
    
    if min_date < max_date:
        date_value_from_input = st.sidebar.date_input(
            "Período da Venda",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )
        if isinstance(date_value_from_input, tuple) and len(date_value_from_input) == 2:
            start_date, end_date = date_value_from_input
        elif isinstance(date_value_from_input, date):
            st.warning("O seletor de período de datas retornou uma data única inesperadamente. Usando esta data como início e fim do período.")
            start_date = end_date = date_value_from_input
        else:
            st.error("Retorno inesperado do seletor de datas. Usando o período completo disponível como padrão.")
            start_date = min_date
            end_date = max_date
    elif min_date == max_date:
        start_date = end_date = st.sidebar.date_input(
            "Data da Venda",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )
    else: # Caso não haja datas válidas
        start_date = end_date = datetime.now().date()
        st.sidebar.warning("Não há dados de vendas suficientes para definir um período.")

    # Filtro de Produto (Nome ou Categoria)
    all_products = sorted(df_merged['nome_produto'].unique().tolist())
    selected_products = st.sidebar.multiselect("Produtos", options=['Todos'] + all_products, default=['Todos'])
    if 'Todos' in selected_products:
        selected_products = all_products

    all_categories = sorted(df_merged['categoria_produto'].unique().tolist())
    selected_categories = st.sidebar.multiselect("Categorias de Produto", options=['Todas'] + all_categories, default=['Todas'])
    if 'Todas' in selected_categories:
        selected_categories = all_categories

    # Filtro de Cliente (Nome ou Região)
    all_clients = sorted(df_merged['nome_cliente'].unique().tolist())
    selected_clients = st.sidebar.multiselect("Clientes", options=['Todos'] + all_clients, default=['Todos'])
    if 'Todos' in selected_clients:
        selected_clients = all_clients

    all_client_regions = sorted(df_merged['regiao_cliente'].unique().tolist())
    selected_client_regions = st.sidebar.multiselect("Regiões do Cliente", options=['Todas'] + all_client_regions, default=['Todas'])
    if 'Todas' in selected_client_regions:
        selected_client_regions = all_client_regions

    # Filtro de Vendedor
    all_sellers = sorted(df_merged['nome_vendedor'].unique().tolist())
    selected_sellers = st.sidebar.multiselect("Vendedores", options=['Todos'] + all_sellers, default=['Todos'])
    if 'Todos' in selected_sellers:
        selected_sellers = all_sellers

    # Aplicar filtros ao DataFrame
    df_filtered = df_merged[
        (df_merged['data_venda'].dt.date >= start_date) &
        (df_merged['data_venda'].dt.date <= end_date) &
        (df_merged['nome_produto'].isin(selected_products)) &
        (df_merged['categoria_produto'].isin(selected_categories)) &
        (df_merged['nome_cliente'].isin(selected_clients)) &
        (df_merged['regiao_cliente'].isin(selected_client_regions)) &
        (df_merged['nome_vendedor'].isin(selected_sellers))
    ]
else:
    st.sidebar.warning("DataFrame vazio, filtros não podem ser aplicados.")
    df_filtered = df_merged # Mantém o DF vazio

#  Abas do Dashboard 
tab1, tab2 = st.tabs(["Visão Geral de Vendas", "Análise de Produtos e Clientes"])

with tab1: # Aba "Visão Geral de Vendas"
    st.header("Visão Geral de Vendas")
    if not df_filtered.empty:
        # KPIs
        total_vendas_valor = df_filtered['valor_total_venda'].sum()
        total_lucro_valor = df_filtered['lucro_venda'].sum()
        num_transacoes = df_filtered['id_venda'].nunique()
        ticket_medio = total_vendas_valor / num_transacoes if num_transacoes > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Vendas (R$)", f"{total_vendas_valor:,.2f}")
        col2.metric("Total de Lucro (R$)", f"{total_lucro_valor:,.2f}")
        col3.metric("Número de Transações", f"{num_transacoes:,}")
        col4.metric("Ticket Médio (R$)", f"{ticket_medio:,.2f}")

        st.markdown("---    ")
        # Gráfico de Linha: Evolução das Vendas e Lucro ao longo do tempo
        df_evolucao = df_filtered.groupby('ano_mes_venda')[['valor_total_venda', 'lucro_venda']].sum().reset_index()
        df_evolucao = df_evolucao.sort_values(by='ano_mes_venda')
        fig_evolucao = px.line(df_evolucao, x='ano_mes_venda', y=['valor_total_venda', 'lucro_venda'],
                               title="Evolução Mensal de Vendas e Lucro", markers=True,
                               labels={'value': 'Valor (R$)', 'variable': 'Métrica', 'ano_mes_venda': 'Mês'})
        fig_evolucao.update_layout(yaxis_title="Valor (R$)")
        st.plotly_chart(fig_evolucao, use_container_width=True)

        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            # Gráfico de Barras: Top N Vendedores por valor de venda
            top_n_vendedores = st.number_input("Número de Top Vendedores para exibir:", min_value=3, max_value=20, value=5, key='top_vendedores_geral')
            df_top_vendedores = df_filtered.groupby('nome_vendedor')['valor_total_venda'].sum().nlargest(top_n_vendedores).reset_index()
            fig_top_vendedores = px.bar(df_top_vendedores, x='nome_vendedor', y='valor_total_venda',
                                        title=f"Top {top_n_vendedores} Vendedores por Valor de Venda",
                                        labels={'nome_vendedor': 'Vendedor', 'valor_total_venda': 'Total Vendas (R$)'},
                                        color='nome_vendedor')
            st.plotly_chart(fig_top_vendedores, use_container_width=True)

        with col_vis2:
            # Gráfico de Pizza/Barras: Distribuição de Vendas por Região do Cliente
            df_vendas_regiao = df_filtered.groupby('regiao_cliente')['valor_total_venda'].sum().reset_index()
            fig_vendas_regiao = px.pie(df_vendas_regiao, values='valor_total_venda', names='regiao_cliente',
                                       title="Distribuição de Vendas por Região do Cliente",
                                       hole=.3)
            fig_vendas_regiao.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_vendas_regiao, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para os filtros selecionados na Visão Geral de Vendas.")

with tab2: # Aba "Análise de Produtos e Clientes"
    st.header("Análise de Produtos e Clientes")
    if not df_filtered.empty:
        col_prod1, col_prod2 = st.columns(2)
        with col_prod1:
            # Gráfico de Barras: Produtos mais vendidos (por valor ou quantidade)
            tipo_analise_produto = st.radio("Analisar produtos por:", ('Valor de Venda', 'Quantidade Vendida'), key='tipo_analise_prod')
            top_n_produtos = st.number_input("Número de Top Produtos para exibir:", min_value=3, max_value=20, value=5, key='top_produtos_analise')
            
            if tipo_analise_produto == 'Valor de Venda':
                df_top_produtos = df_filtered.groupby('nome_produto')['valor_total_venda'].sum().nlargest(top_n_produtos).reset_index()
                y_axis_prod = 'valor_total_venda'
                y_label_prod = 'Total Vendas (R$)'
            else:
                df_top_produtos = df_filtered.groupby('nome_produto')['quantidade_vendida'].sum().nlargest(top_n_produtos).reset_index()
                y_axis_prod = 'quantidade_vendida'
                y_label_prod = 'Quantidade Vendida'

            fig_top_produtos = px.bar(df_top_produtos, x='nome_produto', y=y_axis_prod,
                                      title=f"Top {top_n_produtos} Produtos por {tipo_analise_produto}",
                                      labels={'nome_produto': 'Produto', y_axis_prod: y_label_prod},
                                      color='nome_produto')
            st.plotly_chart(fig_top_produtos, use_container_width=True)

        with col_prod2:
            # Gráfico de Barras: Clientes que mais compraram (por valor)
            top_n_clientes = st.number_input("Número de Top Clientes para exibir:", min_value=3, max_value=20, value=5, key='top_clientes_analise')
            df_top_clientes = df_filtered.groupby('nome_cliente')['valor_total_venda'].sum().nlargest(top_n_clientes).reset_index()
            fig_top_clientes = px.bar(df_top_clientes, x='nome_cliente', y='valor_total_venda',
                                      title=f"Top {top_n_clientes} Clientes por Valor de Compra",
                                      labels={'nome_cliente': 'Cliente', 'valor_total_venda': 'Total Comprado (R$)'},
                                      color='nome_cliente')
            st.plotly_chart(fig_top_clientes, use_container_width=True)
        
        st.markdown("---    ")
        # Tabela: Detalhes dos produtos com filtros
        st.subheader("Detalhes dos Produtos Vendidos")
        
        # Selecionar colunas para exibir na tabela de produtos
        cols_produtos_disponiveis = ['nome_produto', 'categoria_produto', 'preco_venda_unitario', 'preco_custo', 'quantidade_vendida', 'valor_total_venda', 'lucro_venda', 'margem_lucro_percentual']
        selected_cols_tabela_prod = st.multiselect("Selecione as colunas para a tabela de produtos:", 
                                                   options=cols_produtos_disponiveis, 
                                                   default=['nome_produto', 'categoria_produto', 'quantidade_vendida', 'valor_total_venda', 'lucro_venda'])
        
        if selected_cols_tabela_prod:
            # Agrupar para evitar repetição excessiva de produtos se não houver filtros muito específicos
            # Poderia ser mais detalhado se necessário (ex: por transação)
            df_produtos_detalhes = df_filtered.groupby(['id_produto', 'nome_produto', 'categoria_produto', 'preco_venda_unitario', 'preco_custo']).agg(
                quantidade_total_vendida=('quantidade_vendida', 'sum'),
                valor_total_arrecadado=('valor_total_venda', 'sum'),
                lucro_total_gerado=('lucro_venda', 'sum')
            ).reset_index()
            df_produtos_detalhes['margem_lucro_media_percentual'] = (df_produtos_detalhes['lucro_total_gerado'] / df_produtos_detalhes['valor_total_arrecadado']) * 100
            df_produtos_detalhes['margem_lucro_media_percentual'] = df_produtos_detalhes['margem_lucro_media_percentual'].fillna(0)
            
            # Renomear colunas para a exibição e selecionar as colunas corretas
            display_cols_map = {
                'nome_produto': 'Produto',
                'categoria_produto': 'Categoria',
                'preco_venda_unitario': 'Preço Unit. (R$)',
                'preco_custo': 'Custo Unit. (R$)',
                'quantidade_total_vendida': 'Qtd. Vendida Total',
                'valor_total_arrecadado': 'Receita Total (R$)',
                'lucro_total_gerado': 'Lucro Total (R$)',
                'margem_lucro_media_percentual': 'Margem Lucro Média (%)'
            }
            
            # Mapear as colunas selecionadas pelo usuário para as colunas do DataFrame agregado
            # E depois para os nomes de exibição
            cols_to_show_in_table = []
            if 'nome_produto' in selected_cols_tabela_prod: cols_to_show_in_table.append('nome_produto')
            if 'categoria_produto' in selected_cols_tabela_prod: cols_to_show_in_table.append('categoria_produto')
            if 'preco_venda_unitario' in selected_cols_tabela_prod: cols_to_show_in_table.append('preco_venda_unitario')
            if 'preco_custo' in selected_cols_tabela_prod: cols_to_show_in_table.append('preco_custo')
            if 'quantidade_vendida' in selected_cols_tabela_prod: cols_to_show_in_table.append('quantidade_total_vendida')
            if 'valor_total_venda' in selected_cols_tabela_prod: cols_to_show_in_table.append('valor_total_arrecadado')
            if 'lucro_venda' in selected_cols_tabela_prod: cols_to_show_in_table.append('lucro_total_gerado')
            if 'margem_lucro_percentual' in selected_cols_tabela_prod: cols_to_show_in_table.append('margem_lucro_media_percentual')
            
            df_display_produtos = df_produtos_detalhes[cols_to_show_in_table].rename(columns=display_cols_map)
            st.dataframe(df_display_produtos, use_container_width=True)
        else:
            st.info("Selecione colunas para exibir os detalhes dos produtos.")

    else:
        st.info("Nenhum dado disponível para os filtros selecionados na Análise de Produtos e Clientes.")


# Para rodar: streamlit run dashboard_vendas_projeto.py