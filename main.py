# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.sql_db import create_all_tables, SessionLocal
from models.sql_models import User
from api.routes import router


def seed_if_empty():
    """Seed the database if it's empty — safe to run on every startup."""
    db = SessionLocal()
    try:
        count = db.query(User).count()
        if count == 0:
            print("🌱 Empty database detected. Seeding initial data...")
            from seed_data import seed
            seed()
            print("✅ Seed complete.")
        else:
            print(f"✅ Database already has {count} users. Skipping seed.")
    except Exception as e:
        print(f"⚠️ Seed check failed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables()
    print("✅ Database tables ready.")
    seed_if_empty()
    yield


app = FastAPI(
    title="Vani.coach API",
    description="AI-powered speech coaching with 3-layer memory architecture",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")

@app.post("/admin/seed")
def manual_seed():
    from database.sql_db import SessionLocal
    from models.sql_models import User
    import traceback
    db = SessionLocal()
    try:
        count = db.query(User).count()
        if count == 0:
            from seed_data import seed
            seed()
            db2 = SessionLocal()
            count_after = db2.query(User).count()
            db2.close()
            return {"status": "seeded", "users_after": count_after}
        return {"status": "already seeded", "users": count}
    except Exception as e:
        return {"status": "error", "detail": str(e), "trace": traceback.format_exc()}
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Vani.coach API is running"}