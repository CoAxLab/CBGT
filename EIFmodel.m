function dx=EIFmodel(t,x,nVneurons,neqModel,taug)

% t = time (not necessary)
% x = [D1act1*neqModel, D1act2*neqModel, D2act1*neqModel, D2act2*neqModel]
% nDneurons = [D1act1, D1act2, D2act1, D2act2] vector containing the number 
%             of neurons in each subpopulation
% neqModel = number of equations in the neural model

nNeurons=sum(nVneurons); % Total number of neurons. All have the same model!
                         % Otherwise we need to change the code as in
                         % 'Dopamine-plasticity-BaladronEJN2017-Go_NoGo'.

% Neural parameters
vT=-59.9;   deltaT=3.48;    % specific parameters from the V-I curve
C=1;        Iapp=0;         
gL=0.1;     vL=-65;         % leak parameters
vE=0;       % vI=-80;       % I only consider excitatory input.


dx=zeros(nNeurons*neqModel,1);
for i=1:nNeurons
    pos=neqModel*(i-1);  % neqModel since each neuron is given by neqModel equations
    % pre-step values
    v=x(pos+1);
    g=x(pos+2);
    
    % synpatic current -- if XPre=1, we have setted g=w in rk45_DA_LTDPcontrol routine.
    Isyn=g*(v-vE);
    
    % Neuron Model
    dx(pos+1)=1/C*(-gL*(v-vL)+gL*deltaT*exp((v-vT)/deltaT)-Isyn+Iapp);  % voltage (mV)
    dx(pos+2)=-g/taug;
end