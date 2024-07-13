from prefect import flow, task
from prefect_github.repository import GitHubRepository

from utils import get_supabase_client

@task(log_prints=True)
def call_supabase_function(supabase):
    try:
        response = supabase.rpc('db_clean_up').execute()
        print("Called supabase function successfully")
    except Exception as e:
        print("Error when calling supabase function")
        raise e

@flow(log_prints=True)
def clean_up_db():
    print("Cleaning up database")
    req = {"schema": "medtechfindr"}

    supabase = get_supabase_client(req)

    call_supabase_function(supabase)

if __name__ == "__main__":
    '''
    clean_up_db.from_source(
        source=GitHubRepository.load("findr-scheduler"),
        entrypoint="db_clean_up.py:clean_up_db"
    ).deploy(
        name="Clean up DB",
        work_pool_name="findr"
    )
    '''
    clean_up_db()
