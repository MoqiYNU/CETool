# coding=gbk
import copy
import inner_utils as iu
import net as nt
import circle_utils as cu
import cbp_utils as cbpu
from collections import Counter


# 1.获取一个网中执行路径-----------------------------------------------
def get_exec_path_nets(net: nt.OpenNet):
    inner = iu.get_inner_net(net)
    inner_exec_paths = iu.decompose_inner_net(inner)
    exec_paths = []
    for inner_exec_path in inner_exec_paths:
        # 1.初始和终止标识
        init_marking = nt.Marking([inner_exec_path.source])
        final_marking = nt.Marking([inner_exec_path.sink])
        # 2.变迁集
        trans = inner_exec_path.trans
        ep_label_map = {}
        for tran in trans:
            ep_label_map[tran] = net.label_map[tran]
        # 3.流关系
        ep_flows = []
        for flow in net.flows:
            flow_from, flow_to = flow.get_infor()
            if flow_from in trans or flow_to in trans:
                ep_flows.append(flow)
        # 4.库所集(内部/消息库所,Note:避免重复!!!)
        ep_places = set()
        ep_inner_places = set()
        ep_msg_places = set()
        for flow in ep_flows:
            flow_from, flow_to = flow.get_infor()
            if flow_from in net.places:
                ep_places.add(flow_from)
                if flow_from in net.msg_places:
                    ep_msg_places.add(flow_from)
                else:
                    ep_inner_places.add(flow_from)
            if flow_to in net.places:
                ep_places.add(flow_to)
                if flow_to in net.msg_places:
                    ep_msg_places.add(flow_to)
                else:
                    ep_inner_places.add(flow_to)
        exec_path = nt.OpenNet(init_marking, [final_marking], list(ep_places),
                               trans, ep_label_map, ep_flows)
        exec_path.inner_places = list(ep_inner_places)
        exec_path.msg_places = list(ep_msg_places)
        exec_paths.append(exec_path)
    return exec_paths


# 2.计算执行路径组合中变迁集----------------------------------------------
def compute_trans_in_exec_path_comp(exec_paths_set):
    index_array = []
    for exec_paths in exec_paths_set:
        index_array.append(range(len(exec_paths)))
    prod = product(index_array)
    # 存储多条执行路径组合中的变迁集
    trans_in_exec_path_comp = []
    # exec_path_comp_set = []
    for elem in prod:
        # Note:index是字符串
        indexs = elem.split(' ')
        trans = []
        # exec_path_comp = []
        for i in range(len(indexs)):
            exec_path = exec_paths_set[i][int(indexs[i])]
            trans = trans + exec_path.trans
            # exec_path_comp.append(exec_path)
        trans_in_exec_path_comp.append(trans)
        # exec_path_comp_set.append(exec_path_comp)
    return trans_in_exec_path_comp


# 判断执行路径组合中变迁是否生成过
def exist_trans(trans_in_exec_path_comp, trans):
    for temp_trans in trans_in_exec_path_comp:
        if Counter(temp_trans) == Counter(trans):
            return True
        else:
            return False


# 计算多个集合的笛卡尔积
def product(list_of_list):
    list1 = list_of_list[0]
    for tmp_list in list_of_list[1:]:
        list2 = tmp_list
        two_res_list = two(list1, list2)
        list1 = two_res_list
    return list1


def two(list1, list2):
    res_list = []
    for int1 in list1:
        for int2 in list2:
            res_list.append(str(int1) + ' ' + str(int2))
    return res_list


# 3.由执行路径组合中变迁集确定在组合网中投影(即计划)------------------------
def gen_plans(comp_net: nt.OpenNet, trans_in_exec_path_comp):

    plans = []  # 返回计划集
    for trans in trans_in_exec_path_comp:

        # 1.确定映射在组合网中的变迁集~~~~~~~~~~~~~~~~~~~~~~~~~~~
        proj_trans = []
        for tran in comp_net.trans:
            if tran in trans:
                proj_trans.append(tran)

        proj_label_map = {}
        for id, label in comp_net.label_map.items():
            if id in proj_trans:
                proj_label_map[id] = label

        # 2.确定流和内部/消息库所~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        proj_places = set()
        proj_inner_places = set()
        proj_msg_places = set()
        proj_flows = []
        flows = comp_net.get_flows()
        for flow in flows:
            fl_from, fl_to = flow.get_infor()
            if fl_from in proj_trans:  #fl_from为变迁
                proj_places.add(fl_to)
                if fl_to in comp_net.inner_places:
                    proj_inner_places.add(fl_to)
                if fl_to in comp_net.msg_places:
                    proj_msg_places.add(fl_to)
                proj_flows.append(flow)
            elif fl_to in proj_trans:  #fl_to为变迁
                proj_places.add(fl_from)
                if fl_from in comp_net.inner_places:
                    proj_inner_places.add(fl_from)
                if fl_from in comp_net.msg_places:
                    proj_msg_places.add(fl_from)
                proj_flows.append(flow)

        # 构建由投影生成的网
        plan = nt.OpenNet(comp_net.source, comp_net.sinks, list(proj_places),
                          proj_trans, proj_label_map, proj_flows)
        plan.inner_places = list(proj_inner_places)
        plan.msg_places = list(proj_msg_places)
        # print('plan net========================================')
        # plan.print_infor()

        plans.append(plan)

    return plans


# 4.纠正计划-------------------------------------------------------------
def correct_plan(plan: nt.OpenNet):
    # 1)获取导致部分正确性的back变迁
    rov_back_trans = []
    inner = iu.get_inner_net(plan)
    source = inner.source
    to_graph = inner.to_graph()
    dfs_obj = cu.DFS()
    dfs_obj.dfs(source, to_graph)
    circles = dfs_obj.circles
    comm_trans = cbpu.get_comm_trans(plan)
    for circle in circles:
        if set(comm_trans) & set(circle):
            rov_back_trans.append(circle[-1])
    # 2)移除导致部分正确性的back变迁及关联流
    cor_plan = copy.deepcopy(plan)
    rov_flows = []
    for flow in plan.flows:
        flow_from, flow_to = flow.get_infor()
        if flow_from in rov_back_trans or flow_to in rov_back_trans:
            rov_flows.append(flow)
    cor_plan.rov_trans(rov_back_trans)
    cor_plan.rov_flows(rov_flows)
    return cor_plan, rov_back_trans


# 5.参与组织根据计划对其业务过程进行重构
def refactor(net: nt.OpenNet, correct_plans, i, prohibit_back_trans):
    ref_net = rov_prohibit_back_trans(net, prohibit_back_trans)
    ref_net = gen_plan_strategy(ref_net, correct_plans)
    # ref_net.net_to_dot('ref_net{}'.format(i))
    return ref_net


# 5.1.移除导致部分正确的back变迁---------------------------------------------
def rov_prohibit_back_trans(net: nt.OpenNet, prohibit_back_trans):

    trans = []
    tran_label_map = {}
    for tran in net.trans:
        if tran not in prohibit_back_trans:
            trans.append(tran)
            tran_label_map[tran] = net.label_map[tran]

    places = []
    inner_places = []
    msg_places = []
    flows = []
    for flow in net.flows:
        flow_from, flow_to = flow.get_infor()
        if flow_from in trans:
            places.append(flow_to)
            if flow_to in net.inner_places:
                inner_places.append(flow_to)
            if flow_to in net.msg_places:
                msg_places.append(flow_to)
            flows.append(flow)
        if flow_to in trans:
            places.append(flow_from)
            if flow_from in net.inner_places:
                inner_places.append(flow_from)
            if flow_from in net.msg_places:
                msg_places.append(flow_from)
            flows.append(flow)

    ref_net = nt.OpenNet(net.source, net.sinks, places, trans, tran_label_map,
                         flows)
    ref_net.inner_places = inner_places
    ref_net.msg_places = msg_places
    return ref_net


# 5.2.构建面向计划策略-----------------------------------------------------
def gen_plan_strategy(net: nt.OpenNet, correct_plans):

    ref_net = copy.deepcopy(net)
    plan_idfs = range(len(correct_plans))

    # 1.将每个锚点映射为面向计划的策略~~~~~~~~~~~~~~~~~~~~~~~~~~
    anchors = []
    for tran in net.trans:
        if tran.startswith('at'):
            anchors.append(tran)

    for anchor in anchors:

        associate_plans = get_associate_plans(anchor, correct_plans)
        print('plan test..........................', anchor, associate_plans)
        # 若关联计划为空,则通过库所pun禁止其执行
        if not associate_plans:
            ref_net.add_places(['pun'])
            ref_net.add_msg_places(['pun'])
            ref_net.add_flows([nt.Flow('pun', anchor)])
            continue

        start = nt.get_preset(net.flows, anchor)[0]
        end = nt.get_postset(net.flows, anchor)[0]

        ref_net.add_places(['pcs'])
        ref_net.add_msg_places(['pcs'])
        ref_net.source.places = ref_net.source.places + ['pcs']
        for k in plan_idfs:
            pcl = 'pc{}'.format(k)
            ref_net.add_places([pcl])
            ref_net.add_msg_places([pcl])
            ref_net.source.places = ref_net.source.places + [pcl]

        # 关联的正确计划
        for associate_plan in associate_plans:
            et = 'e{}{}'.format(anchor, associate_plan)
            ref_net.add_trans([et])
            ref_net.label_map[et] = et
            ref_net.add_flows(
                [nt.Flow(start, et),
                 nt.Flow(et, 'p{}{}'.format(anchor, 0))])
            ref_net.add_flows([
                nt.Flow('pc{}'.format(associate_plan), et),
                nt.Flow(et, 'pc{}'.format(associate_plan))
            ])
            ref_net.add_flows([nt.Flow('pcs', et)])

        # 未关联的正确计划
        unassociate_plans = list(set(plan_idfs) - set(associate_plans))
        for index in range(len(unassociate_plans)):
            pt = 'p{}{}'.format(anchor, index)
            ref_net.add_places([pt])
            ref_net.add_inner_places([pt])
        for index in range(len(unassociate_plans)):
            unassociate_plan = unassociate_plans[index]
            if index == len(unassociate_plans) - 1:
                pre_place = 'p{}{}'.format(anchor, index)
                rt = 'r{}{}'.format(anchor, unassociate_plan)
                print('rt:', rt)
                ref_net.add_trans([rt])
                ref_net.label_map[rt] = rt
                st = 's{}{}'.format(anchor, unassociate_plan)
                ref_net.add_trans([st])
                ref_net.label_map[st] = st
                ref_net.add_flows([nt.Flow(pre_place, rt), nt.Flow(rt, end)])
                ref_net.add_flows([nt.Flow(pre_place, st), nt.Flow(st, end)])
                ref_net.add_flows(
                    [nt.Flow('pc{}'.format(unassociate_plan), rt)])
                ref_net.inhibitor_arcs.append(
                    ['pc{}'.format(unassociate_plan), st])
                ref_net.add_flows([nt.Flow(rt, 'pcs')])
                ref_net.add_flows([nt.Flow(st, 'pcs')])
            else:
                pre_place = 'p{}{}'.format(anchor, index)
                post_place = 'p{}{}'.format(anchor, index + 1)
                rt = 'r{}{}'.format(anchor, unassociate_plan)
                ref_net.add_trans([rt])
                ref_net.label_map[rt] = rt
                st = 's{}{}'.format(anchor, unassociate_plan)
                ref_net.add_trans([st])
                ref_net.label_map[st] = st
                ref_net.add_flows(
                    [nt.Flow(pre_place, rt),
                     nt.Flow(rt, post_place)])
                ref_net.add_flows(
                    [nt.Flow(pre_place, st),
                     nt.Flow(st, post_place)])
                ref_net.add_flows(
                    [nt.Flow('pc{}'.format(unassociate_plan), rt)])
                ref_net.inhibitor_arcs.append(
                    ['pc{}'.format(unassociate_plan), st])

        # 2.移除锚点及其连接的流~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ref_net.rov_trans([anchor])
        for key in [anchor]:
            ref_net.label_map.pop(key)
        ref_net.rov_flow(start, anchor)
        ref_net.rov_flow(anchor, end)

    print('inhibitor_arcs:', ref_net.inhibitor_arcs)
    # ref_net.print_infor()
    return ref_net


# 获取关联计划标识集
def get_associate_plans(anchor, correct_plans):
    associate_plans = []
    for index, correct_plan in enumerate(correct_plans):
        if anchor in correct_plan.trans:
            associate_plans.append(index)
    return associate_plans
