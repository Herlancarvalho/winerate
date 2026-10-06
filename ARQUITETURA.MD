# Arquitetura e decisões técnicas — Wine Rate

Este documento explica **por que** certas escolhas foram feitas no projeto,
não apenas o que foi feito. O "o quê" e o "como rodar" estão no README.md.

## Visão geral

## Isolamento de dados por usuário

Cada usuário só pode ver, editar ou excluir os próprios vinhos. Isso é
garantido em **três camadas**, de propósito — se uma falhar, as outras
ainda protegem os dados:

1. **Queryset filtrado:** toda consulta ao banco já nasce filtrada pelo
   usuário logado (`Wine.objects.for_user(request.user)`). Um vinho de
   outro usuário nunca entra nem na lista de resultados.
2. **Permissão de objeto:** mesmo que o filtro acima falhasse, a permissão
   `IsOwner` confere, registro por registro, se o dono bate com quem
   está pedindo.
3. **O dono é definido no servidor:** ao criar um vinho, o campo `user`
   nunca vem do que o navegador envia — é sempre atribuído a partir da
   sessão de quem está logado. Isso impede que alguém tente "forjar"
   um vinho em nome de outra pessoa.

**Por que 404 e não 403:** quando alguém tenta acessar um vinho que não é
seu, a API responde "não encontrado" (404), não "sem permissão" (403).
Isso evita confirmar para um invasor que aquele ID existe.

## A IA só sugere, nunca salva sozinha

O endpoint `POST /api/wines/identify-label` lê a foto do rótulo e devolve
os campos extraídos (nome, safra, uva, país, região) — mas **não grava
nada no banco**. O registro só é criado quando o usuário revisa os dados
e confirma, clicando em "Salvar vinho" (`POST /api/wines`), um passo
separado e explícito.

**Por que separar os dois passos:**
- A IA pode errar ou ler algo que não está no rótulo. Separar leitura de
  gravação garante que um erro da IA nunca vira um registro salvo sem
  revisão humana.
- O usuário mantém controle total sobre o que entra no próprio histórico.

**Por que sanitizar a resposta da IA:** antes de devolver os dados ao
frontend, o servidor filtra cada campo por tipo e tamanho máximo
(`_sanitize()` em `label_vision.py`). A resposta de uma IA nunca é
tratada como texto confiável — mesmo vindo de um provedor sério, o
servidor valida antes de deixar passar.

## Autenticação dupla: sessão e token

O projeto aceita dois jeitos de autenticar:

- **Sessão com CSRF:** usada pelo próprio frontend (o navegador do usuário).
  Mais segura para esse caso, porque o cookie de sessão não fica exposto
  em código JavaScript.
- **Token:** usado por clientes externos (um app mobile futuro, uma
  integração de terceiros). Quem consome a API fora do navegador não
  tem como lidar com cookies e CSRF da mesma forma, então recebe um
  token para enviar em cada chamada (`Authorization: Token <token>`).

**Por que as duas:** a sessão é mais segura, mas só funciona dentro do
próprio site. O token é mais flexível, mas exige mais cuidado de quem
o guarda. Oferecer as duas cobre o caso de uso atual (o site) sem fechar
a porta para integrações futuras.

## Outras decisões de segurança

- **Senhas:** nunca armazenadas em texto puro. O Django aplica um hash
  (PBKDF2) — uma transformação de mão única, então nem o banco de dados
  sabe qual é a senha original.
- **Rate limiting:** rotas sensíveis (login, cadastro, leitura de rótulo)
  têm limite de chamadas por minuto, para dificultar ataques de força
  bruta e abuso da IA (que tem custo).
- **Mensagem genérica no login:** um e-mail ou senha errados devolvem a
  mesma mensagem ("E-mail ou senha inválidos"), para não revelar se
  aquele e-mail existe cadastrado.

