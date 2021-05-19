### environment + package management
packrat::on()

library(shiny)
library(reticulate)
library(dplyr)
library(readr)
library(readxl)

# set global shiny options
# use powers of 1024 for kilo/Mega/...bytes
options(shiny.maxRequestSize=2*1024^3)

### preamble

# NUTS 2016 definitions
# read static metadata on NUTS regions generated in Python
nuts_all_levels <- read_csv("shapefiles/zones/nuts2016/cached-nuts-all.csv")
nuts_level0_names <- filter(nuts_all_levels, LEVL_CODE == 0)$NICENAME
nuts_level1_names <- filter(nuts_all_levels, LEVL_CODE == 1)$NICENAME
nuts_level2_names <- filter(nuts_all_levels, LEVL_CODE == 2)$NICENAME
nuts_level3_names <- filter(nuts_all_levels, LEVL_CODE == 3)$NICENAME
level_choices <- c("0","1","2","3")

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
                fileInput(
                    inputId = "raster_data",
                    label = "Upload your data here",
                    multiple = FALSE,
                    accept = c("image/tiff")
                ),
                uiOutput("wf1_title"),
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
                        choices = deims_site_name_mappings,
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
                    label = "Upload your data here",
                    multiple = FALSE,
                    accept = c(".xls",
                               ".xlsx",
                               ".csv")
                ),
                # reactive inputs after data uploaded
                uiOutput("wf2_user_input_sheets"),
                uiOutput("wf2_columns"),
                helpText("3: select DEIMS site and data grouping"),
                selectInput(
                    inputId = "comparison_site",
                    label = "To which site boundaries should the data be trimmed?",
                    choices = deims_site_name_mappings,
                    multiple = FALSE
                ),
                uiOutput("wf2_site_zone_picker")
            )
        ),
        mainPanel(
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                imageOutput(outputId = "raster_plot"),
                downloadButton(
                    outputId = "raster_download",
                    label = "Download data"
                ),
                downloadButton(
                    outputId = "raster_plot_download",
                    label = "Download plot"
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
    # called after user has uploaded data
    raster_output <- reactive({
        # process user upload, taking its validity for granted
        dataset <- input$raster_data$datapath
        plot_title <- input$raster_data_name
        
        if(input$region_toggle == "DEIMS"){
            cropRasterDataset(dataset,"deims",input$deims_filter,plot_title)
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
            cropRasterDataset(dataset,"nuts",crop_id,plot_title)
        }
    })
    output$wf1_title <- renderUI({
        if(is.null(input$raster_data)){
            # pass
        }
        else{
            textInput(
                inputId = "raster_data_name",
                label = "What is this dataset called?",
                value = "Custom"
            )
        }
    })
    
    # wf2
    # populates available zones based on site by reading python metadata
    output$wf2_site_zone_picker <- renderUI({
        selectInput(
            inputId = "data_grouping",
            label = "This data is grouped by...",
            choices = deims_site_zone_options$input$comparison_site,
            multiple = FALSE
            )
    })
    # reads input file, if it exists, and "returns" tibble
    wf2_user_input <- reactive({
        if(is.null(input$tabular_data)){
            # pass
        }
        else{
            if(endsWith(input$tabular_data$datapath,"csv")){
                read_csv(input$tabular_data$datapath)
            }
            else{
                read_excel(input$tabular_data$datapath,input$wf2_sheet_key)
            }
        }
    })
    # creates sheet select box if Excel uploaded
    output$wf2_user_input_sheets <- renderUI({
        if(is.null(input$tabular_data)){
            # pass
        }
        else{
            if(endsWith(input$tabular_data$datapath,"csv")){
                # pass
            }
            else{
                selectInput(
                    inputId = "wf2_sheet_key",
                    label = "Choose sheet to use",
                    choices = excel_sheets(input$tabular_data$datapath),
                    multiple = FALSE
                )
            }
        }
    })
    # creates column selection based on upload + Excel sheet
    output$wf2_columns <- renderUI({
        if(is.null(input$tabular_data)){
            # pass
        }
        else{
            list(selectInput(
                inputId = "plot_key",
                label = "Choose column to plot",
                # [-1] drops the first column, i.e. the ID
                choices = names(wf2_user_input())[-1],
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
    # combines all inputs and returns tibble for download
    tabular_output <- reactive({
        if(is.null(input$tabular_data)){
            # pass
        }
        else{
            aggregateTabularDataset(wf2_user_input(),input$comparison_site,input$data_grouping,input$plot_key,input$tabular_data_name)
        }
    })
    
    # outputs
    output$raster_download <- downloadHandler(
        filename = "cropped-data.tif",
        content = function(file){
            file.copy("/tmp/masked.tif",file)
        })
    
    output$raster_plot <- renderImage({
        if(is.null(input$raster_data)){
            list(src="eLTER-logo.png",alt="eLTER logo",width=645,height=233)
        }
        else{
            replot <- raster_output()
            list(src="/tmp/crop.png",alt="Plot of cropped data")
        }
    }, deleteFile = FALSE)
    
    output$raster_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/crop.png",file)
        })
    
    output$tabular_download <- downloadHandler(
        filename = "aggregated-data.csv",
        content = function(file){
            write_csv(tabular_output(),file)
        })
    
    output$tabular_plot <- renderImage({
        if(is.null(input$tabular_data)){
            list(src="eLTER-logo.png",alt="eLTER logo",width=645,height=233)
        }
        else{
            replot <- tabular_output()
            list(src="/tmp/plot.png",alt="Plot of aggregated data")            
        }
    }, deleteFile = FALSE)
    
    output$tabular_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/plot.png",file)
        })
}

shinyApp(ui,server)
