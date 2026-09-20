# 🏥 Sistema Otimizado de Escalas de Enfermagem — HC-UFG / EBSERH

> **Otimização de Escalas Assistenciais com Inteligência Artificial Open-Source (Google OR-Tools CP-SAT) e Interface Interativa (Streamlit)**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Optimization Engine](https://img.shields.io/badge/Solver-Google%20OR--Tools%20CP--SAT-orange.svg)](https://developers.google.com/optimization)

---

## 📌 Visão Geral do Projeto

Este projeto consiste no desenvolvimento e implementação de uma solução tecnológica aberta e automatizada para a **gestão, otimização e auditoria de escalas mensais de enfermagem** [1, 3]. O sistema foi projetado sob medida para atender às necessidades operacionais e normativas do **15º Andar (Unidade de Clínica Médica)** do Hospital das Clínicas da Universidade Federal de Goiás (**HC-UFG / Rede EBSERH**) [508].

A solução fundamenta-se na metodologia científica apresentada por **Leung et al. (2022)** (*International Journal of Nursing Sciences*) [1, 3] e traduz de forma exata a legislação trabalhista da **Norma SEI nº 2/2024/DGP-EBSERH** [524, 525] e do **Acordo Coletivo de Trabalho (ACT EBSERH 2026/2027)** [102, 108, 109].

---

## 🎯 Justificativa e Diagnóstico Institucional

No ambiente hospitalar, o planejamento das escalas assistenciais é tradicionalmente feito de forma manual pelo enfermeiro gestor, demandando horas ou dias de trabalho administrativo [3, 509, 522]. Além disso, a desconexão entre o posto de enfermagem e a alta gestão dificulta a consolidação de dados estratégicos referentes a **absenteísmo, licenças médicas, férias e impacto orçamentário** [509, 521, 522].

A aplicação de escalas de classificação de pacientes (como a Escala de Fugulin) no dia a dia da assistência não resolve o problema do dimensionamento mensal e da distribuição justa de carga horária [512, 513, 516, 520]. O verdadeiro gargalo reside na gestão do fluxo de pessoas, afastamentos e no cumprimento rígido das regras trabalhistas da EBSERH [509, 520, 521].

---

## 🏢 Arquitetura de Dupla Visão (*Dual-Persona*)

Para resolver a ruptura de informação entre a assistência e a decisão executiva, o sistema organiza-se em duas perspectivas integradas [511, 521, 522]:

```
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │ 🏥 SISTEMA DE GESTÃO DE ESCALAS ASSISTENCIAIS — HC-UFG / EBSERH                   │
 ├──────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                  │
 │ 📋 VISÃO 1: GESTOR OPERACIONAL (Enfermeiro Líder / Posto)                         │
 │ ---------------------------------------------------------                        │
 │  • Tabela Panorâmica Editável em Tela (Novembro/2026 com destaques visuais)       │
 │  • Motor de IA CP-SAT: Geração de Propostas 100% Isentas de Erros em Segundos     │
 │  • Leitura de Pedidos de Folga Mensal (.xlsx) em Segunda Camada (Soft Constraints)│
 │  • Trava de Preservação (Cadeado 🔒) para Não Sobrescrever Férias/Afastamentos    │
 │  • Ferramenta de Lançamento em Lote (Férias, Atestados e Licenças)               │
 │  • Auditoria por Célula em Tempo Real com Alertas de Infração Normativa          │
 │                                                                                  │
 │ 📊 VISÃO 2: ALTA GESTÃO (Chefia de Divisão / Diretoria)                         │
 │ -------------------------------------------------------                          │
 │  • Dashboard de Indicadores em Destaque (Atestados, Licenças, Férias)            │
 │  • Relatório Consolidado Nominal de Ausências e Absenteísmo                      │
 │  • Histórico de Impacto Operacional e Dimensionamento de Pessoal                 │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ Mapeamento de Restrições e Regras de Negócio

### 🚫 Restrições Rígidas (*Hard Constraints* — Invioláveis)
1. **Cobertura Mínima Diária:** Garantia dos quantitativos mínimos assistenciais exigidos por turno para Enfermeiros e Técnicos [10, 27, 43].
2. **Jornada Única Diária:** Impossibilidade de alocação de mais de um plantão por dia para o mesmo colaborador [10, 27, 529].
3. **Regime 12x36 e Interjornada:** Obrigatoriedade do intervalo mínimo de descanso pós-plantão de 12 horas e interjornada de 11 horas [129, 131, 529, 540].
4. **Teto Consecutivo de Trabalho:** Vedado o trabalho por mais de 6 dias sucessivos (DSR obrigatório até o 7º dia) [27, 533].
5. **Proteção de Gênero (ACT Cl. 24ª §1º):** Escala de revezamento que assegura o repouso quinzenal aos domingos para mulheres (vedação a 2 domingos seguidos) [122, 145].
6. **Descanso Semanal Geral:** Garantia de ao menos um final de semana completo de folga (Sábado + Domingo) no mês para todos os colaboradores [145, 534].
7. **Fechamento de Carga Horária Mensal:** Respeito às metas contratuais de **156h (36h semanais)** e **176h (40h semanais)**, com compensações feitas estritamente em blocos de 6h [27, 39, 43, 60, 530, 531].

### 💚 Restrições Flexíveis (*Soft Constraints* — Preferências)
* **Atendimento a Pedidos de Folga Mensal:** Otimização da alocação respeitando os pedidos individuais da equipe enviados via arquivo Excel (`.xlsx`), com destaque em verde (`FP`) na grade [3, 9, 12].

---

## 👥 Equipe do 15º Andar (Base de Dados)

O sistema é configurado com a matriz nominal completa dos **40 colaboradores** do andar [26, 35, 41, 51]:
* **20 Enfermeiros** (12 Diurnos + 8 Noturnos em regime 12x36) [26, 41, 51].
* **20 Técnicos de Enfermagem** (14 Diurnos + 6 Noturnos em regime 12x36) [26, 41, 51].

---

## 🚀 Como Executar o Projeto

### 💻 Opção 1: Execução no Google Colab (Recomendado)

1. Faça o clone do repositório no seu ambiente Colab:
   ```bash
   !git clone https://github.com/seu-usuario/escala-enfermagem-hc.git
   %cd escala-enfermagem-hc
   ```

2. Instale as dependências:
   ```bash
   !pip install -q -r requirements.txt
   ```

3. Execute o aplicativo via Streamlit e Cloudflare Tunnel:
   ```python
   import time
   from google.colab import output

   !pkill -f streamlit
   get_ipython().system_raw('streamlit run sistema_escala_hc15_v5.py &')
   time.sleep(3)

   !wget -q -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   !chmod +x cloudflared
   !./cloudflared tunnel --url http://localhost:8501
   ```

4. Acesse a aplicação pelo link público `.trycloudflare.com` gerado na saída do terminal.

---

### 🖥️ Opção 2: Execução Local (PC / Servidor Hospitalar)

1. Certifique-se de ter o **Python 3.10+** instalado.
2. Clone o repositório e instale os pacotes:
   ```bash
   git clone https://github.com/seu-usuario/escala-enfermagem-hc.git
   cd escala-enfermagem-hc
   pip install -r requirements.txt
   ```
3. Inicie o aplicativo:
   ```bash
   streamlit run sistema_escala_hc15_v5.py
   ```
4. O navegador abrirá automaticamente no endereço `http://localhost:8501`.

---

## 📁 Estrutura de Arquivos do Repositório

```text
escala-enfermagem-hc/
├── sistema_escala_hc15_v5.py       # Aplicativo web em Streamlit (CP-SAT Solver + Dashboard + Edição)
├── banco_profissionais_hc15_v2.csv   # Base de dados nominal dos 40 colaboradores do 15º andar
├── requirements.txt                 # Lista de dependências (streamlit, ortools, pandas, openpyxl)
├── README.md                        # Documentação técnica do projeto
└── docs/
    ├── especificacao_tecnica.pdf    # Especificação normativa (Norma SEI nº 2/2024 e ACT EBSERH)
    └── modelo_pedidos_folga.xlsx    # Modelo padrão de planilha para envio de pedidos da equipe
```

---

## 📚 Referências Científicas e Normativas

1. **LEUNG, F.; LAU, Y.-C.; LAW, M.; DJENG, S.-K.** *Artificial intelligence and end user tools to develop a nurse duty roster scheduling system*. **International Journal of Nursing Sciences**, v. 9, n. 3, p. 373-377, 2022. [1, 2, 3]
2. **EMPRESA BRASILEIRA DE SERVIÇOS HOSPITALARES (EBSERH).** *Norma - SEI nº 2/2024/DGP-EBSERH: Gestão da Frequência e das Jornadas de Trabalho*. Brasília: EBSERH, 2024. [524, 525]
3. **EBSERH / CONDSEF / CNTS / FNE / FENAM.** *Acordo Coletivo de Trabalho (ACT) 2026/2027*. Brasília, 2026. [102, 108]
4. **EBSERH.** *Manual de Parâmetros de Serviços Assistenciais da Rede EBSERH: Método de Determinação de Padrões Temporais para Gestão da Produção*. Brasília: EBSERH, 2022. [177, 178, 200]

---

## 📄 Licença

Este projeto é um software de código aberto (*open-source*) desenvolvido para fins acadêmicos e de gestão hospitalar pública sob a licença MIT [3, 5].
