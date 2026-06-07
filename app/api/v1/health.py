from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Vision API is running"}


@router.get("/health")
def health_check():
    return {"status": "ok"}
