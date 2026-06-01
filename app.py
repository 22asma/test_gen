from flask import Flask, render_template, request #framework web
from test_generator import generate_test_cases #fonction importée du fichier précédent
import re #pour nettoyer la sortie de l’IA

app = Flask(__name__)

def clean_ollama_output(text):
    """Nettoie les commentaires et messages conversationnels d'Ollama"""
    
    # Supprimer les phrases d'introduction communes
    introduction_patterns = [
        r"Here (?:are|is).*?[:\n]",
        r"I'm (?:glad|happy) to help.*?[:\n]",
        r"Sure.*?[:\n]",
        r"Of course.*?[:\n]",
        r"Let me .*?[:\n]",
        r"I'll .*?[:\n]",
        r"Below (?:are|is).*?[:\n]",
        r"This is .*?(?:example|test).*?[:\n]",
        r"Please note.*?\.",
        r"Note:.*?\.",
        r"Important:.*?\.",
        r"Remember.*?\.",
        r"Keep in mind.*?\.",
    ]
    
    for pattern in introduction_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Supprimer les paragraphes explicatifs (lignes qui ne sont pas du code)
    lines = text.split('\n')
    cleaned_lines = []
    skip_next = False
    
    for line in lines:
        # Garder les lignes vides
        if not line.strip():
            cleaned_lines.append(line)
            continue
            
        # Supprimer les lignes qui ressemblent à des explications
        if re.match(r'^(?:This|These|The|In|For|You|We|It|As|Based).*', line.strip(), re.IGNORECASE):
            if not any(char in line for char in ['{', '}', '[', ']', '(', ')', '=', ':', 'def ', 'class ', 'import ', 'from ', 'Given ', 'When ', 'Then ', 'Scenario', 'Feature']):
                continue
        
        # Supprimer les notes et avertissements
        if re.match(r'^(?:Note|Important|Remember|Warning|Tip):', line.strip(), re.IGNORECASE):
            continue
            
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Nettoyer les espaces multiples au début et à la fin
    cleaned_text = cleaned_text.strip()
    
    # Supprimer les lignes vides excessives (plus de 2 consécutives)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    return cleaned_text
#GET : affiche le formulaire vide.
#POST : récupère les valeurs du formulaire 
@app.route("/", methods=["GET", "POST"])
def index():
    scenarios = ""
    test_type = "gherkin"
    requirements = ""
    
    if request.method == "POST":
        requirements = request.form["requirements"]
        test_type = request.form["test_type"]
        req = {"requirement": requirements}
        raw_output = generate_test_cases(req, test_type)
        scenarios = clean_ollama_output(raw_output)

    return render_template(
        "index.html", 
        output=scenarios,
        test_type=test_type,
        requirements=requirements
    )
#Lancement du serveur
if __name__ == "__main__":
    app.run(debug=True)