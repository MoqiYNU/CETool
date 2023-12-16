# coding=gbk
import copy
import circle_utils as cu
from inner import InnerNet
from inner_utils import get_inner_net
import net as nt
from net_gen import gen_nets
import prepro_utils as ppu
'''
  定义网约简工具类(Note:针对无选择结构实例网)
'''


# 1.约简内网中变迁(ps:无选择结构)-----------------------------------------------
def reduce_inner_net(inner_net: InnerNet, pending_reduce_trans):

    visiting_queue = [inner_net]  # 运行队列
    while visiting_queue:
        # 出对一个内网,以其深拷贝进行迁移
        from_net = copy.deepcopy(visiting_queue.pop(0))
        # from_net.net_to_dot('from_ep_net')
        # Note:每次约简前须对并发块中冗余库所进行调整,否则约简会出错
        from_net = adjust_redu_places(from_net, pending_reduce_trans)
        # ps:确定现在还需要约简变迁集
        cur_reduce_trans = list(
            set(from_net.trans).intersection(pending_reduce_trans))
        # print('internal_trans:', internal_trans)
        # 若没有待约简变迁则直接返回,表示是最简
        if not cur_reduce_trans:
            # from_net.inner_to_dot('from')
            return from_net
        try:

            # Note:确定约简变迁,优先级:AND>LOOP>SEQ
            block, type = deter_reduce_block(cur_reduce_trans, from_net)
            print('test:', block, type)
            if type == 'AND':
                print('reduce AND..................', block,
                      from_net.label_map[block])
                reduce_net = reduce_one_and_tran(block, from_net)
                # reduce_net.net_to_dot('reduce_net_AND')
                visiting_queue.append(reduce_net)
                raise Exception()
            if type == 'LOOP':
                print('reduce LOOP..................', block[1],
                      from_net.label_map[block[1]])
                reduce_net = reduce_one_inter_tran(block, from_net)
                visiting_queue.append(reduce_net)
                raise Exception()
            if type == 'SEQ':
                print('reduce SEQ..................', block,
                      from_net.label_map[block])
                reduce_net = reduce_one_seq_tran(block, from_net)
                # reduce_net.inner_to_dot('reduce_net_SEQ')
                visiting_queue.append(reduce_net)
                raise Exception()

        except Exception:
            continue


# 每次约简前需对并发块中冗余库所进行调整,否则约简会出错
# 即:split->place->join==>split->place->redu_t->redu_place->join
def adjust_redu_places(from_net: InnerNet, pending_reduce_trans):
    places = from_net.places
    flows = from_net.flows
    for place in places:
        preset = nt.get_preset(flows, place)
        postset = nt.get_postset(flows, place)
        if len(preset) == 1 and len(postset) == 1:
            from_tran = preset[0]
            to_tran = postset[0]
            if len(nt.get_postset(flows, from_tran)) > 1 and len(
                    nt.get_preset(flows, to_tran)) > 1:
                redu_tran = '{}_t'.format(place)
                redu_place = '{}_p'.format(place)
                # 添加库所及变迁到net中
                from_net.add_places([redu_place])
                from_net.add_trans([redu_tran])
                from_net.label_map[redu_tran] = redu_tran
                pending_reduce_trans.append(redu_tran)
                # 更新流关系
                from_net.rov_flow(place, to_tran)
                from_net.add_flow(place, redu_tran)
                from_net.add_flow(redu_tran, redu_place)
                from_net.add_flow(redu_place, to_tran)
    return from_net


# Note:确定约简变迁,优先级:AND>LOOP>SEQ
def deter_reduce_block(internal_trans, from_net: InnerNet):

    for internal_tran in internal_trans:
        block, type = get_reduce_block(internal_tran, from_net)
        if type == 'AND':
            return block, type
        else:
            continue
    for internal_tran in internal_trans:
        block, type = get_reduce_block(internal_tran, from_net)
        if type == 'LOOP':
            return block, type
        else:
            continue
    for internal_tran in internal_trans:
        block, type = get_reduce_block(internal_tran, from_net)
        if type == 'SEQ':
            return block, type


# 获取一个约简的块
def get_reduce_block(tran, from_net: InnerNet):
    tran_preset = nt.get_preset(from_net.flows, tran)
    pe = tran_preset[0]
    tran_postset = nt.get_postset(from_net.flows, tran)
    px = tran_postset[0]

    pe_preset = nt.get_preset(from_net.flows, pe)
    pe_postset = nt.get_postset(from_net.flows, pe)
    te = pe_preset[0]
    px_preset = nt.get_preset(from_net.flows, px)
    px_postset = nt.get_postset(from_net.flows, px)
    tx = px_postset[0]
    te_postset = set(nt.get_postset(from_net.flows,
                                    te)).intersection(from_net.places)
    tx_preset = set(nt.get_preset(from_net.flows,
                                  tx)).intersection(from_net.places)
    print('test:', tran, pe, px)
    # tran是一个元并发结构
    if len(tran_preset) == 1 and len(tran_postset) == 1 and len(
            pe_preset
    ) == 1 and len(pe_postset) == 1 and len(px_preset) == 1 and len(
            px_postset) == 1 and len(te_postset) > 1 and len(tx_preset) > 1:
        return tran, 'AND'

    # tran是一个元迭代结构
    dfs_obj = cu.DFS()
    source = from_net.source
    to_graph = from_net.to_graph()
    dfs_obj.dfs(source, to_graph)
    circles = dfs_obj.circles
    for circle in circles:
        # 元循环<p,t,p',tb>
        if len(circle) == 4 and circle[1] == tran:
            return circle, 'LOOP'

    # tran是一个元顺序结构(Note:优先级最低)
    if len(tran_preset) == 1 and len(tran_postset) == 1:
        return tran, 'SEQ'


# 约简一个元并发变迁
def reduce_one_and_tran(tran, from_net: InnerNet):
    pe = nt.get_preset(from_net.flows, tran)[0]
    te = nt.get_preset(from_net.flows, pe)[0]
    pte = nt.get_preset(from_net.flows, te)[0]
    px = nt.get_postset(from_net.flows, tran)[0]
    tx = nt.get_postset(from_net.flows, px)[0]
    ptx = nt.get_postset(from_net.flows, tx)[0]
    te_postset = nt.get_postset(from_net.flows, te)
    tx_preset = nt.get_preset(from_net.flows, tx)
    if len(te_postset) == 2 and len(tx_preset) == 2:
        pe1 = list(set(te_postset) - set([pe]))[0]
        pe1_preset = list(set(nt.get_preset(from_net.flows, pe1)) - set([te]))
        pe1_postset = nt.get_postset(from_net.flows, pe1)
        px1 = list(set(tx_preset) - set([px]))[0]
        ptx_preset = list(set(nt.get_preset(from_net.flows, ptx)) - set([tx]))
        ptx_postset = nt.get_postset(from_net.flows, ptx)
        rov_places = [pe, pe1, px, ptx]
        print('rov_places:', rov_places)
        from_net.rov_places(rov_places)
        from_net.rov_trans([tran, te, tx])
        for key in [tran, te, tx]:
            from_net.label_map.pop(key)
        from_net.rov_flow(pte, te)
        from_net.rov_flow(te, pe)
        from_net.rov_flow(pe, tran)
        from_net.rov_flow(tran, px)
        from_net.rov_flow(px, tx)
        from_net.rov_flow(te, pe1)
        from_net.rov_flow(px1, tx)
        from_net.rov_flow(tx, ptx)
        for tran in pe1_preset:
            # Note:移除已有的流
            from_net.rov_flow(tran, pe1)
            from_net.add_flow(tran, pte)
        for tran in pe1_postset:
            # Note:移除已有的流
            from_net.rov_flow(pe1, tran)
            from_net.add_flow(pte, tran)
        for tran in ptx_preset:
            # Note:移除已有的流
            from_net.rov_flow(tran, ptx)
            from_net.add_flow(tran, px1)
        for tran in ptx_postset:
            # Note:移除已有的流
            from_net.rov_flow(ptx, tran)
            from_net.add_flow(px1, tran)
        # print('test.....................')
        # ep_net.net_to_dot('reduce_ep_net')
        return from_net
    # elif len(te_postset) > 2 and len(tx_preset) > 2:
    else:
        from_net.rov_places([pe, px])
        from_net.rov_trans([tran])
        for key in [tran]:
            from_net.label_map.pop(key)
        from_net.rov_flow(te, pe)
        from_net.rov_flow(pe, tran)
        from_net.rov_flow(tran, px)
        from_net.rov_flow(px, tx)
        print('places:', from_net.places)
        return from_net


# 约简一个元迭代变迁
def reduce_one_inter_tran(circle, from_net: InnerNet):
    pe = circle[0]
    tran = circle[1]
    px = circle[2]
    tb = circle[3]
    px_preset = list(set(nt.get_preset(from_net.flows, px)) - set([tran]))
    px_postset = list(set(nt.get_postset(from_net.flows, px)) - set([tb]))
    from_net.rov_places([px])
    from_net.rov_trans([tran, tb])
    for key in [tran, tb]:
        from_net.label_map.pop(key)
    from_net.rov_flow(pe, tran)
    from_net.rov_flow(tran, px)
    from_net.rov_flow(px, tb)
    from_net.rov_flow(tb, pe)
    for tran in px_preset:
        # Note:移除已有的流
        from_net.rov_flow(tran, px)
        from_net.add_flow(tran, pe)
    for tran in px_postset:
        # Note:移除已有的流
        from_net.rov_flow(px, tran)
        from_net.add_flow(pe, tran)
    return from_net


# 约简一个元顺序变迁
def reduce_one_seq_tran(tran, from_net: InnerNet):
    pe = nt.get_preset(from_net.flows, tran)[0]
    px = nt.get_postset(from_net.flows, tran)[0]
    px_preset = list(set(nt.get_preset(from_net.flows, px)) - set([tran]))
    px_postset = nt.get_postset(from_net.flows, px)
    from_net.rov_places([px])
    from_net.rov_trans([tran])
    for key in [tran]:
        from_net.label_map.pop(key)
    from_net.rov_flow(pe, tran)
    from_net.rov_flow(tran, px)
    for tran in px_preset:
        # Note:移除已有的流
        from_net.rov_flow(tran, px)
        from_net.add_flow(tran, pe)
    for tran in px_postset:
        # Note:移除已有的流
        print('rov flow:', px, tran)
        from_net.rov_flow(px, tran)
        from_net.add_flow(pe, tran)
    print([flow.get_infor() for flow in from_net.flows])
    # from_net.inner_to_dot('abc1')
    return from_net



