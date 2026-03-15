# Luna API

*1*. Для запуска приложения одной командой(также можно самостоятельно запустить docker compose up --build -d):

```bash
make up
```

После старта приложения:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostGIS/PostgreSQL: `localhost:5435`

*2*. Для заполнения бд тестовыми данными можно запустить скрипт:

```bash
make seed
```

*3*. Для запуска тестов(предварительно нужно поднять контейнеры п.1 и заполнить бд данными п.2):

```bash
make test
```

*4*. Для использования API необходим API ключ в заголовке X-API-Key:

- Header: `X-API-Key: luna-static-api-key`


