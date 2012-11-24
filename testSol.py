#coding:utf8
import math
import copy
import random
import time
#计算士兵2vs2的战斗结果
#16 vs 16 = 256种组合
#每个回合 移动 1次 或者 攻击1次
#getattr 不能和 deepcopy两个函数一起处理
#搜索深度

INFINITY = 10000
MAX_DEPTH = 2
solKind = [
{'health':100, 'attack':10, 'range':1, 'speed':2},
{'health':150, 'attack':5, 'range':1, 'speed':1},
{'health':100, 'attack':5, 'range':2, 'speed':1},
{'health':50, 'attack':10, 'range':2, 'speed':1},
{'health':100, 'attack':0, 'range':0, 'speed':0}, #城墙
]
attCoff = [
[1., 1., 1.5, 1., 1.],
[1., 1., 1., 1., 1.],
[1., 1., 0.75, 1.5, 1.],
[1.25, 1.25, 0.75, .5, 1.],
[1., 1., 1., 1., 1.],
]



def if_(con, v0, v1):
    if con:
        return v0
    return v1
def sign(v):
    if v >= 0:
        return 1
    return -1

#计算当前用户可能的 移动 
#评估所有移动的值
#返回最大的可能

#一方 下 另一方 下  更新状态
#MAX MIN  
#MIN MAX 
def minimaxDecision(state, game):
    player = state['toMove']
    #我方期望 我方胜利概率最大的路径
    #在 B结束后 A B update A B update
    def maxValue(state, depth, alpha, beta):
        #下一回合开始之前 首先更新状态
        #if player == 'A':
        #    game.update(state)
        #print "max", player, state['toMove'], state['solAttribute']
        nodeCount = 1
        if depth <= 0:#阻止搜索 计算 结果
            return game.utility(state, player), nodeCount

        if game.gameOver(state):
            ##print "max over"
            return game.utility(state, player), nodeCount
        v = -INFINITY
        moved = False
        for a in game.actions(state):
            newV, nc = minValue(game.result(state, a), depth-1, alpha, beta)
            if newV > beta:
                return beta+1, nodeCount
            #if newV < beta:
            beta = newV
            #print "max newV nc", newV, nc
            v = max(v, newV)
            moved = True
            nodeCount += nc
        #没有动作可以执行 地图上放满了 则执行程序
        if not moved:
            ##print "max move"
            return game.utility(state, player), nodeCount
        return v, nodeCount

    #敌方期望 我方的胜利概率最小的路径
    def minValue(state, depth, alpha, beta):
        #移动 A 移动 B update 状态
        #if player == 'B':
        #    game.update(state)

        #print "min", player, state['toMove'], state['solAttribute']
        nodeCount = 1
        if depth <= 0:#阻止搜索 计算 结果
            return game.utility(state, player), nodeCount
        #没有移动则返回当前运行结果
        if game.gameOver(state):
            ##print "min over"
            return game.utility(state, player), nodeCount
        v = INFINITY
        moved = False
        for a in game.actions(state):
            newV, nc = maxValue(game.result(state, a), depth-1, alpha, beta)
            #print "min newV nc", newV, nc
            if newV < alpha:
                return alpha-1, nodeCount
            #if newV > alpha:
            alpha = newV

            v = min(v, newV)
            moved = True
            nodeCount += nc
        if not moved:#没有空闲位置移动
            ##print "min move"
            return game.utility(state, player), nodeCount
        return v, nodeCount

    v = -INFINITY
    possibleAct = []
    nodeCount = 0
    for a in game.actions(state):
        #print "start stra", a
        newState = game.result(state, a)
        if player == 'B':
            game.update(newState)

        newV, nc = minValue(newState, MAX_DEPTH, -INFINITY, INFINITY)#max Jie
        print "stragtry", newV, a
        if newV > v:
            possibleAct = [a]
        elif newV == v:#误差没有意义 本身就是粗糙的估值
            possibleAct.append(a)
        v = max(v, newV)
        nodeCount += nc
    return possibleAct, nodeCount, v

#没有先后顺序 计算回合结果的时候 对方也会动作 不只有我方会动作
class Game(object):
    MAX_NUM = 5
    WIDTH = 9
    HEIGHT = 2
    LEFT_BOUND = WIDTH/2-1
    RIGHT_BOUND = LEFT_BOUND+2
    MAX_UPDATE = 10
    HEALTH_ARGUMENT = 2
    def display(self, state):
        for y in xrange(0, self.HEIGHT):
            for x in xrange(0, self.WIDTH):
                sol = state['boardSol'].get((x, y))
                if sol != None:
                    solData = state['solAttribute'].get(sol)
                    print solData['color'], str(solData['kind']), "%.3d"%(solData['health'])+'| ',
                else:
                    print 'XXXXXXX| ',
            print
                
            
    #开始游戏
    #A 方推测位置放置士兵  统计推测节点数目
    #显示A 回合结果
    #B 方推测位置放置士兵
    #显示B 回合结果
    #A B 同时下子 当前局势对双方是公平的
    #最后计算状态变化 result 不会 update状态
    #在min max 中 下子 我下子 对方 下子 更新 状态 下一状态 
    #两个阶段 优势占据更好的位置
    #下子位置不可能冲突 两者不再同一个区域 只有 移动才冲突
    #A 下子 暴露给对方
    #B 下子 失去先机 
    #更新 AB 状态
    #防止冲突的方式？


    #A 下
    #B 下
    #更新
    def start(self):
        print "start Game"
        while not self.gameOver(self.initial):
            self.initial['toMove'] = 'A'
            print "toMove", self.initial['toMove']
            possibleAct, nodeCount, value = minimaxDecision(self.initial, self)
            movA = None
            #if value >= 0:#估值大于0才下子 放置子能够攻击到对方
            if len(possibleAct) > 0:
                movA = possibleAct[random.randint(0, len(possibleAct)-1)]
            #pass 跳过下棋子 
            if movA != None:
                self.initial = self.result(self.initial, movA)
                #self.initial = self.result(self.initial, mov)
            #没有移动 则 计算一下回合结果
            #if len(possibleAct) == 0:
            #    self.update(self.initial)

            print "compute Node A ", nodeCount, possibleAct, value 
            #self.display(self.initial)
            #time.sleep(0.5)

            #print "toMove", self.to['toMove']
            #B 开始 移动 计算B 位置 
            self.initial['toMove'] = 'B'
            print "toMove", self.initial['toMove']
            possibleAct, nodeCount, value = minimaxDecision(self.initial, self)
            movB = None
            #if value >= 0:
            if len(possibleAct) > 0:
                movB = possibleAct[random.randint(0, len(possibleAct)-1)]
                #self.initial = self.result(self.initial, mov)
            #命令阶段 推测对方下棋子 接着棋盘状态变化
            #self.initial['toMove'] = 'B'
            #命令阶段 推测对方下棋子  棋盘状态变化
            #跳过下棋子
            if movB != None:
                self.initial = self.result(self.initial, movB)
            #if len(possibleAct) == 0:
            #    self.update(self.initial)
            #更新状态
            self.update(self.initial)
            print "compute Node B ", nodeCount, possibleAct, value
            self.display(self.initial)
            #time.sleep(0.5)
        

    #A 城防掉光 B 城防掉光
    #A B 无新人 可走 A 死光光
    #A 死光光 B 死光光

    #addNewSol  doDead
    #
    def gameOver(self, state):
        if state['leftDefense']['health'] <= 0 or state['rightDefense']['health'] <= 0:
            return True
        if state['leftSolNum'] >= self.MAX_NUM and len(state['leftSoldier']) == 0:
            return True
        if state['rightSolNum'] >= self.MAX_NUM and len(state['rightSoldier']) == 0:
            return True
        return False

    #1行 多行的时候 拆除城墙即可
    def testNeedUpdate(self, state):
        if state['leftDefense']['health'] <= 0 or state['rightDefense']['health'] <= 0:
            return True
        if state['leftSolNum'] >= self.MAX_NUM and len(state['leftSoldier']) == 0:
            return True
        if state['rightSolNum'] >= self.MAX_NUM and len(state['rightSoldier']) == 0:
            return True
        #无兵可走 不用 更新状态
        if len(state['rightSoldier']) == 0 and len(state['leftSoldier']) == 0:
            return True
        return False
    
    #快速更新状态得到 每行的战斗终止结果 回合直到结束
    #所有士兵找到攻击目标 执行移动攻击操作
    #依次遍历 0 1 2 3 4 找到士兵
    #         B  A   B A
    #找到最近的士兵 距离 杀死时间 
    #开销最小的最近的士兵作为敌人攻击到死为止 临近的敌人
    # row ---> 1 1  2 1 cost 值

    #我方每个士兵攻击最近敌人的 开销和 / 我方士兵的数量
    #地方每个士兵攻击最近敌人的 开销和 / 地方士兵数量
        

    #根据当前状态值 玩家类型调整状态值
    #计算回合值 针对当前玩家的值
    def utility(self, state, player):
        #print "utilit"
        #print '\t', state, player
        #没有放置士兵的位置 等待所有士兵死亡 
        #接着返回结果
        #回合成本
        num = 0
        #拷贝新的进行状态更新
        #if not self.testNeedUpdate(state):
        #    state = copy.deepcopy(state)
        #更新超过10步则停止 为什么10？ 移动次数 攻击次数的 模拟游戏结果
        while not self.testNeedUpdate(state): #and num < self.MAX_UPDATE:
            #print "update ....", state['solAttribute']
            self.update(state)    
            num += 1

        score = 0
        #考虑城墙 和 士兵两个数值问题 城墙没坏 考虑士兵
        #士兵没死 只考虑士兵
        #伤害最大化 的组合 ---> 对方总兵力 和 我输出的伤害

        AFail = state['leftSolNum'] >= self.MAX_NUM and len(state['leftSoldier']) == 0 
        BFail = state['rightSolNum'] >= self.MAX_NUM and len(state['rightSoldier']) == 0
        if state['leftDefense']['health'] <= 0 and state['rightDefense']['health'] > 0:
            #对方城墙 士兵总损伤比
            totalHealth = 0
            leftHealth = 0
            totalHealth += solKind[4]['health']
            leftHealth += state['rightDefense']['health']
            for i in state['rightSoldier']:
                leftHealth += state['solAttribute'][i]['health'] 
                totalHealth += solKind[state['solAttribute'][i]['kind']]['health']
            #对方士兵死光光？
            if totalHealth > 0:
                score = -leftHealth*100/totalHealth
            else:
                score = -100
        elif state['rightDefense']['health'] <= 0 and state['leftDefense']['health'] > 0:
            totalHealth = 0
            leftHealth = 0
            totalHealth += solKind[4]['health']
            leftHealth += state['leftDefense']['health']
            for i in state['leftSoldier']:
                leftHealth += state['solAttribute'][i]['health'] 
                totalHealth += solKind[state['solAttribute'][i]['kind']]['health']
            #对方士兵死光光？
            if totalHealth > 0:
                score = leftHealth*100/totalHealth
            else:
                score = 100

        elif state['rightDefense']['health'] <= 0 and state['leftDefense']['health'] <= 0:
            score = 0
        elif AFail or BFail:
            ##print state
            if AFail and BFail:
                score = 0
            #B 剩余的生命值百分比 剩余百分比值？
            elif AFail:
                totalHealth = 0
                leftHealth = 0
                for i in state['rightSoldier']:
                    leftHealth += state['solAttribute'][i]['health'] 
                    totalHealth += solKind[state['solAttribute'][i]['kind']]['health']
                if totalHealth > 0:
                    score = -leftHealth*100/totalHealth
                else:
                    score = -100
            elif BFail:
                totalHealth = 0
                leftHealth = 0
                for i in state['leftSoldier']:
                    leftHealth += state['solAttribute'][i]['health'] 
                    totalHealth += solKind[state['solAttribute'][i]['kind']]['health']
                if totalHealth > 0:
                    score = leftHealth*100/totalHealth
                else:
                    score = 100
        #A B 都没失败 都有士兵存活计算当前场面上存活的生命值剩余量
        #剩余生命值 百分比的比较表示 A B 相对大小 50 -50
        """
        else:
            leftAHealth = 0
            totalAHealth = 0
            #ANum = len(state['leftSoldier'])
            for i in state['leftSoldier']:
                leftAHealth += state['solAttribute'][i]['health'] 
                totalAHealth += solKind[state['solAttribute'][i]['kind']]['health']

            leftBHealth = 0
            totalBHealth = 0
            #BNum = len(state['rightSoldier'])
            for i in state['rightSoldier']:
                leftBHealth += state['solAttribute'][i]['health'] 
                totalBHealth += solKind[state['solAttribute'][i]['kind']]['health']
            #总量 和 比例关系
            #总量2倍以上 
            if leftAHealth > leftBHealth*self.HEALTH_ARGUMENT:
                score = 100
            elif leftBHealth > leftAHealth*self.HEALTH_ARGUMENT:
                score = -100
            else:#剩余生命值在 100 200比例之间 比例大于10
                apercent = leftAHealth*100/totalAHealth
                bpercent = leftBHealth*100/totalBHealth
                if apercent - bpercent > 10:
                    score = 50
                elif bpercent - apercent > 10:
                    score = -50
                else:
                    score = 0
        """

        if player == 'B':
            score = -score

        #没有位置移动则返回平局状态 等待 有位置放置
        return score
        
    def __init__(self):
        freeList = set()
        #x----
        #y|
        #solId--->属性
        for x in xrange(0, self.WIDTH):
            for y in xrange(0, self.HEIGHT):
                freeList.add((x, y))
        #互相引用
        #soldier--->x, y
        #x, y --->soldier
        #每行排序好了的结果 [None, None]
        #rows = {},
        self.initial = dict(toMove='A', leftSoldier=set(), rightSoldier=set(), freeList=freeList, leftSolNum = 0, rightSolNum = 0, boardSol = {},  solAttribute = {}, solId = 0)

        #分离5个位置的伤害 到同一个伤害位置？ kind == 4
        #pos 不同----> 但是 health是相同的 分离生命值 ？
        #防御装置的 Y 值没有意义
        sol = dict(sid = self.initial['solId'], pos = (0, 0), kind=4, health = solKind[4]['health'], color='A')
        self.initial['solId'] += 1
        self.initial['leftDefense'] = sol
        self.initial['solAttribute'][sol['sid']] = sol
        for i in xrange(0, self.HEIGHT):
            self.addDefense(self.initial, (0, i), sol)

        sol = dict(sid = self.initial['solId'], pos = (self.WIDTH-1, 0), kind=4, health = solKind[4]['health'], color='B')
        self.initial['solId'] += 1
        self.initial['rightDefense'] = sol
        self.initial['solAttribute'][sol['sid']] = sol
        for i in xrange(0, self.HEIGHT):
            self.addDefense(self.initial, (self.WIDTH-1, i), sol)

        #print "initOver", self.initial

    def addDefense(self, state, pos, sol):
        state['boardSol'][pos] = sol['sid'] 
        state['freeList'].remove(pos)
    
    #move回合制度模拟游戏  [kind,  [pos]]
    #Put soldier on board
    #构造新的状态
    #状态相关士兵信息
    #士兵状态 生命值 共用信息 sid kind  状态相关信息  health  pos
    #leftSoldier sid
    #solAttribute  sid->{sid, kind, pos, }
    #boardSol = [x, y]--->sid
    def addNewSol(self, newState, sol):
        newSid = newState['solId']
        newState['solId'] += 1
        sol['sid'] = newSid
        if sol['color'] == 'A':
            newState['leftSoldier'].add(sol['sid'])
            newState['leftSolNum'] += 1
        else:
            newState['rightSoldier'].add(sol['sid'])
            newState['rightSolNum'] += 1
        newState['solAttribute'][sol['sid']] = sol
        
    #A B 放子 接着 A B 行动 还是A 放子 A行动 B 放子 B 行动
    #def prepareNode()
    #Free Move Attack---> 攻击敌人到死 被别人攻击---> 将会反身攻击对方
    #攻击结果死亡 将会删除士兵
    #A 下子 更新回合状态
    #B 下子 更新回合状态
    def result(self, state, move):
        ##print "add sol", move, state['solAttribute']
        #print "get new State with move result"
        #print '\t', move
        newState = copy.deepcopy(state)
        newState['toMove'] = if_(state['toMove']=='A', 'B', 'A')
        sol = dict(pos = move[1], kind=move[0], health = solKind[move[0]]['health'], color=state['toMove'])#, state='Free'
        self.addNewSol(newState, sol)
        self.setMap(newState, sol)
        #更新一个回合状态 手动更新回合状态
        #self.update(newState)
        ##print newState['solAttribute']
        return newState
            

    def setMap(self, state, sol):
        state['boardSol'][sol['pos']] = sol['sid'] 
        state['freeList'].remove(sol['pos'])
    
    #死亡对象
    #cost 越小越好
    def calCost(self, state, sol, ene):
        if ene['health'] <= 0:
            return INFINITY
        dist = abs(sol['pos'][0]-ene['pos'][0])
        attRange = solKind[sol['kind']]['range']
        movTime = dist-attRange
        
        att = solKind[sol['kind']]['attack']
        attTime = math.ceil(ene['health']/(att*attCoff[sol['kind']][ene['kind']]))
        total = movTime+attTime
        return total

    #移动+攻击时间最少的敌人
    #敌人 按照 位置排序 x x ? M ? x
    #最相邻的两个敌人 作为攻击目标 其它目标忽略掉 

    #防御装置 每行都有 board
    #杀伤生命值 同一个实体
    def findTar(self, state, sol):
        #攻击目标已经有了 且 没有死亡 可以移动或者攻击
        """
        if sol['tar'] != None:
            ene = state['solAttribute'].get(sol['tar'])
            #攻击目标没有死亡 判定可以攻击或者移动
            if ene != None:
                if ene['health']
        """

        minTime = INFINITY
        tar = []
        for i in xrange(sol['pos'][0], -1, -1):
            ene = state['boardSol'].get((i, sol['pos'][1]))
            if ene != None:
                ene = state['solAttribute'][ene]
                if ene['color'] != sol['color']:
                    total = self.calCost(state, sol, ene)
                    if total < minTime:
                        minTime = total
                        tar = [ene]
                    elif total == minTime:
                        tar.append(ene)
                    break

        for i in xrange(sol['pos'][0], self.WIDTH, 1):
            ene = state['boardSol'].get((i, sol['pos'][1]))
            if ene != None:
                ene = state['solAttribute'][ene]
                if ene['color'] != sol['color']:
                    total = self.calCost(state, sol, ene)
                    if total < minTime:
                        minTime = total
                        tar = [ene]
                    elif total == minTime:
                        tar.append(ene)
                    break
        if len(tar) > 1:
            rd = random.randint(0, len(tar)-1)
            tar = tar[rd]
        elif len(tar) == 1:
            tar = tar[0]
        else:
            tar = None
        #if tar != None:
        #    sol['tar'] = tar['sid']
        return tar, minTime
    
    #not in freeList in busy
    #not in buysy in free
    #how to get a free position
    def clearMap(self, state, sol):
        if sol['kind'] == 4:
            for i in xrange(0, self.HEIGHT):
                state['boardSol'].pop((sol['pos'][0], i), None)
                state['freeList'].add((sol['pos'][0], i))
        else:
            state['boardSol'].pop(sol['pos'], None)
            state['freeList'].add(sol['pos'])
        
    #health -= 伤害
    #士兵死亡 处理 清空 
    #要在最后回合最后 清理 死亡士兵
    #地图  敌我双方士兵
    def doAttack(self, state, sol, tar):
        att = solKind[sol['kind']]['attack']
        tar['health'] -= attCoff[sol['kind']][tar['kind']]*att
        if tar['health'] <= 0:
            return True
        return False
        #    self.clearMap(state, tar)

    #暂时不考虑速度问题
    def doMove(self, state, sol, tar):
        direciton = sign(tar['pos'][0]-sol['pos'][0])
        newPos = sol['pos'][0]+direciton
        occ = state['boardSol'].get((newPos, sol['pos'][1]))
        if occ == None:
            self.clearMap(state, sol)
            sol['pos'] = (newPos, sol['pos'][1])
            self.setMap(state, sol)
        
    #执行行动或者攻击 命令
    #要移动 但是目标位置已经被 占用则等待下一回合
    #回合内 先攻击计算 再移动
    #防止 计算顺序 导致的 攻击问题A mov B att
    
    #返回：sol是否需要移动  tar 是否死亡
    def doMoveOrAttack(self, state, sol, tar):
        #不移动 防止 影响dist属性
        dist = abs(sol['pos'][0]-tar['pos'][0])
        attRange = solKind[sol['kind']]['range']
        if dist <= attRange:
            ret = self.doAttack(state, sol, tar)
            return False, ret
        else:
            return True, False
        
    #城墙被拆只删除一次
    #城墙占用多个位置 solAttribute中 
    #防御装置 破坏需要一次性全部删除
    def doDead(self, state, sol):
        self.clearMap(state, sol)
        if sol['color'] == 'A':
            if sol['sid'] in state['leftSoldier']:
                state['leftSoldier'].remove(sol['sid'])
        else:
            if sol['sid'] in state['rightSoldier']:
                state['rightSoldier'].remove(sol['sid'])

        state['solAttribute'].pop(sol['sid'], None)

    #更新当前回合状态
    #寻找最近的敌人
    #最近 最少回合可杀死的士兵

    #攻击
    #移动
    #死亡 但是死亡还是占用 位置 不能清理当前位置
    def update(self, state):
        allMov = []
        allDead = []
        #print "cursoldier"
        #print '\t', state['solAttribute']
        for s in state['solAttribute']:
            sol = state['solAttribute'][s]
            if sol['kind'] != 4:#不是防御建筑
                #if sol.get('state') == 'Free':#新放下的士兵不参与更新计算 不移动 不攻击 但是别人会攻击它
                #    sol.pop('state')
                #else:
                #没有必要阻止update了
                tar, cost = self.findTar(state, sol)
                #print "findTar", tar
                if tar != None:
                    move, dead = self.doMoveOrAttack(state, sol, tar)
                    #print "doMove or attack", move, dead
                    if move:
                        allMov.append([sol, tar])
                    if dead:
                        allDead.append(tar)
        for i in allMov:
            self.doMove(state, i[0], i[1])
        for i in allDead:
            self.doDead(state, i)
        #print "result"
        #print '\t', state['solAttribute']
            

    #计算当前状态可能的action
    #颜色不同放置的x位置不同
    def actions(self, state):
        #有剩余的子 4种类型 所有空白位置
        if state['toMove'] == 'A' and state['leftSolNum'] < self.MAX_NUM:
            def func():
                for i in xrange(0, 4):
                    #边界或者附近有士兵 +1 -1 是为远程考虑的 +2 -2？
                    #边界
                    for p in state['freeList']:#所有空闲位置 没有空闲位置怎么办？ 那就运行结束看结果
                        if p[0] <= self.LEFT_BOUND and p[0] > 0 and (p[0] == self.LEFT_BOUND or (p[0]+1, p[1]) not in state['freeList'] or (p[0]-1 != 0 and (p[0]-1, p[1]) not in state['freeList']) ):
                            yield i, p
            return func()
        if state['toMove'] == 'B' and state['rightSolNum'] < self.MAX_NUM:
            def func():
                for i in xrange(0, 4):
                    for p in state['freeList']:
                        if p[0] >= self.RIGHT_BOUND and p[0] < (self.WIDTH-1) and (p[0] == self.RIGHT_BOUND or (p[0]+1 != self.WIDTH-1 and (p[0]+1, p[1]) not in state['freeList']) or (p[0]-1, p[1]) not in state['freeList'] ):
                            yield i, p
            return func()
        return []

game = Game()
game.start()
            





                            
