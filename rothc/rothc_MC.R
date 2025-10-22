##########################################################################################################################################
# INITIALIZATION
##########################################################################################################################################
options(repos = c(CRAN = "https://cran.rstudio.com/"))

get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- "--file="
  script_path <- sub(file_arg, "", args[grep(file_arg, args)])
  if (length(script_path) > 0) return(dirname(normalizePath(script_path)))
  if (!is.null(sys.frames()[[1]]$ofile)) return(dirname(normalizePath(sys.frames()[[1]]$ofile)))
  return(normalizePath(getwd()))
}

script_dir <- get_script_dir()
cat("Working directory detected as:", script_dir, "\n")
setwd(script_dir)

# Read package names from requirements.txt
packages <- readLines(paste0(script_dir,"/requirements.txt"))
new_packages <- packages[!(packages %in% installed.packages()[, "Package"])]
if (length(new_packages) > 0) install.packages(new_packages)

# Sources RothC functions
source("Function_build_RothC_model_with_monthly_C_input.R")
library(SoilR)
library(parallel)

##########################################################################################################################################
# LOAD DATA AND PROCESS
##########################################################################################################################################
file_path <- paste0(dirname(script_dir),"/data/DataRothCRun.csv")
df_run <- read.csv(file_path)

timeindex=data.frame(numbers = 1:length(df_run$T))
Temp=cbind(timeindex, df_run$T); colnames(Temp)[2] <- "Temp"
Precip=cbind(timeindex, df_run$P); colnames(Precip)[2] <- "Precip"
Evp=cbind(timeindex, df_run$Evap); colnames(Evp)[2] <- "Evap"
FYM=cbind(timeindex, df_run$FYM); colnames(FYM)[2] <- "FYM"
AGB=cbind(timeindex, df_run$AGB); colnames(AGB)[2] <- "AGB"

scenario <- unique(df_run$Scenario)

SOC_start=41.3
clay=11.4
DR=1.44
FallIOM <- 0.049*SOC_start^(1.139)
RPM0=(0.1847*SOC_start+0.1555)*(clay+1.275)^(-0.1158)
HUM0=(0.7148*SOC_start+0.5069)*(clay+0.3421)^(0.0184)
BIO0=(0.0140*SOC_start+0.0075)*(clay+8.8473)^(0.0567)
DPM0=SOC_start-(RPM0+HUM0+BIO0+FallIOM); if (DPM0 < 0) DPM0=0
pool_size_baseline=c(DPM0,RPM0,BIO0,HUM0,FallIOM)

soil.thick=30  

years=seq(1:nrow(Temp)) 
fT=fT.RothC(Temp[,2]) 
fW=fW.RothC(P=(Precip[,2]), E=(Evp[,2]), S.Thick = soil.thick, pClay = clay, pE = 0.75, bare = FALSE)$b 
fC=df_run$SoilCover
xi.frame=data.frame(years,rep(fT*fW*fC,length.out=length(years)))

##########################################################################################################################################
# MONTE CARLO ON MODEL PARAMETERS
##########################################################################################################################################

# Uncertainty settings
n_sims <- 1000
K_nominal <- c(10, 0.3, 0.66, 0.02)
K_log_sd <- 0.2              # ~20% multiplicative SD
DR_sd <- 0.2                  # normal SD for DR
pool_sd_frac <- 0.2          # ±20% SD for initial pools


run_mc_param <- function(sim_id) {
  # Define perturbation percentage locally
  perturb_perc <- 0.20  
  
  # Perturb decomposition rate constants (Ks)
  original_Ks <- c(10, 0.3, 0.66, 0.02)
  perturbed_Ks <- original_Ks * runif(length(original_Ks),
                                      min = (1 - perturb_perc),
                                      max = (1 + perturb_perc))
  
  # Perturb DR ratio
  DR_pert <- DR * runif(1, min = (1 - perturb_perc), max = (1 + perturb_perc))
  
  # Perturb initial pools
  perturbed_pools <- pool_size_baseline * runif(length(pool_size_baseline),
                                                min = (1 - perturb_perc),
                                                max = (1 + perturb_perc))
  
  # Run model (positional args only!)
  CtRun_mc <- RothC_Model_mothly_Cinput(
    clay,
    perturbed_Ks,
    perturbed_pools,
    DR_pert,
    xi.frame,
    AGB,
    FYM
  )
  
  return(data.frame(
    sim_id   = sim_id,
    month    = 1:nrow(CtRun_mc),
    SOC      = CtRun_mc$SOC,
    deltaSOC = CtRun_mc$SOC[1] - CtRun_mc$SOC
  ))
}




# Run in parallel
n_cores <- max(1, detectCores() - 1)
cl <- makeCluster(n_cores)
clusterExport(cl, list("RothC_Model_mothly_Cinput","clay","pool_size_baseline","DR","xi.frame","AGB","FYM",
                       "K_nominal","K_log_sd","DR_sd","pool_sd_frac"), envir=environment())
clusterEvalQ(cl, library(SoilR))

mc_results <- parLapply(cl, 1:n_sims, run_mc_param)
stopCluster(cl)

# Combine
mc_df <- do.call(rbind, mc_results)

##########################################################################################################################################
# SAVE OUTPUTS
##########################################################################################################################################
parent_dir <- dirname(script_dir)
results_dir <- file.path(parent_dir, "results")
if (!dir.exists(results_dir)) dir.create(results_dir, recursive = TRUE)


library(dplyr)

# Summarise across simulations for each month
summary_df <- mc_df %>%
  group_by(month) %>%
  summarise(
    SOC_mean = mean(SOC, na.rm = TRUE),
    SOC_sd   = sd(SOC, na.rm = TRUE),
    deltaSOC_mean = mean(deltaSOC, na.rm = TRUE),
    deltaSOC_sd   = sd(deltaSOC, na.rm = TRUE),
    .groups = "drop"
  )

# Save the summary to CSV
write.csv(
  summary_df,
  file.path(results_dir, paste0("SOC_paramMC_summary_", scenario, ".csv")),
  row.names = FALSE
)

cat("Monthly summary of SOC and deltaSOC (mean, sd) saved.\n")


##########################################################################################################################################


