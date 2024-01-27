from flask import Flask, render_template, request, redirect, url_for, session
from nba_api.stats.static import players
from nba_api.stats.endpoints import CommonPlayerInfo
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # N'oublie pas de changer cela par une clé secrète sécurisée

def get_university_name(player_id):
    try:
        player_info = CommonPlayerInfo(player_id=player_id)
        university_name = player_info.common_player_info.get_dict()['COLLEGE']
        return university_name
    except ReadTimeout as e:
        # Gérer le timeout de l'API ici, par exemple, afficher un message d'erreur
        print(f"Erreur de lecture de l'API : {e}")
        return "Erreur de lecture de l'API"

player_list = players.get_active_players()
# player_list = players.get_players() #Décommenter cette ligne et commenter la ligne du dessus pour jouer avec tous les joueurs de la base de données
nombre_de_tours = 10

@app.route('/', methods=['GET', 'POST'])
def home():
    session.clear()  # Efface toutes les données de session
    return render_template('index.html', tour_actuel=0, nombre_de_tours=nombre_de_tours, points=0, player_name=None)

@app.route('/play', methods=['POST'])
def play():
    if 'tour_actuel' not in session:
        session['tour_actuel'] = 0
        session['points'] = 0

    if session['tour_actuel'] < nombre_de_tours:
        session['tour_actuel'] += 1

        current_player = random.choice(player_list)
        player_id = current_player['id']
        university_name = get_university_name(player_id)

        session['current_player_id'] = player_id
        session['current_player_name'] = current_player['full_name']
        session['university_name'] = university_name

        return render_template('play.html', tour_actuel=session['tour_actuel'], nombre_de_tours=nombre_de_tours, points=session['points'], player_name=current_player['full_name'], university_name=university_name)
    else:
        return redirect(url_for('game_over'))

@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_guess = request.form.get('user_guess', '').strip().lower()
    university_name = session.get('university_name', '').lower()

    correct = user_guess == university_name

    if correct:
        session['points'] += 1

    result_dict = {
        'correct': correct,
        'reponse_joueur': user_guess,
        'universite_attendue': session.get('university_name', ''),
    }

    # Efface les informations relatives au tour précédent
    session.pop('current_player_id', None)
    session.pop('current_player_name', None)
    session.pop('university_name', None)

    return render_template('check_answer.html', resultat=result_dict, points=session['points'], nombre_de_tours=nombre_de_tours)



@app.route('/game_over', methods=['GET', 'POST'])
def game_over():
    return render_template('game_over.html', points=session.get('points', 0), nombre_de_tours=nombre_de_tours)


if __name__ == '__main__':
    app.run(debug=True)
