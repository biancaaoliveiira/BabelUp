import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import re
from datetime import datetime, timedelta
import sqlite3


COR_FUNDO = "#fff8ee"
COR_AZUL = "#1d4a8b"
COR_CINZA = "#d9d9d9"
COR_BOTAO_MENU = "#2a5eb2"
COR_PROVA = "#ff9800"


def conectar():
    return sqlite3.connect("babelup.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT, telefone TEXT, 
        email TEXT, senha TEXT, idiomas_contratados TEXT, plano TEXT, nivel TEXT, 
        data_pagamento TEXT, status_curso TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, idiomas TEXT, 
        plano TEXT, valor REAL, metodo TEXT, vencimento TEXT)''')
    conn.commit()
    conn.close()

class BabelUpApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BabelUp Professional")
        self.root.geometry("500x850")
        self.root.configure(bg=COR_FUNDO)

        self.style = ttk.Style()
        self.style.configure("BotaoVoltar.TButton", font=("Arial", 9, "bold"))

        self.estilo_entry = {"bd": 0, "highlightthickness": 1, "highlightbackground": COR_CINZA,
                             "highlightcolor": COR_AZUL, "font": ("Arial", 11)}

        self.user_data = {}
        self.niveis_por_idioma = {}
        self.aulas_concluidas = []

        self.aulas_por_nivel = {
            "Iniciante": ["Saudações", "Alfabeto", "Números", "Cores", "Família", "Verbo To Be", "Dias da Semana", "Meses", "Clima", "Simulado Inicial"],
            "Básico": ["Presente Simples", "Rotina", "Preposições", "No Mercado", "Roupas", "Habilidades", "Sentimentos", "Direções", "Passado Intro", "Simulado Básico"],
            "Intermediário": ["Passado Contínuo", "Comparativos", "Viagens", "Futuro", "Trabalho", "Saúde", "Voz Passiva", "Culinária", "Expressões", "Simulado Inter"],
            "Avançado": ["Present Perfect", "Modais", "Debates", "Literatura", "Phrasal Verbs", "Cultura", "Gírias", "Redação", "História", "Exame Final"]
        }

        criar_tabelas()
        self.tela_login()

    def _configurar_scroll_mouse(self, canvas):
        canvas.bind('<Enter>', lambda _: canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas)))
        canvas.bind('<Leave>', lambda _: canvas.unbind_all("<MouseWheel>"))

    def limpar(self):
        for w in self.root.winfo_children(): w.destroy()
        self.container = tk.Frame(self.root, bg=COR_FUNDO)
        self.container.pack(expand=True, fill="both")

    def carregar_logo(self, tamanho=(250, 250)):
        try:
            img = Image.open("logo1.png")
            img = img.resize(tamanho, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            return None

    def validar_apenas_letras(self, P):
        return True if P == "" or re.match(r"^[A-Za-zÀ-ÿ\s]+$", P) else False

    def masc_cartao(self, event):
        v = re.sub(r"\D", "", event.widget.get())[:16]
        v = " ".join([v[i:i + 4] for i in range(0, len(v), 4)])
        event.widget.delete(0, tk.END)
        event.widget.insert(0, v)

    def masc_validade(self, event):
        v = re.sub(r"\D", "", event.widget.get())[:4]
        if len(v) > 2: v = f"{v[:2]}/{v[2:]}"
        event.widget.delete(0, tk.END)
        event.widget.insert(0, v)

    def masc_cvv(self, event):
        v = re.sub(r"\D", "", event.widget.get())[:3]
        event.widget.delete(0, tk.END)
        event.widget.insert(0, v)

    def tela_login(self):
        self.limpar()
        self.root.geometry("500x850")

        frame_login = tk.Frame(self.container, bg=COR_FUNDO)
        frame_login.place(relx=0.5, rely=0.45, anchor="center")

        logo = self.carregar_logo()
        if logo:
            lb = tk.Label(frame_login, image=logo, bg=COR_FUNDO)
            lb.image = logo
            lb.pack(pady=(30, 5))

        tk.Label(frame_login, text="LOGIN", font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(pady=(0, 10))

        tk.Label(frame_login, text="E-MAIL", font=("Arial", 9, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(anchor="w",
                                                                                                        padx=10)
        self.ent_e = tk.Entry(frame_login, width=35, **self.estilo_entry)
        self.ent_e.pack(pady=(2, 8), padx=10, ipady=5)

        tk.Label(frame_login, text="SENHA", font=("Arial", 9, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(anchor="w",
                                                                                                       padx=10)
        self.ent_s = tk.Entry(frame_login, show="*", width=35, **self.estilo_entry)
        self.ent_s.pack(pady=(2, 12), padx=10, ipady=5)

        tk.Button(frame_login, text="ENTRAR", bg=COR_AZUL, fg="white", font=("Arial", 11, "bold"), width=30, height=2,
                  relief="flat", cursor="hand2", command=self.logar).pack(pady=(10, 5))

        tk.Button(frame_login, text="Esqueceu a senha?", bg=COR_FUNDO, fg=COR_AZUL, bd=0,
                  font=("Arial", 9, "underline"),
                  cursor="hand2", command=self.janela_esqueceu_senha).pack(pady=5)

        tk.Button(frame_login, text="CRIAR NOVA CONTA", bg=COR_FUNDO, fg=COR_AZUL, bd=0, font=("Arial", 10, "bold"),
                  cursor="hand2", command=self.tela_cadastro).pack(pady=8)

    def janela_esqueceu_senha(self):
        self.janela_esq = tk.Toplevel(self.root)
        self.janela_esq.title("Recuperar Senha")
        self.janela_esq.geometry("350x300")
        self.janela_esq.configure(bg=COR_FUNDO)
        self.janela_esq.grab_set()

        tk.Label(self.janela_esq, text="RECUPERAÇÃO", font=("Arial", 16, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            pady=20)
        tk.Label(self.janela_esq, text="Digite o e-mail cadastrado:", bg=COR_FUNDO, font=("Arial", 10)).pack(pady=5)

        self.ent_email_esq = tk.Entry(self.janela_esq, width=30, **self.estilo_entry)
        self.ent_email_esq.pack(pady=5, ipady=5)

        tk.Button(self.janela_esq, text="ENVIAR CÓDIGO", bg=COR_AZUL, fg="white", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", command=self.verificar_email_esqueci).pack(pady=15, ipady=5, ipadx=10)

    def verificar_email_esqueci(self):
        email_digitado = self.ent_email_esq.get().strip()
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT senha FROM usuarios WHERE email=?", (email_digitado,))
        resultado = c.fetchone()
        conn.close()

        if resultado:
            senha_recuperada = resultado[0]
            messagebox.showinfo("BabelUp", "Um código de verificação foi enviado para o seu e-mail (Fictício).")
            for w in self.janela_esq.winfo_children(): w.destroy()

            tk.Label(self.janela_esq, text="CÓDIGO DE VERIFICAÇÃO", font=("Arial", 14, "bold"), bg=COR_FUNDO,
                     fg=COR_AZUL).pack(pady=20)
            tk.Label(self.janela_esq, text="Digite o código (123456):", bg=COR_FUNDO, font=("Arial", 10)).pack(pady=5)

            ent_codigo = tk.Entry(self.janela_esq, width=15, justify="center", font=("Arial", 14, "bold"), bd=0,
                                  highlightthickness=1)
            ent_codigo.pack(pady=10, ipady=5)

            def validar_codigo():
                if ent_codigo.get().strip() == "123456":
                    messagebox.showinfo("Sucesso", f"Sua senha é:\n\n{senha_recuperada}")
                    self.janela_esq.destroy()
                else:
                    messagebox.showerror("Erro", "Código incorreto! Tente novamente.")

            tk.Button(self.janela_esq, text="VERIFICAR CÓDIGO", bg=COR_AZUL, fg="white", font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2", command=validar_codigo).pack(pady=15, ipady=5, ipadx=10)
        else:
            messagebox.showerror("Erro", "E-mail não encontrado no sistema.")

    def logar(self):
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (self.ent_e.get(), self.ent_s.get()))
        u = c.fetchone()
        conn.close()
        if u:
            self.user_data = dict(zip([d[0] for d in c.description], u))
            idiomas = [i for i in str(self.user_data.get('idiomas_contratados', '')).split(', ') if i]
            niveis_salvos = str(self.user_data.get('nivel', '')).split('|')
            self.niveis_por_idioma = {}
            for item in niveis_salvos:
                if ":" in item:
                    idioma, nv = item.split(":")
                    self.niveis_por_idioma[idioma] = nv
            for idm in idiomas:
                if idm not in self.niveis_por_idioma: self.niveis_por_idioma[idm] = "Iniciante"
            self.dashboard_aulas()
        else:
            messagebox.showerror("Erro", "Login Inválido.")

    def tela_cadastro(self):
        import re
        for w in self.root.winfo_children(): w.destroy()

        f_cad = tk.Frame(self.root, bg=COR_FUNDO)
        f_cad.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f_cad, text="CRIAR CONTA", font=("Arial", 20, "bold"),
                 bg=COR_FUNDO, fg=COR_AZUL).pack(pady=(0, 20))

        def criar_campo(texto_label, is_senha=False):
            tk.Label(f_cad, text=texto_label, font=("Arial", 9, "bold"),
                     bg=COR_FUNDO, fg=COR_AZUL).pack(anchor="w")
            entrada = tk.Entry(f_cad, width=35, font=("Arial", 11), relief="solid", bd=1)
            if is_senha: entrada.config(show="*")
            entrada.pack(pady=(0, 15), ipady=3)
            return entrada

        self.ent_nome = criar_campo("NOME COMPLETO")
        self.ent_cpf = criar_campo("CPF")
        self.ent_telefone = criar_campo("TELEFONE")
        self.ent_email = criar_campo("EMAIL")
        self.ent_senha = criar_campo("SENHA (MÍN. 8 DÍGITOS)", is_senha=True)

        def formatar_cpf(event):
            texto = re.sub(r'\D', '', self.ent_cpf.get())[:11]  # Apenas números, max 11
            novo_texto = ""
            for i, char in enumerate(texto):
                if i == 3 or i == 6: novo_texto += "."
                if i == 9: novo_texto += "-"
                novo_texto += char
            self.ent_cpf.delete(0, "end")
            self.ent_cpf.insert(0, novo_texto)

        def formatar_tel(event):
            texto = re.sub(r'\D', '', self.ent_telefone.get())[:11]  # Apenas números, max 11
            novo_texto = ""
            for i, char in enumerate(texto):
                if i == 0: novo_texto += "("
                if i == 2: novo_texto += ") "
                if i == 7: novo_texto += "-"
                novo_texto += char
            self.ent_telefone.delete(0, "end")
            self.ent_telefone.insert(0, novo_texto)

        self.ent_cpf.bind("<KeyRelease>", formatar_cpf)
        self.ent_telefone.bind("<KeyRelease>", formatar_tel)

        def verificar_e_ir():
            nome = self.ent_nome.get().strip()
            cpf = self.ent_cpf.get().strip()
            tel = self.ent_telefone.get().strip()
            email = self.ent_email.get().strip()
            senha = self.ent_senha.get().strip()

            if not all([nome, cpf, tel, email, senha]):
                messagebox.showwarning("Erro", "Preencha tudo!")
                return

            if len(nome.split()) < 2:
                messagebox.showwarning("Erro", "Digite Nome e Sobrenome.")
                return

            if "@" not in email:
                messagebox.showwarning("Erro", "E-mail inválido!")
                return

            try:
                conn = conectar()
                c = conn.cursor()
                c.execute("SELECT email, cpf, telefone FROM usuarios WHERE email=? OR cpf=? OR telefone=?",
                          (email, cpf, tel))
                resultado = c.fetchone()
                conn.close()

                if resultado:
                    r_email, r_cpf, r_tel = resultado
                    if r_email == email:
                        msg = "Este E-mail já possui cadastro!"
                    elif r_cpf == cpf:
                        msg = "Este CPF já está cadastrado!"
                    else:
                        msg = "Este Telefone já possui cadastro!"
                    messagebox.showwarning("Atenção", msg)
                    return
            except Exception as e:
                print(f"Erro no banco: {e}")

            self.user_data = {'nome': nome, 'cpf': cpf, 'telefone': tel, 'email': email, 'senha': senha}
            self.tela_idiomas()

        tk.Button(f_cad, text="PRÓXIMO", bg=COR_AZUL, fg="white", font=("Arial", 11, "bold"),
                  width=30, height=2, relief="flat", cursor="hand2", command=verificar_e_ir).pack(pady=(15, 5))

        tk.Button(f_cad, text="VOLTAR AO LOGIN", bg=COR_FUNDO, fg=COR_AZUL, bd=0,
                  font=("Arial", 10, "bold"), cursor="hand2", command=self.tela_login).pack(pady=10)

    def tela_idiomas(self):
        logado = self.user_data.get('id') is not None
        if not logado:
            self.limpar()
            alvo = self.container
        else:
            for w in self.corpo.winfo_children(): w.destroy()
            alvo = self.corpo

        lista_mestra = getattr(self, 'LISTA_MESTRA_IDIOMAS',
                               ["Inglês", "Espanhol", "Francês", "Alemão", "Japonês", "Coreano"])

        atuais = [i.strip() for i in str(self.user_data.get('idiomas_contratados', '')).split(',') if i.strip()]

        idiomas_disponiveis = [i for i in lista_mestra if i not in atuais]

        f_meio = tk.Frame(alvo, bg=COR_FUNDO)
        if not logado:
            f_meio.place(relx=0.5, rely=0.5, anchor="center")
        else:
            f_meio.pack(expand=True)

        if not idiomas_disponiveis:
            tk.Label(f_meio, text="🌟 CATÁLOGO COMPLETO", font=("Arial", 20, "bold"),
                     bg=COR_FUNDO, fg=COR_AZUL).pack(pady=10)
            tk.Label(f_meio, text="Você já está estudando todos os idiomas disponíveis!",
                     font=("Arial", 12), bg=COR_FUNDO).pack(pady=20)
            tk.Button(f_meio, text="VOLTAR AO MENU", bg=COR_AZUL, fg="white",
                      width=20, command=self.dashboard_aulas).pack(pady=10)
            return

        tk.Label(f_meio, text="ESCOLHA SEUS IDIOMAS", font=("Arial", 18, "bold"),
                 bg=COR_FUNDO, fg=COR_AZUL).pack(pady=20)

        self.vars = {}

        for i in idiomas_disponiveis:
            v = tk.BooleanVar()
            tk.Checkbutton(f_meio, text=i, variable=v, bg=COR_FUNDO,
                           font=("Arial", 12)).pack(anchor="w", padx=50)
            self.vars[i] = v

        tk.Button(f_meio, text="CONTINUAR", bg=COR_AZUL, fg="white", font=("Arial", 11, "bold"),
                  width=20, height=1, command=self.tela_niveis).pack(pady=(30, 0))

        def acao_voltar():
            if logado:
                self.dashboard_aulas()
            else:
                self.tela_cadastro()

        tk.Button(f_meio, text="VOLTAR", bg=COR_CINZA, fg="black", font=("Arial", 11, "bold"),
                  width=20, height=1, relief="flat", cursor="hand2", command=acao_voltar).pack(pady=(5, 10))

    def tela_niveis(self):
        sel = [k for k, v in self.vars.items() if v.get()]
        if not sel:
            messagebox.showwarning("Atenção", "Selecione ao menos um idioma.")
            return

        self.user_data["idiomas_novos_lista"] = sel
        logado = self.user_data.get('id') is not None
        alvo = self.corpo if logado else self.container
        [w.destroy() for w in alvo.winfo_children()]

        f_meio = tk.Frame(alvo, bg=COR_FUNDO)
        if not logado:
            f_meio.place(relx=0.5, rely=0.5, anchor="center")
        else:
            f_meio.pack(pady=50)

        tk.Label(f_meio, text="QUAL SEU NÍVEL?", font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(pady=20)
        for n in ["Iniciante", "Básico", "Intermediário", "Avançado"]:
            tk.Button(f_meio, text=n, width=30, height=2, bg="white", font=("Arial", 10, "bold"), fg=COR_AZUL,
                      relief="groove", cursor="hand2",
                      command=lambda nv=n: self.tela_planos(nv)).pack(pady=5)
        tk.Button(f_meio, text="VOLTAR", command=self.tela_idiomas, bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=20, ipady=5)

    def tela_planos(self, nivel):
        self.user_data["nivel_selecionado"] = nivel
        logado = self.user_data.get('id') is not None
        alvo = self.corpo if logado else self.container
        [w.destroy() for w in alvo.winfo_children()]
        qtd = len(self.user_data["idiomas_novos_lista"])

        f_meio = tk.Frame(alvo, bg=COR_FUNDO)
        if not logado:
            f_meio.place(relx=0.5, rely=0.5, anchor="center")
        else:
            f_meio.pack(pady=30)

        tk.Label(f_meio, text="ESCOLHA UM PLANO", font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(pady=20)
        planos = [("MENSAL", 100 * qtd), ("SEMESTRAL", 550 * qtd), ("ANUAL", 1000 * qtd)]
        for p, v in planos:
            tk.Button(f_meio, text=f"{p}: R$ {v},00", width=35, height=2, bg="white", font=("Arial", 11, "bold"),
                      fg=COR_AZUL, relief="groove", cursor="hand2",
                      command=lambda pl=p, val=v: self.tela_checkout(pl, val)).pack(pady=8)
        tk.Button(f_meio, text="VOLTAR", command=lambda: self.tela_niveis(), bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=20, ipady=5)

    def tela_checkout(self, plano, valor):
        self.user_data["plano"] = plano
        self.user_data["valor_final"] = valor
        logado = self.user_data.get('id') is not None
        alvo = self.corpo if logado else self.container
        [w.destroy() for w in alvo.winfo_children()]
        ttk.Button(alvo, text="⬅ VOLTAR AO INÍCIO", style="BotaoVoltar.TButton", command=self.dashboard_aulas).pack(
            pady=10, padx=10, anchor="nw")

        tab = ttk.Notebook(alvo)
        f_card = tk.Frame(tab, bg=COR_FUNDO, pady=20)
        f_pix = tk.Frame(tab, bg=COR_FUNDO, pady=20)
        f_bol = tk.Frame(tab, bg=COR_FUNDO, pady=20)

        v_l = (self.root.register(self.validar_apenas_letras), '%P')

        tk.Label(f_card, text="TIPO DE CARTÃO", bg=COR_FUNDO, font=("Arial", 9, "bold")).pack(pady=(10, 0))
        tipo_c = ttk.Combobox(f_card, values=["CRÉDITO", "DÉBITO"], state="readonly", font=("Arial", 10))
        tipo_c.current(0)
        tipo_c.pack(pady=5)

        tk.Label(f_card, text="NOME NO TITULAR", bg=COR_FUNDO, font=("Arial", 9, "bold")).pack(pady=(10, 0))
        en_tit = tk.Entry(f_card, width=35, validate="key", validatecommand=v_l, **self.estilo_entry)
        en_tit.pack(pady=5, ipady=4)

        tk.Label(f_card, text="NÚMERO DO CARTÃO", bg=COR_FUNDO, font=("Arial", 9, "bold")).pack(pady=(10, 0))
        en_c = tk.Entry(f_card, width=35, **self.estilo_entry)
        en_c.pack(pady=5, ipady=4)
        en_c.bind("<KeyRelease>", self.masc_cartao)

        f_meio = tk.Frame(f_card, bg=COR_FUNDO)
        f_meio.pack(pady=10)
        tk.Label(f_meio, text="VALIDADE (MM/AA)", bg=COR_FUNDO, font=("Arial", 8, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(f_meio, text="CVV", bg=COR_FUNDO, font=("Arial", 8, "bold")).grid(row=0, column=1, padx=5)
        e_val = tk.Entry(f_meio, width=15, **self.estilo_entry)
        e_val.grid(row=1, column=0, padx=5, ipady=4)
        e_val.bind("<KeyRelease>", self.masc_validade)
        e_cvv = tk.Entry(f_meio, width=15, **self.estilo_entry)
        e_cvv.grid(row=1, column=1, padx=5, ipady=4)
        e_cvv.bind("<KeyRelease>", self.masc_cvv)

        combo = ttk.Combobox(f_card, state="readonly", width=35, font=("Arial", 10))

        def atualizar_parcelas(event=None):
            ops = []

            if tipo_c.get() == "DÉBITO" or plano == "MENSAL":
                ops = [f"1x de R$ {valor:.2f} (Total: R$ {valor:.2f})"]

            elif plano == "SEMESTRAL":
                for i in range(1, 7):
                    parc_v = valor / i
                    ops.append(f"{i}x de R$ {parc_v:.2f} s/ juros (Total: R$ {valor:.2f})")

            elif plano == "ANUAL":
                for i in range(1, 13):
                    if i <= 10:
                        parc_v = valor / i
                        total_f = valor
                        ops.append(f"{i}x de R$ {parc_v:.2f} s/ juros (Total: R$ {total_f:.2f})")
                    else:
                        total_f = valor * 1.03
                        parc_v = total_f / i
                        ops.append(f"{i}x de R$ {parc_v:.2f} c/ juros (Total: R$ {total_f:.2f})")

            combo['values'] = ops
            combo.current(0)

        tipo_c.bind("<<ComboboxSelected>>", atualizar_parcelas)
        
        atualizar_parcelas()
        combo.pack(pady=15)

        tk.Button(f_card, text="FINALIZAR COMPRA", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), relief="flat",
                  cursor="hand2", width=30,
                  command=lambda: self.finalizar_db("CARTÃO", combo.get())).pack(pady=10, ipady=5)

        tk.Label(f_pix, text="PAGAMENTO VIA PIX", font=("Arial", 14, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(pady=20)
        tk.Button(f_pix, text="GERAR QR CODE", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), relief="flat",
                  cursor="hand2", width=30, command=lambda: self.finalizar_db("PIX", "À VISTA")).pack(pady=20, ipady=5)

        tk.Label(f_bol, text="PAGAMENTO VIA BOLETO", font=("Arial", 14, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            pady=20)
        tk.Button(f_bol, text="GERAR BOLETO", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), relief="flat",
                  cursor="hand2", width=30, command=lambda: self.finalizar_db("BOLETO", "À VISTA")).pack(pady=20,
                                                                                                         ipady=5)

        tab.add(f_card, text="💳 CARTÃO")
        tab.add(f_pix, text="💠 PIX")
        tab.add(f_bol, text="📄 BOLETO")
        tab.pack(expand=1, fill="both", padx=20, pady=10)

    def finalizar_db(self, met, parc):
        conn = conectar()
        c = conn.cursor()
        plano_escolhido = self.user_data['plano']
        dias = 30 if plano_escolhido == "MENSAL" else 180 if plano_escolhido == "SEMESTRAL" else 365
        venc = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")
        novos_idms = self.user_data["idiomas_novos_lista"]
        nv_padrao = self.user_data.get("nivel_selecionado", "Iniciante")

        if self.user_data.get('id'):
            uid = self.user_data['id']
            c.execute("SELECT idiomas_contratados FROM usuarios WHERE id=?", (uid,))
            atual = c.fetchone()[0]
            lista_final = list(set((atual.split(", ") if atual else []) + novos_idms))
            for idm in novos_idms: self.niveis_por_idioma[idm] = nv_padrao
            niveis_db = "|".join([f"{k}:{v}" for k, v in self.niveis_por_idioma.items()])
            c.execute("UPDATE usuarios SET idiomas_contratados=?, nivel=?, plano=?, data_pagamento=? WHERE id=?",
                      (", ".join(lista_final), niveis_db, plano_escolhido, venc, uid))
        else:

            email_c = self.user_data['email']
            cpf_c = self.user_data['cpf']
            tel_c = self.user_data['telefone']

            c.execute("SELECT email, cpf, telefone FROM usuarios WHERE email=? OR cpf=? OR telefone=?",
                      (email_c, cpf_c, tel_c))
            repetido = c.fetchone()

            if repetido:
                res_e, res_c, res_t = repetido
                if res_e == email_c:
                    msg = f"O email {email_c} já está cadastrado!"
                elif res_c == cpf_c:
                    msg = f"O CPF {cpf_c} já está cadastrado!"
                else:
                    msg = f"O telefone {tel_c} já está cadastrado!"

                messagebox.showerror("Erro de Cadastro", msg)
                conn.close()
                return

            for idm in novos_idms: self.niveis_por_idioma[idm] = nv_padrao
            niveis_db = "|".join([f"{k}:{v}" for k, v in self.niveis_por_idioma.items()])
            c.execute(
                "INSERT INTO usuarios (nome, cpf, telefone, email, senha, idiomas_contratados, plano, nivel, data_pagamento, status_curso) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (self.user_data['nome'], self.user_data['cpf'], self.user_data['telefone'], self.user_data['email'],
                 self.user_data['senha'], ", ".join(novos_idms), plano_escolhido, niveis_db, venc, "Ativo"))
            uid = c.lastrowid

        c.execute("INSERT INTO pagamentos (usuario_id, idiomas, plano, valor, metodo, vencimento) VALUES (?,?,?,?,?,?)",
                  (uid, ", ".join(novos_idms), plano_escolhido, self.user_data['valor_final'], f"{met}: {parc}", venc))
        conn.commit()

        c.execute("SELECT * FROM usuarios WHERE id=?", (uid,))
        self.user_data = dict(zip([d[0] for d in c.description], c.fetchone()))
        conn.close()
        messagebox.showinfo("BabelUp", "Compra realizada com sucesso!\nBem-vindo(a) ao BabelUp!")
        self.dashboard_aulas()

    def dashboard_aulas(self):
        self.limpar()
        self.root.geometry("1100x750")
        menu = tk.Frame(self.container, bg=COR_AZUL, width=280)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        tk.Label(menu, text="🎓", font=("Arial", 40), bg=COR_AZUL, fg="white").pack(pady=(30, 0))
        tk.Label(menu, text=f"Olá, {self.user_data['nome'].split()[0]}", fg="white", bg=COR_AZUL,
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))

        btn_s = {"bg": COR_AZUL, "fg": "white", "font": ("Arial", 10, "bold"), "bd": 0, "relief": "flat",
                 "anchor": "w", "padx": 20, "cursor": "hand2", "activebackground": COR_BOTAO_MENU,
                 "activeforeground": "white"}

        tk.Button(menu, text="👤  DADOS PESSOAIS", command=self.mostrar_dados_pessoais, **btn_s).pack(fill="x", pady=2,
                                                                                                     ipady=12)
        tk.Button(menu, text="🏠  MEUS CURSOS", command=self.dashboard_aulas, **btn_s).pack(fill="x", pady=2, ipady=12)
        tk.Button(menu, text="🔴  AULAS AO VIVO", command=self.tela_aulas_ao_vivo, **btn_s).pack(fill="x", pady=2,
                                                                                                ipady=12)
        tk.Button(menu, text="➕  ADICIONAR IDIOMAS", command=self.tela_idiomas, **btn_s).pack(fill="x", pady=2,
                                                                                              ipady=12)
        tk.Button(menu, text="💳  PAGAMENTOS", command=self.mostrar_status_pagamento, **btn_s).pack(fill="x", pady=2,
                                                                                                   ipady=12)
        tk.Button(menu, text="🎧  SUPORTE", command=self.tela_suporte, **btn_s).pack(fill="x", pady=2, ipady=12)
        tk.Button(menu, text="💬  FEEDBACK", command=self.tela_feedback, **btn_s).pack(fill="x", pady=2, ipady=12)

        tk.Button(
            menu,
            text="🚪  SAIR",
            bg=COR_CINZA,
            fg="black",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            activebackground="#bcbcbc",
            command=self.tela_login
        ).pack(side="bottom", fill="x", pady=15, padx=20, ipady=10)
        tk.Button(menu, text="⚠  ENCERRAR CONTA", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), bd=0,
                  cursor="hand2", command=self.tela_encerrar_conta).pack(side="bottom", fill="x", pady=(10, 0), padx=20,
                                                                         ipady=10)

        self.corpo = tk.Frame(self.container, bg=COR_FUNDO)
        self.corpo.pack(side="right", expand=1, fill="both")

        canvas_dash = tk.Canvas(self.corpo, bg=COR_FUNDO, highlightthickness=0)
        scrollbar_dash = ttk.Scrollbar(self.corpo, orient="vertical", command=canvas_dash.yview)
        scrollable_dash = tk.Frame(canvas_dash, bg=COR_FUNDO)

        scrollable_dash.bind("<Configure>", lambda e: canvas_dash.configure(scrollregion=canvas_dash.bbox("all")))
        canvas_dash.create_window((0, 0), window=scrollable_dash, anchor="nw", width=750)
        canvas_dash.configure(yscrollcommand=scrollbar_dash.set)

        self._configurar_scroll_mouse(canvas_dash)

        canvas_dash.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        scrollbar_dash.pack(side="right", fill="y")

        tk.Label(scrollable_dash, text="MEUS CURSOS", font=("Arial", 22, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            anchor="w", pady=(0, 20))

        idms = [i for i in str(self.user_data.get('idiomas_contratados', '')).split(', ') if i]

        if not idms:
            tk.Label(scrollable_dash, text="Você ainda não tem idiomas contratados.", bg=COR_FUNDO,
                     font=("Arial", 12)).pack(anchor="w")

        for idm in idms:
            nv = self.niveis_por_idioma.get(idm, "Iniciante")
            card = tk.Frame(scrollable_dash, bg="white", highlightbackground=COR_CINZA, highlightthickness=1)
            card.pack(fill="x", pady=10, ipady=10)

            f_infos = tk.Frame(card, bg="white")
            f_infos.pack(side="left", padx=20)

            tk.Label(f_infos, text=f"{idm.upper()}", bg="white", font=("Arial", 14, "bold"), fg=COR_AZUL).pack(
                anchor="w")
            tk.Label(f_infos, text=f"Nível Atual: {nv}", bg="white", font=("Arial", 10)).pack(anchor="w")

            tk.Button(card, text="ABRIR CURSO", bg=COR_BOTAO_MENU, fg="white", font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2",
                      command=lambda i=idm: self.tela_lista_aulas(i)).pack(side="right", padx=20, ipady=5, ipadx=10)

    def mostrar_dados_pessoais(self):
        for w in self.corpo.winfo_children(): w.destroy()
        f_conteudo = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=30)
        f_conteudo.pack(fill="both", expand=True)

        tk.Label(f_conteudo, text="DADOS PESSOAIS", font=("Arial", 22, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            anchor="w", pady=(0, 20))

        f = tk.Frame(f_conteudo, bg="white", highlightthickness=1, highlightbackground=COR_CINZA, padx=30, pady=30)
        f.pack(fill="x", pady=10)

        self.label_senha_valor = tk.StringVar(value="********")
        dados = [("👤 Nome:", self.user_data.get('nome')), ("📄 CPF:", self.user_data.get('cpf')),
                 ("📧 E-mail:", self.user_data.get('email')), ("📱 Telefone:", self.user_data.get('telefone'))]

        for label, valor in dados:
            row = tk.Frame(f, bg="white")
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, font=("Arial", 11, "bold"), bg="white", fg=COR_AZUL, width=15, anchor="w").pack(
                side="left")
            tk.Label(row, text=f"{valor}", font=("Arial", 11), bg="white").pack(side="left")

        row_s = tk.Frame(f, bg="white")
        row_s.pack(fill="x", pady=8)
        tk.Label(row_s, text="🔑 Senha:", font=("Arial", 11, "bold"), bg="white", fg=COR_AZUL, width=15,
                 anchor="w").pack(side="left")
        tk.Label(row_s, textvariable=self.label_senha_valor, font=("Arial", 11), bg="white").pack(side="left")

        btn_f = tk.Frame(f, bg="white")
        btn_f.pack(pady=15)
        tk.Label(btn_f, text="Ver Senha por:", bg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        for met in ["E-mail", "WhatsApp", "SMS"]:
            tk.Button(btn_f, text=met, font=("Arial", 9), bg=COR_CINZA, relief="flat", cursor="hand2", width=10,
                      command=lambda m=met: self.janela_validacao_codigo(m)).pack(side="left", padx=5)

        tk.Button(f_conteudo, text="VOLTAR", command=self.dashboard_aulas, bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=20, anchor="w")

    def janela_validacao_codigo(self, metodo):
        messagebox.showinfo("BabelUp", f"Código enviado para o seu {metodo}.")
        janela_val = tk.Toplevel(self.root)
        janela_val.title("Validação")
        janela_val.geometry("300x200")
        janela_val.configure(bg=COR_FUNDO)
        janela_val.grab_set()

        tk.Label(janela_val, text="Digite o código (123456):", bg=COR_FUNDO, font=("Arial", 10, "bold")).pack(pady=20)
        ent_cod = tk.Entry(janela_val, width=15, justify="center", font=("Arial", 14), **self.estilo_entry)
        ent_cod.pack(pady=5, ipady=5)

        def confirmar():
            if ent_cod.get() == "123456":
                self.label_senha_valor.set(self.user_data.get('senha'))
                messagebox.showinfo("Sucesso", "Identidade confirmada!")
                janela_val.destroy()
            else:
                messagebox.showerror("Erro", "Código incorreto.")

        tk.Button(janela_val, text="VALIDAR", command=confirmar, bg=COR_AZUL, fg="white", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=15, ipady=5)

    def mostrar_status_pagamento(self):
        for w in self.corpo.winfo_children(): w.destroy()

        header = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="HISTÓRICO DE ASSINATURAS", font=("Arial", 22, "bold"),
                 bg=COR_FUNDO, fg=COR_AZUL).pack(side="left")

        canvas = tk.Canvas(self.corpo, bg=COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.corpo, orient="vertical", command=canvas.yview)
        scroll_f = tk.Frame(canvas, bg=COR_FUNDO)

        def ajustar_largura_pagamentos(event):
            canvas.itemconfig(window_id, width=event.width)

        window_id = canvas.create_window((0, 0), window=scroll_f, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=30)
        scrollbar.pack(side="right", fill="y")

        canvas.bind("<Configure>", ajustar_largura_pagamentos)
        scroll_f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._configurar_scroll_mouse(canvas)

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT idiomas, plano, valor, metodo, vencimento FROM pagamentos WHERE usuario_id=?",
                  (self.user_data['id'],))
        compras = c.fetchall()
        conn.close()

        if not compras:
            tk.Label(scroll_f, text="Nenhum pagamento registrado.", bg=COR_FUNDO,
                     font=("Arial", 12)).pack(pady=20)

        for idms, plano, valor, metodo, venc in compras:
            f = tk.Frame(scroll_f, bg="white", highlightthickness=1,
                         highlightbackground=COR_CINZA, padx=20, pady=15)
            f.pack(fill="x", pady=10)

            detalhes = [("📚 Idiomas:", idms), ("📅 Plano:", plano),
                        ("💰 Valor:", f"R$ {valor:.2f}"), ("💳 Método:", metodo),
                        ("🔔 Vencimento:", venc)]

            for label, val in detalhes:
                row = tk.Frame(f, bg="white")
                row.pack(fill="x", pady=2)
                tk.Label(row, text=label, font=("Arial", 10, "bold"), bg="white",
                         fg=COR_AZUL, width=15, anchor="w").pack(side="left")
                tk.Label(row, text=f"{val}", font=("Arial", 10), bg="white").pack(side="left")

        tk.Button(scroll_f, text="VOLTAR AO MENU", command=self.dashboard_aulas,
                  bg=COR_CINZA, font=("Arial", 10, "bold"), width=20).pack(pady=30)

    def tela_aulas_ao_vivo(self):
        for w in self.corpo.winfo_children(): w.destroy()
        f_conteudo = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=30)
        f_conteudo.pack(fill="both", expand=True)

        tk.Label(f_conteudo, text="🔴 AULAS AO VIVO", font=("Arial", 22, "bold"), bg=COR_FUNDO, fg="#e74c3c").pack(
            anchor="w", pady=(0, 10))
        tk.Label(f_conteudo, text="Junte-se às salas de conversação com nossos professores nativos.",
                 font=("Arial", 12), bg=COR_FUNDO).pack(anchor="w")

        video_container = tk.Frame(f_conteudo, bg="black", width=640, height=360)
        video_container.pack(pady=30)
        video_container.pack_propagate(False)

        tk.Label(video_container, text="▶ TRANSMISSÃO AO VIVO", font=("Arial", 20, "bold"), bg="black",
                 fg="white").pack(expand=True)
        tk.Label(video_container, text="Prof. Marcos - Sala de Conversação", font=("Arial", 12), bg="black",
                 fg="lightgray").pack(pady=10)

        info_frame = tk.Frame(f_conteudo, bg=COR_FUNDO, width=640)
        info_frame.pack()
        tk.Label(info_frame, text="Status: Online", font=("Arial", 11, "bold"), bg=COR_FUNDO, fg="#27ae60").pack(
            side="left", padx=20)
        tk.Label(info_frame, text="Próxima Sessão: Hoje às 19:00", font=("Arial", 11), bg=COR_FUNDO).pack(side="right",
                                                                                                          padx=20)

        tk.Button(f_conteudo, text="VOLTAR", command=self.dashboard_aulas, bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=40, anchor="w")

    def tela_suporte(self):
        for w in self.corpo.winfo_children(): w.destroy()
        f_conteudo = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=30)
        f_conteudo.pack(fill="both", expand=True)

        tk.Label(f_conteudo, text="SUPORTE TÉCNICO", font=("Arial", 22, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            anchor="w", pady=(0, 20))

        f = tk.Frame(f_conteudo, bg="white", highlightthickness=1, highlightbackground=COR_CINZA, padx=30, pady=30)
        f.pack(fill="x", pady=10)
        contatos = [("📧 E-mail:", "suporte@babelup.com"), ("🟢 WhatsApp:", "(00) 99999-9999"),
                    ("🕒 Horário:", "Segunda a Sexta: 08:00 às 18:00")]
        for label, valor in contatos:
            row = tk.Frame(f, bg="white")
            row.pack(fill="x", pady=10)
            tk.Label(row, text=label, font=("Arial", 12, "bold"), bg="white", fg=COR_AZUL, width=12, anchor="w").pack(
                side="left")
            tk.Label(row, text=f"{valor}", font=("Arial", 12), bg="white").pack(side="left")

        tk.Button(f_conteudo, text="VOLTAR", command=self.dashboard_aulas, bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=20, anchor="w")

    def tela_feedback(self):
        for w in self.corpo.winfo_children(): w.destroy()
        f_conteudo = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=30)
        f_conteudo.pack(fill="both", expand=True)

        tk.Label(f_conteudo, text="ENVIAR FEEDBACK", font=("Arial", 22, "bold"), bg=COR_FUNDO, fg=COR_AZUL).pack(
            anchor="w", pady=(0, 20))
        tk.Label(f_conteudo, text="Sua opinião é fundamental para nós.\nO que podemos melhorar?", font=("Arial", 12),
                 bg=COR_FUNDO, justify="left").pack(anchor="w", pady=10)

        self.txt_fb = tk.Text(f_conteudo, height=6, width=60, font=("Arial", 11), bd=0, highlightthickness=1,
                              highlightbackground=COR_CINZA, highlightcolor=COR_AZUL, padx=10, pady=10)
        self.txt_fb.pack(pady=10, fill="x")

        def enviar():
            if len(self.txt_fb.get("1.0", tk.END).strip()) < 10:
                messagebox.showwarning("Atenção", "Escreva um pouco mais.")
                return
            messagebox.showinfo("BabelUp", "Obrigado! Feedback enviado com sucesso.")
            self.dashboard_aulas()

        tk.Button(f_conteudo, text="ENVIAR FEEDBACK", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", command=enviar, padx=20, pady=10).pack(pady=10, anchor="w")
        tk.Button(f_conteudo, text="VOLTAR", command=self.dashboard_aulas, bg=COR_CINZA, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", width=15).pack(pady=10, anchor="w")

    def tela_encerrar_conta(self)
        for w in self.corpo.winfo_children(): w.destroy()

        f_feedback_style = tk.Frame(self.corpo, bg=COR_FUNDO)
        f_feedback_style.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f_feedback_style, text="SENTIREMOS SUA FALTA!", font=("Arial", 16, "bold"),
                 bg=COR_FUNDO, fg=COR_AZUL).pack(pady=(0, 10))

        tk.Label(f_feedback_style,
                 text="Pode nos dizer por que está encerrando a conta?\nSeu feedback é muito importante para nós.",
                 font=("Arial", 10), bg=COR_FUNDO, fg="#555").pack(pady=5)

        txt_motivo = tk.Text(f_feedback_style, width=45, height=8, font=("Arial", 10),
                             relief="solid", bd=1, padx=10, pady=10)
        txt_motivo.pack(pady=20)

        def confirmar():
            motivo = txt_motivo.get("1.0", tk.END).strip()
            if len(motivo) < 5:
                messagebox.showwarning("Atenção", "Por favor, escreva um breve motivo antes de prosseguir.")
                return

            if messagebox.askyesno("Confirmar", "Isso apagará seu progresso permanentemente. Continuar?"):
                try:
                    conn = conectar()
                    c = conn.cursor()
                    c.execute("DELETE FROM usuarios WHERE id = ?", (self.user_data['id'],))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("BabelUp", "Conta encerrada com sucesso. Esperamos te ver no futuro!")
                    self.tela_login()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao processar: {e}")

        btn_confirmar = tk.Button(f_feedback_style, text="ENCERRAR MINHA CONTA",
                                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                  width=30, height=2, relief="flat", cursor="hand2",
                                  command=confirmar)
        btn_confirmar.pack(pady=5)

        btn_voltar = tk.Button(f_feedback_style, text="CANCELAR E VOLTAR",
                               bg=COR_CINZA, fg="black", font=("Arial", 10),
                               width=30, height=1, relief="flat", cursor="hand2",
                               command=self.dashboard_aulas)
        btn_voltar.pack(pady=10)

    def acao_confirmar_encerramento(self, txt_motivo):
        motivo = txt_motivo.get("1.0", tk.END).strip()

        if len(motivo) < 5:
            messagebox.showwarning("Atenção", "Diga o motivo.")
            return

        try:
            conn = conectar()
            c = conn.cursor()
            c.execute("DELETE FROM usuarios WHERE id=?", (self.user_data['id'],))
            conn.commit()
            conn.close()

            messagebox.showinfo("BabelUp", "Sua conta será desativada em 24h.\nObrigado pelo tempo conosco!")
            self.tela_login()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {e}")

    def tela_lista_aulas(self, idioma):
        for w in self.corpo.winfo_children(): w.destroy()
        nv_atual = self.niveis_por_idioma.get(idioma, "Iniciante")
        aulas_atuais = self.aulas_por_nivel.get(nv_atual, [])

        f_conteudo = tk.Frame(self.corpo, bg=COR_FUNDO, padx=30, pady=30)
        f_conteudo.pack(fill="both", expand=True)

        tk.Label(f_conteudo, text=f"CURSO DE {idioma.upper()}", font=("Arial", 22, "bold"), bg=COR_FUNDO,
                 fg=COR_AZUL).pack(anchor="w")
        tk.Label(f_conteudo, text=f"Módulo: {nv_atual.upper()}", font=("Arial", 14), bg=COR_FUNDO, fg="gray").pack(
            anchor="w", pady=(0, 20))

        frame_canvas = tk.Frame(f_conteudo, bg=COR_FUNDO)
        frame_canvas.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame_canvas, bg=COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, bg=COR_FUNDO)

        canvas.bind('<Enter>', lambda _: canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas)))
        canvas.bind('<Leave>', lambda _: canvas.unbind_all("<MouseWheel>"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COR_FUNDO)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=700)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._configurar_scroll_mouse(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for n, nome in enumerate(aulas_atuais, 1):
            tag = f"{idioma}_{nv_atual}_{n:02d}"
            tag_anterior = f"{idioma}_{nv_atual}_{n - 1:02d}"

            f = tk.Frame(scrollable_frame, bg="white", highlightthickness=1, highlightbackground=COR_CINZA)
            f.pack(fill="x", pady=5, ipady=12, padx=5)
            tk.Label(f, text=f"Aula {n:02d} - {nome}", bg="white", font=("Arial", 11, "bold")).pack(side="left",
                                                                                                    padx=15)

            pode_abrir = True if n == 1 or tag_anterior in self.aulas_concluidas else False
            ja_fez = tag in self.aulas_concluidas

            if ja_fez:
                bt_t, cor_b, cor_t, est, cmd = "CONCLUÍDA ✅", "#27ae60", "white", "normal", lambda: None
            elif pode_abrir:
                bt_t, cor_b, cor_t, est, cmd = "ASSISTIR", COR_AZUL, "white", "normal", lambda \
                    id_a=n: self.concluir_aula(id_a, idioma, nv_atual)
            else:
                bt_t, cor_b, cor_t, est, cmd = "🔒 BLOQUEADA", COR_CINZA, "#7f8c8d", "disabled", lambda: None

            tk.Button(f, text=bt_t, font=("Arial", 9, "bold"), bg=cor_b, fg=cor_t, width=18, state=est, relief="flat",
                      cursor="hand2" if est == "normal" else "arrow", command=cmd).pack(side="right", padx=15, ipady=4)

        pode_prova = f"{idioma}_{nv_atual}_10" in self.aulas_concluidas
        prova_container = tk.Frame(scrollable_frame, bg=COR_FUNDO)
        prova_container.pack(fill="x", pady=30, padx=5)

        btn_prova = tk.Button(prova_container, text="⭐ INICIAR PROVA ⭐" if pode_prova else "🔒 PROVA BLOQUEADA",
                              font=("Arial", 12, "bold"), bg=COR_PROVA if pode_prova else COR_CINZA, fg="white",
                              relief="flat", cursor="hand2" if pode_prova else "arrow",
                              state="normal" if pode_prova else "disabled", command=lambda: self.subir_nivel(idioma))
        btn_prova.pack(fill="x", ipady=10)

        tk.Button(f_conteudo, text="VOLTAR AO MENU", command=self.dashboard_aulas, bg=COR_CINZA,
                  font=("Arial", 10, "bold"), relief="flat", cursor="hand2", width=20).pack(pady=10, anchor="w")

    def concluir_aula(self, num_aula, idioma, nivel):
        tag = f"{idioma}_{nivel}_{num_aula:02d}"
        if tag not in self.aulas_concluidas:
            self.aulas_concluidas.append(tag)
        messagebox.showinfo("BabelUp", f"Aula {num_aula} concluída!")
        self.tela_lista_aulas(idioma)

    def subir_nivel(self, idioma):
        niveis = ["Iniciante", "Básico", "Intermediário", "Avançado"]
        atual = self.niveis_por_idioma.get(idioma, "Iniciante")
        if atual != "Avançado":
            novo = niveis[niveis.index(atual) + 1]
            self.niveis_por_idioma[idioma] = novo
            niveis_db = "|".join([f"{k}:{v}" for k, v in self.niveis_por_idioma.items()])
            conn = conectar()
            c = conn.cursor()
            c.execute("UPDATE usuarios SET nivel=? WHERE id=?", (niveis_db, self.user_data['id']))
            conn.commit()
            conn.close()
            messagebox.showinfo("BabelUp", f"Parabéns! Você subiu para o nível {novo}!")
            self.dashboard_aulas()
        else:
            messagebox.showinfo("BabelUp", "Você já concluiu o nível Avançado deste idioma!")


if __name__ == "__main__":
    root = tk.Tk()
    app = BabelUpApp(root)
    root.mainloop()
