# docker操作
dbuild:
	docker build -t md_manage_server:0.1 -f docker/Dockerfile .

up:
	docker compose -f ./docker/docker-compose.yml up -d

down:
	docker compose -f ./docker/docker-compose.yml down

exec:
	docker exec -it md_manage_server bash