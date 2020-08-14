library(dplyr)

nuts_all_levels <- read_csv("shapefiles/zones/nuts2016/all-nuts-2016.csv") %>%
    #filter(CNTR_CODE == "UK") %>% # DELETE THIS LINE FOR ALL COUNTRIES
    mutate(NICENAME = paste(NUTS_ID,NUTS_NAME,sep=" - ")) %>%
    arrange(NICENAME)

write_csv(nuts_all_levels,"shapefiles/zones/nuts2016/cached-nuts-all.csv")
