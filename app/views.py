from flask import render_template, flash, redirect, Response
from app import app
from app import music

navigation = ['MiriamPi', 'EyeCam', 'WhiteNoise', 'Music']
template_data = {'navigation': navigation}


@app.route('/')
@app.route('/index')
@app.route('/<activeTab>')
def landing(activeTab='MiriamPi'):
    template_data['activeTab'] = activeTab
    if activeTab == 'Music':
        music.connect()
        playlistnames = [row['playlist'] for row in music.listplaylists()]
        music.close()
        template_data['playlistnames'] = playlistnames

    return render_template(activeTab + '.html', **template_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/Tab/<nav>')
def navTab(nav):
    return redirect("/" + nav)


@app.route('/Play/<listName>')
def startPlay(listName):
    music.PlaylistPlay(listName)
    return Response('OK', mimetype='text/plain'), 204
