# python-easyADB

![Banner](https://github.com/omidshm/PyAutoADB/blob/main/logo.png?raw=true)

PyAutoGUI but for Android!
a simple sdk for interacting with android debug bridge and automate boring stuff
this is part of m Commercial program that now is Free and Open Source

## Installation

### Dependencies

- androidsdk-platform-tools
- python 3.12 (not tested on lower versions. but it works probably)

```python

pip install pyautoadb

```

## Usage

```python
import pyautoadb

adb_handler = pyautoadb.ADBDevice("localhost", "55557")

img_path = adb_handler.take_screenshot()

print(img_path)

```

### next step ?

Check out [Documentation](https://github.com/omidshm/PyAutoADB/wiki) for in-depth explanation and examples

## Todo

- [ ] add async support
- [ ] add kernel low level apis
- [ ] add contribution rules
- [ ] write rich documentation

## Contributing

see contribution detail

## Donation

| BTC lightning⚡ | <houseball47@walletofsatoshi.com> |
|----------------|-----------------------------------|
| BTC            | Row 2, Col 2                      |
| USDT(trc-20)   | Row 3, Col 2                      |

thanks for your support

## Licence

This project is licensed under the MIT license. Feel free to use, modify, and distribute
