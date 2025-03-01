import sys
import os
import yfinance as yf
import matplotlib.pyplot as plt

# AutoGen imports
from autogen import AssistantAgent, UserProxyAgent

# 1) Simple inline "tool" functions:
def fetch_stock_data(ticker: str, period: str = "1mo"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def plot_stock_data(ticker: str, period: str = "1mo"):
    hist = fetch_stock_data(ticker, period)
    if hist.empty:
        print(f"No data found for {ticker}")
        return
    plt.figure(figsize=(8, 4))
    plt.plot(hist.index, hist['Close'], label=f'{ticker} Closing Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.title(f'{ticker} Stock Price ({period})')
    plt.legend()
    plt.grid()
    plt.show()

# 2) Custom assistant that checks user messages
class MyStockAgent(AssistantAgent):
    def generate_reply(self, messages, **kwargs):
        """
        messages: list of dicts with keys "role" and "content".
        We'll parse the user's latest message for 'fetch' or 'plot'.
        """
        user_message = messages[-1]["content"].lower()

        if "fetch" in user_message and "stock" in user_message:
            parts = user_message.split()
            ticker = parts[-1].upper()
            data = fetch_stock_data(ticker)
            if not data.empty:
                latest_price = data['Close'][-1]
                return f"The latest closing price for {ticker} is {latest_price:.2f}."
            else:
                return f"No data found for {ticker}."

        elif "plot" in user_message and "stock" in user_message:
            parts = user_message.split()
            ticker = parts[-1].upper()
            plot_stock_data(ticker)
            return f"Plotted stock data for {ticker}."

        # Fallback
        return (
            "Sorry, I didn't understand your request. "
            "Try 'Fetch stock data for AAPL' or 'Plot stock data for TSLA'."
        )

def main():
    # 3) Create the assistant & user agents
    assistant = MyStockAgent(
        name="StockAgent",
        code_execution_config={"use_docker": False}
    )
    user = UserProxyAgent(name="User")

    # 4) Initiate the chat (with the user, NOT the assistant)
    assistant.initiate_chat(user)

    # 5) Simulate user messages
    print("\nUser: fetch stock data for AAPL")
    user.send(assistant, "fetch stock data for AAPL")

    print("\nUser: plot stock data for TSLA")
    user.send(assistant, "plot stock data for TSLA")

    # No call to exit_chat needed.
    print("\nAll done. No errors expected on exit!")

if __name__ == "__main__":
    main()
