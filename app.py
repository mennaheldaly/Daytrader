import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_manager import DataManager
from utils import get_common_mistakes, get_trading_rules, get_good_practices
from chart_utils import get_stock_chart, create_blank_chart_template, convert_image_for_canvas
from streamlit_drawable_canvas import st_canvas
import numpy as np

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

def trading_day_tab(dm):
    st.header("Trading Day Dashboard")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🚨 Most Repeated Mistake (Last Week)")
        most_common_mistake = dm.get_most_common_mistake_last_week()
        if most_common_mistake:
            st.error(f"**{most_common_mistake['mistake']}** (occurred {most_common_mistake['count']} times)")
        else:
            st.info("No mistakes recorded in the last week")
    
    with col2:
        st.subheader("📋 Your Trading Plan")
        plan = dm.get_trading_plan()
        
        if plan.get('setup_criteria'):
            st.write("**Setup Criteria:**")
            st.write(plan['setup_criteria'])
        
        if plan.get('market_notes'):
            st.write("**Market Notes:**")
            st.write(plan['market_notes'])
        
        if plan.get('mental_reminders'):
            st.write("**Mental Reminders:**")
            st.write(plan['mental_reminders'])
        
        if plan.get('tactical_limits'):
            st.write("**Tactical Limits:**")
            st.write(plan['tactical_limits'])
        
        if plan.get('rules'):
            st.write("**Rules to Follow:**")
            for rule in plan['rules']:
                st.write(f"• {rule}")
    
    # Stocks in Play with Interactive Charts
    st.subheader("📊 Stocks in Play Today")
    today_stocks = dm.get_today_stocks()
    
    if not today_stocks:
        st.warning("No stocks selected for today. Go to Morning Setup to add stocks.")
        return
    
    # Create tabs for each stock
    stock_tabs = st.tabs([stock['symbol'] for stock in today_stocks])
    
    for i, stock in enumerate(today_stocks):
        with stock_tabs[i]:
            st.write(f"**Reason for watching:** {stock['reason']}")
            
            # Chart options
            col1, col2, col3 = st.columns(3)
            with col1:
                period = st.selectbox(f"Time Period for {stock['symbol']}", 
                                    ["1d", "5d", "1mo"], 
                                    key=f"period_{stock['symbol']}")
            with col2:
                interval = st.selectbox(f"Interval for {stock['symbol']}", 
                                      ["1m", "5m", "15m", "30m", "1h"] if period == "1d" else ["5m", "15m", "30m", "1h", "1d"],
                                      key=f"interval_{stock['symbol']}")
            with col3:
                if st.button(f"Refresh Chart", key=f"refresh_{stock['symbol']}"):
                    st.rerun()
            
            # Fetch and display chart
            with st.spinner(f"Loading chart for {stock['symbol']}..."):
                chart_img = get_stock_chart(stock['symbol'], period, interval)
                
                if chart_img is None:
                    st.error(f"Could not fetch chart data for {stock['symbol']}. Using template.")
                    chart_img = create_blank_chart_template()
            
            # Interactive drawing canvas
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Current Stock Chart:**")
                st.image(chart_img, caption=f"{stock['symbol']} Price Chart", use_container_width=True)
                
                # Alternative drawing approach using plotly
                st.write("**Interactive Chart with Drawing:**")
                try:
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",
                        stroke_width=2,
                        stroke_color="red",
                        background_image=None,  # Use None to avoid compatibility issues
                        update_streamlit=True,
                        width=800,
                        height=300,
                        drawing_mode="freedraw",
                        key=f"canvas_{stock['symbol']}",
                    )
                except Exception as e:
                    st.warning("Interactive drawing not available. Using text-based planning instead.")
                    canvas_result = None
                
                # Drawing instructions
                if canvas_result is not None:
                    st.write("**Drawing Instructions:**")
                    st.write("- Red lines: Entry points and stop losses")
                    st.write("- Green lines: Profit targets") 
                    st.write("- Blue lines: Scale-up levels")
                else:
                    st.write("**Use the form on the right to plan your trades for this stock.**")
            
            with col2:
                st.write("**Trading Plan for this Stock:**")
                
                # Initial Entry
                st.write("**a. Initial Entry:**")
                entry_plan = st.text_area(f"Entry strategy", 
                                        placeholder="Describe your entry plan...",
                                        key=f"entry_plan_{stock['symbol']}")
                
                # Scaling conditions
                st.write("**b. If it reaches mark X, do trade of size Y:**")
                scale_up_price = st.number_input(f"Scale up at price $", 
                                               min_value=0.01, 
                                               step=0.01,
                                               key=f"scale_price_{stock['symbol']}")
                scale_up_size = st.selectbox(f"Scale up size", 
                                           ["25%", "50%", "75%", "100%", "Double position"],
                                           key=f"scale_size_{stock['symbol']}")
                
                # Drop action
                st.write("**c. If it drops to certain mark:**")
                drop_price = st.number_input(f"Action at price $", 
                                           min_value=0.01, 
                                           step=0.01,
                                           key=f"drop_price_{stock['symbol']}")
                drop_action = st.selectbox(f"Action to take", 
                                         ["Size up", "Partial exit", "Full exit", "Hold"],
                                         key=f"drop_action_{stock['symbol']}")
                
                # Exit strategy
                st.write("**d. Exit Strategy:**")
                exit_plan = st.text_area(f"Exit conditions", 
                                       placeholder="When and how to exit...",
                                       key=f"exit_plan_{stock['symbol']}")
                
                # Wrong scenario
                st.write("**e. If completely wrong:**")
                wrong_plan = st.text_area(f"Emergency exit plan", 
                                        placeholder="What if everything goes wrong...",
                                        key=f"wrong_plan_{stock['symbol']}")
                
                # Save trading plan for this stock
                if st.button(f"Save Plan for {stock['symbol']}", key=f"save_plan_{stock['symbol']}", type="primary"):
                    trading_plan = {
                        'symbol': stock['symbol'],
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'entry_plan': entry_plan,
                        'scale_up_price': scale_up_price,
                        'scale_up_size': scale_up_size,
                        'drop_price': drop_price,
                        'drop_action': drop_action,
                        'exit_plan': exit_plan,
                        'wrong_plan': wrong_plan,
                        'canvas_data': canvas_result.json_data if canvas_result and hasattr(canvas_result, 'json_data') else None
                    }
                    dm.save_stock_trading_plan(trading_plan)
                    st.success(f"Trading plan saved for {stock['symbol']}!")
            
            st.divider()

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
            mistakes_data = list(weekly_data['mistake_counts'].items())
            mistakes_df = pd.DataFrame(mistakes_data)
            mistakes_df.columns = ['Mistake', 'Frequency']
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
