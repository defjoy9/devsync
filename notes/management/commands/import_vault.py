# notes/management/commands/import_vault.py
import os
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from notes.models import Note

WIKILINK_RE = re.compile(r'\[\[([^\]]+?)\]\]')

class Command(BaseCommand):
    help = "Import markdown files from a vault into Note objects (and create links)."

    def add_arguments(self, parser):
        parser.add_argument('--path', required=True, help='Path to your vault root directory')

    def handle(self, *args, **options):
        vault_path = options['path']
        # first pass: create or update notes
        created = 0; updated = 0; files = []
        for dirpath, _, filenames in os.walk(vault_path):
            for fname in filenames:
                if fname.lower().endswith('.md'):
                    full = os.path.join(dirpath, fname)
                    files.append(full)
                    with open(full, encoding='utf8') as f:
                        text = f.read()
                    # find title from first heading or filename
                    m = re.search(r'^\s*#\s+(.+)$', text, re.MULTILINE)
                    title = m.group(1).strip() if m else os.path.splitext(os.path.basename(full))[0]
                    slug = slugify(title)
                    note, created_flag = Note.objects.get_or_create(slug=slug, defaults={'title': title, 'content': text})
                    if not created_flag:
                        # update content & title
                        note.title = title
                        note.content = text
                        note.save()
                        updated += 1
                    else:
                        created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported/updated {created} created, {updated} updated notes.'))

        # second pass: create links
        Note.objects.all().update()  # ensure cached relations clear
        for note in Note.objects.all():
            note.links.clear()
            for target in WIKILINK_RE.findall(note.content):
                target_title = target.strip()
                target_slug = slugify(target_title)
                target_note = None
                try:
                    target_note = Note.objects.get(slug=target_slug)
                except Note.DoesNotExist:
                    # create placeholder note so graph isn't broken
                    target_note = Note.objects.create(title=target_title, slug=target_slug, content='')
                note.links.add(target_note)
        self.stdout.write(self.style.SUCCESS('Links updated.'))
