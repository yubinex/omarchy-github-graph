# Omarchy GitHub Graph

An Omarchy service plugin that turns your GitHub contribution graph into a
wallpaper, drawn in the colors of your current theme.

It redraws the graph every hour and whenever you switch themes. It only
re-applies the image while the graph is your current background, so it never
replaces a wallpaper you picked.

## Requirements

- The [GitHub CLI](https://cli.github.com/), signed in. The graph is fetched
  with `gh api graphql` as the signed-in account, so it shows that account's
  contributions.
- [Pillow](https://python-pillow.org/) for the system Python (`/usr/bin/python3`),
  from the `python-pillow` package. A Python from mise, pyenv or a virtualenv
  isn't used, so `pip install pillow` there won't help.
- JetBrainsMono Nerd Font (included with Omarchy)

## Installation

Install the dependencies and sign in to GitHub:

```bash
omarchy pkg add github-cli python-pillow
gh auth login
```

Check that `gh auth status` reports you as logged in. The plugin runs in the
background and can't prompt for a login.

Then install and enable the plugin with Omarchy:

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

## Troubleshooting

If the graph never appears, run the script by hand. It prints the reason:

```bash
~/.config/omarchy/plugins/yubinex.github-graph/bin/omarchy-github-graph --set
```

| Message | Fix |
| --- | --- |
| `Pillow is missing` | `omarchy pkg add python-pillow` |
| `gh not found` | `omarchy pkg add github-cli`, then `gh auth login` |
| `gh api failed: …` (e.g. `Bad credentials`) | Check `gh auth status`, then sign in again with `gh auth login` |

The background service writes the same messages to the shell log:

```bash
journalctl --user -t omarchy-shell | grep github-graph
```

## License

[MIT](LICENSE)
