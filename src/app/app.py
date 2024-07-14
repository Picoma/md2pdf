#!/usr/bin/env python

from flask import Flask, render_template, request, send_from_directory, send_file, url_for, abort
import os
import subprocess
import tempfile

app = Flask(__name__)

###################################### PARAMETRES #####################################

# Chemin vers le dossier contenant les templates
MD_TEMPLATES_DIR  = os.getcwd() + '/static/templates/md'
TEX_TEMPLATES_DIR = os.getcwd() + '/static/templates/tex'

###################################### HELPER FUNCTIONS #####################################

def convert_single_file(md_file,template):
    # Enregistrement du fichier .md dans un fichier temporaire
    temp_md_file = tempfile.NamedTemporaryFile(suffix=".md").name
    md_file.save(temp_md_file)
    
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf_file :
        # Exécution de la commande pandoc avec les options spécifiées
        cmd = [
            'pandoc',
            temp_md_file,
            '-o',
            temp_pdf_file.name,
            '--from',
            'markdown',
            '-F', 'mermaid-filter',
            '--template',
            TEX_TEMPLATES_DIR + "/" + template,
            '--listings'
        ]
        subprocess.run(cmd)
        
        # Suppression du fichier temporaire md (n'ayant pas été supprimé)...
        os.remove(temp_md_file)
        
        # ... puis renvoi du pdf produit
        return send_file(temp_pdf_file.name, as_attachment=True)

def convert_from_folder(user_files, md_file, template):
    # Crée un dossier temporaire
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        # Y sauvegarde les fichiers reçus par la requête
        for file in user_files : file.save(tmp_dir_name + "/" + file.filename)
        md_file.save(tmp_dir_name + "/" + md_file.filename)
        
        # Création d'un fichier temporaire qui contiendra le fichier pdf produit
        with tempfile.NamedTemporaryFile(suffix=".pdf", dir=tmp_dir_name) as temp_pdf_file :
            # Exécution de la commande pandoc avec les options spécifiées
            cmd = [
                'pandoc',
                md_file.filename,
                '-o',
                temp_pdf_file.name,
                '--from',
                'markdown',
                '--template',
                TEX_TEMPLATES_DIR + "/" + template,
                '--listings'
            ]
            subprocess.run(cmd, cwd=tmp_dir_name)
        
            # renvoi du pdf produit
            return send_file(temp_pdf_file.name, as_attachment=True)


###################################### FRONT-END #####################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/templates')
def get_md_templates():
    files = os.listdir(MD_TEMPLATES_DIR)
    return render_template('get_md_templates.html', files=files)

@app.route('/convert', methods=['GET'])
def get_upload_interface():
    tex_templates = os.listdir(TEX_TEMPLATES_DIR)
    return render_template('convert.html', tex_templates=tex_templates)

###################################### BACK-END #####################################

@app.route('/templates/<path:filename>')
def dl_md_template(filename):
    return send_from_directory(MD_TEMPLATES_DIR, filename, as_attachment=True)

@app.route('/convert', methods=['POST'])
def convert_user_file_to_pdf():
    # Récupère les données du formulaire
    md_file = request.files["md_file"]
    user_files = request.files.getlist("user_files")
    template = request.form['tex_template_selection']
    
    # Si aucun fichier annexe n'a été envoyé :
    if user_files[0].filename == '':
        return convert_single_file(md_file, template)
    else :
        return convert_from_folder(user_files, md_file, template)

#####################################################################################

if __name__ == '__main__':
    app.run()
 
