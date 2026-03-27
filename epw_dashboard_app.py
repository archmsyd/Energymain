"""Streamlit app for exploring EPW weather files with interactive gauges and charts.

Run with:
    streamlit run epw_dashboard_app.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


EPW_COLUMNS = [
    "year", "month", "day", "hour", "minute", "data_source", "dry_bulb_c",
    "dew_point_c", "relative_humidity", "atmospheric_pressure_pa",
    "extraterrestrial_horizontal_radiation", "extraterrestrial_direct_normal_radiation",
    "horizontal_infrared_radiation", "global_horizontal_radiation",
    "direct_normal_radiation", "diffuse_horizontal_radiation",
    "global_horizontal_illuminance", "direct_normal_illuminance",
    "diffuse_horizontal_illuminance", "zenith_luminance", "wind_direction_deg",
    "wind_speed_m_s", "total_sky_cover", "opaque_sky_cover", "visibility_km",
    "ceiling_height_m", "present_weather_observation", "present_weather_codes",
    "precipitable_water_mm", "aerosol_optical_depth", "snow_depth_cm",
    "days_since_last_snowfall", "albedo", "liquid_precipitation_depth_mm",
    "liquid_precipitation_quantity_hr",
]


@dataclass
class EPWMetadata:
    city: str
    state: str
    country: str
    source: str
    wmo: str
    latitude: float
    longitude: float
    timezone: float
    elevation_m: float


def _parse_location_line(line: str) -> EPWMetadata:
    fields = [part.strip() for part in line.split(",")]
    if len(fields) < 10 or fields[0] != "LOCATION":
        raise ValueError("Invalid EPW location header.")

    return EPWMetadata(
        city=fields[1],
        state=fields[2],
        country=fields[3],
        source=fields[4],
        wmo=fields[5],
        latitude=float(fields[6]),
        longitude=float(fields[7]),
        timezone=float(fields[8]),
        elevation_m=float(fields[9]),
    )


def load_epw(uploaded_file) -> tuple[EPWMetadata, pd.DataFrame]:
    raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    lines = raw.splitlines()
    if len(lines) < 9:
        raise ValueError("The file appears too short to be a valid EPW.")

    metadata = _parse_location_line(lines[0])
    df = pd.read_csv(
        pd.io.common.StringIO("\n".join(lines[8:])),
        header=None,
        names=EPW_COLUMNS,
    )

    # EPW hour is 1-24; normalize to 0-23 for timestamp creation.
    normalized_hour = (df["hour"] - 1).clip(lower=0)
    df["timestamp"] = pd.to_datetime(
        {
            "year": df["year"],
            "month": df["month"],
            "day": df["day"],
            "hour": normalized_hour,
            "minute": 0,
        },
        errors="coerce",
    )
    df = df.dropna(subset=["timestamp"]).copy()

    numeric_columns = [
        "dry_bulb_c", "dew_point_c", "relative_humidity", "wind_speed_m_s",
        "global_horizontal_radiation", "direct_normal_radiation",
        "diffuse_horizontal_radiation", "atmospheric_pressure_pa",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["month_name"] = df["timestamp"].dt.strftime("%b")
    return metadata, df


def gauge(value: float, min_value: float, max_value: float, title: str, suffix: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": f" {suffix}"},
            title={"text": title},
            gauge={
                "axis": {"range": [min_value, max_value]},
                "bar": {"color": "#4f46e5"},
                "bgcolor": "#f3f4f6",
                "borderwidth": 1,
                "bordercolor": "#d1d5db",
                "steps": [
                    {"range": [min_value, (min_value + max_value) * 0.5], "color": "#e0e7ff"},
                    {"range": [(min_value + max_value) * 0.5, max_value], "color": "#c7d2fe"},
                ],
            },
        )
    )
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=35, b=5))
    return fig


def build_summary(df: pd.DataFrame) -> Dict[str, float]:
    return {
        "avg_temp": float(df["dry_bulb_c"].mean()),
        "avg_rh": float(df["relative_humidity"].mean()),
        "avg_wind": float(df["wind_speed_m_s"].mean()),
        "avg_ghi": float(df["global_horizontal_radiation"].mean()),
        "temp_min": float(df["dry_bulb_c"].min()),
        "temp_max": float(df["dry_bulb_c"].max()),
    }


def monthly_analytics(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(df["timestamp"].dt.month)
        .agg(
            avg_temp_c=("dry_bulb_c", "mean"),
            avg_rh=("relative_humidity", "mean"),
            avg_wind_m_s=("wind_speed_m_s", "mean"),
            avg_ghi=("global_horizontal_radiation", "mean"),
        )
        .reset_index(names="month")
    )
    grouped["month_name"] = pd.to_datetime(grouped["month"], format="%m").dt.strftime("%b")
    return grouped


def main() -> None:
    st.set_page_config(page_title="EPW World-Dominance Gauge Cluster", layout="wide")
    st.title("🌍 EPW Weather Analytics · World-Dominance Gauge Cluster")
    st.caption("Upload any .epw file to inspect location-aware weather analytics.")

    uploaded_file = st.file_uploader("Drop an EPW file", type=["epw"])
    if not uploaded_file:
        st.info("Upload an `.epw` file to get started.")
        return

    try:
        metadata, df = load_epw(uploaded_file)
    except Exception as exc:
        st.error(f"Failed to parse EPW file: {exc}")
        return

    summary = build_summary(df)

    st.subheader("Site & Climate Metadata")
    info_cols = st.columns(4)
    info_cols[0].metric("City", metadata.city)
    info_cols[1].metric("Country", metadata.country)
    info_cols[2].metric("Latitude", f"{metadata.latitude:.3f}°")
    info_cols[3].metric("Longitude", f"{metadata.longitude:.3f}°")

    map_df = pd.DataFrame(
        {
            "lat": [metadata.latitude],
            "lon": [metadata.longitude],
            "name": [f"{metadata.city}, {metadata.country}"],
        }
    )
    st.map(map_df, size=20)

    st.subheader("Gauge Cluster")
    g1, g2, g3, g4 = st.columns(4)
    g1.plotly_chart(gauge(summary["avg_temp"], -30, 50, "Avg Dry Bulb", "°C"), use_container_width=True)
    g2.plotly_chart(gauge(summary["avg_rh"], 0, 100, "Avg Relative Humidity", "%"), use_container_width=True)
    g3.plotly_chart(gauge(summary["avg_wind"], 0, 20, "Avg Wind Speed", "m/s"), use_container_width=True)
    g4.plotly_chart(gauge(summary["avg_ghi"], 0, 1000, "Avg Global Hor. Rad.", "W/m²"), use_container_width=True)

    st.subheader("Time-Series Explorer")
    metric_options: Dict[str, str] = {
        "Dry Bulb Temperature (°C)": "dry_bulb_c",
        "Dew Point (°C)": "dew_point_c",
        "Relative Humidity (%)": "relative_humidity",
        "Wind Speed (m/s)": "wind_speed_m_s",
        "Global Horizontal Radiation (W/m²)": "global_horizontal_radiation",
    }
    selection = st.selectbox("Choose metric", options=list(metric_options.keys()))
    metric_col = metric_options[selection]

    ts_fig = px.line(
        df.sort_values("timestamp"),
        x="timestamp",
        y=metric_col,
        title=f"{selection} across the year",
        template="plotly_white",
    )
    st.plotly_chart(ts_fig, use_container_width=True)

    st.subheader("Monthly Analytics")
    monthly = monthly_analytics(df)
    monthly_fig = px.bar(
        monthly,
        x="month_name",
        y=["avg_temp_c", "avg_rh", "avg_wind_m_s", "avg_ghi"],
        barmode="group",
        title="Monthly average climate indicators",
        labels={"value": "Average", "month_name": "Month", "variable": "Metric"},
        template="plotly_white",
    )
    st.plotly_chart(monthly_fig, use_container_width=True)

    st.subheader("Raw Weather Data")
    st.dataframe(df.head(200), use_container_width=True)


if __name__ == "__main__":
    main()
