###################
packrat::on()

install.packages("tidyverse")
install.packages("reticulate")
install.packages("rgdal")
install.packages("raster")
install.packages("lubridate")
install.packages("maptools")
install.packages("sf")
install.packages("jsonlite")
install.packages("leaflet")

###################
# DEIMS API

library(jsonlite)

deims_all_sites <- fromJSON("https://deims.org/api/sites")

deims_LTSER_urls <- list("https://deims.org/79d6c1df-570f-455f-a929-6cfe5c4ca1e9",
                         "https://deims.org/d4854af8-9d9f-42a2-af96-f1ed9cb25712",
                         "https://deims.org/1b94503d-285c-4028-a3db-bc78e31dea07",
                         "https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2",
                         "https://deims.org/d0a8da18-0881-4ebe-bccf-bc4cb4e25701")


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
