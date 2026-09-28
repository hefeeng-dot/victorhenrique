# CLAUDE.md — Site de iscas de @victor.henriquef

Site estático hospedado na Vercel. Cada post do Instagram/TikTok termina com "Comente CÓDIGO que eu te mando no direct", e cada código tem uma página aqui (`/codigo/`). O `index.html` cataloga todas.

**Nome público: Biblioteca.** Para quem acessa o site, nunca use a palavra "isca": o site é a "Biblioteca" e cada página é um material/post. "Isca" fica só no uso interno (arquivos, commits, esta documentação). O nome público vem de `library_name` em `site.json`.

Repositório: github.com/hefeeng-dot/victorhenrique (**público**). Responda sempre em português do Brasil.

## Regras que nunca se quebram

1. **Este repositório é público.** Nunca coloque aqui dados pessoais, financeiros, tokens, senhas, chaves de API ou arquivos `.env`. Se encontrar algo assim, pare e avise.
2. **Não misture com o repositório `central`.** Ele é o painel pessoal privado do Victor (gastos, cartões, tarefas). Nada dele entra aqui, nem links para ele.
3. **Não edite os `index.html` à mão.** Eles são gerados pelo `build.py`. Mude o conteúdo em `content/*.json` (ou o estilo em `assets/style.css`) e rode o build.
4. **Só publique afirmações que foram verificadas.** As iscas são enviadas a seguidores. Se um link, preço ou descrição não puder ser confirmado, marque o item com `"draft": true` em vez de publicar e avise o Victor.

## Estrutura

```
site.json          handle, textos do index, noindex
content/*.json     uma isca por arquivo (nome do arquivo = código em minúsculas)
assets/style.css   visual escuro premium: fundo quase preto, brilho e detalhes na cor de destaque do post, Inter + JetBrains Mono
build.py           gera index.html e <codigo>/index.html (só Python 3 padrão)
vercel.json        URLs limpas + noindex
```

A Vercel **não roda build**: ela publica os arquivos como estão. Por isso os HTML gerados precisam ir no commit.

## Formato de uma isca (`content/<codigo>.json`)

```json
{
  "code": "4TQZC",
  "title": "Título da isca",
  "summary": "Uma frase para o card do index.",
  "date": "AAAA-MM-DD",
  "accent": "#6B8F71",
  "verified": "DD/MM/AAAA",
  "intro": "Texto de abertura da página.",
  "items": [
    {
      "name": "Nome do item",
      "url": "https://exemplo.com",
      "sections": [
        {"label": "O que faz", "text": "..."},
        {"label": "Cuidado", "text": "...", "warn": true}
      ]
    },
    {
      "name": "Item com prompt copiável",
      "sections": [{"label": "Quando usar", "text": "..."}],
      "prompt": "Texto que ganha o botão 'Copiar prompt'."
    }
  ],
  "closing": "Texto opcional no fim da página."
}
```

- Campos opcionais do item: `"chips": ["★ 107 mil", "Licença MIT"]` (selos abaixo do nome; o primeiro ganha a cor do post).
- Uma seção pode ter `text`, `list` (lista de frases) e `code` (lista de `{"caption": "opcional", "code": "comando"}`, cada bloco ganha botão "Copiar"). Pode combinar os três.
- `"warn": true` destaca a seção em vermelho (use para riscos reais).
- **Hierarquia da página:** o build organiza cada item em camadas, pelo rótulo da seção. "O que é/O que faz" vira o texto principal; "Casos de uso/Quando usar" vira o bloco de cartões; `warn` fica sempre visível; "Antes de começar" e toda seção com `code` vão para o bloco recolhido "Como instalar e usar" (também as seções comuns que vierem depois do primeiro comando). "Sobre estes casos de uso" logo após os casos de uso vira nota deles. Para forçar um papel, use `"type"`: `lead`, `uses`, `reqs`, `step`, `warn` ou `info`. Páginas com 3 itens ou mais ganham o resumo "Neste material" no topo.
- `"draft": true` no item deixa ele fora da página. Para ver com rascunhos: `python3 build.py --drafts`.
- `verified` é a data em que os links foram conferidos. Mostre-a só se realmente conferiu.
- Cores de destaque usadas: terracota `#D97757`, sage `#6B8F71`, slate `#5B7C99`, heather `#A66B7A`. Varie entre os posts.

## Como adicionar uma isca nova

Quando o Victor colar um JSON de isca (ou pedir para criar uma):

1. Salve em `content/<codigo-em-minusculas>.json`.
2. Valide: o JSON precisa ser válido e ter `code`, `title`, `summary`, `date`, `intro` e `items`.
3. Rode `python3 build.py` e leia os avisos (por exemplo, itens em rascunho).
4. Confira `git status`: devem mudar apenas o JSON, o `index.html` e a pasta do novo código.
5. Mostre ao Victor o resumo do que vai ser publicado e **espere a confirmação** antes do push.
6. Commit com mensagem curta, por exemplo `isca: 4TQZC — 7 sites`, e `git push origin main`.
7. A Vercel publica sozinha em cerca de um minuto. Confirme que `/<codigo>/` abre.

## Estado atual

- Páginas: `/4tqzc/` (sites testados) e `/discorda/` (5 prompts para a IA discordar).
- **Pendência:** em `content/4tqzc.json` o item **Koha.wtf** está como `draft`. O endereço abriu o portfólio pessoal de outra pessoa, não o gerador de sites aleatórios do roteiro original. Só tire o `draft` depois que o Victor confirmar o link correto. Nesse momento o título pode voltar a "Os 7 sites testados".
- `noindex` está ligado (não aparece no Google). Isso **não é proteção de acesso**: quem tiver o link abre.

## Monetização futura

O Victor pretende, se for viável, criar uma assinatura para as iscas. Página estática não segura conteúdo pago. Isso exigirá login e pagamento (por exemplo, funções serverless da Vercel ou uma plataforma de assinatura na frente). Ao mexer na estrutura, mantenha o conteúdo separado da apresentação, como está hoje, e não construa proteção falsa (senha no front-end, por exemplo).
