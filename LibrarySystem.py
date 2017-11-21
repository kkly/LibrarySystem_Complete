from flask import Flask, render_template, request, flash, redirect, url_for, session
from wtforms import Form, StringField, TextAreaField, RadioField, SelectField, validators, PasswordField
from Magazine import Magazine
from Book import Book
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('cred/library-system-a3843-firebase-adminsdk-av5pi-b432c9b613.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://library-system-a3843.firebaseio.com/'

})

root = db.reference()
app = Flask(__name__)


@app.route('/')
def default():
    return render_template('home.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/viewpublications')
def viewpublications():
    publications = root.child('publications').get()
    list = [] #create a list to store all the publication objects
    print(publications)
    for pubid in publications:

        eachpublication = publications[pubid]

        if eachpublication['type'] == 'smag':
            magazine = Magazine(eachpublication['title'], eachpublication['publisher'], eachpublication['status'], eachpublication['created_by'], eachpublication['category'], eachpublication['type'], eachpublication['frequency'])
            magazine.set_pubid(pubid)
            print(magazine.get_pubid())
            list.append(magazine)
        else:
            book = Book(eachpublication['title'], eachpublication['publisher'], eachpublication['status'], eachpublication['created_by'], eachpublication['category'], eachpublication['type'], eachpublication['synopsis'], eachpublication['author'], eachpublication['isbn'])
            book.set_pubid(pubid)
            list.append(book)

    return render_template('view_all_publications.html', publications = list)

class RequiredIf(object):

    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.items():
            if name not in form._fields:
                validators.Optional()(field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data:
                    validators.DataRequired().__call__(form, field)
                else:
                    validators.Optional().__call__(form, field)


@app.route('/delete_publication/<string:id>', methods=['POST'])
def delete_publication(id):
    mag_db = root.child('publications/' + id)
    mag_db.delete()
    flash('Article Deleted', 'success')

    return redirect(url_for('viewpublications'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        if username == 'admin' and password == 'P@ssw0rd': #harcoded username and password
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('viewpublications'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('Login.html', form=form)


    return render_template('Login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class PublicationForm(Form):
    title = StringField('Title', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    pubtype = RadioField('Type Of Publication', choices=[('sbook', 'Book'), ('smag', 'Magazine')], default='sbook')
    category = SelectField('Caterory', [validators.DataRequired()],
                           choices=[('', 'Select'), ('FANTASY', 'Fantasy'), ('FASHION', 'Fashion'),
                                    ('THRILLER', 'Thriller'), ('CRIME', 'Crime'), ('BUSINESS', 'Business')],
                           default='')
    publisher = StringField('Publisher', [
        validators.Length(min=1, max=100),
        validators.DataRequired()])
    status = SelectField('Status', [validators.DataRequired()],
                         choices=[('', 'Select'), ('P', 'Pending'), ('A', 'Available For Borrowing'),
                                  ('R', 'Only For Reference')], default='')
    isbn = StringField('ISBN No', [validators.Length(min=1, max=100), RequiredIf(pubtype='sbook')])
    author = StringField('Author', [
        validators.Length(min=1, max=100),
        RequiredIf(pubtype='sbook')])
    synopsis = TextAreaField('Synopsis', [
        RequiredIf(pubtype='sbook')])
    frequency = RadioField('Frequency', [RequiredIf(pubtype='smag')],
                           choices=[('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')])


@app.route('/newpublication', methods=['GET', 'POST'])
def new():
    form = PublicationForm(request.form)
    if request.method == 'POST' and form.validate():
        if  form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001" # hardcoded value

            mag = Magazine(title, publisher, status, created_by, category, type, frequency)


            #create the magazine object
            mag_db = root.child('publications')
            mag_db.push({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Inserted Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn)
            mag_db = root.child('publications')
            mag_db.push({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })

            flash('Book Inserted Sucessfully.', 'success')

        return redirect(url_for('viewpublications'))


    return render_template('create_publication.html', form=form)

@app.route('/update/<string:id>/', methods=['GET', 'POST'])
def update_publication(id):
    form = PublicationForm(request.form)

    if request.method == 'POST' and form.validate():
        if form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value

            mag = Magazine(title, publisher, status, created_by, category, type, frequency)

            # create the magazine object
            mag_db = root.child('publications/' + id)
            mag_db.set({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Updated Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn)
            mag_db = root.child('publications/' + id)
            mag_db.set({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })

            flash('Book Updated Successfully.', 'success')

        return redirect(url_for('viewpublications'))

    else:
        url = 'publications/' + id
        eachpub = root.child(url).get()

        if eachpub['type'] == 'smag':
            magazine = Magazine(eachpub['title'], eachpub['publisher'], eachpub['status'],
                                eachpub['created_by'], eachpub['category'], eachpub['type'],
                                eachpub['frequency'])

            magazine.set_pubid(id)
            form.title.data = magazine.get_title()
            form.pubtype.data = magazine.get_type()
            form.category.data = magazine.get_category()
            form.publisher.data =  magazine.get_publisher()
            form.status.data =  magazine.get_status()
            form.frequency.data = magazine.get_frequency()
        elif eachpub['type'] == 'sbook':
            book = Book(eachpub['title'], eachpub['publisher'], eachpub['status'],
                        eachpub['created_by'], eachpub['category'], eachpub['type'],
                        eachpub['synopsis'], eachpub['author'], eachpub['isbn'])
            book.set_pubid(id)
            form.title.data = book.get_title()
            form.pubtype.data = book.get_type()
            form.category.data = book.get_category()
            form.publisher.data = book.get_publisher()
            form.status.data = book.get_status()
            form.synopsis.data = book.get_synopsis()
            form.author.data = book.get_author()
            form.isbn.data = book.get_isbnno()

        return render_template('update_publication.html', form=form)

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()
