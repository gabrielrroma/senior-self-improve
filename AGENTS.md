# AGENTS.md

Instrucoes para agentes trabalhando neste projeto.

## Antes de alterar arquivos

- Leia `VERSIONAMENTO.md`.
- Confira `git status --short --branch`.
- Nao trabalhe diretamente na branch `main`.
- Use a branch `develop` como branch padrao de trabalho.
- Nao crie branch especifica por tarefa automaticamente.

## Padrao de branches

- `develop` para desenvolvimento do dia a dia.
- `main` para versoes estaveis e oficiais.
- Branches extras sao opcionais e devem ser usadas apenas quando ajudarem de verdade, como em mudancas grandes, arriscadas ou experimentais.

Se uma branch extra for necessaria, use prefixos claros:

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
