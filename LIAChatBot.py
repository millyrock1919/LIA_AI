import tweepy
from wallet_analyzer import WalletAnalyzer
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

class LIAChatBot:
    def __init__(self, rpc_url="https://api.mainnet-beta.solana.com"):
        """
        Initialize LIA AI chatbot backend.
        
        Args:
            rpc_url (str): Solana RPC endpoint URL for blockchain data access.
        """
        # Twitter API credentials
        self.twitter_api_keys = {
            "consumer_key": "d8f7a9x3KpRq2Jz17VbN",
            "consumer_secret": "Z9x7FyT8NhLmP4QaWbFj3kYp5Rt2Vx6LJkT3FgMq",
            "access_token": "13764828293-aJxFyNqPmZ9LpQ2R7VyT8LmXbK3Yf5LkT",
            "access_token_secret": "p9x7Z8LmR6Q2FJbT5YkN3Vx4FyPmT6aJLqW8Rt",
        }
        self.api = self._initialize_twitter_api()
        self.analyzer = WalletAnalyzer(rpc_url)

    def _initialize_twitter_api(self):
        """
        Authenticate and connect to the Twitter API.
        
        Returns:
            tweepy.API: Authenticated Twitter API client.
        """
        auth = tweepy.OAuthHandler(
            self.twitter_api_keys["consumer_key"],
            self.twitter_api_keys["consumer_secret"]
        )
        auth.set_access_token(
            self.twitter_api_keys["access_token"],
            self.twitter_api_keys["access_token_secret"]
        )
        return tweepy.API(auth)

    def _extract_wallet_address(self, text):
        """
        Extract a Solana wallet address from text.
        
        Args:
            text (str): Text to scan for wallet addresses.
        
        Returns:
            str: The wallet address if found, otherwise None.
        """
        pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def fetch_mentions(self):
        """
        Fetch recent mentions of the bot's Twitter account.
        
        Returns:
            list: List of fetched tweets.
        """
        mentions = self.api.mentions_timeline(count=10, tweet_mode="extended")
        return mentions

    def analyze_wallet_from_tweet(self, tweet):
        """
        Extract wallet address from tweet, analyze it, and return results.
        
        Args:
            tweet (tweepy.Status): The tweet mentioning the bot.
        
        Returns:
            dict: Analysis result or an error message.
        """
        wallet_address = self._extract_wallet_address(tweet.full_text)
        if wallet_address:
            return self.analyzer.generate_summary(wallet_address)
        return {"error": "No valid wallet address found."}

    def process_mentions(self):
        """
        Process mentions, extract wallet addresses, and trigger analysis.
        
        Returns:
            list: Results of analysis for each mention.
        """
        mentions = self.fetch_mentions()
        results = []
        for tweet in mentions:
            result = self.analyze_wallet_from_tweet(tweet)
            results.append({
                "tweet_id": tweet.id,
                "user": tweet.user.screen_name,
                "analysis": result
            })
        return results

# Flask Routes
@app.route("/process_mentions", methods=["GET"])
def process_mentions():
    """
    Endpoint to trigger processing of Twitter mentions and return analysis results.
    
    Returns:
        Response: JSON response with the results.
    """
    bot = LIAChatBot()
    results = bot.process_mentions()
    return jsonify(results)

@app.route("/analyze_wallet", methods=["POST"])
def analyze_wallet():
    """
    Endpoint to analyze a wallet address provided in the request.
    
    Args:
        wallet_address (str): Wallet address to analyze.
    
    Returns:
        Response: JSON response with the analysis result.
    """
    data = request.json
    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    bot = LIAChatBot()
    result = bot.analyzer.generate_summary(wallet_address)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
