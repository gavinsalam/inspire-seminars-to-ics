Contains a script to get seminars from the InspireHEP API and write them to an ics file.

Usage

```
./inspire-seminars-to-ics.py "series name" [--all] -o output-file.ics
```

With the `--all` flag you get all seminars, otherwise just the upcoming ones. 

The script is not yet entirely robust. E.g. if can only handle up to 500 entries.

Written by Melissa van Beekveld, with adaptations from Gavin Salam.