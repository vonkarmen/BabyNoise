from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)
navigation = ['MiriamPi', 'EyeCam', 'WhiteNoise', 'Music']
activeTab = navigation[0]


@app.route("/")
def landing():
    return render_template(activeTab + '.html', activeTab=activeTab, navigation=navigation)


@app.route("/Tab/<nav>")
def navTab(nav):
    activeTab = nav
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
