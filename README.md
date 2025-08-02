# Hedging Strategy Trading Bot

## Overview

This is a grid-based hedging strategy for cryptocurrency futures trading on Binance. The strategy implements an automated trading system that can profit from price reversals by creating hedged positions.

## ⚠️ Important Disclaimer

**This software is for educational and testing purposes only.**
- Use only with Binance Testnet, NOT live trading
- Cryptocurrency trading involves substantial risk
- Past performance does not guarantee future results
- Always test thoroughly before any live implementation
- Consider consulting with financial advisors

## How the Strategy Works

### Core Concept
The strategy operates on a **grid-based hedging principle**:

1. **Initial Position**: Opens either a LONG or SHORT position
2. **Hedging Trigger**: When price moves 0.4% against the current position, opens an opposite position
3. **Position Management**: Maintains both LONG and SHORT positions simultaneously
4. **Profit Taking**: Closes all positions when price reaches take-profit levels (0.8%)
5. **Cycle Restart**: Begins a new cycle after position closure

### Strategy Flow

```
Start → Open Initial Position (LONG/SHORT)
  ↓
Price moves 0.4% against position
  ↓
Open opposite position (creates hedge)
  ↓
Price continues moving
  ↓
Take profit at 0.8% → Close all positions
  ↓
Restart cycle
```

### Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Entry Distance | 0.4% | Distance for triggering opposite position |
| Take Profit | 0.8% | Profit target for closing all positions |
| Stop Loss | 1.2% | Emergency stop loss (currently unused) |
| Leverage | 50x | Position leverage multiplier |

## Risk Management Guidelines

### 1. Capital Allocation
- **Never risk more than 1-2% of total capital per trade**
- **Recommended maximum: 5% of capital in active positions**
- **Keep 80-90% of capital in reserve for emergencies**

### 2. Position Sizing Formula
```
Position Size = (Account Balance × Risk Per Trade) ÷ (Leverage × Stop Loss Distance)
```

**Example:**
- Account Balance: $10,000
- Risk Per Trade: 1% ($100)
- Leverage: 50x
- Stop Loss: 1.2%

```
Position Size = $100 ÷ (50 × 0.012) = $100 ÷ 0.6 = $166.67
```

### 3. Risk Management Rules

#### Before Trading:
- ✅ Test on Binance Testnet first
- ✅ Start with small position sizes
- ✅ Set maximum daily loss limits
- ✅ Have emergency stop procedures

#### During Trading:
- ✅ Monitor position exposure continuously
- ✅ Don't increase position sizes during losses
- ✅ Have a maximum drawdown limit (e.g., 10%)
- ✅ Keep detailed trading logs

#### Emergency Procedures:
- ❌ Never panic sell
- ❌ Don't override automated systems manually
- ❌ Don't increase leverage to recover losses

### 4. Market Conditions to Avoid

**High Volatility Periods:**
- Major news events
- Market crashes
- High-impact economic releases

**Low Liquidity:**
- Low volume periods
- Thin order books
- Weekend trading (for some pairs)

## Position Sizing Recommendations

### Conservative Approach (Recommended for Beginners)
```
Initial Position Size = 0.1 BTC (or smaller)
Account Size: $5,000+
Risk Per Trade: 0.5%
Maximum Daily Loss: 2%
```

### Moderate Approach (Experienced Traders)
```
Initial Position Size = 0.3 BTC
Account Size: $10,000+
Risk Per Trade: 1%
Maximum Daily Loss: 3%
```

### Aggressive Approach (Advanced Traders Only)
```
Initial Position Size = 0.5 BTC+
Account Size: $20,000+
Risk Per Trade: 1.5%
Maximum Daily Loss: 5%
```

## Setup Instructions

### 1. Prerequisites
```bash
pip install python-binance pandas
```

### 2. Binance Testnet Setup
1. Create account at [Binance Testnet](https://testnet.binance.vision/)
2. Generate API keys
3. Fund testnet account with test BTC

### 3. Configuration
```python
# Trading parameters (modify these)
symbol = "BTCUSDT"                    # Trading pair
initial_units = 0.1                   # Start small!
leverage = 50                         # Leverage multiplier
side = "LONG"                         # Initial direction

# Strategy parameters
long_entry_add = 0.4/100             # 0.4% entry distance
short_entry_deduct = 0.4/100         # 0.4% entry distance
long_tp_add = 0.8/100                # 0.8% take profit
short_tp_deduct = 0.8/100            # 0.8% take profit
```

### 4. Running the Bot
```bash
python main.py
```

## Strategy Advantages

### ✅ Pros
- **Automated**: No emotional trading decisions
- **Hedged**: Reduces directional risk
- **Scalable**: Can handle multiple positions
- **Backtested**: Can be tested on historical data
- **Real-time**: Responds to market changes instantly

### ⚠️ Cons
- **Complex**: Requires understanding of futures trading
- **Risky**: High leverage can amplify losses
- **Market Dependent**: Performance varies with market conditions
- **Technical**: Requires reliable internet and system uptime

## Performance Monitoring

### Key Metrics to Track
1. **Win Rate**: Percentage of profitable cycles
2. **Average Profit**: Average profit per completed cycle
3. **Maximum Drawdown**: Largest peak-to-trough decline
4. **Sharpe Ratio**: Risk-adjusted returns
5. **Position Exposure**: Total open position value

### Recommended Monitoring Tools
- Trading journal (Excel/Google Sheets)
- Performance dashboard
- Risk metrics calculator
- Real-time position monitor

## Advanced Configuration

### Customizing Strategy Parameters

```python
# More conservative settings
long_entry_add = 0.3/100             # 0.3% entry distance
long_tp_add = 0.6/100                # 0.6% take profit

# More aggressive settings
long_entry_add = 0.5/100             # 0.5% entry distance
long_tp_add = 1.0/100                # 1.0% take profit
```

### Multiple Timeframes
```python
bar_length = "1m"                     # 1-minute candles
# Alternative: "5m", "15m", "1h"
```

### Different Trading Pairs
```python
symbol = "ETHUSDT"                    # Ethereum
symbol = "ADAUSDT"                    # Cardano
symbol = "DOTUSDT"                    # Polkadot
```

## Troubleshooting

### Common Issues

**1. API Connection Errors**
- Check internet connection
- Verify API keys are correct
- Ensure testnet URL is used

**2. Position Not Opening**
- Check account balance
- Verify leverage settings
- Ensure dual-side position mode is enabled

**3. Unexpected Behavior**
- Review strategy parameters
- Check market conditions
- Monitor position tracking variables

### Debug Mode
Uncomment debug prints in the code:
```python
#print('Hedging loop started')
#print('Last direction is Long')
```

## Legal and Compliance

### Important Notes
- This is educational software only
- Not financial advice
- Test thoroughly before any live use
- Comply with local trading regulations
- Consider tax implications

### Risk Warnings
- Cryptocurrency markets are highly volatile
- Leverage trading can result in significant losses
- Past performance doesn't guarantee future results
- Only trade with capital you can afford to lose

## Support and Resources

### Learning Resources
- [Binance Futures Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [Python-Binance Library](https://python-binance.readthedocs.io/)
- [Technical Analysis Resources](https://www.investopedia.com/technical-analysis-4689657)

### Community
- Binance Community Forum
- Trading Discord servers
- Reddit trading communities

---

**Remember: The best strategy is the one you understand and can stick to consistently. Always prioritize risk management over potential profits.**
