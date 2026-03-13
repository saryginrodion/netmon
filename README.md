# netmon
Netmon - программа для сбора метрик по сети, включающая в себя несколько коллекторов

# Запуск
В netmon есть набор модулей, которые можно запустить

Перед этим нужно установить пакетный менеджер для python - `uv`

## ActiveTCPServer
Запуск сервера активного TCP теста
```sh
uv run -m netmon.cmd.active_tcp_server

# Вывод help описания
uv run -m netmon.cmd.active_tcp_server --help
```

## ActiveTCPCollector
Запуск единственного коллектора для активного TCP теста
```sh
uv run -m netmon.cmd.active_tcp_collector

# Вывод help описания
uv run -m netmon.cmd.active_tcp_collector --help
```
