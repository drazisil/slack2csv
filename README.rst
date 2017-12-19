slack2csv
=========

|CircleCI|

Python script to export Slack channel history to csv for reporting

Usage
-----

::

    usage: slack2csv.py [-h] [--text TEXT] [--past_days PAST_DAYS] --token TOKEN
                        --channel CHANNEL --filename FILENAME

    slack2csv

    optional arguments:
      -h, --help            show this help message and exit
      --text TEXT           text to search for
      --past_days PAST_DAYS
                            days to go back

    required named arguments:
      --token TOKEN         Slack API token
      --channel CHANNEL     Slack channel id or name
      --filename FILENAME   CSV filename

.. |CircleCI| image:: https://circleci.com/gh/drazisil/slack2csv.svg?style=shield
   :target: https://circleci.com/gh/drazisil/slack2csv

