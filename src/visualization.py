"""
Visualization module for dollar price data using Plotly.
Provides interactive charts for financial time series data.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class ChartConfig:
    """Configuration for chart styling and behavior."""
    
    # Color palette for currencies/commodities
    COLORS = {
        'EUR': '#1f77b4',
        'GBP': '#ff7f0e',
        'JPY': '#2ca02c',
        'CHF': '#d62728',
        'CAD': '#9467bd',
        'AUD': '#8c564b',
        'GOLD': '#FFD700',
        'SILVER': '#C0C0C0',
        'OIL': '#000000',
        'default': '#007bff'
    }
    
    # Chart templates
    TEMPLATE = 'plotly_white'
    
    # Default figure size
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 600


class PriceVisualizer:
    """Visualizer for price history data."""
    
    def __init__(self, queries):
        """
        Initialize visualizer with queries instance.
        
        Args:
            queries: PriceQueries instance from src.queries
        """
        self.queries = queries
        self.config = ChartConfig()
    
    def _parse_period(self, period: str) -> tuple[date, date]:
        """
        Parse period string to start and end dates.
        
        Args:
            period: Period string (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            
        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = date.today()
        
        period_map = {
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1),
            '1m': timedelta(days=30),
            '3m': timedelta(days=90),
            '6m': timedelta(days=180),
            '1y': timedelta(days=365),
            '5y': timedelta(days=365*5),
        }
        
        if period not in period_map:
            raise ValueError(
                f"Invalid period: {period}. "
                f"Valid periods: {', '.join(period_map.keys())}"
            )
        
        start_date = end_date - period_map[period]
        return start_date, end_date
    
    def _get_color(self, name: str) -> str:
        """Get color for a currency/commodity."""
        return self.config.COLORS.get(name.upper(), self.config.COLORS['default'])
    
    def plot_exchange_rate(self, 
                          currency: str, 
                          period: str = '1y',
                          chart_type: str = 'line',
                          show_volume: bool = False,
                          save_path: Optional[str] = None) -> go.Figure:
        """
        Plot exchange rate history for a single currency.
        
        Args:
            currency: Currency code (e.g., EUR, GBP, JPY)
            period: Time period (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            chart_type: Type of chart ('line' or 'candlestick')
            show_volume: Whether to show volume subplot
            save_path: Optional path to save HTML file
            
        Returns:
            Plotly Figure object
        """
        start_date, end_date = self._parse_period(period)
        df = self.queries.get_exchange_rates(currency, start_date, end_date)
        
        if df.empty:
            raise ValueError(f"No data found for currency {currency} in period {period}")
        
        currency = currency.upper()
        color = self._get_color(currency)
        
        # Determine if OHLC data is available
        has_ohlc = all(col in df.columns for col in ['open', 'high', 'low', 'close'])
        has_ohlc = has_ohlc and df[['open', 'high', 'low', 'close']].notna().any().any()
        
        # Create subplots if volume is requested
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'USD/{currency} Exchange Rate', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # Add main price chart
        if chart_type == 'candlestick' and has_ohlc:
            if show_volume:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=f'USD/{currency}',
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=f'USD/{currency}',
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    )
                )
        else:
            # Use close price if available, otherwise rate
            price_col = 'close' if 'close' in df.columns else 'rate'
            if show_volume:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name=f'USD/{currency}',
                        line=dict(color=color, width=2),
                        hovertemplate='<b>%{x}</b><br>Rate: %{y:.4f}<extra></extra>'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name=f'USD/{currency}',
                        line=dict(color=color, width=2),
                        hovertemplate='<b>%{x}</b><br>Rate: %{y:.4f}<extra></extra>'
                    )
                )
        
        # Add volume if requested and available
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(128, 128, 128, 0.5)',
                    hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            template=self.config.TEMPLATE,
            title=f'USD/{currency} Exchange Rate - {period}',
            xaxis_title='Date',
            yaxis_title='Rate',
            hovermode='x unified',
            width=self.config.DEFAULT_WIDTH,
            height=self.config.DEFAULT_HEIGHT + (200 if show_volume else 0),
            showlegend=True
        )
        
        if show_volume:
            fig.update_yaxes(title_text='Rate', row=1, col=1)
            fig.update_yaxes(title_text='Volume', row=2, col=1)
        
        # Save if path provided
        if save_path:
            fig.write_html(save_path)
            print(f"Chart saved to {save_path}")
        
        return fig
    
    def plot_commodity_price(self,
                            commodity: str,
                            period: str = '1y',
                            chart_type: str = 'line',
                            show_volume: bool = False,
                            save_path: Optional[str] = None) -> go.Figure:
        """
        Plot commodity price history.
        
        Args:
            commodity: Commodity name (e.g., GOLD, OIL)
            period: Time period (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            chart_type: Type of chart ('line' or 'candlestick')
            show_volume: Whether to show volume subplot
            save_path: Optional path to save HTML file
            
        Returns:
            Plotly Figure object
        """
        start_date, end_date = self._parse_period(period)
        df = self.queries.get_commodity_prices(commodity=commodity, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for commodity {commodity} in period {period}")
        
        commodity = commodity.upper()
        color = self._get_color(commodity)
        
        # Determine if OHLC data is available
        has_ohlc = all(col in df.columns for col in ['open', 'high', 'low', 'close'])
        has_ohlc = has_ohlc and df[['open', 'high', 'low', 'close']].notna().any().any()
        
        # Get unit for title
        unit = df['unit'].iloc[0] if 'unit' in df.columns and not df['unit'].isna().all() else ''
        
        # Create subplots if volume is requested
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{commodity} Price', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # Add main price chart
        if chart_type == 'candlestick' and has_ohlc:
            if show_volume:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=commodity,
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=commodity,
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    )
                )
        else:
            # Use close price if available, otherwise price
            price_col = 'close' if 'close' in df.columns else 'price'
            if show_volume:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name=commodity,
                        line=dict(color=color, width=2),
                        hovertemplate=f'<b>%{{x}}</b><br>{commodity}: %{{y:.2f}} {unit}<extra></extra>'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name=commodity,
                        line=dict(color=color, width=2),
                        hovertemplate=f'<b>%{{x}}</b><br>{commodity}: %{{y:.2f}} {unit}<extra></extra>'
                    )
                )
        
        # Add volume if requested and available
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(128, 128, 128, 0.5)',
                    hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            template=self.config.TEMPLATE,
            title=f'{commodity} Price - {period}',
            xaxis_title='Date',
            yaxis_title=f'Price ({unit})' if unit else 'Price',
            hovermode='x unified',
            width=self.config.DEFAULT_WIDTH,
            height=self.config.DEFAULT_HEIGHT + (200 if show_volume else 0),
            showlegend=True
        )
        
        if show_volume:
            fig.update_yaxes(title_text=f'Price ({unit})' if unit else 'Price', row=1, col=1)
            fig.update_yaxes(title_text='Volume', row=2, col=1)
        
        # Save if path provided
        if save_path:
            fig.write_html(save_path)
            print(f"Chart saved to {save_path}")
        
        return fig
    
    def plot_currency_comparison(self,
                                currencies: List[str],
                                period: str = '3m',
                                normalize: bool = True,
                                save_path: Optional[str] = None) -> go.Figure:
        """
        Plot multiple currencies on the same chart for comparison.
        
        Args:
            currencies: List of currency codes (e.g., ['EUR', 'GBP', 'JPY'])
            period: Time period (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            normalize: Whether to normalize prices to start at 100 for comparison
            save_path: Optional path to save HTML file
            
        Returns:
            Plotly Figure object
        """
        start_date, end_date = self._parse_period(period)
        
        fig = go.Figure()
        
        for currency in currencies:
            currency = currency.upper()
            df = self.queries.get_exchange_rates(currency, start_date, end_date)
            
            if df.empty:
                print(f"Warning: No data found for {currency}, skipping...")
                continue
            
            color = self._get_color(currency)
            
            # Use close price if available, otherwise rate
            price_col = 'close' if 'close' in df.columns else 'rate'
            prices = df[price_col].copy()
            
            if normalize and len(prices) > 0:
                # Normalize to start at 100
                prices = (prices / prices.iloc[0]) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=prices,
                    mode='lines',
                    name=f'USD/{currency}',
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>%{{x}}</b><br>USD/{currency}: %{{y:.2f}}{" (normalized)" if normalize else ""}<extra></extra>'
                )
            )
        
        if len(fig.data) == 0:
            raise ValueError("No data found for any of the specified currencies")
        
        # Update layout
        fig.update_layout(
            template=self.config.TEMPLATE,
            title=f'Currency Comparison - {period}' + (' (Normalized to 100)' if normalize else ''),
            xaxis_title='Date',
            yaxis_title='Price (normalized)' if normalize else 'Rate',
            hovermode='x unified',
            width=self.config.DEFAULT_WIDTH,
            height=self.config.DEFAULT_HEIGHT,
            showlegend=True
        )
        
        # Save if path provided
        if save_path:
            fig.write_html(save_path)
            print(f"Chart saved to {save_path}")
        
        return fig
    
    def plot_performance_comparison(self,
                                   currencies: List[str],
                                   period: str = '3m',
                                   save_path: Optional[str] = None) -> go.Figure:
        """
        Plot performance comparison showing percentage change over period.
        
        Args:
            currencies: List of currency codes (e.g., ['EUR', 'GBP', 'JPY'])
            period: Time period (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            save_path: Optional path to save HTML file
            
        Returns:
            Plotly Figure object
        """
        start_date, end_date = self._parse_period(period)
        
        performance_data = []
        
        for currency in currencies:
            currency = currency.upper()
            df = self.queries.get_exchange_rates(currency, start_date, end_date)
            
            if df.empty or len(df) < 2:
                print(f"Warning: Insufficient data for {currency}, skipping...")
                continue
            
            price_col = 'close' if 'close' in df.columns else 'rate'
            start_price = df[price_col].iloc[0]
            end_price = df[price_col].iloc[-1]
            pct_change = ((end_price - start_price) / start_price) * 100
            
            performance_data.append({
                'currency': currency,
                'pct_change': pct_change,
                'start_price': start_price,
                'end_price': end_price
            })
        
        if not performance_data:
            raise ValueError("No performance data available for the specified currencies")
        
        # Create bar chart
        perf_df = pd.DataFrame(performance_data)
        colors = ['green' if x >= 0 else 'red' for x in perf_df['pct_change']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=perf_df['currency'],
                y=perf_df['pct_change'],
                marker_color=colors,
                text=perf_df['pct_change'].apply(lambda x: f'{x:+.2f}%'),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Change: %{y:.2f}%<br>Start: %{customdata[0]:.4f}<br>End: %{customdata[1]:.4f}<extra></extra>',
                customdata=perf_df[['start_price', 'end_price']]
            )
        ])
        
        # Update layout
        fig.update_layout(
            template=self.config.TEMPLATE,
            title=f'Currency Performance Comparison - {period}',
            xaxis_title='Currency',
            yaxis_title='Percentage Change (%)',
            hovermode='x unified',
            width=self.config.DEFAULT_WIDTH,
            height=self.config.DEFAULT_HEIGHT,
            showlegend=False
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        # Save if path provided
        if save_path:
            fig.write_html(save_path)
            print(f"Chart saved to {save_path}")
        
        return fig
    
    def plot_dollar_index(self,
                         period: str = '1y',
                         chart_type: str = 'line',
                         show_volume: bool = False,
                         save_path: Optional[str] = None) -> go.Figure:
        """
        Plot Dollar Index (DXY) history.
        
        Args:
            period: Time period (e.g., '1d', '1w', '1m', '3m', '6m', '1y', '5y')
            chart_type: Type of chart ('line' or 'candlestick')
            show_volume: Whether to show volume subplot
            save_path: Optional path to save HTML file
            
        Returns:
            Plotly Figure object
        """
        start_date, end_date = self._parse_period(period)
        df = self.queries.get_dollar_index(start_date, end_date)
        
        if df.empty:
            raise ValueError(f"No Dollar Index data found for period {period}")
        
        # Determine if OHLC data is available
        has_ohlc = all(col in df.columns for col in ['open', 'high', 'low', 'close'])
        has_ohlc = has_ohlc and df[['open', 'high', 'low', 'close']].notna().any().any()
        
        # Create subplots if volume is requested
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=('Dollar Index (DXY)', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # Add main price chart
        if chart_type == 'candlestick' and has_ohlc:
            if show_volume:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name='DXY',
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name='DXY',
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    )
                )
        else:
            # Use close price if available, otherwise value
            price_col = 'close' if 'close' in df.columns else 'value'
            if show_volume:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name='DXY',
                        line=dict(color='#636EFA', width=2),
                        hovertemplate='<b>%{x}</b><br>DXY: %{y:.2f}<extra></extra>'
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[price_col],
                        mode='lines',
                        name='DXY',
                        line=dict(color='#636EFA', width=2),
                        hovertemplate='<b>%{x}</b><br>DXY: %{y:.2f}<extra></extra>'
                    )
                )
        
        # Add volume if requested and available
        if show_volume and 'volume' in df.columns and df['volume'].notna().any():
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(128, 128, 128, 0.5)',
                    hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            template=self.config.TEMPLATE,
            title=f'Dollar Index (DXY) - {period}',
            xaxis_title='Date',
            yaxis_title='Index Value',
            hovermode='x unified',
            width=self.config.DEFAULT_WIDTH,
            height=self.config.DEFAULT_HEIGHT + (200 if show_volume else 0),
            showlegend=True
        )
        
        if show_volume:
            fig.update_yaxes(title_text='Index Value', row=1, col=1)
            fig.update_yaxes(title_text='Volume', row=2, col=1)
        
        # Save if path provided
        if save_path:
            fig.write_html(save_path)
            print(f"Chart saved to {save_path}")
        
        return fig


def get_visualizer(queries):
    """
    Factory function to get a visualizer instance.
    
    Args:
        queries: PriceQueries instance
        
    Returns:
        PriceVisualizer instance
    """
    return PriceVisualizer(queries)
