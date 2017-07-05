# network.conf and int DescribeNetwork()

The network.conf file decribes all neural populations, receptors, and connections. Similar to the network.pro file, there is 1 statement per line.  


  


The file is organized as a list of neural populations. Each population declaration begins with  


NeuralPopulation: [name]  


and ends with  


EndNeuralPopulation  


  


Within each population declaration is a list of population parameters, followed by a list of receptor declarations, followed by a list of target declarations.  


  


The available population parameters are listed below. Several population parameters take on specific values by default, so not all parameters must be listed in the file.

  


N= .Ncells : number of neurons in the population  


  


C= .C : capacitance (nF)  


Taum= .Taum : membrane time constant  


RestPot= .RestPot : cell resting potential (mV)  


ResetPot= .ResetPot : cell reset potential after spike  


Threshold= .Threshold : Threshold for emitting a spike (mV)  


  


RestPot_ca= .Vk : Resting potential for calcium-activated potassium channels (mV)  


Alpha_ca= .alpha_ca : Amount of increment of [Ca] with each spike discharge. (muM)  


Tau_ca= .tau_ca : Time constant for calcium-activated potassium channels (msec)  


Eff_ca= .g_ahp : Efficacy for calcium-activated potassium channels (nS)  


  


//Anomalous delayed rectifier (ADR)  


g_ADR_Max= .g_adr_max (= 0) : Maximun value of the g  


V_ADR_h= .Vadr_h (= -100) : Potential for g_adr=0.5g_adr_max  


V_ADR_s= .Vadr_s (= 10) : Slope of g_adr at Vadr_h, defining sharpness of g_ard shape.   


ADRRevPot= .ADRRevPot (= -90) : Reverse potential for ADR  


g_k_Max= .g_k_max (= 0) : Maximum outward rectifying current  


V_k_h= .Vk_h (= -34) : Potential for g_k=0.5g_k_max  


V_k_s= .Vk_s (= 6.5) : Slope of g_k at Vk_h, defining how sharp the shape of g_k is.  


tau_k_max= .tau_k_max (= 8) : maximum tau for outward rectifying k current  


  


tauhm= .tauhm (= 20) : ?  


tauhp= .tauhp (= 100) : ?  


V_h= .V_h (= -60) : ?  


V_T= .V_T (= 120) : ?  


g_T= .g_T (= 0.0) : ?  


  


After these population parameters, and still within the population declaration, is a list of receptor declarations. Each receptor declaration begins with  


Receptor: [name]  


and ends with  


EndReceptor  


  


Within each receptor declaration is a list of receptor parameters. The available receptor parameters are listed below.  


  


Tau= .Tau[currentreceptor] : tau for conductance, see EQ 5/6  


RevPot= .RevPots[...] : Reversal potential  


FreqExt= .FreqExt[...] : External frequency  


FreqExtSD= .FreqExtSD[...] (= 0) : External frequency standard deviation  


MeanExtEff= .MeanExtEff[...] : External efficacy  


ExtEffSD= .ExtEffSD[...] (= 0) : External efficacy standard deviation  


MeanExtCon= .MeanExtCon[...] : External connections  


  


There is also a .MgFlag[...] parameter, corresponding to magnesium block, which is set to true if the receptor name is NMDA.   


  


Following the receptor declarations, and still within the population declaration, is a list of declarations for each target population (representing synaptic projections from population to target population). Each target population declaration starts with  


TargetPopulation: [name]  


and ends with  


EndTargetPopulation  


  


Within each target declaration is a list of parameters.  


  


Connectivity= .Connectivity : mean fraction of randomly connected target neurons  


TargetReceptor= .TargetReceptor : Target receptor code (name)  


MeanEff= .MeanEfficacy : mean efficacy (for initialization)  


EffSD= .EfficacySD (= 0) : Standard deviation of the efficacy distribution.  


STDepressionP= .pv (= 0) : Short-term depression P (see equation 7)  


STDepressionTau= .tauD (= 1000) : Short-term depression Tau (see equation 7)  


STFacilitationP= .Fp (= 0) : Short-term facilitation P (see equation 7)  


STFacilitationTau= .tauF (= 5000) : Short-term facilitation Tau (see equation 7)   


  


The function parses the file in two passes, the first to gather the names of populations and receptors, and the second for all of the details.  
