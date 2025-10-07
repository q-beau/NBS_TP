#Modified based on carbon Turnover Function https://rdrr.io/cran/soilassessment/src/R/carbonTurnover.R
#                 and RothCModel Function https://rdrr.io/rforge/SoilR/src/R/RothCModel.R
#by Yue Zhou 04.2024
#################################################################################
# RothC_Model_mothly_Cinput
# brief: Run rothC model with defined monthly changed C input from annual crop and cover crop & FYM
#
# Input:
# clay = clay content 
# Ks: decomposition rate constants  default value: DPM : 10.0 RPM : 0.3 BIO : 0.66 HUM : 0.02 
#      thus c=(10.0,0.3, 0.66,0.02)
# C0: start point Carbon pool, result from spin_up step, length=5  C0=(C_pool_DPM,C_pool_RPM,C_pool_BIO,
#                                                                       C_pool_HUM,C_pool_IOM) 
# DR: fractions that enter the DPM/RPM, with a DR of 1.44, fraction=c((DR)/(DR+1),1-(DR)/(DR+1)) 
# xi: modifying factor based on climate: two column data frame, 
#                                       column 1: time   
#                                       column 2: multiply modifying factor for temperature/moisture/plant retainment
# In: C input from plant residues of annual crops and cover crop: two column data frame, 
#                                       column 1: time   
#                                       column 2: Monthly C input (t/ha)
# FYM: farmyard manure: two column data frame, 
#                                       column 1: time   
#                                       column 2: Monthly FYM (t/ha)
#Output: Monthly changed carbon pool
################################################################################


RothC_Model_mothly_Cinput=function(clay,Ks,C0,DR,xi,In,FYM){
  
  C1=C0[1];C2=C0[2];C3=C0[3];C4=C0[4];C5=C0[5]; #pool size for DPM,RPM,BIO,HUM,IOM 
  Ks1=Ks[1];Ks2=Ks[2];Ks3=Ks[3];Ks4=Ks[4];  #Decomposition rate constant for DPM,RPM,BIO,HUM 
  length=nrow(xi)     #Number of month
  Ct<-as.data.frame(matrix(nrow=length+1,ncol=6)) #create blank data frame
  colnames(Ct)<-c("DPM","RPM","BIO","HUM","IOM","CO2" )
  Ct[1,]<-c(C0,0)
  
  # #Here changedy the Allocation fractions of FYM from (49,49,2) to (72.7,27.3,0) based on Dechow et al.,2019
  # FYM=predict(smooth.spline(seq_along(FYM[,2]), FYM[,2]))$y
  # FYM[FYM < 0] <- 0
  # 
  # In=predict(smooth.spline(seq_along(In[,2]), In[,2]))$y
  # In[In < 0] <- 0
  
  for (i in 1:length) {
    # If an active compartment contains Y t C ha-1, this declines to Y e-abckt t C ha-1 at the end of the month.
    # where a/b/c is the rate modifying factor for temperature/moisture/soil cover; here xi=a*b*c
    # k is the decomposition rate constant for that compartment
    # t is 1 / 12, since k is based on a yearly decomposition rate.
    
    New_DPM<-In[i,2]*(DR/(DR+1))+(FYM[i,2]*0.49)+C1*exp(-Ks1*xi[i,2]/12) #C_input start Decomposition next month
    Diff_DPM<-C1-C1*exp(-Ks1*xi[i,2]/12)
    
    New_RPM<-In[i,2]*(1/(DR+1))+(FYM[i,2]*0.49)+C2*exp(-Ks2*xi[i,2]/12) #input start Decomposition next month
    Diff_RPM<-C2-C2*exp(-Ks2*xi[i,2]/12) 
    
    New_BIO<-C3*exp(-Ks3*xi[i,2]/12) 
    Diff_BIO<-C3-C3*exp(-Ks3*xi[i,2]/12) 
    
    New_HUM<-C4*exp(-Ks4*xi[i,2]/12) +(FYM[i,2]*0.02)#input start Decomposition next month #(FYM[i,2]*0.02)
    Diff_HUM<-C4-C4*exp(-Ks4*xi[i,2]/12)
    
    Diff_ALL<-Diff_DPM+Diff_RPM+Diff_BIO+Diff_HUM
    
    x=1.67*(1.85+1.60*exp(-0.0786*clay))
    C<-x/(x+1) # Proportion that goes to the CO2
    B=0.46/(x+1) # Proportion that goes to the BIO pool
    H=0.54/(x+1) # Proportion that goes to the HUM pool
    
    
    C1<-New_DPM
    C2<-New_RPM
    C3<-New_BIO+Diff_ALL*B
    C4<-New_HUM+Diff_ALL*H
    C5<-C0[5]
    
    CO2<-Diff_ALL*C
    
    Ct[i+1,1:6]<-c(C1,C2,C3,C4,C5,CO2)
    
  }
  Ct$SOC=rowSums(Ct[,1:5])
  return(Ct)
  
}


