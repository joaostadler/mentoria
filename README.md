# Cursus — Plataforma de Cursos Online

Sistema web para gerenciamento de cursos educacionais com suporte a tópicos, aulas e upload de materiais.

## Funcionalidades

- **Autenticação**: Cadastro e login com senhas seguras (bcrypt). O primeiro usuário se torna administrador automaticamente.
- **Cursos**: Criação, edição e exclusão com imagem de capa
- **Tópicos**: Organização das aulas em módulos sequenciais
- **Aulas**: Conteúdo textual e upload de múltiplos materiais
- **Materiais**: Upload de PDF, vídeo (MP4, AVI, MOV), imagens e outros arquivos (até 500MB)
- **Roles**: Admin (cria e gerencia tudo) e Aluno (visualiza cursos publicados)

## Estrutura do Projeto

```
cursus/
├── run.py                     # Ponto de entrada
├── requirements.txt
└── app/
    ├── __init__.py            # Factory da aplicação Flask
    ├── models.py              # Modelos do banco (User, Course, Topic, Lesson, Material)
    ├── routes/
    │   ├── auth.py            # Login, cadastro, logout
    │   ├── main.py            # Dashboard
    │   ├── courses.py         # CRUD de cursos
    │   ├── topics.py          # CRUD de tópicos
    │   └── lessons.py         # CRUD de aulas + upload de arquivos
    ├── templates/
    │   ├── base.html          # Template base (navbar, alertas)
    │   ├── auth/              # login.html, register.html
    │   ├── main/              # index.html, dashboard.html
    │   ├── courses/           # list.html, view.html, form.html
    │   ├── topics/            # form.html
    │   └── lessons/           # view.html, form.html
    └── static/
        └── uploads/           # Arquivos enviados pelos usuários
```

## Como Rodar

### 1. Clone ou baixe o projeto

```bash
cd cursus
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Inicie o servidor

```bash
python run.py
```

Acesse: **http://localhost:5000**

## Primeiros Passos

1. Acesse `/auth/register` e cadastre a primeira conta — ela será **administrador**
2. Crie um curso em **"+ Novo Curso"**
3. Dentro do curso, adicione tópicos com **"+ Novo Tópico"**
4. Dentro de cada tópico, adicione aulas com **"+ Aula"**
5. Em cada aula, faça upload de PDFs, vídeos ou imagens
6. Publique o curso para que os alunos vejam

## Banco de Dados

O banco SQLite é criado automaticamente em `app/cursus.db` na primeira execução. Nenhuma configuração extra necessária.

## Variáveis de Ambiente (Opcional)

```bash
SECRET_KEY=sua-chave-secreta-aqui
```

Em produção, defina uma `SECRET_KEY` forte no ambiente.
