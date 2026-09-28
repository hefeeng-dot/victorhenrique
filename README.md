# Site de iscas — @victor.henriquef

Site estático: um index com o catálogo e uma página por código (`/4tqzc/`, `/discorda/`).
Sem dependências: o `build.py` usa só o Python 3 padrão.

## Estrutura
```
site.json            configurações (handle, textos do index, noindex)
content/*.json       uma isca por arquivo (o nome do arquivo = código em minúsculas)
assets/style.css     visual escuro premium (Inter + cor de destaque de cada post)
build.py             gera index.html e <codigo>/index.html
vercel.json          URLs limpas + noindex
```

## Criar uma isca nova
1. Copie um arquivo de `content/` (ex.: `4tqzc.json`) e renomeie para o código, em minúsculas.
2. Troque `code`, `title`, `summary`, `date`, `accent` (cor de destaque do post) e os `items`.
   - Item com link: `name`, `url` e `sections` (cada seção tem `label` e `text`; `"warn": true` destaca em vermelho).
   - Item com prompt para copiar: campo `prompt` (ganha o botão "Copiar prompt").
   - `"draft": true` deixa o item fora da página até você confirmar. Para ver com rascunhos: `python3 build.py --drafts`.
3. Rode `python3 build.py`.
4. Faça commit **incluindo os arquivos gerados** (o Vercel não roda build aqui) e dê push.

## Publicar (uma vez só)
1. Crie um **repositório novo** só para isto. Não use o `central`.
2. Suba esta pasta em `main`.
3. Na Vercel: Add New → Project → escolha o repositório → Framework Preset **Other** → sem Build Command → Deploy.
4. Opcional: aponte um domínio seu. A partir daí, cada push em `main` publica sozinho.

## Sobre privacidade e monetização
- `noindex` está ligado: as páginas não aparecem no Google. Isso **não é proteção**: quem tiver o link abre.
- Para cobrar no futuro é preciso proteger o acesso de verdade. Página estática não segura conteúdo pago. Caminhos comuns: login + pagamento com funções serverless da Vercel, ou uma plataforma de assinatura na frente. A estrutura em JSON facilita isso: o conteúdo já está separado da apresentação.
- Quando for cobrar, o index pode continuar público (só título e resumo) e o conteúdo completo fica atrás do acesso.

## Pendências
- `content/4tqzc.json`: o item **Koha.wtf** está como `draft`. O endereço abriu o portfólio de outra pessoa, não o gerador de sites aleatórios. Confirme o link correto, atualize o item e tire o `draft`. Depois disso, o título pode voltar a ser "Os 7 sites testados".
- As fontes vêm do Google Fonts. Sem internet, cai numa fonte do sistema.
