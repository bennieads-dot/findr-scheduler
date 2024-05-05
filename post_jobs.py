import praw
import slack_sdk
from datetime import datetime, timezone

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from prefect.blocks.system import Secret
from prefect import flow, task

#Get jobs from supabase
@task(log_prints=True)
def fetch_jobs(req, supabase):
  columns = ["job_id","job_title","employer_name","job_apply_link","job_is_remote","job_city","job_state","job_country"]
  print("Querying DB for jobs")
  try:
    response = supabase.table('jobs') \
                .select(','.join(columns)) \
                .is_('li_posted_at', 'NULL') \
                .is_('reddit_posted_at', 'NULL') \
                .order('job_id') \
                .limit(req.get('limit')) \
                .execute()
    print(f"Found {len(response.data)} jobs")
    return response.data
  except Exception as e:
    raise e

@task(log_prints=True)
def post_jobs_func(req,jobs):
  try:
    #reddit connection
    reddit = praw.Reddit(
        client_id=Secret.load('reddit-app-client-id').get(),
        client_secret=Secret.load('reddit-app-client-secret').get(),
        user_agent=Secret.load('reddit-app-user-agent').get(),
        username=Secret.load('reddit-username').get(),
        password=Secret.load('reddit-password').get()
    ) if req.get('post_to_reddit') else None

    #slack connection
    slack = slack_sdk.WebClient(token=Secret.load('slack-token').get()) if req.get('post_to_slack') else None

    report_at = datetime.now(tz=timezone.utc).isoformat()
    all_posts = []
    #iterate through jobs
    for job in jobs:
      job_title = job.get('job_title')
      company_name = job.get('employer_name')
      apply_link = job.get('job_apply_link')
      remote = job.get("job_is_remote")
      city = job.get("job_city")
      state = job.get("job_state")
      country =job.get("job_country")

      location = f"{city}, {state}, {country}"
      
      if city and state and country and remote:
        location = f"{city}, {state}, {country} - (remote)"
      elif city and state and country:
        location = f"{city}, {state}, {country}"
      elif remote:
        location = 'Remote'
      else:
        location = None

      # Create the post content
      post_content = f"{company_name} is hiring a {job_title}\n- {location if location else 'Location not specified'}\n- Apply here: {apply_link}\n{req.get('hash_tags')}\n"
      all_posts.append(post_content)

      job['li_posted_at'] = report_at

      #post to reddit
      if reddit:
        channel_map = {"medtechfindr": "medtechjobs"}
        
        subreddit = reddit.subreddit(channel_map.get(req.get('schema')))

        post_content = f"{company_name} is hiring a {job_title}\n* {location if location else 'Location not specified'}\n* Apply here: [{apply_link}]({apply_link})\n* {req.get('hash_tags')}"

        subreddit.submit(job_title, selftext=post_content)
        job['reddit_posted_at'] = report_at

    report = "\n".join(all_posts)
    
    #post report to slack channel
    if slack:
      slack.chat_postMessage(
        channel=req.get('schema'),
        text=report
      )
      #print(report)
    return jobs
  except Exception as e:
    raise e

@task(log_prints=True)
def update_jobs(jobs, supabase):
  print("Updating jobs after posting")
  try:
  #update posting timestamps
    supabase.table('jobs') \
      .upsert(jobs) \
      .execute()
  except Exception as e:
    raise e


#Get jobs
@flow(log_prints=True)
def post_jobs(req):
  try:
    supabase_url: str = Secret.load("supabase-findr-url").get()
    supabase_key: str = Secret.load("supabase-findr-key").get()

    opts = ClientOptions().replace(schema = req.get('schema'))
    supabase: Client = create_client(supabase_url, supabase_key, options=opts)

    print(f"Start post jobs function for {req.get('schema')}")
    jobs = fetch_jobs(req, supabase)

    if jobs:
      jobs = post_jobs_func(req,jobs)
      update_jobs(jobs, supabase)
      print(f"successfully posted {len(jobs)} jobs for model: {req.get('schema')}")
    else:
      print("No new jobs found")
  except Exception as e:
    raise e