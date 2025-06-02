'''
Script para gerar arquivos CSV de Vendas com dados fictícios.

Arquivos gerados:
- produtos.csv
- clientes.csv
- vendedores.csv
- fornecedores.csv
- vendas.csv
'''
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np

# Inicializar o Faker
fake = Faker('pt_BR')

# Configurações de Geração
NUM_FORNECEDORES = 10
NUM_PRODUTOS = 50
NUM_CLIENTES = 200
NUM_VENDEDORES = 20
NUM_VENDAS = 1000

# Geração de Fornecedores
fornecedores_data = []
for i in range(1, NUM_FORNECEDORES + 1):
    fornecedores_data.append({
        'id_fornecedor': i,
        'nome_fornecedor': fake.company(),
        'contato_fornecedor': fake.name(),
        'email_fornecedor': fake.email(),
        'telefone_fornecedor': fake.phone_number()
    })
fornecedores_df = pd.DataFrame(fornecedores_data)

# Geração de Produtos
produtos_data = []
categorias_produto = ['Eletrônicos', 'Livros', 'Roupas', 'Alimentos', 'Móveis', 'Brinquedos', 'Esportes']
fornecedor_ids = fornecedores_df['id_fornecedor'].tolist()

for i in range(1, NUM_PRODUTOS + 1):
    custo = round(random.uniform(5.0, 500.0), 2)
    preco_venda = round(custo * random.uniform(1.2, 2.5), 2) # Margem de lucro entre 20% e 150%
    produtos_data.append({
        'id_produto': i,
        'nome_produto': f'{fake.word().capitalize()} {fake.word().capitalize()}', # Nome de produto mais genérico
        'categoria_produto': random.choice(categorias_produto),
        'preco_custo': custo,
        'preco_venda_unitario': preco_venda,
        'id_fornecedor': random.choice(fornecedor_ids)
    })
produtos_df = pd.DataFrame(produtos_data)

# Geração de Clientes
clientes_data = []
regioes_cliente = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
for i in range(1, NUM_CLIENTES + 1):
    clientes_data.append({
        'id_cliente': i,
        'nome_cliente': fake.name(),
        'email_cliente': fake.unique.email(),
        'telefone_cliente': fake.phone_number(),
        'endereco_cliente': fake.street_address(),
        'cidade_cliente': fake.city(),
        'estado_cliente': fake.state_abbr(),
        'pais_cliente': 'Brasil',
        'regiao_cliente': random.choice(regioes_cliente),
        'data_cadastro': fake.date_between(start_date='-3y', end_date='today')
    })
clientes_df = pd.DataFrame(clientes_data)

# Geração de Vendedores
vendedores_data = []
equipes_vendas = ['Equipe Alpha', 'Equipe Beta', 'Equipe Gamma', 'Equipe Delta']
for i in range(1, NUM_VENDEDORES + 1):
    vendedores_data.append({
        'id_vendedor': i,
        'nome_vendedor': fake.name(),
        'email_vendedor': fake.unique.email(),
        'matricula_vendedor': f'V{fake.unique.random_number(digits=5)}',
        'equipe_vendas': random.choice(equipes_vendas)
    })
vendedores_df = pd.DataFrame(vendedores_data)

# Geração de Vendas
vendas_data = []
produto_ids = produtos_df['id_produto'].tolist()
cliente_ids = clientes_df['id_cliente'].tolist()
vendedor_ids = vendedores_df['id_vendedor'].tolist()
metodos_pagamento = ['Cartão de Crédito', 'Boleto Bancário', 'PIX', 'Débito Online', 'Transferência Bancária']

# Criar um dicionário para consulta rápida de preços dos produtos
precos_produtos = produtos_df.set_index('id_produto')['preco_venda_unitario'].to_dict()

for i in range(1, NUM_VENDAS + 1):
    id_prod = random.choice(produto_ids)
    quantidade = random.randint(1, 10)
    preco_unitario_prod = precos_produtos[id_prod]
    valor_total = round(preco_unitario_prod * quantidade, 2)
    
    # Simular datas de venda nos últimos 2 anos
    data_venda = fake.date_time_between(start_date='-2y', end_date='now', tzinfo=None)
    
    vendas_data.append({
        'id_venda': i,
        'id_produto': id_prod,
        'id_cliente': random.choice(cliente_ids),
        'id_vendedor': random.choice(vendedor_ids),
        'data_venda': data_venda,
        'quantidade_vendida': quantidade,
        'valor_total_venda': valor_total,
        'metodo_pagamento': random.choice(metodos_pagamento)
    })
vendas_df = pd.DataFrame(vendas_data)

# Salvar DataFrames em arquivos CSV
output_path = '.' # Salvar no diretório atual

fornecedores_df.to_csv(output_path + '/fornecedores.csv', index=False, encoding='utf-8-sig')
produtos_df.to_csv(output_path + '/produtos.csv', index=False, encoding='utf-8-sig')
clientes_df.to_csv(output_path + '/clientes.csv', index=False, encoding='utf-8-sig')
vendedores_df.to_csv(output_path + '/vendedores.csv', index=False, encoding='utf-8-sig')
vendas_df.to_csv(output_path + '/vendas.csv', index=False, encoding='utf-8-sig')

print(f"Arquivos CSV gerados com sucesso em: {output_path if output_path != '.' else 'diretório atual'}")
print(f" - {len(fornecedores_df)} fornecedores em fornecedores.csv")
print(f" - {len(produtos_df)} produtos em produtos.csv")
print(f" - {len(clientes_df)} clientes em clientes.csv")
print(f" - {len(vendedores_df)} vendedores em vendedores.csv")
print(f" - {len(vendas_df)} vendas em vendas.csv")
