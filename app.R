# environment + package management
packrat::on()

library(shiny)
library(reticulate)
library(readr)
library(readxl)
library(tidyr)
library(dplyr)
library(stringr)
library(lubridate)

# set global shiny options
# use powers of 1024 for kilo/Mega/...bytes
options(shiny.maxRequestSize=2*1024^3)

# reticulate
use_virtualenv("./reticulate-venv")
source_python("analyse.py")
source_python("shapefiles/scripts/shapefile-generator.py")
source_python("shapefiles/scripts/directoryparse.py")
source_python("interface.py")

# data
wf3_unit_mappings <- c(
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

wf3_deims_id <- c(
    'AT-Neu' = 'https://deims.org/324f92a3-5940-4790-9738-5aa21992511c',
    'DE-RuR' = 'https://deims.org/356417de-5a3c-429d-82c1-08a4e924ab3b',
    'FI-Hyy' = 'https://deims.org/663dac80-211d-4c19-a356-04ee0da0f0eb',
    'IT-Tor' = 'https://deims.org/4312983f-c36a-4b46-b10a-a9dea2172849'
)

# helper function - see wf3-data-prep.R for more details
convertToElterFormat <- function(dataset,deims_id,station_code,variable_names){
    # step 3: temporarily group variables with their _QC
    for(x in 1:length(variable_names)){
        colname <- variable_names[x]
        qc_colname <- sub("$","_QC",colname)
        dataset <- dataset %>% unite({{colname}},colname,qc_colname)
    }

    # steps 4-8
    dataset <- dataset %>%
        # step 4: pivot from columns to rows
        pivot_longer(variable_names,"VARIABLE","VALUE") %>%
        # step 5: split _QC back out to FLAGQUA
        separate(value,c("VALUE","FLAGQUA"),sep="_",convert=TRUE) %>%
        # step 6: add hardcoded columns
        mutate(SITE_CODE = deims_id) %>%
        mutate(STATION_CODE = station_code) %>%
        mutate(LEVEL = NA) %>%
        mutate(FLAGSTA = NA) %>%
        # step 7: create UNIT column based on VARIABLE
        mutate(UNIT=str_replace_all(VARIABLE,wf3_unit_mappings)) %>%
        # step 8: reorder
        relocate(SITE_CODE,STATION_CODE,VARIABLE,LEVEL,TIME,VALUE,UNIT,FLAGQUA,FLAGSTA)

    return(dataset)
}

# shiny
ui <- fluidPage(
    titlePanel("Data cookie-cutter"),
    sidebarLayout(
        sidebarPanel(
            # common to both workflows
            helpText("1: select workflow"),
            selectInput(
                inputId = "active_workflow",
                label = "Workflow",
                choices = c("Mask gridded dataset","Aggregate non-gridded dataset","FLUXNET/ICOS (experimental)"),
                multiple = FALSE
            ),
            # first workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                helpText("2: select and describe data"),
                uiOutput("wf1_files"),
                fileInput(
                    inputId = "wf1_upload",
                    label = "Upload new data",
                    multiple = FALSE,
                    accept = c("image/tiff")
                ),
                uiOutput("wf1_title")
            ),
            # second workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                helpText("2: select and describe data"),
                uiOutput("wf2_files"),
                fileInput(
                    inputId = "wf2_upload",
                    label = "Upload new data",
                    multiple = FALSE,
                    accept = c(".xls",
                               ".xlsx",
                               ".csv")
                ),
                uiOutput("wf2_user_input_sheets"),
                uiOutput("wf2_columns"),
                uiOutput("wf2_site_zone_picker")
            ),
            # third workflow
            conditionalPanel(
                condition = "input.active_workflow === 'FLUXNET/ICOS (experimental)'",
                helpText("2: select data source"),
                selectInput(
                    inputId = "wf3_data_source",
                    label = "Data",
                    choices = c("FLUXNET" = "fluxnet","ICOS" = "icos")
                ),
                helpText("3: select variable"),
                selectInput(
                    inputId = "wf3_variable",
                    label = "Variable",
                    choices = c(
                        "TA_F_MDS",
                        "SW_IN_F_MDS",
                        "VPD_F_MDS",
                        "P_F",
                        "WS_F",
                        "SWC_F_MDS_1",
                        "LE_F_MDS",
                        "NEE_VUT_REF",
                        "NEE_VUT_USTAR50",
                        "RECO_NT_VUT_REF",
                        "RECO_NT_VUT_USTAR50",
                        "GPP_NT_VUT_REF",
                        "GPP_NT_VUT_USTAR50"
                    ),
                    multiple = TRUE
                )
            ),
            conditionalPanel(
                condition = "input.active_workflow !== 'FLUXNET/ICOS (experimental)'",
                # common to first two workflows
                helpText("3: select DEIMS site to cookie-cut"),
                uiOutput("deims_site_picker"),
                textInput("new_deims_ID","Add a new site by its DEIMS ID"),
                actionButton("new_site", "Add")
            ),
            conditionalPanel(
                condition = "input.active_workflow === 'FLUXNET/ICOS (experimental)'",
                # common to first two workflows
                helpText("3: select LTER site to cookie-cut"),
                selectInput(
                    inputId = "wf3_site",
                    label = "eLTER site",
                    choices = c(
                        "Stubai" = "AT-Neu",
                        "Rollesbroich" = "DE-RuR",
                        "Hyytiälä" = "FI-Hyy",
                        "Torgnon Larch Forest" = "IT-Tor"
                    ),
                    multiple = FALSE
                )
            )
        ),
        mainPanel(
            # first workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Mask gridded dataset'",
                imageOutput(outputId = "wf1_plot"),
                uiOutput("wf1_output_options"),
                uiOutput("wf1_download_options")
            ),
            # second workflow
            conditionalPanel(
                condition = "input.active_workflow === 'Aggregate non-gridded dataset'",
                imageOutput(outputId = "wf2_plot"),
                uiOutput("wf2_output_options"),
                uiOutput("wf2_download_options")
            ),
            # third workflow
            conditionalPanel(
                condition = "input.active_workflow === 'FLUXNET/ICOS (experimental)'",
                imageOutput(outputId = "wf3_plot"),
                actionButton("save_wf3_output", "Save data"),
                downloadButton(
                    outputId = "wf3_plot_download",
                    label = "Download plot"
                ),
                uiOutput("wf3_download_options")
            )
        )
    )
)

server <- function(input,output){
    # setup reactive values
    wf1_initial_input_files <- list.files("input/wf1")
    wf1_initial_output_files <- list.files("output/wf1")
    wf2_initial_input_files <- list.files("input/wf2")
    wf2_initial_output_files <- list.files("output/wf2")
    wf3_initial_output_files <- list.files("output/wf3")
    all_reactive_values <- reactiveValues(
        sites = deims_site_name_mappings,
        zones = deims_site_zone_options,
        wf1_inputs = wf1_initial_input_files,
        wf1_outputs = wf1_initial_output_files,
        wf2_inputs = wf2_initial_input_files,
        wf2_outputs = wf2_initial_output_files,
        wf3_outputs = wf3_initial_output_files
    )

    # "input" UI rendering
    # if there are raster files available, let user choose via dropdown
    output$wf1_files <- renderUI({
        if(length(all_reactive_values$wf1_inputs)==0){
            # pass
        }
        else{
            selectInput(
                inputId = "wf1_selected_file",
                label = "Data to crop",
                # any way to force this to be empty on start, even if there are options ready?
                #selected = "",
                choices = all_reactive_values$wf1_inputs,
                multiple = FALSE
            )
        }
    })

    # if there are tabular files available, let user choose via dropdown
    output$wf2_files <- renderUI({
        if(length(all_reactive_values$wf2_inputs)==0){
            # pass
        }
        else{
            selectInput(
                inputId = "wf2_selected_file",
                label = "Data to crop",
                # any way to force this to be empty on start, even if there are options ready?
                #selected = "",
                choices = all_reactive_values$wf2_inputs,
                multiple = FALSE
            )
        }
    })

    # if raster data is chosen, prompt user for title to use in plot
    output$wf1_title <- renderUI({
        if(length(all_reactive_values$wf1_inputs)==0){
            # pass
        }
        else{
            textInput(
                inputId = "wf1_data_name",
                label = "Plot title",
                value = "Custom"
            )
        }
    })

    # creates sheet select box if Excel selected
    output$wf2_user_input_sheets <- renderUI({
        if(length(all_reactive_values$wf2_inputs)==0){
            # pass
        }
        else{
            if(endsWith(input$wf2_selected_file,"csv")){
                # pass
            }
            else{
                qualified_filename <- paste0("input/wf2/",input$wf2_selected_file)
                selectInput(
                    inputId = "wf2_sheet_key",
                    label = "Sheet to use",
                    choices = excel_sheets(qualified_filename),
                    multiple = FALSE
                )
            }
        }
    })

    # creates column selection based on upload + Excel sheet
    output$wf2_columns <- renderUI({
        if(length(all_reactive_values$wf2_inputs)==0){
            # pass
        }
        else{
            list(selectInput(
                inputId = "plot_key",
                label = "Column to plot",
                # [-1] drops the first column, i.e. the ID
                choices = names(wf2_user_input())[-1],
                multiple = FALSE
            ),
            textInput(
                inputId = "wf2_data_name",
                label = "Plot title",
                value = "Custom"
            )
            )
        }
    })

    # populates available zones based on site by reading python metadata
    output$wf2_site_zone_picker <- renderUI({
        selectInput(
            inputId = "data_grouping",
            label = "Zones to extract",
            choices = all_reactive_values$zones[[input$deims_site]],
            multiple = FALSE
        )
    })

    # render DEIMS site picker - reactive in case user adds site
    output$deims_site_picker <- renderUI({
        selectInput(
            inputId = "deims_site",
            label = "DEIMS site",
            choices = all_reactive_values$sites,
            multiple = FALSE
        )
    })

    # add new DEIMS sites on user input
    observeEvent(input$new_site, {
        addSiteToInterface(input$new_deims_ID)
        all_reactive_values$sites <- py$deims_site_name_mappings
        all_reactive_values$zones <- py$deims_site_zone_options
    })

    # reads input file, if it exists, and "returns" tibble
    wf2_user_input <- reactive({
        if(is.null(input$wf2_selected_file)){
            # pass
        }
        else{
            if(endsWith(input$wf2_selected_file,"csv")){
                qualified_filename <- paste0("input/wf2/",input$wf2_selected_file)
                read_csv(qualified_filename)
            }
            else{
                qualified_filename <- paste0("input/wf2/",input$wf2_selected_file)
                read_excel(qualified_filename,input$wf2_sheet_key)
            }
        }
    })

    # "output" UI rendering
    # render wf1 preview, triggering the workflow if needed
    output$wf1_plot <- renderImage({
        if(length(all_reactive_values$wf1_inputs)==0){
            list(src="eLTER-logo.png",alt="eLTER logo",width=645,height=233)
        }
        else{
            wf1_output()
            list(src="/tmp/crop.png",alt="Plot of cropped data")
        }
    }, deleteFile = FALSE)

    # render wf2 preview, triggering the workflow if needed
    output$wf2_plot <- renderImage({
        if(length(all_reactive_values$wf2_inputs)==0){
            list(src="eLTER-logo.png",alt="eLTER logo",width=645,height=233)
        }
        else{
            wf2_output()
            list(src="/tmp/plot.png",alt="Plot of aggregated data")
        }
    }, deleteFile = FALSE)

    # render wf3 preview, triggering the workflow if needed
    output$wf3_plot <- renderImage({
        wf3_output()
        list(src="/tmp/wf3.png",alt="Plot of aggregated data")
    }, deleteFile = FALSE)

    # render options when there is wf1 input data being processed
    output$wf1_output_options <- renderUI({
        if(length(all_reactive_values$wf1_inputs)==0){
            # pass
        }
        else{
            tagList(
                actionButton("save_wf1_output", "Save data"),
                downloadButton(
                    outputId = "wf1_plot_download",
                    label = "Download plot"
                )
            )
        }
    })

    # render options when there is wf2 input data being processed
    output$wf2_output_options <- renderUI({
        if(length(all_reactive_values$wf2_inputs)==0){
            # pass
        }
        else{
            tagList(
                actionButton("save_wf2_output", "Save data"),
                downloadButton(
                    outputId = "wf2_plot_download",
                    label = "Download plot"
                )
            )
        }
    })

    # render options for when output is available to download
    output$wf1_download_options <- renderUI({
        if(length(all_reactive_values$wf1_outputs)==0){
            # pass
        }
        else{
            tagList(
                # selectinput for choosing download file, updated on save button click
                selectInput(
                    inputId = "wf1_download_choice",
                    label = "Select data to download",
                    choices = all_reactive_values$wf1_outputs,
                    multiple = FALSE
                ),
                downloadButton(
                    outputId = "wf1_download",
                    label = "Download data"
                )
            )
        }
    })

    # render options for when output is available to download
    output$wf2_download_options <- renderUI({
        if(length(all_reactive_values$wf2_outputs)==0){
            # pass
        }
        else{
            tagList(
                # selectinput for choosing download file, updated on save button click
                selectInput(
                    inputId = "wf2_download_choice",
                    label = "Select data to download",
                    choices = all_reactive_values$wf2_outputs,
                    multiple = FALSE
                ),
                downloadButton(
                    outputId = "wf2_download",
                    label = "Download data"
                )
            )
        }
    })

    # render options for when output is available to download
    output$wf3_download_options <- renderUI({
        if(length(all_reactive_values$wf3_outputs)==0){
            # pass
        }
        else{
            tagList(
                # selectinput for choosing download file, updated on save button click
                selectInput(
                    inputId = "wf3_download_choice",
                    label = "Select data to download",
                    choices = all_reactive_values$wf3_outputs,
                    multiple = FALSE
                ),
                downloadButton(
                    outputId = "wf3_download",
                    label = "Download data"
                )
            )
        }
    })


    # "logic"
    # execute wf1, returning nothing - output is to disk
    wf1_output <- reactive({
        path_to_dataset <- paste0("input/wf1/",input$wf1_selected_file)
        cropRasterDataset(path_to_dataset,input$deims_site,input$wf1_data_name)
    })

    # execute wf2, returning tibble for download
    wf2_output <- reactive({
        aggregateTabularDataset(wf2_user_input(),input$deims_site,input$data_grouping,input$plot_key,input$wf2_data_name)
    })

    # execute wf3, returning tibble for download
    wf3_output <- reactive({
        wf3_filename <- paste0("input/",input$wf3_data_source,"/",input$wf3_site,".csv")
        # parse TIME as character deliberately, as date/time does not work with reticulate
        # due to pandas using numpy's custom datetime64 type and the fact that
        # "If a Python object of a custom class is returned then an R reference to that object is returned."
        #
        # see:
        # https://pandas.pydata.org/docs/user_guide/timeseries.html
        # https://rstudio.github.io/reticulate/articles/calling_python.html#type-conversions
        wf3_data <- read_csv(wf3_filename,col_types="cdddddddddddddddddddddddddd")
        filterColumns(wf3_data,input$wf3_variable)
    })

    # watch for wf1 uploads and handle them
    wf1_upload_watcher <- observe({
        if(is.null(input$wf1_upload)){
            # pass
        }
        else{
            # process user upload, taking its validity for granted
            dataset_path <- paste0("input/wf1/",input$wf1_upload$name)
            file.copy(input$wf1_upload$datapath,dataset_path)
            all_reactive_values$wf1_inputs <- list.files("input/wf1")
            updateSelectInput(
                inputId = "wf1_selected_file",
                selected = input$wf1_upload$name
            )
        }
    })

    # watch for wf2 uploads and handle them
    wf2_upload_watcher <- observe({
        if(is.null(input$wf2_upload)){
            # pass
        }
        else{
            # process user upload, taking its validity for granted
            dataset_path <- paste0("input/wf2/",input$wf2_upload$name)
            file.copy(input$wf2_upload$datapath,dataset_path)
            all_reactive_values$wf2_inputs <- list.files("input/wf2")
            updateSelectInput(
                inputId = "wf2_selected_file",
                selected = input$wf2_upload$name
            )
        }
    })

    # save raster output on user input
    observeEvent(input$save_wf1_output, {
        # take everything off input filename after first dot - foo.x.y.z becomes foo
        original_filename_without_extension <- strsplit(input$wf1_selected_file,".",TRUE)[[1]][1]
        unqualified_filename <- paste0(original_filename_without_extension,"-",input$deims_site,".tif")
        qualified_filename <- paste0("output/wf1/",unqualified_filename)
        file.copy("/tmp/masked.tif",qualified_filename)
        all_reactive_values$wf1_outputs <- list.files("output/wf1")
        updateSelectInput(
            inputId = "wf1_download_choice",
            selected = unqualified_filename
        )
    })

    # save tabular output on user input
    observeEvent(input$save_wf2_output, {
        # take everything off input filename after first dot - foo.x.y.z becomes foo
        original_filename_without_extension <- strsplit(input$wf2_selected_file,".",TRUE)[[1]][1]
        unqualified_filename <- paste0(original_filename_without_extension,"-",input$deims_site,"-",input$data_grouping,".csv")
        qualified_filename <- paste0("output/wf2/",unqualified_filename)
        write_csv(wf2_output(),qualified_filename)
        all_reactive_values$wf2_outputs <- list.files("output/wf2")
        updateSelectInput(
            inputId = "wf2_download_choice",
            selected = unqualified_filename
        )
    })

    # save wf3 output on user input
    observeEvent(input$save_wf3_output, {
        # prepare filenames
        filename_root <- paste0(input$wf3_site,"-",input$wf3_data_source,"-",format(Sys.time(),"%Y-%m-%d-%H-%M-%S"))

        unqualified_data_filename <- paste0(filename_root,".csv")
        qualified_data_filename <- paste0("/tmp/",unqualified_data_filename)
        unqualified_zip_filename <- paste0(filename_root,".zip")
        qualified_zip_filename <- paste0("output/wf3/",unqualified_zip_filename)

        # write data, metadata, then zip to output folder
        output_data <- convertToElterFormat(wf3_output(),wf3_deims_id[[input$wf3_site]],input$wf3_site,input$wf3_variable)
        write_csv(output_data,qualified_data_filename)
        writeFilterColumnsMetadata(input$wf3_data_source,input$wf3_site,wf3_deims_id[[input$wf3_site]],input$wf3_variable,unqualified_data_filename)
        zip(qualified_zip_filename,c(qualified_data_filename,"/tmp/metadata.txt",paste0("input/",input$wf3_data_source,"/method.csv"),paste0("input/",input$wf3_data_source,"/reference.csv")),flags="-j")
        all_reactive_values$wf3_outputs <- list.files("output/wf3/")
        updateSelectInput(
            inputId = "wf3_download_choice",
            selected = unqualified_zip_filename
        )
    })

    # handle wf1 data download
    output$wf1_download <- downloadHandler(
        filename = function(){
            input$wf1_download_choice
        },
        content = function(file){
            qualified_filename <- paste0("output/wf1/",input$wf1_download_choice)
            file.copy(qualified_filename,file)
        })

    # handle wf1 plot download
    output$wf1_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/crop.png",file)
        })

    # handle wf2 data download
    output$wf2_download <- downloadHandler(
        filename = function(){
            input$wf2_download_choice
        },
        content = function(file){
            qualified_filename <- paste0("output/wf2/",input$wf2_download_choice)
            file.copy(qualified_filename,file)
        })

    # handle wf2 plot download
    output$wf2_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/plot.png",file)
        })

    # handle wf3 data download
    output$wf3_download <- downloadHandler(
        filename = function(){
            input$wf3_download_choice
        },
        content = function(file){
            qualified_filename <- paste0("output/wf3/",input$wf3_download_choice)
            file.copy(qualified_filename,file)
        })

    # handle wf3 plot download
    output$wf3_plot_download <- downloadHandler(
        filename = "plot.png",
        content = function(file){
            file.copy("/tmp/wf3.png",file)
        })
}

shinyApp(ui,server)
