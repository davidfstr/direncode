# direncode 1.0

Encodes all video files in a source directory to a destination directory. Optionally, the source directory will be watched continuously for changes and any new files will be encoded.

## Requirements

* Operating System:
    * Mac OS X 10.9.5 (Mavericks) or later
    * Linux &mdash; probably works, but untested
    * Windows &mdash; probably works, but untested
* [Python] 2.7 or later
    * Python 3.x &mdash; probably works, but untested
* [hbencode] 1.1 or later
* [watchdog] 0.8.3 or later

[Python]: http://www.python.org
[hbencode]: https://github.com/davidfstr/hbencode
[watchdog]: https://pypi.python.org/pypi/watchdog

## Installation

1. Install and configure all requirements mentioned above.
    * In particular [hbencode] has some required configuration.
    * [watchdog] can usually be installed with `pip install watchdog`.
2. Copy `direncode.py` to somewhere in your system path.

## Usage

Encode all files in directory `/srcdir` to directory `/dstdir` using:

```
direncode.py /srcdir /dstdir
```

Continously encode all files that appear in `/srcdir` to directory `/dstdir` until you interrupt the program with Control-C:

```
direncode.py --watch /srcdir /dstdir
```

## Support

If you run into problems or have questions, feel free to file a
[bug] or [contact] me.

[contact]: http://dafoster.net/about#contact
[bug]: https://github.com/davidfstr/direncode/issues

## License

This software is licensed under the [MIT License].

[MIT License]: https://github.com/davidfstr/direncode/blob/master/LICENSE.txt
