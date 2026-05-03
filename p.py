from flask import Flask , render_template
#flask:the Flask package we instelled
#Flask:the main class used to create a web application

app=Flask(__name__)
#app: web application varible
#Flask():create a Flask application
#__name__: tell Flask where the app is located

@app.route("/")
#@:decorator in Python
#app.route:defines a webpage
#"/":the hompage URL
def home():
    return render_template("coffee.html")

if __name__=="__main__":
    app.run(debug=True)
#app.run(): start the web server
#debug=True: shows erros and auto-reloads   
#example - if we change code, Flask reloads automatically