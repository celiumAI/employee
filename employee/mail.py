import os
from pydantic import BaseModel
from dotenv import load_dotenv
import yaml

from note.model import Note, Repository
from .utils import get_time
from pathlib import Path

load_dotenv()

PATH_MAIL = Path(os.getenv("PATH_MAIL", "./data/mails"))
EDITOR = os.getenv('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
FILE_EXTENSION = "md"


class Message(Note):
    sender: str
    receivers: list[str] = [os.environ["ID"]]
    subject: str
    content: str
    time_sent: int
    time_received: int = None

    def __str__(self):
        frontmatter = yaml.dump({
            "sender": self.sender,
            "receivers": self.receivers,
            "subject": self.subject,
            "time_sent": self.time_sent,
            "time_received": self.time_received,
        })
        return f"---\n{frontmatter}---\n{self.content}"
    
    def save(self, repo: Repository = None):
        if repo is None:
            repo_context = Repository(path="./data" ,node_type=Note)
            repo_context.ensure_exists()
            repo_mails = Repository(path=repo_context.path / "mails", node_type=Note)
            repo_mails.ensure_exists()
            repo = Repository(path=repo_mails.path / str(self.subject), node_type=Note)
            repo.ensure_exists()

        if self.time_received is None:
            self.time_received = get_time()

        # add a chain to build a representation of the other agent
        note = Note.new(repo)
        with open(note.path, "w") as f:
            f.write(str(self))
    
    @staticmethod
    def from_path(path: str) -> "Message":
        with open(path, "r") as f:
            content = f.read()
        frontmatter, content = content.split("---")
        frontmatter = yaml.load(frontmatter)
        message = Message(**frontmatter, content=content)
        return message

class MailBox(Repository):
    path: Path = PATH_MAIL
    node_type: Message = Message
    extension: str = FILE_EXTENSION

