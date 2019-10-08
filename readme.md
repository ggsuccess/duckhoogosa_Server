# 서버 사용설명서

### 앱실행
1) source /venv/bin/activate
2) python3 /app/app.py [dev]  [옵션 없거나 dev면 dev]
3) python3 /app/app.py prod   [서버실행]
3) python3 /app/app.py test   [테스트서버실행]

### 백그라운드 실행 (with log)
* nohup python3 app/app.py prod > app.log &
> 에러출력이 파일에 찍혀서 터미널로 확인 안됨 주의)    
* netstat -ntlp | grep :8000      
> (포트점유 확인)
* tail -f app.log   
> (로그 확인)

### 호스트 정보
* 54.180.82.249

### 실행유의사항
bash theme을 설정해놓은 ec2user에서 가상환경으로 실행

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
서버는 EC2user 계정으로 실행
- pip install venv
- python3 -m venv venv
- which python3 
- source venv/bin/activate
- /Users/mac/WebstormProjects/4WEEKS/DuckhooGosa-server/venv/bin/python3

=> 이렇게 떠야 정상. 원래 파이선 설치 경로면 에러발생

## 디버깅.
- 셋팅 다되어있는데 CORS나면 그냥 잘못된 라우팅 또는 로직이 터져서 그냥 응답이 안간거다. 