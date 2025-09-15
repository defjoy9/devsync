# notes/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from notes.models import Note
from notes.neo4j_utils import run_query

def notes_graph(request):
    query = "MATCH (n:Note)-[r:LINKS_TO]->(m:Note) RETURN n.title as from, m.title as to"
    edges = run_query(query)
    nodes_set = set()
    for e in edges:
        nodes_set.add(e['from'])
        nodes_set.add(e['to'])
    nodes = [{'id': i, 'label': n} for i, n in enumerate(nodes_set)]
    # Build edges for vis.js
    return render(request, "notes/graph.html", {"nodes": nodes, "edges": edges})

def graph_api(request):
    notes = Note.objects.all()  # make sure this returns something
    nodes = []
    edges = []
    for n in notes:
        nodes.append({
            'id': n.id,
            'label': n.title,
            'title': n.title,
            'url': f'/notes/{n.slug}/'
        })
        for linked in n.links.all():
            edges.append({'from': n.id, 'to': linked.id})

    return JsonResponse({'nodes': nodes, 'edges': edges})


def graph_page(request):
    return render(request, 'notes/graph.html')

def note_detail(request, slug):
    note = get_object_or_404(Note, slug=slug)
    # render markdown to HTML (see security note below)
    import markdown as md
    html = md.markdown(note.content, extensions=['extra', 'toc'])
    # optional: sanitize with bleach (recommended)
    try:
        import bleach
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p','pre','span','h1','h2','h3','code']
        html = bleach.clean(html, tags=allowed_tags, strip=True)
    except Exception:
        pass

    return render(request, 'notes/note_detail.html', {'note': note, 'html': html})
