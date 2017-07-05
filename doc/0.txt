# Adjusting the time step

  


To adjust the time step, there's 3 values to adjust  


  


dt = 0.1 -&gt; 0.2  


delayindt = 2 -&gt; 1  


STEPSFORSAVINGFREQS 10 -&gt; 5  


  


As initially written, there was a bug in the SaveSpikes() function. The code to increment the spike buffer pointer (currentpt) was placed inside of the population loop instead of after the end of it. 

  


if (currentpt &lt; buffersize - 1)   
currentpt++;   
else   
currentpt = 0;  


  


This caused the program to edit the buffer in a wrapping diagonal pattern instead of the correct way of one column at a time, left to right. It turns out that this works fine... as long as the buffersize and number of populations is coprime (greatest common factor of 1). When the time window was 20ms and dt was 0.1ms, then the buffersize was 20/0.2 -&gt; 199 due to flooring the floating point number. This value is prime, so the code worked fine. When dt was changed to 0.2, the buffersize was 20/0.2-&gt;99\. Since the number of populations was 15, and GCF(99,15) = 3, then only 1/3rd of the buffer was used, which resulted in all frequencies being divided by 3 and less smooth data.  


  


Another minor bug was in the line  


buffersize = (int)(TIMEWINDOWFORFREQ / dt);  


which, due to floating point and the cast rounding down, resulting in 1 fewer bins than needed (199 instead of 200, and 99 instead of 100). I have changed this line to:   


buffersize = (int)(TIMEWINDOWFORFREQ / dt + 0.5);  

