import logging
import os
import requests

from prefect.variables import Variable
from prefect.blocks.system import Secret
from prefect import flow, task

from models.models import jobListModel
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

@task(log_prints=True)
def find_jobs(req):
  try:
    jsearch_url = Variable.get('jsearch_url').value
    jsearch_host = Variable.get('jsearch_host').value
    jsearch_key = Secret.load("jsearch-key").get()

    url = jsearch_url
    querystring = {"query":req.get('query'),
                  "page":"1",
                  "num_pages":"1",
                  "job_titles":req.get('job_titles'),
                  "exclude_job_publishers": "indeed,glassdoor,ziprecruiter,linkedin"
    }
    headers = {
      "X-RapidAPI-Key": jsearch_key,
      "X-RapidAPI-Host": jsearch_host
    }
    print(f"Finding new jobs for {req.get('schema')}")
    response = requests.get(url, headers=headers, params=querystring).json()
    print(f"Retrieved {len(response.get('data'))} jobs")
    return response
  except Exception as e:
    raise e

@task(log_prints=True)
def transform_jobs(jobs):
  try:
    print("Validating fetched jobs")
    jobs = jobListModel(**jobs).model_dump()
    print("Jobs validated successfully")
    return jobs
  except Exception as e:
    raise e

@task(log_prints=True)
def merge_jobs(req, jobs):
  url: str = Secret.load("supabase-findr-url").get()
  key: str = Secret.load("supabase-findr-key").get()

  opts = ClientOptions().replace(schema = req.get('schema'))
  supabase: Client = create_client(url, key, options=opts)

  print("Upserting jobs")
  try:
    supabase.table('jobs') \
    .upsert(jobs.get('data')) \
    .execute()
    print(f"successfully merged: {len(jobs.get('data'))} jobs for model: {req.get('schema')}")
  except Exception as e:
    raise e
  
@flow(log_prints=True)
def import_jobs(payload):
  try:
    print(f"Importing jobs for {payload.get('schema')}")
    jobs = find_jobs(payload)
    if not jobs:
      raise Exception("No jobs retrieved")
    jobs = transform_jobs(jobs)
    merge_jobs(payload, jobs)
  except Exception as e:
      raise e