from fastapi import APIRouter, Query, Depends
from app.repositories.template_repository import TemplateRepository
from app.models.api_models import Template
from typing import List

router = APIRouter()


@router.get("/get-all-templates", response_model=List[Template])
async def get_all_templates():
    templates = await TemplateRepository().get_all()
    template_list = []
    for template in templates:
        template_list.append(Template(**template))
    return template_list
