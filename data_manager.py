import json
import os
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any

class DataManager:
    def __init__(self, username=None):
        self.data_dir = "data"
        self.ensure_data_directory()
        self.username = username
        self.today_stocks_file = self._user_file("today_stocks.json")
        self.permanent_stocks_file = self._user_file("permanent_stocks.json")
        self.trading_plan_file = self._user_file("trading_plan.json")
        self.stock_trading_plans_file = self._user_file("stock_trading_plans.json")
        self.reflections_file = self._user_file("reflections.json")
        self.historical_stocks_file = self._user_file("historical_stocks.json")
    
    def _user_file(self, filename):
        if self.username:
            name, ext = os.path.splitext(filename)
            return os.path.join(self.data_dir, f"{self.username}_{name}{ext}")
        return os.path.join(self.data_dir, filename)
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_json_file(self, filename: str, default: Any = None) -> Any:
        """Load data from JSON file with error handling"""
        if default is None:
            default = {}
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return default
    
    def save_json_file(self, filename: str, data: Any):
        """Save data to JSON file with error handling"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    # Today's stocks management
    def add_today_stock(self, symbol: str, reason: str):
        """Add a stock to today's watchlist"""
        today_stocks = self.load_json_file(self.today_stocks_file, [])
        
        # Check if stock already exists
        for stock in today_stocks:
            if stock['symbol'] == symbol:
                stock['reason'] = reason  # Update reason if stock exists
                stock['date_added'] = datetime.now().strftime('%Y-%m-%d')
                self.save_json_file(self.today_stocks_file, today_stocks)
                return
        
        # Add new stock
        today_stocks.append({
            'symbol': symbol,
            'reason': reason,
            'date_added': datetime.now().strftime('%Y-%m-%d')
        })
        self.save_json_file(self.today_stocks_file, today_stocks)
        self._archive_today_stocks()
    
    def remove_today_stock(self, symbol: str):
        """Remove a stock from today's watchlist"""
        today_stocks = self.load_json_file(self.today_stocks_file, [])
        today_stocks = [stock for stock in today_stocks if stock['symbol'] != symbol]
        self.save_json_file(self.today_stocks_file, today_stocks)
    
    def get_today_stocks(self) -> List[Dict]:
        """Get today's watchlist"""
        return self.load_json_file(self.today_stocks_file, [])
    
    def _archive_today_stocks(self):
        """Archive today's stocks to historical data"""
        today_stocks = self.get_today_stocks()
        if not today_stocks:
            return
        
        historical_data = self.load_json_file(self.historical_stocks_file, {})
        today_date = datetime.now().strftime('%Y-%m-%d')
        historical_data[today_date] = today_stocks
        self.save_json_file(self.historical_stocks_file, historical_data)
    
    def get_last_week_stocks(self) -> List[Dict]:
        """Get stocks from the last week"""
        historical_data = self.load_json_file(self.historical_stocks_file, {})
        last_week_stocks = []
        
        # Get dates from last 7 days
        for i in range(1, 8):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in historical_data:
                for stock in historical_data[date]:
                    # Avoid duplicates
                    if not any(s['symbol'] == stock['symbol'] for s in last_week_stocks):
                        last_week_stocks.append(stock)
        
        return last_week_stocks
    
    # Permanent stocks management
    def add_permanent_stock(self, symbol: str, reason: str):
        """Add a stock to permanent watchlist"""
        permanent_stocks = self.load_json_file(self.permanent_stocks_file, [])
        
        # Check if stock already exists
        for stock in permanent_stocks:
            if stock['symbol'] == symbol:
                stock['reason'] = reason  # Update reason if stock exists
                self.save_json_file(self.permanent_stocks_file, permanent_stocks)
                return
        
        # Add new permanent stock
        permanent_stocks.append({
            'symbol': symbol,
            'reason': reason,
            'date_added': datetime.now().strftime('%Y-%m-%d')
        })
        self.save_json_file(self.permanent_stocks_file, permanent_stocks)
    
    def remove_permanent_stock(self, symbol: str):
        """Remove a stock from permanent watchlist"""
        permanent_stocks = self.load_json_file(self.permanent_stocks_file, [])
        permanent_stocks = [stock for stock in permanent_stocks if stock['symbol'] != symbol]
        self.save_json_file(self.permanent_stocks_file, permanent_stocks)
    
    def get_permanent_stocks(self) -> List[Dict]:
        """Get permanent watchlist"""
        return self.load_json_file(self.permanent_stocks_file, [])
    
    # Trading plan management
    def save_trading_plan(self, plan_data: Dict):
        """Save trading plan"""
        plan_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_json_file(self.trading_plan_file, plan_data)
    
    def get_trading_plan(self) -> Dict:
        """Get trading plan"""
        return self.load_json_file(self.trading_plan_file, {})
    
    # Stock-specific trading plans
    def save_stock_trading_plan(self, symbol: str, plan_data: Dict):
        """Save trading plan for a specific stock"""
        stock_plans = self.load_json_file(self.stock_trading_plans_file, {})
        stock_plans[symbol] = plan_data
        self.save_json_file(self.stock_trading_plans_file, stock_plans)
    
    def get_stock_trading_plans(self) -> Dict:
        """Get all stock-specific trading plans"""
        return self.load_json_file(self.stock_trading_plans_file, {})
    
    def get_stock_trading_plan(self, symbol: str) -> Dict:
        """Get trading plan for a specific stock"""
        stock_plans = self.get_stock_trading_plans()
        return stock_plans.get(symbol, {})
    
    # Daily reflection management
    def save_daily_reflection(self, reflection_data: Dict):
        """Save daily reflection"""
        reflections = self.load_json_file(self.reflections_file, [])
        
        # Remove existing reflection for today if it exists
        today = reflection_data['date']
        reflections = [r for r in reflections if r.get('date') != today]
        
        # Add new reflection
        reflections.append(reflection_data)
        self.save_json_file(self.reflections_file, reflections)
    
    def get_daily_reflections(self) -> List[Dict]:
        """Get all daily reflections"""
        return self.load_json_file(self.reflections_file, [])
    
    def get_most_common_mistake_last_week(self) -> Dict:
        """Get the most common mistake from the last week"""
        reflections = self.get_daily_reflections()
        last_week_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Filter reflections from last week
        last_week_reflections = [
            r for r in reflections 
            if r.get('date', '') >= last_week_date
        ]
        
        # Count mistakes
        all_mistakes = []
        for reflection in last_week_reflections:
            all_mistakes.extend(reflection.get('mistakes_made', []))
        
        if all_mistakes:
            mistake_counts = Counter(all_mistakes)
            most_common = mistake_counts.most_common(1)[0]
            return {'mistake': most_common[0], 'count': most_common[1]}
        
        return {}
    
    def get_weekly_scorecard_data(self) -> Dict:
        """Get data for weekly scorecard"""
        reflections = self.get_daily_reflections()
        last_week_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Filter reflections from last week
        weekly_reflections = [
            r for r in reflections 
            if r.get('date', '') >= last_week_date
        ]
        
        # Count mistakes
        all_mistakes = []
        for reflection in weekly_reflections:
            all_mistakes.extend(reflection.get('mistakes_made', []))
        mistake_counts = Counter(all_mistakes)
        
        # Count broken rules
        all_broken_rules = []
        for reflection in weekly_reflections:
            all_broken_rules.extend(reflection.get('broken_rules', []))
        broken_rules_counts = Counter(all_broken_rules)
        
        # Count good practices
        all_good_practices = []
        for reflection in weekly_reflections:
            all_good_practices.extend(reflection.get('good_practices', []))
        good_practices_counts = Counter(all_good_practices)
        
        # Calculate discipline metrics
        discipline_scores = [
            {'date': r.get('date'), 'score': r.get('discipline_score', 0)}
            for r in weekly_reflections
            if r.get('discipline_score') is not None
        ]
        
        # Calculate discipline streak (consecutive days with score > 8)
        discipline_streak = 0
        sorted_reflections = sorted(weekly_reflections, key=lambda x: x.get('date', ''), reverse=True)
        
        for reflection in sorted_reflections:
            if reflection.get('discipline_score', 0) > 8:
                discipline_streak += 1
            else:
                break
        
        # Calculate average discipline score
        scores = [r.get('discipline_score', 0) for r in weekly_reflections if r.get('discipline_score') is not None]
        avg_discipline = sum(scores) / len(scores) if scores else None
        
        return {
            'reflections': weekly_reflections,
            'mistake_counts': dict(mistake_counts),
            'broken_rules_counts': dict(broken_rules_counts),
            'good_practices_counts': dict(good_practices_counts),
            'discipline_scores': discipline_scores,
            'discipline_streak': discipline_streak,
            'avg_discipline': avg_discipline
        }
