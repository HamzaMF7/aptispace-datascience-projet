import json
import os
import subprocess
import sys
import uuid

# Répertoires de travail
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
notebooks_dir = os.path.join(base_dir, 'notebooks')
# Répertoires de travail dans le dossier gitignoré 'build'
build_dir = os.path.join(base_dir, 'build')
src_dir = os.path.join(build_dir, 'src')
logs_dir = os.path.join(build_dir, 'logs')
report_notebooks_dir = os.path.join(build_dir, 'notebooks')

# S'assurer que les répertoires de destination existent
os.makedirs(src_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(report_notebooks_dir, exist_ok=True)

# Scan dynamique des notebooks présents (tous les fichiers .ipynb triés par ordre alphabétique)
notebook_files = sorted([f for f in os.listdir(notebooks_dir) if f.endswith('.ipynb')])

print(f"🚀 Début de la compilation de {len(notebook_files)} notebooks...")

for nb_file in notebook_files:
    nb_path = os.path.join(notebooks_dir, nb_file)

        
    name_no_ext = os.path.splitext(nb_file)[0]
    
    # Lecture du fichier de notebook JSON
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb_data = json.load(f)
        
    py_lines = []
    qmd_lines = []
    
    # Injection des imports de chemin système au début du script pour s'exécuter proprement
    py_lines.append("import os, sys")
    py_lines.append(f"sys.path.append('{base_dir}')\n")
    
    for cell in nb_data.get('cells', []):
        cell_type = cell.get('cell_type')
        source = cell.get('source', [])
        
        # Force la conversion en liste de lignes si string unique
        if isinstance(source, str):
            source = source.splitlines(keepends=True)
            
        source_str = "".join(source)
        
        if cell_type == 'markdown':
            qmd_lines.append(source_str + "\n\n")
        elif cell_type == 'code':
            # Ignore les cellules vides
            if not source_str.strip():
                continue
            
            # Génération du bloc de code pour Quarto (.qmd)
            qmd_lines.append("```{python}\n")
            qmd_lines.append(source_str)
            if not source_str.endswith("\n"):
                qmd_lines.append("\n")
            qmd_lines.append("```\n\n")

            # Recherche des sorties Plotly dans la cellule
            plotly_html = None
            for output in cell.get('outputs', []):
                data = output.get('data', {})
                if 'application/vnd.plotly.v1+json' in data:
                    plotly_data = data['application/vnd.plotly.v1+json']
                    fig_data = json.dumps(plotly_data.get('data', []))
                    fig_layout = json.dumps(plotly_data.get('layout', {}))
                    fig_config = json.dumps(plotly_data.get('config', {}))
                    div_id = f"plotly-{uuid.uuid4()}"
                    plotly_html = f"""<div id="{div_id}" style="width:100%; height:400px; background: white; border-radius: 8px;"></div>
<script type="text/javascript">
  document.addEventListener("DOMContentLoaded", function() {{
    if (typeof Plotly !== 'undefined') {{
      Plotly.newPlot('{div_id}', {fig_data}, {fig_layout}, {fig_config});
    }} else {{
      console.error("Plotly library is not loaded.");
    }}
  }});
</script>
"""
                    break
                elif 'text/html' in data:
                    html_lines = data['text/html']
                    if isinstance(html_lines, list):
                        html_content = "".join(html_lines)
                    else:
                        html_content = html_lines
                    if 'plotly' in html_content.lower() or 'plotly-graph-div' in html_content:
                        plotly_html = html_content
                        break
            
            if plotly_html:
                qmd_lines.append("::: {.content-visible unless-format=\"pdf\"}\n")
                qmd_lines.append(plotly_html)
                if not plotly_html.endswith("\n"):
                    qmd_lines.append("\n")
                qmd_lines.append(":::\n\n")
            
            # Alimentation des lignes de script Python (.py) - en commentant les commandes magiques IPython (% ou !) pour éviter les SyntaxError
            py_cell_lines = []
            for line in source:
                stripped_line = line.strip()
                if stripped_line.startswith('%') or stripped_line.startswith('!'):
                    py_cell_lines.append(f"# {line}")
                else:
                    py_cell_lines.append(line)
            py_cell_str = "".join(py_cell_lines)
            py_lines.append(py_cell_str)
            if not py_cell_str.endswith("\n"):
                py_lines.append("\n")
                
    # 1. Écriture du script Python à exécuter (.py) dans src/
    py_file_path = os.path.join(src_dir, f"{name_no_ext}.py")
    with open(py_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(py_lines))
    print(f"  ➡️  [PY]  Généré : {py_file_path}")
    
    # 2. Écriture du fichier Quarto Markdown (.qmd) dans report/notebooks/
    qmd_file_path = os.path.join(report_notebooks_dir, f"{name_no_ext}.qmd")
    with open(qmd_file_path, 'w', encoding='utf-8') as f:
        f.write("".join(qmd_lines))
    print(f"  ➡️  [QMD] Généré : {qmd_file_path}")
    
    # 3. Exécution et capture des résultats dans un fichier journal (.log) dans logs/
    log_file_path = os.path.join(logs_dir, f"{name_no_ext}.log")
    try:
        result = subprocess.run(
            [sys.executable, py_file_path],
            capture_output=True,
            text=True,
            env={**os.environ, "MPLBACKEND": "agg"},
            cwd=notebooks_dir,
            timeout=30  # Timeout pour éviter les boucles infinies de code étudiant
        )
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)
        print(f"  ➡️  [LOG] Généré : {log_file_path} (Exit Code: {result.returncode})")
    except subprocess.TimeoutExpired:
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("❌ ÉCHEC : Temps d'exécution limite dépassé (30s).")
        print(f"  ➡️  [LOG] Généré : {log_file_path} (TIMEOUT)")
    except Exception as e:
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"❌ ÉCHEC : Erreur lors de l'exécution : {e}")
        print(f"  ➡️  [LOG] Généré : {log_file_path} (ERROR)")

print("✅ Compilation des notebooks terminée !")
