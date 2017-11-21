from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)
navigation = ['MiriamPi', 'EyeCam', 'WhiteNoise', 'Music']


@app.route("/")
@app.route("/<activeTab>")
def landing(activeTab='MiriamPi'):
    return render_template(activeTab + '.html', activeTab=activeTab, navigation=navigation)


@app.route("/Tab/<nav>")
def navTab(nav):
    return redirect("/"+nav)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
