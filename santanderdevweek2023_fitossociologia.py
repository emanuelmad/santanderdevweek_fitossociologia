# -*- coding: utf-8 -*-
"""Cópia de SantanderDevWeek2023.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y34JyeZK4hrr82XL2EPPLHzW3w1S7rH3

# Santander Dev Week 2023 (ETL com Python)

##**Contexto:**##
Ao combinar o conhecimento em Engenharia Florestal com avanços em tecnologia de IA, posso fazer contribuições significativas tanto na academia quanto em aplicações práticas de manejo e conservação florestal.

#Importância dos Dados Fitossociológicos
Dados fitossociológicos, como densidade, dominância, frequência e valor de cobertura de cada espécie, são fundamentais para entender a dinâmica da vegetação e suas relações ecológicas. Esses dados podem ser utilizados para:

Identificar Espécies-Chave: Algumas espécies podem desempenhar papéis ecológicos críticos e podem ser foco de esforços de conservação.

Manejo Sustentável: Informações sobre a estrutura da vegetação ajudam no planejamento de práticas de manejo, como o corte seletivo, que minimiza o impacto ecológico.

Restauração Ecológica: O conhecimento fitossociológico é crucial para restaurar áreas degradadas à sua condição original.

Conservação: Os dados podem ajudar na identificação de áreas que requerem proteção imediata ou monitoramento a longo prazo.

#Integração com Tecnologias de IA
A integração de dados fitossociológicos com tecnologias de Inteligência Artificial, como GPT-4, abre novas portas para a análise e interpretação desses dados. Por exemplo, um modelo de linguagem treinado pode gerar relatórios analíticos instantâneos, propor planos de manejo ou até mesmo identificar padrões e tendências que podem não ser imediatamente aparentes para os humanos.

**Condições do Problema:**

1. Você recebeu uma planilha simples, em formato CSV ('estrutura_horizontal.csv'), com uma lista de IDs de usuário do banco:
  ```
A planilha contém as seguintes colunas:
N: Número de indivíduos.
DA: Densidade absoluta.
DR: Densidade relativa.
FA: Frequência absoluta.
FR: Frequência relativa.
DoA: Dominância absoluta.
DoR: Dominância relativa.
VC: Valor de cobertura.
AB: Abundância.
  ```
2. Extract: Ler a planilha e armazenar os dados em um banco de dados SQLite.
3. Transform: Utilizar a API do GPT-4 para gerar uma análise fitossociológica para cada espécie.
4. Load: Atualizar o banco de dados com as análises geradas.
`.

## **E**xtract
"""

#instalar bibliotecas
!pip install openai

#instalar bibliotecas
import pandas as pd
import sqlite3
import openai

#configuração do chatgpt
openai.api_key = "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"

#Função de Transformação
#criação de uma função transformação
def generate_gpt4_analysis(especie):
    completion = openai.ChatCompletion.create(
        model="gpt-4",  # Substitua pelo modelo de chat que você deseja usar
        messages=[
            {
                "role": "system",
                "content": "Você é um especialista em fitossociologia."
            },
            {
                "role": "user",
                "content": f"Por favor, gere uma análise fitossociológica para a espécie {especie}."
            }
        ]
    )
    return completion['choices'][0]['message']['content'].strip()

# Ler o arquivo Excel
df = pd.read_excel('/content/estrutura_horizontal.xlsx')

# Renomear a primeira coluna para 'Especie'
df.rename(columns={'Unnamed: 0': 'Especie'}, inplace=True)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("inventario_florestal.db")
cursor = conn.cursor()

# Etapa de Transformação (Transform)
# Aplicar a função de análise GPT-4 para cada espécie no DataFrame
df['AnaliseGPT'] = df['Especie'].apply(generate_gpt4_analysis)

# Etapa de Carga (Load)
# Criar a tabela InventarioFlorestal
cursor.execute("""
CREATE TABLE IF NOT EXISTS InventarioFlorestal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Especie TEXT NOT NULL,
    N INTEGER NOT NULL,
    DA REAL NOT NULL,
    DR REAL NOT NULL,
    FA INTEGER NOT NULL,
    FR REAL NOT NULL,
    DoA REAL NOT NULL,
    DoR REAL NOT NULL,
    VC REAL NOT NULL,
    AB REAL NOT NULL
);
""")

# Inserir os dados do DataFrame na tabela InventarioFlorestal
df.to_sql('InventarioFlorestal', conn, if_exists='replace', index=False)

# Criar a tabela Analises para armazenar as análises geradas
cursor.execute("""
CREATE TABLE IF NOT EXISTS Analises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Especie TEXT NOT NULL,
    AnaliseGPT TEXT NOT NULL,
    FOREIGN KEY (Especie) REFERENCES InventarioFlorestal (Especie)
);
""")

# Inserir as análises geradas na tabela Analises
df[['Especie', 'AnaliseGPT']].to_sql('Analises', conn, if_exists='replace', index=False)

print(df['AnaliseGPT'])

#Exportar os dados em xlsx e csv
df.to_excel('analises_geradas.xlsx', index=False)
df.to_csv('analises_geradas.csv', index=False)

conn = sqlite3.connect("inventario_florestal.db")
analises_df = pd.read_sql_query("SELECT * FROM Analises", conn)
conn.close()

print(analises_df)

"""# Análise Geral
Neste caso solicitamos para que o chatgpt identificasse as espécies florestais com maior importância dentro da análise fitossociológica. Além disso, também foi criado análise para a espécie de menor representação e análises dentro de um contexto geral.

Logicamente esse notebook apesar de ser direcionado a minha área de atuação (**Engenharia Florestal**), pode muito bem ser útil a banco de dados relacionados a clientes, além disso, com um plus de extrair informações dentro de uma análise geral do banco de dados.
"""

# Encontrar a espécie com o maior e menor valor para cada variável
summary_data = {}
for column in df.columns[1:]:  # Começa de 1 para ignorar a coluna de espécies
    max_species = df[df[column] == df[column].max()]['Especie'].iloc[0]
    min_species = df[df[column] == df[column].min()]['Especie'].iloc[0]
    summary_data[column] = {'max_species': max_species, 'min_species': min_species}

# Criar um resumo para fornecer ao GPT-4
descriptive_summary = "Neste conjunto de dados fitossociológicos, observamos o seguinte:\n"
for variable, data in summary_data.items():
    descriptive_summary += f"- A espécie com o maior valor de {variable} é {data['max_species']}, enquanto a espécie com o menor valor é {data['min_species']}.\n"

# Gerar a análise geral usando GPT-4
general_analysis = generate_gpt4_analysis(descriptive_summary)

# Imprimir ou salvar a análise geral
print("Análise Geral:", general_analysis)

#Exportar os dados em xlsx e csv
df.to_excel('general_analysis.xlsx', index=False)
df.to_csv('general_analysis.csv', index=False)