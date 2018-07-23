function synch=PopulationSynchrony(V)

%V=V(time,neurons)
avgVi = mean(V,2); % average over neurons
Vbar=mean(avgVi,1); % average over time
synch2=mean((avgVi-Vbar).^2);
synch=sqrt(synch2);