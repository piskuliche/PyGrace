import argparse
import sys
from pathlib import Path

from .data import load_datasets
from .gui import launch_gui, render_hardcopy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xmgrace",
        description="PyGrace: XMGrace-like plotting with a Qt/Matplotlib backend.",
        add_help=True,
    )
    parser.add_argument("files", nargs="*", help="Data files")
    parser.add_argument("-nxy", dest="nxy_files", action="append", default=[], help="Read simple XY data")
    parser.add_argument(
        "-bxy",
        "--bxy",
        dest="bxy_specs",
        action="append",
        default=[],
        help="Column mapping per file: x:y, x:y:dy, or x:y:dx:dy (1-based indices)",
    )
    parser.add_argument("-title", dest="title", default=None, help="Plot title")
    parser.add_argument("-xlabel", dest="xlabel", default=None, help="X axis label")
    parser.add_argument("-ylabel", dest="ylabel", default=None, help="Y axis label")
    parser.add_argument(
        "-legend",
        dest="legend",
        default=None,
        help="Comma-separated legend labels (e.g. 'a,b,c')",
    )
    parser.add_argument(
        "-world",
        dest="world",
        nargs=4,
        type=float,
        metavar=("XMIN", "XMAX", "YMIN", "YMAX"),
        help="Set world bounds",
    )
    parser.add_argument("-autoscale", dest="autoscale", action="store_true", help="Autoscale axes")
    parser.add_argument("-hardcopy", dest="hardcopy", action="store_true", help="Render without GUI")
    parser.add_argument("-printfile", dest="printfile", default=None, help="Output file for hardcopy")
    parser.add_argument("-device", dest="device", default=None, help="Output device (PNG supported)")
    parser.add_argument("-version", action="version", version="pygrace 0.1.0")
    return parser


def normalize_args(argv: list[str]) -> list[str]:
    # XMGrace allows -param, -nxy, etc. without strict ordering.
    return argv


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args, unknown = parser.parse_known_args(normalize_args(argv))

    if unknown:
        sys.stderr.write(
            "Warning: unsupported options ignored: " + " ".join(unknown) + "\n"
        )

    data_files = [Path(p) for p in args.files] + [Path(p) for p in args.nxy_files]
    if len(args.bxy_specs) > len(data_files):
        sys.stderr.write("Error: more -bxy specs than data files\n")
        return 2
    bxy_by_file = [None for _ in data_files]
    for idx, spec in enumerate(args.bxy_specs):
        bxy_by_file[idx] = spec

    try:
        datasets = load_datasets(data_files, bxy_specs=bxy_by_file)
    except ValueError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 2

    legend_labels = None
    if args.legend:
        legend_labels = [label.strip() for label in args.legend.split(",") if label.strip()]

    if args.hardcopy:
        if not args.printfile:
            sys.stderr.write("Error: -hardcopy requires -printfile\n")
            return 2
        device = (args.device or "PNG").upper()
        if device != "PNG":
            sys.stderr.write("Error: only PNG device is supported\n")
            return 2
        render_hardcopy(
            datasets=datasets,
            output_path=Path(args.printfile),
            title=args.title,
            xlabel=args.xlabel,
            ylabel=args.ylabel,
            world=args.world,
            autoscale=args.autoscale or args.world is None,
            legend_labels=legend_labels,
        )
        return 0

    launch_gui(
        datasets=datasets,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        world=args.world,
        autoscale=args.autoscale or args.world is None,
        legend_labels=legend_labels,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
