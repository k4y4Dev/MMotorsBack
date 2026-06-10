# case_management_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..schemas.case_management_schema import (
    CaseManagementResponse,
    CaseManagementUpdate,
    CaseManagementCreate,
    AdminCaseManagementResponse,
    CarCaseSummary
)
from ..service.case_management_service import (
    get_active_case_by_user,
    update_case_status,
    create_case,
    get_all_active_cases,
    get_cases_grouped_by_car
)
from ..models.user_model import User
from ..models.case_management_model import CaseManagement
from ..service.auth_py import get_current_user  # votre dépendance d'auth JWT

router = APIRouter()


# ── GET : dossier en cours ────────────────────────────────────────────────────
@router.get("/",  response_model=list[AdminCaseManagementResponse])
def get_all_cases(
    db: Session = Depends(get_db),
    #current_user: User = Depends(get_current_user),  # user connecté
):
    return get_all_active_cases(db)

@router.get("/grouped", response_model=list[CarCaseSummary])
def get_cases_by_car(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
):
    return get_cases_grouped_by_car(db)

@router.get("/me/active", response_model=CaseManagementResponse)
def read_my_active_case(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # user connecté
):
    """
    Accessible par l'utilisateur connecté.
    Retourne son dossier en cours (pending ou processing).
    """
    return get_active_case_by_user(db, user_id=current_user.id)


@router.get("/{user_id}/active", response_model=CaseManagementResponse)
def read_user_active_case(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accessible par l'admin uniquement.
    Retourne le dossier en cours d'un utilisateur donné.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs."
        )
    return get_active_case_by_user(db, user_id=user_id)


# ── PATCH : mise à jour du statut ─────────────────────────────────────────────

@router.patch("/{case_id}/status", response_model=CaseManagementResponse)
def update_status(
    case_id: int,
    payload: CaseManagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accessible par l'admin uniquement.
    Met à jour le statut d'un dossier :
      pending → processing → approved | refused
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs."
        )
    return update_case_status(db, case_id=case_id, new_status=payload.status)

@router.post("/", response_model=CaseManagementResponse, status_code=status.HTTP_201_CREATED)
def create_new_case(
    payload: CaseManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accessible par l'utilisateur connecté.
    Crée un nouveau dossier pour la voiture ciblée.
    Un seul dossier actif (pending/processing) autorisé à la fois.
    """
    return create_case(db, user_id=current_user.id, car_id=payload.car_id)
#    return create_case(db, user_id=payload.user_id,  car_id=payload.car_id)