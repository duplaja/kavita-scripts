# kavita-scripts
Various scripts to use with Kavita

## [Epub Fix GUI Local](https://github.com/duplaja/kavita-scripts/blob/main/epub-fix-gui-local.py)

* Sets title, author, series, and series index metadata (attempts to load existing, or use sane defaults)
* Converts from epub to epub, using Calibre CLI (fixes many malformed epub issues).
* Creates a folder structure suitable for placing in Kavita (series name). Placement can be done manually, or with this script if you run it on your machine that hosts Kavita. To automatically place it in a remote server, see the next script.

**Note: This script requires Calibre to be installed, as it uses Calibre CLI. You must first configure the usual defaults for Calibre, for this to work well (include metadata in epub rather than sidecar file, etc).**

## [Epub Fix GUI Remote](https://github.com/duplaja/kavita-scripts/blob/main/epub-fix-gui-remote.py)

* Sets title, author, series, and series index metadata (attempts to load existing, or use sane defaults)
* Converts from epub to epub, using Calibre CLI (fixes many malformed epub issues).
* Creates a folder structure suitable for placing in Kavita (series name).
* **Unlike the previous script, this pulls your library names and paths from the Kavita API. Be sure to set all needed variables at the top.**
* After the file is converted you can (optionally) upload the epub to a remote server, via rsync. See settings for details.
* After (optionally) uploading to a remote server, a scan is triggered so the epub will be added to your library (may take a minute or two to run).

**Note: This script requires Calibre to be installed, as it uses Calibre CLI. You must first configure the usual defaults for Calibre, for this to work well (include metadata in epub rather than sidecar file, etc). You must configure your remote host to accept SSH via key, if you want to use rsync to send the file, and must configure Kavita to enable ODPS support.**

## [Find Missing Chapters](https://github.com/duplaja/kavita-scripts/blob/main/find-missing-chapters.py)

* Attempts to find missing chapters in a given Kavita Library. You will need your Library ID, to run this (can be found from the URL).
* This looks for "skipped" whole numbers, where you have a chapter 7 and a chapter 9 for example, but not a chapter 8. Some series that use decimals such as .1 may cause false positives.
* Runs with `python kavita-missing-chapters.py 9` in terminal, (replacing 9 with your library ID).

## [View Your Reading History](https://github.com/duplaja/kavita-scripts/blob/main/view-your-reading-history.py)

* Shows your reading, from most recent "last read" date to earliest. For epub, shows percent read. For manga, shows % read and last read chapter.
* This one is fairly slow / experimental. Feel free to tweak it to make it your own.
* If you backtrack in a book, that may affect the output.

