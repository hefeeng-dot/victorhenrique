# Como publicar um material na Biblioteca

Este guia funciona sem IA nenhuma. Você só precisa do material pronto (um arquivo `.json`) e de um dos três caminhos abaixo.

## Onde cada coisa fica

```
Posts/                          (no Google Drive: fonte de tudo)
  2026-09-28_DECISAO/
    slides/                     01.png, 02.png ... e vídeos
    post.md                     legenda, texto do direct, código, link
    material/decisao.json       o material que vai para o site
  2026-09-28_ACHADOS/
    ...

victorhenrique/                 (este repositório: FORA do Google Drive)
  content/*.json                cópia dos materiais publicados
  build.py                      gera as páginas
  publicar.py / publicar.bat    publica tudo o que for novo em Posts/
```

- Uma pasta por post: `AAAA-MM-DD_CODIGO`.
- O arquivo do material tem o nome do código em minúsculas: `decisao.json` para o código `DECISAO`.
- O repositório fica fora do Google Drive (por exemplo, `C:\dev\victorhenrique`). O Drive sincroniza a pasta `.git` arquivo por arquivo e pode corromper o repositório. O backup do site já é o GitHub.

## Caminho 1: o script (o normal)

1. Salve o material em `Posts/<post>/material/<codigo>.json`.
2. Dê dois cliques em `publicar.bat` (ou rode `python publicar.py` no terminal, dentro desta pasta).
3. Na primeira vez ele pergunta onde está a pasta `Posts` e o endereço do site. Isso fica guardado em `publicar.local.json`, que não vai para o GitHub.
4. Ele confere cada material, copia os novos, gera o site, mostra o que vai subir e pergunta **"Publicar? (s/n)"**.
5. Responda `s`. Em cerca de um minuto os links `/<codigo>/` estão no ar.

Para só conferir sem publicar nada: `python publicar.py --teste`.

O script para sozinho se o JSON estiver quebrado, se faltar campo obrigatório, se o nome do arquivo não bater com o código, se aparecer a palavra proibida para o público, ou se tiver algo parecido com senha, chave de API, CPF ou número de cartão.

## Caminho 2: manual no computador

Dentro da pasta do repositório:

```
copy "<caminho do post>\material\codigo.json" content\
python build.py
git status
git add content index.html codigo
git commit -m "biblioteca: CODIGO"
git push
```

No `git status` devem aparecer só o JSON, o `index.html` e a pasta do código. Se aparecer outra coisa, não suba.

## Caminho 3: só pelo navegador (sem instalar nada)

1. Abra o repositório no github.com e entre em `content`.
2. **Add file → Upload files**, arraste o `.json` e clique em **Commit changes**.
3. A aba **Actions** roda o `build.py` sozinha (arquivo `.github/workflows/build.yml`) e grava as páginas. Espere o ✓ verde e mais um minuto da Vercel.

Esse caminho não faz as conferências do script. Revise o JSON antes de subir.

## Formato do material

O formato completo está no `CLAUDE.md`. O mínimo: `code`, `title`, `summary`, `date`, `intro` e `items`. Item que você não conseguiu confirmar leva `"draft": true` e fica fora da página.

## Instalar do zero (computador novo)

1. **Python 3** (python.org). No Windows, marque "Add Python to PATH" na instalação.
2. **Git** (git-scm.com) ou o **GitHub Desktop**.
3. Clone o repositório numa pasta fora do Google Drive:
   ```
   git clone https://github.com/hefeeng-dot/victorhenrique.git C:\dev\victorhenrique
   ```
4. Na primeira vez que der `push`, o Git pede para entrar na conta do GitHub pelo navegador.

## Quando algo dá errado

- **"Não achei a pasta"**: o caminho mudou. Apague `publicar.local.json` e rode de novo.
- **Erro no push (rejected)**: alguém subiu algo antes (por exemplo, pelo navegador). Rode `git pull --rebase` e depois `git push`.
- **A página não mudou**: espere um minuto e recarregue com Ctrl+F5. Confira na Vercel se o último deploy terminou.
- **Material aparece sem um item**: o item está com `"draft": true`.
