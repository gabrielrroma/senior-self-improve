# ROADMAP.md ? App de Rotina Diária com Recompensas

Este roadmap organiza a evolução do app de rotina diária com recompensas.

A ideia principal do projeto é criar um webapp local simples onde o usuário possa organizar suas tarefas, acompanhar seu progresso, ganhar pontos e se motivar a manter uma rotina mais consistente.

---

## Visão geral do projeto

O app deve permitir que o usuário:

* Cadastre tarefas diárias
* Marque tarefas como concluídas
* Ganhe pontos por tarefas concluídas
* Veja seu progresso diário
* Acompanhe histórico de desempenho
* Evolua com níveis, streaks e recompensas

---

## Objetivo do MVP

O MVP ideal é:

> Um webapp local onde o usuário adiciona tarefas do dia, define prioridade, marca como concluída, ganha pontos, vê o progresso diário e mantém tudo salvo localmente com um histórico simples.

---

## Status atual

Atualizado em 2026-07-05.

O app já cobre o MVP, organização visual, histórico diário, reset diário, gamificação inicial, metas diárias, recompensas personalizáveis com resgate, estatísticas semanais, meta semanal com bônus, conquistas iniciais, perfil local com avatar, tema claro/escuro e navegação por abas.

Também já houve limpeza do repositório: dados locais ficam fora do Git, cache Python fica ignorado, configurações pessoais do VS Code saíram do versionamento e o projeto ganhou `.editorconfig` e `.gitattributes`.

No workspace atual, a interface está em redesign visual: a navbar passou para uma sidebar inspirada no Todoist, e a tela de recompensas recebeu correção de layout desktop/mobile. Essas mudanças ainda precisam ser commitadas e publicadas.

Na prática, o produto está depois da Fase 7, com parte da Fase Técnica já iniciada. O próximo ciclo deveria ser menos sobre adicionar coisa nova e mais sobre estabilizar, testar e organizar.

---

## O que falta agora

Nota de 2026-07-05: a interface principal em `/` foi migrada para React mantendo o backend Python/API atual e as features existentes. O prototipo paralelo em `/react/` foi removido para evitar duas interfaces concorrentes.

## Migracao para React

Objetivo: manter a interface principal em React sem quebrar o backend Python/API atual e sem manter telas paralelas concorrentes.

Etapa 1 - Prototipo React inicial:

* [x] Criar uma rota paralela para a primeira tela React
* [x] Montar layout de board com colunas `Pendentes`, `Em foco` e `Concluidas`
* [x] Integrar a API existente para listar, adicionar, concluir, reabrir, editar, fixar e excluir tarefas
* [x] Permitir mover cards entre colunas com drag-and-drop simples
* [x] Remover o prototipo paralelo depois da migracao completa da tela principal

Etapa 2 - Base de tooling:

* [ ] Instalar/disponibilizar Node.js no ambiente local
* [ ] Criar base Vite + React quando o runtime estiver disponivel
* [ ] Migrar a interface React atual para componentes JSX versionados no fluxo Vite
* [ ] Definir processo de build para gerar arquivos estaticos servidos por `web_app.py`

Etapa 3 - Paridade com a interface atual:

* [x] Migrar modo foco Pomodoro para React
* [x] Migrar perfil, metas e estatisticas semanais
* [x] Migrar conquistas
* [x] Migrar recompensas e historico de resgates
* [x] Substituir a tela principal antiga somente depois de validar os fluxos principais

Etapa 4 - Polimento e confiabilidade:

* [x] Adicionar estados de loading, erro e vazio consistentes em todas as telas React
* [ ] Criar testes para o contrato frontend/API das tarefas
* [ ] Revisar acessibilidade, foco de teclado e contraste
* [x] Documentar no README como rodar a versao React

---

Prioridade alta:

* [ ] Commitar e publicar o redesign da sidebar e os ajustes da tela de recompensas
* [ ] Revisar a interface completa em tema claro e escuro
* [ ] Testar manualmente os fluxos principais no navegador
* [ ] Criar testes para CRUD de tarefas
* [ ] Criar testes para recompensas e resgates
* [ ] Criar testes para salvamento/carregamento dos JSONs

Prioridade média:

* [ ] Filtrar tarefas por prioridade
* [ ] Filtrar tarefas por categoria
* [ ] Criar backup automático dos dados antes de sobrescrever JSONs
* [x] Organizar o código em pastas (`services/`, `models/`, `web/`, `tests/`)
* [ ] Melhorar README com screenshots e estado atual do app

Prioridade baixa / ideias futuras:

* [ ] Modo foco / temporizador
* [ ] Recorrência semanal e mensal
* [ ] Lembretes e notificações locais
* [ ] Bônus por streak
* [ ] Recompensa diária aleatória
* [ ] Sincronização online, login e ranking

---

# Fase 1 ? MVP Funcional

Objetivo: criar a base mínima para o app funcionar bem.

## Tarefas

* [x] Criar modelo de tarefa

  * Nome
  * Status
  * Prioridade
  * Data de criação
  * Data de conclusão

* [x] Adicionar nova tarefa

* [x] Listar tarefas do dia

* [x] Marcar tarefa como concluída

* [x] Desmarcar tarefa concluída

* [x] Editar tarefa

* [x] Excluir tarefa

* [x] Confirmar antes de excluir uma tarefa

---

## Status das tarefas

* [x] Criar status `Pendente`

* [x] Criar status `Concluída`

* [x] Atualizar status ao concluir tarefa

* [x] Atualizar status ao desmarcar tarefa

---

## Sistema de pontos

* [x] Criar pontuação ao concluir tarefa

* [x] Definir pontos por prioridade:

  * Baixa: 5 pontos
  * Média: 10 pontos
  * Alta: 20 pontos

* [x] Somar pontos ao concluir tarefa

* [x] Remover pontos ao desmarcar tarefa

* [x] Mostrar pontos ganhos no dia

* [x] Mostrar pontos totais acumulados

---

## Salvamento local

* [x] Criar arquivo local para salvar os dados

* [x] Salvar tarefas localmente

* [x] Carregar tarefas ao abrir o app

* [x] Salvar pontos localmente

* [x] Carregar pontos ao abrir o app

* [x] Salvar automaticamente após mudanças importantes

---

## Resumo do dia

* [x] Mostrar quantidade de tarefas concluídas

* [x] Mostrar quantidade total de tarefas

* [x] Mostrar progresso do dia em porcentagem

* [x] Mostrar pontos ganhos hoje

* [x] Mostrar pontos totais

---

# Fase 2 ? Organização e Experiência

Objetivo: deixar o app mais organizado, visual e agradável de usar.

## Prioridades

* [x] Permitir escolher prioridade da tarefa:

  * Baixa
  * Média
  * Alta

* [x] Exibir prioridade na lista de tarefas

* [x] Usar prioridade para calcular pontos

* [x] Permitir editar prioridade da tarefa

---

## Categorias

* [x] Criar categorias básicas:

  * Estudos
  * Trabalho
  * Saúde
  * Casa
  * Lazer
  * Outros

* [x] Permitir selecionar categoria ao criar tarefa

* [x] Exibir categoria na lista de tarefas

* [x] Permitir editar categoria da tarefa

---

## Progresso visual

* [x] Criar barra de progresso diária

* [x] Atualizar barra ao concluir tarefa

* [x] Atualizar barra ao desmarcar tarefa

* [x] Mostrar porcentagem junto com a barra

---

## Histórico diário simples

* [x] Criar registro diário de progresso

* [x] Salvar resumo do dia:

  * Data
  * Tarefas concluídas
  * Total de tarefas
  * Pontos ganhos
  * Porcentagem concluída

* [x] Criar tela ou seção para visualizar histórico

---

## Reset diário

* [x] Detectar quando o dia mudou

* [x] Salvar resumo do dia anterior

* [x] Preparar lista de tarefas do novo dia

* [x] Manter pontos totais acumulados

* [x] Garantir que os dados antigos não sejam perdidos

---

# Fase 3 ? Gamificação Inicial

Objetivo: transformar o app em uma experiência mais motivadora.

## Sistema de níveis

* [x] Criar XP baseado nos pontos ganhos

* [x] Criar nível do usuário

* [x] Definir regra de evolução de nível

* [x] Mostrar nível atual na tela principal

* [x] Mostrar XP atual

* [x] Mostrar XP necessário para o próximo nível

---

## Streak

* [x] Criar contagem de dias seguidos usando o app

* [x] Definir regra para manter streak

* [x] Definir regra para perder streak

* [x] Mostrar streak atual na tela principal

* [ ] Dar bônus por manter streak

---

## Mensagens motivacionais

* [x] Criar mensagens para início do dia

* [x] Criar mensagens para metade do progresso

* [x] Criar mensagens para dia completo

* [x] Criar mensagens quando o usuário perde streak

* [x] Mostrar mensagem motivacional no resumo do dia

---

## Metas diárias

* [x] Criar meta diária de pontos

* [x] Mostrar progresso da meta diária

* [x] Dar feedback quando a meta diária for concluída

---

# Fase 4 ? Recompensas

Objetivo: permitir que o usuário use os pontos como recompensa real.

## Recompensas personalizáveis

* [x] Permitir criar recompensa personalizada

* [x] Definir custo em pontos para cada recompensa

* [x] Listar recompensas disponíveis

* [x] Editar recompensa

* [x] Excluir recompensa

---

## Loja de recompensas

* [x] Criar tela de loja de recompensas

* [x] Permitir resgatar recompensa usando pontos

* [x] Impedir resgate caso o usuário não tenha pontos suficientes

* [x] Separar pontos totais de pontos disponíveis

* [x] Registrar histórico de recompensas resgatadas

---

## Histórico de recompensas

* [x] Salvar data de resgate

* [x] Salvar nome da recompensa resgatada

* [x] Salvar custo em pontos da recompensa

* [x] Exibir histórico de recompensas resgatadas

---

# Fase 5 ? Estatísticas e Conquistas

Objetivo: fazer o usuário enxergar melhor sua evolução.

## Estatísticas semanais

* [x] Mostrar total de tarefas concluídas na semana

* [x] Mostrar total de pontos ganhos na semana

* [x] Mostrar melhor dia da semana

* [x] Mostrar categoria mais concluída

* [x] Mostrar taxa de conclusão semanal

---

## Metas semanais

* [x] Criar meta semanal de tarefas

* [x] Mostrar progresso da meta semanal

* [x] Dar bônus ao cumprir meta semanal

---

## Conquistas

* [x] Criar sistema de conquistas

* [x] Criar conquista de primeira tarefa concluída

* [x] Criar conquista de 7 dias seguidos

* [x] Criar conquista de 100 tarefas concluídas

* [x] Criar conquista de primeira semana perfeita

* [x] Criar conquista de 500 pontos acumulados

* [x] Mostrar conquistas desbloqueadas

---

# Fase 6 ? Recursos Extras

Objetivo: adicionar recursos mais avançados depois que a base estiver estável.

## Tarefas recorrentes

* [x] Criar tarefa recorrente diária

* [x] Recriar tarefa diária automaticamente

* [ ] Criar tarefa recorrente semanal

* [ ] Criar tarefa recorrente mensal

* [ ] Permitir editar recorrência

* [x] Permitir desativar recorrência

---

## Filtros

* [x] Filtrar tarefas por status

* [ ] Filtrar tarefas por prioridade

* [ ] Filtrar tarefas por categoria

* [x] Filtrar apenas tarefas pendentes

* [x] Filtrar apenas tarefas concluídas

---

## Modo foco / temporizador

* [ ] Criar temporizador para tarefa

* [ ] Permitir iniciar foco em uma tarefa

* [ ] Permitir pausar temporizador

* [ ] Permitir finalizar temporizador

* [ ] Registrar tempo gasto na tarefa

---

## Notificações

* [ ] Criar lembrete de tarefa

* [ ] Permitir definir horário da tarefa

* [ ] Notificar tarefa pendente

* [ ] Notificar meta diária incompleta

---

# Fase 7 ? Personalização Visual

Objetivo: melhorar a aparência e a experiência visual do app.

## Aparência

* [x] Melhorar layout da tela principal

* [x] Melhorar visual da lista de tarefas

* [x] Criar navegação lateral inspirada em apps de produtividade

* [x] Adaptar navegação para mobile sem rolagem horizontal

* [x] Melhorar layout da loja de recompensas no desktop

* [x] Corrigir layout responsivo da tela de recompensas

* [x] Destacar tarefas concluídas

* [x] Destacar tarefas de alta prioridade

* [x] Criar tema claro

* [x] Criar tema escuro

* [x] Permitir alternar entre tema claro e escuro

* [x] Criar perfil local com nome e avatar

---

## Recompensas diárias

* [ ] Criar recompensa diária aleatória

* [ ] Criar bônus de pontos diário

* [ ] Mostrar recompensa especial do dia

* [ ] Evitar repetir recompensa todos os dias

---

# Fase Técnica ? Qualidade e Organização

Objetivo: manter o projeto fácil de evoluir e evitar perda de dados.

## Organização do código

* [x] Separar código em pastas

* [x] Criar pasta de modelos

* [x] Criar pasta de serviços

* [x] Criar pasta de interface

* [x] Criar pasta de dados

* [x] Evitar deixar toda a lógica no arquivo principal

* [x] Separar responsabilidades em serviços (`routine_service`, `progress_service`, `reward_service`, `storage`)

* [x] Remover arquivos locais/desnecessários do GitHub

* [x] Configurar `.gitignore` para dados locais, cache e notas locais

* [x] Adicionar `.editorconfig` e `.gitattributes`

---

## Segurança dos dados

* [ ] Criar backup do arquivo de dados

* [ ] Salvar backup antes de sobrescrever dados

* [x] Tratar erro ao carregar arquivo corrompido

* [x] Criar arquivo novo caso o arquivo de dados não exista

* [x] Separar dados locais em JSONs por domínio

* [x] Manter pasta `data/` fora do versionamento

* [x] Migrar leitura de arquivo legado quando existir `data/tasks.json` antigo

* [ ] Evitar duplicidade de tarefas ao carregar dados

---

## Qualidade

* [ ] Padronizar nomes de variáveis e funções

* [ ] Criar comentários apenas onde for necessário

* [ ] Remover código morto

* [x] Criar testes de estatísticas semanais

* [x] Criar testes de bônus semanal

* [x] Criar testes de conquistas

* [ ] Testar fluxo de adicionar tarefa

* [ ] Testar fluxo de concluir tarefa

* [ ] Testar fluxo de editar tarefa

* [ ] Testar fluxo de excluir tarefa

* [ ] Testar salvamento e carregamento dos dados

---

# Futuro

Essas ideias só fazem sentido se o app crescer bastante.

## Conta e sincronização

* [ ] Criar sistema de login

* [ ] Criar banco de dados online

* [ ] Sincronizar dados entre dispositivos

* [ ] Criar backup em nuvem

---

## Ranking

* [ ] Criar ranking de usuários

* [ ] Mostrar usuários com mais pontos

* [ ] Mostrar usuários com maior streak

* [ ] Criar ranking semanal

* [ ] Criar ranking mensal

---

# Ordem recomendada de desenvolvimento

## Primeiro

* [x] Criar tarefas
* [x] Listar tarefas
* [x] Concluir tarefas
* [x] Editar tarefas
* [x] Excluir tarefas
* [x] Salvar dados localmente
* [x] Criar sistema de pontos
* [x] Mostrar resumo do dia

## Depois

* [x] Adicionar prioridade
* [x] Adicionar categoria
* [x] Criar barra de progresso
* [x] Criar histórico diário
* [x] Criar reset diário

## Em seguida

* [x] Criar sistema de níveis
* [x] Criar streak
* [x] Criar mensagens motivacionais
* [x] Criar metas diárias

## Mais tarde

* [x] Criar recompensas personalizadas
* [x] Criar loja de recompensas
* [x] Criar estatísticas semanais
* [x] Criar conquistas
* [x] Criar tarefas recorrentes

## Agora

* [ ] Fechar e publicar redesign visual atual
* [ ] Revisar responsividade geral
* [ ] Criar filtros por prioridade e categoria
* [ ] Ampliar testes dos fluxos principais
* [ ] Criar backup automático dos dados
* [x] Reorganizar estrutura de pastas

---

# Versões sugeridas

Versão atual registrada no projeto: `1.0.0`.

Próxima versão sugerida: `v1.1.0`, focada em polimento visual, filtros melhores, testes e segurança dos dados.

## v0.1.0 ? MVP básico

* Criar, listar, concluir, editar e excluir tarefas
* Pontos simples
* Salvamento local
* Resumo do dia

## v0.2.0 ? Organização

* Prioridades
* Categorias
* Barra de progresso
* Histórico diário simples

## v0.3.0 ? Rotina diária

* Reset diário
* Streak
* Meta diária
* Mensagens motivacionais

## v0.4.0 ? Gamificação

* Sistema de níveis
* XP
* Bônus por streak
* Conquistas iniciais

## v0.5.0 ? Recompensas

* Recompensas personalizadas
* Loja de recompensas
* Pontos disponíveis
* Histórico de resgates

## v1.0.0 ? Primeira versão completa

* App estável
* Dados seguros
* Histórico funcional
* Sistema de pontos funcional
* Progressão por níveis
* Streak
* Recompensas
* Interface organizada

## v1.1.0 ? Polimento e confiabilidade

* Redesign da navegação lateral
* Melhorias na tela de recompensas
* Filtros por prioridade e categoria
* Mais testes automatizados
* Backup automático dos dados locais
* Organização do código em pastas
