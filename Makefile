up:        ## Levanta todo
	docker compose up -d --build
down:      ## Apaga todo
	docker compose down
logs:      ## Logs de API
	docker compose logs -f api
ps:        ## Estado
	docker compose ps
shell:     ## Bash dentro de api
	docker compose exec api bash
test:      ## Pruebas rápidas (sin jq)
	curl -sS http://localhost:8000/health | python3 -m json.tool
	curl -sS "http://localhost:8000/discover?limit=5" | python3 -m json.tool
	curl -sS "http://localhost:8000/wrappers/weather?lat=-31.42&lon=-64.19" | python3 -m json.tool
