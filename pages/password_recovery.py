import dash
from dash import Dash, html,Input,Output,dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/password_recovery")

#Password recovery form inputs
email_input = html.Div(
    [
        dbc.Label("Email", html_for="recoveryEmail", style={'fontWeight':700}),
        dbc.Input(type="email",
                  id="recoveryEmail", 
                  placeholder="Ingresa tu correo electrónico",
                  style={'height': 63,'margin':'auto'}),
    ],
    className="mb-3",
)

# Page layout
layout = dbc.Container([

    #Heading
    dbc.Navbar(
        dbc.Container([

            html.A(
                dbc.Row(
                    dbc.Col(html.Img(src="assets/georregias_logo.jpeg", height="30px")),
                    align="center", className="g-0"
                ), href="/"
            ),

            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),


            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Iniciar sesión", href="/login")),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse", navbar=True,
            )
            
        ]), color="#FFFFFF", dark=False,
    ),


    #Title
    html.H1("Restablecer contraseña", style={'textAlign': 'center', 'fontSize':40, 'marginBottom':40, 'marginTop':40}),

    #Legend
    html.P("Ingresa en el formulario tu correo de administrador."
                "Te enviaremos un correo con un link para restablecer la contraseña.", style={'textAlign': 'center', 'width':'45%', 'marginLeft':'auto', 'marginRight':'auto', 'marginTop':20, 'fontSize':18}),


    #Div for password recovery form
    html.Div([
    
            dbc.Form([email_input]),

             html.Div(
                [
                    dbc.Button(
                        "Enviar email", id="submitBtn", className="me-2", style={'backgroundColor': '#8D65C5', 'border': '1px solid #8D65C5', 'fontWeight': 600, 'fontSize':16, 'height': 50, 'margin-top':30,}, 
                    ),
                ], style={'textAlign':'center'}
             )
             
    ] ,style={'margin':'auto', 'width':'55%'} )

], fluid=False)

   
