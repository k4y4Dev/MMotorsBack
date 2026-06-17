# case_management_service.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from itertools import groupby

from ..models.case_management_model import CaseManagement
from ..schemas.case_management_schema import CaseStatus, AdminCaseManagementResponse

# ── GET ──────────────────────────────────────────────────────────────────────

def get_all_active_cases(db: Session) -> list[AdminCaseManagementResponse]:
    query  = select(CaseManagement).filter(
            CaseManagement.status.in_([CaseStatus.PENDING, CaseStatus.PROCESSING]))
    cases = db.execute(query).scalars().all()
    
    return cases

def get_cases_grouped_by_car(db: Session) -> list[dict]:
    cases = db.execute(
        select(CaseManagement)
        .filter(CaseManagement.status.in_([CaseStatus.PENDING, CaseStatus.PROCESSING]))
        .order_by(CaseManagement.car_id)  # ✅ obligatoire pour groupby
    ).scalars().all()

    grouped = []
    for car_id, group in groupby(cases, key=lambda c: c.car_id):
        group_list = list(group)
        car = group_list[0].car  # tous ont la même voiture

        grouped.append({
            "car": {                  # ← objet imbriqué qui correspond à CarResponse
                "id": car.id,
                "name": car.name,
                "price": car.price,
                "km": car.km,
                "image": car.image,
                "trade": car.trade,
            },
            "pending_count": len(group_list),
            "cases": [
                {
                    "case_id": c.id,
                    "email": c.user.email,
                    "lastname": c.user.lastname,
                    "firstname": c.user.firstname,
                    "status": c.status,
                    "doc_links": [
                        {
                            "id": doc.id,
                            "user_id": doc.user_id,
                            "doc_type": doc.doc_type,
                            "doc_url": doc.doc_url,
                            "created_at": doc.created_at,
                        }
                        for doc in c.user.doc_links
                    ],
                    "created_at": c.created_at,
                }
                for c in group_list
            ]
        })

    return grouped

def get_active_case_by_user(db: Session, user_id: int) -> CaseManagement:
    """Retourne le dossier actif (non refusé/accepté) de l'utilisateur."""
    case = (
        db.query(CaseManagement)
        .filter(
            CaseManagement.user_id == user_id,
            CaseManagement.status.in_([CaseStatus.PENDING, CaseStatus.PROCESSING])
        )
        .first()
    )
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun dossier en cours pour cet utilisateur."
        )
    return case


def get_case_by_id(db: Session, case_id: int) -> CaseManagement:
    """Retourne un dossier par son id (usage admin)."""
    case = db.query(CaseManagement).filter(CaseManagement.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier introuvable."
        )
    return case


# ── UPDATE ───────────────────────────────────────────────────────────────────

def update_case_status(
    db: Session,
    case_id: int,
    new_status: CaseStatus
) -> CaseManagement:
    """Met à jour le statut d'un dossier (admin uniquement)."""
    case = get_case_by_id(db, case_id)
    case.status = new_status
    db.commit()
    db.refresh(case)
    return case


# ── CREATE ───────────────────────────────────────────────────────────────────

def create_case(db: Session, user_id: int, car_id: int) -> CaseManagement:
    active = (
        db.query(CaseManagement)
        .filter(
            CaseManagement.user_id == user_id,
            CaseManagement.status.in_([CaseStatus.PENDING, CaseStatus.PROCESSING])
        )
        .first()
    )
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="L'utilisateur a déjà un dossier en cours."
        )
    new_case = CaseManagement(user_id=user_id, car_id=car_id, status=CaseStatus.PENDING)
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case