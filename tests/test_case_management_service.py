import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch, PropertyMock

from src.schemas.case_management_schema import CaseStatus
from src.service.case_management_service import (
    get_all_active_cases,
    get_cases_grouped_by_car,
    get_active_case_by_user,
    get_case_by_id,
    update_case_status,
    create_case,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_mock_user(user_id: int = 1, email: str = "user@example.com",
                   firstname: str = "Jean", lastname: str = "Test"):
    user = MagicMock()
    user.id = user_id
    user.email = email
    user.firstname = firstname
    user.lastname = lastname
    return user


def make_mock_car(car_id: int = 10, name: str = "Tesla Model 3",
                  price: int = 40000, km: int = 15000,
                  image: str = "tesla.jpg", trade: bool = False):
    car = MagicMock()
    car.id = car_id
    car.name = name
    car.price = price
    car.km = km
    car.image = image
    car.trade = trade
    return car


def make_mock_case(case_id: int = 1, user_id: int = 1, car_id: int = 10,
                   status: CaseStatus = CaseStatus.PENDING):
    case = MagicMock()
    case.id = case_id
    case.user_id = user_id
    case.car_id = car_id
    case.status = status
    case.user = make_mock_user(user_id)
    case.car = make_mock_car(car_id)
    return case


# ── get_all_active_cases ──────────────────────────────────────────────────────

class TestGetAllActiveCases:

    def test_returns_pending_and_processing_cases(self):
        """Doit retourner les dossiers PENDING et PROCESSING."""
        db = MagicMock()
        cases = [
            make_mock_case(1, status=CaseStatus.PENDING),
            make_mock_case(2, status=CaseStatus.PROCESSING),
        ]
        db.execute.return_value.scalars.return_value.all.return_value = cases

        result = get_all_active_cases(db)

        assert result == cases
        assert len(result) == 2

    def test_returns_empty_list_when_no_active_cases(self):
        """Doit retourner une liste vide s'il n'y a aucun dossier actif."""
        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = []

        result = get_all_active_cases(db)

        assert result == []


# ── get_cases_grouped_by_car ──────────────────────────────────────────────────

class TestGetCasesGroupedByCar:

    def test_groups_cases_by_car(self):
        """Doit regrouper les dossiers par car_id."""
        db = MagicMock()
        car = make_mock_car(car_id=10)
        case1 = make_mock_case(1, car_id=10, status=CaseStatus.PENDING)
        case2 = make_mock_case(2, car_id=10, status=CaseStatus.PROCESSING)
        case1.car = car
        case2.car = car

        db.execute.return_value.scalars.return_value.all.return_value = [case1, case2]

        result = get_cases_grouped_by_car(db)

        assert len(result) == 1
        group = result[0]
        assert group["car"]["id"] == 10
        assert group["pending_count"] == 2
        assert len(group["cases"]) == 2

    def test_groups_cases_by_multiple_cars(self):
        """Doit créer un groupe par voiture distincte."""
        db = MagicMock()
        car_a = make_mock_car(car_id=10, name="Tesla")
        car_b = make_mock_car(car_id=20, name="BMW")

        case1 = make_mock_case(1, car_id=10)
        case2 = make_mock_case(2, car_id=20)
        case1.car = car_a
        case2.car = car_b

        db.execute.return_value.scalars.return_value.all.return_value = [case1, case2]

        result = get_cases_grouped_by_car(db)

        assert len(result) == 2
        car_ids = [g["car"]["id"] for g in result]
        assert 10 in car_ids
        assert 20 in car_ids

    def test_case_fields_are_correct(self):
        """Chaque entrée de 'cases' doit contenir les bons champs utilisateur."""
        db = MagicMock()
        car = make_mock_car(car_id=10)
        user = make_mock_user(user_id=1, email="john@example.com",
                              firstname="John", lastname="Doe")
        case = make_mock_case(1, car_id=10)
        case.car = car
        case.user = user

        db.execute.return_value.scalars.return_value.all.return_value = [case]

        result = get_cases_grouped_by_car(db)
        case_entry = result[0]["cases"][0]

        assert case_entry["case_id"] == 1
        assert case_entry["email"] == "john@example.com"
        assert case_entry["firstname"] == "John"
        assert case_entry["lastname"] == "Doe"

    def test_returns_empty_list_when_no_cases(self):
        """Doit retourner une liste vide s'il n'y a aucun dossier actif."""
        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = []

        result = get_cases_grouped_by_car(db)

        assert result == []


# ── get_active_case_by_user ───────────────────────────────────────────────────

class TestGetActiveCaseByUser:

    def test_returns_active_case(self):
        """Doit retourner le dossier actif de l'utilisateur."""
        db = MagicMock()
        case = make_mock_case(user_id=1, status=CaseStatus.PENDING)
        db.query.return_value.filter.return_value.first.return_value = case

        result = get_active_case_by_user(db, user_id=1)

        assert result == case

    def test_raises_404_when_no_active_case(self):
        """Doit lever une 404 si l'utilisateur n'a aucun dossier actif."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_active_case_by_user(db, user_id=99)

        assert exc_info.value.status_code == 404


# ── get_case_by_id ────────────────────────────────────────────────────────────

class TestGetCaseById:

    def test_returns_case_when_found(self):
        """Doit retourner le dossier correspondant à l'id."""
        db = MagicMock()
        case = make_mock_case(case_id=5)
        db.query.return_value.filter.return_value.first.return_value = case

        result = get_case_by_id(db, case_id=5)

        assert result == case
        assert result.id == 5

    def test_raises_404_when_not_found(self):
        """Doit lever une 404 si le dossier n'existe pas."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_case_by_id(db, case_id=999)

        assert exc_info.value.status_code == 404


# ── update_case_status ────────────────────────────────────────────────────────

class TestUpdateCaseStatus:

    def test_updates_status_successfully(self):
        """Doit mettre à jour le statut et retourner le dossier modifié."""
        db = MagicMock()
        case = make_mock_case(case_id=1, status=CaseStatus.PENDING)
        db.query.return_value.filter.return_value.first.return_value = case

        result = update_case_status(db, case_id=1, new_status=CaseStatus.PROCESSING)

        assert case.status == CaseStatus.PROCESSING
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(case)

    def test_raises_404_when_case_not_found(self):
        """Doit lever une 404 si le dossier à modifier n'existe pas."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            update_case_status(db, case_id=999, new_status=CaseStatus.PROCESSING)

        assert exc_info.value.status_code == 404
        db.commit.assert_not_called()

    @pytest.mark.parametrize("new_status", [
        CaseStatus.PENDING,
        CaseStatus.PROCESSING,
    ])
    def test_accepts_all_valid_statuses(self, new_status):
        """Doit accepter tous les statuts valides."""
        db = MagicMock()
        case = make_mock_case(case_id=1)
        db.query.return_value.filter.return_value.first.return_value = case

        update_case_status(db, case_id=1, new_status=new_status)

        assert case.status == new_status


# ── create_case ───────────────────────────────────────────────────────────────

class TestCreateCase:

    def test_creates_case_successfully(self):
        """Doit créer un nouveau dossier si l'utilisateur n'en a pas d'actif."""
        db = MagicMock()
        # Pas de dossier actif existant
        db.query.return_value.filter.return_value.first.return_value = None

        result = create_case(db, user_id=1, car_id=10)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

        # Vérifie que le bon objet a été ajouté
        added_case = db.add.call_args[0][0]
        assert added_case.user_id == 1
        assert added_case.car_id == 10
        assert added_case.status == CaseStatus.PENDING

    def test_raises_409_when_active_case_exists(self):
        """Doit lever une 409 si l'utilisateur a déjà un dossier en cours."""
        db = MagicMock()
        existing_case = make_mock_case(user_id=1, status=CaseStatus.PENDING)
        db.query.return_value.filter.return_value.first.return_value = existing_case

        with pytest.raises(HTTPException) as exc_info:
            create_case(db, user_id=1, car_id=10)

        assert exc_info.value.status_code == 409
        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_new_case_has_pending_status(self):
        """Le nouveau dossier doit avoir le statut PENDING par défaut."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        create_case(db, user_id=2, car_id=5)

        added_case = db.add.call_args[0][0]
        assert added_case.status == CaseStatus.PENDING

    def test_different_users_can_have_active_cases(self):
        """Deux utilisateurs différents peuvent chacun avoir un dossier actif."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        create_case(db, user_id=1, car_id=10)
        create_case(db, user_id=2, car_id=10)

        assert db.add.call_count == 2