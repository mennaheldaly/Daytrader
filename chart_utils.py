import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import numpy as np

def get_stock_chart(symbol: str, period: str = "1d", interval: str = "5m"):
    """
    Fetch stock data and create a chart image
    Returns: PIL Image object of the chart
    """
    try:
        # Fetch stock data
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            return None
        
        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        
        # Customize chart appearance
        fig.update_layout(
            title=f"{symbol} - {period.upper()} Chart",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            width=800,
            height=500,
            xaxis_rangeslider_visible=False,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Convert to image
        img_bytes = pio.to_image(fig, format="png", width=800, height=500)
        img = Image.open(io.BytesIO(img_bytes))
        
        return img
        
    except Exception as e:
        print(f"Error fetching chart for {symbol}: {e}")
        return None

def create_blank_chart_template(width=800, height=500):
    """
    Create a blank chart template when stock data is unavailable
    """
    # Create blank white image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([0, 0, width-1, height-1], outline='black', width=2)
    
    # Add grid lines
    for i in range(5):
        y = int(height * (i + 1) / 6)
        draw.line([50, y, width-50, y], fill='lightgray', width=1)
    
    for i in range(8):
        x = int(50 + (width - 100) * i / 7)
        draw.line([x, 50, x, height-50], fill='lightgray', width=1)
    
    # Add labels
    try:
        font = ImageFont.load_default()
        draw.text((width//2 - 50, 20), "Chart Template", fill='black', font=font)
        draw.text((20, height//2), "Price", fill='black', font=font)
        draw.text((width//2 - 20, height - 30), "Time", fill='black', font=font)
    except:
        pass
    
    return img

def convert_image_for_canvas(img):
    """
    Convert PIL Image to format compatible with streamlit-drawable-canvas
    """
    if img is None:
        return create_blank_chart_template()
    return img