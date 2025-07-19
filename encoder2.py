import streamlit as st
import unicodedata
import json
import os

st.set_page_config(
    page_title="Sistema SZ",
    page_icon="images/bandeirasz.png",  # Pode ser um emoji ou caminho para um ícone
    layout="centered"  # (opcional) ou "wide"
)

def f(val):
    sum_div = 0
    for i in range(1, val + 1):
        if val % i == 0:
            sum_div += i
    return sum_div

t = [' '] + [chr(i) for i in range(ord('a'), ord('z')+1)]

def normalize(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.lower()

def encrypt_text(text):
    de = []
    en = []
    text = normalize(text)
    for c in text:
        if c in t:
            idx = t.index(c)
            de.append(t[idx])
            num = len(de)
            en.append(t[(idx + f(num)) % 27])
    return ''.join(en)

def decrypt_text(text):
    de = []
    en = []
    text = normalize(text)
    for c in text:
        if c in t:
            idx = t.index(c)
            en.append(t[idx])
            num = len(en)
            de.append(t[(idx + 54 - f(num)) % 27])
    return ''.join(de)

# Gerenciamento de usuários

def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Página de login

def login_page():
    st.title("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        users = load_users()
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["name"] = users[username]["name"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

# Página Home

def home_page():
    st.header("Home")

    st.write(f"Bem-vindo, **{st.session_state.get('name', 'Usuário')}**!")
    st.write("Use o menu lateral para acessar as funcionalidades do Sistema Schmerzen")

# Página Encriptador

def encoder_page():
    st.header("🔐 Encriptador / Decriptador")

    mode = st.radio("Escolha o modo:", ("Encriptar", "Decriptar"))

    input_text = st.text_area("Digite o texto:")

    if st.button("Executar"):
        if mode == "Encriptar":
            result = encrypt_text(input_text)
            st.success("Texto Encriptado:")
            st.code(result)
        else:
            result = decrypt_text(input_text)
            st.success("Texto Decriptado:")
            st.code(result)

# Página Usuários

def users_page():
    st.header("👥 Gerenciar Usuários")

    users = load_users()
    st.subheader("Usuários cadastrados:")

    for user in users:
        col1, col2, col3 = st.columns([3,3,1])
        col1.write(f"**Usuário:** {user}")
        col2.write(f"**Nome:** {users[user]['name']}")
        if col3.button("Excluir", key=f"del_{user}"):
            if user == st.session_state["username"]:
                st.error("Você não pode excluir a si mesmo.")
            else:
                users.pop(user)
                save_users(users)
                st.success(f"Usuário '{user}' removido com sucesso!")
                st.rerun()

    st.subheader("Adicionar novo usuário")
    new_user = st.text_input("Login")
    new_name = st.text_input("Nome")
    new_pass = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        if new_user in users:
            st.error("Usuário já existe.")
        elif new_user == "" or new_pass == "" or new_name == "":
            st.error("Preencha todos os campos corretamente.")
        else:
            users[new_user] = {"name": new_name, "password": new_pass}
            save_users(users)
            st.success(f"Usuário '{new_user}' cadastrado com sucesso!")
            st.rerun()

# Controle principal

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    # Sidebar de navegação
    st.sidebar.title(f"Olá, {st.session_state.get('name', 'Usuário')}")
    page = st.sidebar.radio("Navegação", ["Home", "Encriptador", "Usuários"])

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # Renderiza a página escolhida
    if page == "Home":
        home_page()
    elif page == "Encriptador":
        encoder_page()
    elif page == "Usuários":
        users_page()
else:
    login_page()