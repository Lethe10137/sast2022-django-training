from lb.models import Submission, User
from random import randint
import functools
import pathlib
def get_leaderboard():
    """
    Get the current leaderboard
    :return: list[dict]
    """

    # 坏了，我似乎已经忘了 ORM 中该怎么调 API 了
    # 在这里你可选择
    #    1. 看一眼数据表, 然后后裸写 SQL
    #    2. 把所有数据一股脑取回来然后手工选出每个用户的最后一次提交
    #    3. 学习 Django API 完成这个查询

    # 方案1: 直接裸写 SQL 摆烂，注意，由于数据库类型等因素，这个查询未必能正确执行，如果使用这种方法可能需要进行调整
    # subs = list(Submission.objects.raw(
    #         """
    #         SELECT
    #             `lb_submission`.`id`,
    #             `lb_submission`.`avatar`,
    #             `lb_submission`.`score`,
    #             `lb_submission`.`subs`,
    #             `lb_submission`.`time`
    #         FROM `lb_submission`, (
    #             SELECT `user_id`, MAX(`time`) AS mt FROM `lb_submission` GROUP BY `user_id`
    #         ) `sq`
    #         WHERE
    #             `lb_submission`.`user_id`=`sq`.`user_id` AND
    #             `time`=`sq`.`mt`;
    #         ORDER BY
    #             `lb_submission`.`subs` DESC,
    #             `lb_submission`.`time` ASC
    #         ;
    #         """
    # ))
    # return [
    #     {
    #         "user": obj.user.username,
    #         "score": obj.score,
    #         "subs": [int(x) for x in obj.subs.split()],
    #         "avatar": obj.avatar,
    #         "time": obj.time,
    #         "votes": obj.user.votes
    #     }
    #     for obj in subs
    # ]

    # 方案2：一股脑拿回本地计算
    all_submission = Submission.objects.all()
    subs = {}
    for s in all_submission:
        if s.username not in subs or (s.username in subs and s.time > subs[s.username].time):
            subs[s.username] = s

    subs = sorted(subs.values(), key=lambda x: (-x.score, x.time))
    return [
        {
            "user": obj.username.username,
            "score": obj.score,
            "subs": [int(x) for x in obj.subs.split()],
            "avatar": obj.avatar,
            "time": obj.time,
            "votes": obj.username.votes
        }
        for obj in subs
    ]

    # 方案3：调用 Django 的 API (俺不会了
    # ...

def judge(content: str):
    """
    Convert submitted content to a main score and a list of sub scors
    :param content: the submitted content to be judged
    :return: main score, list[sub score]
    """

    # TODO: Use `ground_truth.txt` and the content to calculate scores.
    #  If `content` is invalid, raise an Exception so that it can be
    #  captured in the view function.
    #  You can define the calculation of main score arbitrarily.
    submit = []
    for a in content:
        if(a == '0'):
            submit.append(0)
        if(a == '1'):
            submit.append(1)
    # print(submit)
    subs = [0,0,0]
    # print(submit)
    print(len(submit))

    ground_truth_position = pathlib.Path.cwd() /"lb"/ "ground_truth.txt"
    

    with open(str(ground_truth_position ),"r") as f:
        
        all_truth = [w.split(",")[1:] for w in f][1:]
        standard_answers = [[w[k][0] for w in all_truth]for k in range(3)] 
    
    
    try:
        if(len(submit) != 3000):
            print("submit lentgh is ",len(submit))
            raise
        for one_answer in submit:
            if(one_answer != 0 and one_answer != 1):
                raise

        submits = [[submit[k+j*3] for j in range(1000)]for k in range(3)]

        for i in range(3):
            
            std = standard_answers[i]
            sub = submits[i]
            correct = len([_ for _ in range(1000) if (std[_] == "T" and sub[_] == 1) or (std[_] == "F" and sub[_] == 0)])
            subs[i] = correct 

        
    except:
        raise ValueError
    print(subs)
    return sum(subs)//3, subs
