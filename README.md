<!DOCTYPE html>
<html>

    <head>
        <title>Index Page</title>
    </head>
    <body>
        <h1>Welcome to the Index Page</h1>
            <img src="{{ url_for('static', filename='Rookie\'s Ledger.png') }}" alt="Welcome to Rookie's Ledger!">
            <a href="/register">Register</a>
    </body>
</html>
