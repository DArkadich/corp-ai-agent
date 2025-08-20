NS=corp-ai

.PHONY: deploy pull-model port-forward

deploy:
	kubectl apply -f k8s/ns.yaml
	kubectl -n $(NS) apply -f k8s/secrets/corp-secrets.yaml
	kubectl -n $(NS) apply -f k8s/ollama
	kubectl -n $(NS) apply -f k8s/litellm
	kubectl -n $(NS) apply -f k8s/tei
	kubectl -n $(NS) apply -f k8s/pgvector
	kubectl -n $(NS) apply -f k8s/agent
	kubectl -n $(NS) apply -f k8s/rbac.yaml

pull-model:
	kubectl -n $(NS) exec deploy/ollama -- sh -lc \
	  'curl -s http://localhost:11434/api/pull -d "{\"name\":\"llama3.1:8b\"}" '

port-forward:
	kubectl -n $(NS) port-forward svc/agent-api 8000:8000
