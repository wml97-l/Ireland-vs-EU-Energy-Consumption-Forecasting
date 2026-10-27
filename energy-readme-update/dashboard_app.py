"""
Interactive Panel dashboard: Ireland vs EU average energy and electricity use.

Run it live (hover updates the yearly table, the metric switch rescales the chart):

    pip install panel holoviews bokeh pandas
    panel serve dashboard_app.py --show

Changes from the notebook version (CA2_WIN_Part1.ipynb, "Interactive Dashboard"):
  * the EU average is now computed from the 27 EU countries only
    (the notebook averaged every country and region in merged.csv, including "World")
  * framewise=True so the y-axis rescales when the metric changes
  * the hover stream now drives the chart directly, and the yearly table (now with the
    Ireland vs EU difference) updates in place as the mouse moves
  * hover tooltips on Ireland's data points
"""
import holoviews as hv
import pandas as pd
import panel as pn

hv.extension("bokeh")

EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland",
    "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovak Republic", "Slovenia", "Spain", "Sweden",
]

df = pd.read_csv("merged.csv")
eu = df[df["Country Name"].isin(EU_COUNTRIES)].reset_index(drop=True)

# Prepare data
ireland = eu[eu["Country Name"] == "Ireland"].reset_index(drop=True)
eu_avg = eu[eu["Country Name"] != "Ireland"].groupby("Year", as_index=False)[
    ["Energy use", "Electric Power Consumption"]
].mean()

variable = pn.widgets.Select(
    name="Select Metric",
    options={
        "Energy Use (kg oil equivalent)": "Energy use",
        "Electric Power Consumption (kWh)": "Electric Power Consumption",
    },
    value="Energy use",
)



def create_plot(metric):
    ylabel = {
        "Energy use": "Energy use (kg of oil equivalent per capita)",
        "Electric Power Consumption": "Electric power consumption (kWh per capita)",
    }.get(metric, metric)

    avg_line = hv.Curve(eu_avg, "Year", metric, label="EU Average").opts(color="blue", line_dash="dashed")
    ireland_line = hv.Curve(ireland, "Year", metric, label="Ireland").opts(color="green")
    points = hv.Scatter(ireland, "Year", metric).opts(
        color="orange", size=6, tools=["hover"],
        hover_tooltips=[("Year", "@Year"), ("Ireland", f"@{{{metric}}}{{0,0}}")],
    )

    return (avg_line * ireland_line * points).opts(
        title=f"Ireland vs EU Average: {[k for k, v in variable.options.items() if v == metric][0]}",
        ylabel=ylabel,
        width=600,
        height=400,
        legend_position="top_left",
        show_grid=True,
    )


UNITS = {"Energy use": "kg oil eq.", "Electric Power Consumption": "kWh"}


def table_markdown(x, metric):
    if x is None:
        return "Hover over the plot to see data"
    year = int(round(x))
    ireland_row = ireland[ireland["Year"] == year]
    eu_row = eu_avg[eu_avg["Year"] == year]
    if ireland_row.empty or eu_row.empty or ireland_row[metric].isna().all():
        return f"### Year: {year}\n\nNo data for this year"
    ie_val, eu_val = float(ireland_row[metric].iloc[0]), float(eu_row[metric].iloc[0])
    return (
        f"### Year: {year}\n\n"
        f"| | {UNITS[metric]} per person |\n|---|---:|\n"
        f"| **Ireland** | {ie_val:,.0f} |\n"
        f"| **EU average** | {eu_val:,.0f} |\n"
        f"| **Difference** | {ie_val - eu_val:+,.0f} ({ie_val / eu_val - 1:+.0%}) |"
    )


tap = hv.streams.PointerX(x=ireland["Year"].min())
metric_stream = hv.streams.Params(variable, ["value"], rename={"value": "metric"})
plot = hv.DynamicMap(lambda metric, x: create_plot(metric), streams=[metric_stream, tap]).opts(
    hv.opts.Curve(framewise=True), hv.opts.Scatter(framewise=True)
)
table = pn.pane.Markdown(table_markdown(tap.x, variable.value), width=300)


def _update_table(*_):
    table.object = table_markdown(tap.x, variable.value)


tap.param.watch(_update_table, "x")
variable.param.watch(_update_table, "value")

dashboard = pn.Column(
    "# Energy Consumption: Ireland vs. EU Average",
    variable,
    pn.Row(plot, table),
    sizing_mode="stretch_width",
)

dashboard.servable()
