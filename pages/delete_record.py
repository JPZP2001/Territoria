import dash
from dash import Dash, html,Input,Output,dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/delete_record")


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
                                dbc.NavItem(dbc.Button("Cerrar sesión", color="link", id="sign_out_button", n_clicks=0, className='sign_out_btn')),
                            ], className="ms-auto", navbar=True),
                            id="navbar-collapse", navbar=True,
                        )
                        
                    ]), color="#FFFFFF", dark=False,
    ),

    

   
    #Title
    html.H1("Confirmar eliminación",className="title"),

    #Main div
    html.Div([
    
            html.Div(id="table")
             
    ],className="delete_record_div"),

     
   
 
], fluid=False)

   
