### environment + package management
packrat::on()

library(shiny)
library(tidyverse)
library(raster)
library(rgdal)
library(reticulate)
#library(lubridate)
#library(jsonlite)
#library(leaflet) for maps

### preamble
# data
#data_placeholders <- list("Zöbelboden SOS","NOx data","Census data")
#cdn_austria <- read_csv("/data/data/cdn/lter_austria_1568635867427_lter_at_lter_eu_at_022_atsonam15411_tempmean_air_1.csv")
pollution_data <- brick("/data/data/nox/agricn2o17.asc")

# NUTS 2016 definitions
# this is a static set of metadata on NUTS regions generated from Python
# under the assumption that reticulate will pass to Python actual processing tasks.
nuts_all_levels <- read_csv("cached-data/uk/uk-all.csv")
nuts_level0_names <- filter(nuts_all_levels, LEVL_CODE == 0)$NICENAME
nuts_level1_names <- filter(nuts_all_levels, LEVL_CODE == 1)$NICENAME
nuts_level2_names <- filter(nuts_all_levels, LEVL_CODE == 2)$NICENAME
nuts_level3_names <- filter(nuts_all_levels, LEVL_CODE == 3)$NICENAME
level_choices <- list("0","1","2","3")

# this section does some direct manipulation of NUTS shapefiles, in violation of the previous
# NUTS section. I acknowledge this is strange, but for now the architecture of this whole labs
# solution is yet to be finalised, so the split-brain approach doesn't need resolving yet.
#
# read shapefiles...
nuts0 <- readOGR(dsn = "/data/shapefiles/nuts-2016/rstudio/l0",layer = "NUTS_RG_01M_2016_3857_LEVL_0")
nuts1 <- readOGR(dsn = "/data/shapefiles/nuts-2016/rstudio/l1",layer = "NUTS_RG_01M_2016_3857_LEVL_1")
nuts2 <- readOGR(dsn = "/data/shapefiles/nuts-2016/rstudio/l2",layer = "NUTS_RG_01M_2016_3857_LEVL_2")
nuts3 <- readOGR(dsn = "/data/shapefiles/nuts-2016/rstudio/l3",layer = "NUTS_RG_01M_2016_3857_LEVL_3")

# ...filter UK only temporarily...
nuts0 <- nuts0[nuts0@data$CNTR_CODE=="UK",]
nuts1 <- nuts1[nuts1@data$CNTR_CODE=="UK",]
nuts2 <- nuts2[nuts2@data$CNTR_CODE=="UK",]
nuts3 <- nuts3[nuts3@data$CNTR_CODE=="UK",]

# ...and convert to CRS of example data, i.e. pollution data
nuts0 <- spTransform(nuts0,crs(pollution_data))
nuts1 <- spTransform(nuts1,crs(pollution_data))
nuts2 <- spTransform(nuts2,crs(pollution_data))
nuts3 <- spTransform(nuts3,crs(pollution_data))

# DEIMS definitions
deims_LTSER_choices <- list("LTSER Zone Atelier Alpes","Braila Islands","Cairngorms National Park","Doñana LTSER","LTSER Platform Eisenwurzen")
#deims_LTSER_urls <- list("https://deims.org/79d6c1df-570f-455f-a929-6cfe5c4ca1e9",
#                         "https://deims.org/d4854af8-9d9f-42a2-af96-f1ed9cb25712",
#                         "https://deims.org/1b94503d-285c-4028-a3db-bc78e31dea07",
#                         "https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2",
#                         "https://deims.org/d0a8da18-0881-4ebe-bccf-bc4cb4e25701")

# read DEIMS shapefile manually for now - will retrieve from API later or store all locally for performance
cairngorms <- readOGR(dsn = "/data/shapefiles/deims/cairngorms",layer = "deims_sites_boundariesPolygon")
cairngorms <- spTransform(cairngorms,crs(pollution_data))

# As described above, for now we limit DEIMS sites to the five LTSER test platforms
# This code can be activated later to retrive arbitrary sites from DEIMS on the fly

## get sites from DEIMS as json
#deims_url <- "https://deims.org/api/sites"
#deims_all_sites <- fromJSON(deims_url)

# quick and dirty list of countries will do for now, 10 sites to avoid spamming API
#countries <- character(0)
#deims_active_sites <- list()
#for(n in 1:10){
#    site_url <- paste0("https://deims.org/api/sites/",deims_all_sites$id$suffix[n])
#    detailed_record <- fromJSON(site_url)
#    deims_active_sites <- append(deims_active_sites,detailed_record)
#    countries <- append(countries,detailed_record$attributes$geographic$country)
#}
#countries <- unique(countries)
#countries

# reticulate
use_python('/usr/bin/python3')

### shiny code
ui <- fluidPage(
    titlePanel("Data cookie-cutting"),
    sidebarLayout(
        sidebarPanel(
            helpText("1: select workflow"),
            selectInput(
                inputId = "active_workflow",
                label = "Select a workflow",
                choices = c("Mask gridded dataset","Aggregate non-gridded dataset"),
                multiple = FALSE
            ),
            # first workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                helpText("2: select data"),
                selectInput(
                    inputId = "active_data",
                    label = "Choose data",
                    choices = c("NOx data"),
                    multiple = FALSE
                ),
                fileInput(
                    inputId = "user_data",
                    label = "Alternatively, upload your data here",
                    multiple = FALSE,
                    accept = c("text/csv",
                               "text/comma-separated-values,text/plain",
                               ".csv")
                ),
                
                # This section can be reintroduced if/when date filtering becomes relevant 
                #helpText("3: filter by date and region"),
                #dateRangeInput(
                #    inputId = "date_filter",
                #    label = "Select dates to include"
                #),
                helpText("3: filter by either DEIMS site boundaries or EU NUTS levels 0-3"),
                # toggle NUTS or DEIMS
                radioButtons(
                    inputId = "region_toggle",
                    label = "Choose filter type",
                    choices = c("DEIMS","NUTS")
                ),
                # NUTS
                conditionalPanel(
                    condition = "input.region_toggle === 'NUTS'",
                    selectInput(
                        inputId = "nutslevel_filter",
                        label = "NUTS level",
                        choices = level_choices
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '0'",
                        selectInput(
                            inputId = "nuts_region_0_filter",
                            label = "NUTS region",
                            choices = nuts_level0_names,
                            multiple = FALSE
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '1'",
                        selectInput(
                            inputId = "nuts_region_1_filter",
                            label = "NUTS region",
                            choices = nuts_level1_names,
                            multiple = FALSE
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '2'",
                        selectInput(
                            inputId = "nuts_region_2_filter",
                            label = "NUTS region",
                            choices = nuts_level2_names,
                            multiple = FALSE
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '3'",
                        selectInput(
                            inputId = "nuts_region_3_filter",
                            label = "NUTS region",
                            choices = nuts_level3_names,
                            multiple = FALSE
                        )
                    )
                ),
                # DEIMS
                conditionalPanel(
                    condition = "input.region_toggle === 'DEIMS'",
                    selectInput(
                        inputId = "deims_filter",
                        label = "Deims site (currently always maps Cairngorms as other sites don't fit example data)",
                        choices = deims_LTSER_choices,
                        selected = deims_LTSER_choices[3],
                        multiple = FALSE
                    )
                )
            ),
            # second workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                helpText("2: testing")
            )
        ),
        mainPanel(
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                plotOutput(outputId = "crop_preview")
            ),
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                textOutput(outputId = "reticulate_test")
            ),
            actionButton(
                inputId = "download",
                label = "Download data"
            )
        )
    )
)

server <- function(input,output){
    output$crop_preview <- renderPlot({
        #dplyr::filter(as.Date(TIME) >= as.Date(input$daterange1[1]) &
        #              as.Date(TIME) <= as.Date(input$daterange1[2]) )
        #plot(cdn_austria$DATE,cdn_austria$VALUE,type="l")
        if(input$region_toggle == "DEIMS"){
            plot(crop(pollution_data,cairngorms),axes=FALSE)
        }
        if(input$region_toggle == "NUTS"){
            if(input$nutslevel_filter == "0"){
                selected_region_id <- nuts_all_levels[nuts_all_levels$NICENAME==input$nuts_region_0_filter,]$NUTS_ID
                selected_region <- nuts0[nuts0@data$NUTS_ID==selected_region_id,]
                plot(crop(pollution_data,selected_region),axes=FALSE)
            }
            if(input$nutslevel_filter == "1"){
                selected_region_id <- nuts_all_levels[nuts_all_levels$NICENAME==input$nuts_region_1_filter,]$NUTS_ID
                selected_region <- nuts1[nuts1@data$NUTS_ID==selected_region_id,]
                plot(crop(pollution_data,selected_region),axes=FALSE)
            }
            if(input$nutslevel_filter == "2"){
                selected_region_id <- nuts_all_levels[nuts_all_levels$NICENAME==input$nuts_region_2_filter,]$NUTS_ID
                selected_region <- nuts2[nuts2@data$NUTS_ID==selected_region_id,]
                plot(crop(pollution_data,selected_region),axes=FALSE)
            }
            if(input$nutslevel_filter == "3"){
                selected_region_id <- nuts_all_levels[nuts_all_levels$NICENAME==input$nuts_region_3_filter,]$NUTS_ID
                selected_region <- nuts3[nuts3@data$NUTS_ID==selected_region_id,]
                plot(crop(pollution_data,selected_region),axes=FALSE)
            }
        }
    })
    output$reticulate_test <- rendertext({
        py_run_string("x = 'foo'")
        py$x
    })
}

shinyApp(ui,server)