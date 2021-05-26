# eLTER cookie-cutting prototype FAQs
*What is this?*

A web app to “cookie-cut” data to extract only the data relevant to a particular DEIMS site.

*Which DEIMS sites does it work with?*

Currently it is limited to the 5 LTSER platforms (LTSER Zone Atelier Alpes, Braila Islands, Cairngorms National Park, Doñana LTSER platform and LTSER platform Eisenwurzen), although support is planned for on-the-fly retrieval of any site from DEIMS.

*What kinds of data does it work with?*

There are two workflows in the app: one for spatial raster/gridded data and one for normal tabular data.

*What file formats are supported?*

For raster data, Geotiff is the only format tested extensively and known to work.
The code to handle raster data is file format-neutral in principle but no guarantees are made about other formats.
For tabular data, csv and Excel sheets have been tested successfully, although there are some requirements on how the data is structured for both formats—another FAQ addresses this in more detail.

*What does the raster workflow do?*

The raster workflow crops the extent of your dataset to the geographical boundaries of the DEIMS site you choose.
It plots a preview of the new dataset and allows you to download the resulting plot and dataset to your computer.

*What does the tabular workflow do?*

The tabular workflow filters your dataset to rows which relate to your chosen DEIMS site, along with some additional spatial information about each zone.
The assumption is that each row of data represents an observation(s) for a statistical region (e.g. county, state, NUTS region, canton…).

*What are the data formatting requirements for tabular data?*

- the first column of data must contain IDs (e.g. S01006798 for Scottish data zones, AT122 for NUTS regions) which identify the region the row relates to, **with no extra formatting** (e.g. “AT122 - Niederösterreich-Süd” won’t work)
- the first row contains column name information
- there are no textual headers or comments.

The above applies to both CSV files and Excel sheets.
Additionally:

- for Excel files, each sheet must contain only one table of data.

*How can I access a working app?*

The app has been developed in UKCEH’s Datalabs platform where it can be accessed by anybody.
To do so, first create an account at [https://datalab.datalabs.ceh.ac.uk/](https://datalab.datalabs.ceh.ac.uk/).
Once you have an account, email wilbol@ceh.ac.uk and ask to be added to the eLTER PLUS project.
Once you have been added to the project, the app will be available.
The code for the app is all on Github at [https://github.com/eLTER-RI/spatial-data-processor](https://github.com/eLTER-RI/spatial-data-processor), so you’re also welcome to look at it, modify it and run it on your own infrastructure.
Pull requests are welcome.
