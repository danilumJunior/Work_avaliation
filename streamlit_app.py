import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(
    page_title="Minhas Avaliações",
    page_icon="📚",
    layout="wide"
)

# =========================
# CONEXÃO COM SUPABASE
# =========================

@st.cache_resource
def conectar_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

supabase = conectar_supabase()


# =========================
# SESSION STATE
# =========================

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None


# =========================
# FUNÇÕES DE AUTENTICAÇÃO
# =========================

def login(email, senha):
    try:
        resposta = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })

        st.session_state.usuario = resposta.user
        st.session_state.access_token = resposta.session.access_token

        st.success("Login realizado com sucesso!")
        st.rerun()

    except Exception as erro:
        st.error("Erro ao fazer login. Verifique seu e-mail e senha.")
        st.write(erro)


def cadastrar_usuario(email, senha):
    try:
        supabase.auth.sign_up({
            "email": email,
            "password": senha
        })

        st.success("Cadastro realizado! Verifique seu e-mail, se a confirmação estiver ativada.")

    except Exception as erro:
        st.error("Erro ao cadastrar usuário.")
        st.write(erro)


def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass

    st.session_state.usuario = None
    st.session_state.access_token = None
    st.success("Você saiu da conta.")
    st.rerun()


def usuario_logado():
    return st.session_state.usuario is not None


# =========================
# FUNÇÕES CRUD
# =========================

def listar_obras():
    try:
        resposta = (
            supabase
            .table("obras")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return resposta.data

    except Exception as erro:
        st.error("Erro ao buscar obras.")
        st.write(erro)
        return []


def inserir_obra(titulo, tipo, autor_diretor, genero, ano, nota, critica, capa_url):
    try:
        user_id = st.session_state.usuario.id

        dados = {
            "titulo": titulo,
            "tipo": tipo,
            "autor_diretor": autor_diretor,
            "genero": genero,
            "ano": ano,
            "nota": nota,
            "critica": critica,
            "capa_url": capa_url,
            "user_id": user_id
        }

        supabase.table("obras").insert(dados).execute()
        st.success("Obra cadastrada com sucesso!")
        st.rerun()

    except Exception as erro:
        st.error("Erro ao cadastrar obra.")
        st.write(erro)


def atualizar_obra(id_obra, titulo, tipo, autor_diretor, genero, ano, nota, critica, capa_url):
    try:
        dados = {
            "titulo": titulo,
            "tipo": tipo,
            "autor_diretor": autor_diretor,
            "genero": genero,
            "ano": ano,
            "nota": nota,
            "critica": critica,
            "capa_url": capa_url
        }

        supabase.table("obras").update(dados).eq("id", id_obra).execute()
        st.success("Obra atualizada com sucesso!")
        st.rerun()

    except Exception as erro:
        st.error("Erro ao atualizar obra.")
        st.write(erro)


def excluir_obra(id_obra):
    try:
        supabase.table("obras").delete().eq("id", id_obra).execute()
        st.success("Obra excluída com sucesso!")
        st.rerun()

    except Exception as erro:
        st.error("Erro ao excluir obra.")
        st.write(erro)


# =========================
# SIDEBAR
# =========================

st.sidebar.title("📚 Avaliador")

menu = st.sidebar.radio(
    "Menu",
    ["Início", "Login", "Cadastrar obra", "Gerenciar obras", "Ranking"]
)

if usuario_logado():
    st.sidebar.success(f"Logado como: {st.session_state.usuario.email}")

    if st.sidebar.button("Sair"):
        logout()
else:
    st.sidebar.warning("Você não está logado.")


# =========================
# PÁGINA INÍCIO
# =========================

if menu == "Início":
    st.title("📚🎬 Minhas avaliações de livros e filmes")

    obras = listar_obras()

    if not obras:
        st.info("Nenhuma obra cadastrada ainda.")
    else:
        filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "Livro", "Filme"])

        if filtro_tipo != "Todos":
            obras = [obra for obra in obras if obra["tipo"] == filtro_tipo]

        busca = st.text_input("Pesquisar por título")

        if busca:
            obras = [
                obra for obra in obras
                if busca.lower() in obra["titulo"].lower()
            ]

        for obra in obras:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])

                with col1:
                    if obra.get("capa_url"):
                        st.image(obra["capa_url"], width=130)
                    else:
                        st.write("Sem capa")

                with col2:
                    st.subheader(obra["titulo"])
                    st.write(f"**Tipo:** {obra['tipo']}")
                    st.write(f"**Autor/Diretor:** {obra.get('autor_diretor') or 'Não informado'}")
                    st.write(f"**Gênero:** {obra.get('genero') or 'Não informado'}")
                    st.write(f"**Ano:** {obra.get('ano') or 'Não informado'}")
                    st.write(f"**Nota:** ⭐ {obra.get('nota')}/10")
                    st.write("**Crítica:**")
                    st.write(obra.get("critica") or "Sem crítica.")


# =========================
# PÁGINA LOGIN
# =========================

elif menu == "Login":
    st.title("🔐 Login")

    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

    with aba_login:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        if st.button("Entrar"):
            if email and senha:
                login(email, senha)
            else:
                st.warning("Preencha e-mail e senha.")

    with aba_cadastro:
        novo_email = st.text_input("Novo e-mail", key="cadastro_email")
        nova_senha = st.text_input("Nova senha", type="password", key="cadastro_senha")

        if st.button("Criar conta"):
            if novo_email and nova_senha:
                cadastrar_usuario(novo_email, nova_senha)
            else:
                st.warning("Preencha e-mail e senha.")


# =========================
# PÁGINA CADASTRAR OBRA
# =========================

elif menu == "Cadastrar obra":
    st.title("➕ Cadastrar nova obra")

    if not usuario_logado():
        st.warning("Você precisa estar logado para cadastrar uma obra.")
    else:
        with st.form("form_cadastro"):
            titulo = st.text_input("Título")
            tipo = st.selectbox("Tipo", ["Livro", "Filme"])
            autor_diretor = st.text_input("Autor ou diretor")
            genero = st.text_input("Gênero")
            ano = st.number_input("Ano", min_value=0, max_value=2100, step=1)
            nota = st.slider("Nota", 0.0, 10.0, 5.0, 0.5)
            capa_url = st.text_input("URL da capa")
            critica = st.text_area("Crítica", height=180)

            enviar = st.form_submit_button("Cadastrar")

            if enviar:
                if not titulo:
                    st.warning("O título é obrigatório.")
                else:
                    inserir_obra(
                        titulo,
                        tipo,
                        autor_diretor,
                        genero,
                        ano,
                        nota,
                        critica,
                        capa_url
                    )


# =========================
# PÁGINA GERENCIAR OBRAS
# =========================

elif menu == "Gerenciar obras":
    st.title("⚙️ Gerenciar obras")

    if not usuario_logado():
        st.warning("Você precisa estar logado para editar ou excluir obras.")
    else:
        obras = listar_obras()

        minhas_obras = [
            obra for obra in obras
            if obra.get("user_id") == st.session_state.usuario.id
        ]

        if not minhas_obras:
            st.info("Você ainda não cadastrou nenhuma obra.")
        else:
            opcoes = {
                f"{obra['titulo']} - {obra['tipo']}": obra
                for obra in minhas_obras
            }

            selecionada = st.selectbox("Escolha uma obra", list(opcoes.keys()))
            obra = opcoes[selecionada]

            st.divider()
            st.subheader("Editar obra")

            with st.form("form_edicao"):
                titulo = st.text_input("Título", value=obra["titulo"])
                tipo = st.selectbox(
                    "Tipo",
                    ["Livro", "Filme"],
                    index=0 if obra["tipo"] == "Livro" else 1
                )
                autor_diretor = st.text_input(
                    "Autor ou diretor",
                    value=obra.get("autor_diretor") or ""
                )
                genero = st.text_input(
                    "Gênero",
                    value=obra.get("genero") or ""
                )
                ano = st.number_input(
                    "Ano",
                    min_value=0,
                    max_value=2100,
                    step=1,
                    value=obra.get("ano") or 0
                )
                nota = st.slider(
                    "Nota",
                    0.0,
                    10.0,
                    float(obra.get("nota") or 0),
                    0.5
                )
                capa_url = st.text_input(
                    "URL da capa",
                    value=obra.get("capa_url") or ""
                )
                critica = st.text_area(
                    "Crítica",
                    value=obra.get("critica") or "",
                    height=180
                )

                salvar = st.form_submit_button("Salvar alterações")

                if salvar:
                    atualizar_obra(
                        obra["id"],
                        titulo,
                        tipo,
                        autor_diretor,
                        genero,
                        ano,
                        nota,
                        critica,
                        capa_url
                    )

            st.divider()

            if st.button("Excluir obra", type="primary"):
                excluir_obra(obra["id"])


# =========================
# PÁGINA RANKING
# =========================

elif menu == "Ranking":
    st.title("🏆 Ranking das melhores obras")

    obras = listar_obras()

    if not obras:
        st.info("Nenhuma obra cadastrada.")
    else:
        df = pd.DataFrame(obras)

        df = df[["titulo", "tipo", "genero", "ano", "nota"]]
        df = df.sort_values(by="nota", ascending=False)

        st.dataframe(df, use_container_width=True)

        st.subheader("Top 5")
        top_5 = df.head(5)

        for index, obra in top_5.iterrows():
            st.write(f"⭐ **{obra['titulo']}** — {obra['nota']}/10")
