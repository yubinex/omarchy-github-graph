import QtQuick
import Quickshell
import Quickshell.Io

// Keeps the contribution graph wallpaper fresh. Rendering lives in
// bin/omarchy-github-graph; this service only decides when to run it.
// Every run uses --if-active, so it never changes a background the user
// picked, it only redraws the graph while the graph is showing.
Item {
  id: root

  readonly property string moduleName: "yubinex.github-graph"
  readonly property string home: Quickshell.env("HOME")
  readonly property string pluginDir: Qt.resolvedUrl(".").toString().replace(/^file:\/\//, "")
  readonly property string scriptPath: pluginDir + "/bin/omarchy-github-graph"

  function refresh() {
    if (renderProcess.running)
      return;
    renderProcess.running = true;
  }

  // Give the network and gh a moment after login before the first fetch.
  Timer {
    interval: 2 * 60 * 1000
    running: true
    onTriggered: root.refresh()
  }

  Timer {
    interval: 15 * 60 * 1000
    running: true
    repeat: true
    onTriggered: root.refresh()
  }

  // omarchy-theme-set rewrites theme.name after the new colors are in place
  // and then relinks the background; wait for that before re-rendering.
  FileView {
    path: root.home + "/.local/state/omarchy/current/theme.name"
    watchChanges: true
    onFileChanged: themeSettle.restart()
  }

  Timer {
    id: themeSettle
    interval: 3000
    onTriggered: root.refresh()
  }

  // A login shell so gh is found the same way it is in a terminal (mise shims,
  // ~/.local/bin). The system Python is used explicitly: python-pillow is a
  // system package, and a mise-managed python3 on PATH wouldn't have it.
  Process {
    id: renderProcess
    command: ["bash", "-lc", "exec /usr/bin/python3 \"$0\" --if-active", root.scriptPath]
    stderr: SplitParser {
      onRead: data => console.warn(root.moduleName + ": " + data)
    }
  }
}
