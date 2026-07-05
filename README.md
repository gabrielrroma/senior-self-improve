# Rotina Diaria

Webapp local para acompanhar tarefas do dia e recompensas por conclusao.

## Como executar

1. Instale o Python 3.10+.
2. Execute o servidor local:

   ```bash
   python web_app.py
   ```

3. Abra o endereco exibido no terminal, como `http://127.0.0.1:8000/`.

A interface principal em `/` e renderizada em React a partir dos arquivos estaticos de `web/`. Nao ha passo separado de `npm install` ou build neste momento; o servidor Python continua sendo a entrada unica do app.

## Estrutura

- `web_app.py`: servidor local, rotas HTTP e API do app
- `web/`: interface React estatica servida pelo Python
- `services/`: regras de rotina, progresso, recompensas e persistencia
- `models/`: constantes e configuracoes de dominio
- `tests/`: testes automatizados
- `data/`: dados locais gerados pelo app, fora do Git

## Testes

Execute os testes com:

```bash
python -m unittest discover -s tests
```

## Dados locais

O app cria arquivos JSON separados dentro de `data/` para salvar os dados locais:

- `profile.json`: perfil local e carteira de pontos
- `tasks.json`: dia atual e tarefas
- `rewards.json`: recompensas e resgates
- `history.json`: historico e dias arquivados
- `settings.json`: configuracoes e gamificacao

A pasta `data/` fica fora do Git. Se existir um `data/tasks.json` antigo com tudo junto, o app ainda consegue ler e migrar os dados para os arquivos separados no proximo salvamento.

## Funcionalidades

- adicionar, editar, excluir, fixar e reabrir tarefas
- marcar tarefas como concluidas
- somar pontos por prioridade
- acompanhar meta diaria, nivel, XP, streak e historico
- acompanhar estatisticas semanais, meta semanal e conquistas
- criar e resgatar recompensas com imagem opcional usando pontos disponiveis
