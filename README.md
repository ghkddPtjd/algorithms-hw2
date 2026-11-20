# 과제2 · 에이전트와 함께 만드는 URL 단축기

2026-2 **고급알고리즘**(SIT2001-01) 과제2의 **시작 저장소**입니다.
채팅창에 묻고 복사·붙여넣기 하던 방식에서 벗어나, Codespace 안의 에이전트가
저장소를 읽고, 파일을 고치고, 테스트를 직접 돌리게 하는 방법을 익힙니다.

- 과제 안내: [lec-algorithm.github.io/lecture/article/hw2-2026](https://lec-algorithm.github.io/lecture/article/hw2-2026/)
- 수업 슬라이드: [lec-algorithm.github.io/lecture/slides/hw2-2026](https://lec-algorithm.github.io/lecture/slides/hw2-2026/)
- 해시 테이블 복습: [주제 08 해시 테이블](https://lec-algorithm.github.io/lecture/course/topic-08-hashing/)

## 시작하기

1. 이 저장소 상단의 **Use this template** → **Create a new repository**
2. 저장소 이름은 `algorithms-hw2`처럼 정합니다. 공개(Public)로 만듭니다.
3. 만들어진 **내 저장소**에서 **Code** → **Codespaces** 탭 → **Create codespace on main**
4. 왼쪽 막대의 Copilot 아이콘을 눌러 채팅 창을 열고, 창 아래쪽에서 **Agent** 모드를 고릅니다.

## 들어 있는 것

| 파일 | 하는 일 |
| --- | --- |
| `SPEC.md` | 명세 틀. 에이전트가 초안을 쓰고 **본인이 고칩니다** |
| `src/` · `tests/` · `experiments/` | 비어 있습니다. 수업에서 채웁니다 |
| `tools/catchup.sh` | 수업 중 놓친 단계를 따라잡는 스크립트 |
| `Makefile` | `make test` · `make serve` · `make experiment` |

정답 코드는 들어 있지 않습니다. 에이전트는 작업 공간의 파일을 읽으므로, 정답이
옆에 있으면 그대로 베껴 와서 연습이 되지 않습니다.

## 명령

컨테이너 안(Codespaces 터미널)에서 실행합니다.

| 하고 싶은 것 | 명령 |
| --- | --- |
| 테스트 | `make test` |
| 웹 서버 (포트 8000) | `make serve` |
| 충돌 실험 | `make experiment` |
| 놓친 단계 따라잡기 | `sh tools/catchup.sh <단계 번호>` |

외부 라이브러리는 쓰지 않습니다. Python 표준 모듈만으로 충분합니다.

`make serve`는 모든 인터페이스에서 포트 8000을 엽니다. Codespaces에서는 포트 8000이
전달되면 브라우저가 자동으로 열립니다. 다른 사람도 접속해야 한다면 **Ports** 탭에서 포트의
**Port Visibility → Public**을 선택합니다. 공개 포트는 URL을 아는 누구나 접속할
수 있습니다. 일반 Docker VM에서는 VM의 공개 주소와 방화벽에서 8000번 포트를
허용해야 합니다.

웹 페이지에서 URL을 입력하거나 아래 API를 호출해 단축 URL을 만들 수 있습니다.
만들어진 단축 경로를 열면 원래 URL로 이동합니다.
Codespaces에서는 Ports 탭에서 복사한 주소를 `BASE_URL`에 넣어 호출하세요.

```sh
curl -X POST "$BASE_URL/shorten" \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

URL과 코드는 현재 서버 프로세스 메모리에 저장되므로 서버를 재시작하면 초기화됩니다.

## 로컬에서 하기

```sh
git clone https://github.com/<본인 계정>/<내 저장소>.git
cd <내 저장소>
docker compose up -d
docker compose exec lab bash
```

**이후 모든 `docker compose` 명령은 이 폴더에서 칩니다.**
컨테이너 안에서 `make serve`를 실행하면 호스트의 8000번 포트로 연결됩니다.
