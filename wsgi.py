from app import create_app

app = create_app()

application = app

app.run(debug=True)