nuts_all_levels <- read_csv("all-nuts-2016.csv") %>%
    filter(CNTR_CODE == "UK") %>% # DELETE THIS LINE FOR ALL COUNTRIES
    mutate(NICENAME = paste(NUTS_ID,NUTS_NAME,sep=" - ")) %>%
    arrange(NICENAME)

write_csv(nuts_all_levels,"uk/uk-all.csv")
