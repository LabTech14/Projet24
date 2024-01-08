#!/usr/bin/env python
# coding: utf-8

# In[21]:


import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
from decimal import Decimal

import plotly.io as pio
pio.renderers.default = "browser"  # Utiliser le rendu dans le navigateur

import warnings
warnings.filterwarnings("ignore")

# Charger le DataFrame INVENTAIRE2
#inventaire2_df = pd.read_excel("consolidated_data.xlsx")


# Chemin du répertoire contenant les fichiers Excel
input_directory = 'C:\\Users\\Administrateur\\Desktop\\code\\input'
fina = pd.read_csv('C:\\Users\\Administrateur\\Desktop\\code\\non.csv')


############################################## exploration et traitements des données #####################################

# Remplacez 'votre_fichier.xlsx' par le nom de votre fichier Excel
excel_file = "Analyse TB2023.xlsx"

# Remplacez 'Feuille1' et 'Feuille3' par les noms des feuilles que vous souhaitez consolider
sheets_to_consolidate = ['AVRIL 23', 'MAI 23', 'JUIN 23', 'JUILLET 23'] 

# Charger les feuilles spécifiées en un dictionnaire de DataFrames
dfs = pd.read_excel(excel_file, sheet_name=sheets_to_consolidate)

# Concaténer les DataFrames en utilisant les noms d'entête de colonnes
consolidated_sheet = pd.concat(dfs, ignore_index=True, sort=False)

# Convertir la colonne "Date " en format de date avec gestion des erreurs
consolidated_sheet["Date "] = pd.to_datetime(consolidated_sheet["Date "], format="%Y-%m-%d %H:%M:%S", errors='coerce')

# Filtrer les lignes où la colonne "Date " est au format de date valide
consolidated_sheet = consolidated_sheet[consolidated_sheet["Date "].notnull()]

# Sélectionner uniquement les colonnes "Date ", "CA" et "ACHATS"
columns_to_keep = ["Date ", "CA", "ACHATS"]
consolidated_sheet = consolidated_sheet[columns_to_keep]

# Enregistrer la feuille consolidée avec les colonnes spécifiques dans un nouveau fichier Excel
consolidated_excel_file = 'feuille_consolid.xlsx'
consolidated_sheet.to_excel(consolidated_excel_file, index=False)


################################################### 2 #############################################################################

# Ouvrir le fichier Excel "Analyse TB2023.xlsx" et charger la feuille "Détail Dépenses"
excel_file = "Analyse TB2023.xlsx"
sheet_name =  "Détail Dépenses"

df = pd.read_excel(excel_file, sheet_name)

# Transformer la colonne "Date " en format de date avec gestion des erreurs
df["Date "] = pd.to_datetime(df["Date "], format="%Y-%m-%d %H:%M:%S", errors='coerce')

# Supprimer les lignes où la colonne "Date " n'est pas au format "date"
df = df.dropna(subset=["Date "])

# Supprimer les colonnes "Unnamed: 25" et "JOURS"
columns_to_drop = ["Unnamed: 25", "JOURS","TOTAL DEPENSES "]
df = df.drop(columns=columns_to_drop)

# Enregistrer les données dans un nouveau fichier Excel "Analyse.xlsx"
new_excel_file = "Analyse.xlsx"

df.to_excel(new_excel_file, index=False)

################################################ 3 ###############################################################################
# Fusionner les DataFrames df et consolidated_sheet sur la colonne "Date "
merged_df = df.merge(consolidated_sheet[["Date ", "CA", "ACHATS"]], on="Date ", how="left")



# Remplacer les valeurs NaN par 0 dans tout le DataFrame
merged_df.fillna(0, inplace=True)


# Enregistrer les données dans un nouveau fichier Excel "Analyse.xlsx"
new_excel_file = "Analyse_Globale.xlsx"

merged_df.to_excel(new_excel_file, index=False)

print(f"Données de la feuille '{sheet_name}' traitées et enregistrées dans '{new_excel_file}'.")


###################################################  4  #######################################################################

# Charger les données de la feuille "RH" depuis le fichier Excel
excel_file = "Analyse TB2023.xlsx"
sheet_name = "RH"
df = pd.read_excel(excel_file, sheet_name)

# Ouvrir un nouveau fichier Excel pour sauvegarder le contenu traité
new_excel_file = "ChargePersonnel.xlsx"
with pd.ExcelWriter(new_excel_file, engine="xlsxwriter") as writer:
    # Enregistrer le DataFrame d'origine dans le nouveau fichier Excel
    df.to_excel(writer, sheet_name="RH", index=False)

# Lire le nouveau fichier Excel pour le traitement ultérieur
df_new = pd.read_excel(new_excel_file, sheet_name="RH")

# Sélectionner uniquement la colonne "Date" et la colonne "ChargePersonnel"
df_filtered = df_new[['Date ', "ChargePersonnel"]]

# Supprimer les lignes vides ou égales à 0
df_filtered = df_filtered.dropna(subset=['Date ', "ChargePersonnel"])
df_filtered = df_filtered[(df_filtered != 0).all(axis=1)]

# Transformer la colonne "Date" au format de date
df_filtered['Date '] = pd.to_datetime(df_filtered['Date '], format='%d/%m/%Y')  # Adapter le format au format réel dans votre fichier

# Enregistrer le DataFrame filtré dans un autre fichier Excel
new_filtered_excel_file = "ChargePersonnel.xlsx"
df_filtered.to_excel(new_filtered_excel_file, index=False)

print(f"Données filtrées enregistrées dans '{new_filtered_excel_file}'.")
#df_filtered

merged = merged_df.merge(df_filtered[["Date ", "ChargePersonnel"]], on="Date ", how="left")

merged.fillna(0, inplace=True)

merged


# Enregistrer le DataFrame filtré dans un autre fichier Excel
new_filtered_excel_file = "DétailsDépenses.xlsx"
merged.to_excel(new_filtered_excel_file, index=False)

print(f"Données consolidées et enregistrées dans '{new_filtered_excel_file}'.")
#df_filtered

#merged


########################################### calcul financier #################################################################


merged_copy = merged.copy()
df0 = merged_copy

########Calculer le total par colonne :#########

# Somme de chaque colonne
total_par_colonne = df0.sum()

# Somme de chaque ligne
total_par_ligne = df0.sum(axis=1)


######Coûts des produits vendus##########

# Liste des colonnes à inclure dans le calcul
colonnes_a_inclure = ["SMOKE", "EAT", "GAZ", "DRINK", "MIAMI 228 ", "PICASSO", "GLACONS"]

# Ajouter une colonne "Coûts des produits vendus"
df0["Coûts des produits vendus"] = df0[colonnes_a_inclure].sum(axis=1)



##################################################

########## Marge brute#######

# Créer la nouvelle colonne "Marge brute"
df0["Marge brute"] = df0["CA"] - df0["Coûts des produits vendus"]

########## Charge operationnel ##########

# Liste des colonnes à inclure dans le calcul
colonnesinclure = ['CACHETS',  'CASH POWER',
         'MARKETING','ADMINISTRATIF',
        'MONNAIE', 
       'CREDIT TEL', 'INTERNET / TV', 'LOYERS',
       'CONSOMMABLES', 'ENTRETIEN ', 'TRANSPORT', 'AUTRE',  'ChargePersonnel']

# Ajouter une colonne "OPEX"
df0["OPEX"] = df0[colonnesinclure].sum(axis=1)

########## Resultat d'exploitation ##########

df0["Resultat d'exploitation"] = df0["Marge brute"] - df0["OPEX"]

########## Resultat avant Impôts ##########

ChargesInterets = 0
df0["Resultat avant Impôts"] = df0["Resultat d'exploitation"] - ChargesInterets

########## Resultat net comptable ##########

Taxes = 0
df0["Resultat net comptable"] = df0["Resultat avant Impôts"] - Taxes

 ########## Tresorerie net d'exploitation ##########


df0["Tresorerie net d'exploitation"] = df0["Resultat net comptable"]

########## Travaux et equipements ##########

# Liste des colonnes à inclure dans le calcul
colonnescal = ['EQUIPEMENTS','TRAVAUX']

# Ajouter une colonne "Coûts des produits vendus"
df0["Travaux et equipements"] = -df0[colonnescal].sum(axis=1)

########## Tresorerie net d'investissement ##########

df0["Tresorerie net d'investissement"] = df0["Travaux et equipements"]

########## Resultat net ##########

df0["Resultat net"] = df0["Tresorerie net d'exploitation"] + df0["Tresorerie net d'investissement"]

########## Working Capital ##########

df0["Working Capital"] = df0["ACHATS"]

########## Trésorerie Fin de Mois ##########

df0["Trésorerie Fin de Mois"] = df0["Working Capital"]

########## Taux marge brute ##########

df0["Taux marge brute"] = (df0["Marge brute"]/df0["CA"])*100


# Liste des colonnes à inclure dans le calcul
col = ['MONNAIE', 
       'CREDIT TEL', 'INTERNET / TV', 'LOYERS',
       'CONSOMMABLES', 'ENTRETIEN ', 'TRANSPORT', 'AUTRE']

# Ajouter une colonne "Autres"
df0["Autres"] = df0[col].sum(axis=1)


# Liste des colonnes à inclure dans le calcul
col1 = [ 'MARKETING', 'ADMINISTRATIF']

# Ajouter une colonne "MARKETINGADMINISTRATIF"
df0["MARKETINGADMINISTRATIF"] = df0[col1].sum(axis=1)


# Liste des colonnes à afficher
#columns_to_display = ['Date ', "Coûts des produits vendus", "Marge brute", "OPEX", "Resultat d'exploitation","Resultat avant Impôts",
#                     "Resultat net comptable","Tresorerie net d'exploitation","Travaux et equipements","Tresorerie net d'investissement",
#                     "Resultat net","Working Capital","Trésorerie Fin de Mois","Taux marge brute"]

# Créer un nouveau DataFrame avec uniquement les colonnes à afficher
#df_subset = df0[columns_to_display]

# Afficher le DataFrame résultat
#df_subset

############################################ TCD #############################################################

# Convertir la colonne 'Date' en type datetime
df0['Date '] = pd.to_datetime(df0['Date '])

# Extraire le mois et l'année à partir de la colonne 'Date'
df0['Mois'] = df0['Date '].dt.to_period('M')

# Liste des colonnes pour le TCD
columns_for_tcd = ['Mois', "CA",'Coûts des produits vendus', 'Marge brute','CACHETS', 'CASH POWER',
                   "MARKETINGADMINISTRATIF",'ChargePersonnel',"Autres",'OPEX', 'Resultat d\'exploitation',
                   'Resultat avant Impôts', 'Resultat net comptable', 'Tresorerie net d\'exploitation',
                   'Travaux et equipements', 'Tresorerie net d\'investissement', 'Resultat net',
                   'Working Capital', 'Trésorerie Fin de Mois', 'Taux marge brute']

# Créer le TCD en groupant par mois
tcd = df0[columns_for_tcd].groupby('Mois').sum()

# Afficher le tableau croisé dynamique
#tcd
# Enregistrer le DataFrame filtré dans un autre fichier Excel
new_filtered_excel_file = "non.csv"
tcd.to_csv(new_filtered_excel_file, index=True)

print(f"Données consolidées et enregistrées dans '{new_filtered_excel_file}'.")


# Liste pour stocker les DataFrames de chaque fichier
data_frames = []

# Parcourir tous les fichiers Excel dans le répertoire
for filename in os.listdir(input_directory):
    if filename.endswith('.xlsx') and not filename.startswith('~$'):
        file_path = os.path.join(input_directory, filename)
        try:
            # Lire le fichier Excel dans un DataFrame
            df = pd.read_excel(file_path)
            # Ajouter le DataFrame à la liste
            data_frames.append(df)
        except PermissionError:
            print(f"Ignoré : {filename} (Fichier verrouillé)")

# Concaténer les DataFrames en un seul DataFrame
consolidated_df = pd.concat(data_frames, ignore_index=True)


inventaire2_df = consolidated_df 

# Renommer la colonne "Famille/Produit" en "Item"
inventaire2_df.rename(columns={"Famille/Produit": "Item"}, inplace=True)

# Charger le DataFrame de correspondance
correspondances_df = pd.read_excel("correspondances.xlsx")

# Créer les nouvelles colonnes "Catégorie" et "Sous-catégorie"
inventaire2_df["Catégorie"] = ""
inventaire2_df["Sous-catégorie"] = ""

# Remplir les colonnes "Catégorie" et "Sous-catégorie" en utilisant la correspondance
for index, row in inventaire2_df.iterrows():
    item = row["Item"]
    matching_row = correspondances_df[correspondances_df["Item"] == item]
    if not matching_row.empty:
        inventaire2_df.at[index, "Catégorie"] = matching_row["Catégorie"].values[0]
        inventaire2_df.at[index, "Sous-catégorie"] = matching_row["Sous-catégorie"].values[0]

# Remplacer les "NaN" dans la colonne "Total HT" par 0
inventaire2_df["Total HT"].fillna(0, inplace=True)

# Réorganiser les colonnes
column_order = ["Catégorie", "Sous-catégorie", "Item","Qté", "Offert","Offert formule","Total Qté","Total TTC","Coût",
                "Total remise","TTC remisé","Total HT","Mois","Années"]
inventaire2_df = inventaire2_df[column_order]

# Supprimer les lignes commençant par "Total..." ou "TOTAL..."
inventaire2_df = inventaire2_df[~inventaire2_df["Item"].str.startswith("Total", na=False)]
inventaire2_df = inventaire2_df[~inventaire2_df["Item"].str.startswith("TOTAL", na=False)]

# Supprimer les lignes ayant au moins trois NaN
inventaire2_df = inventaire2_df.dropna(thresh=inventaire2_df.shape[1] - 3)

# Supprimer les lignes vides
inventaire2_df = inventaire2_df.dropna(how="all")

# Réinitialiser les index
inventaire2_df.reset_index(drop=True, inplace=True)

# Calculer la somme de Total Qté par Sous-Catégorie
sous_cat_sum = inventaire2_df.groupby('Sous-catégorie')['Total Qté'].transform('sum')

# Calculer la colonne "Quantité Absolue"
inventaire2_df['Quantité Absolue'] = inventaire2_df['Total Qté'] / sous_cat_sum*100

# Calculer la colonne "Quantité Relative"
total_sum = inventaire2_df['Total Qté'].sum()

inventaire2_df['Quantité Relative'] = inventaire2_df['Total Qté'] / sous_cat_sum

# Afficher le DataFrame résultant
#inventaire2_df



# Chemin du répertoire où vous voulez enregistrer le fichier Excel
output_directory = 'C:\\Users\\Administrateur\\Desktop\\code\\inputcons'

# Vérifier si le répertoire existe, sinon le créer
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Chemin complet du fichier de sortie
output_path = os.path.join(output_directory, 'BD.xlsx')

# Enregistrer le DataFrame en fichier Excel
inventaire2_df.to_excel(output_path, index=False)



#####################################################SECONDE PARTIE#############################################################

# Chargement des données à partir du fichier Excel
#file_path =  r"C:\Users\Administrateur\Desktop\Dashboardv001\inputcons\BD.xlsx"

df = inventaire2_df    #pd.read_excel(file_path)

# Obtenir la liste des mois uniques dans la colonne 'Mois'
mois_list = df['Mois'].unique()

# Obtenir la liste des années uniques dans la colonne 'Année'
annee_list = df['Années'].unique()

# Obtenir la liste des années uniques dans la colonne 'Année'
categorie_list = df['Catégorie'].unique()

# Obtenir la liste des années uniques dans la colonne 'Année'
sous_categorie_list = df['Sous-catégorie'].unique()

# Fonctions pour générer les visualisations des KPIs

#########    1   ########

def generate_pie_chart_weight_on_revenue(filtered_df):
    df_category_revenue = filtered_df.groupby('Catégorie')['Total HT'].sum().reset_index()
    total_revenue = df_category_revenue['Total HT'].sum()

    df_category_revenue['Poids'] = df_category_revenue['Total HT'] / total_revenue
    df_category_revenue['Valeur Absolue'] = df_category_revenue['Total HT'] * 0.75  # 75% of Total HT

    # Trouver l'indice de la part la plus petite
    min_index = df_category_revenue['Poids'].idxmin()
    explode = [0.1 if i == min_index else 0 for i in range(len(df_category_revenue))]

    fig = go.Figure(go.Pie(
        labels=df_category_revenue['Catégorie'],
        values=df_category_revenue['Poids'],
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Poids : %{percent:.2%}<br>Valeur Absolue : %{customdata} FCFA',
        customdata=df_category_revenue['Valeur Absolue'],
        marker=dict(
            colors=['#FF5733', '#FFC300', '#36D7B7', '#3C40C6', '#27AE60', '#F39C12', '#9B59B6', '#D4AC0D', '#E74C3C', '#3498DB']
        ),
        hole=0.4,
        sort=False,
        pull=explode  # Appliquer la fonction d'explosion
    ))

    fig.update_layout()

    return fig


#########    2    ########
def generate_treemap_item_subcategory(filtered_df):
    df = filtered_df.copy()
    total_relative_quantity = df['Quantité Relative'].sum()
    df['PctRelative'] = df['Quantité Relative'] / total_relative_quantity * 100  # Calcul du pourcentage

    fig = px.treemap(df, path=['Catégorie', 'Sous-catégorie', 'Item'],
                     values='PctRelative',  # Utilisation des pourcentages calculés
                     custom_data=['PctRelative'],  # Stockage des pourcentages dans les données personnalisées
                     color='Sous-catégorie')

    fig.update_layout()

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Poids: %{customdata[0]:.2f}%',  # Format en pourcentage avec 2 décimales
        textinfo='label+percent entry'  # Affiche le label de la catégorie et le pourcentage
    )

    return fig


#########    3    ########

def generate_sunburst_item_category(filtered_df):
    fig = go.Figure()

    # Ajouter une trace de barres pour le CA
    fig.add_trace(go.Bar(x=fina['Mois'], y=fina['CA'], name='Chiffre d\'affaires'))

    # Ajouter une trace de ligne pour le taux de marge brute avec un axe y secondaire
    fig.add_trace(go.Scatter(x=fina['Mois'], y=fina['Taux marge brute'], mode='lines', yaxis='y2', name='Taux de marge brute'))

    # Personnalisation de l'axe y2 (axe de droite)
    fig.update_layout(yaxis2=dict(anchor='x', overlaying='y', side='right'))

    # Personnalisation du titre et des axes
    fig.update_layout(title_text='',
                      title_x=0.5, xaxis_title='Mois', yaxis_title='Chiffre d\'affaires', yaxis2_title='Taux de marge brute')

    return fig
    
#Chiffre d\'affaires et Taux de Marge Brute par mois
    
#########    4   ########
def generate_sunburst_subcategory_within_category(filtered_df):
    
    fina_grouped = fina.groupby('Mois').sum().reset_index()
    fig = px.line(fina_grouped, x='Mois', y=['CACHETS', 'CASH POWER', 'MARKETINGADMINISTRATIF', 'ChargePersonnel', 'Autres'],
                  title='')#Évolution des Charges Opérationnelles

    #fig.update_xaxes(categoryorder='category ascending')  # Ajoute cette ligne pour corriger l'ordre des mois
   
    # Personnalisation du style du titre
    fig.update_layout(title_text='',
                      title_x=0.5, xaxis_title='Mois', yaxis_title='Chiffre d\'affaires')
    #fig.update_layout( )
    return fig


#########    5    ########
def generate_bar_weight_on_revenue(filtered_df):
    fina_grouped = fina.groupby('Mois').sum().reset_index()
    fig = px.pie(fina_grouped, values='CA', names='Mois', title='')#Répartition du CA sur les Mois

     # Personnalisation du style du titre
    fig.update_layout(title_text='',
                      title_x=0.5, xaxis_title='Mois', yaxis_title='Chiffre d\'affaires')
    #fig.update_layout()
    
    return fig


#########   6   ########
def generate_box_category_revenue(filtered_df):
    
    fig = px.line(fina, x='Mois', y=['Coûts des produits vendus', 'Marge brute'],
                  labels={'value': 'Montant', 'variable': 'Catégorie'},
                  title='')#Coûts des produits vendus et Marge brute
    return fig


#########    7    ########
def generate_box_total_revenue(filtered_df):
    fina_grouped = fina.groupby('Mois').sum().reset_index()
    fig = px.bar(fina_grouped, x='Mois', y=['Tresorerie net d\'exploitation', 'Tresorerie net d\'investissement'],
                  title='')#Évolution des Flux de Trésorerie

    fig.update_layout(
        barmode='relative',  # Afficher les barres relatives aux valeurs positives et négatives
        bargap=0.1,  # Espacement entre les groupes de barres
        xaxis=dict(title='Mois'),
        yaxis=dict(title='Montant'),
        legend_title='Catégorie'
    )

    return fig


# Création du tableau de bord
app = dash.Dash(__name__)

# Ajustement de la taille des graphiques Sunburst
sunburst_height = 200

app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='https://adminlte.io/themes/v3/plugins/fontawesome-free/css/all.min.css'),    
    html.Link(
        rel='stylesheet',
        href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'),
    html.Link(
        rel='stylesheet',
        href='https://adminlte.io/themes/v3/dist/css/adminlte.min.css?v=3.2.0'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Dashboard d'analyse des données", className="m-0")
                ], className="col-sm-8"),
                html.Div([
                    html.Ol([
                        html.Li(id='current-time', className="breadcrumb-item active")
                    ], className="breadcrumb float-sm-right")
                ], className="col-sm-4")
            ], className="row mb-2"),
            html.Div([
                html.Div([
                    dcc.Dropdown(id='year-dropdown', options=[{'label': str(annee), 'value': annee} for annee in annee_list],
                                value=None, placeholder="Sélectionnez les années", multi=True)
                ], className='col-md-3'),

                html.Div([
                    dcc.Dropdown(id='month-dropdown', options=[{'label': mois, 'value': mois} for mois in mois_list],
                                value=None, placeholder="Sélectionnez les mois", multi=True)
                ], className='col-md-3'),
                    
                html.Div([
                    dcc.Dropdown(id='categorie-dropdown', options=[{'label': str(categorie), 'value': categorie} for categorie in categorie_list],
                                value=None, placeholder="Sélectionnez les catégories", multi=True)
                ], className='col-md-3'),

                html.Div([
                    dcc.Dropdown(id='sous-categorie-dropdown', options=[{'label': str(sous_categorie), 'value': sous_categorie} for sous_categorie in sous_categorie_list],
                                value=None, placeholder="Sélectionnez les sous catégorie", multi=True)
                ], className='col-md-3'),

            ], className='row mb-3'),

            html.Div(id='revenue-summary')

        ], className="container-fluid")
    ], className="content-header mb-4 pb-1", style={'background-color': '#c2c2c3'} ),

    html.Section([
        html.Div([
            html.Div([
                html.Div(id='visualizations-container'),
            ], className="container-fluid")
        ], className="row"),
    ], className="content"),

    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),  # Rafraîchissement toutes les secondes
], className='content-wrapper', style={'margin-left': '0px', 'min-height': '100vh'})

@app.callback(
    Output('sous-categorie-dropdown', 'options'),
    Input('categorie-dropdown', 'value')
)
def update_sous_categorie_dropdown(selected_categories):
    if selected_categories is None:
        return []
    
    filtered_df = df[df['Catégorie'].isin(selected_categories)]
    sous_categorie_options = [{'label': sous_categorie, 'value': sous_categorie} for sous_categorie in filtered_df['Sous-catégorie'].unique()]
    return sous_categorie_options

@app.callback(
    Output('revenue-summary', 'children'),
    Input('month-dropdown', 'value'),
    Input('year-dropdown', 'value'),
    Input('categorie-dropdown', 'value'),
    Input('sous-categorie-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_revenue_summary(selected_months, selected_years, selected_categories, selected_sous_categories, n_intervals):
    if selected_months is None or selected_years is None:
        return html.Div()

    filtered_df = df[df['Années'].isin(selected_years)]
    filtered_df = filtered_df[df['Mois'].isin(selected_months)]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Catégorie'].isin(selected_categories)]
    
    if selected_sous_categories:
        filtered_df = filtered_df[filtered_df['Sous-catégorie'].isin(selected_sous_categories)]

    if filtered_df.empty:
        return html.Div("")

    total_revenue = filtered_df['Total HT'].sum()
    formatted_total_revenue = '{:,.2f}'.format(total_revenue).replace(',', ' ').replace('.', ',') + " FCFA"

    selected_month_names = ', '.join(map(str, selected_months))
    selected_year_names = ', '.join(map(str, selected_years))
    
    if selected_categories:
        selected_categorie_names = ', '.join(selected_categories)
        if selected_sous_categories:
            selected_sous_categorie_names = ', '.join(selected_sous_categories)
            formatted_message = f"Le chiffre d'affaires de(s) sous-catégorie(s) {selected_sous_categorie_names} de(s) catégorie(s) {selected_categorie_names} du mois de {selected_month_names} de l'année {selected_year_names}"
        else:
            formatted_message = f"Le chiffre d'affaires de(s) catégorie(s) {selected_categorie_names} du mois de {selected_month_names} de l'année {selected_year_names}"
    else:
        formatted_message = f"Le chiffre d'affaires du mois de {selected_month_names} de l'année {selected_year_names}"

    return html.Div([
        html.Div([
            html.Div([
                html.H3(f"{formatted_total_revenue}"),
                html.P(f"{formatted_message}", className="mb-0"),
            ], className="inner p-2"),
        ], className="small-box bg-info col-md-12 col-12")
    ], className="")


@app.callback(
    Output('current-time', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_current_time(n_intervals):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Heure actuelle : {current_time}"

@app.callback(
    Output('visualizations-container', 'children'),
    Input('month-dropdown', 'value'),
    Input('year-dropdown', 'value'),
    Input('categorie-dropdown', 'value'),
    Input('sous-categorie-dropdown', 'value')
)
def update_visualizations(selected_months, selected_years, selected_categories, selected_sous_categories):
    if selected_months is None or selected_years is None:
        return html.Div()

    filtered_df = df[df['Années'].isin(selected_years)]
    filtered_df = filtered_df[df['Mois'].isin(selected_months)]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Catégorie'].isin(selected_categories)]
    
    if selected_sous_categories:
        filtered_df = filtered_df[filtered_df['Sous-catégorie'].isin(selected_sous_categories)]

    if filtered_df.empty:
        return html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H1("Aucune donnée disponible pour les sélections faites."),
                    ], className="inner p-2"),
                ])
            ], className="small-box bg-danger")
        ], className="col-lg-12 col-12")
    
    # Utilisation des différentes fonctions de génération de graphiques
    fig_pie_chart_weight_on_revenue = generate_pie_chart_weight_on_revenue(filtered_df)
    fig_treemap_item_subcategory = generate_treemap_item_subcategory(filtered_df)
    fig_sunburst_item_category = generate_sunburst_item_category(filtered_df)
    fig_sunburst_subcategory_within_category = generate_sunburst_subcategory_within_category(filtered_df)
    fig_bar_weight_on_revenue = generate_bar_weight_on_revenue(filtered_df)
    fig_box_category_revenue = generate_box_category_revenue(filtered_df)
    fig_box_total_revenue = generate_box_total_revenue(filtered_df)

    return html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Poids de chaque catégorie sur le chiffre d'affaires global", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_pie_chart_weight_on_revenue.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Poids de chaque Item dans sa sous-catégorie", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_treemap_item_subcategory.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Chiffre d\'affaires et Taux de Marge Brute par mois", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_sunburst_item_category.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Évolution des Charges Opérationnelles", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_sunburst_subcategory_within_category.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Répartition du CA sur les Mois", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_bar_weight_on_revenue.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Coûts des produits vendus et Marge brute", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_box_category_revenue.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-6"),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Évolution des Flux de Trésorerie", className="card-title")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.Div(dcc.Graph(figure=fig_box_total_revenue.update_layout(margin=dict(t=0, b=0, l=0, r=0)))),
                        ], className="card-body pad table-responsive p-0")
                    ], className="card-body")
                ], className="card card-primary card-outline")
            ], className="col-md-12")

        ], className="row")

if __name__ == '__main__':
    app.run_server(debug=True, port=5517)


# In[ ]:




