import tweepy
import os

bearer_token = os.getenv("bearer_token")
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

bearer_client = tweepy.Client(bearer_token=bearer_token)
sender = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

def normalize_to_text(options):
  options = options[:-1]
  total_votes = 0
  for option in options:
    total_votes = total_votes + option['votes']
  if total_votes == 0:
    total_votes = 1
  reply_text = ''
  for option in options:
    option['votes'] = option['votes']/total_votes
    reply_text+=option['label']+ ' - '+ str(int(option['votes']*100))+ '%'+ '\n'
  return reply_text

class Normalizer(tweepy.StreamingClient):
  
  def on_connect(self):
    print("connected")
    return super().on_connect()
  
  def on_response(self, response):
    print(response)
    return super().on_response(response)

  def on_tweet(self, tweet):
    try:
      tweet_full = bearer_client.get_tweet(
        tweet.referenced_tweets[0]["id"],
        poll_fields="id,options,voting_status",
        expansions="attachments.poll_ids"
      )
      print(tweet_full)
      poll_options = tweet_full.includes["polls"][0].options  # type: ignore
      text = normalize_to_text(poll_options)
      sender.create_tweet(text = text, in_reply_to_tweet_id = tweet.id)
      print(text)
    except:
      raise


streaming_client = Normalizer(bearer_token)
streaming_client.delete_rules([i.id for i in streaming_client.get_rules()[0]])  # type: ignore
streaming_client.add_rules(tweepy.StreamRule("@Poll_Normalizer"))
print(streaming_client.get_rules())
streaming_client.filter(tweet_fields = "referenced_tweets")