### environment + package management
packrat::on()

library(shiny)
library(tidyverse)
library(reticulate)

### preamble
# data
# cached-data/...

# NUTS 2016 definitions
# read static metadata on NUTS regions generated in Python
nuts_all_levels <- read_csv("shapefiles/zones/nuts2016/uk-all.csv")
nuts_level0_names <- filter(nuts_all_levels, LEVL_CODE == 0)$NICENAME
nuts_level1_names <- filter(nuts_all_levels, LEVL_CODE == 1)$NICENAME
nuts_level2_names <- filter(nuts_all_levels, LEVL_CODE == 2)$NICENAME
nuts_level3_names <- filter(nuts_all_levels, LEVL_CODE == 3)$NICENAME
level_choices <- list("0","1","2","3")

# DEIMS definitions
deims_LTSER_choices <- list("LTSER Zone Atelier Alpes","Braila Islands","Cairngorms National Park","Doñana LTSER","LTSER Platform Eisenwurzen")

# reticulate
use_virtualenv("./reticulate-venv")
source_python("analyse.py")

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
                helpText("2: select data"),
                selectInput(
                    inputId = "active_data",
                    label = "Choose data",
                    choices = c("Scottish births"),
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
                helpText("3: describe data and choose comparison site"),
                selectInput(
                    inputId = "data_grouping",
                    label = "This data is grouped by...",
                    choices = c(
                        "Scottish data zones",
                        "NUTS 0 regions",
                        "NUTS 1 regions",
                        "NUTS 2 regions",
                        "NUTS 3 regions"
                        ),
                    multiple = FALSE
                ),
                selectInput(
                    inputId = "comparison_site",
                    label = "To which site boundaries should the data be trimmed?",
                    choices = deims_LTSER_choices,
                    multiple = FALSE
                )
            )
        ),
        mainPanel(
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                plotOutput(outputId = "crop_placeholder")
            ),
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                imageOutput(outputId = "reticulate_test")
            ),
            actionButton(
                inputId = "download",
                label = "Download data"
            )
        )
    )
)

server <- function(input,output){
    output$crop_placeholder <- renderPlot({
        if(input$region_toggle == "DEIMS"){
            plot(c(0,1,2,3,4),c(1,0,1,0,1),type="l")
        }
        if(input$region_toggle == "NUTS"){
            plot(c(0,1,2,3,4),c(0,1,0,1,0),type="l")
        }
    })
    output$reticulate_test <- renderImage({
        source_python("dummyplot.py")
        
        #list(src=png(py$data),contenttype="image/png;base64",width=100,height=100,alt="alt text here")
        #source_python("testplot.py")
        list(src="/tmp/newtest1.png",width=400,height=400,alt="alt text here")
    })
}

shinyApp(ui,server)