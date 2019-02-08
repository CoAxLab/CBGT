
function [wi, widop, DA, STn, ST, QQ, ActPrev, Reward, ti] = rk45_DA_LTDPcontrol (RHS, t0, x0, x0dop, tf, N, paramSpikeControl, DAModelParam1, DAModelParam2, ActionParam, taug, ST, DA, nVneurons, neqModel, Qcritic, Reward,RewardParam)
                                                                
nD1=nVneurons(1)+nVneurons(2);
nD2=nVneurons(3)+nVneurons(4);

% Spike Control Parameters:
SpitkeThresh=paramSpikeControl(1);
%RefractoryTime=paramSpikeControl(2);
Vrest=paramSpikeControl(3);

% Action parameters
tauDOP = ActionParam(2);    % decay constant for dopamine
Tsilent=ActionParam(3);     % period to ensure the silent state
action1Thr=ActionParam(5);
action2Thr=ActionParam(6);


% Initializations
nNeurons = sum(nVneurons);
neqn = length(x0);
neqdop = length(x0dop);
neq = floor(length(x0dop)/nNeurons);
STn=zeros(1,nNeurons);          % At t0, non-striatum neurons do any spikes.
SpikeControl=zeros(1,nNeurons);
actionGiven=0;
actionCounter(1:2)=0;

                                
% INTEGRATOR SOLVER CONSIDERING CONDUCTANCES + ELIGIBILITY
ti(1) = t0;
wi(1:neqn, 1) = x0';
widop(1:neqdop,1)=x0dop';
QQ(1,:)=Qcritic';
ActPrev(1,:)=[0 0];
i = 2;

if(N <= 0)
    disp( 'N must be positive and different to 0' );
    return;
else
    h = (tf - t0)/N;
end
while(t0 < tf)
    % INTEGRATE THE NEURAL MODEL at time t0
    k1 = h * feval(RHS, t0, x0, nVneurons, neqModel, taug);
    k2 = h * feval(RHS, t0 + h/2, x0 + k1/2, nVneurons, neqModel, taug);
    k3 = h * feval(RHS, t0 + h/2, x0 + k2/2, nVneurons, neqModel, taug);
    k4 = h * feval(RHS, t0 + h, x0 + k3, nVneurons, neqModel, taug);
    
    x0 = x0 + (k1 + 2*k2 + 2*k3 + k4)/6;
    
    % SPIKE CONTROL - We also treat the reset condition v<-vrest for EIF neurons.
    STn(i,:)=0;
    SpikeControl(i,:)=0; % For action's control.
    for ni=1:nNeurons
        pos=(ni-1)*neqModel;
        %Look for spikes...
        if x0(pos+1)>SpitkeThresh % we reset the membrane potential to the Vrest value
            x0(pos+1)=Vrest;      % Spike!
            STn(i,ni)=1;          % Post-synpatic spike train necessary to integrate the Dopamine equations
            SpikeControl(i,ni)=1; % Copy of the Post-synpatic spike train to be modified in the action function
        end
    end
    
    % DOPAMINE PROCEDURE
    % If now action is performed, DA decays to 0
    DAupdate=DA(end,:)*exp(-(h/tauDOP));
    DA = [DA; DAupdate];
    if actionGiven==0
        % Change DA acording to some Rule -> 3 spikes in a given window - 1 spike if prevention.
        [DA,SpikeControl,actionGiven,actionCounter,Qcritic,ActPrev,Reward] = action(t0,h,DA,SpikeControl,nVneurons,ActionParam,actionGiven,actionCounter,Qcritic,ActPrev,RewardParam,Reward,i);
    end
    % % If either action 1 or action 2 reach the threshold, We switch the actions (from now on)
    % if actionCounter(1)==action1Thr || actionCounter(2)==action2Thr
        % Reward(i+1:end,1)=Reward(i,2);  
        % Reward(i+1:end,2)=Reward(i,1); 
        % actionCounter=0*actionCounter;
    % end
        
    % Integrate the dopamine
    k1 = h * feval('DA_LTDPmodel', t0, x0dop, nD1, nD2, DA, ST, STn, i, DAModelParam1,DAModelParam2);
    k2 = h * feval('DA_LTDPmodel', t0 + h/2, x0dop + k1/2, nD1, nD2, DA, ST, STn, i, DAModelParam1,DAModelParam2);
    k3 = h * feval('DA_LTDPmodel', t0 + h/2, x0dop + k2/2, nD1, nD2, DA, ST, STn, i, DAModelParam1,DAModelParam2);
    k4 = h * feval('DA_LTDPmodel', t0 + h, x0dop + k3, nD1, nD2, DA, ST, STn, i, DAModelParam1,DAModelParam2);
    
    x0dop = x0dop + (k1 + 2*k2 + 2*k3 + k4)/6;
    
    % Update g
    if actionGiven==1
        STinit=floor(max(t0-Tsilent,0)/h)+1;
        STend=floor(t0/h)+1;
        if sum(sum(STn(STinit:STend,:)))~=0
            ST(i,:)=0;
        else
            actionGiven=0;
        end
    end
    for ni=1:nNeurons
        posg=(ni-1)*neqModel+2;
        posw=(ni-1)*neq+4;
        if ST(i,ni)==1
            x0(posg)=x0(posg)+x0dop(posw); %g=g+w!
            if x0(posg)<0
                x0(posg)=0;
            end
        end
    end
    
    
    t0 = t0 + h;
    ti(i) = t0;                      % save the integrated time t0
    wi(1:neqn, i) = x0';             % save the obtained solution x0
    widop(1:neqdop, i) = x0dop';     % save the obtained solution x0dop
    QQ(i,:)=Qcritic';                % save the updated Q values (just for "plot" intentions)
    i = i + 1;
end

