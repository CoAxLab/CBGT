%% --------------- P1 = 0.85 ---------------
% 1st - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5sec-p1_0_85.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials1=1:1:length(OnsetTrial);
QQ1 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act11=zeros(size(QQ1));
Act21=zeros(size(QQ1));
posA1=find(ActPrev(p,2)==1);
Act11(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act21(posA2) = 1;


% 2nd - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5sec-p1_0_85-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials2=1:1:length(OnsetTrial);
QQ2 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act12=zeros(size(QQ2));
Act22=zeros(size(QQ2));
posA1=find(ActPrev(p,2)==1);
Act12(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act22(posA2) = 1;


% 3rd - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5sec-p1_0_85-3.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials3=1:1:length(OnsetTrial);
QQ3 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act13=zeros(size(QQ3));
Act23=zeros(size(QQ3));
posA1=find(ActPrev(p,2)==1);
Act13(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act23(posA2) = 1;


% 4th - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/7sec-p1_0_85-4.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials4=1:1:length(OnsetTrial);
QQ4 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act14=zeros(size(QQ4));
Act24=zeros(size(QQ4));
posA1=find(ActPrev(p,2)==1);
Act14(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act24(posA2) = 1;

% 5th - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5sec-p1_0_85-5.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials5=1:1:length(OnsetTrial);
QQ5 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act15=zeros(size(QQ5));
Act25=zeros(size(QQ5));
posA1=find(ActPrev(p,2)==1);
Act15(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act25(posA2) = 1;


% 6th - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5sec-p1_0_85-6.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials6=1:1:length(OnsetTrial);
QQ6 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act16=zeros(size(QQ6));
Act26=zeros(size(QQ6));
posA1=find(ActPrev(p,2)==1);
Act16(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act26(posA2) = 1;

% 7th - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/7sec-p1_0_85-7.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials7=1:1:length(OnsetTrial);
QQ7 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act17=zeros(size(QQ7));
Act27=zeros(size(QQ7));
posA1=find(ActPrev(p,2)==1);
Act17(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act27(posA2) = 1;


% 8th - 6 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/6sec-p1_0_85-8.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials8=1:1:length(OnsetTrial);
QQ8 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act18=zeros(size(QQ8));
Act28=zeros(size(QQ8));
posA1=find(ActPrev(p,2)==1);
Act18(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act28(posA2) = 1;


% 8th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_85/5_5sec-p1_0_85-9.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials9=1:1:length(OnsetTrial);
QQ9 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act19=zeros(size(QQ9));
Act29=zeros(size(QQ9));
posA1=find(ActPrev(p,2)==1);
Act19(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act29(posA2) = 1;




h11=figure(11); 
set(gca,'FontSize',16);
hold on;
plot(Trials1,QQ1,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials2,QQ2,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials3,QQ3,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials4,QQ4,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials5,QQ5,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials6,QQ6,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials7,QQ7,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials8,QQ8,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
plot(Trials9,QQ9,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;


minT=min(length(Trials1),length(Trials2));
minT=min(minT,length(Trials3));
minT=min(minT,length(Trials4));
minT=min(minT,length(Trials5));
minT=min(minT,length(Trials6));
minT=min(minT,length(Trials7));
minT=min(minT,length(Trials8));
minT=min(minT,length(Trials9));

Trials=Trials1(1:minT);
QQ1=QQ1(1:minT); QQ2=QQ2(1:minT); QQ3=QQ3(1:minT); QQ4=QQ4(1:minT);
QQ5=QQ5(1:minT); QQ6=QQ6(1:minT); QQ7=QQ7(1:minT); QQ8=QQ8(1:minT);
QQ9=QQ9(1:minT);

Act11 = Act11(1:minT);   Act21 = Act21(1:minT);
Act12 = Act12(1:minT);   Act22 = Act22(1:minT);
Act13 = Act13(1:minT);   Act23 = Act23(1:minT);
Act14 = Act14(1:minT);   Act24 = Act24(1:minT);
Act15 = Act15(1:minT);   Act25 = Act25(1:minT);
Act16 = Act16(1:minT);   Act26 = Act26(1:minT);
Act17 = Act17(1:minT);   Act27 = Act27(1:minT);
Act18 = Act18(1:minT);   Act28 = Act28(1:minT);
Act19 = Act19(1:minT);   Act29 = Act29(1:minT);

QQ=[QQ1, QQ2, QQ3, QQ4, QQ5, QQ6, QQ7, QQ8, QQ9];

Act1=[Act11, Act12, Act13, Act14, Act15, Act16, Act17, Act18, Act19];
Act2=[Act21, Act22, Act23, Act24, Act25, Act26, Act27, Act28, Act29];

QQ=mean(QQ,2);
PercAct = sum(Act1,2)./(sum(Act1,2)+sum(Act2,2));

WS=10;
PercActWindow=zeros(length(PercAct)-WS,1);
for i=1:length(PercAct)-WS
    PercActWindow(i)=sum(PercAct(i:i+WS))/(WS+1);
end

h=figure(1); 
set(gca,'FontSize',16);
hold on;
plot(Trials,QQ,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;

h2=figure(2); 
set(gca,'FontSize',16);
hold on;
plot(Trials,PercAct,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;

h3=figure(3); 
set(gca,'FontSize',16);
hold on;
plot(Trials(1:end-WS),PercActWindow,'bo-','linewidth',2,'MarkerFace',[222/255,235/255,250/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;


%% --------------- P1 = 0.75 ---------------
% 1st - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5sec-p1_0_75.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials1=1:1:length(OnsetTrial);
QQ1 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act11=zeros(size(QQ1));
Act21=zeros(size(QQ1));
posA1=find(ActPrev(p,2)==1);
Act11(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act21(posA2) = 1;

% 2nd - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/7sec-p1_0_75.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials2=1:1:length(OnsetTrial);
QQ2 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act12=zeros(size(QQ2));
Act22=zeros(size(QQ2));
posA1=find(ActPrev(p,2)==1);
Act12(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act22(posA2) = 1;

% 3rd - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/7sec-p1_0_75-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials3=1:1:length(OnsetTrial);
QQ3 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act13=zeros(size(QQ3));
Act23=zeros(size(QQ3));
posA1=find(ActPrev(p,2)==1);
Act13(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act23(posA2) = 1;


% 4th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials4=1:1:length(OnsetTrial);
QQ4 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act14=zeros(size(QQ4));
Act24=zeros(size(QQ4));
posA1=find(ActPrev(p,2)==1);
Act14(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act24(posA2) = 1;


% 5th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-3.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials5=1:1:length(OnsetTrial);
QQ5 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act15=zeros(size(QQ5));
Act25=zeros(size(QQ5));
posA1=find(ActPrev(p,2)==1);
Act15(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act25(posA2) = 1;

% 6th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-4.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials6=1:1:length(OnsetTrial);
QQ6 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act16=zeros(size(QQ6));
Act26=zeros(size(QQ6));
posA1=find(ActPrev(p,2)==1);
Act16(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act26(posA2) = 1;

% 7th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-5.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials7=1:1:length(OnsetTrial);
QQ7 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act17=zeros(size(QQ7));
Act27=zeros(size(QQ7));
posA1=find(ActPrev(p,2)==1);
Act17(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act27(posA2) = 1;


% 8th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-6.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials8=1:1:length(OnsetTrial);
QQ8 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act18=zeros(size(QQ8));
Act28=zeros(size(QQ8));
posA1=find(ActPrev(p,2)==1);
Act18(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act28(posA2) = 1;


% 9th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_75/5_5sec-p1_0_75-7.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials9=1:1:length(OnsetTrial);
QQ9 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act19=zeros(size(QQ9));
Act29=zeros(size(QQ9));
posA1=find(ActPrev(p,2)==1);
Act19(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act29(posA2) = 1;


h11=figure(11); 
set(gca,'FontSize',16);
hold on;
plot(Trials1,QQ1,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials2,QQ2,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials3,QQ3,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials4,QQ4,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials5,QQ5,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials6,QQ6,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials7,QQ7,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials8,QQ8,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
plot(Trials9,QQ9,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;


minT=min(length(Trials1),length(Trials2));
minT=min(minT,length(Trials3));
minT=min(minT,length(Trials4));
minT=min(minT,length(Trials5));
minT=min(minT,length(Trials6));
minT=min(minT,length(Trials7));
minT=min(minT,length(Trials8));
minT=min(minT,length(Trials9));

Trials=Trials1(1:minT);
QQ1=QQ1(1:minT); QQ2=QQ2(1:minT); QQ3=QQ3(1:minT); QQ4=QQ4(1:minT); 
QQ5=QQ5(1:minT);  QQ6=QQ6(1:minT); QQ7=QQ7(1:minT); QQ8=QQ8(1:minT); 
QQ9=QQ9(1:minT); 

Act11 = Act11(1:minT);   Act21 = Act21(1:minT);
Act12 = Act12(1:minT);   Act22 = Act22(1:minT);
Act13 = Act13(1:minT);   Act23 = Act23(1:minT);
Act14 = Act14(1:minT);   Act24 = Act24(1:minT);
Act15 = Act15(1:minT);   Act25 = Act25(1:minT);
Act16 = Act16(1:minT);   Act26 = Act26(1:minT);
Act17 = Act17(1:minT);   Act27 = Act27(1:minT);
Act18 = Act18(1:minT);   Act28 = Act28(1:minT);
Act19 = Act19(1:minT);   Act29 = Act29(1:minT);

QQ=[QQ1, QQ2, QQ3, QQ4, QQ5, QQ6, QQ7, QQ8, QQ9];

Act1=[Act11, Act12, Act13, Act14, Act15, Act16, Act17, Act18, Act19];
Act2=[Act21, Act22, Act23, Act24, Act25, Act26, Act27, Act28, Act29];


QQ=mean(QQ,2);
PercAct = sum(Act1,2)./(sum(Act1,2)+sum(Act2,2));

PercActWindow=zeros(length(PercAct)-WS,1);
for i=1:length(PercAct)-WS
    PercActWindow(i)=sum(PercAct(i:i+WS))/(WS+1);
end

h=figure(1); 
set(gca,'FontSize',16);
hold on;
plot(Trials,QQ,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;

h2=figure(2); 
set(gca,'FontSize',16);
hold on;
plot(Trials,PercAct,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;

h3=figure(3); 
set(gca,'FontSize',16);
hold on;
plot(Trials(1:end-WS),PercActWindow,'o-','Color',[0.5,0,0.5],'linewidth',2,'MarkerFace',[245/255,235/255,235/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;


%% --------------- P1 = 0.65 ---------------
% 1st - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5sec-p1_0_65.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials1=1:1:length(OnsetTrial);
QQ1 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act11=zeros(size(QQ1));
Act21=zeros(size(QQ1));
posA1=find(ActPrev(p,2)==1);
Act11(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act21(posA2) = 1;

% 2nd - 5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5sec-p1_0_65-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials2=1:1:length(OnsetTrial);
QQ2 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act12=zeros(size(QQ2));
Act22=zeros(size(QQ2));
posA=find(ActPrev(p,2)==1);
Act12(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act22(posA2) = 1;

% 3rd - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/7sec-p1_0_65.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials3=1:1:length(OnsetTrial);
QQ3 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act13=zeros(size(QQ3));
Act23=zeros(size(QQ3));
posA1=find(ActPrev(p,2)==1);
Act13(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act23(posA2) = 1;

% 4th - 7 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/7sec-p1_0_65-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials4=1:1:length(OnsetTrial);
QQ4 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act14=zeros(size(QQ4));
Act24=zeros(size(QQ4));
posA1=find(ActPrev(p,2)==1);
Act14(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act24(posA2) = 1;

% 5th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5_5sec-p1_0_65.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials5=1:1:length(OnsetTrial);
QQ5 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act15=zeros(size(QQ5));
Act25=zeros(size(QQ5));
posA1=find(ActPrev(p,2)==1);
Act15(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act25(posA2) = 1;

% 6th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5_5sec-p1_0_65-2.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials6=1:1:length(OnsetTrial);
QQ6 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act16=zeros(size(QQ6));
Act26=zeros(size(QQ6));
posA1=find(ActPrev(p,2)==1);
Act16(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act26(posA2) = 1;

% 7th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5_5sec-p1_0_65-3.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials7=1:1:length(OnsetTrial);
QQ7 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act17=zeros(size(QQ7));
Act27=zeros(size(QQ7));
posA1=find(ActPrev(p,2)==1);
Act17(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act27(posA2) = 1;

% 8th - 5.5 sec
load('/Users/CatiVich/Documents/MATLAB/Matlab programes/Dopamine_plasticity/Dopamine_Plasticity_RewardProbability-model/Plots/p1_0_65/5_5sec-p1_0_65-4.mat')
p=find(abs(ActPrev(:,2))==1);
OnsetTrial=ActPrev(p,1);
Trials8=1:1:length(OnsetTrial);
QQ8 = QQ(floor(OnsetTrial/dt)+1,1)-QQ(floor(OnsetTrial/dt)+1,2);
Act18=zeros(size(QQ8));
Act28=zeros(size(QQ8));
posA1=find(ActPrev(p,2)==1);
Act18(posA1) = 1;
posA2=find(ActPrev(p,2)==-1);
Act28(posA2) = 1;

h11=figure(11); 
set(gca,'FontSize',16);
hold on;
plot(Trials1,QQ1,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials2,QQ2,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials3,QQ3,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials4,QQ4,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials5,QQ5,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials6,QQ6,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials7,QQ7,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
plot(Trials8,QQ8,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;


minT=min(length(Trials1),length(Trials2));
minT=min(minT,length(Trials3));
minT=min(minT,length(Trials4));
minT=min(minT,length(Trials5));
minT=min(minT,length(Trials6));
minT=min(minT,length(Trials7));
minT=min(minT,length(Trials8));

Trials=Trials1(1:minT);
QQ1=QQ1(1:minT); QQ2=QQ2(1:minT); QQ3=QQ3(1:minT); QQ4=QQ4(1:minT); 
QQ5=QQ5(1:minT);  QQ6=QQ6(1:minT); QQ7=QQ7(1:minT); QQ8=QQ8(1:minT); 

Act11 = Act11(1:minT);   Act21 = Act21(1:minT);
Act12 = Act12(1:minT);   Act22 = Act22(1:minT);
Act13 = Act13(1:minT);   Act23 = Act23(1:minT);
Act14 = Act14(1:minT);   Act24 = Act24(1:minT);
Act15 = Act15(1:minT);   Act25 = Act25(1:minT);
Act16 = Act16(1:minT);   Act26 = Act26(1:minT);
Act17 = Act17(1:minT);   Act27 = Act27(1:minT);
Act18 = Act18(1:minT);   Act28 = Act28(1:minT);

QQ=[QQ1, QQ2, QQ3, QQ4, QQ5, QQ6, QQ7, QQ8];

Act1=[Act11, Act12, Act13, Act14, Act15, Act16, Act17, Act18];
Act2=[Act21, Act22, Act23, Act24, Act25, Act26, Act27, Act28];

QQ=mean(QQ,2);
PercAct = sum(Act1,2)./(sum(Act1,2)+sum(Act2,2));

PercActWindow=zeros(length(PercAct)-WS,1);
for i=1:length(PercAct)-WS
    PercActWindow(i)=sum(PercAct(i:i+WS))/(WS+1);
end


h=figure(1); 
set(gca,'FontSize',16);
hold on;
plot(Trials,QQ,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('Q_1 - Q_2');
hold off;


h2=figure(2); 
set(gca,'FontSize',16);
hold on;
plot(Trials,PercAct,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;


h3=figure(3); 
set(gca,'FontSize',16);
hold on;
plot(Trials(1:end-WS),PercActWindow,'ro-','linewidth',2,'MarkerFace',[255/255,242/255,221/255],'MarkerSize',4);
xlabel('Time (ms)');
ylabel('% Choice high value');
hold off;


strplot='./Plots/Qsubjects';
saveas(h,strplot);
saveas(h,strplot,'epsc');

strplot='./Plots/PercentAct1_doubleAverage';
saveas(h3,strplot);
saveas(h3,strplot,'epsc');

strplot='./Plots/DifferentRealizations';
saveas(h11,strplot);
saveas(h11,strplot,'epsc');


