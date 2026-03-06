import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import ticker

from pygrace.backend import LINEAR_REGRESSION_PLUGIN_ID, Y_EQUALS_X_PLUGIN_ID, PlotBackend, PlotState
from pygrace.backend import render_hardcopy
from pygrace.data import Dataset


def test_apply_transform_updates_existing_dataset_y():
    datasets = [Dataset(name="s0", x=[0, 1, 2], y=[1, 2, 3])]
    backend = PlotBackend(datasets, PlotState(None, None, None, None, True), None)

    target_index = backend.apply_transform("y0 = y0 + 2")

    assert target_index == 0
    assert datasets[0].y == [3.0, 4.0, 5.0]


def test_apply_transform_creates_dataset_when_target_missing():
    datasets = [Dataset(name="s0", x=[0, 1, 2], y=[1, 2, 3])]
    backend = PlotBackend(datasets, PlotState(None, None, None, None, True), None)

    target_index = backend.apply_transform("y1 = y0 * 2")

    assert target_index == 1
    assert len(datasets) == 2
    assert datasets[1].name == "set1"
    assert datasets[1].y == [2.0, 4.0, 6.0]


def test_align_extrema_shifts_dataset_to_common_y():
    ds0 = Dataset(name="a", x=[0, 1, 2], y=[0, 2, 0])
    ds1 = Dataset(name="b", x=[0, 1, 2], y=[0, 4, 0])
    backend = PlotBackend([ds0, ds1], PlotState(None, None, None, None, True), None)

    selections = [
        (ds0, ("max", 1, 1.0, 2.0)),
        (ds1, ("max", 1, 1.0, 4.0)),
    ]
    backend.align_extrema(selections)

    assert ds0.y[1] == 3.0
    assert ds1.y[1] == 3.0


def test_extrema_falls_back_to_global_when_no_local_extrema():
    ds = Dataset(name="flat", x=[0, 1], y=[5, 7])
    backend = PlotBackend([ds], PlotState(None, None, None, None, True), None)

    extrema = backend.extrema_for_dataset(ds)

    assert len(extrema) == 2
    assert extrema[0][0] == "min"
    assert extrema[1][0] == "max"


def test_plot_datasets_respects_visibility_and_legend_labels():
    ds0 = Dataset(name="a", x=[0, 1], y=[1, 2], line_color="red")
    ds1 = Dataset(name="b", x=[0, 1], y=[2, 3], line_color="blue")
    backend = PlotBackend(
        [ds0, ds1],
        PlotState(None, None, None, None, True),
        legend_labels=["L0", "L1"],
    )
    backend.set_dataset_visible(1, False)

    fig, ax = plt.subplots()
    backend.plot_datasets(ax)

    assert len(ax.lines) == 1
    assert ax.lines[0].get_label() == "L0"
    legend = ax.get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["L0"]
    plt.close(fig)


def test_apply_axes_state_applies_labels_ticks_and_world_limits():
    state = PlotState(
        title="Title",
        xlabel="X",
        ylabel="Y",
        world=[0.0, 10.0, -1.0, 1.0],
        autoscale=False,
        title_size=16,
        xlabel_size=11,
        ylabel_size=12,
        xtick_size=9,
        ytick_size=10,
        x_major_step=2.0,
        y_major_step=0.5,
        x_minor_step=1.0,
        y_minor_step=0.25,
        minor_ticks=True,
    )
    backend = PlotBackend([Dataset(name="a", x=[0, 1], y=[0, 1])], state, None)

    fig, ax = plt.subplots()
    backend.apply_axes_state(ax)

    assert ax.get_title() == "Title"
    assert ax.get_xlabel() == "X"
    assert ax.get_ylabel() == "Y"
    assert tuple(round(v, 6) for v in ax.get_xlim()) == (0.0, 10.0)
    assert tuple(round(v, 6) for v in ax.get_ylim()) == (-1.0, 1.0)
    assert isinstance(ax.xaxis.get_major_locator(), ticker.MultipleLocator)
    assert isinstance(ax.yaxis.get_major_locator(), ticker.MultipleLocator)
    assert isinstance(ax.xaxis.get_minor_locator(), ticker.MultipleLocator)
    assert isinstance(ax.yaxis.get_minor_locator(), ticker.MultipleLocator)
    plt.close(fig)


def test_render_clears_existing_axes_content():
    backend = PlotBackend(
        [Dataset(name="a", x=[0, 1], y=[2, 3])],
        PlotState(None, None, None, None, True),
        None,
    )

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="stale")
    assert len(ax.lines) == 1

    backend.render(ax)

    assert len(ax.lines) == 1
    assert ax.lines[0].get_ydata().tolist() == [2, 3]
    plt.close(fig)


def test_set_dataset_appearance_updates_properties():
    ds = Dataset(name="a", x=[0, 1], y=[1, 2], line_color="black", marker_face_color="black")
    backend = PlotBackend([ds], PlotState(None, None, None, None, True), None)

    backend.set_dataset_appearance(
        0,
        line_width=3.5,
        line_style="--",
        line_color="",
        marker="o",
        marker_size=8.0,
        marker_face_color="",
        marker_edge_color="green",
        marker_fill=True,
    )

    assert ds.line_width == 3.5
    assert ds.line_style == "--"
    assert ds.line_color == "black"
    assert ds.marker == "o"
    assert ds.marker_size == 8.0
    assert ds.marker_face_color == "black"
    assert ds.marker_edge_color == "green"
    assert ds.marker_fill is True


def test_plot_datasets_draws_errorbars_for_dx_dy():
    ds = Dataset(
        name="err",
        x=[0, 1, 2],
        y=[1, 2, 1.5],
        dx=[0.1, 0.1, 0.2],
        dy=[0.2, 0.3, 0.2],
    )
    backend = PlotBackend([ds], PlotState(None, None, None, None, True), None)

    fig, ax = plt.subplots()
    backend.plot_datasets(ax)

    assert len(ax.lines) >= 1
    assert len(ax.collections) > 0
    plt.close(fig)


def test_render_hardcopy_writes_png(tmp_path):
    output = tmp_path / "plot.png"
    datasets = [Dataset(name="a", x=[0, 1, 2], y=[1, 3, 2])]

    render_hardcopy(
        datasets=datasets,
        output_path=output,
        title="T",
        xlabel="X",
        ylabel="Y",
        world=None,
        autoscale=True,
        legend_labels=None,
    )

    assert output.exists()
    assert output.stat().st_size > 0


def test_render_draws_y_equals_x_plugin_with_alpha():
    backend = PlotBackend(
        [Dataset(name="a", x=[0, 1], y=[0.5, 1.5])],
        PlotState(None, None, None, [0.0, 2.0, 0.0, 2.0], False),
        None,
    )

    fig, ax = plt.subplots()
    backend.render(ax)
    base_line_count = len(ax.lines)
    base_collection_count = len(ax.collections)

    backend.enable_plugin(Y_EQUALS_X_PLUGIN_ID, alpha=0.33)
    backend.render(ax)

    assert len(ax.lines) >= base_line_count + 1
    assert len(ax.collections) >= base_collection_count + 1
    alphas = [c.get_alpha() for c in ax.collections if c.get_alpha() is not None]
    assert any(abs(a - 0.33) < 1e-9 for a in alphas)
    plt.close(fig)


def test_render_draws_linear_regression_plugin_line():
    ds = Dataset(name="lin", x=[0, 1, 2, 3], y=[1, 3, 5, 7])
    backend = PlotBackend([ds], PlotState(None, None, None, None, True), None)

    fig, ax = plt.subplots()
    backend.render(ax)
    base_line_count = len(ax.lines)

    backend.enable_plugin(LINEAR_REGRESSION_PLUGIN_ID, dataset_index=0, color="black")
    backend.render(ax)

    assert len(ax.lines) >= base_line_count + 1
    fit_line = ax.lines[-1]
    x_vals = fit_line.get_xdata().tolist()
    y_vals = fit_line.get_ydata().tolist()
    assert x_vals == [0, 3]
    assert y_vals == [1.0, 7.0]
    plt.close(fig)
