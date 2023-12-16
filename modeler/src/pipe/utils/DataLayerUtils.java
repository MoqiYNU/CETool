package pipe.utils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

import org.apache.commons.collections4.CollectionUtils;

import pipe.dataLayer.AnnotationNote;
import pipe.dataLayer.Arc;
import pipe.dataLayer.DataLayer;
import pipe.dataLayer.Place;
import pipe.dataLayer.Transition;
import toolkits.def.petri.Flow;
import toolkits.def.petri.Marking;
import toolkits.def.petri.ProNet;
import toolkits.utils.petri.PetriUtils;

/**
 * @author Moqi
 * Pipe�����ݲ�Utils
 */
public class DataLayerUtils {
	
	
	/*************************��dataLayer�в������������*************************/
	
	public List<ProNet> genProNetsFromDL(DataLayer dataLayer) {

		//���ջ�ÿ�����(����м���,����������Ϣ������label���)
		List<ProNet> openNets = new ArrayList<ProNet>();

		//�洢�зֵõ��м���
		List<ProNet> interOpenNets = new ArrayList<ProNet>();

		//��ȡDataLayer�е��������
		Place[] places = dataLayer.getPlaces();
		Marking initMarking = dataLayer.createInitMarking();
		List<String> initPlaces = initMarking.getPlaces();
		Transition[] transitions = dataLayer.getTransitions();
//		List<String> ctrlTrans = dataLayer.getCtrlTrans();//���Ʊ�Ǩ��
		Arc[] arcs = dataLayer.getArcs();
	    List<String> msgPlaces = dataLayer.getMsgPlaces();//��Id��ʶ
	    List<String> resPlaces = dataLayer.getResPlaces();//��Id��ʶ
//	    List<String> linkPlaces = dataLayer.getLinkPlaces();//��Id��ʶ
	    //System.out.println("msgPlaces: " + msgPlaces);
	    AnnotationNote[] annotationNotes = dataLayer.getLabels();
	    
	    // 1.���������ֹ��ʶ
	    List<Marking> sinks = new ArrayList<Marking>();
        for (AnnotationNote annotationNote : annotationNotes) {
			if (annotationNote.isFinalMarkingNote()) {
				String marksStr = annotationNote.getText();
				sinks.addAll(parseMarkSet(marksStr));
			}
		}
	    
	    // 2.����ÿ����Ǩ��ȡ������Ƭ��,���Դ˹����м���(�м俪������ֻ������,��Ǩ����)
	    List<String> visitedTrans = new ArrayList<>();
	    for (Transition tran : transitions) {
	    	
	    	String tranId = tran.getId();
	    	
	    	if (visitedTrans.contains(tranId)) {//�����ɹ�,������
				continue;
			}
	    	
	    	//�����ɿ�����
	    	ProNet interOpenNet = new ProNet();
	    	Bag bag = getBag(arcs, tranId);
	    	List<String> tranIdsInBag = bag.getTrans();
	    	
	    	// 2.1ȷ����Ǩ
	    	for (String tranIdInBag : tranIdsInBag) {
	    		interOpenNet.addTran(tranIdInBag);
	    	}
	    	
	    	// 2.2ȷ������
	    	List<String> tempPlaces = new ArrayList<String>();
	    	for (String tranIdInBag : tranIdsInBag) {
		    	List<String> preSet = getPreSet(arcs, tranIdInBag);
		    	for (String place : preSet) {
					if (!tempPlaces.contains(place)) {
						tempPlaces.add(place);
					}
				}
		    	List<String> postSet = getPostSet(arcs, tranIdInBag);
		    	for (String place : postSet) {
		    		if (!tempPlaces.contains(place)) {
						tempPlaces.add(place);
					}
				}
			}
	    	interOpenNet.addPlaces(tempPlaces);
	    	
	    	// 2.3ȷ������ϵ
	    	for (String tranIdInBag : tranIdsInBag) {
		    	interOpenNet.addFlows(getFlowsByTran(arcs, tranIdInBag));
	    	}
			interOpenNets.add(interOpenNet);
			
			//��tranIdsInBag�ѱ�����
			visitedTrans.addAll(tranIdsInBag);
			//System.out.println("PN size: " + petris.size() + " Visiting tran: " + tranId + " Bag: " + tranIdsInBag);
	    }
	    
	    // 3.���ÿ���м���,����������
        for (ProNet interOpenNet : interOpenNets) {

			//��ȡ�м����п���,��Ǩ������ϵ
        	List<String> interPlaces = interOpenNet.getPlaces();
        	List<String> interTrans = interOpenNet.getTrans();
        	List<Flow> interFlows = interOpenNet.getFlows();

			//������Petri��
			ProNet openNet = new ProNet();

			//������Դ������:��Name��ʶ(�蹲��)�ұ����ظ�
            List<String> rPlaces = new ArrayList<String>();
			for (String rPace : resPlaces) {
				if (interPlaces.contains(rPace)) {
					rPlaces.add(rPace);
				}
			}
			for (String rPlace : rPlaces) {
				openNet.addResPlace(getPlaceLabel(places, rPlace));
			}

			//����Դ��������Դ
			List<String> tempPlaces = new ArrayList<String>();
			for (String initPlace : initPlaces) {
				if (interPlaces.contains(initPlace)) {
					tempPlaces.add(initPlace);
				}
			}
			//Note:sourcePlaces������Դ����
			List<String> sourcePlaces = new ArrayList<String>();
			List<String> resources = new ArrayList<String>();
			for (String tempPlace : tempPlaces) {
				if (rPlaces.contains(tempPlace)) {
					//������Դ,����Դ������Name
					resources.add(getPlaceLabel(places, tempPlace));
				}else {
					sourcePlaces.add(tempPlace);
				}
			}
			
			Marking source = new Marking();
			//Դ�����в�����Դ����
			source.addPlaces(sourcePlaces);
			openNet.setSource(source);
			openNet.setResources(resources);

			//������Ϣ����(��Name��ʶ,�ұ����ظ�)
			List<String> mPlaces = new ArrayList<String>();
			
			for (String mPlace : msgPlaces) {
				if (interPlaces.contains(mPlace)) {
					mPlaces.add(mPlace);
				}
			}
            for (String mPlace : mPlaces) {
				openNet.addMsgPlace(getPlaceLabel(places, mPlace));
			}
            
            //�������ӿ���(��Id��ʶ,�ұ����ظ�)
//            List<String> lPlaces = new ArrayList<String>();
//            for (String lPlace : linkPlaces) {
//				if (interPlaces.contains(lPlace)) {
//					lPlaces.add(lPlace);
//				}
//			}
//            for (String lPlace : lPlaces) {
//				openNet.addLinkPlace(lPlace);
//			}

			//����Places
            for (String interPlace : interPlaces) {
				if (mPlaces.contains(interPlace)) {
					openNet.addPlace(getPlaceLabel(places, interPlace));
				}else if (rPlaces.contains(interPlace)) {
					openNet.addPlace(getPlaceLabel(places, interPlace));
				}else{
					openNet.addPlace(interPlace);
				}
			}

			//������ֹ��ʶ��
			List<Marking> fMarkings = new ArrayList<Marking>();
			for (Marking sink : sinks) {
				if (interPlaces.containsAll(sink.getPlaces())) {
					fMarkings.add(sink);
				}
			}
			openNet.setSinks(fMarkings);

			//���û�����ƻ
			List<String> trans = interOpenNet.getTrans();
			openNet.setTrans(trans);
//			for (String tran : trans) {
//				if (ctrlTrans.contains(tran)) {
//					openNet.addCtrlTran(tran);
//				}
//			}
			
			//����Flow
			for (Flow flow : interFlows) {
		    	   String flowFrom = flow.getFlowFrom();
		    	   String flowTo = flow.getFlowTo();
		    	   if (mPlaces.contains(flowFrom)) {
				       Flow fFlow = new Flow();
				       fFlow.setFlowFrom(getPlaceLabel(places, flowFrom)); 
				       fFlow.setFlowTo(flowTo);
				       openNet.addFlow(fFlow);
				   }else if (mPlaces.contains(flowTo)) {
					   Flow fFlow = new Flow();
				       fFlow.setFlowFrom(flowFrom); 
				       fFlow.setFlowTo(getPlaceLabel(places, flowTo));
				       openNet.addFlow(fFlow);
				   }else if (rPlaces.contains(flowFrom)) {
					   Flow rFlow = new Flow();
				       rFlow.setFlowFrom(getPlaceLabel(places, flowFrom)); 
				       rFlow.setFlowTo(flowTo);
				       openNet.addFlow(rFlow);
				   }else if (rPlaces.contains(flowTo)) {
					   Flow rFlow = new Flow();
				       rFlow.setFlowFrom(flowFrom); 
				       rFlow.setFlowTo(getPlaceLabel(places, flowTo));
				       openNet.addFlow(rFlow);
				   }else{
					   openNet.addFlow(flow);
				   }
			}

			//��������������Ϣ������
			List<String> msgPls = openNet.getMsgPlaces();
			for (String msgPl : msgPls) {
				List<String> preSet = PetriUtils.getPreSet(msgPl, openNet.getFlows());
				if (preSet.size() == 0) {//1.ǰ��Ϊ��,��Ϊ������Ϣ����
					openNet.addInputMsgPlace(msgPl);
				}else {//2.ǰ����Ϊ��,��Ϊ�����Ϣ����
					openNet.addOutputMsgPlace(msgPl);
				}
			}

			//����������Դ��Ǩ������Դ����ӳ��
			Map<String, List<String>> reqResMap = new HashMap<String, List<String>>();
			Map<String, Integer> resProperMap = new HashMap<String, Integer>();
			List<String> resPls = openNet.getResPlaces();
			for (String resPl : resPls) {
				List<String> preSet = PetriUtils.getPreSet(resPl, openNet.getFlows());
				List<String> postSet = PetriUtils.getPostSet(resPl, openNet.getFlows());
				if (postSet.size() != 0) {//������Դ��Ǩ��
					reqResMap.put(resPl, postSet);
				}
				if (preSet.size() != 0 && postSet.size() != 0) {//1.ǰ�󼯾���Ϊ��,��Ϊ�ظ�������Դ
					resProperMap.put(resPl, 0);
				}else {//2.����Ϊ������Դ
					resProperMap.put(resPl, 1);
				}
			}
			openNet.setResProperMap(resProperMap);
			openNet.setReqResMap(reqResMap);

			//���ñ�ǨId������ӳ��
			Map<String, String> tranLabelMap = new HashMap<String, String>();
			for (String interTran : interTrans) {
				tranLabelMap.put(interTran, getTranLabel(transitions, interTran));
			}
			openNet.setTranLabelMap(tranLabelMap);
			
			openNets.add(openNet);
		}
        
        /*//��ӡÿ��������
	    int size = openNets.size();
	    for (int i = 0; i < size; i++) {
	    	System.out.println("Print each petri net......" + "\n");
	    	PrintUtils.printNet(openNets.get(i));
	    	System.out.println("CtrlTrans: " + openNets.get(i).getCtrlTrans());
		}*/
        
        return openNets;
        
	}

	//��ÿ����ı��
	public String getPlaceLabel(Place[] places, String placeId) {
		for (Place place : places) {
			String tempId = place.getId();
			String label = place.getName();
			if (tempId.equals(placeId)) {
				return label;
			}
		}
		return null;
	}

	//��ñ�Ǩ�ı��
	public String getTranLabel(Transition[] trans, String tranId) {
		for (Transition tran : trans) {
			String tempId = tran.getId();
			String label = tran.getName();
			if (tempId.equals(tranId)) {
				return label;
			}
		}
		return null;
	}

	//�жϵ�ǰƬ���Ƿ����,�������򷵻ض�Ӧ������(��index��ʶ)
	public int isInGenPNs(List<ProNet> openNets, List<String> tempPlaces) {
		if (openNets.size() == 0) {
			return -1;
		}else {
			int size = openNets.size();
			for (int i = 0; i < size; i++) {
				List<String> places = openNets.get(i).getPlaces();
				//System.out.println("Places in: " + i + places);
				//Note:???????,??size???
				if (CollectionUtils.intersection(places, tempPlaces).size() != 0) {
					return i;
				}
			}
		}
		return -1;
	}

	//��ñ�Ǩ��Ӧ��flow
	public List<Flow> getFlowsByTran(Arc[] arcs, String tran) {
		List<Flow> flows = new ArrayList<Flow>();
		for (Arc arc : arcs) {
			String from = arc.getSource().getId();
	    	String to = arc.getTarget().getId();
	    	if (from.equals(tran) || to.equals(tran)) {
	    		Flow flow = new Flow();
	    		flow.setFlowFrom(from);
	    		flow.setFlowTo(to);
	    		flows.add(flow);
			}
		}
		return flows;
	}

	//��ȡ��Ǩ��ǰ��
	public List<String> getPreSet(Arc[] arcs, String tran) {
		List<String> preSet = new ArrayList<String>();
		for (Arc arc : arcs) {
			String from = arc.getSource().getId();
	    	String to = arc.getTarget().getId();
	    	if (tran.equals(to)) {
	    		if (!preSet.contains(from)) {
					preSet.add(from);
				}
			}
		}
		return preSet;
	}

	//��ȡ��Ǩ�ĺ�
	public List<String> getPostSet(Arc[] arcs, String tran) {
		List<String> postSet = new ArrayList<String>();
		for (Arc arc : arcs) {
			String from = arc.getSource().getId();
	    	String to = arc.getTarget().getId();
	    	if (tran.equals(from)) {
	    		if (!postSet.contains(to)) {
	    			postSet.add(to);
				}
			}
		}
		return postSet;
	}

	//���IdΪtranId�ı�Ǩ�İ�
	public Bag getBag(Arc[] arcs, String tranId) {
		
		Queue<String> visitingQueue = new LinkedList<>(); 
  		List<String> visitedQueue = new ArrayList<>(); 
  		visitingQueue.offer(tranId);
  		visitedQueue.add(tranId);//����tranId�Լ�

		//��������
  		while(visitingQueue.size() > 0){

			//����һ����Ǩ(��Id),�Դ˽���ǰ������
  			String tranIdFrom = visitingQueue.poll();

			//tempPlaces���ڴ洢tran��ǰ���ͺ�,������ѭ��ǰ���ظ�
  	    	List<String> tempPlaces = new ArrayList<String>();
  	    	List<String> preSetPlace = getPreSet(arcs, tranIdFrom);
  	    	for (String place : preSetPlace) {
  				if (!tempPlaces.contains(place)) {
  					tempPlaces.add(place);
  				}
  			}
  	    	List<String> postSetPlace = getPostSet(arcs, tranIdFrom);
  	    	for (String place : postSetPlace) {
  	    		if (!tempPlaces.contains(place)) {
  					tempPlaces.add(place);
  				}
  			}

			//tempTrans���ڴ洢tran�ɴ��ǰ��Ǩ�Ƽ�,������ѭ��ǰ���ظ�
  	    	List<String> tempTrans = new ArrayList<String>();
            for (String tempPlace : tempPlaces) {
				List<String> preSetTran = getPreSet(arcs, tempPlace);
				for (String preTran : preSetTran) {
					if (!tempTrans.contains(preTran)) {
						tempTrans.add(preTran);
					}
				}
				List<String> postSetTran = getPostSet(arcs, tempPlace);
				for (String postTran : postSetTran) {
					if (!tempTrans.contains(postTran)) {
						tempTrans.add(postTran);
					}
				}
			}
  			
  			for (String tempTran : tempTrans) {
				if (!visitedQueue.contains(tempTran)) {
					visitingQueue.offer(tempTran);
			  		visitedQueue.add(tempTran);
				}
			}
  		}
  		Bag bag = new Bag();
  		bag.addTrans(visitedQueue);
		return bag;
	}
	
	/******************************������ֹ��ʶ******************************/

	//����ÿ����֯��Ӧ�ַ�����ʶ,��Щ��ʶ����";"�ָ�,����1*P1+2*P2;2*P3+3*P4
	public List<Marking> parseMarkSet(String marksStr) {
		List<Marking> markings = new ArrayList<Marking>();
		//ÿ����֯����ֹ��ʶ�ַ���,�����ʶ��";"�ָ�
		String[] marks = marksStr.split(";");
		for (String mark : marks) {
			Marking tempMarking = parseOneMark(mark);
			markings.add(tempMarking);
			System.out.println("split marking: " + tempMarking.getPlaces());
		}
		return markings;
	}

	//����һ���ַ�����ʶ,����1*P1+2*P3+3*P4
	public Marking parseOneMark(String markStr) {
		Marking marking = new Marking();
		List<String> places = new ArrayList<String>();
		String[] maps = markStr.split("\\+");
		for (String map : maps) {
			String[] mappingArray = map.split("\\*");
			int num = Integer.parseInt(mappingArray[0].trim());
			for (int i = 0; i < num; i++) {
				places.add(mappingArray[1].trim());
			}
		}
		marking.setPlaces(places);
		return marking;
	}
	
}