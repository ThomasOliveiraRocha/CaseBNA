# Case Técnico - bna.dev

## Descrição do Projeto

Este repositório é parte do desafio técnico da bna.dev para a vaga de Desenvolvedor de Software.  
O objetivo é construir uma solução que ajude a equipe de vendas a **coletar e processar informações relevantes da web**, antes de reuniões com clientes.

A solução completa envolve:

- Uma **API** que recebe links de sites e retorna informações relevantes.
- Um sistema de **web scraping** com cache local para evitar requisições repetidas.
- Uma **interface web** para facilitar o uso pelo time de vendas.
- Bônus: autenticação, painel admin, deploy e testes automatizados.

---

## Planejamento da Semana

### Dia 1 - Terça-feira (29/07)

- [x] Criar repositório e configurar ambiente local
- [x] Iniciar backend com FastAPI
- [x] Criar endpoint `/scrape` que recebe uma URL e retorna o `<title>`
- [x] Adicionar dependências no `requirements.txt`
- [x] Criar `.gitignore`
- [x] Documentar projeto no `README.md`

---

### Dia 2 - Quarta-feira (30/07)

- [x] Melhorar scraping com mais dados úteis (ex: headings, e-mails, telefone, etc)
- [x] Criar banco de dados local (SQLite ou MongoDB)
- [x] Implementar cache de scraping para URLs já processadas
- [x] Modularizar código

---

### Dia 3 - Quinta-feira (31/07)

- [x] Criar rota `/analyze` que usa IA com o conteúdo da página
- [x] Iniciar frontend com React (Vite)
- [x] Criar tela básica com envio de URL e exibição dos resultados

---

### Dia 4 - Sexta-feira (01/08)

- [x] Finalizar frontend com visualização de histórico e dados
- [ ] Criar autenticação simples com JWT
- [ ] Criar painel admin (bônus)
- [ ] Dockerizar o projeto
- [ ] Adicionar testes com `pytest`
- [ ] Criar script de execução (`start.sh` ou `make run`)
- [ ] Deploy (Render para backend, Vercel/Netlify para frontend)

---


