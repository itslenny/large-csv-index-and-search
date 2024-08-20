# Large CSV index and search

This project is meant for allowing quick searches (< 1 second) of large CSV (100GB+) files without needing a database. This was just a fun project to test an idea for parsing large data files. Doing the same search using grep without this index took several minutes.

## How it works

This script assumes the file has a `firstname` `lastname` `middlename` and `st` column for filtering, but those headers could easily be adjusted.

For every line in the CSV a file named `lastname` is created which includes the first name and byte offsets of the line where it was founded in the larger CSV.

To search we simply read the `lastname` file, and for every line that matches `firstname` we get that data from the large csv using the byte offset data stored in the indexing step

An example of the index file format is as follows:

```
reynaldo,53440580500,53440580621
dennis,53440633867,53440633974
marta,53440670231,53440670340
anna,53440682328,53440682451
ana,53440684795,53440684900
anna,53440686681,53440686787
antonio,53441036122,53441036226
```

## Why?

It seemed like a fun project to play with parsing large files. This could've obviously been achieved by using an off-the-shelf database solution, but this was more fun. Also, I was curious if this was possible using a low-tech solution (without needing fancy data structures. just flat files on disk)

