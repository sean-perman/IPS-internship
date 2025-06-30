import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import datetime

# --- Settings ---
ticker = "AAPL"
#ticker = "NVDA"
stock = yf.Ticker(ticker)
expirations = stock.options[:5]  # Pull first 5 expirations to keep things fast

# --- Collect Options Data (Calls Only) ---
option_data = []

for expiry in expirations:
    chain = stock.option_chain(expiry)
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    ttm = (expiry_date - datetime.today()).days / 365  # Time to maturity (in years)

    for call in chain.calls.itertuples():
        # Only include options with a valid, positive implied volatility
        if call.impliedVolatility and call.impliedVolatility > 0:
            option_data.append({
                "contract": call.contractSymbol,        # The full option contract name (e.g., AAPL240719C00175000)
                "strike": call.strike,                  # The option's strike price
                "expiration": expiry,                   # The expiration date (YYYY-MM-DD)
                "ttm": ttm,                             # Time to maturity: days until expiry divided by 365
                "IV": call.impliedVolatility,           # Implied volatility (market's expectation of future volatility)
                "bid": call.bid,                        # Bid price for the option (what someone is willing to pay)
                "ask": call.ask,                        # Ask price (what someone is willing to sell it for)
                "lastPrice": call.lastPrice             # Last traded price of the option
            })

# --- Convert to DataFrame ---
df = pd.DataFrame(option_data)

# --- Pretty Print Sample ---
print("\n📊 Sample Option Chain Data (Calls Only):\n")
print(df[["contract", "strike", "expiration", "ttm", "IV", "bid", "ask", "lastPrice"]].head().to_string(index=False))

# --- Plot Volatility Surface ---
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

strikes = df["strike"].values
ttms = df["ttm"].values
ivs = df["IV"].values

surf = ax.plot_trisurf(strikes, ttms, ivs, cmap=cm.viridis, linewidth=0.2, antialiased=True)

ax.set_title(f"{ticker} Implied Volatility Surface (Calls Only)")
ax.set_xlabel("Strike Price")
ax.set_ylabel("Time to Maturity (Years)")
ax.set_zlabel("Implied Volatility")
fig.colorbar(surf, shrink=0.5, aspect=10)

plt.tight_layout()
plt.show()