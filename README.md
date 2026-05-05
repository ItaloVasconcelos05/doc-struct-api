# 📄 DocStruct API

O **DocStruct** é um sistema inteligente que automatiza a leitura de documentos complexos, como contratos e notas fiscais. Utilizando Inteligência Artificial (LLMs), ele extrai dados cruciais do texto livre — como nomes, valores monetários, datas e documentos (CPF/CNPJ) — transformando papelada desorganizada em informações estruturadas e prontas para uso em sistemas financeiros ou relatórios.

## ⚙️ Como funciona? (Arquitetura)

O fluxo de dados da aplicação é dividido em três etapas assíncronas:
1. **Ingestão (`/ingest`):** O sistema varre o diretório de arquivos físicos, lê o conteúdo (suporta PDFs via `pypdf` e TXT) e cadastra o documento no banco de dados com o status `PENDING`.
2. **Processamento (`/process`):** Um motor de extração (NER) consulta os documentos pendentes, envia o texto para uma IA via OpenRouter com um prompt rigoroso de formatação JSON, e salva as entidades extraídas, alterando o status para `COMPLETED`.
3. **Disponibilização (`GET`):** As rotas de leitura devolvem os dados estruturados e a probabilidade de acerto (confidence) de cada extração.

**Stack Tecnológico:**
* Python 3.11
* FastAPI (Web Framework)
* PostgreSQL (Banco de Dados)
* SQLAlchemy (ORM)
* Docker & Docker Compose (Infraestrutura)
* OpenRouter API (Integração LLM)

---

## 🛠️ Pré-requisitos

Graças à conteinerização, você não precisa instalar o Python ou o PostgreSQL na sua máquina. Você precisará apenas de:

* **Docker Desktop** instalado e rodando.
* Uma chave de API gratuita no [OpenRouter](https://openrouter.ai/).

## 🚀 Como rodar o projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/ItaloVasconcelos05/doc-struct-api.git
   cd doc-struct-api

2. **Configure as Variáveis de Ambiente:**

Crie um arquivo .env na raiz do projeto com as seguintes chaves:

```
DATABASE_URL=postgresql+psycopg2://admin:secret123@postgres:5432/docstruct_db
OPENROUTER_API_KEY=sua_chave_aqui
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/owl-alpha
```

3. **Inicie a Infraestrutura:**

Abra o seu terminal na pasta do projeto e execute:
```
docker compose up --build
```
Aguarde até que o terminal exiba que o Uvicorn está rodando na porta 8000.

## 💻 Como usar (Testando a API)
A API possui uma interface gráfica interativa (Swagger UI) gerada automaticamente.
Acesse no seu navegador: 👉 http://localhost:8000/docs

### O Fluxo de Teste:
1. **Adicione um documento:**
Crie uma pasta chamada documents na raiz do projeto e coloque um arquivo .pdf ou .txt dentro dela. (Essa pasta é espelhada diretamente para dentro do container).

2. **Faça a Ingestão:**
No Swagger, abra a rota POST /documents/ingest, clique em Try it out e envie o payload apontando para a pasta do container:
```
{
  "directory": "/app/documents"
}
```

3. **Inicie a Inteligência Artificial:**
Abra a rota POST /documents/process e execute. O sistema irá ler o seu documento e conectar com o OpenRouter para extrair as entidades.

4. **Veja os Resultados:**
Use a rota GET /documents/ para ver seus documentos salvos e a rota GET /documents/{id}/entities (usando o ID gerado) para ver a mágica da extração estruturada funcionando!
