# eLTER cookie-cutting prototype FAQs
*What is this?*

A collection of workflows to “cookie-cut” data by extracting only the data relevant to a DEIMS site.
There's also a web-based user interface to make using the workflows easier for non-programmers.

*Which DEIMS sites does it work with?*

All of them!
6 LTSER platforms are included out of the box but on-the-fly retrieval of any site from DEIMS is fully-supported.

*What kinds of data does it work with?*

There are two workflows in the app: one for spatial raster/gridded data and one for tabular data.

*What file formats are supported?*

For raster data, Geotiff is the only format tested extensively and known to work.
The code to handle raster data is file format-neutral in principle but no guarantees are made.

For tabular data, csv and Excel files are supported.

*What does the raster workflow do?*

The raster workflow crops your dataset to the geographical boundaries of the DEIMS site you choose.
It plots a preview of the new dataset and allows you to download the resulting plot and dataset to your computer.

*What does the tabular workflow do?*

The tabular workflow filters your dataset to rows which relate to your chosen DEIMS site, along with some additional spatial information about each zone.
The assumption is that each row of data represents an observation(s) for a statistical region (e.g. county, state, NUTS region, canton...).

*What are the data formatting requirements for tabular data?*

See [the wf2 reference documentation](../reference/wf2.md), "Technical description" > "Dependencies" > "Data".

*How can I access a working app?*

The app has been developed in UKCEH’s DataLabs platform where it can be accessed by anybody.
To do so, first create an account at [https://datalab.datalabs.ceh.ac.uk/](https://datalab.datalabs.ceh.ac.uk/).
Once you have an account, email wilbol@ceh.ac.uk and ask to be added to the eLTER PLUS project.
Once you have been added to the project, the app will be available.
The code for the app is all on GitHub at [https://github.com/eLTER-RI/spatial-data-processor](https://github.com/eLTER-RI/spatial-data-processor), so you’re also welcome to look at it, modify it and run it on your own infrastructure.
Pull requests are welcome.
