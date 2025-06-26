import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from streamlit_drawable_canvas import st_canvas
from data_manager import DataManager
from utils import get_common_mistakes, get_trading_rules, get_good_practices

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

def main():
    st.set_page_config(
        page_title="DayTrading Helper",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 DayTrading Helper")
    
    # Initialize data manager
    dm = get_data_manager()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌅 Morning Setup", 
        "📋 Longterm Playbook", 
        "📊 Trading Day", 
        "🌙 End-of-day Reflection", 
        "📑 Weekly Scorecard"
    ])
    
    with tab1:
        morning_setup_tab(dm)
    
    with tab2:
        longterm_playbook_tab(dm)
    
    with tab3:
        trading_day_tab(dm)
    
    with tab4:
        end_of_day_reflection_tab(dm)
    
    with tab5:
        weekly_scorecard_tab(dm)

def morning_setup_tab(dm):
    st.header("Morning Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Add Today's Stocks")
        
        # Add new stock for today
        with st.form("add_today_stock"):
            new_stock = st.text_input("Stock Symbol", placeholder="e.g., AAPL").upper()
            reason = st.text_area("Reason for watching", placeholder="Enter why you're watching this stock")
            submitted = st.form_submit_button("Add Stock")
            
            if submitted and new_stock:
                dm.add_today_stock(new_stock, reason)
                st.success(f"Added {new_stock} to today's watchlist!")
                st.rerun()
    
    with col2:
        st.subheader("🗑️ Remove Today's Stocks")
        today_stocks = dm.get_today_stocks()
        if today_stocks:
            stock_to_remove = st.selectbox("Select stock to remove", 
                                         options=[f"{stock['symbol']} - {stock['reason']}" for stock in today_stocks])
            if st.button("Remove Selected Stock"):
                symbol = stock_to_remove.split(" - ")[0]
                dm.remove_today_stock(symbol)
                st.success(f"Removed {symbol} from today's watchlist!")
                st.rerun()
    
    # Display current watchlists
    st.subheader("📊 Current Watchlists")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Today's Stocks**")
        today_stocks = dm.get_today_stocks()
        if today_stocks:
            for stock in today_stocks:
                st.write(f"• {stock['symbol']}: {stock['reason']}")
        else:
            st.write("No stocks added for today")
    
    with col2:
        st.write("**Last Week's Stocks**")
        last_week_stocks = dm.get_last_week_stocks()
        if last_week_stocks:
            for stock in last_week_stocks:
                st.write(f"• {stock['symbol']}: {stock['reason']}")
                if st.button(f"Add {stock['symbol']} to today", key=f"add_{stock['symbol']}"):
                    dm.add_today_stock(stock['symbol'], stock['reason'])
                    st.success(f"Added {stock['symbol']} to today's watchlist!")
                    st.rerun()
        else:
            st.write("No stocks from last week")
    
    with col3:
        st.write("**Permanent Watchlist**")
        permanent_stocks = dm.get_permanent_stocks()
        if permanent_stocks:
            for stock in permanent_stocks:
                st.write(f"• {stock['symbol']}: {stock['reason']}")
                if st.button(f"Add {stock['symbol']} to today", key=f"add_perm_{stock['symbol']}"):
                    dm.add_today_stock(stock['symbol'], stock['reason'])
                    st.success(f"Added {stock['symbol']} to today's watchlist!")
                    st.rerun()
        else:
            st.write("No permanent stocks")

def longterm_playbook_tab(dm):
    st.header("Longterm Playbook")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Trading Plan")
        
        plan = dm.get_trading_plan()
        
        with st.form("trading_plan"):
            setup_criteria = st.text_area("Setup Criteria", 
                                        value=plan.get('setup_criteria', ''),
                                        placeholder="Enter your setup criteria...")
            market_notes = st.text_area("Market Notes", 
                                      value=plan.get('market_notes', ''),
                                      placeholder="Enter market observations...")
            mental_reminders = st.text_area("Mental Reminders", 
                                           value=plan.get('mental_reminders', ''),
                                           placeholder="Enter mental reminders...")
            tactical_limits = st.text_area("Tactical Limits", 
                                         value=plan.get('tactical_limits', ''),
                                         placeholder="Enter your limits...")
            
            st.write("**Select Trading Rules:**")
            available_rules = get_trading_rules()
            current_rules = plan.get('rules', [])
            selected_rules = st.multiselect("Rules to follow", 
                                          options=available_rules,
                                          default=current_rules)
            
            if st.form_submit_button("Save Trading Plan"):
                plan_data = {
                    'setup_criteria': setup_criteria,
                    'market_notes': market_notes,
                    'mental_reminders': mental_reminders,
                    'tactical_limits': tactical_limits,
                    'rules': selected_rules
                }
                dm.save_trading_plan(plan_data)
                st.success("Trading plan saved!")
                st.rerun()
    
    with col2:
        st.subheader("🎯 Permanent Watchlist")
        
        # Add permanent stock
        with st.form("add_permanent_stock"):
            new_perm_stock = st.text_input("Stock Symbol", placeholder="e.g., TSLA").upper()
            perm_reason = st.text_area("Reason for permanent watch", 
                                     placeholder="Why is this in your long-term playbook?")
            if st.form_submit_button("Add to Permanent List"):
                if new_perm_stock:
                    dm.add_permanent_stock(new_perm_stock, perm_reason)
                    st.success(f"Added {new_perm_stock} to permanent watchlist!")
                    st.rerun()
        
        # Display and manage permanent stocks
        permanent_stocks = dm.get_permanent_stocks()
        if permanent_stocks:
            st.write("**Current Permanent Stocks:**")
            for stock in permanent_stocks:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• **{stock['symbol']}**: {stock['reason']}")
                with col_b:
                    if st.button("Remove", key=f"remove_perm_{stock['symbol']}"):
                        dm.remove_permanent_stock(stock['symbol'])
                        st.success(f"Removed {stock['symbol']} from permanent watchlist!")
                        st.rerun()

def get_stock_chart_image(symbol, period="1d", interval="5m"):
    """Fetch stock data and create a matplotlib chart as image for drawing"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            return None, None
            
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot candlestick-style chart
        for i in range(len(data)):
            open_price = data['Open'].iloc[i]
            close_price = data['Close'].iloc[i]
            high_price = data['High'].iloc[i]
            low_price = data['Low'].iloc[i]
            
            # Color based on up/down
            color = 'green' if close_price >= open_price else 'red'
            
            # Draw high-low line
            ax.plot([i, i], [low_price, high_price], color='black', linewidth=1)
            
            # Draw open-close rectangle
            rect_height = abs(close_price - open_price)
            rect_bottom = min(open_price, close_price)
            rect = patches.Rectangle((i-0.3, rect_bottom), 0.6, rect_height, 
                               facecolor=color, alpha=0.7, edgecolor='black')
            ax.add_patch(rect)
        
        ax.set_title(f"{symbol} - {period.upper()} Chart")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price ($)")
        ax.grid(True, alpha=0.3)
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_data = buf.getvalue()
        buf.close()
        plt.close(fig)
        
        return img_data, data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

def get_stock_chart(symbol, period="1d", interval="5m"):
    """Fetch stock data and create a plotly chart"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            return None, None
            
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        
        fig.update_layout(
            title=f"{symbol} - {period.upper()} Chart",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            height=400,
            showlegend=False
        )
        
        return fig, data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

def trading_day_tab(dm):
    st.header("Trading Day Dashboard")
    
    today_stocks = dm.get_today_stocks()
    
    if not today_stocks:
        st.warning("No stocks selected for today. Go to Morning Setup to add stocks.")
        return
    
    # Stock selection for detailed analysis
    st.subheader("📊 Select Stock for Analysis")
    selected_stock = st.selectbox(
        "Choose a stock to analyze:",
        options=[f"{stock['symbol']} - {stock['reason']}" for stock in today_stocks],
        key="stock_selector"
    )
    
    if selected_stock:
        symbol = selected_stock.split(" - ")[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📈 {symbol} Chart & Trading Plan")
            
            # Chart time frame selection
            time_frame = st.selectbox("Time Frame:", ["1d", "5d", "1mo"], key=f"timeframe_{symbol}")
            interval_map = {"1d": "5m", "5d": "15m", "1mo": "1h"}
            interval = interval_map[time_frame]
            
            # Get and display chart with drawing capability
            chart_img, data = get_stock_chart_image(symbol, time_frame, interval)
            
            if chart_img is not None:
                # Current price info
                if data is not None and len(data) > 0:
                    current_price = data['Close'].iloc[-1]
                    price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
                    price_change_pct = (price_change / data['Close'].iloc[0]) * 100
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Current Price", f"${current_price:.2f}")
                    with col_b:
                        st.metric("Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
                    with col_c:
                        st.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}")
                
                # Drawing mode selection
                st.write("**Drawing Mode:**")
                drawing_modes = {
                    "Entry Points": {"color": "#00ff00", "stroke_width": 3},
                    "Scale Up Levels": {"color": "#0000ff", "stroke_width": 3}, 
                    "Stop Loss": {"color": "#ff0000", "stroke_width": 3},
                    "Exit Targets": {"color": "#ff8c00", "stroke_width": 3},
                    "Notes": {"color": "#800080", "stroke_width": 2}
                }
                
                selected_mode = st.selectbox(
                    "Select drawing mode:",
                    options=list(drawing_modes.keys()),
                    key=f"drawing_mode_{symbol}"
                )
                
                mode_config = drawing_modes[selected_mode]
                
                # Convert image to base64 for canvas background
                import base64
                img_base64 = base64.b64encode(chart_img).decode()
                
                # Load existing drawings
                saved_drawings = dm.get_stock_chart_drawings(symbol)
                
                # Convert chart to PIL Image for canvas background
                from PIL import Image
                chart_image = Image.open(io.BytesIO(chart_img))
                
                # Resize chart image to fit canvas dimensions
                canvas_width = 900
                canvas_height = 450
                chart_image = chart_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                # Drawing canvas with chart as background
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.1)",
                    stroke_width=mode_config["stroke_width"],
                    stroke_color=mode_config["color"],
                    background_image=chart_image,
                    update_streamlit=True,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode="freedraw",
                    point_display_radius=3,
                    display_toolbar=True,
                    key=f"canvas_{symbol}_{time_frame}_{selected_mode}",
                )
                
                # Save drawings button
                col_save, col_clear = st.columns(2)
                with col_save:
                    if st.button(f"Save {selected_mode} Drawing", key=f"save_drawing_{symbol}"):
                        if canvas_result.json_data is not None:
                            drawing_data = {
                                "mode": selected_mode,
                                "data": canvas_result.json_data,
                                "color": mode_config["color"],
                                "timestamp": datetime.now().isoformat()
                            }
                            dm.save_stock_chart_drawing(symbol, selected_mode, drawing_data)
                            st.success(f"Saved {selected_mode} drawing!")
                
                with col_clear:
                    if st.button(f"Clear {selected_mode} Drawings", key=f"clear_drawing_{symbol}"):
                        dm.clear_stock_chart_drawings(symbol, selected_mode)
                        st.success(f"Cleared {selected_mode} drawings!")
                        st.rerun()
                
                # Display legend
                st.write("**Drawing Legend:**")
                legend_cols = st.columns(len(drawing_modes))
                for i, (mode, config) in enumerate(drawing_modes.items()):
                    with legend_cols[i]:
                        st.markdown(f"<span style='color: {config['color']}'>●</span> {mode}", unsafe_allow_html=True)
                        
            else:
                st.error(f"Unable to fetch chart data for {symbol}")
        
        with col2:
            st.subheader("📋 Trading Strategy")
            
            # Trading plan for this specific stock
            stock_plans = dm.get_stock_trading_plans()
            current_plan = stock_plans.get(symbol, {})
            
            with st.form(f"trading_plan_{symbol}"):
                st.write("**Entry Strategy:**")
                initial_entry = st.text_input(
                    "Initial Entry Price/Condition:",
                    value=current_plan.get('initial_entry', ''),
                    placeholder="e.g., $150.50 on breakout"
                )
                
                entry_size = st.text_input(
                    "Position Size:",
                    value=current_plan.get('entry_size', ''),
                    placeholder="e.g., 100 shares, 1% of portfolio"
                )
                
                st.write("**Scaling Strategy:**")
                scale_up_condition = st.text_input(
                    "Scale Up If Reaches:",
                    value=current_plan.get('scale_up_condition', ''),
                    placeholder="e.g., $155 - add 50 shares"
                )
                
                scale_down_condition = st.text_input(
                    "Scale Down/Stop If Drops To:",
                    value=current_plan.get('scale_down_condition', ''),
                    placeholder="e.g., $145 - cut 50%, $140 - full stop"
                )
                
                st.write("**Exit Strategy:**")
                exit_strategy = st.text_area(
                    "Exit Conditions:",
                    value=current_plan.get('exit_strategy', ''),
                    placeholder="e.g., Take 50% at $160, full exit at $165 or stop at $145",
                    height=80
                )
                
                st.write("**Risk Management:**")
                wrong_scenario = st.text_area(
                    "If Completely Wrong:",
                    value=current_plan.get('wrong_scenario', ''),
                    placeholder="e.g., Hard stop at $140, reassess strategy, max loss 2%",
                    height=80
                )
                
                if st.form_submit_button("Save Trading Plan", type="primary"):
                    plan_data = {
                        'initial_entry': initial_entry,
                        'entry_size': entry_size,
                        'scale_up_condition': scale_up_condition,
                        'scale_down_condition': scale_down_condition,
                        'exit_strategy': exit_strategy,
                        'wrong_scenario': wrong_scenario,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    dm.save_stock_trading_plan(symbol, plan_data)
                    st.success(f"Trading plan saved for {symbol}!")
                    st.rerun()
    
    # Display all stocks summary
    st.subheader("📊 All Stocks Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Today's Watchlist:**")
        for stock in today_stocks:
            st.write(f"• **{stock['symbol']}**: {stock['reason']}")
    
    with col2:
        st.subheader("🚨 Most Repeated Mistake (Last Week)")
        most_common_mistake = dm.get_most_common_mistake_last_week()
        if most_common_mistake:
            st.error(f"**{most_common_mistake['mistake']}** (occurred {most_common_mistake['count']} times)")
        else:
            st.info("No mistakes recorded in the last week")
        
        # Display general trading plan
        st.subheader("📋 General Trading Rules")
        plan = dm.get_trading_plan()
        
        if plan.get('rules'):
            st.write("**Rules to Follow Today:**")
            for rule in plan['rules'][:5]:  # Show first 5 rules
                st.write(f"• {rule}")
            if len(plan['rules']) > 5:
                st.write(f"... and {len(plan['rules']) - 5} more")

def end_of_day_reflection_tab(dm):
    st.header("End-of-day Reflection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Plan Adherence")
        plan = dm.get_trading_plan()
        
        if plan.get('rules'):
            st.write("**Which rules did you NOT follow today?**")
            broken_rules = st.multiselect("Select rules you broke",
                                        options=plan['rules'],
                                        key="broken_rules")
        else:
            broken_rules = []
            st.info("No rules set in your trading plan")
        
        st.subheader("❌ Mistakes Made")
        available_mistakes = get_common_mistakes()
        mistakes_made = st.multiselect("Select mistakes you made today",
                                     options=available_mistakes,
                                     key="mistakes_made")
        
        st.subheader("✅ Good Practices")
        available_practices = get_good_practices()
        good_practices = st.multiselect("Select good practices you followed",
                                      options=available_practices,
                                      key="good_practices")
    
    with col2:
        st.subheader("📊 Discipline Rating")
        discipline_score = st.slider("Rate your discipline today (1-10)", 
                                   min_value=1, max_value=10, value=5)
        
        st.subheader("📝 Reflection Notes")
        reflection_notes = st.text_area("Why did you rate yourself this way?",
                                      placeholder="Explain your discipline rating...",
                                      height=150)
        
        if st.button("Save Today's Reflection", type="primary"):
            reflection_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'broken_rules': broken_rules,
                'mistakes_made': mistakes_made,
                'good_practices': good_practices,
                'discipline_score': discipline_score,
                'reflection_notes': reflection_notes
            }
            dm.save_daily_reflection(reflection_data)
            st.success("Daily reflection saved!")

def weekly_scorecard_tab(dm):
    st.header("Weekly Scorecard Summary")
    
    # Get weekly data
    weekly_data = dm.get_weekly_scorecard_data()
    
    if not weekly_data['reflections']:
        st.warning("No reflection data available. Complete some daily reflections to see your weekly scorecard.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Mistake Frequency")
        if weekly_data['mistake_counts']:
            # Create bar chart for mistakes
            mistakes_data = {'Mistake': [], 'Frequency': []}
            for mistake, freq in weekly_data['mistake_counts'].items():
                mistakes_data['Mistake'].append(mistake)
                mistakes_data['Frequency'].append(freq)
            mistakes_df = pd.DataFrame(mistakes_data)
            fig = px.bar(mistakes_df, x='Mistake', y='Frequency', 
                        title="Mistakes This Week")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Most common mistake
            most_common = max(weekly_data['mistake_counts'].items(), key=lambda x: x[1])
            st.error(f"**Most Common Mistake:** {most_common[0]} ({most_common[1]} times)")
        else:
            st.info("No mistakes recorded this week!")
        
        st.subheader("📈 Discipline Trend")
        if weekly_data['discipline_scores']:
            discipline_df = pd.DataFrame(weekly_data['discipline_scores'])
            fig = px.line(discipline_df, x='date', y='score', 
                         title="Daily Discipline Scores",
                         markers=True)
            fig.add_hline(y=8, line_dash="dash", line_color="green", 
                         annotation_text="Good Discipline Threshold (8+)")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Key Metrics")
        
        # Discipline streak
        discipline_streak = weekly_data['discipline_streak']
        if discipline_streak > 0:
            st.success(f"**Discipline Streak:** {discipline_streak} days with score > 8")
        else:
            st.warning("**Discipline Streak:** 0 days with score > 8")
        
        # Average discipline score
        avg_discipline = weekly_data['avg_discipline']
        if avg_discipline:
            st.metric("Average Discipline Score", f"{avg_discipline:.1f}")
        
        # Rules broken
        st.subheader("⚠️ Rules Broken This Week")
        if weekly_data['broken_rules_counts']:
            for rule, count in weekly_data['broken_rules_counts'].items():
                st.write(f"• {rule}: {count} times")
        else:
            st.success("No rules broken this week!")
        
        # Good practices
        st.subheader("✅ Good Practices This Week")
        if weekly_data['good_practices_counts']:
            for practice, count in weekly_data['good_practices_counts'].items():
                st.write(f"• {practice}: {count} times")
        else:
            st.info("No good practices recorded this week")

if __name__ == "__main__":
    main()
