# coding=gbk

from collections import Counter
import cbp_plan_utils as plu
import cbp_utils as cbpu
import net_gen as ng
import prepro_utils as ppu

# Exp 1.考虑隐私保护的面向计划的迫使-----------------------------------------------

# nets为参与组织        #
# 第i个参与组织         #


def plan_enforce(nets):

    # 1)获取第i个业务过程的私有执行路径~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    update_nets = []
    public_nets = []
    for i, net_i in enumerate(nets):
        insert_se_net_i = ppu.insert_start_end_trans(net_i, i)
        insert_and_net_i = ppu.insert_and_split_join(insert_se_net_i, i)
        # Note:需提前插入锚点,即在业务过程中插入
        insert_anchor_net_i = ppu.insert_anchors(insert_and_net_i, i)
        update_nets.append(insert_anchor_net_i)
        # insert_anchor_net_i.net_to_dot('public_net{}'.format(i), False)
        public_net_i = cbpu.gen_public_net(insert_anchor_net_i)
        # public_net_i.net_to_dot('public_net{}'.format(i), False)
        public_nets.append(public_net_i)

    # 2)获取公共过程的执行路径~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    exec_paths_set = []
    for public_net in public_nets:
        exec_paths = plu.get_exec_path_nets(public_net)
        exec_paths_set.append(exec_paths)

    # 3)构建计划~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    trans_in_exec_path_comp = plu.compute_trans_in_exec_path_comp(
        exec_paths_set)
    comp_net = cbpu.get_compose_net(public_nets)
    # comp_net.net_to_dot('comp_net', False)

    # 4)构建正确计划~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    correct_plans = []
    prohibit_back_trans = []
    plans = plu.gen_plans(comp_net, trans_in_exec_path_comp)
    for index, plan in enumerate(plans):
        result = cbpu.net_is_correct(plan)
        if result == 'Correct':
            if not cor_plan_exist(plan, correct_plans):
                # plan.net_to_dot('cor_plan{}'.format(index), False)
                correct_plans.append(plan)
        elif result == 'Partially Correct':
            cor_plan, rov_back_trans = plu.correct_plan(plan)
            if not cor_plan_exist(cor_plan, correct_plans):
                prohibit_back_trans = prohibit_back_trans + rov_back_trans
                # cor_plan.net_to_dot('cor_plan{}'.format(index))
                correct_plans.append(cor_plan)
            # plan.net_to_dot('plan{}'.format(index), False)

    # 5)产生重构过程~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ref_nets = []
    for i, net in enumerate(update_nets):
        # net.net_to_dot('net{}'.format(i), False)
        ref_net = plu.refactor(net, correct_plans, i, prohibit_back_trans)
        ref_net.print_infor()
        # print('inhibitor_arcs:', ref_net.inhibitor_arcs)
        ref_net.net_to_dot('ref_net{}'.format(i), False)
        ref_nets.append(ref_net)


def cor_plan_exist(cor_plan, correct_plans):
    for correct_plan in correct_plans:
        if Counter(cor_plan.trans) == Counter(correct_plan.trans):
            return True
    return False


# -------------------------------测试---------------------------------#

if __name__ == '__main__':

    # 'your_PNML_file_path' is the path of your PNML file
    nets = ng.gen_nets('your_PNML_file_path')
    plan_enforce(nets)
   

# -------------------------------------------------------------------#
