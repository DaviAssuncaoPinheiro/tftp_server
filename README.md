# TFTP Server

Servidor TFTP implementado em Python.

## Como usar

```bash
python server.py --host 0.0.0.0 --port 69 --directory ./files
```

### Argumentos

| Argumento     | Padrão    | Descrição                          |
|---------------|-----------|------------------------------------|
| `--host`      | `0.0.0.0` | Endereço para bind do servidor    |
| `--port`      | `69`      | Porta UDP para escutar            |
| `--directory` | `.`       | Diretório raiz para transferências |

## Estrutura

```
tftp-server/
├── server.py
├── README.md
├── docs/
│   ├── diagrams/
│   └── prints/
└── src/
    ├── __init__.py
    └── cli.py
```