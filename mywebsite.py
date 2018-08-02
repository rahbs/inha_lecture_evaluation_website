from flask import Flask, render_template, url_for, redirect, request, session
import sqlite3
import os
from flask import Flask, flash, request, redirect, url_for


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# http://flask.pocoo.org/
# https://media.amazonwebservices.com/architecturecenter/AWS_ac_ra_web_01.pdf
# Insomnia

# 메인화면
# 회원 기능 - 로그인
@app.route('/', methods=['GET', 'POST'])
def index():
    u_name = None
    login_error = None

    #회원 수 가져오기
    con=sqlite3.connect('mywebsite')
    cur=con.cursor()
    cur.execute('SELECT max(u_id) FROM tbuser;')
    userNum=cur.fetchall()
    app.logger.debug('index() - %s' % str(userNum))
    con.close()

    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_name=session['u_name']
        return render_template('index.html', u_name=u_name, login_error=login_error,userNum=userNum)
    else:                               # 로그인 되어 있지 않다면
        if request.method == 'POST':    # 회원 등록 정보가 넘어오는 경우
            email = request.form['email']
            password = request.form['password']
            params = (email, password)
            app.logger.debug('index() - %s' % str(params))

            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
                SELECT u_id, u_name FROM tbuser WHERE email=? AND password=? AND use_flag='Y';
                ''', params)
            rows=cur.fetchall()
            con.close()
            app.logger.debug('index() - %s' % str(rows))
            if len(rows) == 1:  # 로그인 정상
                # 세션을 생성하고 다시 리다이렉션
                session['u_id'] = rows[0][0]
                session['u_name'] = rows[0][1]
                return redirect(url_for('index'))
            else:               # 로그인 오류
                login_error='로그인에 실패하였습니다.'
                return render_template('index.html',  userNum=userNum, u_name=u_name, login_error=login_error,rows=rows)
        else:                           # 기본 접속 (미 로그인 & GET)
            return render_template('index.html', userNum=userNum,u_name=u_name, login_error=login_error)

# 회원 기능 - 회원_등록 
@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        # 입력받은 email, u_name, password, gender, birth_year 를 데이터베이스에 저장한다. 오류 처리는 생략 한다. 
        email = request.form['email']
        u_name = request.form['u_name']
        password = request.form['password']
        params = (email, u_name, password)
        app.logger.debug('user_signup() - %s' % str(params))
        
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
            INSERT INTO tbuser (email, u_name, password) 
            VALUES (?, ?, ?);
            ''', params)
        con.commit()
        con.close()
        return redirect(url_for('index'))
    return render_template('user_signup.html')

# 회원 기능 - 로그아웃
@app.route('/user/logout')
def user_logout():
    logout()
    return redirect(url_for('index'))

#로그아웃 수행
def logout():
    session.pop('u_id', None)
    session.pop('u_name', None)

#로그인 여부
def isLogin():
    return 'u_id' in session    

# 회원 기능 - 회원_정보보기
@app.route('/user/')
def user_profile():
    user_info=None
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_id = session['u_id']
        params = (u_id,)
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
            SELECT u_id, email, password, u_name, add_dt, upd_dt FROM tbuser WHERE u_id=?;
            ''', params)
        rows=cur.fetchall()
        app.logger.debug('index() - %s' % str(rows))
        con.close()
        user_info = rows[0]
        if len(rows) == 1:  # 로그인 정상
            return render_template('user_profile.html', user_info=user_info)
        else:
            return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

# 회원 기능 - 회원_수정
@app.route('/user/update', methods=['GET', 'POST'])
def user_update():
    user_info=None
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        if request.method != 'POST':            # 회원 정보를 제공함
            u_id = session['u_id']
            params = (u_id,)
            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
                SELECT u_id, email, password, u_name, add_dt, upd_dt FROM tbuser WHERE u_id=?;
                ''', params)
            rows=cur.fetchall()
            app.logger.debug('user_update() - rows: %s' % str(rows))
            con.close()
            user_info = rows[0]
            if len(rows) == 1:  # 로그인 정상
                return render_template('user_update.html', user_info=user_info)
            else:
                return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
        else:                           # 회원 정보를 업데이트 함 (POST)
            # 입력받은 email, u_name, password, gender, birth_year 를 데이터베이스에 저장한다. 오류 처리는 생략 한다. 
            u_id = session['u_id']
            email = request.form['email']
            u_name = request.form['u_name']
            password = request.form['password']
            params = (email, u_name, password, u_id)
            app.logger.debug('user_update() - params: %s' % str(params))
            
            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
                UPDATE tbuser SET email=?, u_name=?, password=?, upd_dt=DATETIME('now', 'localtime') WHERE u_id=?
                ''', params)
            con.commit()
            con.close()
            return redirect(url_for('user_profile'))
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

# 회원 기능 - 회원_탈퇴
@app.route('/user/leave')
def user_leave():
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_id = session['u_id']
        params = (u_id,)
        app.logger.debug('user_leave() - params: %s' % str(params))
        
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
            UPDATE tbuser SET u_name='탈퇴한사용자', use_flag='N', upd_dt=DATETIME('now', 'localtime') WHERE u_id=?
            ''', params)
        con.commit()
        con.close()
        logout()        # 로그아웃
        return redirect(url_for('index'))
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯


#강의평가 글 목록
@app.route('/lecture_evaluation/', methods=["GET", "POST"])
def lecture_evaluation():
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_name=session['u_name']
        pageNum = None
        pageNumList = None 

        pageNum = request.args.get('page')  # http://127.0.0.1:5000/lecture_evaluation/?page=1
        if pageNum is None:
            pageNum = '1'
        pageNum = int(pageNum)
        if pageNum < 1:
            pageNum = 1
        app.logger.debug('lecture_evaluation() - pageNum: %d' % pageNum)
        keyword = None
        keyword = request.args.get('keyword')

        startNum, endNum = 0, 0
        if pageNum >= 3:
            startNum = pageNum - 2
        else:
            startNum = 1
        endNum = startNum + 4
        pageNumList = list(range(startNum, endNum+1))
        app.logger.debug('lecture_evaluation() - pageNumList: %s' % str(pageNumList))

        if request.method == 'POST':           
            # 입력받은 data를 데이터베이스에 저장한다. 
            u_id = session['u_id']  
            lectureName = request.form['lectureName']
            professorName = request.form['professorName']  
            lectureYear = request.form['lectureYear']
            semesterDivide = request.form['semesterDivide']
            lectureDivide = request.form['lectureDivide']   
            evaluationContent = request.form['evaluationContent']
            totalScore = request.form['totalScore']
            gradeScore = request.form['gradeScore']
            comfortableScore = request.form['comfortableScore']
            lectureScore = request.form['lectureScore']
            likeCount = 0
            
            if (lectureName == None) | (professorName == None) | (lectureYear == 0) | (semesterDivide == None) | (lectureDivide == None) | (evaluationContent == None) | (totalScore == None) | (gradeScore == None) | (comfortableScore == None) | (lectureScore == None) | (evaluationContent =='') :
                app.logger.debug('데이터 베이스 오류')

            else:
                params = (u_id, lectureName, professorName,lectureYear,semesterDivide,lectureDivide,evaluationContent,totalScore,gradeScore,comfortableScore,lectureScore,likeCount)            
                app.logger.debug('lecture_evaluation() - %s' % str(params))                
                con=sqlite3.connect('mywebsite')
                cur=con.cursor()
                cur.execute('''
                    INSERT INTO tbevaluation (u_id, lectureName, 
                    professorName,lectureYear,semesterDivide,lectureDivide, evaluationContent,
                    totalScore,gradeScore,comfortableScore,lectureScore,likeCount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    ''', params)
                con.commit()
                con.close()  
              
            return redirect(url_for('lecture_evaluation'))                     
        else:
        
            return render_template('lecture_evaluation.html', u_name=u_name, pageNum=pageNum, pageNumList=pageNumList, keyword=keyword)
               
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

#강의 평가 글목록
@app.route('/evaluation_list/')
def evaluation_list():
     # 조회할 페이지 번호를 가져옴 get query string
    pageNum = request.args.get('page')  # http://127.0.0.1:5000/evaluation/?page=1
    if pageNum is None:
        pageNum = '1'
    pageNum = int(pageNum)
    if pageNum < 1:
        pageNum = 1
    app.logger.debug('evaluation_list() - pageNum: %d' % pageNum)

    keyword = None
    keyword = request.args.get('keyword')
    isEdit = False
    isEdit = request.args.get('isEdit')

    # DB로 부터 tbboard 게시판 목록을 가져옴
    offset = (pageNum - 1) * 6

    con=sqlite3.connect('mywebsite')
    cur=con.cursor()

    u_id = session['u_id']
    isMine = []

    if keyword==None:
        params = (offset,)
        cur.execute('''
            SELECT e_id, lectureName, professorName, lectureYear, 
            semesterDivide, lectureDivide, evaluationcontent,
            totalScore, gradeScore, comfortableScore, lectureScore, likeCount, u.u_id
            FROM tbevaluation e INNER JOIN tbuser u
            ON e.u_id = u.u_id
            WHERE e.use_flag='Y' ORDER BY e_id DESC LIMIT 6 OFFSET ?;
            ''', params)
 
    else:
        params = (keyword, keyword, keyword, offset)
        cur.execute('''
            SELECT e_id, lectureName, professorName, lectureYear, 
            semesterDivide, lectureDivide, evaluationcontent,
            totalScore, gradeScore, comfortableScore, lectureScore, likeCount, u.u_id
            FROM tbevaluation e INNER JOIN tbuser u
            ON e.u_id = u.u_id
            WHERE e.use_flag='Y' 
            AND (e.lectureName like '%'||?||'%' 
            OR e.professorName like '%'||?||'%' 
            OR e.evaluationContent like '%'||?||'%')
            ORDER BY e_id DESC LIMIT 6 OFFSET ?;
            ''', params)
    rows=cur.fetchall()
    app.logger.debug(u_id)

    #자기가 쓴 글인지 아닌지 판단한다.
    for i in range(0,len(rows)):
        if (u_id==rows[i][12]):
            app.logger.debug(rows[i][12])
            isMine.append(True)
        else:
            app.logger.debug(rows[i][12])
            isMine.append(False)
    app.logger.debug(str(isMine))
    app.logger.debug('evaluation_list() - %s' % str(rows))
    con.close()

    return render_template('evaluation_list.html',board_rows=rows, isMine=isMine, isEdit=isEdit)

# 강의평가 기능 - 게시판_글삭제
@app.route('/lecture_evaluation/<int:e_id>/delete')
def evaluation_delete(e_id):
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_id = session['u_id']
        params = (e_id, u_id)
        app.logger.debug('evaluation_delete() - params: %s' % str(params))
        
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
            UPDATE tbevaluation SET use_flag='N', upd_dt=DATETIME('now', 'localtime') WHERE e_id=? AND u_id=?;
            ''', params)
        con.commit()
        con.close()
        return redirect(url_for('lecture_evaluation'))
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

#강의평가 기능 - 좋아요(추천)
# def evaluation_like():
#     u_id = session['u_id']
#     params = (u_id,)
#     con=sqlite3.connect('mywebsite')
#     cur=con.cursor()
#     cur.execute('''
#         UPDATE tbevaluation SET likeCount = likeCount + 1 WHERE e_id = ?
#         ''', params)
#     con.commit()
#     con.close()

# def like():
#     u_id = session['u_id']
#     u_name=session['u_name']
#     userIp = socket.gethostbyname(socket.getfqdn())
#     params = (u_id,u_name,userIp)
#     con=sqlite3.connect('mywebsite')
#     cur=con.cursor()
#     cur.execute('''
#        INSERT INTO tblike VALUES (?, ?, ?)
#         ''', params)
#     con.commit()
#     con.close()

#족보     
@app.route('/jockbo', methods=["GET", "POST"])
def jockbo():
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_name=session['u_name']
        pageNum = None
        pageNumList = None 

        pageNum = request.args.get('page')  
        if pageNum is None:
            pageNum = '1'
        pageNum = int(pageNum)
        if pageNum < 1:
            pageNum = 1
        app.logger.debug('jockbo() - pageNum: %d' % pageNum)
        keyword = None
        keyword = request.args.get('keyword')

        startNum, endNum = 0, 0
        if pageNum >= 3:
            startNum = pageNum - 2
        else:
            startNum = 1
        endNum = startNum + 4
        pageNumList = list(range(startNum, endNum+1))
        app.logger.debug('jockbo() - pageNumList: %s' % str(pageNumList))

        return render_template('jockbo.html', u_name=u_name, pageNum=pageNum, pageNumList=pageNumList, keyword=keyword)               
    # 로그인 되어 있지 않다면
    else:                              
        return render_template('user_notlogin.html')

# 족보 게시판 기능 - 게시판_글목록
@app.route('/jockbo_list/')
def jockbo_list():
    # 조회할 페이지 번호를 가져옴 get query string
    pageNum = request.args.get('page')  # http://127.0.0.1:5000/board/?page=1
    if pageNum is None:
        pageNum = '1'
    pageNum = int(pageNum)
    if pageNum < 1:
        pageNum = 1
    app.logger.debug('jockbo_list() - pageNum: %d' % pageNum)

    keyword = None
    keyword = request.args.get('keyword')   # 검색 키워드를 가져옴
    app.logger.debug('jockbo_list() - keyword: %s' % keyword)

    # DB로 부터 tbboard 게시판 목록을 가져옴
    offset = (pageNum - 1) * 10
    
    con=sqlite3.connect('mywebsite')
    cur=con.cursor()
    app.logger.debug('1')
    if keyword==None:
        params = (offset,)
        cur.execute('''
            SELECT b_id, u_name, title, b.add_dt
            FROM tbboard b INNER JOIN tbuser u
            ON b.u_id = u.u_id
            WHERE b.use_flag='Y' ORDER BY b_id DESC LIMIT 10 OFFSET ?;
            ''', params)
    else:
        params = (keyword, keyword, offset)
        cur.execute('''
            SELECT b_id, u_name, title, b.add_dt
            FROM tbboard b INNER JOIN tbuser u
            ON b.u_id = u.u_id
            WHERE b.use_flag='Y' AND (b.title like '%'||?||'%' OR b.content like '%'||?||'%') ORDER BY b_id DESC LIMIT 10 OFFSET ?;
            ''', params)
    rows=cur.fetchall()
    app.logger.debug('2board() - %s' % str(rows))
    con.close()
    return render_template('jockbo_list.html', board_rows=rows)

# 족보 게시판 기능 - 게시판_글등록
@app.route('/board/post', methods=["GET", "POST"])
def board_post():
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        if request.method == 'POST':            
            # 입력받은 title, content 를 데이터베이스에 저장한다. 오류 처리는 생략 한다. 
            u_id = session['u_id']
            title = request.form['title']
            content = request.form['content']
            params = (u_id, title, content)
            app.logger.debug('board_post() - %s' % str(params))
            
            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
                INSERT INTO tbboard (u_id, title, content) 
                VALUES (?, ?, ?);
                ''', params)
            con.commit()
            con.close()            
            return redirect(url_for('jockbo'))
        else:
            u_name=session['u_name']
            return render_template('board_post.html', u_name=u_name)
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

# 게시판 기능 - 게시판_글수정
@app.route('/board/<int:board_id>/update', methods=["GET", "POST"])
def board_update(board_id):
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        if request.method == 'GET':            # 회원 정보를 제공함 (GET)
            u_id = session['u_id']
            params = (board_id,)
            app.logger.debug('board_update() - %s' % str(params))
            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
            SELECT b_id, b.u_id, u_name, title, content, b.add_dt, b.upd_dt
            FROM tbboard b INNER JOIN tbuser u
            ON b.u_id = u.u_id
            WHERE b.use_flag='Y' AND b_id=?;
                ''', params)
            rows=cur.fetchall()
            app.logger.debug('board_update() - %s' % str(rows))
            con.close()
            board_view = rows[0]
            if len(rows) == 1:  # 로그인 정상
                u_name=session['u_name']
                if u_id==board_view[1]: # 현재 세션의 유저와 가져온 게시글의 유저가 같은 경우
                    return render_template('board_update.html', board_view=board_view, u_id=u_id, u_name=u_name)
                else:
                    return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
            else:
                return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
        else:                           # 회원 정보를 업데이트 함 (POST)
            # 입력받은 b_id, title, content 를 데이터베이스에 저장한다. 오류 처리는 생략 한다. 
            u_id = session['u_id']
            b_id = int(request.form['b_id'])
            title = request.form['title']            
            content = request.form['content']
            params = (title, content, b_id, u_id)
            app.logger.debug('board_update() - params: %s' % str(params))

            if b_id!=board_id:  # URL의 게시글 번호와 POST로 넘겨 받은 게시글의 번호가 불일치 하는 경우
                return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
            
            con=sqlite3.connect('mywebsite')
            cur=con.cursor()
            cur.execute('''
                UPDATE tbboard SET title=?, content=?, upd_dt=DATETIME('now', 'localtime') WHERE b_id=? AND u_id=?;
                ''', params)
            con.commit()
            con.close()
            return redirect(url_for('board_view', board_id=board_id))
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

# 게시판 기능 - 게시판_글삭제
@app.route('/board/<int:board_id>/delete')
def board_delete(board_id):
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_id = session['u_id']
        params = (board_id, u_id)
        app.logger.debug('board_delete() - params: %s' % str(params))
        
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
            UPDATE tbboard SET use_flag='N', upd_dt=DATETIME('now', 'localtime') WHERE b_id=? AND u_id=?;
            ''', params)
        con.commit()
        con.close()
        return redirect(url_for('jockbo'))
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

# 게시판 기능 - 게시판_글보기
@app.route('/board/<int:board_id>')
def board_view(board_id):
    if isLogin(): #'u_id' in session:   # 로그인 되어 있다면
        u_id = session['u_id']
        params = (board_id,)
        app.logger.debug('board_view() - %s' % str(params))
        con=sqlite3.connect('mywebsite')
        cur=con.cursor()
        cur.execute('''
        SELECT b_id, b.u_id, u_name, title, content, b.add_dt, b.upd_dt
        FROM tbboard b INNER JOIN tbuser u
        ON b.u_id = u.u_id
        WHERE b.use_flag='Y' AND b_id=?;
            ''', params)
        rows=cur.fetchall()
        app.logger.debug('board_view() - %s' % str(rows))
        con.close()
        board_view = rows[0]
        if len(rows) == 1:  # 로그인 정상
            u_name=session['u_name']
            return render_template('board_view.html', board_view=board_view, u_id=u_id, u_name=u_name)
        else:
            return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯
    else:                               # 로그인 되어 있지 않다면
        return render_template('user_notlogin.html')   # 잘못된 페이지 접근이라고 보여주고 이동해도 될듯

if __name__ == '__main__':
    # createTables()
    app.run(host='0.0.0.0', port=5000, debug=True)

