import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import numpy as np

def get_stock_chart(symbol: str, period: str = "1d", interval: str = "5m"):
    """
    Fetch stock data and create a simple line chart using matplotlib
    Returns: PIL Image object of the chart
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        # Fetch stock data
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            return None
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('white')
        
        # Simple line chart of closing prices
        ax.plot(range(len(data)), data['Close'], linewidth=2, color='blue', label='Close Price')
        ax.fill_between(range(len(data)), data['Close'], alpha=0.3, color='lightblue')
        
        # Add high and low lines
        ax.plot(range(len(data)), data['High'], linewidth=1, color='green', alpha=0.7, label='High')
        ax.plot(range(len(data)), data['Low'], linewidth=1, color='red', alpha=0.7, label='Low')
        
        # Customize the chart
        ax.set_title(f"{symbol} - {period.upper()} Chart", fontsize=16, fontweight='bold')
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Price ($)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set x-axis labels with simpler approach
        num_ticks = min(8, len(data))
        if num_ticks > 1:
            tick_positions = np.linspace(0, len(data)-1, num_ticks, dtype=int)
            ax.set_xticks(tick_positions)
            
            # Simple time labels
            labels = []
            for pos in tick_positions:
                try:
                    timestamp = data.index[pos]
                    if hasattr(timestamp, 'strftime'):
                        if period == '1d':
                            labels.append(timestamp.strftime('%H:%M'))
                        else:
                            labels.append(timestamp.strftime('%m/%d'))
                    else:
                        labels.append(f"T{pos}")
                except:
                    labels.append(f"T{pos}")
            
            ax.set_xticklabels(labels, rotation=45)
        
        plt.tight_layout()
        
        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
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