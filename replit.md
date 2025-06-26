# DayTrading Helper Application

## Overview

This is a Streamlit-based day trading helper application designed to assist traders with their daily trading activities. The application provides a comprehensive workflow from morning setup to end-of-day reflection, helping traders maintain discipline and track their performance.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit (Python web framework)
- **UI Components**: Multi-tab interface with 5 main sections
- **Visualization**: Plotly for charts and graphs
- **Data Display**: Pandas DataFrames for tabular data

### Backend Architecture
- **Language**: Python 3.11
- **Data Storage**: JSON files for persistence
- **File Structure**: Modular design with separate components for data management and utilities

### Technology Stack
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **JSON**: Data persistence format

## Key Components

### Core Modules

1. **app.py** - Main application entry point
   - Sets up Streamlit configuration
   - Creates tab-based navigation
   - Manages overall application flow

2. **data_manager.py** - Data persistence layer
   - Handles JSON file operations
   - Manages different data types (stocks, plans, reflections)
   - Provides error handling for file operations

3. **utils.py** - Utility functions
   - Contains trading rules and common mistakes
   - Provides reference data for the application

### Application Tabs

1. **Morning Setup** - Pre-market preparation
2. **Longterm Playbook** - Strategic planning
3. **Trading Day** - Active trading interface
4. **End-of-day Reflection** - Post-market analysis
5. **Weekly Scorecard** - Performance tracking

## Data Flow

### Data Storage Strategy
- **Format**: JSON files for simplicity and portability
- **Location**: Local `data/` directory
- **Files**:
  - `today_stocks.json` - Daily watchlist
  - `permanent_stocks.json` - Long-term watchlist
  - `trading_plan.json` - Trading strategies and plans
  - `reflections.json` - Daily reflections and notes
  - `historical_stocks.json` - Historical stock data

### Data Management Approach
- **Caching**: Uses Streamlit's `@st.cache_resource` for data manager instance
- **Error Handling**: Graceful fallbacks for missing or corrupted files
- **Persistence**: Automatic saving of user inputs and modifications

## External Dependencies

### Python Packages
- **streamlit**: Web application framework (>=1.46.0)
- **pandas**: Data manipulation (>=2.3.0)
- **plotly**: Interactive visualizations (>=6.1.2)
- **Standard library**: json, os, datetime, collections

### System Dependencies
- **Python 3.11**: Runtime environment
- **Nix packages**: glibcLocales for proper locale support

## Deployment Strategy

### Platform Configuration
- **Target**: Replit with autoscale deployment
- **Runtime**: Python 3.11 with Nix stable-24_05 channel
- **Port**: 5000 (configured for Streamlit server)

### Execution Flow
- **Run Command**: `streamlit run app.py --server.port 5000`
- **Server Configuration**: Headless mode with external access
- **Workflows**: Parallel execution with port waiting

### Rationale for Choices

1. **Streamlit Selection**:
   - **Problem**: Need for rapid prototyping of data-driven web application
   - **Solution**: Streamlit for its simplicity and built-in components
   - **Pros**: Fast development, good for data apps, minimal frontend code
   - **Cons**: Limited customization compared to full web frameworks

2. **JSON Storage**:
   - **Problem**: Need for simple data persistence without database overhead
   - **Solution**: JSON files for structured data storage
   - **Pros**: Simple, portable, human-readable, no database setup required
   - **Cons**: Not suitable for high-volume concurrent access, limited querying

3. **Modular Design**:
   - **Problem**: Maintainability and code organization
   - **Solution**: Separate modules for data management and utilities
   - **Pros**: Clear separation of concerns, easier testing and maintenance
   - **Cons**: Slight complexity increase for small application

## Changelog

```
Changelog:
- June 26, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```