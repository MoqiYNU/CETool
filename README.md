# CETool
CETool
We develop a correctness enforcement tool called CETool, which consists of two modules, i.e., a modeler and an analyzer. The modeler is realized on PIPE (Platform Independent Petri net Editor) [55], which can be used by participating organizations to visually model their business processes. The output of the modeler is a PNML file extended with initial markings, final markings, and message places. The following figure shows the motiving example (accessed at: https://github.com/MoqiYNU/Cases) modeled by CETool, where the green places are message places.
 
![image](https://github.com/MoqiYNU/CETool/assets/49392929/a6b94bd6-6fd7-4f97-9255-8a2012c3701c)


The analyzer consists of three components, i.e., a reducer used to obtain the public process, a generator employed to obtain correct plans, and a refactor to generate the refactored business process. Using CETool, the refactored processes of CL and SU are generated as follows.

![ref_net0](https://github.com/MoqiYNU/CETool/assets/49392929/03d78ac8-b2af-47c2-8be1-28af3a2cd7ca)

![ref_net1](https://github.com/MoqiYNU/CETool/assets/49392929/3efda9ba-6d04-466d-a216-188de67aa4a5) 

[55]	Bonet P, Llado C, Puigjaner R, et al. PIPE v2.5: a Petri net tool for performance modeling. Proc. 23rd Latin American Confer-ence on Informatics (CLEI 2007), 2007, pp.1-12.