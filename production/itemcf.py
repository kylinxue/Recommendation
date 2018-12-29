# coding:utf-8
"""
item cf main Algo
"""
import math
import operator
import sys
from __future__ import division

sys.path.append("../util")
import util.reader as reader


def base_contribute_score():
    return 1


def cal_item_sim(user_click):
    """
    :param user_click:dick, key:userid, value:[itemid1,itemid2...]
    :return: dict, key:itemid_i, value:dict, value_key:itemid_j, value_value:simscore
    """
    co_appear = {}  # 用户贡献的
    item_user_click_time = {}  # item-i被多少个用户点击过，求相似度做分母
    for user, itemlist in user_click.items():
        for index_i in range(0, len(itemlist)):
            itemid_i = itemlist[index_i]
            item_user_click_time.setdefault(itemid_i, 0)
            item_user_click_time[itemid_i] += 1  # 用户对itemid_i的点击量
            for index_j in range(index_i + 1, len(itemlist)):
                itemid_j = itemlist[index_j]
                co_appear.setdefault(itemid_i, {})
                co_appear[itemid_i].setdefault(itemid_j, 0)
                # 如果是同一个用户，物品i和物品j对彼此的贡献加1
                co_appear[itemid_i][itemid_j] += base_contribute_score()

                co_appear.setdefault(itemid_j, {})
                co_appear[itemid_j].setdefault(itemid_i, 0)
                co_appear[itemid_j][itemid_i] += base_contribute_score()
    item_sim_score = {}
    item_sim_score_sorted = {}
    for itemid_i, relate_item in co_appear.items():
        for itemid_j, co_time in relate_item.items():
            sim_score = co_time / math.sqrt(item_user_click_time[itemid_i] * item_user_click_time[itemid_j])
            item_sim_score.setdefault(itemid_i, {})
            item_sim_score[itemid_i].setdefault(itemid_j, 0)
            item_sim_score[itemid_i][itemid_j] += sim_score
    for itemid in item_sim_score:
        item_sim_score_sorted[itemid] = sorted(item_sim_score[itemid].iteritems(),
                                               key=operator.itemgetter(1), reverse=True)
    return item_sim_score_sorted


def cal_recom_result(sim_info, user_click):
    """
    recommond result by itemcf
    :param sim_info: item sim dict
    :param user_click: user click dict
    :return: dict, key:userid, value:dict, value_key: itemid, value_value: recom_score
    """
    recent_click_num = 3
    topk = 5
    recom_info = {}
    for user in user_click:
        click_list = user_click[user]
        for itemid in click_list[:recent_click_num]:
            if itemid not in sim_info:
                continue
            for itemsimTuple in sim_info[itemid][:topk]:
                itemsimid = itemsimTuple[0]
                itemsimscore = itemsimTuple[1]
                # 根据用户最近点击的物品，将得分最靠前的相似物品推荐给用户user
                recom_info[user][itemsimid] = itemsimscore
    return recom_info


def main_flow():
    """
    main flow of itemcf
    1. 得到用户的点击序列
    2. 根据用户的点击序列得到item的相似度
    3. 根据用户点击序列和item的相似度信息得到推荐结果
    """
    user_click = reader.get_user_click("../data/ratings.txt")
    sim_info = cal_item_sim(user_click)
    recom_result = cal_recom_result(sim_info, user_click)
    print(recom_result["1"])


if __name__ == "__main__":
    main_flow()
