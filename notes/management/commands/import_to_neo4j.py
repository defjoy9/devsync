import os, re
from django.core.management.base import BaseCommand
from neo4j import GraphDatabase

WIKILINK_RE = re.compile(r'\[\[([^\]]+?)\]\]')

class Command(BaseCommand):
    help = "Import markdown files into Neo4j"

    def add_arguments(self, parser):
        parser.add_argument('--path', required=True, help='Path to vault folder')
        parser.add_argument('--uri', default='bolt://localhost:7687')
        parser.add_argument('--user', default='neo4j')
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        path = options['path']
        uri = options['uri']
        user = options['user']
        password = options['password']

        driver = GraphDatabase.driver(uri, auth=(user, password))

        notes = {}

        # 1️⃣ Read files
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                if fname.endswith(".md"):
                    full = os.path.join(dirpath, fname)
                    with open(full, "r", encoding="utf-8") as f:
                        text = f.read()
                    title = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
                    title = title.group(1).strip() if title else os.path.splitext(fname)[0]
                    links = WIKILINK_RE.findall(text)
                    notes[title] = {"content": text, "links": links}

        # 2️⃣ Push to Neo4j
        with driver.session() as session:
            for title, data in notes.items():
                session.run("MERGE (n:Note {title: $title, content: $content})",
                            title=title, content=data["content"])

            for title, data in notes.items():
                for linked_title in data["links"]:
                    session.run("""
                        MATCH (a:Note {title: $title})
                        MERGE (b:Note {title: $linked_title})
                        MERGE (a)-[:LINKS_TO]->(b)
                    """, title=title, linked_title=linked_title)

        self.stdout.write(self.style.SUCCESS(f"Imported {len(notes)} notes to Neo4j."))
