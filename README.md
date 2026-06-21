# Rotina Diaria

Webapp local para acompanhar tarefas do dia e recompensas por conclusao.

## Como executar

1. Instale o Python 3.10+.
2. Execute o servidor local:

   ```bash
   python web_app.py
   ```

3. Abra o endereco exibido no terminal, como `http://127.0.0.1:8000/`.

## Dados locais

O app cria `data/tasks.json` automaticamente para salvar tarefas, pontos, historico e recompensas. A pasta `data/` fica fora do Git.

## Funcionalidades

- adicionar, editar, excluir, fixar e reabrir tarefas
- marcar tarefas como concluidas
- somar pontos por prioridade
- acompanhar meta diaria, nivel, XP, streak e historico
- criar e resgatar recompensas usando pontos disponiveis
