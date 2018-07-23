clear all;
clc;

% Plots for the constant case:
load('./Tables/Dopamine_p1_085-1.mat'); % You must write here the folder's name
x1='D_L';
x2='D_R';
x3='I_L';
x4='I_R';
%% All variables for one neuron

Action1=find(ActPrev(:,2)==1);
Action2=find(ActPrev(:,2)==-1);

% Here you can plot longer or shorter times. In case you want to zoom in
xinf=t0; % initial time
xsup=tf; % final time
% here you can play with the number of the neuron you want to plot.
% n\in[1,5] --> dMSN facilitating L-action
% n\in[6,10] --> dMSN facilitating R-action
% n\in[11,15] --> iMSN suppressing L-action
% n\in[16,20] --> iMSN suppressing R-action
n=1;  % 1st dMSN-left
n2=8; % 1st dMSN-right
STscalar1=ST(:,n);
pos01=find(STscalar1==0);
pos11=find(STscalar1==1);
STscalar2=ST(:,n2);
pos02=find(STscalar2==0);
pos12=find(STscalar2==1);
    
xpannel=8; %number of subpannels
h=figure();
subplot(xpannel,1,1); set(gca,'XTickLabel',[],'FontSize',16);
hold on;
STscalar1(pos01,1)=-80;  STscalar2(pos02,1)=-80;
STscalar1(pos11,1)=-40;  STscalar2(pos12,1)=-40;
plot(t,STscalar2,'Color',[0.8,0.5,0.5],'linewidth',2);
plot(t,STscalar1,'Color',[0.8,0.8,0.8],'linewidth',2);
plot(t,v(:,n2),'-','Color',[0.8,0,0],'linewidth',2);
plot(t,v(:,n),'k-','linewidth',2);
plot(ActPrev(Action1,1),-60+0*ActPrev(Action1,1),'o','MarkerEdge','k','MarkerFace',[0.2,1,0],'MarkerSize',6);
plot(ActPrev(Action2,1),-60+0*ActPrev(Action2,1),'o','MarkerEdge','k','MarkerFace',[1,153/255,51/255],'MarkerSize',6);
ylabel('ST cortex');
xlim([xinf xsup]);
ylabel('v'); % mV
hold off;


subplot(xpannel,1,2);  set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,Apre(:,n2),'-r','linewidth',2);
plot(t,Apre(:,n),'-k','linewidth',2);
ylabel('Apre');
xlim([xinf xsup]);
hold off;
%axis([t0 tf 0 3.1]);
subplot(xpannel,1,3);  set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,Apost(:,n2),'-r','linewidth',2);
plot(t,Apost(:,n),'-k','linewidth',2);
ylabel('Apost');
xlim([xinf xsup]);
hold off;

subplot(xpannel,1,4);  set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,E(:,n2),'r-','linewidth',2);
plot(t,E(:,n),'k-','linewidth',2);
ylabel('E');
xlim([xinf xsup]);
hold off;

subplot(xpannel,1,5); set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,DA(1:end-1,n),'k-','linewidth',2);
ylabel('DA');
xlim([xinf xsup]);
hold off;

subplot(xpannel,1,6);  set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,w(:,n),'k-','linewidth',2);
plot(t,w(:,n2),'r-','linewidth',2);
%legend('D1_1 neuron', 'D1_2 neuron');
ylabel('w');
xlim([xinf xsup]);
hold off;

subplot(xpannel,1,7);  set(gca,'XTickLabel',[],'FontSize',16);
hold on;
plot(t,g(:,n2),'-r','linewidth',2);
plot(t,g(:,n),'-k','linewidth',2);
ylabel('g'); % (\muA/cm^2)
xlim([xinf xsup]);
hold off;
%axis([t0 tf 0 1]);

subplot(xpannel,1,8);  set(gca,'FontSize',16);
hold on;
plot(t,QQ(:,1),'k-','linewidth',2);
plot(t,QQ(:,2),'r-','linewidth',2);
ylabel('Q'); %  (\muA/cm^2)
%legend('Q_1', 'Q_2');
xlim([xinf xsup]);
xlabel('Time (ms)');
hold off;

%% Weights + Q
xx=[x1; x2; x3; x4];
xpannel2=5;
h=figure();
for j=1:4
    actualPopNeurons = nVneurons(j);
    iniNeuroPlot= sum(nVneurons(1:j-1));
    subplot(xpannel2,1,j); set(gca,'XTickLabel',[],'FontSize',16);
    hold on;
    hold all;
    for ni=1:actualPopNeurons
        plot(t,w(:,iniNeuroPlot+ni),'-');
    end
    ylabel(xx(j,:));
    xlim([t0 tf]);
    hold off;
end
subplot(xpannel2,1,5); set(gca,'FontSize',16);
hold on;
plot(t,QQ(:,1),'k-','linewidth',2);
plot(t,QQ(:,2),'r-','linewidth',2);
ylabel('Q(t)');
xlim([t0 tf]);
hold off;

%% wD/wI - Q Contour
pointsize=10;
h=figure(); 
subplot(1,2,1); set(gca,'FontSize',16);
hold on; 
scatter(wDIact1(1:10:end),QQ(1:10:end,1),pointsize, transpose(t(1:10:end)/1000));
xlabel('w_{D}/w_{I}');
ylabel('Q_L');
hold off;
subplot(1,2,2); set(gca,'FontSize',16);
hold on;
scatter(wDIact2(1:10:end),QQ(1:10:end,2),pointsize, transpose(t(1:10:end)/1000));
xlabel('w_{D}/w_{I}');
ylabel('Q_R');
colorbar;
hold off;

%% Population Averaged Firing Rate (Hz)
sumSTnD1act1=sum(sum(STn(:,1:nD1act1),1)./(t(end)-t(1)))/nD1act1*1000;
sumSTnD1act2=sum(sum(STn(:,nD1act1+1:nD1act1+nD1act2),1)./(t(end)-t(1)))/nD1act2*1000;
sumSTnD2act1=sum(sum(STn(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),1)./(t(end)-t(1)))/nD2act1*1000;
sumSTnD2act2=sum(sum(STn(:,nD1act1+nD1act2+nD2act1+1:end),1)./(t(end)-t(1)))/nD2act2*1000;

barFig=[sumSTnD1act1 sumSTnD1act2 sumSTnD2act1 sumSTnD2act2];
h=figure();
hold on;
title('Averaged Population Firing Rate');
bar(barFig);
set(gca, 'XTick', [1 2 3 4]);
set(gca,'XTickLabel',{x1, x2, x3, x4},'FontSize',16);
hold off;


%% Population Firing Rate (Hz)
% Average into the bins (each tw=50ms)
sumSTnD1act1=sum(STn(:,1:nD1act1),2)./nD1act1*1000;
sumSTnD1act2=sum(STn(:,nD1act1+1:nD1act1+nD1act2),2)./nD1act2*1000;
sumSTnD2act1=sum(STn(:,nD1act1+nD1act2+1:nD1act1+nD1act2+nD2act1),2)./nD2act1*1000;
sumSTnD2act2=sum(STn(:,nD1act1+nD1act2+nD2act1+1:end),2)./nD2act2*1000;

tw=500; 
posBit=floor(tw/dt);
totalBits=floor(length(t)/posBit);
FiringRateD1act1=zeros(totalBits,1);
FiringRateD1act2=zeros(totalBits,1);
FiringRateD2act1=zeros(totalBits,1);
FiringRateD2act2=zeros(totalBits,1);
FiringRateTime=zeros(totalBits,1);
pi=1;
for i=1:totalBits
    FiringRateTime(i,1)=(tw*(i-1)+tw*i)/2;
    FiringRateD1act1(i,1)=sum(sumSTnD1act1(pi:pi+posBit-1))/tw;
    FiringRateD1act2(i,1)=sum(sumSTnD1act2(pi:pi+posBit-1))/tw;
    FiringRateD2act1(i,1)=sum(sumSTnD2act1(pi:pi+posBit-1))/tw;
    FiringRateD2act2(i,1)=sum(sumSTnD2act2(pi:pi+posBit-1))/tw;
    pi=pi+posBit;
end

h=figure(); set(gca,'FontSize',16);
hold on;
p1 = createPatches(FiringRateTime,FiringRateD1act1,tw/2,'k',0.4);
p2 = createPatches(FiringRateTime,FiringRateD1act2,tw/2,'r',0.3);
xlabel('Time (ms)');
ylabel('Population firing rate');
%xlim([t0 tf]);
hold off;

%% Action Rate 
h=figure(); set(gca,'FontSize',16);
hold on; 
p1 = createPatches(rateTime,rateAct1*tw,tw/2,'k',0.4);
p2 = createPatches(rateTime,rateAct2*tw,tw/2,'r',0.3);
xlabel('Time (ms)');
ylabel('Rate of action');
hold off;

