# Padrão de Versionamento do Projeto

Este documento define o fluxo simples de versionamento, branches, commits, tags e lançamento de versões deste projeto.

O projeto é um app pessoal, então o objetivo é manter o processo leve: trabalhar no dia a dia na `develop` e usar a `main` apenas para versões estáveis.

---

# 1. Regra principal

Não desenvolver diretamente na branch `main`.

O fluxo padrão é:

```text
develop -> main
```

A `develop` é a branch de trabalho diário.

A `main` é a branch estável, usada apenas quando uma versão oficial estiver pronta.

Branches extras podem ser criadas só em casos específicos, como testes arriscados, mudanças grandes ou quando for útil isolar uma alteração. Para o uso normal do app, trabalhar direto na `develop` é suficiente.

---

# 2. Branches principais

## `develop`

A branch `develop` representa a versão em desenvolvimento.

Usar a `develop` para:

* criar funcionalidades;
* corrigir bugs;
* ajustar interface;
* refatorar código;
* atualizar documentação;
* testar ideias pequenas e seguras.

Antes de começar uma tarefa, conferir:

```bash
git checkout develop
git status --short --branch
```

Se houver mudanças locais, preservar o que já existe e evitar misturar alterações sem necessidade.

---

## `main`

A branch `main` representa a versão estável e oficial do projeto.

Só deve receber código que:

* esteja funcionando;
* tenha sido testado minimamente;
* não tenha erro crítico conhecido;
* represente uma versão segura do app.

Não trabalhar diretamente na `main`.

Quando a `develop` estiver estável, ela pode ser integrada na `main` como uma nova versão oficial.

---

# 3. Branches extras opcionais

Como o projeto é pessoal, branches por tarefa não são obrigatórias.

Criar uma branch extra apenas quando ajudar de verdade, por exemplo:

* testar uma mudança grande sem bagunçar a `develop`;
* fazer uma refatoração arriscada;
* experimentar uma ideia que talvez seja descartada;
* separar uma correção urgente enquanto a `develop` estiver instável.

Prefixos sugeridos, se uma branch extra for criada:

```text
feat/       nova funcionalidade
fix/        correção de bug
refactor/   melhoria interna sem mudar comportamento
docs/       documentação
chore/      configuração ou manutenção
style/      ajuste visual ou formatação
test/       testes
```

Exemplos:

```text
feat/recompensas
fix/salvamento-tarefas
refactor/storage
docs/versionamento
```

Depois de concluir a mudança, integrar a branch extra de volta na `develop`.

---

# 4. Padrão de commits

Usar commits pequenos, claros e objetivos.

Formato:

```text
tipo: descrição curta da alteração
```

Tipos principais:

```text
feat: nova funcionalidade
fix: correção de bug
refactor: melhoria interna sem mudar comportamento
docs: documentação
chore: configuração ou manutenção
style: ajuste visual ou formatação
test: testes
```

Exemplos bons:

```text
feat: adiciona cadastro de tarefas
feat: adiciona sistema de pontos
fix: corrige salvamento de tarefas concluídas
fix: corrige duplicação de pontos
refactor: separa lógica de tarefas em service
docs: atualiza versionamento
chore: configura gitignore
style: melhora layout da lista de tarefas
```

Evitar commits genéricos como:

```text
teste
alterações
arrumei coisas
agora vai
final
mudanças
```

O histórico do Git deve permitir entender o que foi feito sem precisar abrir todos os arquivos.

---

# 5. Versionamento

O projeto usa versionamento semântico simples.

Formato:

```text
MAJOR.MINOR.PATCH
```

Exemplos:

```text
v0.1.0
v0.2.0
v0.2.1
v1.0.0
```

## MAJOR

Representa uma mudança grande no projeto.

Exemplo:

```text
v1.0.0 -> v2.0.0
```

Usar quando houver mudança muito grande na estrutura, arquitetura ou comportamento principal do app.

## MINOR

Representa uma nova funcionalidade relevante.

Exemplo:

```text
v0.1.0 -> v0.2.0
```

Usar quando adicionar algo importante, como:

* categorias;
* recompensas;
* histórico;
* streak;
* prioridades;
* nova tela relevante.

## PATCH

Representa uma correção pequena ou ajuste simples.

Exemplo:

```text
v0.2.0 -> v0.2.1
```

Usar para:

* correção de bugs;
* ajustes visuais pequenos;
* melhoria de texto;
* pequenos ajustes internos;
* correção de salvamento;
* correção de comportamento inesperado.

---

# 6. Planejamento de versões do app

## `v0.1.0` - MVP básico

Primeira versão funcional do app.

Deve conter:

* adicionar tarefas;
* listar tarefas;
* marcar tarefas como concluídas;
* ganhar pontos ao concluir tarefas;
* salvar dados localmente.

## `v0.2.0` - Categorias e prioridades

Pode conter:

* categorias de tarefas;
* prioridade baixa, média e alta;
* organização visual melhor da lista;
* filtro ou separação por tipo de tarefa.

## `v0.3.0` - Histórico diário

Pode conter:

* registro de tarefas concluídas por dia;
* pontos acumulados por dia;
* visualização do histórico;
* tela ou seção de progresso diário.

## `v0.4.0` - Recompensas

Pode conter:

* cadastro de recompensas;
* custo em pontos para cada recompensa;
* resgate de recompensas;
* controle de pontos disponíveis.

## `v0.5.0` - Streak

Pode conter:

* sequência de dias ativos;
* bônus por manter rotina;
* exibição da sequência atual;
* perda de streak se o usuário não cumprir o mínimo diário.

## `v1.0.0` - Primeira versão estável

Versão pronta para apresentar como projeto sério.

Deve conter:

* MVP completo;
* interface minimamente organizada;
* salvamento funcionando;
* README claro;
* changelog atualizado;
* versionamento definido;
* sem bugs críticos conhecidos.

---

# 7. Tags no Git

Sempre que uma versão oficial for finalizada, criar uma tag.

Exemplo:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Ou para enviar todas as tags:

```bash
git push origin --tags
```

A tag marca uma versão oficial do projeto.

Resumo:

```text
commit normal = progresso
tag = versão oficial
```

---

# 8. Arquivo VERSION

O projeto deve ter um arquivo chamado `VERSION` na raiz.

Exemplo de conteúdo:

```text
0.1.0
```

Sempre que uma nova versão oficial for lançada, esse arquivo deve ser atualizado.

Exemplo:

```text
0.2.0
```

---

# 9. Changelog

O projeto deve ter um arquivo chamado `CHANGELOG.md`.

Exemplo:

```md
# Changelog

## v0.1.0

- Adiciona cadastro de tarefas
- Adiciona listagem de tarefas
- Adiciona conclusão de tarefas
- Adiciona sistema de pontos
- Adiciona salvamento local
```

Toda versão oficial deve ter uma seção no changelog.

Formato recomendado:

```md
## v0.2.0

- Adiciona categorias de tarefas
- Adiciona prioridade baixa, média e alta
- Melhora organização visual da lista
```

---

# 10. Fluxo de trabalho padrão

## 1. Trabalhar na `develop`

```bash
git checkout develop
git status --short --branch
```

Se quiser buscar atualizações do GitHub:

```bash
git pull origin develop
```

## 2. Fazer alterações

Fazer mudanças pequenas, organizadas e relacionadas ao objetivo atual.

Evitar misturar muitas coisas diferentes no mesmo commit.

## 3. Verificar

Antes de finalizar uma mudança, rodar uma verificação adequada ao tipo de alteração.

Exemplos:

```bash
python -m compileall .
```

```bash
python web_app.py
```

Para documentação, revisar o arquivo alterado já costuma ser suficiente.

## 4. Commitar alterações

```bash
git add .
git commit -m "tipo: descrição curta"
```

Exemplo:

```bash
git commit -m "docs: simplifica fluxo de versionamento"
```

## 5. Enviar para o GitHub

```bash
git push origin develop
```

---

# 11. Lançamento de nova versão

Quando a `develop` estiver estável e pronta para virar uma versão oficial:

```bash
git checkout main
git pull origin main
git merge develop
```

Atualizar o arquivo `VERSION`.

Atualizar o arquivo `CHANGELOG.md`.

Depois:

```bash
git add .
git commit -m "chore: prepara versão v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

Depois do lançamento, voltar para a `develop`:

```bash
git checkout develop
```

---

# 12. Regras para o Codex seguir

Ao trabalhar neste projeto, o Codex deve seguir estas regras:

1. Não modificar diretamente a branch `main`.

2. Usar a `develop` como branch padrão de trabalho.

3. Não criar branch por tarefa automaticamente, a menos que o usuário peça ou que a mudança seja grande, arriscada ou experimental.

4. Manter alterações pequenas e relacionadas ao objetivo atual.

5. Preservar mudanças locais já existentes no workspace.

6. Não reverter arquivos sem pedido explícito.

7. Fazer commits pequenos e objetivos quando o usuário pedir commit.

8. Usar mensagens de commit no padrão:

```text
tipo: descrição curta da alteração
```

9. Atualizar o `CHANGELOG.md` quando a alteração fizer parte de uma versão oficial.

10. Atualizar o arquivo `VERSION` apenas quando uma nova versão oficial for preparada.

11. Não criar tag para qualquer commit. Tags devem ser usadas somente para versões oficiais.

12. Antes de preparar uma versão, garantir que o app esteja minimamente funcional.

13. Se a mudança for experimental ou arriscada, sugerir uma branch extra antes de começar.

---

# 13. Quando criar nova versão

Criar nova versão quando houver um conjunto de mudanças relevantes e estáveis.

Exemplos:

```text
v0.1.0 -> MVP básico pronto
v0.2.0 -> adiciona categorias e prioridades
v0.3.0 -> adiciona histórico diário
v0.4.0 -> adiciona recompensas
v0.5.0 -> adiciona streak
v1.0.0 -> app estável e apresentável
```

Não criar nova versão para cada pequeno commit.

Para correções pequenas depois de uma versão, usar `PATCH`.

Exemplo:

```text
v0.2.0 -> v0.2.1
```

---

# 14. Resumo final

Modelo de branches:

```text
develop -> trabalho diário e desenvolvimento
main    -> versão estável e oficial
```

Branches extras são opcionais e só entram quando ajudarem de verdade.

Modelo de versões:

```text
v0.1.0 = MVP básico
v0.2.0 = nova feature relevante
v0.2.1 = correção pequena
v1.0.0 = versão estável e apresentável
```

Regra mais importante:

```text
Trabalhar na develop no dia a dia.
Levar para main apenas quando for lançar uma versão estável.
```
