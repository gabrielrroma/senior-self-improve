# ROADMAP.md ? App de Rotina Diária com Recompensas

Este roadmap organiza a evolução do app de rotina diária com recompensas.

A ideia principal do projeto é criar um app desktop simples onde o usuário possa organizar suas tarefas, acompanhar seu progresso, ganhar pontos e se motivar a manter uma rotina mais consistente.

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

> Um app desktop onde o usuário adiciona tarefas do dia, define prioridade, marca como concluída, ganha pontos, vê o progresso diário e mantém tudo salvo localmente com um histórico simples.

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

* [ ] Criar registro diário de progresso

* [ ] Salvar resumo do dia:

  * Data
  * Tarefas concluídas
  * Total de tarefas
  * Pontos ganhos
  * Porcentagem concluída

* [ ] Criar tela ou seção para visualizar histórico

---

## Reset diário

* [ ] Detectar quando o dia mudou

* [ ] Salvar resumo do dia anterior

* [ ] Preparar lista de tarefas do novo dia

* [ ] Manter pontos totais acumulados

* [ ] Garantir que os dados antigos não sejam perdidos

---

# Fase 3 ? Gamificação Inicial

Objetivo: transformar o app em uma experiência mais motivadora.

## Sistema de níveis

* [ ] Criar XP baseado nos pontos ganhos

* [ ] Criar nível do usuário

* [ ] Definir regra de evolução de nível

* [ ] Mostrar nível atual na tela principal

* [ ] Mostrar XP atual

* [ ] Mostrar XP necessário para o próximo nível

---

## Streak

* [ ] Criar contagem de dias seguidos usando o app

* [ ] Definir regra para manter streak

* [ ] Definir regra para perder streak

* [ ] Mostrar streak atual na tela principal

* [ ] Dar bônus por manter streak

---

## Mensagens motivacionais

* [ ] Criar mensagens para início do dia

* [ ] Criar mensagens para metade do progresso

* [ ] Criar mensagens para dia completo

* [ ] Criar mensagens quando o usuário perde streak

* [ ] Mostrar mensagem motivacional no resumo do dia

---

## Metas diárias

* [ ] Criar meta diária de pontos

* [ ] Mostrar progresso da meta diária

* [ ] Dar feedback quando a meta diária for concluída

---

# Fase 4 ? Recompensas

Objetivo: permitir que o usuário use os pontos como recompensa real.

## Recompensas personalizáveis

* [ ] Permitir criar recompensa personalizada

* [ ] Definir custo em pontos para cada recompensa

* [ ] Listar recompensas disponíveis

* [ ] Editar recompensa

* [ ] Excluir recompensa

---

## Loja de recompensas

* [ ] Criar tela de loja de recompensas

* [ ] Permitir resgatar recompensa usando pontos

* [ ] Impedir resgate caso o usuário não tenha pontos suficientes

* [ ] Separar pontos totais de pontos disponíveis

* [ ] Registrar histórico de recompensas resgatadas

---

## Histórico de recompensas

* [ ] Salvar data de resgate

* [ ] Salvar nome da recompensa resgatada

* [ ] Salvar custo em pontos da recompensa

* [ ] Exibir histórico de recompensas resgatadas

---

# Fase 5 ? Estatísticas e Conquistas

Objetivo: fazer o usuário enxergar melhor sua evolução.

## Estatísticas semanais

* [ ] Mostrar total de tarefas concluídas na semana

* [ ] Mostrar total de pontos ganhos na semana

* [ ] Mostrar melhor dia da semana

* [ ] Mostrar categoria mais concluída

* [ ] Mostrar taxa de conclusão semanal

---

## Metas semanais

* [ ] Criar meta semanal de tarefas

* [ ] Mostrar progresso da meta semanal

* [ ] Dar bônus ao cumprir meta semanal

---

## Conquistas

* [ ] Criar sistema de conquistas

* [ ] Criar conquista de primeira tarefa concluída

* [ ] Criar conquista de 7 dias seguidos

* [ ] Criar conquista de 100 tarefas concluídas

* [ ] Criar conquista de primeira semana perfeita

* [ ] Criar conquista de 500 pontos acumulados

* [ ] Mostrar conquistas desbloqueadas

---

# Fase 6 ? Recursos Extras

Objetivo: adicionar recursos mais avançados depois que a base estiver estável.

## Tarefas recorrentes

* [ ] Criar tarefa recorrente diária

* [ ] Recriar tarefa diária automaticamente

* [ ] Criar tarefa recorrente semanal

* [ ] Criar tarefa recorrente mensal

* [ ] Permitir editar recorrência

* [ ] Permitir desativar recorrência

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

* [x] Destacar tarefas concluídas

* [x] Destacar tarefas de alta prioridade

* [x] Criar tema claro

* [x] Criar tema escuro

* [x] Permitir alternar entre tema claro e escuro

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

* [ ] Separar código em pastas

* [ ] Criar pasta de modelos

* [ ] Criar pasta de serviços

* [ ] Criar pasta de interface

* [ ] Criar pasta de dados

* [ ] Evitar deixar toda a lógica no arquivo principal

---

## Segurança dos dados

* [ ] Criar backup do arquivo de dados

* [ ] Salvar backup antes de sobrescrever dados

* [x] Tratar erro ao carregar arquivo corrompido

* [x] Criar arquivo novo caso o arquivo de dados não exista

* [ ] Evitar duplicidade de tarefas ao carregar dados

---

## Qualidade

* [ ] Padronizar nomes de variáveis e funções

* [ ] Criar comentários apenas onde for necessário

* [ ] Remover código morto

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
* [ ] Criar histórico diário
* [ ] Criar reset diário

## Em seguida

* [ ] Criar sistema de níveis
* [ ] Criar streak
* [ ] Criar mensagens motivacionais
* [ ] Criar metas diárias

## Mais tarde

* [ ] Criar recompensas personalizadas
* [ ] Criar loja de recompensas
* [ ] Criar estatísticas semanais
* [ ] Criar conquistas
* [ ] Criar tarefas recorrentes

---

# Versões sugeridas

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
