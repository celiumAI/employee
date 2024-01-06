import sys
import fastapi
from pydantic import BaseModel
import note
from .interface import run_query

class Text(BaseModel):
    text: str

app = fastapi.FastAPI()

@app.post("/api")
def api(text: Text):
    return run(text.text)

def run(text: str = None):
    if text is not None:
        note.main.write_new_note(text)

    run_query(input("Communication:"))
    

def serve():
    import uvicorn
    import os
    uvicorn.run(app, host=os.environ["HOST"], port=os.environ["PORT"])

def cli():
    """CLI entry point."""
    import fire
    if len(sys.argv) == 1:
        run()
        exit()

    fire.Fire({
        'run': run,
        'serve': serve,
    })

if __name__ == "__main__":
    cli()