# Sublime Commands

Sublime Text's command palette misses most of the internal commands exposed by the main menu.

Packages like [Missing Commands](https://github.com/fjl/Sublime-Missing-Palette-Commands) therefore provide all commands not located in Sublime Text's _Default_ package.

This package provides a merged and hopefully complete Default.sublime-commands which is intended to be placed into the _Default_ package.


##### Warning and Disclaimer

As this package partially overwrites the _Default.sublime-package_ package provided by Sublime Text out of the box, the original content will be completely hidden.

If you encounter any issues don't therefore blame the core devs but first try to remove this package.

The package author tries his best to keep up to date with the ongoing development but can't provide any warranty.


##### Package Control

As this package is and will never be added to the official [packagecontrol.io](https://packagecontrol.io/) for official reasons, you need to add the following settings to your _User/Package Control.sublime-settings_ if you want Package Control to keep this package up to date for you.

```json
{
    "repositories": [
        "https://github.com/deathaxe/sublime-commands"
    ],
    "package_name_map": {
        "sublime-commands": "Default"
    }
}
```

Save the settings file.
Open command palette, select _Package Control: Install Package_, search for _Default_ and install it.

##### Manual Setup

If you want to use it to override ST's commands you'll need to clone this repo into Sublime Text's _Packages_ path as _Default_

##### OSX

```sh
#!/usr/bin/env bash
cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
git clone https://github.com/deathaxe/sublime-commands "Default"
```


##### Linux

```sh
cd ~/.config/sublime-text-3/Packages
git clone https://github.com/deathaxe/sublime-commands "Default"
```


##### Windows

```dos
cd "%APPDATA%\Sublime Text 3\Packages"
git clone https://github.com/deathaxe/sublime-commands "Default"
```
