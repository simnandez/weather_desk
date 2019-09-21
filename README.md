# WeatherDesk

Change the wallpaper based on Mojave theme and the local time.

Thanks to [Martin Hansen](http://stackoverflow.com/users/2118300/martin-hansen) for the original `Desktop.py` module.

Powered by

[![Powered by OpenWeatherMap!](https://openweathermap.org/themes/openweathermap/assets/img/openweather-negative-logo-RGB.png)](https://openweathermap.org)

# Installation

Just download the repository, get some wallpapers (see [the Wallpapers section](#wallpapers)) and run the `WeatherDesk.py` script.

**NOTE:** If you use OS X, see [the note for OS X users](#note-for-os-x-users).

## Options

    $ python3 WeatherDesk.py
      -c name [name ...], --city name [name ...]
                            Specify city for weather. If not given, taken from ipinfo.io.
    
**Example:** WeatherDesk.py -c paris

## Wallpapers

Put the .weatherdesk_walls directory in the default `~/.weatherdesk_walls/` directory or specify a directory with the `--dir` option.
**You can choose your own custom set**, conforming to the [naming rules](#naming-of-pictures).

## Supported Platforms

- Linux

  - AfterStep
  - Awesome WM
  - Blackbox
  - Cinnamon
  - Deepin
  - Enlightenment
  - Fluxbox
  - Gnome 2
  - Gnome 3
  - i3
  - IceWM
  - JWM
  - KDE
  - LXDE
  - LXQt
  - Mate
  - Openbox
  - Pantheon
  - Razor-Qt
  - Trinity
  - Unity
  - Windowmaker
  - XFCE

- Windows

- OS X

## In background mode (only for OS X and Linux)

Run

```sh
$ nohup python3 WeatherDesk.py > /dev/null &
```

## Note for OS X users

Please disable the auto-reset/change of wallpaper in the  "Desktop and Screen Saver" preferences.

[![Disable this](http://i.imgur.com/BFi1GHGm.png)](http://i.imgur.com/BFi1GHG.png)
