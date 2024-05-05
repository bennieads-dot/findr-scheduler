from prefect import flow, task

from default_reqs import default_reqs

from import_jobs import import_jobs
from post_jobs import post_jobs

@task(log_prints=True)
def import_medtechfinder_jobs(payloads:dict):
    try:
      if not payloads:
          print("No items in the pull payload")
          raise Exception("No items in the post payload")
      [import_jobs(payload) for payload in payloads.get('payloads')]
    except Exception as e:
      raise e

@task(log_prints=True)
def post_medtechfindr_jobs(payloads:dict):
    try:
      if not payloads:
        print("No items in the post payload")
        raise Exception("No items in the post payload")
      [post_jobs(payload) for payload in payloads.get('payloads')]
    except Exception as e:
        raise e
        

@flow(log_prints=True)
def medtechfindr(reqs:dict = None):

    if not reqs:
      reqs = default_reqs
    
    try:
      if reqs.get('pull').get('payloads'):
        import_medtechfinder_jobs(reqs.get('pull'))

      if reqs.get('post').get('payloads'):
        post_medtechfindr_jobs(reqs.get('post'))

    except Exception as e:
       print(e)

if __name__ == "__main__":
    # For deploying to work pool
    '''
    medtechfindr.from_source(
      source=GitHubRepository.load("findr-scheduler"), 
      entrypoint="medtechfindr.py:medtechfindr"
    ).deploy(
      name="medtechfindr Daily",
      work_pool_name="findr",
    )
    '''
    medtechfindr()