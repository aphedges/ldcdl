# LDC package downloading tool

By Jonathan May (jonmay@isi.edu)

March 4, 2016


# Requirements:

* Python 2.7
* mechanize and beautifulsoup4 python packages
* ldc login/password


# Usage:

```
$ ./ldcdl.py -h
usage: ldcdl.py [-h] [--outdir OUTDIR] [--suffix SUFFIX]
                [--corpus CORPUS [CORPUS ...]] [--login LOGIN]
                [--password PASSWORD]

Get corpus from LDC

optional arguments:
  -h, --help            show this help message and exit
  --outdir OUTDIR, -o OUTDIR
                        output directory (default: None)
  --suffix SUFFIX, -s SUFFIX
                        file suffix (default: tar.gz)
  --corpus CORPUS [CORPUS ...], -c CORPUS [CORPUS ...]
                        corpus name(s) (e.g. LDC99T42) (default: None)
  --login LOGIN, -l LOGIN
                        ldc login (default: None)
  --password PASSWORD, -p PASSWORD
                        ldc password (default: None)


$ ./ldcdl.py -o . -c LDC99T42 LDC95T7 -l my_login -p my_password
Retrieved LDC99T42 to ./LDC99T42.tar.gz
Retrieved LDC95T7 to ./LDC95T7.tar.gz
```

# Known Issues

* Mechanize is not memory-safe: you should have as much memory as the size of the corpus you are downloading.
