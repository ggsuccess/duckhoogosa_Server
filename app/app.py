# -'-coding:utf-8-'-
import sys
import json
import datetime
import pprint
import time
from flask import Flask, session, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_restful import reqparse, abort, Api, Resource
from util import getFileNameFromLink
from scheduleModule import imageScheduleQueue
from requests import get
from functools import wraps
from flask_cors import CORS, cross_origin
import logging
import sys
import config

from setConfigure import set_secret

app = Flask(__name__)

set_secret(__name__)

# 환경변수 로드 (from secret.json)
conf_host = getattr(sys.modules[__name__], 'DB-HOST')
conf_user = getattr(sys.modules[__name__], 'DB-USER')
conf_password = getattr(sys.modules[__name__], 'DB-PASSWORD')

# 환경변수 로드 (from config.py)
env = sys.argv[1] if len(sys.argv) >= 2 else 'dev'
app.config.from_object(config.Base)
if env == 'dev':
    print("DEV!!!!!!!!!!!!")
    app.config.from_object(config.DevelopmentConfig)
elif env == 'test':
    print("TEST!!!!!!!!!!!!")
    app.config.from_object(config.TestConfig)
elif env == 'prod':
    print("PRODUCTION!!!!!!!!!!!!")
    app.config.from_object(config.ProductionConfig)
else:
    raise ValueError('Invalid environment name')

# flask CORS
print(app.config['CLIENT_HOST'])
cors = CORS(app, origins=[app.config['CLIENT_HOST']], headers=['Content-Type'],
            expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)
# flask REST-api
api = Api(app)
# logging
logging.getLogger('flask_cors').level = logging.DEBUG

print("This APP use __________________ ", app.config['DATABASE_NAME'], "______________ Are you sure?")

connection = MongoClient(conf_host,
                         username=conf_user,
                         password=conf_password,
                         authSource='duck',
                         authMechanism='SCRAM-SHA-256')
db = connection[app.config['DATABASE_NAME']]

# 테스트용 스키마
tool = db.tool
posts = db.posts

# 실제 사용 스키마
commentsCollections = db.comments
problemsCollections = db.problems
ratingsColeections = db.ratings
usersCollections = db.users


# # 로그인할때 세션에 집어넣어음.
@app.route('/*', methods=['OPTION'])
def option():
    # print("OPTION RCVD 전체 도메인")
    return "GOOD"


def login_required():
    def _decorated_function(f):
        @wraps(f)
        def __decorated_function(*args, **kwargs):
            if 'logged_in' in session:
                print("🍎", session['email'], "session pass")
                return f(*args, **kwargs)
            else:
                print("✂️ ___no session___")
                return "NO SESSION ERROR"

        return __decorated_function

    return _decorated_function


@app.route('/login', methods=['POST', 'OPTION'])
def Login():
    if 'access_token' in request.headers:
        access_token = request.headers['access_token']
        data = get("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=" + access_token).json()
        if 'user_id' in data:
            email = data['email']
            session['logged_in'] = True
            session['email'] = email
            result = usersCollections.find_one({"email": email})
            if result is None:
                user = {
                    "email": email,
                    "nickname": None,
                    "img": None,
                    "tier": None,
                    "answerCount": 0,
                    "totalProblemCount": 0,
                    "solution": []
                }
                usersCollections.insert_one(user)
                print("🎉", email, " inputed user")

            return {'result': True}
        else:
            session.clear()
            return {'result': False, "reason": "Token is not validate"}
    else:
        return {"result": False, "reason": "Req didn't has token"}


@app.route('/logout', methods=['POST', 'OPTION'])
@login_required()
def Logout():
    print("logout SEQ", session)
    session.clear()
    return {'result': True}


app.secret_key = getattr(sys.modules[__name__], 'FN_FLASK_SECRET_KEY')

# json 쪼개는 로직
parser = reqparse.RequestParser()
parser.add_argument('task')
parser.add_argument('email')
parser.add_argument('comment')
parser.add_argument('problem_id')
parser.add_argument('id')
parser.add_argument('representImg')
parser.add_argument('next_problem')
parser.add_argument('load_count')
parser.add_argument('word')
parser.add_argument('genre')


@app.route("/")
def helloroute():
    print("first hello")
    return "hello"


class CommentList(Resource):
    @login_required()
    def get(self, problem_id):
        temp = commentsCollections.find({"problem_id": problem_id}).sort('day', -1)
        result = []
        for v in temp:
            v['_id'] = str(v['_id'])
            v['day'] = str(v['day'])
            nick = usersCollections.find_one({"email": v['email']})
            if type(nick) != None:
                v['nick'] = nick['nickname']
                v['img'] = nick['img']
                result.append(v)
        return json.dumps(list(result))


class Comment(Resource):
    @login_required()
    def post(self):
        args = parser.parse_args()
        comment = {
            "email": args.email,
            "problem_id": args.problem_id,
            "comment": args.comment,
            "day": int(time.mktime(datetime.datetime.utcnow().timetuple())) * 1000}

        result_id = commentsCollections.insert_one(comment).inserted_id
        obj = {"_id": str(result_id)}
        return json.dumps(obj)


class ProblemGet(Resource):
    def get(self, problem_id):
        print(problem_id, "give me problem")
        result = problemsCollections.find_one(ObjectId(problem_id))
        result['_id'] = str(result['_id'])
        return result


class Problem(Resource):
    def post(self):
        args = parser.parse_args()
        obj = {"link": args['representImg'], "filename": getFileNameFromLink(args['representImg'])}
        imageScheduleQueue.append(obj)
        content = request.get_json()
        content['nickName'] = "아무개 G"
        content['ratingNumber'] = 0
        content['tryCount'] = 0
        content['okCount'] = 0
        content['tags'] = ["테스트"]
        for problem in content['problems']:
            problem['tryCount'] = 0
            problem['okCount'] = 0
        # pprint.pprint(content)
        result_id = problemsCollections.insert_one(content).inserted_id
        obj = {"_id": str(result_id)}
        return json.dumps(obj)


class ProblemMain(Resource):
    def post(self):
        args = parser.parse_args()
        count = problemsCollections.count()
        if count <= int(args['next_problem']):
            return json.dumps('NoData')
        sortedproblem = problemsCollections.find().sort('date', -1).skip(int(args['next_problem'])) \
            .limit(5)
        result = []
        for v in sortedproblem:
            v['_id'] = str(v['_id'])
            result.append(v)
        if len(result) is 0:
            return json.dumps('NoData')
        return json.dumps(result)

    @login_required()
    def get(self):
        return "good!"


class ProblemSearch(Resource):  # 제목 OR 검색
    # @login_required()
    def post(self):
        args = parser.parse_args()
        problemsCollections.drop_index('*')
        count = problemsCollections.count()
        word = args['word']
        if count <= int(args['next_problem']):
            return json.dumps('NoData')
        problemsCollections.create_index([('title', 'text')])
        sortedproblem = problemsCollections.find({"$text": {"$search": word}}).sort('date', -1).skip(
            int(args['next_problem'])) \
            .limit(5)
        result = []
        for v in sortedproblem:
            v['_id'] = str(v['_id'])
            result.append(v)
        if len(result) is 0:
            return json.dumps('NoData')
        return json.dumps(result)


class ProblemGenre(Resource):  # 장르검색
    # @login_required()
    def post(self):
        args = parser.parse_args()
        problemsCollections.drop_index('*')
        count = problemsCollections.count()
        word = args['genre']
        if count <= int(args['next_problem']):
            return json.dumps('NoData')
        problemsCollections.create_index([('genre', 'text')])
        sortedproblem = problemsCollections.find({"$text": {"$search": word}}).sort('date', -1).skip(
            int(args['next_problem'])) \
            .limit(5)
        result = []
        for v in sortedproblem:
            v['_id'] = str(v['_id'])
            result.append(v)
        if len(result) is 0:
            return json.dumps('NoData')
        return json.dumps(result)


class ProblemSolution(Resource):
    @login_required()
    def post(self):
        content = request.get_json()
        # print(content, "__제출된 답__")
        original = problemsCollections.find_one(ObjectId(content['problem_id']))
        original_answers = []
        for problem in original['problems']:
            arr = [];
            if problem['subjectAnswer'] is not False and len(problem['choice']) == 1:
                original_answers.append(problem['subjectAnswer'])
                continue

            for index, choice in enumerate(problem['choice']):
                if choice['answer']:
                    arr.append(index)
            original_answers.append(arr)
        # print(original_answers, "__ 진짜 답 __")

        try_count = len(original_answers)
        right_count = 0
        check_problem = []
        temp_obj = {}
        for i, answer in enumerate(content["answer"]):
            # print(answer == original_answers[i], "정답 비교 <>")
            if answer == original_answers[i]:
                right_count = right_count + 1
                problemsCollections.update_one({"_id": ObjectId(content['problem_id'])},
                                               {'$inc': {"problems." + str(i) + ".okCount": 1,
                                                         "problems." + str(i) + ".tryCount": 1}})
                temp_obj['ok'] = True
            else:
                problemsCollections.update_one({"_id": ObjectId(content['problem_id'])}, {'$inc':
                    {
                        "problems." + str(
                            i) + ".tryCount": 1}})
                temp_obj['ok'] = False
            check_problem.append(temp_obj)
            temp_obj = {}

        problemsCollections.update_one({"_id": ObjectId(content['problem_id'])},
                                       {'$inc': {"okCount": right_count, "tryCount": try_count}})
        original = problemsCollections.find_one(ObjectId(content['problem_id']))
        for i, problem in enumerate(original['problems']):
            check_problem[i]['num'] = i + 1
            check_problem[i]['okCount'] = problem['okCount']
            check_problem[i]['tryCount'] = problem['tryCount']

        response_obj = {
            "_id": content['problem_id'],
            "checkProblem": check_problem,
            "commentCount": commentsCollections.count_documents({"problem_id": content['problem_id']}),
            "all_okCount": original['okCount'],
            "all_tryCount": original['tryCount'],
        }
        # print(content, "이거 데이터 검증")

        solution_obj = {
            "problem_id": content['problem_id'],
            "title": original['title'],
            "answer": content['answer'],
            "img": original['representImg'],
            "date": content['date'],
            "accuracy": round((right_count / try_count) * 100, 2)
        }

        usersCollections.update_one({"email": content['email']},
                                    {'$push': {'solution': solution_obj},
                                     '$inc': {'answerCount': right_count, 'totalProblemCount': try_count}
                                     })
        return json.dumps(response_obj)


class ProblemEvalation(Resource):
    @login_required()
    def post(self):
        evaluation = request.get_json()
        # print('평가', evaluation)
        rating = {
            "problem_id": evaluation['_id'],
            "quality": evaluation['evalQ'],
            "dificulty": evaluation['evalD'],
            "email": evaluation['email']
        }
        comment = {
            "problem_id": evaluation['_id'],
            "email": evaluation['email'],
            "comment": evaluation['comments'],
            "day": datetime.datetime.utcnow()
        }
        commentsCollections.insert_one(comment)
        ratingsColeections.insert_one(rating)
        return "good!"


class Account(Resource):
    @login_required()
    def get(self):
        user = usersCollections.find_one({'email': session['email']})
        problems = problemsCollections.find({'email': session['email']})
        new_problems = [];
        for problem in problems:
            problem['img'] = problem.pop('representImg')
            problem['_id'] = str(problem['_id'])
            new_problems.append(problem)
        user['problems'] = new_problems

        new_solutions = [];
        for solution in user['solution']:
            solution['successRate'] = solution.pop('accuracy')
            new_solutions.append(solution)

        user["solution"] = new_solutions
        user['_id'] = str(user['_id'])
        return user


class AccountNick(Resource):
    @login_required()
    def post(self):
        evaluation = request.get_json()
        nick = evaluation['nick']
        usersCollections.update_one({'email': session['email']},
                                    {'$set': {"nickname": nick}})
        return 'ok'


class AccountImg(Resource):
    @login_required()
    def post(self):
        pic = request.get_json()
        img = pic['img']
        usersCollections.update_one({'email': session['email']},
                                    {'$set': {"img": img}})
        return 'ok'


# URL Router에 맵핑한다.(Rest URL정의)

# comments _ POST
api.add_resource(Comment, '/comment')
# comments _ GET
api.add_resource(CommentList, '/comment/<string:problem_id>')

# problem _ POST
api.add_resource(ProblemMain, '/problem/main')
api.add_resource(ProblemSearch, '/problem/search')
api.add_resource(ProblemGenre, '/problem/genre')

# problem _ POST
api.add_resource(ProblemSolution, '/problem/solution')
api.add_resource(ProblemEvalation, '/problem/evaluation')

# problem - GET, POST
api.add_resource(ProblemGet, '/problem/<string:problem_id>')
api.add_resource(Problem, '/problem')

# account - GET, POST
api.add_resource(Account, '/account/info')
api.add_resource(AccountNick, '/account/nick')

api.add_resource(AccountImg, '/account/img')

# 서버 실행
if __name__ == '__main__':
    app.secret_key = getattr(sys.modules[__name__], 'FN_FLASK_SECRET_KEY')
    print(app.config)
    app.run(port=app.config['PORT'], host=app.config['SERVER_HOST'])
    print("🍨__APP START__")
