import flet as ft
import locale  # used to format balance and numbers
import time
import random

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

CUSTOM_TEXT_COLOR = ft.colors.GREY
CUSTOM_RED_COLOR = ft.colors.RED
CUSTOM_GREEN_COLOR = ft.colors.GREEN
CUSTOM_BLUE_COLOR = ft.colors.BLUE
CUSTOM_YELLOW_COLOR = ft.colors.YELLOW
CUSTOM_BGCOLOR = "#1f2128"


base_chart_style: dict = {
    "expand": True,
    "tooltip_bgcolor": ft.colors.with_opacity(0.8, ft.colors.WHITE),
    "left_axis": ft.ChartAxis(labels_size=50),
    "bottom_axis": ft.ChartAxis(labels_interval=1, labels_size=40),
    "horizontal_grid_lines": ft.ChartGridLines(
        interval=10, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
    ),
}


class BaseChart(ft.LineChart):
    def __init__(self, line_color: str) -> None:
        super().__init__(**base_chart_style)

        # create empty list to store coordinates
        self.points: list = []

        # set the min and max X axis
        self.min_x = (
            int(min(self.points, key=lambda x: x[0][0])) if self.points else None
        )

        self.max_x = (
            int(max(self.points, key=lambda x: x[0][0])) if self.points else None
        )

        # this is the main line to be displayed on the UI
        self.line = ft.LineChartData(
            color=line_color,  # red for OUT, green for IN
            stroke_width=2,
            stroke_cap_round=True,
            curved=True,
            # some gradient styling:
            below_line_gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.colors.with_opacity(0.25, line_color),
                    "transparent",
                ],
            ),
        )

        self.line.data_points = self.points
        self.data_series = [self.line]

    # create a method that appends the data from the tracker to the charts
    def create_data_points(self, x, y) -> None:
        self.points.append(
            ft.LineChartDataPoint(
                x,
                y,
                selected_below_line=ft.ChartPointLine(
                    width=0.5, color="white54", dash_pattern=[2, 4]
                ),
                selected_point=ft.ChartCirclePoint(stroke_width=1),
            ),
        )
        self.update()


in_style: dict = {
    "expand": 1,
    "bgcolor": "#17181d",
    "border_radius": 10,
    "padding": 30,
}


class GraphIn(ft.Container):
    def __init__(self) -> None:
        super().__init__(**in_style)
        self.chart = BaseChart(line_color=CUSTOM_GREEN_COLOR)  # "teal600"
        self.content = self.chart


out_style: dict = {
    "expand": 1,
    "bgcolor": "#17181d",
    "border_radius": 10,
    "padding": 30,
}


class GraphOut(ft.Container):

    def __init__(self) -> None:
        super().__init__(**out_style)
        self.chart = BaseChart(line_color=CUSTOM_RED_COLOR)  # "red500"
        self.content = self.chart


tracker_style: dict = {
    "main": {
        "expand": True,
        "bgcolor": "#17181d",
        "border_radius": 10,
    },
    "balance": {
        "size": 48,
        "weight": "bold",
        "color": CUSTOM_TEXT_COLOR,
    },
    # styling for input field
    "input": {
        "width": 220,
        "height": 40,
        "bgcolor": "#17181d",
        "border_radius": 10,
        "border_width": 1,
        "border_color": "white12",
        "cursor_height": 24,
        "content_padding": 10,
        "text_align": "center",
        "color": CUSTOM_TEXT_COLOR,
        "autofocus": True,
    },
    # styling for add button
    "add": {
        "icon": ft.icons.ADD,
        "bgcolor": CUSTOM_BGCOLOR,
        "icon_color": "teal600",
        "icon_size": 16,
        "scale": ft.transform.Scale(0.8),
    },
    # styling for subtract button
    "subtract": {
        "icon": ft.icons.REMOVE,
        "bgcolor": CUSTOM_BGCOLOR,
        "icon_color": "red600",
        "icon_size": 16,
        "scale": ft.transform.Scale(0.8),
    },
    # styling for the datatable
    "data_table": {
        "columns": [
            ft.DataColumn(ft.Text("Timestamp", weight="w900", color=CUSTOM_TEXT_COLOR)),
            ft.DataColumn(
                ft.Text("Amount", weight="w900", color=CUSTOM_TEXT_COLOR), numeric=True
            ),
        ],
        "width": 380,
        "heading_row_height": 35,
        "data_row_max_height": 40,
    },
    # styling for the data_table_container
    "data_table_container": {
        "expand": True,
        "width": 450,
        "padding": 10,
        "border_radius": ft.border_radius.only(top_left=10, top_right=10),
        "shadow": ft.BoxShadow(
            spread_radius=8,
            blur_radius=15,
            color=ft.colors.with_opacity(0.15, "black"),
            offset=ft.Offset(4, 4),
        ),
        "bgcolor": ft.colors.with_opacity(0.75, "#1f2128"),
    },
    #
}


class Tracker(ft.Container):
    def __init__(self, _in: object, _out: object) -> None:
        super().__init__(**tracker_style.get("main"))
        self._in: object = _in
        self._out: object = _out

        self.counter = 0.0
        self.balance = ft.Text(
            locale.currency(self.counter, grouping=True), **tracker_style.get("balance")
        )

        self.input = ft.TextField(**tracker_style.get("input"))

        self.add = ft.IconButton(
            **tracker_style.get("add"),
            data=True,
            on_click=lambda e: self.update_balance(e),
        )
        self.subtract = ft.IconButton(
            **tracker_style.get("subtract"),
            data=False,
            on_click=lambda e: self.update_balance(e),
        )

        self.table = ft.DataTable(**tracker_style.get("data_table"))

        self.content = ft.Column(
            horizontal_alignment="center",
            controls=[
                ft.Divider(height=15, color="transparent"),
                ft.Text(
                    "Total Balance", size=11, weight="w900", color=CUSTOM_TEXT_COLOR
                ),
                ft.Row(alignment="center", controls=[self.balance]),
                ft.Divider(height=15, color="transparent"),
                ft.Row(
                    alignment="center", controls=[self.subtract, self.input, self.add]
                ),
                ft.Divider(height=25, color="transparent"),
                ft.Container(
                    **tracker_style.get("data_table_container"),
                    content=ft.Column(
                        expand=True,
                        scroll="hidden",
                        controls=[self.table],
                    ),
                ),
            ],
        )

        # for show purposes
        self.x = 0

    # first, a method to update the data table
    def update_table(self, amount: float, sign: bool) -> int:
        timestamp = int(time.time())
        data = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(timestamp)),
                ft.DataCell(
                    ft.Text(
                        locale.currency(amount, grouping=True),
                        color="teal" if sign else "red",
                        # the condition of the color proerty will set the color based on the boolean of sign argument
                    )
                ),
            ]
        )
        self.table.rows.append(data)
        self.table.update()
        return timestamp

    def update_balance(self, event) -> None:

        # create an list of randomics values for tests
        test_values = self.create_random_list(200)

        # testing all values of the list
        for value in test_values:
            # update the balance
            self.input.value = str(value)
            self.input.update()
            
            # 1. check to see if input is not empty and value is digists
            if self.input.value and self.input.value.isdigit():
                # 2. Get the inputed value and change it to a float
                inputed_value: float = float(self.input.value)
                # 3. Check to see if the value is positive or negative (if button clicked was + or -)
                if event.control.data:
                    self.counter += inputed_value
                    self.update_table(inputed_value, True)
                    # to show the amounts on the charts, we can do the folloing ...
                    # _in is the instance of GraphIN class
                    # chart is the self.chart in the base class
                    # create_data_points is a method in the BaseChart class that creates a coordinate => method takes two arguments: x and y
                    self._in.chart.create_data_points(
                        x=self.x,
                        y=inputed_value,
                    )
                    self.x += 1
                else:
                    self.counter -= inputed_value
                    self.update_table(inputed_value, False)
                    # change the _IN to _OUT
                    self._out.chart.create_data_points(
                        x=self.x,
                        y=inputed_value,
                    )
                    self.x -= 1

                # 4. Update the UI balance and update the UI
                self.balance.value = locale.currency(self.counter, grouping=True)
                self.balance.update()
                # clear the input_field
                self.input.value = ""
                self.input.update()

            elif not self.input.value.isdigit():
                # 5. If the input is empty or not a digit, clear the input_field
                self.input.value = ""
                self.input.update()

            # moving focus to input_field
            self.input.focus()

            # if counter is negative, change the color the text in the balance
            if self.counter < 0:
                self.balance.color = CUSTOM_RED_COLOR
            else:
                self.balance.color = CUSTOM_TEXT_COLOR
            self.balance.update()

    # create an random list of values for tests
    def create_random_list(self, length: int) -> list:
        return [random.randint(50, 100) for _ in range(length)]
    


def main(page: ft.Page):
    page.title = "My Financial Control App"
    # page.theme_mode = ft.ThemeMode.SYSTEM
    page.bgcolor = CUSTOM_BGCOLOR
    page.padding = 30

    graph_in: ft.Container = GraphIn()
    graph_out: ft.Container = GraphOut()
    tracker: ft.Container = Tracker(_in=graph_in, _out=graph_out)

    page.add(
        ft.Row(
            expand=True,
            controls=[
                tracker,
                ft.Column(
                    expand=2,  # True,  # expand=2
                    controls=[graph_in, graph_out],
                ),
            ],
        )
    )

    page.update()


# execute the app
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
