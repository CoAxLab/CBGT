function [DA,SpikeControl,actionGiven,actionCounter,Qcritic,ActPrev,Reward] = action(t,h,DA,SpikeControl,nVneurons,ActionParam,actionGiven,actionCounter,Qcritic,ActPrev,RewardParam,Reward,i)
% ONLY FOR FIXED STEP-SIZE.
% SpikeControl = spike train of all neurons of the post-synaptic population. From
%                the initial time (t0) to current time (tcurr).
% h = time step size - considered to be fixed along the simulation.
% nVneurons = [D1act1, D1act2, D2act1, D2act2] vector containing the number
%             of each neuron population
% ActionParam = Parameters requierd for the action. 
% lastAction = keeps the last time that an action happens. Necessary for
%              the DA refractory time period
% Qcritic = [Q1,Q2] current values 
% ActPrev = Keeps the action that takes place: 
%           1=action1; 0.5=prevention of action1
%           -1=action2; -0.5=prevention of action2
% Reward=[r1 r2] contains the two current rewards (two real numbers between 0 and 1).

Spikes=3; % Number of necessary spikes inside the window.

% Different neuron types
nD1act1 = nVneurons(1);
nD1act2 = nVneurons(2);
nD2act1 = nVneurons(3);
nNeurons = sum(nVneurons);

% Dopamine parameters
dtDA = ActionParam(1);    % dtDA = time window where the action has to be given.        
alphaQ = ActionParam(4);  % Learning rate

% Reward parameters
rbar = RewardParam(1);
r1Prob = RewardParam(2);
r2Prob = RewardParam(3);
reward1 = 0;
reward2 = 0;

Q1critic = Qcritic(1);
Q2critic = Qcritic(2);

% Spike Counter to check the action
% SpikeNeuron(ni) = 1 if neuron ni did an spike during the last dtDA ms; 
%                 = 0 otherwise
spikeNeuro=zeros(nNeurons,1);
initDA=max(1,size(SpikeControl,1) - floor(dtDA/h));
for ni=1:nNeurons
    if sum(SpikeControl(initDA:end,ni))>0
        spikeNeuro(ni)=1;   
    end
end

%% Action choice
% IF action happens in D1act1 or in D2act1, APPLY ACTION TO EVERYONE 
% (1) If a D1act2 neuron does an spike at this instant time, then we delete 
%     the last spike in the D1act1 counter.
% ELSE, 
% (2) we look if action 1 is given in D2act1 population of neurons
iniD2act1=nD1act1+nD1act2+1;
endD2act1=nD1act1+nD1act2+nD2act1;
if sum(SpikeControl(end,iniD2act1:endD2act1))>=1   % it means that at least one D2act1 does an spike right now
    [r,c]=find(SpikeControl(:,1:nD1act1)); [mr,p]=max(r); SpikeControl(mr,c(p))=0; % we cancel one previous spike corresponding to the last time.
    ActPrev=[ActPrev; t 0.5];  % Save Action/Prevention table (Prevention to act 1 has place)
elseif sum(spikeNeuro(1:nD1act1))>=Spikes
        % Change the reward according to a given probability
        if rand<r1Prob
            reward1=rbar;
        else
            reward1=0;
        end
        DA(end,:)=reward1-max(Q1critic,Q2critic);       % Update DA
        Q1critic=Q1critic+alphaQ*(reward1-Q1critic);    % Updat Q1
        SpikeControl=0*SpikeControl;    % We reset the spike counting of all neurons!
        ActPrev=[ActPrev; t 1];         % Save Action/Prevention table (Action 1 has place)
        actionGiven=1;
        actionCounter(1)=actionCounter(1)+1;
end

iniD2act2=nD1act1+nD1act2+nD2act1+1;
endD2act2=nNeurons;
if sum(SpikeControl(end,iniD2act2:endD2act2))>=1  % it means that at least one D2act2 does an spike right now
    [r,c]=find(SpikeControl(:,nD1act1+1:nD1act1+nD1act2)); [mr,p]=max(r); SpikeControl(mr,nD1act1+c(p))=0; % we cancel one previous spike corresponding to the last time.
    ActPrev=[ActPrev; t -0.5];  % Save Action/Prevention table (Prevention to act 2 has place)
elseif sum(spikeNeuro(nD1act1+1:nD1act1+nD1act2))>=Spikes
    if rand<r2Prob
        reward2=rbar;
    else
        reward2=0;
    end
    DA(end,:)=reward2-max(Q1critic,Q2critic);        % Update DA
    Q2critic=Q2critic+alphaQ*(reward2-Q2critic);     % Update Q2
    SpikeControl=0*SpikeControl; % We reset the spike counting of all neurons!
    ActPrev=[ActPrev; t -1];  % Save Action/Prevention table (Action 2 has place)
    actionGiven=1; 
    actionCounter(2)=actionCounter(2)+1;
end

Qcritic=[Q1critic, Q2critic];
Reward(i,1)=reward1;
Reward(i,2)=reward2;
