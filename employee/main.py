import os
import sys
import fastapi
from .work import do_work
from dotenv import load_dotenv
from .mail import Message, MailBox
from .utils import get_time
from note.main import write_new_note

load_dotenv()

app = fastapi.FastAPI()

mailbox = MailBox()

@app.post("/api")
def api(message_in: Message):
    message_in.time_received = get_time()
    email = mailbox.new_mail(message_in)
    email.write(str(message_in))
    message_in.save(mailbox)
    message_out = do_work(message_in)
    message_out.time_sent = get_time()
    email = mailbox.new_mail(message_out)
    return message_out

def run_interactive():
    while True:
        content = input(">>> ")
        if content == "exit":
            break

        message = Message(
            content=content,
            sender="manager",
            subject="inquiry",
            time_sent=get_time(),
            time_received=get_time(),
        )
        email = mailbox.new_mail(message)
        email.write(str(message))
        write_new_note(str(message))
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
