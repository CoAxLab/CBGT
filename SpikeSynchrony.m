function synch=SpikeSynchrony(t,SpikeTrain,tbin)

% Following the same procedure than Corbit, Whalen et al. 2016

% t = time vector
% SpikeTrain=SpikeTrain(time,neurons) Containing 0-1


binpos=zeros(floor(t(end)/tbin)+1,1);
ai=zeros(floor(t(end)/tbin)+1,size(SpikeTrain,2));
%ai=zeros(floor(t(end)/tbin),size(SpikeTrain,2));
binpos(1)=1;
for i=1:floor(t(end)/tbin)
    [val,pos]=min(abs(t-i*tbin)); % Find all i*tbin positions in vector t
    % we need to do it because the itegrator has variable step-size
    binpos(i+1)=pos;  %  binpos(1)=1.
end
for i=1:length(binpos)-1
    ai(i,:)=sum(SpikeTrain(binpos(i):binpos(i+1),:),1)/tbin;
end
si2=mean(ai.^2,1)-mean(ai,1).^2;     % neuron variance si2(neurons)
a=mean(ai,2);                       % a(t)=mean(ai(t,i)) over neurons
spop2=mean(a.^2)-mean(a)^2;    % population variance spop2

synch=spop2/mean(si2);