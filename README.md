# 0.3/api
FAST API 구현완료

# Swagger UI로 API 요청 방법
## 1. FastAPI 실행 
```uvicorn src.ez2z.app:app --reload```
## 2. Swagger UI 접근
http://127.0.0.1:8000/docs   
경로에 Swagger UI 생성되어 API의 모든 엔드포인트와 요청 형식을 확인가능
## 3. API 요청
- Swagger UI 페이지에서 /add-song-data/ 엔드포인트를 찾기
- "Try it out" 버튼이 나타납니다. 이 버튼을 클릭하여 테스트 모드를 활성화
- JSON 형식의 요청 본문에 keyword를 입력
