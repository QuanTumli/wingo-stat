# wingo-stat

wingo-stat let's you download your usage details from your Wingo Account (https://www.wingo.ch/)

## Dependencies

To use this script you need Python (**Version > 3**) installed on your Computer (https://www.python.org/downloads/)


## Running It

To run wingo-stat, you need to rename `config-sample.json` to `config.json` and insert your credentials.

Then you can run it like this:

```
python3.4 download.py
```

It outputs 3 CSV-Files to the `results`-Folder:
- output.csv / all data
- output_monthly_stats.csv / data grouped by months
- output_daily_stats.csv / data grouped by days

## Credits

This script was written by [QuanTumli](https://github.com/QuanTumli).
