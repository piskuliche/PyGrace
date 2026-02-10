# pygrace

PyGrace: XMGrace-like plotting with a Qt/Matplotlib backend.

## Install

```bash
pip install -e .
```

## Usage

Launch GUI with datasets:

```bash
xmgrace data1.dat data2.dat
```

Explicit XY data mode (XMGrace-style):

```bash
xmgrace -nxy data1.dat -nxy data2.dat
```

Set labels:

```bash
xmgrace -title "My Plot" -xlabel "Time" -ylabel "Value" data.dat
```

Export to PNG without launching the GUI (XMGrace-style):

```bash
xmgrace -hardcopy -device PNG -printfile out.png data.dat
```

## Notes

Supported CLI subset: `-nxy`, `-title`, `-xlabel`, `-ylabel`, `-legend`, `-world`, `-autoscale`, `-hardcopy`, `-device`, `-printfile`.
Unknown flags are ignored with a warning.
