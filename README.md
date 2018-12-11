# PyZipEI

PyZipEI is a python utility library for extracting electrical utility rates from OpenEI.org via zipcode

## Installation

```
pip3 install pyzipei
```

## Command Line Interface

A simple CLI is provided. This can be used to verify installations by calling "PyZipEI" or "python3 -m PyZipEI". This will locate the residential rate for the US zipcode 27612. You can provide the CLI with arguments to change the zipcode, sector and logging verbosity.

## Application Note

Requests to OpenEI are not the speediest. Request timeouts have been defaulted to 30 seconds.
