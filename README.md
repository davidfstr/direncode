# direncode

Encodes all video files in a source directory to a destination directory. Optionally, the source directory will be watched continuously for changes and any new files will be encoded.

This behavior is useful for setting up a video encoding pipeline where one directory's contents are continuously encoded to another directory.

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

Continously encode from `/srcdir` to `/dstdir`, and additionally synchronize deletions that occur in `/srcdir` to `/dstdir`:

```
direncode.py --watch --delete /srcdir /dstdir
```

Display full usage information by invoking `direncode.py` with no arguments:

```
syntax: direncode.py [<options>] SOURCE_DIR DESTINATION_DIR
    
    Options:
        -w, --watch             Continuously watch the source directory
                                and continue synchronizing both directories.
        -d, --delete            Delete extraneous files from destination.
```

## Support

If you run into problems or have questions, feel free to file a
[bug] or [contact] me.

[contact]: http://dafoster.net/about#contact
[bug]: https://github.com/davidfstr/direncode/issues

## License

This software is licensed under the [MIT License].

[MIT License]: https://github.com/davidfstr/direncode/blob/master/LICENSE.txt

## Release Notes

* 1.1
	* Supports `--delete` option to additionally synchronize deletes.
* 1.0
	* Initial version.
	* Supports `--watch` option for continuous synchronization.
