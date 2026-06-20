# Padrão de Versionamento do Projeto

Este documento define o padrão de versionamento, branches, commits, tags e lançamento de versões deste projeto.

O objetivo é manter o projeto organizado, fácil de evoluir e seguro para desenvolver novas funcionalidades sem quebrar a versão principal.

---

# 1. Regra principal

Nunca desenvolver diretamente na branch `main`.

O fluxo padrão deve ser:

```text
branch específica -> develop -> main
```

A `main` deve representar a versão estável do app.

A `develop` deve representar a versão em desenvolvimento.

Cada funcionalidade, correção ou melhoria deve ser feita em uma branch separada.

---

# 2. Branches principais

## `main`

A branch `main` representa a versão estável e oficial do projeto.

Só deve receber código que:

* esteja funcionando;
* tenha sido testado minimamente;
* não tenha erro crítico conhecido;
* represente uma versão segura do app.

Não trabalhar diretamente na `main`.

---

## `develop`

A branch `develop` representa a versão em desenvolvimento.

Todas as features, correções e melhorias devem ser integradas primeiro na `develop`.

Quando a `develop` estiver estável, ela pode ser enviada para a `main` como uma nova versão oficial.

---

# 3. Branches de funcionalidade

Para criar uma nova funcionalidade, usar o prefixo `feat/`.

Formato:

```text
feat/nome-da-feature
```

Exemplos:

```text
feat/adicionar-tarefa
feat/concluir-tarefa
feat/sistema-pontos
feat/recompensas
feat/historico-diario
feat/streak
feat/categorias
feat/prioridade-tarefas
```

Cada branch de feature deve sair da `develop`.

Fluxo:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/nome-da-feature
```

---

# 4. Branches de correção

Para corrigir bugs, usar o prefixo `fix/`.

Formato:

```text
fix/nome-do-problema
```

Exemplos:

```text
fix/tarefa-nao-salva
fix/pontos-duplicados
fix/erro-ao-abrir-app
fix/lista-nao-atualiza
```

---

# 5. Branches de refatoração

Para melhorar código sem alterar comportamento, usar o prefixo `refactor/`.

Formato:

```text
refactor/nome-da-melhoria
```

Exemplos:

```text
refactor/organizar-services
refactor/separar-storage
refactor/melhorar-modelo-tarefa
refactor/organizar-estrutura-pastas
```

Usar `refactor/` quando a mudança melhora a estrutura interna, mas não adiciona uma funcionalidade visível ao usuário.

---

# 6. Branches de documentação

Para documentação, usar o prefixo `docs/`.

Formato:

```text
docs/nome-da-documentacao
```

Exemplos:

```text
docs/criar-readme
docs/atualizar-roadmap
docs/documentar-versionamento
docs/adicionar-changelog
```

---

# 7. Branches de configuração/manutenção

Para configurações, dependências e arquivos auxiliares, usar o prefixo `chore/`.

Formato:

```text
chore/nome-da-tarefa
```

Exemplos:

```text
chore/configurar-gitignore
chore/criar-requirements
chore/adicionar-arquivo-version
chore/organizar-ambiente-projeto
```

---

# 8. Branches de ajuste visual

Para mudanças visuais ou de interface que não alterem regra de negócio, usar o prefixo `style/`.

Formato:

```text
style/nome-do-ajuste
```

Exemplos:

```text
style/melhorar-layout
style/ajustar-espacamento
style/padronizar-botoes
style/melhorar-textos-interface
```

---

# 9. Padrão de commits

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
docs: adiciona instruções de instalação
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

# 10. Versionamento

O projeto deve usar versionamento semântico simples.

Formato:

```text
MAJOR.MINOR.PATCH
```

Exemplo:

```text
v0.1.0
v0.2.0
v0.2.1
v1.0.0
```

---

## MAJOR

Representa uma mudança grande no projeto.

Exemplo:

```text
v1.0.0 -> v2.0.0
```

Usar quando houver mudança muito grande na estrutura, arquitetura ou comportamento principal do app.

---

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

---

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

# 11. Planejamento de versões do app

## `v0.1.0` ? MVP básico

Primeira versão funcional do app.

Deve conter:

* adicionar tarefas;
* listar tarefas;
* marcar tarefas como concluídas;
* ganhar pontos ao concluir tarefas;
* salvar dados localmente.

---

## `v0.2.0` ? Categorias e prioridades

Pode conter:

* categorias de tarefas;
* prioridade baixa, média e alta;
* organização visual melhor da lista;
* filtro ou separação por tipo de tarefa.

---

## `v0.3.0` ? Histórico diário

Pode conter:

* registro de tarefas concluídas por dia;
* pontos acumulados por dia;
* visualização do histórico;
* tela ou seção de progresso diário.

---

## `v0.4.0` ? Recompensas

Pode conter:

* cadastro de recompensas;
* custo em pontos para cada recompensa;
* resgate de recompensas;
* controle de pontos disponíveis.

---

## `v0.5.0` ? Streak

Pode conter:

* sequência de dias ativos;
* bônus por manter rotina;
* exibição da sequência atual;
* perda de streak se o usuário não cumprir o mínimo diário.

---

## `v1.0.0` ? Primeira versão estável

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

# 12. Tags no Git

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

# 13. Arquivo VERSION

O projeto deve ter um arquivo chamado `VERSION` na raiz.

Exemplo de conteúdo:

```text
0.1.0
```

Sempre que uma nova versão for lançada, esse arquivo deve ser atualizado.

Exemplo:

```text
0.2.0
```

---

# 14. Changelog

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

# 15. Estrutura recomendada do projeto

Estrutura base recomendada:

```text
rotina-diaria/
?
??? app/
?   ??? main.py
?   ??? models/
?   ??? services/
?   ??? storage/
?   ??? ui/
?
??? data/
?   ??? tarefas.json
?
??? docs/
?   ??? roadmap.md
?   ??? versionamento.md
?
??? README.md
??? CHANGELOG.md
??? VERSION
??? requirements.txt
??? .gitignore
```

---

# 16. Fluxo de trabalho padrão

## 1. Atualizar a `develop`

```bash
git checkout develop
git pull origin develop
```

---

## 2. Criar uma branch nova

Para funcionalidade:

```bash
git checkout -b feat/nome-da-feature
```

Para correção:

```bash
git checkout -b fix/nome-do-problema
```

Para refatoração:

```bash
git checkout -b refactor/nome-da-refatoracao
```

Para documentação:

```bash
git checkout -b docs/nome-da-documentacao
```

---

## 3. Fazer alterações no código

Fazer mudanças pequenas, organizadas e relacionadas ao objetivo da branch.

Evitar misturar muitas coisas diferentes no mesmo commit.

---

## 4. Commitar alterações

```bash
git add .
git commit -m "feat: adiciona sistema de pontos"
```

---

## 5. Voltar para `develop`

```bash
git checkout develop
git pull origin develop
```

---

## 6. Fazer merge da branch

```bash
git merge feat/nome-da-feature
```

---

## 7. Enviar para o GitHub

```bash
git push origin develop
```

---

# 17. Lançamento de nova versão

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

---

# 18. Regras para o Codex seguir

Ao trabalhar neste projeto, o Codex deve seguir estas regras:

1. Não modificar diretamente a branch `main`.

2. Sempre sugerir ou criar uma branch específica para a tarefa atual.

3. Usar nomes de branches claros, seguindo os prefixos:

```text
feat/
fix/
refactor/
docs/
chore/
style/
test/
```

4. Não misturar funcionalidades diferentes na mesma alteração.

5. Fazer commits pequenos e objetivos.

6. Usar mensagens de commit no padrão:

```text
tipo: descrição curta da alteração
```

7. Atualizar o `CHANGELOG.md` quando a alteração fizer parte de uma versão oficial.

8. Atualizar o arquivo `VERSION` apenas quando uma nova versão oficial for preparada.

9. Não criar tag para qualquer commit. Tags devem ser usadas somente para versões oficiais.

10. Antes de preparar uma versão, garantir que o app esteja minimamente funcional.

11. Se a mudança for experimental, manter fora da `main`.

12. Se a tarefa for grande, dividir em etapas menores.

13. Ao sugerir mudanças, explicar em qual tipo de branch elas deveriam entrar.

14. Ao finalizar uma feature, orientar o merge para `develop`.

15. Ao preparar release, orientar o merge de `develop` para `main`.

---

# 19. Quando criar nova versão

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

# 20. Resumo final

Modelo de branches:

```text
main         -> versão estável
develop      -> versão em desenvolvimento
feat/...     -> funcionalidades novas
fix/...      -> correções
refactor/... -> melhorias internas
docs/...     -> documentação
chore/...    -> configuração/manutenção
style/...    -> ajustes visuais
test/...     -> testes
```

Modelo de versões:

```text
v0.1.0 = MVP básico
v0.2.0 = nova feature relevante
v0.2.1 = correção pequena
v1.0.0 = versão estável e apresentável
```

Regra mais importante:

```text
Não trabalhar direto na main.
Sempre desenvolver em branch específica, integrar na develop e só depois lançar na main.
```
