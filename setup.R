# script to restore from lone packrat.lock file
# packrat workflow cribbed from Miles McBain:
# https://milesmcbain.xyz/packrat-lite/
packrat::restore()

packrat::init(
    infer.dependencies = FALSE,
    options = list(
        vcs.ignore.lib = TRUE,
        vcs.ignore.src = TRUE
        )
    )
