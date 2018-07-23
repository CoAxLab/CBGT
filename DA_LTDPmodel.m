function dx=DA_LTDPmodel(t,x,nD1,nD2,DAs,XPRE,XPOST,it,DAModelParam1,DAModelParam2)

% t = time (not necessary)
% x = [nMSN1*neq; nMSN2*neq]. D2-MSN neurons starts at position nMSN1*neq1+1.
%      only contains the dopamine variables (4 equations)
% nD1 = total number of D1 neurons
% nD2 = total number of D2 neurons

% Total number of neurons
nNeurons=nD1+nD2;

% Dopamine-plasticity parameters D1-Neurons
alpha_D1 = DAModelParam1(1);          
dPRE_D1 = DAModelParam1(2);          
dPOST_D1 = DAModelParam1(3);       
tauE_D1 = DAModelParam1(4);          
tauPRE_D1 = DAModelParam1(5);        
tauPOST_D1 = DAModelParam1(6);         
delta_D1 = DAModelParam1(7);           
kD1=DAModelParam1(8);   % We added the term -k*w to w' equation, to bound it instead of using \w in [w_min, w_max];

% Dopamine-plasticity parameters D2-Neurons
alpha_D2 = DAModelParam2(1); 
dPRE_D2 = DAModelParam2(2);
dPOST_D2 = DAModelParam2(3);
tauE_D2 = DAModelParam2(4);
tauPRE_D2 = DAModelParam2(5); 
tauPOST_D2 = DAModelParam2(6);
delta_D2 = DAModelParam2(7);  
kD2=DAModelParam2(8);          
c2=DAModelParam2(9);

% Boudaries of the weight (w) <--- NOT NECESSARY SINCE WEW HAVE ADDED THE -k*w in w' equation.
wmax_D1=DAModelParam1(9);        
wmax_D2=DAModelParam2(9);
wmin_D1=DAModelParam1(10);        
wmin_D2=DAModelParam2(10);
neq = floor(length(x)/nNeurons);
dx=zeros(nNeurons*neq,1);
% D1 - MSN neurons
for i=1:nD1
    pos=neq*(i-1);  % neq since each neuron is given by neq equations
    % pre-step values
    APRE=x(pos+1);
    APOST=x(pos+2);
    E=x(pos+3);
    w=x(pos+4);
    
    % Pre- and Post-spiking controllers
    XPRE_D1 = XPRE(it,i);    XPOST_D1 = XPOST(it,i);    
    DA=DAs(it,i);
    
    % Neuron Model
    % Eligibility and plasticity equations
    dx(pos+1)=(-APRE+dPRE_D1*XPRE_D1)/tauPRE_D1;         % dA_PRE / dt : Presynaptic firing
    dx(pos+2)=(-APOST+dPOST_D1*XPOST_D1)/tauPOST_D1;     % dA_POST / dt : Postsynaptic firing
    dx(pos+3)=(-E-XPRE_D1*APOST+XPOST_D1*APRE)/tauE_D1;  % dE/dt : Eligibility
    dx(pos+4)=alpha_D1*E*DA*(wmax_D1-w)-delta_D1*XPRE_D1-kD1*(w-wmin_D1);      % dw/dt : weigth changes according to DA (alpha*E*DA) and extra LTD (delta*XPRE)
end


% D2 - MSN neurons
for i=1:nD2
    pos=neq*(i-1)+nD1*neq;  % neq since each neuron is given by neq equations
    % pre-step values
    APRE=x(pos+1);
    APOST=x(pos+2);
    E=x(pos+3);
    w=x(pos+4);
    
    % Pre- and Post-spiking controllers
    XPRE_D2 = XPRE(it,nD1+i);    XPOST_D2 = XPOST(it,nD1+i);    
    DA=DAs(it,nD1+i);

    % Eligibility and plasticity equations
    dx(pos+1)=(-APRE+dPRE_D2*XPRE_D2)/tauPRE_D2;     % dA_PRE / dt : Presynaptic firing
    dx(pos+2)=(-APOST+dPOST_D2*XPOST_D2)/tauPOST_D2; % dA_POST / dt : Postsynaptic firing
    dx(pos+3)=(-E-XPRE_D2*APOST+XPOST_D2*APRE)/tauE_D2; % dE/dt : Eligibility
    %dx(pos+4)=alpha_D2*E*DA*(wmax_D2-w)-delta_D2*XPRE_D2-kD2*(w-wmin_D2);        % dw/dt : weigth changes according to DA (alpha*E*DA) and extra LTD (delta*XPRE)
    dx(pos+4)=(alpha_D2*E*DA)/(c2+DA)*(wmax_D2-w)-delta_D2*XPRE_D2-kD2*(w-wmin_D2);        % dw/dt : weigth changes according to DA (alpha*E*DA) and extra LTD (delta*XPRE)
end