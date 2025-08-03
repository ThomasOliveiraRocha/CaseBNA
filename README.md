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

##  Planejamento da Semana

| Dia        | Atividades                                                                            |
|------------|---------------------------------------------------------------------------------------|
| **29/07**  | Configuração do repositório, FastAPI inicial, endpoint `/scrape`, título da página    |
| **30/07**  | Extração de dados úteis (e-mail, telefone, headings), banco SQLite, cache de scraping |
| **31/07**  | Rota `/analyze` com IA, frontend com React (Vite), JWT e painel admin                 |
| **01/08**  | Finalização, testes, ajustes de layout, documentação e apresentação                   |

---

##  Tecnologias Utilizadas

### Backend
- **Framework**: FastAPI
- **Scraping**: BeautifulSoup + Requests
- **Banco de Dados**: SQLite (via SQLAlchemy)
- **Autenticação**: JWT (JSON Web Tokens)

### Frontend
- **Framework**: React + Vite
- **Estilização**: CSS 
- **Autenticação**: LocalStorage + JWT
---
## Instalação e Execução

### Pré-requisitos
- Node.js + npm
- Python 3.10+
- SQLite3

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
### Frontend
```bash
cd frontend
npm install
npm run dev
```
