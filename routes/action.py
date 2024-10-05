from fastapi import APIRouter, HTTPException
from app.services.action_service import ActionService
from app.models.request_models import ActionRequest

action_router = APIRouter()
action_service = ActionService()

@action_router.post("/")
def create_action(request: ActionRequest):
    action_service.add_action(request.action_data)
    return {"status": "Action added"}

@action_router.get("/")
def list_actions():
    actions = action_service.get_all_actions()
    return {"actions": actions}

@action_router.put("/{action_id}")
def update_action(action_id: int, request: ActionRequest):
    updated_action = action_service.get_action_by_id(action_id)
    if updated_action:
        return {"status": "Action updated"}
    else:
        raise HTTPException(status_code=404, detail="Action not found")

@action_router.delete("/{action_id}")
def delete_action(action_id: int):
    action_service.delete_action(action_id)
    return {"status": "Action deleted"}
