import json
import requests
from prefect.variables import Variable
from prefect.blocks.system import Secret
from prefect import flow, task
from prefect_github.repository import GitHubRepository

@task
def pull_jobs(payload:dict):
    try:
      url = Variable.get('pull_jobs_func_url').value
      func_key = Secret.load('pull-jobs-func-key').get()
      headers = {
        'x-functions-key': func_key,
        'Content-Type': 'application/json'
      }
      response = requests.post(url, headers=headers, data=json.dumps(payload))
      if response.status_code != 200:
        raise Exception(f'Error in pull task: {response.status_code} - {response.text}')
      print(response.text)
    except Exception as e:
      raise e

@task
def post_jobs(payload:dict):
    try:
      url = Variable.get('post_jobs_func_url').value
      func_key = Secret.load('post-jobs-func-key').get()
      headers = {
        'x-functions-key': func_key,
        'Content-Type': 'application/json'
      }
      response = requests.post(url, headers=headers, data=json.dumps(payload))
      if response.status_code != 200:
        raise Exception(f'Error in post task: {response.status_code} - {response.text}')
      print(response.text)
    except Exception as e:
      raise e


@flow(log_prints=True)
def medtechfindr():
    try:
      '''
      pull_jobs({
          "schema": "medtechfindr",
          "query": "cardiovascular tech in New York, NY",
          "job_titles": "Radiologic Technologist, Radiographer, X-Ray Technician, Computed Tomography (CT) Technologist, Magnetic Resonance Imaging (MRI) Technologist, Mammographer, Nuclear Medicine Technologist, Radiation Therapist, Interventional Radiology Technologist, Vascular Interventional Technologist, Sonographer, Ultrasound Technician, Cardiovascular Technologist, Cardiac Catheterization Technologist, Echocardiography Technician, Electrocardiogram (EKG/ECG) Technician, Stress Test Technician, Cardiac Sonographer, Vascular Technologist, Cardiac Electrophysiology Specialist, Cardiac Device Technician, Pacemaker Technician, Perfusionist"
      })

      pull_jobs({
          "schema": "medtechfindr",
          "query": "radiology tech in New York, Ny",
          "job_titles": "Radiologic Technologist, Radiographer, X-Ray Technician, Computed Tomography (CT) Technologist, Magnetic Resonance Imaging (MRI) Technologist, Mammographer, Nuclear Medicine Technologist, Radiation Therapist, Interventional Radiology Technologist, Vascular Interventional Technologist, Sonographer, Ultrasound Technician, Cardiovascular Technologist, Cardiac Catheterization Technologist, Echocardiography Technician, Electrocardiogram (EKG/ECG) Technician, Stress Test Technician, Cardiac Sonographer, Vascular Technologist, Cardiac Electrophysiology Specialist, Cardiac Device Technician, Pacemaker Technician, Perfusionist"
      })
      '''
      post_jobs({
          "schema":"medtechfindr",
          "limit": 10,
          "hash_tags": "#MedicalTechnicianJobs #HiringMedicalTechnicians #MedTechCareers",
          "post_to_reddit": True,
          "post_to_slack": True
      })

    except Exception as e:
       print(e)

if __name__ == "__main__":
    '''
    medtechfindr.serve(
        name="medtechfindr Daily",
        cron = "0 1 * * *",
        description="Pulls and posts medtechfindr jobs daily at",
    )
    '''
    # For deploying to work pool
    medtechfindr.from_source(
      source=GitHubRepository.load("findr-scheduler"), 
      entrypoint="medtechfindr.py:medtechfindr"
    ).deploy(
      name="medtechfindr Daily",
      work_pool_name="findr",
    )