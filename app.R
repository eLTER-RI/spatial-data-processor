### environment + package management
packrat::on()

library(shiny)
library(reticulate)
library(dplyr)
library(readr)

### preamble
# data
test_births <- read_csv("data/births-cleaned.csv")

# NUTS 2016 definitions
# read static metadata on NUTS regions generated in Python
nuts_all_levels <- read_csv("shapefiles/zones/nuts2016/cached-nuts-all.csv")
nuts_level0_names <- filter(nuts_all_levels, LEVL_CODE == 0)$NICENAME
nuts_level1_names <- filter(nuts_all_levels, LEVL_CODE == 1)$NICENAME
nuts_level2_names <- filter(nuts_all_levels, LEVL_CODE == 2)$NICENAME
nuts_level3_names <- filter(nuts_all_levels, LEVL_CODE == 3)$NICENAME
level_choices <- c("0","1","2","3")

# DEIMS definitions
deims_LTSER_choices <- c(
    "LTSER Zone Atelier Alpes" = "aa",
    "Braila Islands" = "bi",
    "Cairngorms National Park" = "cg",
    "Doñana LTSER" = "dn",
    "LTSER Platform Eisenwurzen" = "ew")

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
                # wf1 input 1
                selectInput(
                    inputId = "active_raster_data",
                    label = "Choose data",
                    choices = c("NOx data"),
                    multiple = FALSE
                ),
                fileInput(
                    inputId = "raster_data",
                    label = "Alternatively, upload your data here",
                    multiple = FALSE,
                    accept = c("image/tiff")
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
                            multiple = FALSE,
                            selected = "UK - UNITED KINGDOM"
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '1'",
                        selectInput(
                            inputId = "nuts_region_1_filter",
                            label = "NUTS region",
                            choices = nuts_level1_names,
                            multiple = FALSE,
                            selected = "UKD - NORTH WEST (ENGLAND)"
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '2'",
                        selectInput(
                            inputId = "nuts_region_2_filter",
                            label = "NUTS region",
                            choices = nuts_level2_names,
                            multiple = FALSE,
                            selected = "UKD4 - Lancashire"
                        )
                    ),
                    conditionalPanel(
                        condition = "input.nutslevel_filter === '3'",
                        selectInput(
                            inputId = "nuts_region_3_filter",
                            label = "NUTS region",
                            choices = nuts_level3_names,
                            multiple = FALSE,
                            selected = "UKD44 - Lancaster and Wyre"
                        )
                    )
                ),
                # DEIMS
                conditionalPanel(
                    condition = "input.region_toggle === 'DEIMS'",
                    selectInput(
                        inputId = "deims_filter",
                        label = "Deims site",
                        choices = deims_LTSER_choices,
                        selected = "cg",
                        multiple = FALSE
                    )
                )
            ),
            # second workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                helpText("2: select data and active column"),
                fileInput(
                    inputId = "tabular_data",
                    label = "Alternatively, upload your data here",
                    multiple = FALSE,
                    accept = c("text/csv",
                               "text/comma-separated-values,text/plain",
                               ".csv")
                ),
                uiOutput("wf2_columns"),
                helpText("3: describe data and choose comparison site"),
                selectInput(
                    inputId = "data_grouping",
                    label = "This data is grouped by...",
                    choices = c(
                        "Scottish data zones" = "dz",
                        "NUTS 0 regions" = "n0",
                        "NUTS 1 regions" = "n1",
                        "NUTS 2 regions" = "n2",
                        "NUTS 3 regions" = "n3"
                        ),
                    multiple = FALSE
                ),
                selectInput(
                    inputId = "comparison_site",
                    label = "To which site boundaries should the data be trimmed?",
                    choices = deims_LTSER_choices,
                    selected = "cg",
                    multiple = FALSE
                )
            )
        ),
        mainPanel(
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                imageOutput(outputId = "raster_plot"),
                downloadButton(
                    outputId = "raster_download",
                    label = "Download data"
                )
            ),
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                imageOutput(outputId = "tabular_plot"),
                downloadButton(
                    outputId = "tabular_download",
                    label = "Download data"
                ),
                downloadButton(
                    outputId = "tabular_plot_download",
                    label = "Download plot"
                )
            )
        )
    )
)

server <- function(input,output){
    # reactive intermediates
    # wf1
    raster_output <- reactive({
        user_input <- input$raster_data
        {
            if(is.null(user_input)){
                dataset <- "nox"
                }
            else{
                dataset <- user_input$datapath
                }
        }
        if(input$region_toggle == "DEIMS"){
            cropRasterDataset(dataset,"deims",input$deims_filter)
        }
        else{
            if(input$nutslevel_filter == "0"){
                crop_id <- filter(nuts_all_levels, NICENAME == input$nuts_region_0_filter)$NUTS_ID
            }
            if(input$nutslevel_filter == "1"){
                crop_id <- filter(nuts_all_levels, NICENAME == input$nuts_region_1_filter)$NUTS_ID
            }
            if(input$nutslevel_filter == "2"){
                crop_id <- filter(nuts_all_levels, NICENAME == input$nuts_region_2_filter)$NUTS_ID
            }
            if(input$nutslevel_filter == "3"){
                crop_id <- filter(nuts_all_levels, NICENAME == input$nuts_region_3_filter)$NUTS_ID
            }
            cropRasterDataset(dataset,"nuts",crop_id)
        }
    })
    
    # wf2
    tabular_output <- reactive({
        user_input <- input$tabular_data
        if(is.null(user_input)){
            aggregateTabularDataset(test_births,input$comparison_site,input$data_grouping,input$plot_key,"Births")
        }
        else{
            infile <- read_csv(user_input$datapath)
            aggregateTabularDataset(infile,input$comparison_site,input$data_grouping,input$plot_key,input$tabular_data_name)
        }
    })
    output$wf2_columns <- renderUI({
        user_input <- input$tabular_data
        if(is.null(user_input)){
            selectInput(
                inputId = "plot_key",
                label = "Choose column to plot",
                # [-1] drops the first column, i.e. the ID
                choices = names(test_births)[-1],
                multiple = FALSE
            )
        }
        else{
            infile <- read_csv(user_input$datapath)
            list(selectInput(
                inputId = "plot_key",
                label = "Choose column to plot",
                # [-1] drops the first column, i.e. the ID
                choices = names(infile)[-1],
                multiple = FALSE
            ),
            textInput(
                inputId = "tabular_data_name",
                label = "What is this dataset called?",
                value = "Custom"
            )
            )
        }
    })
    
    # outputs
    output$raster_download <- downloadHandler(
        filename = "cropped-data.tif",
        content = function(file){
            file.copy("/tmp/masked.tif",file)
        })
    
    output$raster_plot <- renderImage({
        replot <- raster_output()
        list(src="/tmp/crop-preview.png",alt="Plot of cropped data")
    }, deleteFile = FALSE)
    
    output$tabular_download <- downloadHandler(
        filename = "aggregated-data.csv",
        content = function(file){
            write_csv(tabular_output(),file)
        })
    
    output$tabular_plot <- renderImage({
        replot <- tabular_output()
        list(src="/tmp/plot.png",alt="Plot of aggregated data")
    }, deleteFile = FALSE)
    
    output$tabular_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/plot.png",file)
        })
}

shinyApp(ui,server)