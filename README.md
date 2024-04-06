# Summarizing code folders

This script summarizes a folder of code files. It uses the `summarize.py` script to summarize each file in the folder. It then combines the summaries into a single summary.

## Excluding files

```console
> python summarize.py --folder /home/stijn/Documents/scene/zuos-data/data/conservation_areas --exclude_indices 0 2

...

0 [ ] 778 /home/stijn/Documents/scene/zuos-data/data/conservation_areas/models.py
1 [x] 1053 /home/stijn/Documents/scene/zuos-data/data/conservation_areas/README.md
2 [ ] 2105 /home/stijn/Documents/scene/zuos-data/data/conservation_areas/tests.py

total tokens: 1129
```
