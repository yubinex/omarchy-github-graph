# Omarchy GitHub Graph

An Omarchy service plugin that turns your GitHub contribution graph into a
wallpaper, drawn in the colors of your current theme.

It redraws the graph every hour and whenever you switch themes. It only
re-applies the image while the graph is your current background, so it never
replaces a wallpaper you picked.

## Requirements

- [GitHub CLI](https://cli.github.com/), signed in with `gh auth login`
- `python-pillow`
- JetBrainsMono Nerd Font (included with Omarchy)

## Installation

Install and enable the plugin with Omarchy:

```bash
omarchy plugin add https://github.com/yubinex/omarchy-github-graph.git --enable
```

Update it later with:

```bash
omarchy plugin update yubinex.github-graph --yes
```

## Usage

The image is saved as
`~/.config/omarchy/backgrounds/<theme>/github-contributions.png`, so it also
shows up in that theme's background rotation.

To switch between the graph and your previous background with a key, add this
to `~/.config/hypr/bindings.lua`:

```lua
o.bind("SUPER + CTRL + G", "Toggle GitHub graph wallpaper", os.getenv("HOME") .. "/.config/omarchy/plugins/yubinex.github-graph/bin/omarchy-github-graph --toggle")
```

The script can also be run directly:

| Flag | Effect |
| --- | --- |
| `--set` | Render and switch to the graph |
| `--toggle` | Switch between the graph and the background shown before it |
| `--if-active` | Render, and re-apply only if the graph is already the background |

## License

[MIT](LICENSE)
