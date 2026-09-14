# ==================================================
# SISTEMA CLÍNICA PET — FICHA DO PET ATUALIZADA
# ✅ Campos: Raça, Cor, Pelagem, Vacinas, Idade, Última Consulta, Retorno
# ✅ NOVO | EDITAR | EXCLUIR
# ✅ Chave Estrangeira tutor_id validadada
# ✅ CEP Automático no Cliente
# ✅ Roda em JSON — sem instalar banco
# ==================================================

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests
from datetime import datetime

# ==================================================
# 🔧 FUNÇÃO: BUSCAR ENDEREÇO PELA API VIA CEP (Correios)
# ==================================================
def buscar_cep(cep):
    cep_limpo = ''.join(c for c in cep if c.isdigit())
    if len(cep_limpo) != 8:
        return None
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            dados = resposta.json()
            if "erro" not in dados:
                return {
                    "logradouro": dados.get("logradouro", ""),
                    "bairro": dados.get("bairro", ""),
                    "cidade": dados.get("localidade", ""),
                    "uf": dados.get("uf", ""),
                    "completo": f"{dados.get('logradouro','')}, {dados.get('bairro','')} - {dados.get('localidade','')}/{dados.get('uf','')}"
                }
    except:
        pass
    return None

# ==================================================
# 📁 ARQUIVOS = TABELAS
# ==================================================
ARQUIVO_CLIENTES = "tbl_clientes.json"
ARQUIVO_PETS = "tbl_pets.json"
ARQUIVO_ESTOQUE = "tbl_estoque.json"
ARQUIVO_ATENDIMENTOS = "tbl_atendimentos.json"

tbl_clientes = []
tbl_pets = []
tbl_estoque = []
tbl_atendimentos = []

# ==================================================
# 🔐 INTEGRIDADE REFERENCIAL (Chaves Estrangeiras)
# ==================================================
def validar_chave_estrangeira(tabela_filha, campo_fk, valor_id):
    if tabela_filha == "pets":
        existe = any(c["id"] == valor_id for c in tbl_clientes)
        if not existe:
            messagebox.showerror("❌ Erro de Chave Estrangeira", 
                f"Cliente ID {valor_id} NÃO está cadastrado!\nCadastre o cliente primeiro.")
        return existe
    elif tabela_filha == "atendimentos":
        existe = any(p["id"] == valor_id for p in tbl_pets)
        if not existe:
            messagebox.showerror("❌ Erro de Chave Estrangeira", 
                f"Pet ID {valor_id} NÃO está cadastrado!\nCadastre o pet primeiro.")
        return existe
    return True

def exclusao_cascata(tabela_pai, id_pai):
    global tbl_pets, tbl_atendimentos
    if tabela_pai == "cliente":
        pets_apagar = [p["id"] for p in tbl_pets if p["tutor_id"] == id_pai]
        tbl_pets = [p for p in tbl_pets if p["tutor_id"] != id_pai]
        tbl_atendimentos = [a for a in tbl_atendimentos if a["pet_id"] not in pets_apagar]
        return len(pets_apagar)
    return 0

# ==================================================
# 💾 CARREGAR E SALVAR
# ==================================================
def carregar_tabela(arquivo, padrao):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return padrao

def carregar_dados():
    global tbl_clientes, tbl_pets, tbl_estoque, tbl_atendimentos
    tbl_clientes = carregar_tabela(ARQUIVO_CLIENTES, [])
    tbl_pets = carregar_tabela(ARQUIVO_PETS, [])
    tbl_estoque = carregar_tabela(ARQUIVO_ESTOQUE, [])
    tbl_atendimentos = carregar_tabela(ARQUIVO_ATENDIMENTOS, [])

def salvar_tabela(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_dados():
    salvar_tabela(ARQUIVO_CLIENTES, tbl_clientes)
    salvar_tabela(ARQUIVO_PETS, tbl_pets)
    salvar_tabela(ARQUIVO_ESTOQUE, tbl_estoque)
    salvar_tabela(ARQUIVO_ATENDIMENTOS, tbl_atendimentos)
    atualizar_dashboard()

# ==================================================
# 📅 CALCULAR IDADE AUTOMATICAMENTE
# ==================================================
def calcular_idade(nascimento_str):
    if not nascimento_str or len(nascimento_str.strip()) < 8:
        return "---"
    try:
        nasc = datetime.strptime(nascimento_str.strip(), "%d/%m/%Y")
        hoje = datetime.now()
        anos = hoje.year - nasc.year
        meses = hoje.month - nasc.month
        dias = hoje.day - nasc.day
        if dias < 0: meses -= 1; dias += 30
        if meses < 0: anos -= 1; meses += 12
        if anos > 0 and meses > 0: return f"{anos} ano(s) e {meses} mês(es)"
        elif anos > 0: return f"{anos} ano(s)"
        elif meses > 0: return f"{meses} mês(es) e {dias} dia(s)"
        else: return f"{dias} dia(s)"
    except: return "Data inválida"

# ==================================================
# 🔍 CONSULTAS COM JOIN
# ==================================================
def buscar_pets_com_tutor():
    resultado = []
    for pet in tbl_pets:
        tutor = next((c for c in tbl_clientes if c["id"] == pet["tutor_id"]), None)
        linha = pet.copy()
        linha["tutor_nome"] = tutor["nome"] if tutor else "Desconhecido"
        linha["idade_calculada"] = calcular_idade(pet.get("nascimento",""))
        resultado.append(linha)
    return resultado

def buscar_atendimentos_completos():
    resultado = []
    for atd in tbl_atendimentos:
        pet = next((p for p in tbl_pets if p["id"] == atd["pet_id"]), None)
        if pet:
            tutor = next((c for c in tbl_clientes if c["id"] == pet["tutor_id"]), None)
            linha = atd.copy()
            linha["pet_nome"] = pet["nome"]
            linha["tutor_nome"] = tutor["nome"] if tutor else "Desconhecido"
            resultado.append(linha)
    return resultado

# ==================================================
# 📊 DASHBOARD
# ==================================================
def atualizar_dashboard():
    lbl_qtd_clientes.config(text=f"👥 Clientes: {len(tbl_clientes)}")
    lbl_qtd_pets.config(text=f"🐾 Pets: {len(tbl_pets)}")
    lbl_qtd_atend.config(text=f"📋 Atendimentos: {len(tbl_atendimentos)}")
    total = sum(a["total"] for a in tbl_atendimentos)
    lbl_faturamento.config(text=f"💰 Faturado: R$ {total:.2f}")

# ==================================================
# 👥 TELA CLIENTES — CEP AUTOMÁTICO + EDITAR + EXCLUIR
# ==================================================
def tela_clientes():
    janela = tk.Toplevel(root)
    janela.title("📋 Tabela de Clientes")
    janela.geometry("850x450")

    tabela = ttk.Treeview(janela, columns=("id","nome","tel","cep","endereco"), show="headings")
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Nome Completo")
    tabela.heading("tel", text="Telefone")
    tabela.heading("cep", text="CEP")
    tabela.heading("endereco", text="Endereço")
    tabela.column("id", width=40)
    tabela.column("nome", width=220)
    tabela.column("tel", width=120)
    tabela.column("cep", width=90)
    tabela.column("endereco", width=320)
    tabela.pack(fill="both", expand=True)

    def recarregar():
        for i in tabela.get_children(): tabela.delete(i)
        for c in tbl_clientes:
            tabela.insert("", "end", values=(c["id"], c["nome"], c["telefone"], c.get("cep",""), c.get("endereco","")))

    recarregar()

    def formulario_cliente(titulo, dados=None):
        jan = tk.Toplevel(janela)
        jan.title(titulo)
        jan.geometry("520x420")

        tk.Label(jan, text="Nome Completo:", font=("Arial",10,"bold")).pack(pady=(15,3), anchor="w", padx=25)
        txt_nome = tk.Entry(jan, width=55)
        txt_nome.pack(pady=3, padx=25)
        if dados: txt_nome.insert(0, dados["nome"])

        tk.Label(jan, text="Telefone / WhatsApp:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        txt_tel = tk.Entry(jan, width=55)
        txt_tel.pack(pady=3, padx=25)
        if dados: txt_tel.insert(0, dados["telefone"])

        tk.Label(jan, text="CEP:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        frm_cep = tk.Frame(jan)
        frm_cep.pack(pady=3, padx=25, fill="x")
        txt_cep = tk.Entry(frm_cep, width=20)
        txt_cep.pack(side="left")
        if dados: txt_cep.insert(0, dados.get("cep",""))

        lbl_endereco_auto = tk.Label(frm_cep, text="🔍 Digite o CEP e clique BUSCAR", fg="#555555")
        lbl_endereco_auto.pack(side="left", padx=10)

        def buscar_endereco_click():
            cep_digitado = txt_cep.get().strip()
            end = buscar_cep(cep_digitado)
            if end:
                txt_endereco.delete(0, tk.END)
                txt_endereco.insert(0, end["completo"])
                lbl_endereco_auto.config(text=f"✅ {end['cidade']}/{end['uf']}", fg="green")
            else:
                lbl_endereco_auto.config(text="❌ CEP não encontrado", fg="red")

        tk.Button(frm_cep, text="🔍 Buscar CEP", command=buscar_endereco_click, bg="#3498db", fg="white").pack(side="right")

        tk.Label(jan, text="Endereço Completo:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        txt_endereco = tk.Entry(jan, width=65)
        txt_endereco.pack(pady=3, padx=25)
        if dados: txt_endereco.insert(0, dados.get("endereco",""))

        def salvar():
            if not txt_nome.get().strip():
                messagebox.showwarning("Aviso", "Digite o nome!")
                return
            if dados:
                dados["nome"] = txt_nome.get().strip()
                dados["telefone"] = txt_tel.get().strip()
                dados["cep"] = txt_cep.get().strip()
                dados["endereco"] = txt_endereco.get().strip()
            else:
                proximo_id = max([x["id"] for x in tbl_clientes], default=0) + 1
                tbl_clientes.append({
                    "id": proximo_id,
                    "nome": txt_nome.get().strip(),
                    "telefone": txt_tel.get().strip(),
                    "cep": txt_cep.get().strip(),
                    "endereco": txt_endereco.get().strip()
                })
            salvar_dados()
            recarregar()
            jan.destroy()
            messagebox.showinfo("✅ Sucesso!", "Cliente salvo com sucesso!")

        tk.Button(jan, text="💾 SALVAR", command=salvar, bg="#27ae60", fg="white", 
                  font=("Arial",11,"bold"), width=25, height=2).pack(pady=20)

    def novo():
        formulario_cliente("➕ Cadastrar Novo Cliente")

    def editar():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente na tabela!")
            return
        item = tabela.item(sel[0])["values"]
        cli = next((x for x in tbl_clientes if x["id"] == item[0]), None)
        formulario_cliente(f"✏️ Editar Cliente — ID {cli['id']}", cli)

    def excluir():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente na tabela!")
            return
        item = tabela.item(sel[0])["values"]
        if messagebox.askyesno("⚠️ Confirmar Exclusão", 
            f"Excluir cliente: {item[1]}?\n\n⚠️ Todos os pets e atendimentos vinculados também serão excluídos!"):
            apagados = exclusao_cascata("cliente", item[0])
            tbl_clientes[:] = [x for x in tbl_clientes if x["id"] != item[0]]
            salvar_dados()
            recarregar()
            messagebox.showinfo("✅ Excluído!", f"Cliente removido!\n{apagados} pet(s) também excluído(s).")

    frm_botoes = tk.Frame(janela, pady=12)
    frm_botoes.pack()
    tk.Button(frm_botoes, text="➕ NOVO", command=novo, bg="#27ae60", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=0, padx=8)
    tk.Button(frm_botoes, text="✏️ EDITAR", command=editar, bg="#f39c12", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=1, padx=8)
    tk.Button(frm_botoes, text="🗑️ EXCLUIR", command=excluir, bg="#e74c3c", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=2, padx=8)

# ==================================================
# 🐾 TELA PETS — FICHA COMPLETA ATUALIZADA
# ==================================================
def tela_pets():
    janela = tk.Toplevel(root)
    janela.title("📋 Ficha Completa do Pet — Chave Estrangeira: tutor_id")
    janela.geometry("1100x500")

    # Tabela com TODOS os campos novos
    tabela = ttk.Treeview(janela, columns=("id","nome","nasc","idade","raca","cor","tutor_id","tutor","ultima","retorno"), show="headings")
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Nome do Pet")
    tabela.heading("nasc", text="Nascimento")
    tabela.heading("idade", text="Idade")
    tabela.heading("raca", text="Raça")
    tabela.heading("cor", text="Cor")
    tabela.heading("tutor_id", text="FK Tutor-ID")
    tabela.heading("tutor", text="Tutor")
    tabela.heading("ultima", text="Última Consulta")
    tabela.heading("retorno", text="Retorno")
    
    tabela.column("id", width=40)
    tabela.column("nome", width=110)
    tabela.column("nasc", width=90)
    tabela.column("idade", width=100)
    tabela.column("raca", width=110)
    tabela.column("cor", width=90)
    tabela.column("tutor_id", width=70)
    tabela.column("tutor", width=160)
    tabela.column("ultima", width=110)
    tabela.column("retorno", width=110)
    tabela.pack(fill="both", expand=True)

    def recarregar():
        for i in tabela.get_children(): tabela.delete(i)
        for p in buscar_pets_com_tutor():
            tabela.insert("", "end", values=(
                p["id"], 
                p["nome"], 
                p.get("nascimento",""), 
                p.get("idade_calculada","---"),
                p.get("raca",""), 
                p.get("cor",""), 
                p["tutor_id"], 
                p["tutor_nome"],
                p.get("ultima_consulta",""),
                p.get("retorno","")
            ))

    recarregar()

    # ==================================================
    # FORMULÁRIO COM TODOS OS CAMPOS NOVOS
    # ==================================================
    def formulario_pet(titulo, dados=None):
        jan = tk.Toplevel(janela)
        jan.title(titulo)
        jan.geometry("520x580")

        tk.Label(jan, text="🔑 ID do Tutor (Cliente):", font=("Arial",10,"bold"), fg="#2c3e50").pack(pady=(15,3), anchor="w", padx=25)
        tid = tk.Entry(jan, width=55)
        tid.pack(pady=3, padx=25)
        if dados: tid.insert(0, dados["tutor_id"])

        tk.Label(jan, text="🐾 Nome do Pet:", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        nome = tk.Entry(jan, width=55)
        nome.pack(pady=3, padx=25)
        if dados: nome.insert(0, dados["nome"])

        tk.Label(jan, text="📅 Nascimento (DD/MM/AAAA):", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        nasc = tk.Entry(jan, width=55)
        nasc.pack(pady=3, padx=25)
        if dados: nasc.insert(0, dados.get("nascimento",""))

        tk.Label(jan, text="🐶 Raça:", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        raca = tk.Entry(jan, width=55)
        raca.pack(pady=3, padx=25)
        if dados: raca.insert(0, dados.get("raca",""))

        tk.Label(jan, text="🎨 Cor:", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        cor = tk.Entry(jan, width=55)
        cor.pack(pady=3, padx=25)
        if dados: cor.insert(0, dados.get("cor",""))

        tk.Label(jan, text="🧶 Pelagem:", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        pelagem = tk.Entry(jan, width=55)
        pelagem.pack(pady=3, padx=25)
        if dados: pelagem.insert(0, dados.get("pelagem",""))

        tk.Label(jan, text="💉 Vacinas:", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        vacinas = tk.Text(jan, width=55, height=4)
        vacinas.pack(pady=3, padx=25)
        if dados and dados.get("vacinas"): vacinas.insert("1.0", dados["vacinas"])

        tk.Label(jan, text="🏥 Última Consulta (DD/MM/AAAA):", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        ultima = tk.Entry(jan, width=55)
        ultima.pack(pady=3, padx=25)
        if dados: ultima.insert(0, dados.get("ultima_consulta",""))

        tk.Label(jan, text="📆 Retorno Agendado (DD/MM/AAAA):", font=("Arial",10,"bold")).pack(pady=(8,3), anchor="w", padx=25)
        retorno = tk.Entry(jan, width=55)
        retorno.pack(pady=3, padx=25)
        if dados: retorno.insert(0, dados.get("retorno",""))

        def salvar():
            try: tutor_id = int(tid.get())
            except:
                messagebox.showerror("Erro", "ID do Tutor deve ser número!"); return
            if not validar_chave_estrangeira("pets", "tutor_id", tutor_id): return
            if not nome.get().strip():
                messagebox.showwarning("Aviso", "Digite o nome do Pet!"); return

            if dados:
                dados["tutor_id"] = tutor_id
                dados["nome"] = nome.get().strip()
                dados["nascimento"] = nasc.get().strip()
                dados["raca"] = raca.get().strip()
                dados["cor"] = cor.get().strip()
                dados["pelagem"] = pelagem.get().strip()
                dados["vacinas"] = vacinas.get("1.0", tk.END).strip()
                dados["ultima_consulta"] = ultima.get().strip()
                dados["retorno"] = retorno.get().strip()
            else:
                proximo_id = max([x["id"] for x in tbl_pets], default=0) + 1
                tbl_pets.append({
                    "id": proximo_id,
                    "tutor_id": tutor_id,
                    "nome": nome.get().strip(),
                    "nascimento": nasc.get().strip(),
                    "raca": raca.get().strip(),
                    "cor": cor.get().strip(),
                    "pelagem": pelagem.get().strip(),
                    "vacinas": vacinas.get("1.0", tk.END).strip(),
                    "ultima_consulta": ultima.get().strip(),
                    "retorno": retorno.get().strip()
                })
            salvar_dados()
            recarregar()
            jan.destroy()
            messagebox.showinfo("✅ Sucesso!", "Ficha do Pet salva com sucesso!\nIdade calculada automaticamente!")

        tk.Button(jan, text="💾 SALVAR FICHA", command=salvar, bg="#27ae60", fg="white", 
                  font=("Arial",11,"bold"), width=28, height=2).pack(pady=15)

    def novo():
        formulario_pet("➕ Cadastrar Novo Pet — Ficha Completa")

    def editar():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um Pet na tabela!"); return
        item = tabela.item(sel[0])["values"]
        pet = next((x for x in tbl_pets if x["id"] == item[0]), None)
        formulario_pet(f"✏️ Editar Ficha do Pet — ID {pet['id']} — {pet['nome']}", pet)

    def excluir():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um Pet na tabela!"); return
        item = tabela.item(sel[0])["values"]
        if messagebox.askyesno("⚠️ Confirmar Exclusão", f"Excluir Pet: {item[1]}?"):
            tbl_pets[:] = [x for x in tbl_pets if x["id"] != item[0]]
            salvar_dados()
            recarregar()
            messagebox.showinfo("✅ Excluído!", "Pet removido!")

    frm_botoes = tk.Frame(janela, pady=12)
    frm_botoes.pack()
    tk.Button(frm_botoes, text="➕ NOVO", command=novo, bg="#27ae60", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=0, padx=8)
    tk.Button(frm_botoes, text="✏️ EDITAR", command=editar, bg="#f39c12", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=1, padx=8)
    tk.Button(frm_botoes, text="🗑️ EXCLUIR", command=excluir, bg="#e74c3c", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=2, padx=8)

# ==================================================
# 📦 TELA ESTOQUE — EDITAR + EXCLUIR
# ==================================================
def tela_estoque():
    janela = tk.Toplevel(root)
    janela.title("📋 Tabela de Estoque")
    janela.geometry("650x420")

    tabela = ttk.Treeview(janela, columns=("id","nome","qtd","preco"), show="headings")
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Produto")
    tabela.heading("qtd", text="Quantidade")
    tabela.heading("preco", text="Preço R$")
    tabela.column("id", width=40)
    tabela.column("nome", width=300)
    tabela.column("qtd", width=110)
    tabela.column("preco", width=130)
    tabela.pack(fill="both", expand=True)

    def recarregar():
        for i in tabela.get_children(): tabela.delete(i)
        for p in tbl_estoque:
            tag = "alerta" if p["quantidade"] <= 3 else ""
            tabela.insert("", "end", values=(p["id"], p["nome"], p["quantidade"], f"{p['preco_venda']:.2f}"), tags=(tag,))
        tabela.tag_configure("alerta", background="#ffcccc")

    recarregar()

    def formulario_produto(titulo, dados=None):
        jan = tk.Toplevel(janela)
        jan.title(titulo)
        jan.geometry("420x320")

        tk.Label(jan, text="Nome do Produto:", font=("Arial",10,"bold")).pack(pady=(15,3), anchor="w", padx=25)
        txt_nome = tk.Entry(jan, width=50)
        txt_nome.pack(pady=3, padx=25)
        if dados: txt_nome.insert(0, dados["nome"])

        tk.Label(jan, text="Quantidade:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        txt_qtd = tk.Entry(jan, width=50)
        txt_qtd.pack(pady=3, padx=25)
        if dados: txt_qtd.insert(0, dados["quantidade"])

        tk.Label(jan, text="Preço de Venda R$:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        txt_preco = tk.Entry(jan, width=50)
        txt_preco.pack(pady=3, padx=25)
        if dados: txt_preco.insert(0, f"{dados['preco_venda']:.2f}")

        def salvar():
            try:
                qtd = int(txt_qtd.get())
                preco = float(txt_preco.get().replace(",", "."))
            except:
                messagebox.showerror("Erro", "Digite valores numéricos válidos!"); return
            if not txt_nome.get().strip():
                messagebox.showwarning("Aviso", "Digite o nome do produto!"); return

            if dados:
                dados["nome"] = txt_nome.get().strip()
                dados["quantidade"] = qtd
                dados["preco_venda"] = preco
            else:
                proximo_id = max([x["id"] for x in tbl_estoque], default=0) + 1
                tbl_estoque.append({"id": proximo_id, "nome": txt_nome.get().strip(), 
                                    "quantidade": qtd, "preco_venda": preco})
            salvar_dados()
            recarregar()
            jan.destroy()
            messagebox.showinfo("✅ Sucesso!", "Produto salvo!")

        tk.Button(jan, text="💾 SALVAR", command=salvar, bg="#27ae60", fg="white", 
                  font=("Arial",11,"bold"), width=22, height=2).pack(pady=20)

    def novo():
        formulario_produto("➕ Novo Produto")

    def editar():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um produto!"); return
        item = tabela.item(sel[0])["values"]
        prod = next((x for x in tbl_estoque if x["id"] == item[0]), None)
        formulario_produto(f"✏️ Editar Produto — ID {prod['id']}", prod)

    def excluir():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um produto!"); return
        item = tabela.item(sel[0])["values"]
        if messagebox.askyesno("⚠️ Confirmar Exclusão", f"Excluir: {item[1]}?"):
            tbl_estoque[:] = [x for x in tbl_estoque if x["id"] != item[0]]
            salvar_dados()
            recarregar()
            messagebox.showinfo("✅ Excluído!", "Produto removido!")

    frm_botoes = tk.Frame(janela, pady=12)
    frm_botoes.pack()
    tk.Button(frm_botoes, text="➕ NOVO", command=novo, bg="#27ae60", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=0, padx=8)
    tk.Button(frm_botoes, text="✏️ EDITAR", command=editar, bg="#f39c12", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=1, padx=8)
    tk.Button(frm_botoes, text="🗑️ EXCLUIR", command=excluir, bg="#e74c3c", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=2, padx=8)

# ==================================================
# 📋 TELA ATENDIMENTOS — EDITAR + EXCLUIR + FK
# ==================================================
def tela_atendimentos():
    janela = tk.Toplevel(root)
    janela.title("📋 Tabela de Atendimentos — FK: pet_id")
    janela.geometry("950x420")

    tabela = ttk.Treeview(janela, columns=("id","pet_id","pet","tutor","servico","total","pag"), show="headings")
    tabela.heading("id", text="ID")
    tabela.heading("pet_id", text="FK Pet-ID")
    tabela.heading("pet", text="Pet")
    tabela.heading("tutor", text="Tutor")
    tabela.heading("servico", text="Serviço")
    tabela.heading("total", text="Total R$")
    tabela.heading("pag", text="Pagamento")
    tabela.column("id", width=40)
    tabela.column("pet_id", width=70)
    tabela.column("pet", width=110)
    tabela.column("tutor", width=140)
    tabela.column("servico", width=180)
    tabela.column("total", width=90)
    tabela.column("pag", width=100)
    tabela.pack(fill="both", expand=True)

    def recarregar():
        for i in tabela.get_children(): tabela.delete(i)
        for a in buscar_atendimentos_completos():
            tabela.insert("", "end", values=(a["id"], a["pet_id"], a["pet_nome"], 
                                              a["tutor_nome"], a["servico"], 
                                              f"{a['total']:.2f}", a["forma_pagamento"]))

    recarregar()

    def formulario_atendimento(titulo, dados=None):
        jan = tk.Toplevel(janela)
        jan.title(titulo)
        jan.geometry("480x400")

        tk.Label(jan, text="ID do Pet:", font=("Arial",10,"bold")).pack(pady=(15,3), anchor="w", padx=25)
        pid = tk.Entry(jan, width=50)
        pid.pack(pady=3, padx=25)
        if dados: pid.insert(0, dados["pet_id"])

        tk.Label(jan, text="Serviço Prestado:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        serv = tk.Entry(jan, width=50)
        serv.pack(pady=3, padx=25)
        if dados: serv.insert(0, dados["servico"])

        tk.Label(jan, text="Valor Total R$:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        val = tk.Entry(jan, width=50)
        val.pack(pady=3, padx=25)
        if dados: val.insert(0, f"{dados['total']:.2f}")

        tk.Label(jan, text="Forma de Pagamento:", font=("Arial",10,"bold")).pack(pady=(10,3), anchor="w", padx=25)
        pag = ttk.Combobox(jan, values=["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Transferência"])
        pag.set("Pix")
        pag.pack(pady=3, padx=25)
        if dados: pag.set(dados["forma_pagamento"])

        def salvar():
            try: pet_id = int(pid.get()); valor = float(val.get().replace(",", "."))
            except: messagebox.showerror("Erro", "Valores inválidos!"); return
            if not validar_chave_estrangeira("atendimentos", "pet_id", pet_id): return
            if not serv.get().strip(): messagebox.showwarning("Aviso", "Informe o serviço!"); return

            if dados:
                dados["pet_id"] = pet_id
                dados["servico"] = serv.get().strip()
                dados["total"] = valor
                dados["forma_pagamento"] = pag.get()
            else:
                proximo_id = max([x["id"] for x in tbl_atendimentos], default=0) + 1
                pet = next((p for p in tbl_pets if p["id"] == pet_id), None)
                tbl_atendimentos.append({
                    "id": proximo_id,
                    "pet_id": pet_id,
                    "servico": serv.get().strip(),
                    "valor_servico": valor,
                    "valor_produtos": 0,
                    "total": valor,
                    "forma_pagamento": pag.get()
                })
            salvar_dados()
            recarregar()
            jan.destroy()
            messagebox.showinfo("✅ Sucesso!", "Atendimento registrado!")

        tk.Button(jan, text="💾 SALVAR", command=salvar, bg="#27ae60", fg="white", 
                  font=("Arial",11,"bold"), width=25, height=2).pack(pady=20)

    def novo():
        formulario_atendimento("➕ Novo Atendimento")

    def editar():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um atendimento!"); return
        item = tabela.item(sel[0])["values"]
        atd = next((x for x in tbl_atendimentos if x["id"] == item[0]), None)
        formulario_atendimento(f"✏️ Editar Atendimento — ID {atd['id']}", atd)

    def excluir():
        sel = tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um atendimento!"); return
        item = tabela.item(sel[0])["values"]
        if messagebox.askyesno("⚠️ Confirmar Exclusão", f"Excluir atendimento ID {item[0]}?"):
            tbl_atendimentos[:] = [x for x in tbl_atendimentos if x["id"] != item[0]]
            salvar_dados()
            recarregar()
            messagebox.showinfo("✅ Excluído!", "Atendimento removido!")

    frm_botoes = tk.Frame(janela, pady=12)
    frm_botoes.pack()
    tk.Button(frm_botoes, text="➕ NOVO", command=novo, bg="#27ae60", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=0, padx=8)
    tk.Button(frm_botoes, text="✏️ EDITAR", command=editar, bg="#f39c12", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=1, padx=8)
    tk.Button(frm_botoes, text="🗑️ EXCLUIR", command=excluir, bg="#e74c3c", fg="white", 
              font=("Arial",10,"bold"), width=18, height=2).grid(row=0, column=2, padx=8)

# ==================================================
# 🏠 TELA PRINCIPAL / DASHBOARD
# ==================================================
carregar_dados()

root = tk.Tk()
root.title("🏥 SISTEMA CLÍNICA PET — Ficha do Pet Completa")
root.geometry("780x530")

tk.Label(root, text="🏥 SISTEMA DE GERENCIAMENTO — CLÍNICA PET", 
         font=("Arial",17,"bold"), fg="#2c3e50").pack(pady=(15,5))
tk.Label(root, text="📋 Ficha Completa do Pet: Raça, Cor, Pelagem, Vacinas, Idade, Última Consulta e Retorno", 
         font=("Arial",9), fg="#666666").pack(pady=(0,10))

frame_stats = tk.Frame(root, relief="ridge", bd=3, padx=25, pady=18, bg="#f8f9fa")
frame_stats.pack(fill="x", padx=20)

lbl_qtd_clientes = tk.Label(frame_stats, text="👥 Clientes: 0", font=("Arial",12,"bold"), fg="#2980b9")
lbl_qtd_clientes.grid(row=0, column=0, padx=20)
lbl_qtd_pets = tk.Label(frame_stats, text="🐾 Pets: 0", font=("Arial",12,"bold"), fg="#8e44ad")
lbl_qtd_pets.grid(row=0, column=1, padx=20)
lbl_qtd_atend = tk.Label(frame_stats, text="📋 Atendimentos: 0", font=("Arial",12,"bold"), fg="#16a085")
lbl_qtd_atend.grid(row=0, column=2, padx=20)
lbl_faturamento = tk.Label(frame_stats, text="💰 Faturado: R$ 0.00", font=("Arial",13,"bold"), fg="#27ae60")
lbl_faturamento.grid(row=1, column=0, columnspan=3, pady=(12,0))

atualizar_dashboard()

frame_botoes = tk.Frame(root, pady=20)
frame_botoes.pack()
estilo = {"width":26, "height":3, "font":("Arial",11,"bold")}

tk.Button(frame_botoes, text="👥  CLIENTES\n(CADASTRO COMPLETO)", command=tela_clientes, 
          bg="#3498db", fg="white", **estilo).grid(row=0, column=0, padx=12, pady=10)
tk.Button(frame_botoes, text="🐾  PETS\n(FICHA COMPLETA)", command=tela_pets, 
          bg="#9b59b6", fg="white", **estilo).grid(row=0, column=1, padx=12, pady=10)
tk.Button(frame_botoes, text="📦  ESTOQUE\n(PRODUTOS)", command=tela_estoque, 
          bg="#f39c12", fg="white", **estilo).grid(row=1, column=0, padx=12, pady=10)
tk.Button(frame_botoes, text="📋  ATENDIMENTOS\n(SERVIÇOS)", command=tela_atendimentos, 
          bg="#1abc9c", fg="white", **estilo).grid(row=1, column=1, padx=12, pady=10)

tk.Label(root, text="✅ Idade calculada automaticamente | ✅ Vacinas | ✅ Última Consulta e Retorno | ✅ Chaves Estrangeiras", 
         font=("Arial",9), fg="#555555").pack(pady=(5,10))

root.mainloop()