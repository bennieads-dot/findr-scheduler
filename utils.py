import praw
import slack_sdk
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from prefect.blocks.system import Secret

# Get supabase client
def get_supabase_client(req):
  print("creating supabase connection client")
  try:
    supabase_url: str = Secret.load("supabase-findr-url").get()
    supabase_key: str = Secret.load("supabase-findr-key").get()

    opts = ClientOptions().replace(schema = req.get('schema'))
    supabase: Client = create_client(supabase_url, supabase_key, options=opts)
    print(f"Connected to schema: {req.get('schema')}")

    return supabase
  except Exception as e:
    print("Error when getting supabase client")
    raise e

def get_reddit_client(schema):
  print("creating reddit connection")
  try:
    channel_map = {"medtechfindr": "medtechjobs"}
    reddit = praw.Reddit(
        client_id=Secret.load('reddit-app-client-id').get(),
        client_secret=Secret.load('reddit-app-client-secret').get(),
        user_agent=Secret.load('reddit-app-user-agent').get(),
        username=Secret.load('reddit-username').get(),
        password=Secret.load('reddit-password').get()
    )
    subreddit = reddit.subreddit(channel_map.get(schema))
    print("Connected to Reddit")
    return subreddit
  except Exception as e:
    print("Error when getting reddit client")
    raise e
  
def get_slack_client():
  print("creating slack connection")
  try:
    slack = slack_sdk.WebClient(token=Secret.load('slack-token').get())
    print("Connected to slack")
    return slack
  except Exception as e:
    print("Error when getting slack client")
    raise e