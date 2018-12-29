# coding:utf-8
import math
import operator
import sys
sys.path.append("../util")
import util.reader as reader


def transfer_user_click(user_click):
    """
    将用户点击列表转换为物品的倒排索引 {key: item, value:[user1, user2 ...]}
    :param user_click: {key:user, value: [item1, item2 ...]
    :return: dict: {key: item, value:[user1, user2 ...]}
    """
    item_click_by_user = {}
    for user in user_click:
        item_list = user_click[user]
        for itemid in item_list:
            item_click_by_user.setdefault(itemid, [])
            item_click_by_user[itemid].append(user)
    return item_click_by_user


def base_contribution_score():
    return 1


def cal_user_sim(item_click_by_user):
    """
    :param item_click_by_user: {key: itemid, value: [user1, user2 ...]}
    :return: dict:{key:userid_i, value:{key:userid_j, value: simscore}}
        类似于user_sim[user_i][user_j]
    """
    co_appear = {}
    user_click_time = {}
    for itemid, user_list in item_click_by_user.items():
        for i in range(0, len(user_list)):
            user_i = user_list[i]
            user_click_time.setdefault(user_i, 0)
            user_click_time[user_i] += 1
            for j in range(0, len(user_list)):
                user_j = user_list[j]
                co_appear.setdefault(user_i, {})
                co_appear[user_i].setdefault(user_j, 0)
                co_appear[user_i][user_j] += base_contribution_score()

                co_appear.setdefault(user_j, {})
                co_appear[user_j].setdefault(user_i, 0)
                co_appear[user_j][user_i] += base_contribution_score()
    user_sim_info = {}
    for user_i, relate_user in co_appear.items():
        user_sim_info.setdefault(user_i, {})
        for user_j, cotime in relate_user.items():
            user_sim_info[user_i].setdefault(user_j, 0)
            user_sim_info[user_i][user_j] = cotime / math.sqrt(user_click_time[user_i]*user_click_time[user_j])
    user_sim_sorted = {}
    # 对每一个user对应的user集合按照cotime进行排序，为了后面给每个user选出topK个相似用户
    for user_i in user_sim_info:
        user_sim_sorted = sorted(user_sim_info[user_i].iteritems(),
                                 key=operator.itemgetter(1), reverse=True)
    return user_sim_sorted


def cal_recom_result(user_click, user_sim):
    """
    get recommodation result to every user in user_click dict
    :param user_click: {key: userid, value:[item1,item2 ...]
    :param user_sim:
    :return: dict:{{user1:[itemid1 ...]}...}
    """
    recom_result = {}
    topK_user = 3
    item_num = 5
    for user, item_list in user_click:
        item_dict = {}  #此处没有用到当前用户的浏览物品表，应当把这些从推荐结果中去掉，因为用户刚浏览过
        for itemid in item_list:
            item_dict.setdefault(itemid, 1)
        recom_result.setdefault(user, {})
        for tupleElement in user_sim[user][:topK_user]:
            userid_j, sim_score = tupleElement
            if userid_j not in user_click:
                continue
            # 将userid_j的点击物品推荐给当前user
            for itemid_j in user_click[userid_j][:item_num]:
                recom_result[user].setdefault(itemid_j, sim_score)
    return recom_result


def main_flow():
    user_click = reader.get_user_click("../data/ratings.txt")
    item_click_by_user = transfer_user_click(user_click)
    user_sim = cal_user_sim(item_click_by_user)
    # 通过用户点击和用户相似度矩阵得到推荐结果
    recom_result = cal_recom_result(user_click, user_sim)


if __name__ == '__main__':
    main_flow()