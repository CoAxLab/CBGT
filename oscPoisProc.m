% Tim Whalen May 2017
% The function oscPoisProc(T, dt, lambda, theta, A, refrac) has been provided
% for you (T, dt and refrac are all in seconds). 
% This generates an oscillating spike train, where 
% theta is the frequency (in Hz) of the underlying oscillation, 
% A is a value between 0 and 1 indicating the amplitude of the oscillation, 
% and refract is the neuronís refractory period
function [ bin ] = oscPoisProc( T, dt, lambda, theta, A, refrac )

times = 0:dt:T;
bin = zeros(length(times),1);
refracbin = ceil(refrac/dt);

i = 1;
while i < length(times)
    p = dt*(lambda +lambda*A * sin(times(i)*theta*2*pi));
    if rand < p
        bin(i) = 1;
        i = i+1+refracbin;
    else
        i = i+1;
    end
end

end