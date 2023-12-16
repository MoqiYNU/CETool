# coding=gbk
import circle_utils as cu
import inner_utils as iu
import net as nt
import net_gen as ng
from collections import Counter
import lts_utils as lu
import net_utils as nu
import inner_utils as inu
import reduce_utils as reu
'''
  ����Эͬҵ����̹�����,����Ӧ����������
  1. ��������˳��,ѡ��,�����͵����ṹ���;
  2. �����ṹֻ��Repeat-Until�ṹ;
  3. �������첽��;
  4. ���漰��Դ��ʱ����Ϣ.
'''


# 1.��Ͽ�����(ps:�첽���)----------------------------------------------
def get_compose_net(nets):
    if len(nets) == 0:
        print('no nets exist, exit...')
        return
    if len(nets) == 1:
        return nets[0]
    else:
        net = compose_two_nets(nets[0], nets[1])
        for i in range(2, len(nets)):
            net = compose_two_nets(net, nets[i])
        return net


# �������������
def compose_two_nets(net1: nt.OpenNet, net2: nt.OpenNet):

    # 1)����Դ����ֹ��ʶ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    source1, sinks1 = net1.get_start_ends()
    source2, sinks2 = net2.get_start_ends()

    # ps:�����ظ������Ϣ(��Ϣ���Գ�ʼ����)
    source_places = source1.get_infor()
    print(source1.get_infor())
    for place in source2.get_infor():
        if place in net1.msg_places:
            continue
        else:
            source_places.append(place)

    source = nt.Marking(source_places)
    sinks = []
    for sink1 in sinks1:
        for sink2 in sinks2:
            sink = nt.Marking(sink1.get_infor() + sink2.get_infor())
            sinks.append(sink)

    # 2)��������(�����ظ�)~~~~~~~~~~~~~~~~~~~~
    places1, inner_places1, msg_places1 = net1.get_places()
    places2, inner_places2, msg_places2 = net2.get_places()
    places = list(set(places1 + places2))
    inner_places = list(set(inner_places1 + inner_places2))
    msg_places = list(set(msg_places1 + msg_places2))

    # 3)������Ǩ(ps:���漰ͬ����Ǩ)~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    trans1, rout_trans1, tran_label_map1 = net1.get_trans()
    trans2, rout_trans2, tran_label_map2 = net2.get_trans()
    trans = []
    tran_label_map = {}

    for tran1 in trans1:
        trans.append(tran1)
        tran_label_map[tran1] = tran_label_map1[tran1]
    for tran2 in trans2:
        trans.append(tran2)
        tran_label_map[tran2] = tran_label_map2[tran2]

    # 4)��������ϵ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    flows1 = net1.get_flows()
    flows2 = net2.get_flows()
    flows = flows1 + flows2

    openNet = nt.OpenNet(source, sinks, places, trans, tran_label_map, flows)
    openNet.inner_places = inner_places
    openNet.msg_places = msg_places
    return openNet


# 2.�����ȹ̼��жϿ�����net�Ƿ�����ȷ��--------------------------------------
def net_is_correct(net):
    rrg = nu.gen_rg_with_subset(net)
    # ���㺬����Ϣ����ֹ��ʶ
    final_markings = []
    start, ends, states, trans = rrg.get_infor()
    for state in states:
        if is_final(state, ends, net.msg_places):
            final_markings.append(state)
    # Note:û�пɴ����ֹ��ʶ~~~~~~~~~
    if not final_markings:
        return 'Fully Incorrect'
    # ��lts�ϼ��
    rrg_to_lts, index_marking_map = rrg.rg_to_lts()
    final_indexs = []
    for final_marking in final_markings:
        for index, marking in index_marking_map.items():
            if nt.equal_markings(final_marking, marking):
                final_indexs.append(index)
                break
    lts_start, lts_ends, lts_states, lts_trans = rrg_to_lts.get_infor()
    valid_states = []
    # ����ÿ��״̬��Ǩ�Ʊհ�
    for state in lts_states:
        tran_closure = lu.gen_tran_closure(state, rrg_to_lts)
        # print('tran closure:', state, tran_closure)
        if set(tran_closure) & set(final_indexs):
            valid_states.append(state)
    if len(valid_states) == len(states):
        return 'Correct'
    if len(valid_states) == 0:
        return "Fully Incorrect"
    else:
        return 'Partially Correct'


# �ж�state�Ƿ�Ϊ��ֹ��ʶ(ps:��ֹ��ʶ�п��Ժ���ʣ����Ϣ)
def is_final(state, ends, msg_places):
    places = state.get_infor()
    # print('places', places)
    for end in ends:
        end_places = end.get_infor()
        cou = Counter(places)
        cou.subtract(Counter(end_places))
        # print('cou', cou)
        if valid(cou, msg_places):
            return True
    return False


def valid(cou, msg_places):
    vals = cou.values()
    for val in vals:
        if val < 0:
            return False
    for key, val in cou.items():
        if val > 0 and key not in msg_places:
            return False
    return True


# 3.����������--------------------------------------------------------
def gen_public_net(net: nt.OpenNet):

    inner_net = inu.get_inner_net(net)
    public_inner_net = reu.reduce_inner_net(inner_net, get_inter_trans(net))

    public_source = nt.Marking([public_inner_net.source])
    public_sinks = [nt.Marking([public_inner_net.sink])]

    public_trans = public_inner_net.trans
    msg_places = set()
    msg_flows = []
    for flow in net.flows:
        fl_from, fl_to = flow.get_infor()
        # print('flow', fl_from, fl_to)
        if fl_from in public_trans:  #fl_fromΪ��Ǩ
            if fl_to in net.msg_places:
                msg_places.add(fl_to)
                msg_flows.append(flow)
        elif fl_to in public_trans:  #fl_toΪ��Ǩ
            if fl_from in net.msg_places:
                msg_places.add(fl_from)
                msg_flows.append(flow)

    public_net = nt.OpenNet(public_source, public_sinks,
                            public_inner_net.places + list(msg_places),
                            public_trans, public_inner_net.label_map,
                            public_inner_net.flows + msg_flows)
    public_net.inner_places = public_inner_net.places
    public_net.msg_places = list(msg_places)
    return public_net


# ��ȡÿ��ҵ��������ڲ���Ǩ
def get_inter_trans(net: nt.OpenNet):
    inter_trans = []
    dfs_obj = cu.DFS()
    # ����ѭ����tb��Ǩ~~~~~~~~~~~~~~~~~~~~~~~~~~
    back_trans = []
    inner = iu.get_inner_net(net)
    source = inner.source
    to_graph = inner.to_graph()
    dfs_obj.dfs(source, to_graph)
    circles = dfs_obj.circles
    for circle in circles:
        back_trans.append(circle[-1])
    comm_trans = get_comm_trans(net)
    for tran in net.trans:
        # 5.1 �ų�ͨ�ű�Ǩ
        if tran in comm_trans:
            continue
        # 5.2�ų���ʼ/������Ǩ
        if tran.startswith('ti'):
            continue
        if tran.startswith('to'):
            continue
        # 5.3 �ų�ê��
        if tran.startswith('at'):
            continue
        # 5.4 �ų�and-split/join��Ǩ
        if tran.startswith('tas'):
            continue
        if tran.startswith('taj'):
            continue
        # 5.5 �ų�ѭ����tb��Ǩ
        if tran in back_trans:
            continue
        inter_trans.append(tran)
    return inter_trans


# ��ȡÿ��ҵ��������첽ͨ�ű�Ǩ
def get_comm_trans(net: nt.OpenNet):
    comm_trans = set()
    # �����Ϣ�����������첽��Ǩ
    for flow in net.flows:
        flow_from, flow_to = flow.get_infor()
        if flow_from in net.msg_places:
            comm_trans.add(flow_to)
        if flow_to in net.msg_places:
            comm_trans.add(flow_from)
    return list(comm_trans)


# -------------------------------����---------------------------------#

if __name__ == '__main__':

    # nets = ng.gen_nets('/Users/moqi/Desktop/��ʱ�ļ�/2023.xml')
    nets = ng.gen_nets('/Users/moqi/Desktop/��������/Motiving example.xml')
    from_net = get_compose_net(nets)
    from_net.net_to_dot('abc', False)
    from_net.print_infor()
    # result = net_is_correct(from_net)
    # print(result)

    # bottom_up_construction(nets, 1)

# -------------------------------------------------------------------#
