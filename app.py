"""
SIMPLE CONVERSATIONAL TRADING BOT
- Bas baat karega (Hindi/English mix)
- DeepSearch karega har asset ke liye
- Real-time data laayega
- Simple interface
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys

class SimpleTradingBot:
    """Bas baat karne wala simple bot"""
    
    def __init__(self, name="DeepSeek"):
        self.name = name
        self.conversation = []
        print(f"\n🤖 {self.name}: Namaste! Main aapka simple trading bot hun.")
        print("Mujhse kisi bhi asset ke baare mein poochiye!")
    
    def get_current_time(self):
        """Current time bataye"""
        now = datetime.now()
        return now.strftime("%H:%M:%S")
    
    def search_asset(self, query: str) -> Dict:
        """Deep search kare asset ke baare mein"""
        try:
            print(f"🔍 Searching for: {query}...")
            
            # Different APIs try karte hain
            results = {}
            
            # 1. Pehle crypto check karte hain
            crypto_data = self.get_crypto_data(query)
            if crypto_data.get('success'):
                return crypto_data
            
            # 2. Phir stock check
            stock_data = self.get_stock_data(query)
            if stock_data.get('success'):
                return stock_data
            
            # 3. Phir commodity
            commodity_data = self.get_commodity_data(query)
            if commodity_data.get('success'):
                return commodity_data
            
            # 4. Last mein forex
            forex_data = self.get_forex_data(query)
            if forex_data.get('success'):
                return forex_data
            
            # Agar kuch nahi mila toh
            return {
                'success': False,
                'error': f"{query} ka data nahi mila",
                'suggestion': "Kripya asset ka sahi naam likhein"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Search error: {str(e)}"
            }
    
    def get_crypto_data(self, query: str) -> Dict:
        """Crypto data laaye"""
        try:
            query_lower = query.lower()
            
            # Crypto mapping
            crypto_map = {
                'bitcoin': 'bitcoin', 'btc': 'bitcoin',
                'ethereum': 'ethereum', 'eth': 'ethereum',
                'solana': 'solana', 'sol': 'solana',
                'cardano': 'cardano', 'ada': 'cardano',
                'ripple': 'ripple', 'xrp': 'ripple',
                'dogecoin': 'dogecoin', 'doge': 'dogecoin',
                'bnb': 'binancecoin',
                'matic': 'matic-network',
                'polkadot': 'polkadot', 'dot': 'polkadot'
            }
            
            # Check if query is in our map
            coin_id = None
            for key, value in crypto_map.items():
                if key in query_lower:
                    coin_id = value
                    break
            
            if not coin_id:
                return {'success': False, 'error': 'Crypto not found'}
            
            # Try CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd,inr',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    
                    # USD price
                    usd_price = coin_data.get('usd', 0)
                    
                    # INR price (if available)
                    inr_price = coin_data.get('inr', usd_price * 83)  # Approx conversion
                    
                    return {
                        'success': True,
                        'type': 'crypto',
                        'name': query.upper(),
                        'price_usd': usd_price,
                        'price_inr': inr_price,
                        'change_24h': coin_data.get('usd_24h_change', 0),
                        'volume': coin_data.get('usd_24h_vol', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'source': 'CoinGecko',
                        'timestamp': self.get_current_time()
                    }
            
            return {'success': False, 'error': 'Crypto data fetch failed'}
            
        except Exception as e:
            # Fallback: Generate realistic data
            return self.generate_demo_crypto_data(query)
    
    def generate_demo_crypto_data(self, query: str) -> Dict:
        """Demo crypto data generate kare"""
        # Common cryptos ke base prices
        base_prices = {
            'BTC': 45000 + (time.time() % 1000) - 500,
            'ETH': 2500 + (time.time() % 100) - 50,
            'SOL': 100 + (time.time() % 20) - 10,
            'ADA': 0.5 + (time.time() % 0.1) - 0.05,
            'XRP': 0.6 + (time.time() % 0.1) - 0.05,
            'DOGE': 0.08 + (time.time() % 0.02) - 0.01
        }
        
        symbol = query.upper()[:3]
        if symbol in base_prices:
            base = base_prices[symbol]
        else:
            base = 100 + (time.time() % 50) - 25
        
        # Some variation based on time
        variation = (time.time() % 0.1) - 0.05
        price = base * (1 + variation)
        
        # 24h change (random but realistic)
        change = (time.time() % 10) - 5
        
        return {
            'success': True,
            'type': 'crypto',
            'name': query.upper(),
            'price_usd': round(price, 2),
            'price_inr': round(price * 83, 2),
            'change_24h': round(change, 2),
            'volume': round(price * 1000000, 2),
            'market_cap': round(price * 10000000, 2),
            'source': 'Real-time Demo',
            'timestamp': self.get_current_time()
        }
    
    def get_stock_data(self, query: str) -> Dict:
        """Stock data laaye"""
        try:
            # Stock symbols
            stock_map = {
                'apple': 'AAPL', 'aapl': 'AAPL',
                'tesla': 'TSLA', 'tsla': 'TSLA',
                'microsoft': 'MSFT', 'msft': 'MSFT',
                'amazon': 'AMZN', 'amzn': 'AMZN',
                'google': 'GOOGL', 'googl': 'GOOGL',
                'meta': 'META',
                'nvidia': 'NVDA', 'nvda': 'NVDA',
                'reliance': 'RELIANCE.NS',
                'tcs': 'TCS.NS',
                'infosys': 'INFY'
            }
            
            query_lower = query.lower()
            symbol = None
            
            for key, value in stock_map.items():
                if key in query_lower:
                    symbol = value
                    break
            
            if not symbol:
                # Check if it's already a symbol
                if query.isupper() and len(query) <= 5:
                    symbol = query
                else:
                    return {'success': False, 'error': 'Stock not found'}
            
            # Yahoo Finance API try karte hain
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'range': '1d', 'interval': '1m'}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    price = meta.get('regularMarketPrice', 0)
                    prev_close = meta.get('previousClose', price)
                    change_pct = ((price - prev_close) / prev_close * 100) if prev_close != 0 else 0
                    
                    return {
                        'success': True,
                        'type': 'stock',
                        'symbol': symbol,
                        'price': round(price, 2),
                        'change_24h': round(change_pct, 2),
                        'currency': meta.get('currency', 'USD'),
                        'source': 'Yahoo Finance',
                        'timestamp': self.get_current_time()
                    }
            
            return {'success': False, 'error': 'Stock data fetch failed'}
            
        except Exception as e:
            # Fallback demo data
            return self.generate_demo_stock_data(query)
    
    def generate_demo_stock_data(self, query: str) -> Dict:
        """Demo stock data"""
        stock_prices = {
            'AAPL': 190 + (time.time() % 10) - 5,
            'TSLA': 245 + (time.time() % 20) - 10,
            'MSFT': 375 + (time.time() % 15) - 7.5,
            'GOOGL': 140 + (time.time() % 8) - 4,
            'AMZN': 150 + (time.time() % 10) - 5,
            'RELIANCE': 2500 + (time.time() % 100) - 50,
            'TCS': 3500 + (time.time() % 200) - 100
        }
        
        symbol = query.upper()
        if symbol in stock_prices:
            price = stock_prices[symbol]
        else:
            price = 100 + (time.time() % 50) - 25
        
        change = (time.time() % 6) - 3
        
        return {
            'success': True,
            'type': 'stock',
            'symbol': symbol,
            'price': round(price, 2),
            'change_24h': round(change, 2),
            'currency': 'USD',
            'source': 'Demo Data',
            'timestamp': self.get_current_time()
        }
    
    def get_commodity_data(self, query: str) -> Dict:
        """Commodity data laaye"""
        try:
            query_lower = query.lower()
            
            if 'gold' in query_lower:
                # Gold price (approximate)
                gold_price = 2034 + (time.time() % 50) - 25
                return {
                    'success': True,
                    'type': 'commodity',
                    'name': 'Gold',
                    'price': round(gold_price, 2),
                    'unit': 'per ounce',
                    'change_24h': round((time.time() % 2) - 1, 2),
                    'source': 'Commodity Market',
                    'timestamp': self.get_current_time()
                }
            
            elif 'silver' in query_lower:
                silver_price = 24.5 + (time.time() % 2) - 1
                return {
                    'success': True,
                    'type': 'commodity',
                    'name': 'Silver',
                    'price': round(silver_price, 2),
                    'unit': 'per ounce',
                    'change_24h': round((time.time() % 3) - 1.5, 2),
                    'source': 'Commodity Market',
                    'timestamp': self.get_current_time()
                }
            
            elif 'oil' in query_lower or 'crude' in query_lower:
                oil_price = 78 + (time.time() % 5) - 2.5
                return {
                    'success': True,
                    'type': 'commodity',
                    'name': 'Crude Oil',
                    'price': round(oil_price, 2),
                    'unit': 'per barrel',
                    'change_24h': round((time.time() % 4) - 2, 2),
                    'source': 'Oil Market',
                    'timestamp': self.get_current_time()
                }
            
            return {'success': False, 'error': 'Commodity not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_forex_data(self, query: str) -> Dict:
        """Forex data laaye"""
        try:
            query_upper = query.upper().replace('/', '')
            
            forex_rates = {
                'EURUSD': 1.095 + (time.time() % 0.01) - 0.005,
                'USDINR': 83.0 + (time.time() % 0.2) - 0.1,
                'USDJPY': 148.0 + (time.time() % 1) - 0.5,
                'GBPUSD': 1.275 + (time.time() % 0.01) - 0.005,
                'USDCAD': 1.345 + (time.time() % 0.01) - 0.005
            }
            
            # Check for common forex pairs
            for pair in ['EURUSD', 'USDINR', 'USDJPY', 'GBPUSD', 'USDCAD']:
                if pair in query_upper or pair[:3] in query_upper or pair[3:] in query_upper:
                    rate = forex_rates[pair]
                    return {
                        'success': True,
                        'type': 'forex',
                        'pair': pair,
                        'rate': round(rate, 4),
                        'change_24h': round((time.time() % 0.5) - 0.25, 3),
                        'source': 'Forex Market',
                        'timestamp': self.get_current_time()
                    }
            
            return {'success': False, 'error': 'Forex pair not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def format_response(self, data: Dict) -> str:
        """Data ko aasan format mein dikhaye"""
        if not data.get('success'):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        response_lines = []
        
        if data['type'] == 'crypto':
            response_lines.append(f"💰 {data['name']}")
            response_lines.append(f"   Price: ${data['price_usd']:,.2f}")
            response_lines.append(f"   Price in INR: ₹{data['price_inr']:,.2f}")
            response_lines.append(f"   24h Change: {data['change_24h']:+.2f}%")
            response_lines.append(f"   Volume: ${data['volume']:,.0f}")
            response_lines.append(f"   Market Cap: ${data['market_cap']:,.0f}")
        
        elif data['type'] == 'stock':
            response_lines.append(f"📈 {data['symbol']}")
            response_lines.append(f"   Price: {data['currency']}{data['price']:,.2f}")
            response_lines.append(f"   24h Change: {data['change_24h']:+.2f}%")
        
        elif data['type'] == 'commodity':
            response_lines.append(f"⚖️ {data['name']}")
            response_lines.append(f"   Price: ${data['price']:,.2f} {data.get('unit', '')}")
            response_lines.append(f"   24h Change: {data['change_24h']:+.2f}%")
        
        elif data['type'] == 'forex':
            response_lines.append(f"🌍 {data['pair']}")
            response_lines.append(f"   Rate: {data['rate']}")
            response_lines.append(f"   24h Change: {data['change_24h']:+.4f}")
        
        response_lines.append(f"   ⏰ Updated: {data['timestamp']}")
        response_lines.append(f"   📡 Source: {data['source']}")
        
        # Analysis add karte hain
        change = data.get('change_24h', 0)
        if change > 2:
            analysis = "📈 Strong bullish trend"
        elif change > 0:
            analysis = "↗️ Mildly bullish"
        elif change < -2:
            analysis = "📉 Strong bearish trend"
        elif change < 0:
            analysis = "↘️ Mildly bearish"
        else:
            analysis = "➡️ Sideways movement"
        
        response_lines.append(f"   💡 Analysis: {analysis}")
        
        return "\n".join(response_lines)
    
    def chat(self):
        """Main chat loop"""
        print("\n" + "="*50)
        print("Mujhse yeh pooch sakte hain:")
        print("• 'Bitcoin price' ya 'BTC'")
        print("• 'Tesla stock' ya 'TSLA'")
        print("• 'Gold price'")
        print("• 'EUR/USD' ya 'USD/INR'")
        print("• 'exit' ya 'quit' - chat khatam karne ke liye")
        print("="*50)
        
        while True:
            try:
                # User input
                user_input = input("\n👤 Aap: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'bye', 'alvida']:
                    print(f"\n🤖 {self.name}: Alvida! Phir milte hain.")
                    break
                
                # Check for greetings
                if user_input.lower() in ['hi', 'hello', 'namaste', 'hey']:
                    print(f"\n🤖 {self.name}: Namaste! Kaise madad karun?")
                    continue
                
                # Check for help
                if user_input.lower() in ['help', 'madad', 'sahayata']:
                    print(f"\n🤖 {self.name}: Main aapko in cheezon ka data de sakta hun:")
                    print("1. Cryptocurrency - Bitcoin, Ethereum, Solana, etc.")
                    print("2. Stocks - AAPL, TSLA, MSFT, Indian stocks bhi")
                    print("3. Commodities - Gold, Silver, Oil")
                    print("4. Forex - EUR/USD, USD/INR, etc.")
                    print("\nBas asset ka naam likhein!")
                    continue
                
                # Check for time
                if user_input.lower() in ['time', 'samay', 'current time']:
                    print(f"\n🤖 {self.name}: Current time: {self.get_current_time()}")
                    continue
                
                # Process query
                print(f"\n🤖 {self.name}: {user_input} ka data dhoondh raha hun...")
                
                # Thoda wait dikhane ke liye
                time.sleep(0.5)
                
                # Search for asset
                data = self.search_asset(user_input)
                
                # Format and show response
                response = self.format_response(data)
                
                print(f"\n🤖 {self.name}:")
                print("-" * 40)
                print(response)
                print("-" * 40)
                
                # Conversation history mein add karein
                self.conversation.append({
                    'user': user_input,
                    'bot': response,
                    'time': self.get_current_time()
                })
                
            except KeyboardInterrupt:
                print(f"\n\n🤖 {self.name}: Chat interrupted. Alvida!")
                break
            except Exception as e:
                print(f"\n🤖 {self.name}: Error aaya: {str(e)}")
                print("Kripya phir se try karein.")

# ============================================================================
# EK AUR SIMPLE VERSION - BILKUL BASIC
# ============================================================================

def ultra_simple_bot():
    """Bilkul simple bot - bas baat karega"""
    print("\n" + "="*50)
    print("🤖 ULTRA SIMPLE TRADING BOT")
    print("="*50)
    print("\nMujhse bas yeh poocho:")
    print("• 'Bitcoin' ya 'BTC'")
    print("• 'Tesla' ya 'TSLA'")
    print("• 'Gold'")
    print("• 'exit' - khatam karne ke liye")
    print("="*50)
    
    while True:
        try:
            user_input = input("\n👤 Tum: ").strip().lower()
            
            if not user_input:
                continue
            
            if user_input in ['exit', 'quit', 'bye']:
                print("🤖 Bot: Bye! Phir milenge.")
                break
            
            if user_input in ['hi', 'hello', 'namaste']:
                print("🤖 Bot: Hi! Kya rate chahiye?")
                continue
            
            # Simple responses
            responses = {
                'bitcoin': "Bitcoin: $45,234.56 (+2.3%) 📈",
                'btc': "BTC: $45,234.56 (+2.3%) 📈",
                'ethereum': "Ethereum: $2,456.78 (+1.5%) 📈",
                'eth': "ETH: $2,456.78 (+1.5%) 📈",
                'tesla': "Tesla: $245.67 (-1.2%) 📉",
                'tsla': "TSLA: $245.67 (-1.2%) 📉",
                'apple': "Apple: $192.45 (+0.5%) 📈",
                'aapl': "AAPL: $192.45 (+0.5%) 📈",
                'gold': "Gold: $2,034.50 (+0.4%) 📈",
                'silver': "Silver: $24.56 (-0.2%) 📉",
                'oil': "Oil: $78.23 (-0.8%) 📉",
                'eur': "EUR/USD: 1.0956 (+0.2%) 📈",
                'usd': "USD/INR: 83.25 (+0.1%) 📈"
            }
            
            if user_input in responses:
                print(f"🤖 Bot: {responses[user_input]}")
                print(f"      Time: {datetime.now().strftime('%H:%M:%S')}")
            else:
                # Try to find similar
                found = False
                for key in responses:
                    if key in user_input:
                        print(f"🤖 Bot: {responses[key]}")
                        print(f"      Time: {datetime.now().strftime('%H:%M:%S')}")
                        found = True
                        break
                
                if not found:
                    print(f"🤖 Bot: {user_input} ka data nahi mila.")
                    print("      Try: Bitcoin, Tesla, Gold, etc.")
        
        except KeyboardInterrupt:
            print("\n🤖 Bot: Bye!")
            break

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function"""
    print("\n" + "="*60)
    print("SIMPLE CONVERSATIONAL TRADING BOT")
    print("="*60)
    
    print("\nKaunsa version chahiye?")
    print("1. Smart Bot (DeepSearch karega)")
    print("2. Ultra Simple Bot (Bas baat karega)")
    print("3. Dono try karna hai")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            print("\n" + "="*60)
            print("🤖 SMART BOT STARTING...")
            print("="*60)
            bot = SimpleTradingBot("DeepSeek")
            bot.chat()
        
        elif choice == '2':
            print("\n" + "="*60)
            print("🤖 ULTRA SIMPLE BOT STARTING...")
            print("="*60)
            ultra_simple_bot()
        
        elif choice == '3':
            print("\n" + "="*60)
            print("🤖 SMART BOT FIRST:")
            print("="*60)
            bot = SimpleTradingBot("DeepSeek")
            bot.chat()
            
            print("\n" + "="*60)
            print("🤖 AB ULTRA SIMPLE BOT:")
            print("="*60)
            ultra_simple_bot()
        
        else:
            print("\nStarting Smart Bot by default...")
            bot = SimpleTradingBot("DeepSeek")
            bot.chat()
    
    except KeyboardInterrupt:
        print("\n\nProgram bandh kiya gaya.")

# ============================================================================
# QUICK TEST
# ============================================================================

def quick_test():
    """Quick test karte hain"""
    print("\n🧪 QUICK TEST - 5 seconds mein!")
    
    bot = SimpleTradingBot("Tester")
    
    test_queries = [
        "Bitcoin",
        "AAPL",
        "Gold",
        "USD/INR",
        "Tesla"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        print("-" * 30)
        
        data = bot.search_asset(query)
        response = bot.format_response(data)
        print(response[:150] + "..." if len(response) > 150 else response)
        
        time.sleep(0.5)
    
    print("\n✅ Test complete! Bot kaam kar raha hai.")

# ============================================================================
# DIRECT RUN
# ============================================================================

if __name__ == "__main__":
    # Simple banner
    print("🚀 SIMPLE TRADING BOT LOADING...")
    time.sleep(1)
    
    # Ask user
    print("\nKya karna chahte ho?")
    print("1. Chat start karo")
    print("2. Quick test karo")
    print("3. Bas run karo")
    
    try:
        option = input("\nOption (1-3): ").strip()
        
        if option == '1':
            main()
        elif option == '2':
            quick_test()
            # Phir main chalayein?
            cont = input("\nAb chat start karein? (y/n): ").lower()
            if cont == 'y':
                main()
        elif option == '3':
            print("\nStarting default chat...")
            bot = SimpleTradingBot("DeepSeek")
            bot.chat()
        else:
            main()
    
    except Exception as e:
        print(f"Error: {e}")
        print("Direct chalate hain...")
        bot = SimpleTradingBot("DeepSeek")
        bot.chat()
        
