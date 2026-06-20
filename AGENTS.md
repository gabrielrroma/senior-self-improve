# AGENTS.md

Instrucoes para agentes trabalhando neste projeto.

## Antes de alterar arquivos

- Leia `VERSIONAMENTO.md`.
- Confira `git status --short --branch`.
- Nao trabalhe diretamente na branch `main`.
- Crie uma branch especifica para a tarefa atual antes de editar codigo.

## Padrao de branches

- `feat/...` para funcionalidades novas.
- `fix/...` para correcoes.
- `refactor/...` para reorganizacao interna.
- `docs/...` para documentacao.
- `style/...` para ajustes visuais.
- `chore/...` para configuracao e manutencao.
- `test/...` para testes.

## Padrao de trabalho

- Mantenha alteracoes pequenas e relacionadas a uma unica tarefa.
- Preserve mudancas locais que ja existirem no workspace.
- Nao reverta arquivos sem pedido explicito.
- Antes de finalizar, rode uma verificacao adequada ao tipo de mudanca.
- Se a mudanca fizer parte de uma release oficial, atualize `CHANGELOG.md` e `VERSION`.

## Referencias do projeto

- `VERSIONAMENTO.md`: fluxo de branches, commits, tags e releases.
- `ROADMAP.md`: planejamento de produto e fases futuras.
- `README.md`: instrucoes basicas de execucao.
