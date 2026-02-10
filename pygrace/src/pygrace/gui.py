from __future__ import annotations

import sys

import matplotlib

from .backend import Y_EQUALS_X_PLUGIN_ID, PlotBackend, PlotState, render_hardcopy
from .data import Dataset


def launch_gui(
    datasets: list[Dataset],
    title: str | None,
    xlabel: str | None,
    ylabel: str | None,
    world: list[float] | None,
    autoscale: bool,
    legend_labels: list[str] | None,
) -> None:
    matplotlib.use("QtAgg")
    from PySide6 import QtCore, QtWidgets
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    fig, ax = plt.subplots()
    canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(canvas, None)

    backend = PlotBackend(
        datasets=datasets,
        state=PlotState(
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            world=world,
            autoscale=autoscale,
        ),
        legend_labels=legend_labels,
    )
    state = backend.state
    backend.plot_datasets(ax)
    backend.apply_axes_state(ax)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("PyGrace")

    central = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(central)
    layout.addWidget(toolbar)
    layout.addWidget(canvas)
    window.setCentralWidget(central)

    controls = QtWidgets.QWidget()
    form = QtWidgets.QFormLayout(controls)

    state.title_size = ax.title.get_fontsize()
    state.xlabel_size = ax.xaxis.label.get_size()
    state.ylabel_size = ax.yaxis.label.get_size()
    state.xtick_size = ax.xaxis.get_ticklabels()[0].get_size() if ax.xaxis.get_ticklabels() else 10
    state.ytick_size = ax.yaxis.get_ticklabels()[0].get_size() if ax.yaxis.get_ticklabels() else 10

    def refresh() -> None:
        backend.render(ax)
        canvas.draw_idle()

    axis_dialog = QtWidgets.QDialog(window)
    axis_dialog.setWindowTitle("Axes")
    axis_dialog.setModal(False)
    axis_layout = QtWidgets.QFormLayout(axis_dialog)

    title_edit = QtWidgets.QLineEdit(state.title or "")
    xlabel_edit = QtWidgets.QLineEdit(state.xlabel or "")
    ylabel_edit = QtWidgets.QLineEdit(state.ylabel or "")

    def update_title(text: str) -> None:
        state.title = text
        refresh()

    def update_xlabel(text: str) -> None:
        state.xlabel = text
        refresh()

    def update_ylabel(text: str) -> None:
        state.ylabel = text
        refresh()

    title_edit.textChanged.connect(update_title)
    xlabel_edit.textChanged.connect(update_xlabel)
    ylabel_edit.textChanged.connect(update_ylabel)

    axis_layout.addRow("Title", title_edit)
    axis_layout.addRow("X label", xlabel_edit)
    axis_layout.addRow("Y label", ylabel_edit)

    title_size_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
    title_size_slider.setRange(8, 48)
    title_size_slider.setValue(int(state.title_size or 12))
    title_size_value = QtWidgets.QLabel(str(title_size_slider.value()))

    def handle_title_size(value: int) -> None:
        title_size_value.setText(str(value))
        state.title_size = value
        refresh()

    title_size_slider.valueChanged.connect(handle_title_size)
    title_size_row = QtWidgets.QWidget()
    title_size_layout = QtWidgets.QHBoxLayout(title_size_row)
    title_size_layout.setContentsMargins(0, 0, 0, 0)
    title_size_layout.addWidget(title_size_slider)
    title_size_layout.addWidget(title_size_value)
    axis_layout.addRow("Title size", title_size_row)

    link_label_sizes = QtWidgets.QCheckBox("Link label sizes")
    link_label_sizes.setChecked(True)

    def make_size_slider(value: int) -> QtWidgets.QSlider:
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setRange(6, 36)
        slider.setValue(value)
        slider.setSingleStep(1)
        return slider

    xlabel_slider = make_size_slider(int(state.xlabel_size or 10))
    ylabel_slider = make_size_slider(int(state.ylabel_size or 10))
    xlabel_value = QtWidgets.QLabel(str(xlabel_slider.value()))
    ylabel_value = QtWidgets.QLabel(str(ylabel_slider.value()))

    def set_label_sizes(x_size: int, y_size: int) -> None:
        state.xlabel_size = x_size
        state.ylabel_size = y_size
        refresh()

    def handle_xlabel_change(value: int) -> None:
        xlabel_value.setText(str(value))
        if link_label_sizes.isChecked():
            ylabel_slider.blockSignals(True)
            ylabel_slider.setValue(value)
            ylabel_slider.blockSignals(False)
            ylabel_value.setText(str(value))
            set_label_sizes(value, value)
        else:
            set_label_sizes(value, ylabel_slider.value())

    def handle_ylabel_change(value: int) -> None:
        ylabel_value.setText(str(value))
        if link_label_sizes.isChecked():
            xlabel_slider.blockSignals(True)
            xlabel_slider.setValue(value)
            xlabel_slider.blockSignals(False)
            xlabel_value.setText(str(value))
            set_label_sizes(value, value)
        else:
            set_label_sizes(xlabel_slider.value(), value)

    xlabel_slider.valueChanged.connect(handle_xlabel_change)
    ylabel_slider.valueChanged.connect(handle_ylabel_change)

    xlabel_row = QtWidgets.QWidget()
    xlabel_row_layout = QtWidgets.QHBoxLayout(xlabel_row)
    xlabel_row_layout.setContentsMargins(0, 0, 0, 0)
    xlabel_row_layout.addWidget(xlabel_slider)
    xlabel_row_layout.addWidget(xlabel_value)

    ylabel_row = QtWidgets.QWidget()
    ylabel_row_layout = QtWidgets.QHBoxLayout(ylabel_row)
    ylabel_row_layout.setContentsMargins(0, 0, 0, 0)
    ylabel_row_layout.addWidget(ylabel_slider)
    ylabel_row_layout.addWidget(ylabel_value)

    axis_layout.addRow(link_label_sizes)
    axis_layout.addRow("X label size", xlabel_row)
    axis_layout.addRow("Y label size", ylabel_row)

    link_tick_sizes = QtWidgets.QCheckBox("Link tick sizes")
    link_tick_sizes.setChecked(True)

    xtick_slider = make_size_slider(int(state.xtick_size or 10))
    ytick_slider = make_size_slider(int(state.ytick_size or 10))
    xtick_value = QtWidgets.QLabel(str(xtick_slider.value()))
    ytick_value = QtWidgets.QLabel(str(ytick_slider.value()))

    def set_tick_sizes(x_size: int, y_size: int) -> None:
        state.xtick_size = x_size
        state.ytick_size = y_size
        refresh()

    def handle_xtick_change(value: int) -> None:
        xtick_value.setText(str(value))
        if link_tick_sizes.isChecked():
            ytick_slider.blockSignals(True)
            ytick_slider.setValue(value)
            ytick_slider.blockSignals(False)
            ytick_value.setText(str(value))
            set_tick_sizes(value, value)
        else:
            set_tick_sizes(value, ytick_slider.value())

    def handle_ytick_change(value: int) -> None:
        ytick_value.setText(str(value))
        if link_tick_sizes.isChecked():
            xtick_slider.blockSignals(True)
            xtick_slider.setValue(value)
            xtick_slider.blockSignals(False)
            xtick_value.setText(str(value))
            set_tick_sizes(value, value)
        else:
            set_tick_sizes(xtick_slider.value(), value)

    xtick_slider.valueChanged.connect(handle_xtick_change)
    ytick_slider.valueChanged.connect(handle_ytick_change)

    xtick_row = QtWidgets.QWidget()
    xtick_layout = QtWidgets.QHBoxLayout(xtick_row)
    xtick_layout.setContentsMargins(0, 0, 0, 0)
    xtick_layout.addWidget(xtick_slider)
    xtick_layout.addWidget(xtick_value)

    ytick_row = QtWidgets.QWidget()
    ytick_layout = QtWidgets.QHBoxLayout(ytick_row)
    ytick_layout.setContentsMargins(0, 0, 0, 0)
    ytick_layout.addWidget(ytick_slider)
    ytick_layout.addWidget(ytick_value)

    axis_layout.addRow(link_tick_sizes)
    axis_layout.addRow("X tick size", xtick_row)
    axis_layout.addRow("Y tick size", ytick_row)

    limits_group = QtWidgets.QGroupBox("Limits")
    limits_layout = QtWidgets.QFormLayout(limits_group)
    limits_enabled = QtWidgets.QCheckBox("Use limits")
    limits_enabled.setChecked(state.world is not None)
    x_min_spin = QtWidgets.QDoubleSpinBox()
    x_max_spin = QtWidgets.QDoubleSpinBox()
    y_min_spin = QtWidgets.QDoubleSpinBox()
    y_max_spin = QtWidgets.QDoubleSpinBox()
    for spin in (x_min_spin, x_max_spin, y_min_spin, y_max_spin):
        spin.setRange(-1e12, 1e12)
        spin.setDecimals(6)

    if state.world:
        x_min_spin.setValue(state.world[0])
        x_max_spin.setValue(state.world[1])
        y_min_spin.setValue(state.world[2])
        y_max_spin.setValue(state.world[3])

    def apply_limits() -> None:
        if limits_enabled.isChecked():
            state.world = [
                x_min_spin.value(),
                x_max_spin.value(),
                y_min_spin.value(),
                y_max_spin.value(),
            ]
            state.autoscale = False
        else:
            state.world = None
            state.autoscale = True
        refresh()

    limits_enabled.stateChanged.connect(lambda _s: apply_limits())
    for spin in (x_min_spin, x_max_spin, y_min_spin, y_max_spin):
        spin.editingFinished.connect(apply_limits)

    limits_layout.addRow(limits_enabled)
    limits_layout.addRow("X min", x_min_spin)
    limits_layout.addRow("X max", x_max_spin)
    limits_layout.addRow("Y min", y_min_spin)
    limits_layout.addRow("Y max", y_max_spin)
    axis_layout.addRow(limits_group)

    ticks_group = QtWidgets.QGroupBox("Ticks")
    ticks_layout = QtWidgets.QFormLayout(ticks_group)
    major_enabled = QtWidgets.QCheckBox("Use major tick spacing")
    minor_enabled = QtWidgets.QCheckBox("Enable minor ticks")
    major_enabled.setChecked(False)
    minor_enabled.setChecked(False)

    x_major_spin = QtWidgets.QDoubleSpinBox()
    y_major_spin = QtWidgets.QDoubleSpinBox()
    x_minor_spin = QtWidgets.QDoubleSpinBox()
    y_minor_spin = QtWidgets.QDoubleSpinBox()
    for spin in (x_major_spin, y_major_spin, x_minor_spin, y_minor_spin):
        spin.setRange(0.0, 1e9)
        spin.setDecimals(6)
        spin.setSingleStep(0.1)

    def apply_ticks() -> None:
        if major_enabled.isChecked() and x_major_spin.value() > 0:
            state.x_major_step = x_major_spin.value()
        else:
            state.x_major_step = None
        if major_enabled.isChecked() and y_major_spin.value() > 0:
            state.y_major_step = y_major_spin.value()
        else:
            state.y_major_step = None
        state.minor_ticks = minor_enabled.isChecked()
        if state.minor_ticks and x_minor_spin.value() > 0:
            state.x_minor_step = x_minor_spin.value()
        else:
            state.x_minor_step = None
        if state.minor_ticks and y_minor_spin.value() > 0:
            state.y_minor_step = y_minor_spin.value()
        else:
            state.y_minor_step = None
        refresh()

    major_enabled.stateChanged.connect(lambda _s: apply_ticks())
    minor_enabled.stateChanged.connect(lambda _s: apply_ticks())
    for spin in (x_major_spin, y_major_spin, x_minor_spin, y_minor_spin):
        spin.editingFinished.connect(apply_ticks)

    ticks_layout.addRow(major_enabled)
    ticks_layout.addRow("X major step", x_major_spin)
    ticks_layout.addRow("Y major step", y_major_spin)
    ticks_layout.addRow(minor_enabled)
    ticks_layout.addRow("X minor step", x_minor_spin)
    ticks_layout.addRow("Y minor step", y_minor_spin)
    axis_layout.addRow(ticks_group)

    dataset_list = QtWidgets.QListWidget()
    for ds in datasets:
        item = QtWidgets.QListWidgetItem(ds.name)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        dataset_list.addItem(item)

    name_edit = QtWidgets.QLineEdit()

    def update_selected_name() -> None:
        row = dataset_list.currentRow()
        if 0 <= row < len(datasets):
            name_edit.setText(datasets[row].name)
        else:
            name_edit.setText("")

    appearance_set = QtWidgets.QComboBox()
    for ds in datasets:
        appearance_set.addItem(ds.name)

    extrema_box = QtWidgets.QGroupBox("Align Extrema")
    extrema_layout = QtWidgets.QFormLayout(extrema_box)
    extrema_selectors: list[tuple[Dataset, QtWidgets.QComboBox]] = []

    def format_extrema_label(entry: tuple[str, int, float, float]) -> str:
        kind, idx, xval, yval = entry
        return f"{kind} @ i={idx}, x={xval:.4g}, y={yval:.4g}"

    def rebuild_extrema_selectors() -> None:
        for i in reversed(range(extrema_layout.rowCount())):
            extrema_layout.removeRow(i)
        extrema_selectors.clear()
        for ds in datasets:
            combo = QtWidgets.QComboBox()
            extrema = backend.extrema_for_dataset(ds)
            for entry in extrema:
                combo.addItem(format_extrema_label(entry), entry)
            extrema_layout.addRow(ds.name, combo)
            extrema_selectors.append((ds, combo))

    def apply_name_change(text: str) -> None:
        row = dataset_list.currentRow()
        if 0 <= row < len(datasets):
            backend.rename_dataset(row, text)
            item = dataset_list.item(row)
            if item is not None:
                item.setText(text)
            if 0 <= row < appearance_set.count():
                appearance_set.setItemText(row, text)
            refresh()
            rebuild_extrema_selectors()

    dataset_list.currentRowChanged.connect(lambda _idx: update_selected_name())
    name_edit.textChanged.connect(apply_name_change)

    def toggle_dataset(item: QtWidgets.QListWidgetItem) -> None:
        idx = dataset_list.row(item)
        backend.set_dataset_visible(idx, item.checkState() == QtCore.Qt.CheckState.Checked)
        refresh()

    dataset_list.itemChanged.connect(toggle_dataset)

    form.addRow("Datasets", dataset_list)
    form.addRow("Set name", name_edit)

    appearance_box = QtWidgets.QGroupBox("Set Appearance")
    appearance_layout = QtWidgets.QFormLayout(appearance_box)

    line_width_spin = QtWidgets.QDoubleSpinBox()
    line_width_spin.setRange(0.1, 10.0)
    line_width_spin.setSingleStep(0.1)

    line_style_combo = QtWidgets.QComboBox()
    line_style_combo.addItems(["-", "--", "-.", ":", "None"])

    line_color_edit = QtWidgets.QLineEdit()
    line_color_button = QtWidgets.QPushButton("Pick")

    marker_combo = QtWidgets.QComboBox()
    marker_combo.addItems(["o", "s", "^", "v", "D", "x", "+", ".", "None"])

    marker_size_spin = QtWidgets.QDoubleSpinBox()
    marker_size_spin.setRange(1.0, 20.0)
    marker_size_spin.setSingleStep(0.5)

    marker_face_edit = QtWidgets.QLineEdit()
    marker_face_button = QtWidgets.QPushButton("Pick")

    marker_edge_edit = QtWidgets.QLineEdit()
    marker_edge_button = QtWidgets.QPushButton("Pick")

    marker_fill_check = QtWidgets.QCheckBox("Fill marker")

    def current_appearance_index() -> int:
        return appearance_set.currentIndex()

    def apply_appearance_from_ui() -> None:
        idx = current_appearance_index()
        if not (0 <= idx < len(datasets)):
            return
        backend.set_dataset_appearance(
            idx,
            line_width=line_width_spin.value(),
            line_style=line_style_combo.currentText(),
            line_color=line_color_edit.text().strip(),
            marker=marker_combo.currentText(),
            marker_size=marker_size_spin.value(),
            marker_face_color=marker_face_edit.text().strip(),
            marker_edge_color=marker_edge_edit.text().strip(),
            marker_fill=marker_fill_check.isChecked(),
        )
        refresh()

    def load_appearance_into_ui() -> None:
        idx = current_appearance_index()
        if not (0 <= idx < len(datasets)):
            return
        ds = datasets[idx]
        line_width_spin.setValue(ds.line_width)
        line_style_combo.setCurrentText(ds.line_style)
        line_color_edit.setText(ds.line_color)
        marker_combo.setCurrentText(ds.marker)
        marker_size_spin.setValue(ds.marker_size)
        marker_face_edit.setText(ds.marker_face_color)
        marker_edge_edit.setText(ds.marker_edge_color)
        marker_fill_check.setChecked(ds.marker_fill)

    def pick_color(target: QtWidgets.QLineEdit) -> None:
        color = QtWidgets.QColorDialog.getColor(parent=window)
        if color.isValid():
            target.setText(color.name())
            apply_appearance_from_ui()

    line_color_button.clicked.connect(lambda: pick_color(line_color_edit))
    marker_face_button.clicked.connect(lambda: pick_color(marker_face_edit))
    marker_edge_button.clicked.connect(lambda: pick_color(marker_edge_edit))

    appearance_set.currentIndexChanged.connect(lambda _idx: load_appearance_into_ui())
    line_width_spin.valueChanged.connect(lambda _v: apply_appearance_from_ui())
    line_style_combo.currentIndexChanged.connect(lambda _i: apply_appearance_from_ui())
    line_color_edit.editingFinished.connect(apply_appearance_from_ui)
    marker_combo.currentIndexChanged.connect(lambda _i: apply_appearance_from_ui())
    marker_size_spin.valueChanged.connect(lambda _v: apply_appearance_from_ui())
    marker_face_edit.editingFinished.connect(apply_appearance_from_ui)
    marker_edge_edit.editingFinished.connect(apply_appearance_from_ui)
    marker_fill_check.stateChanged.connect(lambda _s: apply_appearance_from_ui())

    appearance_layout.addRow("Set", appearance_set)
    appearance_layout.addRow("Line width", line_width_spin)
    appearance_layout.addRow("Line style", line_style_combo)
    line_color_row = QtWidgets.QWidget()
    line_color_row_layout = QtWidgets.QHBoxLayout(line_color_row)
    line_color_row_layout.setContentsMargins(0, 0, 0, 0)
    line_color_row_layout.addWidget(line_color_edit)
    line_color_row_layout.addWidget(line_color_button)
    appearance_layout.addRow("Line color", line_color_row)
    appearance_layout.addRow("Marker", marker_combo)
    appearance_layout.addRow("Marker size", marker_size_spin)
    marker_face_row = QtWidgets.QWidget()
    marker_face_layout = QtWidgets.QHBoxLayout(marker_face_row)
    marker_face_layout.setContentsMargins(0, 0, 0, 0)
    marker_face_layout.addWidget(marker_face_edit)
    marker_face_layout.addWidget(marker_face_button)
    appearance_layout.addRow("Marker face", marker_face_row)
    marker_edge_row = QtWidgets.QWidget()
    marker_edge_layout = QtWidgets.QHBoxLayout(marker_edge_row)
    marker_edge_layout.setContentsMargins(0, 0, 0, 0)
    marker_edge_layout.addWidget(marker_edge_edit)
    marker_edge_layout.addWidget(marker_edge_button)
    appearance_layout.addRow("Marker edge", marker_edge_row)
    appearance_layout.addRow(marker_fill_check)

    appearance_dialog = QtWidgets.QDialog(window)
    appearance_dialog.setWindowTitle("Set Appearance")
    appearance_dialog.setModal(False)
    appearance_layout_container = QtWidgets.QVBoxLayout(appearance_dialog)
    appearance_layout_container.addWidget(appearance_box)
    appearance_dialog.setLayout(appearance_layout_container)

    rebuild_extrema_selectors()
    load_appearance_into_ui()

    def align_selected_extrema() -> None:
        selections: list[tuple[Dataset, tuple[str, int, float, float]]] = []
        for ds, combo in extrema_selectors:
            data = combo.currentData()
            if data is None:
                continue
            selections.append((ds, data))
        if not selections:
            return
        backend.align_extrema(selections)
        refresh()

    align_button = QtWidgets.QPushButton("Align Selected")
    align_button.clicked.connect(align_selected_extrema)
    extrema_layout.addRow(align_button)
    form.addRow(extrema_box)

    transform_edit = QtWidgets.QLineEdit()
    transform_edit.setPlaceholderText("e.g. y1 = y0 + 2, x2 = x0 * 0.5")
    transform_status = QtWidgets.QLabel("")

    def apply_transform() -> None:
        text = transform_edit.text().strip()
        if not text:
            return
        try:
            target_index = backend.apply_transform(text)
            if target_index >= dataset_list.count():
                target = datasets[target_index]
                item = QtWidgets.QListWidgetItem(target.name)
                item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                dataset_list.addItem(item)
                appearance_set.addItem(target.name)
            refresh()
            rebuild_extrema_selectors()
            transform_status.setText("Applied.")
        except Exception as exc:  # noqa: BLE001
            transform_status.setText(f"Error: {exc}")

    transform_button = QtWidgets.QPushButton("Apply Transform")
    transform_button.clicked.connect(apply_transform)
    form.addRow("Transform", transform_edit)
    form.addRow(transform_button)
    form.addRow(transform_status)

    export_button = QtWidgets.QPushButton("Export PNG")

    def export_png() -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            window, "Export PNG", "plot.png", "PNG Files (*.png)"
        )
        if path:
            fig.tight_layout()
            fig.savefig(path, dpi=150)

    export_button.clicked.connect(export_png)
    form.addRow(export_button)

    dock = QtWidgets.QDockWidget("Controls", window)
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(controls)
    dock.setWidget(scroll)
    window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock)

    menu = window.menuBar()
    menu.setNativeMenuBar(False)
    set_menu = menu.addMenu("Set")
    appearance_action = set_menu.addAction("Appearance...")
    axis_menu = menu.addMenu("Axis")
    axis_action = axis_menu.addAction("Axes...")
    plugins_menu = menu.addMenu("Plugins")

    def show_appearance_dialog() -> None:
        appearance_dialog.show()
        appearance_dialog.raise_()
        appearance_dialog.activateWindow()

    def show_axis_dialog() -> None:
        axis_dialog.show()
        axis_dialog.raise_()
        axis_dialog.activateWindow()

    def configure_plugin(plugin_id: str, plugin_name: str) -> None:
        dialog = QtWidgets.QDialog(window)
        dialog.setWindowTitle(plugin_name)
        layout = QtWidgets.QFormLayout(dialog)

        current = backend.get_plugin_config(plugin_id)
        enabled_default = current is not None and bool(current.get("enabled", True))
        alpha_default = float((current or {}).get("alpha", 0.15))

        enabled_check = QtWidgets.QCheckBox("Enabled")
        enabled_check.setChecked(enabled_default)
        alpha_spin = QtWidgets.QDoubleSpinBox()
        alpha_spin.setRange(0.0, 1.0)
        alpha_spin.setSingleStep(0.01)
        alpha_spin.setDecimals(2)
        alpha_spin.setValue(alpha_default)

        layout.addRow(enabled_check)
        if plugin_id == Y_EQUALS_X_PLUGIN_ID:
            layout.addRow("Alpha", alpha_spin)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        layout.addRow(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        if enabled_check.isChecked():
            config = {"enabled": True}
            if plugin_id == Y_EQUALS_X_PLUGIN_ID:
                config["alpha"] = float(alpha_spin.value())
            backend.enable_plugin(plugin_id, **config)
        else:
            backend.disable_plugin(plugin_id)
        refresh()

    appearance_action.triggered.connect(show_appearance_dialog)
    axis_action.triggered.connect(show_axis_dialog)
    for plugin_id, plugin_name in backend.available_plugins():
        action = plugins_menu.addAction(plugin_name)
        action.triggered.connect(
            lambda _checked=False, pid=plugin_id, pname=plugin_name: configure_plugin(pid, pname)
        )

    window.resize(1100, 700)
    window.show()
    app.exec()
