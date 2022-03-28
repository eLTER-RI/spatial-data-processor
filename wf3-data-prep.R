# From the original FLUXNET/ICOS format, the full workflow to get to the eLTER data format is as follows:
#
# 1: insert any missing variables and _QC columns as NAs
# 2: rename TIMESTAMP > TIME and format as ISO timestamp
# 3: merge observations (i.e. X + X_QC) to single columns
# 4: pivot_longer all columns to VARIABLE and VALUE
# 5: separate VALUE back out into VALUE and FLAGQUA
# 6: insert fixed columns: SITE_CODE, STATION_CODE, LEVEL, and FLAGSTA
# 7: insert UNIT column, derived from VARIABLE
# 8: reorder the columns
#
# this file prepares raw data files with steps 1 and 2, as I can't figure out how to automate them properly in R
# it also removes columns which aren't selectable in the interface for performance reasons
library(readr)
library(tidyr)
library(dplyr)
library(stringr)
library(lubridate)


# constants - make sure in sync with app.R
unit_mappings <- c(
    "TA_F_MDS" = "deg C",
    "SW_IN_F_MDS" = "W m-2",
    "VPD_F_MDS" = "hPa",
    "P_F" = "mm",
    "WS_F" = "m s-1",
    "SWC_F_MDS_1" = "%",
    "LE_F_MDS" = "W m-2",
    "NEE_VUT_REF" = "µmolCO2 m-2 s-1",
    "NEE_VUT_USTAR50" = "µmolCO2 m-2 s-1",
    "RECO_NT_VUT_REF" = "µmolCO2 m-2 s-1",
    "RECO_NT_VUT_USTAR50" = "µmolCO2 m-2 s-1",
    "GPP_NT_VUT_REF" = "µmolCO2 m-2 s-1",
    "GPP_NT_VUT_USTAR50" = "µmolCO2 m-2 s-1"
)

vars <- names(unit_mappings)
vars_qc <- sub("$","_QC",vars)

# inputs
filenames <- c(
    "input/fluxnet/AT-Neu.csv",
    "input/fluxnet/DE-RuR.csv",
    "input/fluxnet/FI-Hyy.csv",
    "input/fluxnet/IT-Tor.csv",
    "input/icos/DE-RuR.csv",
    "input/icos/FI-Hyy.csv",
    "input/icos/IT-Tor.csv"
)


# convert each file
for(x in 1:7){
    # load data, parsing datetime correctly
    data <- read_csv(filenames[x], col_types=list(col_date("%Y%m%d")), show_col_types=TRUE, na="-9999")

    # check which variables and _QC columns are missing
    cols <- colnames(data)
    missing_vars <- vars[!(vars %in% cols)]
    missing_vars_qc <- vars_qc[!(vars_qc %in% cols)]

    # add missing columns filled with NA
    data[c(missing_vars,missing_vars_qc)] <- NA

    # restrict data to just 27 needed columns
    data <- data[c("TIMESTAMP",vars,vars_qc)]
    data <- rename(data,"TIME"="TIMESTAMP")

    # write data back to input file
    write_csv(data,filenames[x],append = FALSE)
}
