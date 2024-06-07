# CETool
CETool
We develop a correctness enforcement tool called CETool, which consists of two modules, i.e., a modeler and an analyzer. The modeler is realized on PIPE (Platform Independent Petri net Editor) [55], which can be used by participating organizations to visually model their business processes. The output of the modeler is a PNML file extended with initial markings, final markings, and message places. The following figure shows an example (available at: https://github.com/MoqiYNU/Cases/blob/main/Example.xml) modeled by CETool, where the green places are message places.
 
![image](https://github.com/MoqiYNU/CETool/assets/49392929/59235af9-001c-472e-b7f2-8628d8abfe5a) 

The analyzer consists of three components, i.e., a reducer used to obtain the public process, a generator employed to obtain correct plans, and a refactor to generate the refactored business process. Using CETool, the refactored processes of CL and SU are generated as follows.

![ref_net0](https://github.com/MoqiYNU/CETool/assets/49392929/bcadaa55-ca2b-4fc8-823d-44b09554b6bd) 

![ref_net1](https://github.com/MoqiYNU/CETool/assets/49392929/f991f3b3-fa2f-48c1-a954-1939b58e759b) 

[55]	Bonet P, Llado C, Puigjaner R, et al. PIPE v2.5: a Petri net tool for performance modeling. Proc. 23rd Latin American Confer-ence on Informatics (CLEI 2007), 2007, pp.1-12.

# Guidelines for using CETool
1. One needs to first import the model (available at: https://github.com/MoqiYNU/CETool/tree/main/modeler) into Eclipse and then run the file "RunGui.Java" located in its src directory. In this way, one starts the modeler and can visually build business processes within it. Once the business processes are modeled, they can be exported as a PNML file through the modeler's save operation.
2. One needs to import the analyzer (available at: https://github.com/MoqiYNU/CETool/tree/main/analyzer) into VS Code and runs the file "cbp_exps.py" in it, then the refactored processes of business processes can be generated and displayed in the form of dot files.
