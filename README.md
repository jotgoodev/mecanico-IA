# Meu amigo Mecânico 🚗💡

Bem-vindo ao repositório do **Meu amigo Mecânico**! Este projeto é um assistente de IA desenvolvido para ajudar utilizadores com dúvidas sobre manutenção automóvel, diagnósticos preliminares de sintomas e compreensão de orçamentos de mecânicos.

Este projeto foi desenvolvido como parte da **Imersão IA da Alura + Google**.

## 🎯 Objetivo

O objetivo principal do "Meu amigo Mecânico" é fornecer informações úteis e acessíveis sobre o mundo da mecânica automóvel, capacitando os utilizadores a tomarem decisões mais informadas sobre os seus veículos e a terem conversas mais produtivas com os seus mecânicos.

## ✨ Funcionalidades Implementadas

A aplicação web atualmente oferece três caminhos principais:

1.  **Revisões Padrões:**
    * Apresenta uma lista de itens de revisão comuns (ex: Troca de Óleo, Filtros, Velas).
    * Ao selecionar um item, exibe informações detalhadas sobre:
        * O que é e qual a sua função.
        * A importância da sua manutenção/troca.
        * Intervalos recomendados (tempo e quilometragem).
        * Como um leigo pode verificar algo (se aplicável e seguro).
        * Sinais de problema ou desgaste.
        * Estimativa de custo do serviço no Brasil para carros populares (esta informação é fixa e serve como referência geral).

2.  **Diagnóstico por Sintomas:**
    * O utilizador descreve os sintomas que o seu veículo está a apresentar numa caixa de texto.
    * A IA do Google Gemini analisa a descrição e fornece:
        * Possíveis causas prováveis para o sintoma.
        * Breve explicação de cada causa.
        * Sugestões de verificações simples e seguras (se aplicável).
        * Indicação de quando procurar um mecânico.
        * Um aviso importante de que se trata de um diagnóstico preliminar.

3.  **Entendendo seu Orçamento/Diagnóstico:**
    * O utilizador insere o orçamento ou o diagnóstico que recebeu de um mecânico.
    * A IA do Google Gemini analisa a informação e ajuda a:
        * Explicar cada item ou serviço mencionado.
        * Analisar a necessidade e criticidade geral dos serviços (com base em boas práticas).
        * Identificar serviços que são comumente feitos juntos.
        * Sugerir perguntas úteis para fazer ao mecânico.
        * Inclui um aviso de que a análise é informativa e não substitui a avaliação do profissional que inspecionou o veículo.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python com Flask
* **Inteligência Artificial:** Google Gemini API (através da biblioteca `google-generativeai`)
* **Frontend:** HTML, CSS
* **Gestão de API Key:** `python-dotenv` para carregar variáveis de ambiente localmente.
* **Controlhe de Versão:** Git e GitHub

## 🚀 Como Executar o Projeto Localmente

Para executar o "Meu amigo Mecânico" no seu computador, siga os passos abaixo:

1.  **Pré-requisitos:**
    * Python 3.8 ou superior instalado.
    * Git instalado.

2.  **Clone o Repositório:**
    Abra o seu terminal ou prompt de comando e execute:
    ```bash
    git clone [https://github.com/jotgoodev/mecanico-IA.git](https://github.com/jotgoodev/mecanico-IA.git)
    cd mecanico-IA
    ```

3.  **Crie e Ative um Ambiente Virtual** (Recomendado):
    ```bash
    # No Windows
    python -m venv venv
    venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure a API Key do Google Gemini:**
    * Crie um ficheiro chamado `.env` na raiz do projeto (na mesma pasta que o `app.py`).
    * Dentro do ficheiro `.env`, adicione a seguinte linha, substituindo `SUA_CHAVE_API_REAL_AQUI` pela sua chave de API válida do Google Gemini:
        ```
        GOOGLE_API_KEY=SUA_CHAVE_API_REAL_AQUI
        ```
    * **Importante:** O ficheiro `.env` está listado no `.gitignore` e não deve ser enviado para o repositório. Cada utilizador precisa de usar a sua própria chave.

6.  **Execute a Aplicação Flask:**
    ```bash
    python app.py
    ```

7.  **No Navegador:**
    Abra o seu navegador de internet e vá para o seguinte endereço:
    [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

## 💡 Aprendizados e Desafios
  Primeira vez utilizando Python e VSCode, experiência incrível!

## 🤝 Contribuições

Este é um projeto desenvolvido para fins de estudo e como projeto final da Imersão IA. Contribuições e sugestões são bem-vindas, mas o foco principal foi o aprendizado durante o evento.

## 🙏 Agradecimentos

* À **Alura** e ao **Google** pela oportunidade da Imersão IA e por todo o conhecimento partilhado.

**Desenvolvido por:** jotgoodev
**Data:** Maio de 2025 
