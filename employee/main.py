import os
import sys
import fastapi
from .work import do_work
from dotenv import load_dotenv
from .mail import Message, MailBox
from .utils import get_time

load_dotenv()

app = fastapi.FastAPI()

@app.post("/api")
def api(message_in: Message):
    message_in.time_received = get_time()
    message_in.save()
    message_out = do_work(message_in)
    return message_out

def run_interactive():
    while True:
        content = input(">>> ")
        if content == "exit":
            break
        message = Message.new(MailBox())
        message = Message(
            content=content,
            sender="manager",
            subject="inquiry",
            time_sent=get_time(),
            repo=message.repo,
            index=message.index
        )
        message.save()
        response = do_work(message)
        print(f"final response: {response.content}")

def serve():
    import uvicorn
    import os
    uvicorn.run(app, port=int(os.environ["PORT"]))

def cli():
    """CLI entry point."""
    import fire
    if len(sys.argv) == 1:
        run_interactive()
        exit()

    fire.Fire({
        'run': run_interactive,
        'serve': serve,
    })

if __name__ == "__main__":
    cli()
