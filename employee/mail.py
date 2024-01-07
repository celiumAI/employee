import os
from pydantic import BaseModel
from dotenv import load_dotenv
import yaml

from note.model import Repository, Note, Node
from .utils import get_time
from pathlib import Path

load_dotenv()

PATH_MAIL = Path(os.getenv("PATH_MAIL", "./data/mails"))
EDITOR = os.getenv('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
FILE_EXTENSION = "md"


class Message(BaseModel):
    sender: str
    receivers: list[str] = [os.environ["ID"]]
    subject: str
    content: str
    time_sent: int = get_time()
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
    
    @staticmethod
    def from_node(node: Node) -> "Message":
        with open(node.path, "r") as f:
            content = f.read()
        frontmatter, content = content.split("---")
        frontmatter = yaml.load(frontmatter)
        message = Message(**frontmatter, content=content)
        return message

class Mail(Node):
    """a mail is a node in a mailbox"""
    @classmethod
    def new(cls, repo: "MailBox") -> "Mail":
        index = repo.get_last_index() + 1
        mail = Mail(repo=repo, index=index)
        return mail

class MailBox(Repository):
    """a mailbox is a repository of messages"""
    path: Path = PATH_MAIL
    node_type: Mail = Mail

    def new_mail(self, message: Message) -> Node:
        """create a new mail"""

        repo_message = MailBox(path = self.path / message.subject)
        repo_message.ensure_exists()

        mail = Mail.new(repo_message)

        return mail
