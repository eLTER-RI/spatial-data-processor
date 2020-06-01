###################
packrat::on()

install.packages("tidyverse")
install.packages("rgdal")
install.packages("reticulate")
install.packages("raster")
install.packages("maptools")
install.packages("sf")

###################
# DEIMS API

library(jsonlite)

deims_all_sites <- fromJSON("https://deims.org/api/sites")

# quick and dirty list of countries will do for now, 10 sites to avoid spamming API
countries <- character(0)
deims_active_sites <- list()
for(n in 1:10){
   site_url <- paste0("https://deims.org/api/sites/",deims_all_sites$id$suffix[n])
   detailed_record <- fromJSON(site_url)
   deims_active_sites <- append(deims_active_sites,detailed_record)
   countries <- append(countries,detailed_record$attributes$geographic$country)
}
countries <- unique(countries)
countries
###################
# reticulate

# something isn't right with reticulate, and I'm confident it's to do with the containerisation in datalabs

library(reticulate)

os <- import("os")
py_run_string("x = 10")
py$x

###################
# R raster library

library(raster)
library(maptools)
library(rgdal)

data(wrld_simpl)
uk_map <-  wrld_simpl[wrld_simpl$NAME == "United Kingdom", ] 
plot(uk_map)

pollution_data <- brick("/data/data/nox/agricn2o17.asc")
plot(pollution_data,1)

cairngorms <- readOGR(dsn = "/data/shapefiles/deims/cairngorms",layer = "deims_sites_boundariesPolygon")
cairngorms2 <- spTransform(cairngorms,crs(pollution_data))

nutstest <- readOGR(dsn = "/data/shapefiles/nuts-2016/rstudio-test",layer = "NUTS_RG_01M_2016_3857_LEVL_3")
#lancs3 <- nutstest@data[which(nutstest$NUTS_ID=="UKD44")]
lancs3 <- nutstest[nutstest@data$NUTS_ID=="UKD44",]

result <- crop(pollution_data,cairngorms2)

plot(result)
crs(cairngorms)
crs(pollution_data)
