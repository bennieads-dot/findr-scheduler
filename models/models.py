from pydantic import BaseModel
from typing import Optional, List

class JobModel(BaseModel):
    job_id: str
    employer_name: str
    employer_logo: Optional[str]
    employer_website: Optional[str]
    employer_company_type: Optional[str]
    job_publisher: Optional[str]
    job_employment_type: Optional[str]
    job_title: str
    job_apply_link: str
    job_apply_is_direct: Optional[bool]
    job_apply_quality_score: Optional[float]
    job_is_remote: Optional[bool]
    job_posted_at_timestamp: Optional[int]
    job_posted_at_datetime_utc: Optional[str]
    job_city: Optional[str]
    job_state: Optional[str]
    job_country: Optional[str]
    job_latitude: Optional[float]
    job_longitude: Optional[float]
    job_google_link: Optional[str]
    job_offer_expiration_datetime_utc: Optional[str]
    job_offer_expiration_timestamp: Optional[int]
    job_experience_in_place_of_education: Optional[bool]
    job_min_salary: Optional[float]
    job_max_salary: Optional[float]
    job_salary_currency: Optional[str]
    job_salary_period: Optional[str]

class jobListModel(BaseModel):
  data: List[JobModel]
