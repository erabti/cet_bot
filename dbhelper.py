import sqlite3

class DBHelper:
    def __init__(self, dbname="peopleinfo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS people (ID INTEGER,regid INTEGER ,name TEXT,grp INTEGER,admin INTEGER,pw TEXT,PRIMARY KEY(regid))"
        stmt2= "CREATE TABLE IF NOT EXISTS givenhomework(uni INTEGER,ID INTEGER, fileid TEXT, grp INTEGER, subject TEXT)"
        stmt3= "CREATE TABLE IF NOT EXISTS neededhomework(uni INTEGER primary key autoincrement,ID INTEGER, grp INTEGER, subject TEXT, info TEXT,fileid TEXT)"
        stmt4= "CREATE TABLE IF NOT EXISTS schedule(grp INTEGER,sat TEXT,sun TEXT,mon TEXT,tue TEXT,wed TEXT,thur TEXT,fri TEXt)"
        stmt5= "CREATE TABLE IF NOT EXISTS teachers(ID INTEGER,name TEXT,subject TEXT,groups TEXT,schedule TEXT)"
        stmt6= "CREATE TABLE IF NOT EXISTS scores (ID INTEGER, regid INTEGER, circuit INTEGER, digital INTEGER,maths INTEGER,physics INTEGER,english INTEGER)"
        stmt7= "CREATE TABLE IF NOT EXISTS polling (ID INTEGER,grp INTEGER, name TEXT,photo TEXT,votes INTEGER)"
        stmt8= "CREATE TABLE IF NOT EXISTS peoplelist (grp INTEGER,regid INTEGER,name TEXT)"
        stmt9= "CREATE TABLE IF NOT EXISTS attendance (ID INTEGER,name TEXT,date TEXT,time TEXT,room INTEGER, subject TEXT)"
        stmt10="CREATE TABLE IF NOT EXISTS curriculum (year INTEGER,subject TEXT,category TEXT,title TEXT,link TEXT)"
        self.conn.execute(stmt)
        self.conn.execute(stmt2)
        self.conn.execute(stmt3)
        self.conn.execute(stmt4)
        self.conn.execute(stmt5)
        self.conn.execute(stmt6)
        self.conn.execute(stmt7)
        self.conn.execute(stmt8)
        self.conn.execute(stmt9)
        self.conn.execute(stmt10)
        self.conn.commit()
    def add_curriculum(self,year,subject,category,title,link):
        stmt = "INSERT INTO curriculum (year,subject,category,title,link) VALUES(?,?,?,?,?)"
        args = (year,subject,category,title,link)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def get_curriculum(self,year,subject,category):
        stmt = "SELECT title,link from curriculum WHERE year=? and subject=? and category=?"
        args = (year,subject,category)
        x=self.conn.execute(stmt,args).fetchall()
        return x
    def does_any_curriculum_exist(self,year,subject):
        stmt = "SELECT title,link from curriculum WHERE year=? and subject=?"
        args = (year, subject)
        x = self.conn.execute(stmt, args).fetchone()
        if not x:
            return False
        else:
            return True
    def register_attendance(self,ID,name,date,time,room,subject):
        stmt = "INSERT INTO attendance (ID,name,date,time,room,subject) VALUES(?,?,?,?,?,?)"
        args = (ID, name, date,time,room,subject)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def get_attendance(self,ID,date,subject):
        stmt = "SELECT ID,name,time,room from attendance where ID=? and date=? and subject=?"
        args=(ID,date,subject)
        x=self.conn.execute(stmt, args).fetchone()
        return x
    def get_attendance_group(self,grp,date,subject):
        ids = self.get_all_group_ID(grp)
        result = {}
        for i in ids:
            a = self.get_attendance(i,date,subject)
            if a:
                result[a[0]]=[a[1],a[2],a[3]]
        return result
    def get_firstname(self,ID):
        name = self.get_info('name',ID)
        if name:
            return name.split()[0]
        else:
            return ""
    def is_registed(self,regid):
        stmt="SELECT COUNT(*) regid FROM peoplelist WHERE regid=?"
        args=(regid,)
        x=self.conn.execute(stmt, args)
        data=x.fetchone()[0]
        if data==0:
            return False
        else:
            return True
    def register_a_student_in_list(self,grp,regid,name):
        stmt = "INSERT INTO peoplelist (grp,regid,name) VALUES(?,?,?)"
        args = (grp,regid,name)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def add_polling_member(self,ID,grp,name,photo,votes=0):
        stmt = "INSERT INTO polling (ID,grp,name,photo,votes) VALUES(?,?,?,?,?)"
        args = (ID,grp, name,photo,votes)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def get_candidates(self,grp):
        stmt = "SELECT name,photo from polling where grp=?"
        args=(grp,)
        x=self.conn.execute(stmt,args).fetchall()
        return x
    def get_votes(self,name,grp):
        stmt = "SELECT votes from polling where name=? and grp=?"
        args=(name,grp)
        x=self.conn.execute(stmt, args).fetchone()
        if not x:
            return []
        if not x[0]:
            return []
        return x[0]
    def add_vote(self,name,grp):
        current_votes = self.get_votes(name,grp)
        votes = int(current_votes)+1
        stmt = "UPDATE polling SET votes=? WHERE name=? and grp=?"
        args = (votes, name,grp)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def get_voting_result(self,grp):
        stmt = "SELECT ID,name,photo,votes from polling where grp=?"
        args = (grp,)
        x = self.conn.execute(stmt, args).fetchall()
        return x
    def remove_all_candidate(self,grp):
        stmt = "DELETE FROM polling where grp=?"
        args = (grp,)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def add_homework_one(self,ID,grp,subject,info,fileid=None):
        stmt="INSERT INTO neededhomework (ID,grp,subject,info,fileid) VALUES(?,?,?,?,?)"
        args = (ID,grp,subject,info,fileid)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def add_homework_group(self,grp,subject,info,fileid=None):
        group_ID=self.get_all_group_ID(grp)
        for ID in group_ID:
            self.add_homework_one(ID,grp,subject,info,fileid)
    def remove_needed_homework(self,grp,subject):
        stmt = "DELETE FROM neededhomework where grp=? and subject=?"
        args = (grp,subject)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def remove_givenhomework(self,grp,subject):
        stmt = "DELETE FROM givenhomework where grp=? and subject=?"
        args = (grp,subject)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def submit_homework(self,uni,ID,fileid,grp,subject):
        stmt="INSERT INTO givenhomework (uni,ID,fileid,grp,subject) VALUES(?,?,?,?,?)"
        args=(uni,ID,fileid,grp,subject)
        self.conn.execute(stmt,args)
        self.conn.commit()
        self.remove_needed_homework(uni)
    def get_givenhomework_ID(self,subject):
        stmt="SELECT ID FROM givenhomework WHERE subject=?"
        args=(subject,)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return list(set(j))
    def get_givenhomework_uni(self,subject,grp):
        stmt="SELECT uni FROM givenhomework WHERE subject=? and grp=?"
        args=(subject,grp)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return list(set(j))
    def review_homework(self,uni,grp):
        stmt="SELECT uni,fileid,ID FROM givenhomework where uni=? and grp=?"
        args=(uni,grp)
        x=self.conn.execute(stmt,args).fetchall()
        return x
    def get_needed_homework(self,ID):
        stmt="SELECT subject FROM neededhomework where ID=?"
        args=(ID,)
        x=self.conn.execute(stmt, args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def get_all_groups_in_schedule(self):
        stmt="SELECT grp FROM schedule"
        x=self.conn.execute(stmt).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return list(set(j))
    def get_needed_homework_info(self,ID,subject):
        stmt="SELECT uni,info,fileid FROM neededhomework WHERE ID=? and subject=?"
        args=(ID,subject)
        x=self.conn.execute(stmt, args).fetchall()
        return x
    def get_given_homework_groups(self,subject):
        stmt="SELECT grp FROM givenhomework where subject=?"
        args=(subject,)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def get_given_homework_group(self,grp):
        stmt="SELECT subject FROM givenhomework where grp=?"
        args=(grp,)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def get_given_homewrok_teacher(self, subject,grp):
        stmt="SELECT subject FROM givenhomework where grp=? and subject=?"
        args=(grp,subject)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def remove_needed_homework(self,uni):
        stmt="DELETE FROM neededhomework WHERE uni=?"
        args=(uni,)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def remove_needed_homework_by_id(self,ID):
        stmt="DELETE FROM neededhomework WHERE ID=?"
        args=(ID,)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def remove_needed_homework_group(self,grp,subject):
        stmt="DELETE FROM neededhomework WHERE grp=? and subject=?"
        args=(grp,subject)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def remove_given_homework(self,ID,uni):
        stmt="DELETE FROM givenhomework WHERE ID=? and uni=?"
        args=(ID,uni)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def get_all_group_ID(self,grp):
        stmt="SELECT ID FROM people WHERE grp=?"
        args=(grp,)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j

    def add_person(self,ID,regid, name=None, grp=None,admin=0,pw=None):
        stmt = "INSERT OR REPLACE INTO people (ID,regid,name,grp,admin,pw) VALUES (?,?,?,?,?,?)"
        stmt2 = "INSERT OR REPLACE INTO scores (ID,regid,circuit,digital,maths,physics,english) VALUES(?,?,?,?,?,?,?)"
        args = (ID, regid, name, grp,admin,pw)
        args2= (ID, regid,0,0,0,0,0)
        self.conn.execute(stmt, args)
        self.conn.execute(stmt2,args2)
        self.conn.commit()

    def add_teacher(self,ID,name,subject,groups):
            stmt="INSERT INTO teachers (ID,name,subject,groups) VALUES(?,?,?,?)"
            args=(ID,name,subject,groups)
            self.conn.execute(stmt,args)
            self.conn.commit()

    def update_info(self,info,val,ID=None, regid=None,table='people'):
            if ID:
                stmt="UPDATE {t} SET {info1}=? WHERE ID=?".format(info1=info,t=table)
                args=(val, ID)
            elif regid:
                stmt="UPDATE {t} SET {info1}=? WHERE regid=?".format(info1=info,t=table)
                args=(val, regid)
            self.conn.execute(stmt, args)
            self.conn.commit()
    def user_exists(self, ID):
        stmt="SELECT COUNT(*) ID FROM people WHERE ID=?"
        args=(ID,)
        x=self.conn.execute(stmt, args)
        data=x.fetchone()[0]
        if data==0:
            return False
        else:
            return True
    def isteacher(self, ID):
        stmt="SELECT COUNT(*) ID FROM teachers WHERE ID=?"
        args=(ID,)
        x=self.conn.execute(stmt, args)
        data=x.fetchone()[0]
        if data==0:
            return False
        else:
            return True
    def update_teacher_ID(self,ID,name):
        stmt = "UPDATE teachers SET ID=? WHERE name=?"
        args = (ID,name)
        self.conn.execute(stmt, args)
        self.conn.commit()
    def isteachernameexist(self,name):
        stmt="SELECT COUNT(*) name FROM teachers WHERE name=?"
        args=(name,)
        x=self.conn.execute(stmt, args)
        data=x.fetchone()[0]
        if data==0:
            return False
        else:
            return True
    def get_info(self,info,ID=None,regid=None,table="people"):
        if regid:
            stmt="SELECT {info_} FROM {t} where regid=?".format(info_=info,t=table)
            args=(regid,)
        elif ID:
            stmt="SELECT {info_} FROM {t} where ID=?".format(info_=info,t=table)
            args=(ID,)
        else:
            return
        x=self.conn.execute(stmt, args).fetchone()
        if x==None:
            return
        if len(x)==1:
            return x[0]
        return x
    def get_id_from_file(self,fileid):
        stmt="SELECT ID FROM givenhomework WHERE fileid=?"
        args=(fileid,)
        x=self.conn.execute(stmt,args).fetchall()
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def get_admin_ID(self,grp):
        stmt="SELECT ID FROM people WHERE grp=? and admin=1"
        args=(grp,)
        x=self.conn.execute(stmt, args).fetchone()
        return x
    def get_day_schedule(self,grp,day):
        stmt="SELECT {d} FROM schedule WHERE grp=?".format(d=day)
        args=(grp,)
        x=self.conn.execute(stmt,args).fetchone()
        if not x:
            return
        if not x[0]:
            return ''
        x=x[0]
        return eval(x)
    def get_all_students_id(self):
        stmt="SELECT ID FROM people"
        x=self.conn.execute(stmt)
        j=[]
        for i in x:
            j.append(i[0])
        return j
    def get_all_teachers_id(self):
        stmt = "SELECT ID FROM teachers"
        x = self.conn.execute(stmt)
        j = []
        for i in x:
            j.append(i[0])
        return j
    def get_availiabe_groups(self):
        stmt = "SELECT grp FROM people"
        x = self.conn.execute(stmt)
        j = []
        for i in x:
            j.append(i[0])
        j = list(set(j))
        j.sort()
        return j
