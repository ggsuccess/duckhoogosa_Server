# 서버 사용설명서

### 앱실행
1) source /venv/bin/activate
2) python3 /app/app.py

### 패키지 설치 후엔 패키지를 추가.
pip3 freeze > requirements.txt

### pull upstream 후에는 패키지를 설치.
pip3 install -r requirements.txt

### 파일 구성
- model.py 기존에 작성했던 ORM 흔적
- app 메인
- app/secret.json 비밀정보 ( 이 위치에 있어야함 )
- app/util 자주쓰는 함수관리용( 당장은 uitl.py에 작성 후 사용)

## pylint 설정
https://stackoverflow.com/questions/38134086/how-to-run-pylint-with-pycharm
- 여기 첫번째 답변 기준으로 모든 프로젝트 파일을 검사하면서 관리.


## 가상 환경 설정
- pip install venv
- python3 -m venv venv
- which python3 
- source venv/bin/activate
- /Users/mac/WebstormProjects/4WEEKS/DuckhooGosa-server/venv/bin/python3

=> 이렇게 떠야 정상. 원래 파이선 설치 경로면 에러발생