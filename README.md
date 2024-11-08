# Market App

Este projeto configura uma aplicação Rails com Docker e instala as bibliotecas Python `pandas`, `geopandas`, e `folium` para uso em análises de dados e mapeamento.

## Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Estrutura do Projeto

- **Dockerfile**: Configuração de imagem para a aplicação Rails e bibliotecas Python.
- **docker-compose.yml**: Configuração do serviço para a aplicação e seu ambiente.

## Configuração e Execução

### Passo 1: Construir a Imagem e Subir o Contêiner

Execute o seguinte comando para construir a imagem:

```console
docker-compose build
```

### Passo 2: Executando a aplicação

Em seguida execute o seguinte comando para iniciar o contêiner:

```bash
docker-compose up
```

### Passo 3: Acessando a aplicação

Para acessar basta entrar na porta 3000 no navegador:

```bash
http://localhost:3000
```

### Passo 4: Parando a Aplicação

Para parar os contêineres, execute:

```bash
docker-compose down
```

Ou simplesmente use os comandos "ctrl + c" no console.