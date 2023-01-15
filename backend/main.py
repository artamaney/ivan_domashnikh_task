import platform
from functools import cache

import fastapi
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import datetime
import uuid
from pydantic import BaseModel, BaseSettings

import ydb

TABLE_NAME = "notes"


class Note(BaseModel):
    note_id: str = 0
    author: str
    text: str
    title: str
    created_at: datetime.datetime = datetime.datetime.today()


class NoteHandlerSettings(BaseSettings):
    endpoint = "grpcs://ydb.serverless.yandexcloud.net:2135"
    db = "/ru-central1/b1gf81qohugfbonfebbj/etnsosa269pg1r1b9mna"
    driver_timeout = 7
    host = "0.0.0.0"
    port = 8080

    class Config:
        env_prefix = "NOTE_HANDLER_"


class NoteHandler:
    def __init__(self, settings: NoteHandlerSettings):
        self._settings = settings
        self._driver = ydb.Driver(endpoint=settings.endpoint, database=settings.db)
        self._pool = None

    def connect(self):
        self._driver.wait(timeout=self._settings.driver_timeout, fail_fast=True)
        self._pool = ydb.SessionPool(self._driver)


    def close(self):
        self._driver.stop(timeout=self._settings.driver_timeout)

    def insert_note(self, author: str, title: str, text: str, note_id=0, created_at=0):
        def func(session):
            generated_uuid = uuid.uuid4()
            current_date_formatted = datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            query = """
                INSERT INTO {} (note_id, author, title, text, created_at)
                VALUES ("{}", "{}", "{}", '{}', DATETIME('{}'));
            """.format(
                TABLE_NAME, generated_uuid, author, title, text, current_date_formatted
            )
            session.transaction().execute(query, commit_tx=True)

            return Note(
                note_id=str(generated_uuid),
                author=author,
                text=text,
                title=title,
                created_at=current_date_formatted,
            )

        return self._pool.retry_operation_sync(func)

    def get_notes(self):
        def callee(session):
            result = []
            query = """
                SELECT note_id, author, title, text, created_at FROM {};
            """.format(
                TABLE_NAME
            )
            query_result = session.transaction().execute(query)

            if not query_result:
                return result

            for row in query_result[0].rows:
                print(row.created_at)
                result.append(
                    Note(
                        note_id=row.note_id,
                        author=row.author,
                        title=row.title,
                        text=row.text,
                        created_at=row.created_at,
                    )
                )

            return result

        return self._pool.retry_operation_sync(callee)


@cache
def note_handler():
    return NoteHandler(NoteHandlerSettings())


router = APIRouter()


@router.get("/version")
def app_version():
    with open(".version", "r") as f:
        return f.read(), platform.node()


@router.get("/notes")
def notes(note_handler = fastapi.Depends(note_handler)):
    return note_handler.get_notes()


@router.post("/notes")
async def add_note(note: Note, note_handler = fastapi.Depends(note_handler)):
    return note_handler.insert_note(**note.dict())


def main():
    app = FastAPI()
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    handler = note_handler()
    handler.connect()
    app.note_handler = handler

    app.include_router(router)

    uvicorn.run(app, host=handler._settings.host, port=handler._settings.port)


if __name__ == "__main__":
    main()
