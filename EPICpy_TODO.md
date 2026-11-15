# EPICpy TODO

- is background image drawing working?
- consider bringing mike walton's attention code over to epiclibcpp
- consider adding PTS type changes to MMP

## NOTES

You can test different epiclibcpp versions with uv's --with flag:

```bash
uv tool install /home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy3/EPICpy3 --with "epiclibcpp==0.2.1" --reinstall
```

## COMMUNICATION STUFF

## ASAP

## SOON

- most things in GUI needs hover messages.

## LATER LATER

- add toggle to always clear data before run
- would be nice to have a 'why didn't this rule fire given some starting cycle..will look down and essentially do CiTRIC for you?'
- add go to last rule fired -- or even a which rules fired list
- dynamic schematic
- dynamic brain??
- trial event vs rule-fire list

## EPICpy ideas


## Hold For Now

    "plum-dispatch>=2.5.0,<=2.6.0; sys_platform != 'win32'",
    "plum-dispatch>=2.5.0,<=2.6.0; sys_platform == 'win32'",
        "ulid>=1.1,<2.0",
