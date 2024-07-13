from datetime import datetime, timezone
from prefect import flow, task

from utils import get_supabase_client, get_reddit_client, get_slack_client

# Get jobs from supabase
@task(log_prints=True)
def get_jobs(req, supabase):
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
    print("Error when fetching jobs from database")
    raise e

@task(log_prints=True)
def post_content(req,jobs):
  try:
    #reddit connection
    subreddit = get_reddit_client(req['schema']) if req.get('post_to_reddit') else None

    #slack connection
    slack = get_slack_client() if req.get('post_to_slack') else None

    #get current timestamp
    report_at = datetime.now(tz=timezone.utc).isoformat()
    
    all_posts = []
    
    # Iterate through jobs
    for job in jobs:
      job_title = job.get('job_title')
      company_name = job.get('employer_name')
      apply_link = job.get('job_apply_link')
      remote = job.get("job_is_remote")
      city = job.get("job_city")
      state = job.get("job_state")
      country =job.get("job_country")
      
      # Create the location string
      if city and state and country and remote:
        location = f"{city}, {state}, {country} - (remote)"
      elif city and state and country:
        location = f"{city}, {state}, {country}"
      elif remote:
        location = 'Remote'
      else:
        location = None

      # Create the post content - used for slack and LI. Slack and LI are the only destinations using the list (report)
      post_content = f"{company_name} is hiring a {job_title}\n- {location if location else 'Location not specified'}\n- Apply here: {apply_link}\n{req.get('hash_tags')}\n"
      all_posts.append(post_content)

      job['li_posted_at'] = report_at

      # Post to reddit
      if subreddit:
        post_title = f"{location + ': ' if location else ''}{job_title}"
        post_content = f"{company_name} is hiring a {job_title}\n* {location if location else 'Location not specified'}\n* Apply here: [{apply_link}]({apply_link})\n\n{req.get('hash_tags')}"

        subreddit.submit(post_title, selftext=post_content)
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
    print("Error when posting content")
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
    print("Error when updating jobs in database")
    raise e


#Get jobs
@flow(log_prints=True)
def post_jobs(req):
  try:
    print(f"Start post jobs function for {req.get('schema')}")
    supabase = get_supabase_client(req)
    jobs = get_jobs(req, supabase)

    if jobs:
      jobs = post_content(req,jobs)
      update_jobs(jobs, supabase)
      print(f"successfully posted {len(jobs)} jobs for schema: {req.get('schema')}")
    else:
      print("No new jobs found")
  except Exception as e:
    print("Error in post_jobs flow")
    raise e