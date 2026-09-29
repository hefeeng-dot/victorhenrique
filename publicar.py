#!/usr/bin/env python3
"""Publica na Biblioteca os materiais novos ou alterados das pastas de posts.

Uso (dentro da pasta do repositório do site):
    python publicar.py            copia, gera o site, mostra o resumo e pede confirmação antes do push
    python publicar.py --teste    só confere os materiais, não copia nem publica nada

Na primeira vez ele pergunta onde fica a pasta "Posts" e guarda em publicar.local.json
(esse arquivo não vai para o GitHub). Só usa Python 3 padrão + Git.

Estrutura esperada:
    Posts/
      2026-09-28_DECISAO/
        slides/ ...
        post.md
        material/decisao.json      <- é este arquivo que vai para o site
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
CONTENT = REPO / "content"
CONFIG = REPO / "publicar.local.json"
OBRIGATORIOS = ["code", "title", "summary", "date", "intro", "items"]
PALAVRA_PROIBIDA = re.compile(r"\bisca", re.I)
SUSPEITOS = [  # coisas que nunca podem ir para um repositório público
    (re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_-]{16,}"), "parece uma chave de API"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "parece um token do GitHub"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "parece uma chave da AWS"),
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "parece um CPF"),
    (re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"), "parece um número de cartão"),
    (re.compile(r"senha\s*[:=]", re.I), "parece uma senha"),
]


def falha(msg):
    print(f"\n[PAROU] {msg}")
    sys.exit(1)


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        falha(f"git {' '.join(args)} deu erro:\n{r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def carregar_config():
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    else:
        print("Primeira vez por aqui.")
        pasta = input('Cole o caminho da pasta "Posts" (ex.: F:\\Meu Drive\\...\\Posts): ').strip().strip('"')
        url = input("Endereço do site, sem barra no fim (ex.: https://victorhenrique.vercel.app) [Enter para pular]: ").strip().rstrip("/")
        cfg = {"posts_dir": pasta, "site_url": url}
        CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Guardado em {CONFIG.name}. Para mudar depois, edite ou apague esse arquivo.\n")
    posts = Path(cfg["posts_dir"])
    if not posts.is_dir():
        falha(f'Não achei a pasta "{posts}". Confira o caminho em {CONFIG.name}.')
    return posts, cfg.get("site_url", "")


def conferir(arq: Path):
    """Retorna (dados, lista de problemas)."""
    problemas = []
    texto = arq.read_text(encoding="utf-8")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        return None, [f"JSON inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}"]
    faltam = [c for c in OBRIGATORIOS if not dados.get(c)]
    if faltam:
        problemas.append("faltam os campos: " + ", ".join(faltam))
    code = str(dados.get("code", ""))
    if code and arq.stem != code.lower():
        problemas.append(f'o nome do arquivo deveria ser "{code.lower()}.json"')
    if PALAVRA_PROIBIDA.search(texto):
        problemas.append('tem a palavra "isca" (use "material" ou "Biblioteca")')
    for padrao, motivo in SUSPEITOS:
        if padrao.search(texto):
            problemas.append(f"{motivo}: confira antes de publicar")
    return dados, problemas


def main():
    teste = "--teste" in sys.argv
    if not (REPO / "build.py").exists() or not CONTENT.is_dir():
        falha("Rode este script de dentro da pasta do repositório do site (onde está o build.py).")
    posts, site_url = carregar_config()

    arquivos = sorted(posts.glob("*/material/*.json"))
    if not arquivos:
        falha(f'Nenhum material encontrado em "{posts}\\<post>\\material\\*.json".')

    novos, alterados, erros, vistos = [], [], [], {}
    for arq in arquivos:
        dados, problemas = conferir(arq)
        rotulo = f"{arq.parent.parent.name}/material/{arq.name}"
        if arq.name in vistos:
            problemas.append(f"mesmo nome de arquivo em {vistos[arq.name]}")
        vistos[arq.name] = rotulo
        if problemas:
            erros.append((rotulo, problemas))
            continue
        destino = CONTENT / arq.name
        if not destino.exists():
            novos.append((arq, destino, dados))
        elif destino.read_bytes() != arq.read_bytes():
            alterados.append((arq, destino, dados))

    print(f"Materiais encontrados: {len(arquivos)}")
    for rotulo, problemas in erros:
        print(f"\n  [ERRO] {rotulo}")
        for p in problemas:
            print(f"     - {p}")
    for titulo, lista in (("Novos", novos), ("Alterados", alterados)):
        if lista:
            print(f"\n{titulo}:")
            for arq, _, d in lista:
                print(f"  + {d['code']:<10} {d['title']}")
    if erros:
        falha("Corrija os erros acima e rode de novo. Nada foi publicado.")
    if not (novos or alterados):
        print("\nNada novo para publicar. O site já está igual às pastas.")
        return
    if teste:
        print("\nModo --teste: tudo certo, nada foi copiado.")
        return

    # 1. copiar para content/
    for arq, destino, _ in novos + alterados:
        shutil.copyfile(arq, destino)

    # 2. gerar o site
    print("\nGerando o site (build.py)...")
    r = subprocess.run([sys.executable, "build.py"], cwd=REPO, text=True, encoding="utf-8")
    if r.returncode != 0:
        falha("O build.py deu erro. Nada foi enviado ao GitHub.")

    # 3. conferir o que mudou
    codigos = [d["code"].lower() for _, _, d in novos + alterados]
    todos = [f.stem for f in CONTENT.glob("*.json")]  # o build pode regravar páginas antigas
    permitidos = ("content/", "index.html", *[f"{c}/" for c in todos])
    mudancas = [l[3:].strip().strip('"') for l in git("status", "--porcelain", "--untracked-files=all").splitlines()]
    estranhos = [m for m in mudancas if not m.startswith(permitidos)]
    print("\nArquivos que vão para o GitHub:")
    for m in mudancas:
        print(f"  {'?? ' if m in estranhos else '   '}{m}")
    if estranhos:
        print("\n[ATENÇÃO] Os arquivos marcados com ?? não são de material. Eles NÃO serão enviados.")

    # 4. confirmar e enviar
    lista = ", ".join(d["code"] for _, _, d in novos + alterados)
    if input(f"\nPublicar {lista}? (s/n) ").strip().lower() not in ("s", "sim", "y"):
        print("Cancelado. Os arquivos copiados e gerados ficaram na pasta, sem commit.")
        return
    git("add", "--", *[m for m in mudancas if m not in estranhos])
    git("commit", "-m", f"biblioteca: {lista}")
    print("Enviando...")
    git("push", "origin", "HEAD")

    print("\nPublicado. A Vercel atualiza em cerca de 1 minuto.")
    for c in codigos:
        print(f"  {site_url}/{c}/" if site_url else f"  /{c}/")


if __name__ == "__main__":
    main()
