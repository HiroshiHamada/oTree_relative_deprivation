from otree.api import *
import random


class C(BaseConstants):
    NAME_IN_URL = 'relative_deprivation'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 2
#    NUM_SUCCESS = random.randint(1,5)
    Rvec = [3,5,2,4]#セッション毎に変わるグループ共通の利益率
    nvec = [2,4]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    x = models.IntegerField()
    R = models.IntegerField()#セッション毎に変わるグループ共通の利益率
    PROFIT = models.IntegerField()
    n = models.IntegerField()

class Player(BasePlayer):
    action = models.IntegerField(
        choices=[[0, 'no'],[1,'yes (invest 100)']],
        label="Do you invest? ",initial=(0)
    )
    outcome = models.IntegerField(
        choices=[[5, 'very satisfied'],[4, 'satisfied'],[3, 'neither'],[2, 'dissatisfied'], [1, 'very dissatisfied']],
        label='How do you feel about the result?',
        widget=widgets.RadioSelect,
    )
    profit = models.IntegerField()


# FUNCTIONS
def set_profit(group: Group):#グループオブジェクトを引数にした関数，引数groupのタイプ（クラス）がGroupであることを指定
    players = group.get_players()#playerを取得
    group.x = sum([p.action for p in players])#投資者数の総数ｘを計算
    xids=[p.id_in_group for p in players if p.action==1]#投資者のplayeridを格納するリスト
    #投資者数が多い場合の抽選
    if group.n < group.x:
        win=random.sample(xids,group.n)#group.nだけxidsから勝者を選択
    for p in players:
        if p.action == 0:
            p.profit=0 # 非投資者の利得を計算
        else:
            if group.n >= group.x:
                p.profit= group.PROFIT
            else:
                if p.id_in_group in win:
                    p.profit= group.PROFIT
                else:
                    p.profit= -100


def set_parameters(group: Group):#グループオブジェクトを引数にした関数，引数groupのタイプ（クラス）がGroupであることを指定
    group.R = C.Rvec[group.round_number-1]
    group.PROFIT = group.R*100-100
    group.n = C.nvec[group.round_number-1]
               

# PAGES
class MyWaitPage(WaitPage):
    after_all_players_arrive = set_parameters


class Contribute(Page):
    form_model = 'player'
    form_fields = ['action']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_profit


class Results(Page):
    form_model = 'player'
    form_fields = ['outcome']


page_sequence = [MyWaitPage, Contribute, ResultsWaitPage, Results]
