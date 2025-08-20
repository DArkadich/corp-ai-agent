# Corp AI Agent

Минимальная система RAG-агента на FastAPI + LangGraph, с локальной LLM через Ollama → LiteLLM, эмбеддингами через TEI и векторным хранилищем pgvector.

## Состав
- Сервис агента (`app/`): FastAPI, `/ask`, `/ingest`, метрики `/metrics`, здоровье `/healthz`.
- Ингест-утилита (`ingest/`): батч-заливка текстов/пдф в pgvector.
- Kubernetes манифесты: `k8s/` (ns, secrets, ollama, litellm, tei, pgvector, agent, rbac).
- CI/CD: GitHub Actions для сборки образа и деплоя.

## Локальная сборка образа агента
```bash
docker build -t corp-agent:dev -f app/Dockerfile .
```

## Деплой в Kubernetes
1. Создайте секреты в `k8s/secrets/corp-secrets.yaml` (пароль БД и ключ для SDK).
2. Примените манифесты:
```bash
make deploy
```
3. Загрузите модель в Ollama:
```bash
make pull-model
```
4. Проброс порта и проверка:
```bash
make port-forward
curl -s localhost:8000/healthz
```

## Использование API
- Вопрос к агенту:
```bash
curl -s -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"Что написано в документе policy.pdf?"}'
```
- Ингест файлов:
```bash
curl -s -F files=@/path/to/file1.pdf -F files=@/path/to/file2.txt \
  localhost:8000/ingest
```

## Наблюдаемость
- Метрики: `GET /metrics` (Prometheus). Можно установить kube-prometheus-stack и Loki:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm install kps prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
helm install loki grafana/loki-stack -n monitoring --set grafana.enabled=false
```

## Замечания
- В проде используйте PersistentVolume для Ollama и Postgres, Secrets через ExternalSecrets/SealedSecrets.
- Убедитесь, что `PG_DSN`, `TEI_URL`, `OPENAI_API_BASE` корректно заданы для кластера.
