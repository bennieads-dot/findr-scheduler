import json

medtech_findr_reqs = {
  "post": {
    "payloads": [
      {
        "limit": 10,
        "schema": "medtechfindr",
        "hash_tags": "\#MedicalTechnicianJobs #HiringMedicalTechnicians #MedTechCareers",
        "post_to_slack": True,
        "post_to_reddit": True
      }
    ]
  },
  "pull": {
    "payloads": [
      {
        "query": "cardiovascular tech in New York, NY",
        "schema": "medtechfindr",
        "job_titles": "Radiologic Technologist, Radiographer, X-Ray Technician, Computed Tomography (CT) Technologist, Magnetic Resonance Imaging (MRI) Technologist, Mammographer, Nuclear Medicine Technologist, Radiation Therapist, Interventional Radiology Technologist, Vascular Interventional Technologist, Sonographer, Ultrasound Technician, Cardiovascular Technologist, Cardiac Catheterization Technologist, Echocardiography Technician, Electrocardiogram (EKG/ECG) Technician, Stress Test Technician, Cardiac Sonographer, Vascular Technologist, Cardiac Electrophysiology Specialist, Cardiac Device Technician, Pacemaker Technician, Perfusionist"
      },
      {
        "query": "radiology tech in New York, Ny",
        "schema": "medtechfindr",
        "job_titles": "Radiologic Technologist, Radiographer, X-Ray Technician, Computed Tomography (CT) Technologist, Magnetic Resonance Imaging (MRI) Technologist, Mammographer, Nuclear Medicine Technologist, Radiation Therapist, Interventional Radiology Technologist, Vascular Interventional Technologist, Sonographer, Ultrasound Technician, Cardiovascular Technologist, Cardiac Catheterization Technologist, Echocardiography Technician, Electrocardiogram (EKG/ECG) Technician, Stress Test Technician, Cardiac Sonographer, Vascular Technologist, Cardiac Electrophysiology Specialist, Cardiac Device Technician, Pacemaker Technician, Perfusionist"
      }
    ]
  }
}