from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

# TODO: Add HTTP method check
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username_to_find: str):
    # TODO: Complete `/history/<slug:username>` API
    try:
        res = User.objects.get(username=username_to_find)
        print(res)
        response = {
            "code": 0,
            "data" : [model_to_dict(s, exclude= ["id", "user", "avatar"])for s in res.submission_set.all().order_by('-time')]
            # 这里参考了答案中的实现
            
        }
       
        return JsonResponse(response)

    except:
        return JsonResponse({"code": -1})
    # raise NotImplementedError


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
   
    content = req.body.decode()
    clear_content = content.replace('\n', '').replace('\r', '')
   
    info = json.loads(clear_content) 
  
    
    try:
        user, avatar,  content = info["user"], info["avatar"], info["content"]
    except KeyError:
        return JsonResponse({
            "code": 1,
            "msg": "参数不全"
        })
    if len(user) > 255:
        return JsonResponse({
            "code": -1,
            "msg": "用户名长度大于255"
        })
    if len(avatar) > 102400:
        return JsonResponse({
            "code": -2,
            "msg": "图像大小大于75KiB", # Each character in BASE64 carries 6bits, or 0.75Byte.
        })
    # raise NotImplementedError
    try:
        total_score, sub = utils.judge(content)
        subs = f"{sub[0]} {sub[1]} {sub[2]}"
    except TypeError:
        return JsonResponse({
            "code": -3,
            "msg": "提交内容格式错误"
        })
    print(user)
    submitter = User.objects.filter(username = user).first()
    print("mark2")
    if not submitter:
        print("mark3")
        submitter = User.objects.create(username = user)
        print("mark4")
        
        

    Submission.objects.create(username = submitter, avatar = avatar, score = total_score, subs = subs)
    print("mark5")
    return JsonResponse({
        "code": 0,
        "msg": "提交成功",
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })

@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })

    # TODO: Complete `/vote` API
    info = json.loads(req.body)
    user_be_voted = info["user"]
    if not user_be_voted:
        return JsonResponse({"code": -1})
    if not User.objects.filter(username = user_be_voted).first():
        return JsonResponse({"code": -1})
    else:
        u = User.objects.get(username=user_be_voted)
        u.votes = F("votes") + 1
        u.save()
        return JsonResponse({
        "code": 0,
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })
    
    # raise NotImplementedError
