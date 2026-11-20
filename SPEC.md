# URL 단축기 명세

## 1. 무엇을 만드는가

Python 표준 라이브러리만 사용하는 URL 단축기다. 사용자가 절대 `http` 또는
`https` URL을 제출하면 짧은 코드를 만들고, 해당 코드로 원래 URL을 조회한다.
해시 테이블과 충돌 처리 과정을 실험하고 웹 화면에서 살펴볼 수 있어야 한다.

## 2. base62 인코딩

- `src/base62.py`의 `encode(number: int) -> str`와 `decode(code: str) -> int`를 제공한다.
- 숫자 알파벳 순서는 `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`다.
- 0은 `"0"`으로 인코딩한다. 음수는 `ValueError`, 정수가 아니거나 `bool`이면
  `TypeError`를 발생시킨다.
- 빈 문자열 또는 알파벳 밖 문자가 든 코드는 `ValueError`를 발생시킨다.
- 인코딩과 디코딩은 임의 정밀도 정수를 지원한다.

## 3. 해시 테이블

- 키는 문자열이고 값은 임의의 Python 객체다. 인터페이스는
  `put(key, value)`, `get(key, default=None)`, `contains(key)`,
  `delete(key)`, `len(table)`, `items()`다.
- `put`은 같은 키가 이미 있으면 값을 바꾸고 항목 수를 늘리지 않는다.
  `get`은 키가 없으면 `default`를 반환한다. `delete`는 삭제 성공 여부를 반환한다.
- 기본 `HashTable`은 연결 리스트 체이닝을 사용한다. 기본 용량은 8이고
  적재율이 0.75를 초과하면 용량을 두 배로 늘려 재해싱한다.
- 실험에서는 재해싱 없이 지정한 적재율을 만들 수 있도록
  `max_load_factor=None`을 허용한다. 용량은 양의 정수여야 한다.
- 문자열의 Horner 해시는 각 문자에 대해 `h = (31 * h + ord(c)) % capacity`로
  계산한다. 충돌한 키는 연결 리스트에서 비교한다.
- `LinearProbingHashTable`은 같은 메서드 인터페이스를 사용하고 충돌 시 다음
  슬롯을 순환 탐색한다. 삭제는 tombstone으로 표시하고 기본 적재율 0.75 초과 시
  두 배로 재해싱한다. 재해싱이 꺼진 만석 테이블에 새 키를 넣으면 `OverflowError`다.
- `src/`에서 내장 `dict`, `set`, `hash()`를 사용하지 않는다. 체이닝은 직접 만든
  노드와 버킷 배열로, 선형 탐지는 슬롯 배열과 직접 만든 엔트리로 구현한다.
- 탐색 통계는 비교한 키 수를 세며, 성공 탐색은 일치한 노드를 포함하고
  실패 탐색은 체이닝 버킷의 모든 노드 또는 선형 탐지에서 확인한 빈 칸까지의
  슬롯 수를 포함한다.

## 4. 단축기

- `src/shortener.py`의 `URLShortener`는 `shorten(url) -> code`와
  `expand(code) -> url`을 제공한다.
- URL은 앞뒤 공백이 없어야 하며 `http` 또는 `https` 스킴, 호스트 이름을 가진
  절대 URL이어야 한다. 잘못된 URL은 `ValueError`다. DNS 연결은 검사하지 않는다.
- 같은 URL을 반복해 넣으면 같은 코드를 돌려준다. 서로 다른 URL은 서로 다른 코드다.
- 처음 코드는 `"0"`이며 이후 정수를 base62로 인코딩한다.
- 없는 코드를 확장하면 `KeyError`를 발생시킨다.
- 해시 테이블 구현을 생성자로 주입할 수 있어 연결 리스트와 선형 탐지를 바꿔 쓸 수 있다.

## 5. 웹 서버

- `make serve`는 `src/server.py`의 표준 라이브러리 HTTP 서버를 포트 8000에서 실행한다.
  `PORT` 환경/Make 변수로 포트를 바꿀 수 있다.
- `/`는 URL 입력 폼과 성공·오류 결과를 HTML로 반환한다. 단축 결과는
  `/s/<code>` 경로로 표시한다.
- `/s/<code>`는 등록된 URL로 리다이렉트하고, 없는 코드는 404다.
- `/table`은 구현별 버킷, 노드/슬롯 위치, 키 비교와 Horner 해시 계산을 보여 준다.
- 폼은 `chaining` 또는 `linear` 테이블을 선택한다. 선형 탐지의 짧은 URL은
  `?table=linear`를 포함하며 `/table?table=linear`는 검사한 슬롯 순서를 보여 준다.
- 입력은 HTML escape하고 서버는 외부 패키지를 사용하지 않는다.

## 6. 경계 사례 및 테스트

- base62: 0, 알파벳의 첫/마지막 문자, 62 경계, 큰 정수 왕복,
  음수·잘못된 타입·빈 문자열·잘못된 문자.
- 해시 테이블: 빈 테이블 조회/삭제, 같은 키 덮어쓰기, 충돌한 키 유지,
  없는 키 기본값/삭제, 맨 끝 버킷, 재해싱 전후 데이터 보존, 만석·충돌.
- 선형 탐지: 마지막 슬롯에서 0번 슬롯으로 순환, 만석 삽입 실패,
  tombstone을 건너 조회하고 재사용.
- 단축기: 정상 URL, 같은 URL 중복, 잘못된 스킴/상대 URL/호스트 없는 URL,
  앞뒤 공백, 없는 코드.
- 서버: 메인 폼, 성공/오류, 리다이렉트, 없는 코드 404, `/table`.
- 테스트는 `python3 -m unittest discover -s tests -v` 또는 `make test`로 실행한다.
