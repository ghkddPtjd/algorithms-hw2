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
| `src/` · `tests/` | 단축기, 체이닝/선형 탐지 테이블, 경계 테스트 |
| `experiments/` | 적재율 비교 표·그래프와 선형 탐지 보고서 |
| `tools/catchup.sh` | 수업 중 놓친 단계를 따라잡는 스크립트 |
| `Makefile` | `make test` · `make serve` · `make experiment` · `make compare` |

현재 저장소에는 base62, 두 해시 테이블, 단축기와 테스트가 들어 있습니다.
이슈와 `SPEC.md`를 기준으로 실험 결과를 재현하고 동작을 확인할 수 있습니다.

## 명령

컨테이너 안(Codespaces 터미널)에서 실행합니다.

| 하고 싶은 것 | 명령 |
| --- | --- |
| 테스트 | `make test` |
| 웹 서버 (포트 8000) | `make serve` |
| 체이닝/선형 탐지 실험 | `make experiment` |
| 두 방식 비교만 | `make compare` |
| 놓친 단계 따라잡기 | `sh tools/catchup.sh <단계 번호>` |

외부 라이브러리는 쓰지 않습니다. Python 표준 모듈만으로 충분합니다.
실험은 CSV/Markdown 표와 SVG 그래프를 저장하고,
선형 탐지 비교 보고서는 `experiments/linear_probing_report.pdf`로 생성합니다.

## 해시 테이블 선택

메인 화면의 `Table`에서 체이닝과 선형 탐지를 선택할 수 있습니다.
두 방식은 서로 독립된 해시 테이블과 단축 코드 저장소를 사용하며,
선형 탐지 링크에는 `?table=linear`이 포함되어 기존 `/s/<코드>` 경로에서도
올바른 선형 탐지 저장소로 확장됩니다.

## 외부 공유 링크

`make serve`는 설정하지 않으면 요청의 `Host`를 링크의 기준 주소로 사용합니다.
Codespaces에서는 포트 8000의 공개 포워딩 주소를 자동으로 링크의 기준으로 사용합니다.
일반 로컬 환경에서는 `http://localhost:8000/0/` 같은 링크가 생성됩니다.
다른 호스트나 배포 주소를 사용하려면 다음처럼 기준 주소를 지정할 수 있습니다.

결과 화면에는 현재 서버 기준의 짧은 상대 링크도 함께 표시합니다.
예를 들어 Codespaces에서는 화면의 `Short link`를 `/0/`처럼 짧게 사용할 수 있고,
다른 사람과 공유할 때는 `Shareable absolute link`를 사용합니다.

```sh
PUBLIC_BASE_URL=http://localhost:8000 make serve
```

HTTPS 배포라면 `PUBLIC_BASE_URL`에 `https://` 주소를 지정하세요. 이 설정은
링크에 넣을 주소만 정하므로, `s` 같은 호스트 이름의 DNS나 프록시 연결은 배포
환경에서 제공되어야 합니다. `make serve` 대신 Python 파일을 직접 실행하면
`--public-base-url` 옵션이나 `PUBLIC_BASE_URL` 환경 변수를 지정할 수 있습니다.

## 로컬에서 하기

```sh
git clone https://github.com/<본인 계정>/<내 저장소>.git
cd <내 저장소>
docker compose up -d
docker compose exec lab bash
```

**이후 모든 `docker compose` 명령은 이 폴더에서 칩니다.**
