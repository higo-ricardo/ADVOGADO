"""
ui/pages.py — As 6 telas do fluxo do agente jurídico.
Cada função render_* corresponde a uma etapa do state machine.
"""
import traceback

import streamlit as st
from core.state_machine import Etapa
from core.router import detectar_dominio, codigos_do_dominio, campos_do_codigo, is_autonomo
from ui.components import card_info, badge_codigo, checklist_visual, alerta_erro
from ui.adapters import get_adapter, get_state_machine
from utils import export


# ---------------------------------------------------------------------------
# ETAPA 1 — Triagem: usuário descreve o caso
# ---------------------------------------------------------------------------

def render_triagem():
    st.subheader("Descreva o caso")
    st.caption("Escreva livremente. O sistema identificará o tipo de peça adequada.")

    with st.form("form_triagem"):
        descricao = st.text_area(
            "O que aconteceu?",
            height=160,
            placeholder=(
                "Ex: Meu cliente foi esbulhado de sua propriedade rural há 3 meses. "
                "O invasor entrou de madrugada e não quer sair..."
            ),
            value=get_state_machine().get("descricao_caso", ""),
        )
        enviado = st.form_submit_button("Analisar caso →", type="primary", use_container_width=True)

    if enviado:
        if len(descricao.strip()) < 20:
            alerta_erro("Descreva o caso com mais detalhes (mínimo 20 caracteres).")
            return

        get_state_machine().set("descricao_caso", descricao)

        resultado = detectar_dominio(descricao)
        if resultado:
            dom_id, dom_nome = resultado
            get_state_machine().set("dominio", dom_id)
            get_state_machine().set("dominio_nome", dom_nome)

        get_state_machine().avancar(Etapa.CONFIRMACAO)
        st.rerun()


# ---------------------------------------------------------------------------
# ETAPA 2 — Confirmação: usuário confirma domínio e código
# ---------------------------------------------------------------------------

def render_confirmacao():
    st.subheader("Confirme o tipo de peça")

    descricao = get_state_machine().get("descricao_caso")
    dom_id    = get_state_machine().get("dominio")
    dom_nome  = get_state_machine().get("dominio_nome")

    # Mostra o caso resumido
    with st.expander("[Caso] Caso descrito", expanded=False):
        st.write(descricao)

    # Seleção de domínio
    dominios_opcoes = {
        "A — Imobiliário":                 "A",
        "B — Consumerista / JEC":          "B",
        "C — Cível":                       "C",
        "D — Documentos e Apoio":          "D",
        "F — Família e Sucessões":         "F",
        "G — Remédios Constitucionais":    "G",
        "R — Recursos Cíveis":             "R",
    }

    # Tenta pré-selecionar o domínio detectado automaticamente
    idx_default = 0
    if dom_id:
        for i, (label, did) in enumerate(dominios_opcoes.items()):
            if did == dom_id:
                idx_default = i
                break
        card_info("Domínio detectado automaticamente", f"{dom_id} — {dom_nome}", "green")

    with st.form("form_confirmacao"):
        dominio_sel = st.selectbox(
            "Domínio jurídico",
            options=list(dominios_opcoes.keys()),
            index=idx_default,
        )
        dom_id_sel = dominios_opcoes[dominio_sel]

        # Códigos disponíveis para o domínio selecionado
        codigos = codigos_do_dominio(dom_id_sel)
        codigos_labels = [f"{cod} — {nome}" for cod, nome in codigos]

        codigo_sel_label = st.selectbox("Tipo de peça", options=codigos_labels)

        confirmado = st.form_submit_button("Confirmar e prosseguir →", type="primary", use_container_width=True)
        voltar     = st.form_submit_button("← Voltar")

    if voltar:
        get_state_machine().avancar(Etapa.TRIAGEM)
        st.rerun()

    if confirmado:
        cod, nome_cod = codigos[codigos_labels.index(codigo_sel_label)]
        dom_label = dominio_sel.split(" — ", 1)

        get_state_machine().set("dominio",      dom_id_sel)
        get_state_machine().set("dominio_nome", dom_label[1] if len(dom_label) > 1 else dominio_sel)
        get_state_machine().set("codigo_peca",  cod)
        get_state_machine().set("codigo_nome",  nome_cod)
        get_state_machine().set("modo", "autonomo" if is_autonomo(cod) else "integrado")

        get_state_machine().avancar(Etapa.COLETA)
        st.rerun()


# ---------------------------------------------------------------------------
# ETAPA 3 — Coleta: campos obrigatórios por código de peça
# ---------------------------------------------------------------------------

def render_coleta():
    codigo    = get_state_machine().get("codigo_peca")
    cod_nome  = get_state_machine().get("codigo_nome")
    dom_nome  = get_state_machine().get("dominio_nome")

    st.subheader("Dados do caso")
    badge_codigo(codigo, cod_nome)
    st.caption(f"Domínio: {dom_nome}")

    campos = campos_do_codigo(codigo)
    dados_anteriores = get_state_machine().get("dados_coletados", {})

    with st.form("form_coleta"):
        valores: dict = {}

        for campo in campos:
            cid    = campo["id"]
            label  = campo["label"] + " *"
            tipo   = campo.get("tipo", "text")
            val    = dados_anteriores.get(cid, "")

            if tipo == "textarea":
                valores[cid] = st.text_area(label, value=val, height=100, key=f"campo_{cid}")
            elif tipo == "select":
                opcoes = campo.get("opcoes", [])
                idx = opcoes.index(val) if val in opcoes else 0
                valores[cid] = st.selectbox(label, options=opcoes, index=idx, key=f"campo_{cid}")
            else:
                valores[cid] = st.text_input(label, value=val, key=f"campo_{cid}")

        col1, col2 = st.columns(2)
        with col1:
            voltar = st.form_submit_button("<- Voltar")
        with col2:
            avancar = st.form_submit_button("Gerar briefing ->", type="primary", use_container_width=True)

    if voltar:
        get_state_machine().avancar(Etapa.CONFIRMACAO)
        st.rerun()

    if avancar:
        # Valida campos obrigatórios
        faltando = [
            campos[i]["label"]
            for i, c in enumerate(campos)
            if c.get("tipo") != "select" and not valores.get(c["id"], "").strip()
        ]
        if faltando:
            alerta_erro(f"Preencha os campos: {', '.join(faltando)}")
            return

        get_state_machine().set("dados_coletados", valores)
        get_state_machine().avancar(Etapa.CONTRATO)
        st.rerun()


# ---------------------------------------------------------------------------
# ETAPA 4 — Contrato: gera e exibe o briefing para aprovação
# ---------------------------------------------------------------------------

def render_contrato():
    st.subheader("Briefing do caso")
    st.caption("O sistema preparou o briefing abaixo. Revise antes de gerar a peça.")

    codigo    = get_state_machine().get("codigo_peca")
    cod_nome  = get_state_machine().get("codigo_nome")
    dom_id    = get_state_machine().get("dominio")
    dom_nome  = get_state_machine().get("dominio_nome")
    dados     = get_state_machine().get("dados_coletados", {})
    modo      = get_state_machine().get("modo")
    contrato_existente = get_state_machine().get("contrato", {})

    # Gera o contrato apenas uma vez
    if not contrato_existente:
        with st.spinner("Preparando briefing..."):
            try:
                contrato = get_adapter().gerar_contrato(
                    descricao_caso=get_state_machine().get("descricao_caso"),
                    dominio=dom_id,
                    dominio_nome=dom_nome,
                    codigo=codigo,
                    codigo_nome=cod_nome,
                    dados_coletados=dados,
                    modo=modo,
                )
                get_state_machine().set("contrato", contrato)
            except Exception as e:
                import traceback; traceback.print_exc()
                erro_str = str(e).encode("utf-8", errors="replace").decode("utf-8", errors="replace")
                alerta_erro(f"Erro ao gerar briefing: {erro_str}")
                return
        st.rerun()

    contrato = get_state_machine().get("contrato")

    # Exibe o contrato de forma amigável
    badge_codigo(codigo, cod_nome)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Escopo**")
        st.info(contrato.get("escopo", "—"))
    with col2:
        st.markdown("**Modo de operação**")
        modo_label = "Autônomo (direto)" if modo == "autonomo" else "Integrado (advogado + estagiário)"
        st.info(modo_label)

        st.markdown("**Pedidos identificados**")
        for pedido in contrato.get("pedidos", []):
            st.markdown(f"- {pedido}")

    st.markdown("**Criterios de aceite**")
    for criterio in contrato.get("criterios_aceite", []):
        st.markdown(f"- {criterio}")

    if contrato.get("regras_criticas"):
        st.markdown("**Regras criticas para este tipo de peça**")
        for regra in contrato.get("regras_criticas", []):
            st.warning(regra)

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("<- Voltar"):
            get_state_machine().set("contrato", {})
            get_state_machine().avancar(Etapa.COLETA)
            st.rerun()
    with col2:
        if st.button("Refazer briefing"):
            get_state_machine().set("contrato", {})
            st.rerun()
    with col3:
        if st.button("Gerar peça agora ->", type="primary", use_container_width=True):
            get_state_machine().avancar(Etapa.GERACAO)
            st.rerun()


# ---------------------------------------------------------------------------
# ETAPA 5 — Geração: streaming da peça pelo estagiário
# ---------------------------------------------------------------------------

def render_geracao():
    st.subheader("Gerando a peça processual")

    codigo   = get_state_machine().get("codigo_peca")
    cod_nome = get_state_machine().get("codigo_nome")
    contrato = get_state_machine().get("contrato")

    badge_codigo(codigo, cod_nome)
    st.caption("A peça está sendo redigida. Aguarde...")

    peca_existente = get_state_machine().get("peca_gerada", "")

    if not peca_existente:
        container = st.empty()
        peca_completa = ""

        try:
            with st.spinner("Estagiário redigindo..."):
                stream = get_adapter().estagiario_redigir(contrato, codigo)
                buffer = ""
                for chunk in stream:
                    buffer += chunk
                    container.markdown(buffer)
                peca_completa = buffer
        except Exception as e:
            alerta_erro(f"Erro na geração: {e}")
            if st.button("Tentar novamente"):
                st.rerun()
            return

        get_state_machine().set("peca_gerada", peca_completa)
        get_state_machine().avancar(Etapa.REVISAO)
        st.rerun()
    else:
        get_state_machine().avancar(Etapa.REVISAO)
        st.rerun()


# ---------------------------------------------------------------------------
# ETAPA 6 — Revisão: checklist + delta + download
# ---------------------------------------------------------------------------

def render_revisao():
    st.subheader("Revisão e download")

    codigo    = get_state_machine().get("codigo_peca")
    cod_nome  = get_state_machine().get("codigo_nome")
    contrato  = get_state_machine().get("contrato", {})
    peca      = get_state_machine().get("peca_gerada", "")
    dados     = get_state_machine().get("dados_coletados", {})

    badge_codigo(codigo, cod_nome)

    # Tabs: peça | checklist | delta
    tab_peca, tab_check, tab_delta = st.tabs(["Peca", "Checklist", "Solicitar ajuste"])

    with tab_peca:
        # Separa o corpo da peça do checklist/pendências
        corpo = peca.split("## CHECKLIST")[0].strip()
        st.markdown(corpo)

    with tab_check:
        criterios = contrato.get("criterios_aceite", [])
        if criterios:
            st.markdown("**Critérios de aceite verificados:**")
            checklist_visual(criterios)
        else:
            st.info("Nenhum critério de aceite registrado no contrato.")

        # Exibe pendências se houver [A PREENCHER]
        pendencias = [l.strip() for l in peca.split("\n") if "[A PREENCHER]" in l]
        if pendencias:
            st.warning(f"⚠️ {len(pendencias)} campo(s) precisam ser preenchidos manualmente:")
            for p in pendencias:
                st.markdown(f"• `{p}`")

    with tab_delta:
        st.caption("Solicite uma alteração pontual sem reescrever a peça inteira.")
        instrucao = st.text_area(
            "O que deve ser alterado?",
            placeholder="Ex: No 3º parágrafo, adicione referência ao art. 927 do CC. / Corrija o nome do réu para João da Silva.",
            height=100,
        )
        if st.button("Aplicar ajuste", type="primary"):
            if instrucao.strip():
                nova_peca = ""
                with st.spinner("Aplicando delta..."):
                    stream = get_adapter().advogado_delta(peca, instrucao, contrato)
                    nova_peca = st.write_stream(stream)
                get_state_machine().set("peca_gerada", nova_peca)
                st.success("Ajuste aplicado!")
                st.rerun()
            else:
                st.warning("Descreva o ajuste desejado.")

    st.divider()

    # Download
    st.markdown("**📥 Baixar peça**")
    col1, col2 = st.columns(2)

    with col1:
        # Download como .txt (sempre disponível)
        autor = dados.get("autor", dados.get("requerente", dados.get("exequente", "parte")))
        nome_txt = export.nome_arquivo_peca(codigo, autor).replace(".docx", ".txt")
        st.download_button(
            label="⬇️ Baixar como .txt",
            data=peca.encode("utf-8"),
            file_name=nome_txt,
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        # Download como .docx (requer python-docx)
        if export.DOCX_DISPONIVEL:
            try:
                docx_bytes = export.gerar_docx(peca, codigo)
                nome_docx  = export.nome_arquivo_peca(codigo, autor)
                st.download_button(
                    label="⬇️ Baixar como .docx",
                    data=docx_bytes,
                    file_name=nome_docx,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro ao gerar .docx: {e}")
        else:
            st.info("Para download em .docx, instale: `pip install python-docx`")

    st.divider()
    if st.button("🆕 Novo caso", use_container_width=True):
        get_state_machine().reiniciar()
        st.rerun()
