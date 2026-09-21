import streamlit as st
import pandas as pd
import numpy as np
import io
import json
import os
from ortools.sat.python import cp_model

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E CSS EXECUTIVO COMPACTO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Escalas HC 15º Andar (Clínica Médica)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de CSS para garantir tabela compacta sem rolagem lateral excessiva
st.markdown("""
<style>
    /* Estilização compacta para tabela e container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .stDataFrame {
        font-size: 11px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: bold;
    }
    .badge-enf {
        background-color: #1E3A8A;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-tec {
        background-color: #047857;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Sistema de Gestão e Otimização de Escalas — HC-UFG / EBSERH")
st.caption("Unidade de Clínica Médica (15º Andar) — Arquitetura Dual-Persona (Gestor Operacional & Alta Gestão)")

# -----------------------------------------------------------------------------
# CAMINHO DE PERSISTÊNCIA SEGURO (COMPATÍVEL COM WINDOWS E LINUX)
# -----------------------------------------------------------------------------
CAMINHO_PERSISTENCIA = os.path.join(os.getcwd(), "escala_estado_hc15.json")

# -----------------------------------------------------------------------------
# BASE DE DADOS OFICIAL DOS 40 PROFISSIONAIS (HC 15º ANDAR)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_profissionais_base():
    csv_data = """ID,Nome,Sexo,Cargo,Turno_Base,Carga_Semanal,Regime_12x36
ENF-01,Ana Paula Silva,Feminino,Enfermeiro,Diurno,36h,Não
ENF-02,Beatriz Oliveira,Feminino,Enfermeiro,Diurno,36h,Não
ENF-03,Carlos Eduardo Lima,Masculino,Enfermeiro,Diurno,40h,Não
ENF-04,Daniela Martins,Feminino,Enfermeiro,Diurno,36h,Não
ENF-05,Eduardo Rocha,Masculino,Enfermeiro,Diurno,40h,Não
ENF-06,Fernanda Alves,Feminino,Enfermeiro,Diurno,36h,Não
ENF-07,Gabriel Santos,Masculino,Enfermeiro,Diurno,40h,Não
ENF-08,Helena Costa,Feminino,Enfermeiro,Diurno,36h,Não
ENF-09,Igor Ribeiro,Masculino,Enfermeiro,Diurno,36h,Não
ENF-10,Juliana Lima,Feminino,Enfermeiro,Diurno,40h,Não
ENF-11,Kátia Mendes,Feminino,Enfermeiro,Diurno,36h,Não
ENF-12,Lucas Pereira,Masculino,Enfermeiro,Diurno,40h,Não
ENF-13,Marcelo Silva,Masculino,Enfermeiro,Noturno,36h,Sim
ENF-14,Nádia Ferreira,Feminino,Enfermeiro,Noturno,36h,Sim
ENF-15,Otávio Barbosa,Masculino,Enfermeiro,Noturno,40h,Sim
ENF-16,Patricia Gomes,Feminino,Enfermeiro,Noturno,36h,Sim
ENF-17,Renato Cardoso,Masculino,Enfermeiro,Noturno,36h,Sim
ENF-18,Simone Duarte,Feminino,Enfermeiro,Noturno,40h,Sim
ENF-19,Thiago Moraes,Masculino,Enfermeiro,Noturno,36h,Sim
ENF-20,Vanessa Castro,Feminino,Enfermeiro,Noturno,40h,Sim
TEC-01,Aline Souza,Feminino,Técnico de Enfermagem,Diurno,36h,Não
TEC-02,Bruno Carrijo,Masculino,Técnico de Enfermagem,Diurno,36h,Não
TEC-03,Camila Rodrigues,Feminino,Técnico de Enfermagem,Diurno,36h,Não
TEC-04,Diego Fernandes,Masculino,Técnico de Enfermagem,Diurno,40h,Não
TEC-05,Eliana Machado,Feminino,Técnico de Enfermagem,Diurno,40h,Não
TEC-06,Fabio Henrique,Masculino,Técnico de Enfermagem,Diurno,36h,Não
TEC-07,Gisele Prado,Feminino,Técnico de Enfermagem,Diurno,36h,Não
TEC-08,Heitor Vasconcelos,Masculino,Técnico de Enfermagem,Diurno,40h,Não
TEC-09,Isabela Faria,Feminino,Técnico de Enfermagem,Diurno,40h,Não
TEC-10,João Vitor Cruz,Masculino,Técnico de Enfermagem,Diurno,40h,Não
TEC-11,Karen Stephanie,Feminino,Técnico de Enfermagem,Diurno,36h,Não
TEC-12,Leonardo Nogueira,Masculino,Técnico de Enfermagem,Diurno,36h,Não
TEC-13,Mariana Freitas,Feminino,Técnico de Enfermagem,Diurno,40h,Não
TEC-14,Natália Guimarães,Feminino,Técnico de Enfermagem,Diurno,36h,Não
TEC-15,Orlando Ramos,Masculino,Técnico de Enfermagem,Noturno,36h,Sim
TEC-16,Paula Tejada,Feminino,Técnico de Enfermagem,Noturno,36h,Sim
TEC-17,Quintino Bocaiúva,Masculino,Técnico de Enfermagem,Noturno,36h,Sim
TEC-18,Raquel Xavier,Feminino,Técnico de Enfermagem,Noturno,36h,Sim
TEC-19,Samuel Rosa,Masculino,Técnico de Enfermagem,Noturno,36h,Sim
TEC-20,Tatiana Valente,Feminino,Técnico de Enfermagem,Noturno,40h,Sim"""
    return pd.read_csv(io.StringIO(csv_data))

df_profs = carregar_profissionais_base()

# Dias do mês de Novembro/2026 (1 a 30) - Inicia no Domingo (Dia 1)
# Sábados: 7, 14, 21, 28 | Domingos: 1, 8, 15, 22, 29
DIAS_MES = 30
SABADOS = [7, 14, 21, 28]
DOMINGOS = [1, 8, 15, 22, 29]
FINAIS_DE_SEMANA = SABADOS + DOMINGOS

OPCOES_VALIDAS = ["", "M6", "D12", "N12", "FP", "FE", "AT", "LM", "LIC"]
HORAS_MAP = {
    "": 0,
    "M6": 6,
    "D12": 12,
    "N12": 12,
    "FP": 0,
    "FE": 0,
    "AT": 0,
    "LM": 0,
    "LIC": 0
}

# -----------------------------------------------------------------------------
# PERSISTÊNCIA ROBUSTA EM DISCO
# -----------------------------------------------------------------------------
def salvar_estado_disco(df_escala, travas_dict):
    try:
        data = {
            "escala": df_escala.to_dict(orient="records"),
            "travas": travas_dict
        }
        with open(CAMINHO_PERSISTENCIA, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass # Ignora silenciosamente se o sistema de arquivos for somente leitura

def carregar_estado_disco():
    if os.path.exists(CAMINHO_PERSISTENCIA):
        try:
            with open(CAMINHO_PERSISTENCIA, "r", encoding="utf-8") as f:
                data = json.load(f)
                return pd.DataFrame(data["escala"]), data.get("travas", {})
        except Exception:
            pass
    return None, {}

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# -----------------------------------------------------------------------------
if 'tabela_escala' not in st.session_state:
    df_disco, travas_disco = carregar_estado_disco()
    if df_disco is not None:
        st.session_state['tabela_escala'] = df_disco
        st.session_state['travas_celulas'] = travas_disco
    else:
        rows = []
        for _, row in df_profs.iterrows():
            cargo_sigla = "ENF" if row['Cargo'] == 'Enfermeiro' else "TÉC"
            meta = 156 if row['Carga_Semanal'] == '36h' else 176
            r = {
                'ID': row['ID'],
                'Nome': row['Nome'],
                'Cargo': cargo_sigla,
                'Meta': meta
            }
            for d in range(1, DIAS_MES + 1):
                r[str(d)] = ""
            r['Cumprida'] = 0
            r['Saldo'] = f"-{meta}h"
            rows.append(r)
        st.session_state['tabela_escala'] = pd.DataFrame(rows)
        st.session_state['travas_celulas'] = {}

if 'travas_celulas' not in st.session_state:
    st.session_state['travas_celulas'] = {}

# -----------------------------------------------------------------------------
# CRIAÇÃO DAS ABAS PRINCIPAIS (ESTRUTURA DUAL-PERSONA)
# -----------------------------------------------------------------------------
aba_escala, aba_dashboard = st.tabs([
    "📋 Escala Operacional (Visão do Gestor)",
    "📊 Dashboard de Inteligência & Dimensionamento (Alta Gestão)"
])

# =============================================================================
# ABA 1: ESCALA OPERACIONAL (GESTOR)
# =============================================================================
with aba_escala:
    st.markdown("### 📋 Grade Mensal Panorâmica — Novembro/2026")
    st.caption("Edição direta por célula, aplicação de regras rígidas da Ebserh/ACT e trava manual de afastamentos.")

    # FERRAMENTA DE MARCAÇÃO EM LOTE E LOCKS (EXPANSÍVEL COMPACTO)
    with st.expander("📌 Ferramentas Avançadas: Lançamento em Lote & Lock de Células", expanded=False):
        f1, f2, f3, f4, f5 = st.columns([3, 2, 1.5, 1.5, 2])
        with f1:
            prof_sel = st.selectbox("Profissional", ["TODOS"] + df_profs['Nome'].tolist(), key="lote_prof")
        with f2:
            evento_sel = st.selectbox("Tipo de Evento", ["FE - Férias", "AT - Atestado", "LM - Maternidade", "LIC - Licença Pessoal", "FP - Folga Pedida", "FOLGA (Vazio)"], key="lote_evento")
        with f3:
            dia_ini = st.number_input("Dia Inicial", min_value=1, max_value=30, value=1, key="lote_ini")
        with f4:
            dia_fim = st.number_input("Dia Final", min_value=1, max_value=30, value=15, key="lote_fim")
        with f5:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_aplicar_lote = st.button("📌 Aplicar e Travar", type="secondary", use_container_width=True)

        if btn_aplicar_lote:
            val_map = {
                "FE - Férias": "FE",
                "AT - Atestado": "AT",
                "LM - Maternidade": "LM",
                "LIC - Licença Pessoal": "LIC",
                "FP - Folga Pedida": "FP",
                "FOLGA (Vazio)": ""
            }
            codigo_eve = val_map[evento_sel]
            df_cur = st.session_state['tabela_escala'].copy()
            
            profs_alvo = df_profs['Nome'].tolist() if prof_sel == "TODOS" else [prof_sel]
            for p_nome in profs_alvo:
                idx = df_cur[df_cur['Nome'] == p_nome].index
                if len(idx) > 0:
                    i = idx[0]
                    for d in range(dia_ini, dia_fim + 1):
                        df_cur.at[i, str(d)] = codigo_eve
                        st.session_state['travas_celulas'][f"{p_nome}_{d}"] = codigo_eve
            
            st.session_state['tabela_escala'] = df_cur
            salvar_estado_disco(df_cur, st.session_state['travas_celulas'])
            st.success(f"✅ {evento_sel} aplicado e travado para os dias {dia_ini} a {dia_fim}!")

    # BOTÕES DE OTIMIZAÇÃO E AÇÃO
    c_btn1, c_btn2, c_btn3 = st.columns([3, 2, 3])
    with c_btn1:
        btn_otimizar = st.button("🚀 Otimizar Escala sem Erros (Google OR-Tools)", type="primary", use_container_width=True)
    with c_btn2:
        travar_afastamentos = st.checkbox("🔒 Preservar Afastamentos & Locks Manualmente", value=True)
    with c_btn3:
        btn_limpar_locks = st.button("🔓 Remover Todos os Locks Manuais", use_container_width=True)

    if btn_limpar_locks:
        st.session_state['travas_celulas'] = {}
        st.success("🔓 Todos os cadeados manuais foram removidos.")

    # ENGINE DE OTIMIZAÇÃO CP-SAT (GOOGLE OR-TOOLS)
    if btn_otimizar:
        with st.spinner("Iniciando otimizador CP-SAT... Validando Hard Constraints (Ebserh/ACT)..."):
            num_profs = len(df_profs)
            dias = list(range(1, DIAS_MES + 1))
            turnos = ['M6', 'D12', 'N12']
            
            modelo = cp_model.CpModel()
            escala_vars = {(p, d, t): modelo.NewBoolVar(f'p_{p}_d_{d}_t_{t}') for p in range(num_profs) for d in dias for t in turnos}
            
            # 1. APLICAÇÃO DE LOCKS MANUAIS E AFASTAMENTOS COMO HARD CONSTRAINTS
            afastamentos_bloqueantes = ['FE', 'AT', 'LM', 'LIC', 'FP']
            df_atual = st.session_state['tabela_escala']
            
            for p in range(num_profs):
                prof_nome = df_profs.iloc[p]['Nome']
                row_prof = df_atual[df_atual['Nome'] == prof_nome]
                if len(row_prof) > 0:
                    r_p = row_prof.iloc[0]
                    for d in dias:
                        val_celula = str(r_p[str(d)]).strip().upper()
                        chave_lock = f"{prof_nome}_{d}"
                        
                        # Se estiver travado ou for afastamento e o checkbox estiver ativo
                        if (chave_lock in st.session_state['travas_celulas'] or (travar_afastamentos and val_celula in afastamentos_bloqueantes)):
                            if val_celula in turnos:
                                # Força o turno exato escolhido pelo gestor
                                for t in turnos:
                                    modelo.Add(escala_vars[(p, d, t)] == (1 if t == val_celula else 0))
                            else:
                                # Força folga/afastamento no dia
                                for t in turnos:
                                    modelo.Add(escala_vars[(p, d, t)] == 0)

            # 2. HARD CONSTRAINTS DA EBSERH / ACT
            for p in range(num_profs):
                prof = df_profs.iloc[p]
                
                # A) Domínio de Turno Base
                for d in dias:
                    if prof['Turno_Base'] == 'Noturno':
                        modelo.Add(escala_vars[(p, d, 'M6')] == 0)
                        modelo.Add(escala_vars[(p, d, 'D12')] == 0)
                    else:
                        modelo.Add(escala_vars[(p, d, 'N12')] == 0)
                    modelo.AddAtMostOne(escala_vars[(p, d, t)] for t in turnos)

                # B) Interjornada de 11h / Regime 12x36
                for d in range(1, DIAS_MES):
                    trab_12_hoje = escala_vars[(p, d, 'D12')] + escala_vars[(p, d, 'N12')]
                    trab_amanha = sum(escala_vars[(p, d + 1, t)] for t in turnos)
                    modelo.Add(trab_12_hoje + trab_amanha <= 1)

                # C) Teto de 6 Dias Consecutivos (Art. 7º Norma SEI 2/2024)
                for d in range(1, DIAS_MES - 5):
                    dias_trab = sum(escala_vars[(p, d + i, t)] for i in range(7) for t in turnos)
                    modelo.Add(dias_trab <= 6)

                # D) Lei das Mulheres — Vedado 2 domingos consecutivos (ACT Cl. 24ª §1º)
                if prof['Sexo'] == 'Feminino':
                    for i in range(len(DOMINGOS) - 1):
                        d1, d2 = DOMINGOS[i], DOMINGOS[i + 1]
                        trab_d1 = sum(escala_vars[(p, d1, t)] for t in turnos)
                        trab_d2 = sum(escala_vars[(p, d2, t)] for t in turnos)
                        modelo.Add(trab_d1 + trab_d2 <= 1)

                # E) Pelo menos 1 final de semana completo de folga no mês (ACT Cl. 24ª)
                folgas_fds = []
                for i in range(len(SABADOS)):
                    sab, dom = SABADOS[i], DOMINGOS[i]
                    trab_fds = sum(escala_vars[(p, sab, t)] + escala_vars[(p, dom, t)] for t in turnos)
                    f_folga = modelo.NewBoolVar(f'folga_fds_{p}_{i}')
                    modelo.Add(trab_fds == 0).OnlyEnforceIf(f_folga)
                    modelo.Add(trab_fds > 0).OnlyEnforceIf(f_folga.Not())
                    folgas_fds.append(f_folga)
                if folgas_fds:
                    modelo.Add(sum(folgas_fds) >= 1)

            # 3. COBERTURA DIÁRIA OBRIGATÓRIA DA CLÍNICA MÉDICA (15º ANDAR)
            for d in dias:
                is_weekend = (d in FINAIS_DE_SEMANA)
                enf_diurnos = [p for p in range(num_profs) if df_profs.iloc[p]['Cargo'] == 'Enfermeiro' and df_profs.iloc[p]['Turno_Base'] == 'Diurno']
                tecs_diurnos = [p for p in range(num_profs) if df_profs.iloc[p]['Cargo'] == 'Técnico de Enfermagem' and df_profs.iloc[p]['Turno_Base'] == 'Diurno']
                enf_noturnos = [p for p in range(num_profs) if df_profs.iloc[p]['Cargo'] == 'Enfermeiro' and df_profs.iloc[p]['Turno_Base'] == 'Noturno']
                tecs_noturnos = [p for p in range(num_profs) if df_profs.iloc[p]['Cargo'] == 'Técnico de Enfermagem' and df_profs.iloc[p]['Turno_Base'] == 'Noturno']

                modelo.Add(sum(escala_vars[(p, d, 'M6')] for p in enf_diurnos) == 1)
                modelo.Add(sum(escala_vars[(p, d, 'M6')] for p in tecs_diurnos) == 1)
                
                req_enf_d12 = 3 if is_weekend else 5
                req_tec_d12 = 4 if is_weekend else 6
                
                modelo.Add(sum(escala_vars[(p, d, 'D12')] for p in enf_diurnos) == req_enf_d12)
                modelo.Add(sum(escala_vars[(p, d, 'D12')] for p in tecs_diurnos) == req_tec_d12)
                modelo.Add(sum(escala_vars[(p, d, 'N12')] for p in enf_noturnos) == 4)
                modelo.Add(sum(escala_vars[(p, d, 'N12')] for p in tecs_noturnos) == 3)

            # 4. PENALIDADES E OBJETIVO
            penalidades = []
            for p in range(num_profs):
                prof = df_profs.iloc[p]
                meta = 156 if prof['Carga_Semanal'] == '36h' else 176
                horas_mes = sum(escala_vars[(p, d, 'M6')] * 6 + escala_vars[(p, d, 'D12')] * 12 + escala_vars[(p, d, 'N12')] * 12 for d in dias)
                diff = modelo.NewIntVar(-40, 40, f'diff_{p}')
                modelo.Add(diff == horas_mes - meta)
                abs_diff = modelo.NewIntVar(0, 40, f'abs_diff_{p}')
                modelo.AddAbsEquality(abs_diff, diff)
                penalidades.append(abs_diff * 10)

            modelo.Minimize(sum(penalidades))
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 20.0
            status = solver.Solve(modelo)

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                rows = []
                for p in range(num_profs):
                    prof = df_profs.iloc[p]
                    cargo_sigla = "ENF" if prof['Cargo'] == 'Enfermeiro' else "TÉC"
                    meta = 156 if prof['Carga_Semanal'] == '36h' else 176
                    
                    # Recupera afastamentos que já estavam preenchidos
                    r_p_old = df_atual[df_atual['Nome'] == prof['Nome']].iloc[0]
                    
                    horas_trab = 0
                    r = {'ID': prof['ID'], 'Nome': prof['Nome'], 'Cargo': cargo_sigla, 'Meta': meta}
                    
                    for d in dias:
                        val_old = str(r_p_old[str(d)]).strip().upper()
                        if val_old in ['FE', 'AT', 'LM', 'LIC', 'FP']:
                            r[str(d)] = val_old
                        else:
                            t_val = ""
                            for t in turnos:
                                if solver.Value(escala_vars[(p, d, t)]) == 1:
                                    t_val = t
                                    horas_trab += HORAS_MAP[t]
                            r[str(d)] = t_val
                    
                    saldo = horas_trab - meta
                    r['Cumprida'] = horas_trab
                    r['Saldo'] = f"+{saldo}h" if saldo > 0 else (f"{saldo}h" if saldo < 0 else "0h")
                    rows.append(r)
                
                df_novos_dados = pd.DataFrame(rows)
                st.session_state['tabela_escala'] = df_novos_dados
                salvar_estado_disco(df_novos_dados, st.session_state['travas_celulas'])
                st.success("✅ Escala calculada com SUCESSO! Todas as travas manuais foram respeitadas e as regras da Ebserh/ACT cumpridas.")
            else:
                st.error("❌ ESCALA INVIÁVEL (INFEASIBLE): Não é matematicamente possível gerar a escala com as travas manuais atuais. Motivo provável: Excesso de atestados/licenças em determinado dia impedindo a cobertura mínima de 5 ENF ou 6 TÉC.")

    # TABELA EDITÁVEL COM ST.DATA_EDITOR
    st.markdown("#### ✏️ Editor de Plantões (Selecione o valor direto nas células)")
    st.info("Valores Permitidos: M6 (Manhã 6h) | D12 (Diurno 12h) | N12 (Noturno 12h) | FP (Folga Pedida) | FE (Férias) | AT (Atestado) | LM (Maternidade) | LIC (Licença) | Deixe em BRANCO para Folga de Escala")

    col_config = {
        "ID": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "Nome": st.column_config.TextColumn("Nome Profissional", disabled=True, width="medium"),
        "Cargo": st.column_config.TextColumn("Cargo", disabled=True, width="small"),
        "Meta": st.column_config.NumberColumn("Meta (h)", disabled=True, width="small"),
        "Cumprida": st.column_config.NumberColumn("Cumprida", disabled=True, width="small"),
        "Saldo": st.column_config.TextColumn("Saldo", disabled=True, width="small"),
    }
    
    for d in range(1, DIAS_MES + 1):
        col_config[str(d)] = st.column_config.SelectboxColumn(
            label=f"{d}",
            options=OPCOES_VALIDAS,
            width="small",
            required=False
        )

    df_editavel = st.data_editor(
        st.session_state['tabela_escala'],
        column_config=col_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="editor_escala"
    )

    # RECALCULO INSTANTÂNEO DE HORAS E VALIDAÇÃO DE ENTRADAS INVÁLIDAS
    erros_sintaxe = []
    erros_legais = []
    
    for idx, row in df_editavel.iterrows():
        p_nome = row['Nome']
        total_h = 0
        dias_consecutivos = 0
        
        for d in range(1, DIAS_MES + 1):
            val = str(row[str(d)]).strip().upper()
            if val not in OPCOES_VALIDAS:
                erros_sintaxe.append(f"⚠️ Código inválido '{val}' digitado no Dia {d} para {p_nome}. Utilize apenas códigos da legenda.")
            
            h = HORAS_MAP.get(val, 0)
            total_h += h
            
            # Validação de Dias Consecutivos (>6)
            if h > 0:
                dias_consecutivos += 1
                if dias_consecutivos > 6:
                    erros_legais.append(f"🚨 **{p_nome}**: Excede o limite legal de 6 dias consecutivos de trabalho ao redor do Dia {d}.")
            else:
                dias_consecutivos = 0
            
            # Validação de 12x36
            if d < DIAS_MES:
                val_prox = str(row[str(d+1)]).strip().upper()
                if val in ['D12', 'N12'] and val_prox in ['M6', 'D12', 'N12']:
                    erros_legais.append(f"🚨 **{p_nome}**: Quebra do descanso de 12x36 entre o Dia {d} ({val}) e o Dia {d+1} ({val_prox}).")

        meta = int(row['Meta'])
        saldo = total_h - meta
        df_editavel.at[idx, 'Cumprida'] = total_h
        df_editavel.at[idx, 'Saldo'] = f"+{saldo}h" if saldo > 0 else (f"{saldo}h" if saldo < 0 else "0h")

    st.session_state['tabela_escala'] = df_editavel
    salvar_estado_disco(df_editavel, st.session_state['travas_celulas'])

    # VISUALIZADOR FORMATADO COM PANDAS STYLER (MAPA DE CORES INTEIRAS)
    st.divider()
    st.markdown("#### 🎨 Matriz de Escala Visual (Mapa de Cores e Finais de Semana)")

    def estilar_escala(df):
        def estilar_celula(val):
            v = str(val).strip().upper()
            if v == 'FP':
                return 'background-color: #D4EDDA; color: #155724; font-weight: bold;'
            elif v == 'FE':
                return 'background-color: #FFF3CD; color: #856404; font-weight: bold;'
            elif v == 'AT':
                return 'background-color: #F8D7DA; color: #721C24; font-weight: bold;'
            elif v == 'LM':
                return 'background-color: #E2E0F8; color: #3832A0; font-weight: bold;'
            elif v == 'LIC':
                return 'background-color: #FFE8D6; color: #8A4B00; font-weight: bold;'
            elif v in ['M6', 'D12', 'N12']:
                return 'background-color: #E0F2FE; color: #0369A1; font-weight: bold;'
            return ''

        styler = df.style.map(estilar_celula, subset=[str(d) for d in range(1, DIAS_MES + 1)])
        return styler

    st.dataframe(
        estilar_escala(df_editavel),
        use_container_width=True,
        hide_index=True
    )

    # AUDITORIA E ALERTAS EM TEMPO REAL
    if erros_sintaxe or erros_legais:
        st.divider()
        st.markdown("### 🚨 Painel de Inconsistências & Alertas Regulatórios")
        for err in erros_sintaxe:
            st.warning(err)
        for err in erros_legais[:5]: # Exibe até 5 alertas prioritários
            st.error(err)
    else:
        st.success("✅ Nenhuma infração regulatória identificada nas alterações manuais ativas.")

# =============================================================================
# ABA 2: DASHBOARD DE INTELIGÊNCIA & DIMENSIONAMENTO (ALTA GESTÃO)
# =============================================================================
with aba_dashboard:
    st.markdown("### 📊 Dashboard de Inteligência Executiva & Dimensionamento")
    st.caption("Visão Consolidada para a Chefia de Divisão de Enfermagem e Diretoria da EBSERH / HC-UFG")

    df_atual = st.session_state['tabela_escala']

    # 1. CARDS DE KPIS EXECUTIVOS
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    total_at = sum((df_atual[str(d)] == 'AT').sum() for d in range(1, DIAS_MES + 1))
    total_fe = sum((df_atual[str(d)] == 'FE').sum() for d in range(1, DIAS_MES + 1))
    total_lm = sum((df_atual[str(d)] == 'LM').sum() for d in range(1, DIAS_MES + 1))
    total_lic = sum((df_atual[str(d)] == 'LIC').sum() for d in range(1, DIAS_MES + 1))
    total_fp = sum((df_atual[str(d)] == 'FP').sum() for d in range(1, DIAS_MES + 1))
    
    m1.metric("Equipe Total", len(df_atual))
    m2.metric("Atestados (AT)", f"{total_at} plantões")
    m3.metric("Férias (FE)", f"{total_fe} plantões")
    m4.metric("Maternidade (LM)", f"{total_lm} plantões")
    m5.metric("Licença Pessoal (LIC)", f"{total_lic} plantões")
    m6.metric("Folgas Pedidas (FP)", f"{total_fp} concedidas")

    st.divider()

    # 2. ANÁLISE COMPARATIVA DE COBERTURA DIÁRIA (PLANEJADO x REALIZADO)
    st.markdown("#### 📈 Cobertura Diária de Pessoal Ativo (Presentes no 15º Andar)")
    
    cobertura_enf_d12 = []
    cobertura_tec_d12 = []
    cobertura_noturna = []
    
    dias_list = [str(d) for d in range(1, DIAS_MES + 1)]
    
    for d in range(1, DIAS_MES + 1):
        d_str = str(d)
        enf_pres = ((df_atual['Cargo'] == 'ENF') & (df_atual[d_str].isin(['M6', 'D12']))).sum()
        tec_pres = ((df_atual['Cargo'] == 'TÉC') & (df_atual[d_str].isin(['M6', 'D12']))).sum()
        not_pres = (df_atual[d_str] == 'N12').sum()
        
        cobertura_enf_d12.append(enf_pres)
        cobertura_tec_d12.append(tec_pres)
        cobertura_noturna.append(not_pres)

    df_chart_cob = pd.DataFrame({
        "Dia do Mês": range(1, DIAS_MES + 1),
        "Enfermeiros Diurnos": cobertura_enf_d12,
        "Técnicos Diurnos": cobertura_tec_d12,
        "Equipe Noturna": cobertura_noturna
    }).set_index("Dia do Mês")

    st.bar_chart(df_chart_cob)

    # 3. BALANÇO DE BANCO DE HORAS E ABSENTEÍSMO NOMINAL
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("#### ⚖️ Distribuição do Saldo do Banco de Horas (ACT Cl. 22ª)")
        saldos_num = []
        for idx, row in df_atual.iterrows():
            s_str = str(row['Saldo']).replace('h', '').replace('+', '')
            saldos_num.append(int(s_str))
        
        df_saldos = pd.DataFrame({
            "Profissional": df_atual['Nome'],
            "Saldo (Horas)": saldos_num
        }).set_index("Profissional")
        
        st.bar_chart(df_saldos)

    with col_g2:
        st.markdown("#### 📋 Relatório Nominal de Ausências & Licenças")
        ausencias_rows = []
        for idx, row in df_atual.iterrows():
            nome = row['Nome']
            cargo = row['Cargo']
            
            fe_cnt = sum(1 for d in range(1, DIAS_MES + 1) if str(row[str(d)]) == 'FE')
            at_cnt = sum(1 for d in range(1, DIAS_MES + 1) if str(row[str(d)]) == 'AT')
            lm_cnt = sum(1 for d in range(1, DIAS_MES + 1) if str(row[str(d)]) == 'LM')
            lic_cnt = sum(1 for d in range(1, DIAS_MES + 1) if str(row[str(d)]) == 'LIC')
            
            total_aus = fe_cnt + at_cnt + lm_cnt + lic_cnt
            if total_aus > 0:
                ausencias_rows.append({
                    "Nome": nome,
                    "Cargo": cargo,
                    "Férias (FE)": f"{fe_cnt}d",
                    "Atestados (AT)": f"{at_cnt}d",
                    "Maternidade (LM)": f"{lm_cnt}d",
                    "Licenças (LIC)": f"{lic_cnt}d",
                    "Total Dias Afastado": total_aus
                })
        
        if ausencias_rows:
            st.dataframe(pd.DataFrame(ausencias_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum afastamento ou licença médica cadastrada no mês atual.")

    # 4. ANÁLISE COMPARATIVA: DIAS ÚTEIS x FINAIS DE SEMANA
    st.divider()
    st.markdown("#### 📊 Análise Comparativa de Carga Operacional")
    
    dias_uteis = [d for d in range(1, DIAS_MES + 1) if d not in FINAIS_DE_SEMANA]
    
    media_enf_util = float(np.mean([cobertura_enf_d12[d-1] for d in dias_uteis])) if dias_uteis else 0.0
    media_enf_fds = float(np.mean([cobertura_enf_d12[d-1] for d in FINAIS_DE_SEMANA])) if FINAIS_DE_SEMANA else 0.0
    
    media_tec_util = float(np.mean([cobertura_tec_d12[d-1] for d in dias_uteis])) if dias_uteis else 0.0
    media_tec_fds = float(np.mean([cobertura_tec_d12[d-1] for d in FINAIS_DE_SEMANA])) if FINAIS_DE_SEMANA else 0.0

    pct_red = (((media_enf_util - media_enf_fds) / media_enf_util) * 100.0) if media_enf_util > 0 else 0.0

    c_comp1, c_comp2, c_comp3 = st.columns(3)
    c_comp1.metric("Média Enf. (Dias Úteis)", f"{media_enf_util:.1f} profissionais/dia")
    c_comp2.metric("Média Enf. (Finais de Semana)", f"{media_enf_fds:.1f} profissionais/dia")
    c_comp3.metric("Redução Prevista no Fim de Semana", f"{pct_red:.1f}%")
