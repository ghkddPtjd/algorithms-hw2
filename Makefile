# 과제2를 한 단어로 돌리기 위한 Makefile.
# 컨테이너 안에서 실행한다 (Codespaces 터미널, 또는 docker compose exec lab bash).
#
#   make test        유닛 테스트 (tests/test_*.py)
#   make serve       단축 URL 웹 서버 (포트 8000)
#   make experiment  체이닝·선형 탐지 실험 및 비교
#   make compare     두 충돌 처리 방식만 비교
#   make clean       캐시 정리
#
# 외부 라이브러리를 쓰지 않는다. Python 표준 모듈만으로 돈다.

PORT ?= 8000
PUBLIC_BASE_URL ?=

.PHONY: all test serve experiment compare clean

all: test

test:
	@python3 -m unittest discover -s tests -v

serve:
	@if [ -n "$(PUBLIC_BASE_URL)" ]; then \
		PUBLIC_BASE_URL="$(PUBLIC_BASE_URL)" python3 src/server.py --port $(PORT); \
	else \
		python3 src/server.py --port $(PORT); \
	fi

experiment:
	@python3 experiments/probe_experiment.py
	@python3 experiments/compare_experiment.py

compare:
	@python3 experiments/compare_experiment.py

clean:
	rm -rf src/__pycache__ tests/__pycache__ experiments/__pycache__
