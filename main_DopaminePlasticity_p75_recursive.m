% Simulate Dopamine Plasticity with trails.

% NOTE:
% The "Kyle configuration", use alpha_D2 = -55 and the non-crossed
%                           configuration when daugthers are created.
% The "Jon configuration", use alpha_D2 = 55 and the crossed configuration
%                           when daugthers are created.

clear all
clc
format long;

iterations=10;
for iter=1:iterations
    Config='Kyle';
    %Config='Jon';
    
    r1Prob = 0.75;
    r2Prob = 0.25;
    fileName='./Dopamine_p1_075';
    disp(iter);
    % ::::::::::::::::::: PARAMETERS :::::::::::::::::::
    % Network parameters.
    nD1act1=5;    % # of MSN neurons (D1 that facilitates action 1)
    nD1act2=5;    % # of MSN neurons (D1 that facilitates action 2)
    nD2act1=5;    % # of MSN neurons (D2 that prevents action 1)
    nD2act2=5;    % # of MSN neurons (D2 that prevents action 2)
    nVneurons=[nD1act1, nD1act2, nD2act1, nD2act2];
    nNeurons=nD1act1+nD1act2+nD2act1+nD2act1;
    model='EIFmodel';
    neqModel=2;   % Equations of the model (it depends on the neural model used)
    neqDA=4;      % The dopamine treatment has always 4 differential equations.
    
    % Time parameters.clo
    t0=0;                 % Initial time of the simulation
    tf=500;              % Final time of the simulation
    dt= 0.01;             % Time step size
    tST = t0:dt:tf+dt;    % time vector
    N=(tf-t0)/dt;
    
    
    % Parameters for the Neural Model
    % Spike Control paramenters. Necessaries for I&F neurons:
    SpikeThresh=-40;
    RefractoryTime=0; %between 0 and 5 ms
    Vrest=-75;
    paramSpikeControl=[SpikeThresh, RefractoryTime, Vrest];
    
    % Dopamine parameters - Necessaries for the neural model
    alpha_D1 = 80;                          % regulates the effect of dopamine (w'=alpha*E*DA ...)
    if strcmp(Config,'Kyle'); alpha_D2 = -55; else alpha_D2 = 55;  end
    dPRE_D1 = 10;        dPRE_D2 = 10;      % fixed amount that the pre-synaptic firing (Apre) change
    dPOST_D1 = 6;        dPOST_D2 = 6;      % fixed amount that the post-synaptinc firing (Apost) change
    tauE_D1 = 3;         tauE_D2 = 3;       % Elegibility (E) time decay
    tauPRE_D1 = 9;       tauPRE_D2 = 9;     % pre-synaptic firing (Apre) time decay
    tauPOST_D1 = 1.2;    tauPOST_D2 = 1.2;  % post-synaptic firing (Apost) time decay
    delta_D1 = 0;        delta_D2 = 0;   	% extra LTD on the model (we don't consider it).
    kD1=0;               kD2=0;             % we added -k*w to w' equation (we don't use it).
    c2=2;                                   % To control tonic & phasic DA in D2 neurons.
    
    wmax_D1=0.1; wmin_D1=0;  % max and min values for w w'=alpha*E*DA*abs(wi-w), where i=max or min
    wmax_D2=0.03; wmin_D2=0;  % (wmin is not used since k=0).
    
    taug = 3;
    DAModelParam1=[alpha_D1, dPRE_D1, dPOST_D1, tauE_D1, tauPRE_D1, tauPOST_D1, delta_D1, kD1, wmax_D1, wmin_D1];
    DAModelParam2=[alpha_D2, dPRE_D2, dPOST_D2, tauE_D2, tauPRE_D2, tauPOST_D2, delta_D2, kD2, wmax_D2, wmin_D2,c2];
    
    % Action parameters:
    dtDA = 6;           % dtDA = time window where we consider that the action has to be given.
    tauDOP = 2;         % Dopamine time decay
    Tsilent=50;         % non-spiking period that needs to happens to make sure we are in the silent state
    action1Thr=10;       % Number of actions 1 necesary to switch the reward
    action2Thr=12;       % Number of actions 2 necesary to switch the reward
    alphaQ=0.05;        % learning rate
    Q1criticInitial=0;  % Initialization of Q1 value (DA=r-max(Q1,Q2)).
    Q2criticInitial=0;  % Initialization of Q2
    
    % Reward vectors (to make them variable in time). Now, they are constant and equal to 0.
    rbar=1;
    reward1 = zeros(length(tST),1);      % reward for action 1
    reward2 = zeros(length(tST),1);      % reward for action 2
    
    ActionParam=[dtDA, tauDOP, Tsilent, alphaQ, action1Thr, action2Thr];
    Reward=[reward1 reward2];
    RewardParam=[rbar r1Prob r2Prob];
    QcriticInitial=[Q1criticInitial, Q2criticInitial];
    
    
    % ::::::::::::::::::: CORTEX INPUT :::::::::::::::::::
    % Generate Cortex spike trains from a Mother Poisson Process
    % Kyle configuration for the MSN neurons and the actions (the non-crossed)
    % D1act1 and D2act1 recieves daugther inputs from one mother and
    % D1act2 and D2act2 recieves daugther inputs from anothe mother.
    
    Dcorr=0.;
    ST=zeros(length(tST),nNeurons); % initialization vector
    
    % MOTHER 1:
    % Daughter parameters:
    rateDaughterM1=0.2;     % daugthers rate from mother 1
    rateDaughterM2=0.2;     % daugthers rate from mother 2
    cDaughterM1=0.5+Dcorr;  % correlation of the daughters generated from mother 1
    cDaughterM2=0.5-Dcorr;  % correlation of the daughters generated from mother 1
    theta=1000/25;          % Frequency (in Hz) of the underlying oscillation
    A=0; %0.06;             % Amplitude of the oscillation \in (0,1)
    refrac=0.;              % neurons refractory period
    
    % Mother Oscillatory Poisson Process parameters (in sec)
    probM1= rateDaughterM1+cDaughterM1*(1-rateDaughterM1);
    probM2= rateDaughterM2+cDaughterM2*(1-rateDaughterM2);
    lambdaM1= rateDaughterM1/(probM1);
    lambdaM2= rateDaughterM2/(probM2);
    
    % Mother spike trains
    motherST1=oscPoisProc(tf+dt,dt,lambdaM1,theta,A,refrac);
    motherST2=oscPoisProc(tf+dt,dt,lambdaM2,theta,A,refrac);
    
    % Daughter spike trains. Spike train per each neuron...
    factor=1.5;
    for i=1:length(tST)
        for j=1:nD1act1
            if rand < probM1/factor
                ST(i,j)=motherST1(i);
            end
        end
        for j=1:nD1act2
            if rand < probM2/factor
                ST(i,j+nD1act1)=motherST2(i);
            end
        end
        if strcmp(Config,'Kyle') % Non-Crossed
            for j=1:nD2act1
                if rand < probM1
                    ST(i,j+nD1act1+nD1act2)=motherST1(i);
                end
            end
            for j=1:nD2act2
                if rand < probM2
                    ST(i,j+nD1act1+nD1act2+nD2act1)=motherST2(i);
                end
            end
        else %Jon-Configuration - Crossed
            for j=1:nD2act1
                if rand < probM2
                    ST(i,j+nD1act1+nD1act2)=motherST2(i);
                end
            end
            for j=1:nD2act2
                if rand < probM1
                    ST(i,j+nD1act1+nD1act2+nD2act1)=motherST1(i);
                end
            end
        end
    end
    
    % ::::::::::::::::::: SOLVE THE MODEL :::::::::::::::::::
    %Initial Conditions for the model
    x0=zeros(nNeurons*neqModel,1);
    for i=1:nNeurons
        pos=neqModel*(i-1);
        x0(pos+1)=normrnd(-65,10);   % v = voltage   (mV)
        x0(pos+2)=0;                 % g = conductances
    end
    % Initial Conditions for the DA.
    DA=zeros(1,nNeurons);
    x0dop=zeros(nNeurons*neqDA,1);
    for i=1:nD1act1+nD1act2          % D1-cells
        pos=neqDA*(i-1);
        x0dop(pos+1)=0;       % APRE = Pre-synaptic firing rate
        x0dop(pos+2)=0;       % APOST = Post-synaptic firing rate
        x0dop(pos+3)=0;       % E = Eligibility
        x0dop(pos+4)=0.015;   % w = Strenght
    end
    for i=nD1act1+nD1act2+1:nNeurons  % D2-cells
        pos=neqDA*(i-1);
        x0dop(pos+1)=0;       % APRE = Pre-synaptic firing rate
        x0dop(pos+2)=0;       % APOST = Post-synaptic firing rate
        x0dop(pos+3)=0;       % E = Eligibility
        x0dop(pos+4)=0.02;    % w = Strenght        %0.009;
    end
    
    % Solve the differential equations: the dopamine - neuronal network case
    [wi, widop, DA, STn, ST, QQ, ActPrev, Reward, t]= rk45_DA_LTDPcontrol(model,  t0, x0, x0dop, tf, N, paramSpikeControl, DAModelParam1, DAModelParam2, ActionParam, taug, ST, DA, nVneurons,neqModel,QcriticInitial,Reward,RewardParam);
    wi=transpose(wi(:,1:end-1));
    widop=transpose(widop(:,1:end-1));
    t=t(1:end-1);
    STn=STn(1:end-1,:);
    ST=ST(1:end-1,:);
    
    
    % ----- Create Membrane Potential (v(t,n)) tables -> v(t,n)=voltage(time,neuron)
    v=zeros(length(t),nNeurons);
    g=zeros(length(t),nNeurons);
    Apre=zeros(length(t),nNeurons);
    Apost=zeros(length(t),nNeurons);
    E=zeros(length(t),nNeurons);
    w=zeros(length(t),nNeurons);
    for i=1:nNeurons
        ni=(i-1)*neqModel;
        v(:,i)=wi(:,ni+1);
        g(:,i)=wi(:,ni+2);
        
        ni=(i-1)*neqDA;
        Apre(:,i)=widop(:,ni+1);
        Apost(:,i)=widop(:,ni+2);
        E(:,i)=widop(:,ni+3);
        w(:,i)=widop(:,ni+4);
    end
    reward1=Reward(:,1);
    reward2=Reward(:,2);
    
    % ::::::::::::::::::: DATA TREATMENT :::::::::::::::::::
    
    if size(ST,1)~=size(STn,1)
        ST=ST(1:end-1,:);
    end
    if size(QQ,1)~=size(t,1)
        QQ=QQ(1:end-1,:);
    end
    
    
    % Firing Rate
    sumSTnD1act1=sum(sum(STn(:,1:nD1act1),1)./(t(end)-t(1)))/nD1act1;
    sumSTnD1act2=sum(sum(STn(:,nD1act1+1:nD1act1+nD1act2),1)./(t(end)-t(1)))/nD1act2;
    sumSTnD2act1=sum(sum(STn(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),1)./(t(end)-t(1)))/nD2act1;
    sumSTnD2act2=sum(sum(STn(:,nD1act1+nD1act2+nD2act1+1:end),1)./(t(end)-t(1)))/nD2act2;
    
    % Spike Synchronization between neurons
    tbin=15; %15ms
    SpikesynchD1act1=SpikeSynchrony(t,STn(:,1:nD1act1),tbin);
    SpikesynchD1act2=SpikeSynchrony(t,STn(:,nD1act1+1:nD1act1+nD1act2),tbin);
    SpikesynchD2act1=SpikeSynchrony(t,STn(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),tbin);
    SpikesynchD2act2=SpikeSynchrony(t,STn(:,nD1act1+nD1act2+nD2act1+1:end),tbin);
    
    % Actions
    Action1=find(ActPrev(:,2)==1);
    Action2=find(ActPrev(:,2)==-1);
    
    %  wD and wI
    wDIact1=mean(w(:,1:nD1act1),2)./mean(w(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),2);
    wDIact2=mean(w(:,nD1act1+1:nD1act1+nD1act2),2)./mean(w(:,nD1act1+nD1act2+nD2act1+1:end),2);
    
    % gD and gI
    gDIact1=mean(g(:,1:nD1act1),2)./mean(g(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),2);
    gDIact2=mean(g(:,nD1act1+1:nD1act1+nD1act2),2)./mean(g(:,nD1act1+nD1act2+nD2act1+1:end),2);
    
    % rate of action performance as a function of time
    tw=500;
    rAct1=zeros(length(t),1);
    rAct2=zeros(length(t),1);
    for i=1:length(Action1)
        [val,p]=min(abs(t-ActPrev(Action1(i),1)));
        rAct1(p(1))=1;
    end
    for i=1:length(Action2)
        [val,p]=min(abs(t-ActPrev(Action2(i),1)));
        rAct2(p(1))=1;
    end
    
    posBit=floor(tw/dt);
    totalBits=floor(length(t)/posBit);
    rateAct1=zeros(totalBits,1);
    rateAct2=zeros(totalBits,1);
    rateTime=zeros(totalBits,1);
    pi=1;
    for i=1:totalBits
        rateTime(i,1)=(tw*(i-1)+tw*i)/2;
        rateAct1(i,1)=sum(rAct1(pi:pi+posBit-1))/tw;
        rateAct2(i,1)=sum(rAct2(pi:pi+posBit-1))/tw;
        pi=pi+posBit;
    end
    
    % Q1(action onset time) and Q2(action onset time) traces
    p=find(abs(ActPrev(:,2))==1);
    OnsetTrial=ActPrev(p,1);
    Trials=1:1:length(OnsetTrial);
    QtrialAct1=zeros(length(OnsetTrial),1);
    QtrialAct2=zeros(length(OnsetTrial),1);
    
    QtrialAct1(1)=mean(QQ(1:floor(OnsetTrial(1)/dt)+1,1));
    QtrialAct2(1)=mean(QQ(1:floor(OnsetTrial(1)/dt)+1,2));
    for i=1:length(OnsetTrial)-1
        QtrialAct1(i+1)=mean(QQ(floor(OnsetTrial(i)/dt)+1:floor(OnsetTrial(i+1)/dt)+1,1));
        QtrialAct2(i+1)=mean(QQ(floor(OnsetTrial(i)/dt)+1:floor(OnsetTrial(i+1)/dt)+1,2));
    end
    
    barFigFR=[sumSTnD1act1 sumSTnD1act2 sumSTnD2act1 sumSTnD2act2];
    barFigSyn=[SpikesynchD1act1, SpikesynchD1act2, SpikesynchD2act1, SpikesynchD2act2];
    
    tw=min(500,tf);
    rAct1=zeros(length(t),1);
    rAct2=zeros(length(t),1);
    for i=1:length(Action1)
        [val,p]=min(abs(t-ActPrev(Action1(i),1)));
        rAct1(p(1))=1;
    end
    for i=1:length(Action2)
        [val,p]=min(abs(t-ActPrev(Action2(i),1)));
        rAct2(p(1))=1;
    end
    
    posBit=floor(tw/dt);
    totalBits=floor(length(t)/posBit);
    rateAct1=zeros(totalBits,1);
    rateAct2=zeros(totalBits,1);
    rateTime=zeros(totalBits,1);
    pi=1;
    for i=1:totalBits
        rateTime(i,1)=(tw*(i-1)+tw*i)/2;
        rateAct1(i,1)=sum(rAct1(pi:pi+posBit-1))/tw;
        rateAct2(i,1)=sum(rAct2(pi:pi+posBit-1))/tw;
        pi=pi+posBit;
    end
    
    fileName=[fileName,'-',int2str(iter)];
    save(fileName);
    clearvars -except iterations;
end
