import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Charger les données depuis le fichier Excel
df = pd.read_excel("question.xlsx")

# Initialisation de l'application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Styles pour les boutons
button_style = {'fontSize': '18px', 'color': 'white'}

# Variables de suivi de l'état
current_question_index = 0  # Index de la question actuelle
responses = {}  # Dictionnaire pour stocker les réponses
confirmation_modal = None  # Modal de confirmation
show_radar = False  # Indicateur pour afficher le radar

# Layout de l'application
app.layout = html.Div([
    # Titre de l'application
    html.H1(children='Évaluation des Compétences Digitales', style={'textAlign': 'center'}),
    
    # Bouton suivant
    html.Button('Suivant', id='button-suivant', style={'backgroundColor': 'red', **button_style}),
    
    # Bouton précédent
    html.Button('Précédent', id='button-precedent', style={'backgroundColor': 'green', **button_style}),
    
    # Bouton de mise à jour du graphique radar
    html.Button('Mettre à jour le radar', id='button-update-radar', style={'backgroundColor': 'purple', **button_style}),
    
    # Espace pour afficher les questions
    dcc.Markdown(id='question-display', style={'marginTop': '20px'}),
    
    # Espace pour afficher les réponses
    dcc.Textarea(id='response-display', placeholder='Entrez votre réponse ici...',
                 style={'width': '100%', 'height': '100px', 'marginTop': '20px'}),
    
    # Bouton de validation du test
    html.Button('Valider le test', id='button-valider', style={'backgroundColor': 'blue', **button_style}),
    
    # Modal de confirmation
    dbc.Modal(
        [
            dbc.ModalHeader("Confirmation"),
            dbc.ModalBody("Êtes-vous sûr de vouloir valider le test ? Une fois validé, vous ne pourrez plus modifier vos réponses."),
            dbc.ModalFooter(
                [
                    dbc.Button("Annuler", id="close", className="ml-auto"),
                    dbc.Button("Valider", id="confirm", className="ml-auto"),
                ]
            ),
        ],
        id="modal",
    ),
    
    # Espace pour afficher le graphique radar
    dcc.Graph(id='radar-plot', style={'marginTop': '20px'}),
])

# Fonction pour mettre à jour les questions et les réponses
@app.callback([Output('question-display', 'children'),
               Output('response-display', 'value')],
              Input('button-suivant', 'n_clicks'),
              Input('button-precedent', 'n_clicks'))
def update_question(n_clicks_suivant, n_clicks_precedent):
    global current_question_index
    global responses

    # Vérifier quel bouton a été cliqué
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    # Logique pour afficher la question suivante ou précédente
    if triggered_id == 'button-suivant':
        current_question_index += 1
    elif triggered_id == 'button-precedent':
        current_question_index -= 1

    # Assurez-vous que l'index de la question reste dans les limites
    current_question_index = max(0, min(current_question_index, len(df) - 1))

    # Obtenir la question actuelle
    question_text = df.iloc[current_question_index]['Niveau Faible']

    # Obtenir la réponse précédente
    response_text = responses.get(current_question_index, "")

    return question_text, response_text

# Fonction pour ouvrir la modal de confirmation
@app.callback(
    Output("modal", "is_open"),
    Input("button-valider", "n_clicks"),
    Input("close", "n_clicks"),
    Input("confirm", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Fonction pour mettre à jour le graphique radar et afficher ou masquer le radar
@app.callback([Output('radar-plot', 'figure'),
               Output('radar-plot', 'style')],
              Input('button-update-radar', 'n_clicks'),
              Input('confirm', 'n_clicks'))
def update_radar(n_clicks_update_radar, n_clicks_valider):
    global responses
    global show_radar

    # Si l'utilisateur clique sur "Mettre à jour le radar"
    if n_clicks_update_radar is not None:
        show_radar = not show_radar  # Inverser l'état d'affichage du radar

    # Si l'utilisateur clique sur "Valider le test"
    if n_clicks_valider is not None:
        show_radar = True  # Afficher le radar final

    # Créer une liste des réponses de l'utilisateur dans l'ordre des domaines de compétences
    user_responses = [responses.get(i, 0) for i in range(len(df))]

    # Créer un graphique radar dynamique avec les domaines de compétences comme labels
    fig = px.line_polar(
        r=user_responses,
        theta=df['Domaines'],
        line_close=True,
        title='Niveau de Compétence Digitale (Mise à jour)',
    )

    # Personnaliser les labels de l'axe theta
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
    )

    style = {'display': 'none'} if not show_radar else {'marginTop': '20px'}

    return fig, style

if __name__ == '__main__':
    app.run_server(debug=True)
