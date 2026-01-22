"""
Report generation module for Ising Quant System.
Generates HTML and CSV reports from portfolio data.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from jinja2 import Template

from ising_quant.config import Config
from ising_quant.risk import RiskCalculator


class ReportGenerator:
    """Generate reports from portfolio data."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize report generator.

        Args:
            config: Configuration object. If None, creates new Config.
        """
        self.config = config or Config()
        self.risk_calc = RiskCalculator(config)

        # Ensure reports directory exists
        self.reports_dir = Path(self.config.output_db).parent / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(
        self, dailydata_df: pd.DataFrame, summary_df: pd.DataFrame
    ) -> str:
        """
        Generate HTML report from data.

        Args:
            dailydata_df: DailyData DataFrame.
            summary_df: PortfolioSummary DataFrame.

        Returns:
            Path to generated HTML file.
        """
        print("Generating HTML report...")

        # Calculate metrics
        metrics = self.risk_calc.calculate_metrics(summary_df)

        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        # Generate HTML
        html_content = self._create_html(dailydata_df, summary_df, metrics, timestamp)

        # Save to file
        report_path = self.reports_dir / report_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report generated: {report_path}")
        return str(report_path)

    def generate_csv_exports(self, dailydata_df: pd.DataFrame, summary_df: pd.DataFrame):
        """
        Generate CSV exports of data.

        Args:
            dailydata_df: DailyData DataFrame.
            summary_df: PortfolioSummary DataFrame.
        """
        print("Generating CSV exports...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export DailyData
        if not dailydata_df.empty:
            csv_path = self.reports_dir / f"dailydata_{timestamp}.csv"
            dailydata_df.to_csv(csv_path, index=False)
            print(f"DailyData CSV exported: {csv_path}")

        # Export Summary
        if not summary_df.empty:
            csv_path = self.reports_dir / f"summary_{timestamp}.csv"
            summary_df.to_csv(csv_path, index=False)
            print(f"Summary CSV exported: {csv_path}")

    def _create_html(
        self,
        dailydata_df: pd.DataFrame,
        summary_df: pd.DataFrame,
        metrics: dict,
        timestamp: str,
    ) -> str:
        """Create HTML content for report."""

        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ising Quant System - Portfolio Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
        }
        .header p {
            margin: 0;
            opacity: 0.9;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            font-weight: 600;
        }
        .metric-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        .metric-card .value.positive {
            color: #10b981;
        }
        .metric-card .value.negative {
            color: #ef4444;
        }
        .section {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section h2 {
            margin: 0 0 20px 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background-color: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        tr:hover {
            background-color: #f9fafb;
        }
        .footer {
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 14px;
        }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Ising Quant System</h1>
        <p>Portfolio Performance Report</p>
        <p style="font-size: 14px; margin-top: 10px;">Generated: {{ timestamp }}</p>
    </div>

    <div class="metrics-grid">
        {% if metrics.current_value %}
        <div class="metric-card">
            <h3>Current Value</h3>
            <div class="value">R$ {{ "%.2f"|format(metrics.current_value) }}</div>
        </div>
        {% endif %}

        {% if metrics.total_return_pct %}
        <div class="metric-card">
            <h3>Total Return</h3>
            <div class="value {{ 'positive' if metrics.total_return_pct > 0 else 'negative' }}">
                {{ "%.2f"|format(metrics.total_return_pct) }}%
            </div>
        </div>
        {% endif %}

        {% if metrics.max_drawdown_pct %}
        <div class="metric-card">
            <h3>Max Drawdown</h3>
            <div class="value negative">{{ "%.2f"|format(metrics.max_drawdown_pct) }}%</div>
        </div>
        {% endif %}

        {% if metrics.sharpe_ratio %}
        <div class="metric-card">
            <h3>Sharpe Ratio</h3>
            <div class="value {{ 'positive' if metrics.sharpe_ratio > 1 else '' }}">
                {{ "%.2f"|format(metrics.sharpe_ratio) }}
            </div>
        </div>
        {% endif %}

        {% if metrics.annual_volatility_pct %}
        <div class="metric-card">
            <h3>Annual Volatility</h3>
            <div class="value">{{ "%.2f"|format(metrics.annual_volatility_pct) }}%</div>
        </div>
        {% endif %}

        {% if metrics.win_rate_pct %}
        <div class="metric-card">
            <h3>Win Rate</h3>
            <div class="value">{{ "%.1f"|format(metrics.win_rate_pct) }}%</div>
        </div>
        {% endif %}
    </div>

    <div class="section">
        <h2>📈 Portfolio Summary</h2>
        {% if summary_html %}
        {{ summary_html|safe }}
        {% else %}
        <p>No portfolio summary data available.</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>📋 Recent Transactions</h2>
        {% if dailydata_html %}
        {{ dailydata_html|safe }}
        {% else %}
        <p>No transaction data available.</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>📊 All Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            {% for key, value in metrics.items() %}
            <tr>
                <td>{{ key.replace('_', ' ').title() }}</td>
                <td>
                    {% if 'pct' in key %}
                        {{ "%.2f"|format(value) }}%
                    {% elif 'value' in key or 'profit' in key %}
                        R$ {{ "%.2f"|format(value) }}
                    {% elif 'ratio' in key %}
                        {{ "%.3f"|format(value) }}
                    {% elif 'date' in key %}
                        {{ value }}
                    {% else %}
                        {{ value }}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="footer">
        <p><strong>Ising Quant System</strong> | Asymptotic Capital</p>
        <p style="font-size: 12px; margin-top: 5px;">
            This report is for informational purposes only and does not constitute financial advice.
        </p>
    </div>
</body>
</html>
"""

        # Convert DataFrames to HTML
        summary_html = ""
        if not summary_df.empty:
            # Show last 20 rows
            display_df = summary_df.tail(20).copy()
            summary_html = display_df.to_html(index=False, classes="data-table")

        dailydata_html = ""
        if not dailydata_df.empty:
            # Show last 50 rows
            display_df = dailydata_df.tail(50).copy()
            dailydata_html = display_df.to_html(index=False, classes="data-table")

        # Render template
        template = Template(html_template)
        html = template.render(
            timestamp=timestamp,
            metrics=metrics,
            summary_html=summary_html,
            dailydata_html=dailydata_html,
        )

        return html
