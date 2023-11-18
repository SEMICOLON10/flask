from flask import Flask, render_template, redirect, url_for, request ,flash,session,make_response
import sqlite3

app = Flask(__name__)

app.secret_key = 'super secret key'  # تأكد من تعيين مفتاح سري لجلسة Flask



global_name = None
global_statue = None

@app.before_request
def before_request():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    global global_name, global_statue
    with app.app_context():
        if request.method == 'POST':
            connection = sqlite3.connect('basedata.db')
            cursor = connection.cursor()
            global_name = request.form['name']
            password = request.form['password']
            global_statue = request.form['statue']

            query = "SELECT name, password, statue FROM base WHERE name = ? AND password = ? AND statue = ?"
            cursor.execute(query, (global_name, password, global_statue))
            results = cursor.fetchall()

            if len(results) == 0:
                flash('خطأ في اسم المستخدم أو كلمة المرور', 'error')
                return redirect(url_for('login'))

            elif global_statue == 'Client':
                session['username'] = global_name
                session['statue'] = global_statue
                response = make_response(redirect(url_for('page_home')))
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                return response

            else:
                session['username'] = global_name
                session['statue'] = global_statue
                response = make_response(redirect(url_for('home')))
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                return response

        return render_template('login.html')


@app.route('/logout')
def logout():
    # قم بتنظيف الجلسة وتوجيه المستخدم إلى صفحة تسجيل الدخول أو أي صفحة أخرى
    session.pop('username', None)
    session.pop('statue', None)
    return redirect(url_for('login'))

@app.route('/page_home', methods=['GET', 'POST'])
def page_home():
    global global_name, global_statue

    con = sqlite3.connect('basedata.db')
    cur = con.cursor()
    data_from_db = [row[0] for row in cur.fetchall()]  # قم بتخزين البيانات المسترجعة في متغير مختلف
    cur.execute("SELECT data FROM base WHERE name= ?", (global_name,))
    value = cur.fetchone()
    if value is not None:
        value = value[0]  # استخراج القيمة الوحيدة من ال tuple

    cur.execute("SELECT drive FROM base WHERE name= ?", (global_name,))
    data_link = cur.fetchone()
    if data_link is not None:
        data_link = data_link[0]  # استخراج القيمة الوحيدة من ال tuple

    con.commit()
    con.close()

    if data_link is not None:
        return render_template('client.html', data=data_from_db, data_link=data_link, value=value, name=session['username'].capitalize(), s=session['statue'].capitalize())
    else:
        flash("عذرًا، لا يوجد رابط", "info")
        return render_template('client.html', data=data_from_db, value=value, name=session['username'].capitalize(), s=session['statue'].capitalize())



@app.route('/read',methods=['GET', 'POST'])
def read():
    global global_name, global_statue

    if request.method == 'POST':
            
            list = request.form['list']

            con = sqlite3.connect('basedata.db')
            cur = con.cursor()

            cur.execute('SELECT name FROM base WHERE statue="Client"')  # التأكد من صحة الاستعلام

            data_from_db = [row[0] for row in cur.fetchall()]  # قم بتخزين البيانات المسترجعة في متغير مختلف
            cur.execute("SELECT data FROM base WHERE name= ?", (list,))
            value = cur.fetchone()
            if value is not None:
                value = value[0]  # استخراج القيمة الوحيدة من ال tuple
           
            
            con.commit()
            con.close()
            return render_template('index.html', data=data_from_db, value=value,name=session['username'].capitalize(), s=session['statue'].capitalize())
    return render_template('index.html')




@app.route('/sub', methods=['GET', 'POST'])
def sub():
    global global_name, global_statue
    if request.method == 'POST':
        input_data = request.form['data']  
        name = request.form['list']

        con = sqlite3.connect('basedata.db')
        cur = con.cursor()

        cur.execute('SELECT name FROM base WHERE statue="Client"')  
        data_from_db = [row[0] for row in cur.fetchall()]  

        cur.execute("SELECT data FROM base WHERE name= ?", (name,))
        value = cur.fetchone()
        if value is not None:
            value = value[0]  

        cur.execute("UPDATE base SET data = ? WHERE name = ?", (input_data, name))  
        con.commit()

        if cur.rowcount > 0:
             flash('•  تم الحفظ بنجاح', 'success')
        else:
            flash('لا', 'error')  

        con.close()
        return render_template('index.html', data=data_from_db, value=value,name=session['username'].capitalize(), s=session['statue'].capitalize())

    return render_template('index.html')

  
@app.route('/Cooming_Soon')
def Soon():
    global global_name, global_statue
    return render_template('soon.html')  
        






@app.route('/add')
def add():
    return render_template('add_cus.html', name=session['username'].capitalize(), s=session['statue'].capitalize())
    
    
@app.route('/home')
def home():
    global global_name, global_statue

    if 'username' in session and 'statue' in session:
        # Connect to the SQLite database
        
        connection= sqlite3.connect('basedata.db')
        cursor=connection.cursor()

        # Execute an SQL query to retrieve data
        cursor.execute('SELECT name FROM base where statue="Client"')
        

        # Fetch all the results
        data = [row[0] for row in cursor.fetchall()]

        # Close the database connection
        connection.close()
        return render_template("index.html", name=session['username'].capitalize(), s=session['statue'].capitalize(), data=data)  

    else:
        return redirect(url_for('login')) 
  





@app.route('/edit', methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            global global_name, global_statue
            
            name = request.form['name1']
            password = request.form['password']
            statue = request.form['statues']
            drive = request.form['drive']
            email = request.form['email']
            con = sqlite3.connect('basedata.db')
            cur = con.cursor()

            cur.execute("INSERT INTO base (name, password, statue, drive, email) VALUES (?, ?, ?, ?, ?)", (name, password, statue, drive, email))
            con.commit()

            flash('• تم الحفظ بنجاح')
        except sqlite3.Error as error:
            if str(error) == "UNIQUE constraint failed: base.name":
                flash('• الاسم موجود ','error')
            else:
                flash('• حدث خطأ أثناء إدراج البيانات : {}'.format(error), 'error')
        

        finally:
            if con:
                con.close()

        return render_template('add_cus.html',name=session['username'].capitalize(), s=session['statue'].capitalize())
    return render_template('add_cus.html', name=session['username'].capitalize(), s=session['statue'].capitalize())



    
        
    
                              
               
         



        
            

            
            
        


        
    
