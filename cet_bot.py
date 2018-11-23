from datetime import datetime
import schedule
import pytz
import telebot
from telebot import types
from weather import Weather, Unit
from dbhelper import DBHelper
import re
import time

tz = pytz.timezone('Africa/Tripoli')
db = DBHelper()
db.setup()
TOKEN = "786130091:AAFNZjbMIq0UuGx4HOBMT4uhTETLTmTMAKs"
#dummy
#TOKEN = "786138936:AAH6SPX9QyhcS_hvlyQ_K-58Rt1P2gEh-Bo"
bot = telebot.TeleBot(TOKEN)
MID = "677339387"
PASSWORD = '314159'
# main_menu
homework_btn = "سلم واجبي 📝"
info_btn = "شني عندي ℹ️"
weather_btn = 'شن الجو؟ ⛅'
checkin_btn = "سجل حضوري 🙋‍♂️"
study_btn = "اقرالي حرفين 📖"
settings_btn = "إعدادات ⚙️"
admin_btn = "قائمة المشرف 😎"
# subjects
subjects_en = {'circuit': 'كهربية 🔋', 'digital': "رقمية 👨‍💻", 'maths': "رياضة ➕➗", 'physics': "فيزياء 💡",
               'english': "انجليزي 🇦🇨"}
# settings_menu
settings_change_name_btn = "غير اسمي 🔤"
settings_change_group_btn = 'غير مجموعة 🔢'
get_scores_btn = "نقاطي ⭐"
get_feedback = "ارسل ملاحظات او شكر للمبرمج 👨‍💻"
# info menu
info_timetable_btn = 'جدول المحاضرات 📅'
info_exams_table = "مواعيد الإمتحانات 📚"
info_tomorrow_btn = 'محاضرات غدوا ⏭️'
info_today_btn = 'محاضرات اليوم ▶️'
info_hw = "شن عندي واجبات؟ 📝"

person_type_student_btn = "طالب👨🏽‍🎓"
person_type_teacher_btn = "استاذ👨🏻‍🏫"

back_btn = "↩️"
right_btn = "✔️"
wrong_btn = "❌"


def get_dictkey(dic, val):
    try:
        x = list(dic.keys())[list(dic.values()).index(val)]
        return x
    except Exception as e:
        print(e)

def user_not_exist(message):
    ID = message.chat.id
    if not db.user_exists(ID) and not db.isteacher(ID):
        send_welcome(message)
        return True
    return False

def show_menu(message, *arg, text="اختر واحد من الخيارات: ⬅️"):
    markup = types.ReplyKeyboardMarkup()
    markup.add(*arg)
    bot.send_message(message.from_user.id, text, reply_markup=markup)

def show_main_menu(message):
    ID = message.from_user.id
    text = "🌟القائمة الرئيسية🌟"
    if db.isteacher(ID):
        show_menu(message, t_absent, t_hw, t_review, t_summary, t_message,t_get_attendance,t_attendance, t_schedule,weather_btn, text=text)
    elif db.get_info('admin', ID) == 1:
        show_menu(message, info_btn, homework_btn,weather_btn,study_btn, admin_btn,checkin_btn,settings_btn, text=text)
    else:
        show_menu(message, info_btn, homework_btn,weather_btn,study_btn,checkin_btn,settings_btn, text=text)


def show_hw_menu(message):
    ID = message.from_user.id
    subjects = list(set(db.get_needed_homework(ID)))
    if len(subjects) == 0:
        return
    markup = types.ReplyKeyboardMarkup()
    for subject in subjects:
        markup.add(subjects_en[subject])
    markup.add(back_btn)
    bot.send_message(ID, 'اختر مادة', reply_markup=markup)


def show_info_menu(message):
    show_menu(message, info_timetable_btn, info_tomorrow_btn, info_today_btn,info_exams_table,info_hw,
              back_btn)


def show_settings_menu(message):
    if user_not_exist(message):
        return
    show_menu(message, get_feedback,get_scores_btn, back_btn)

@bot.message_handler(commands=['dev'])
def send_dev_info(message):
    ID = message.chat.id
    users = len(db.get_all_students_id())
    text="server time: "+str(datetime.now(tz))
    text+="\nyour ID: "+str(ID)
    text+="\nnumber of total students: "+users

    if db.isteacher(ID):
        groups = eval(db.get_info('groups',ID,table='teachers'))
        for grp in groups:
            text += "\nnumber of students in group "+str(grp)+":"+len(db.get_all_group_ID(grp))
    else:
        grp = db.get_info('grp',ID)
        text += "\nnumber of student in group "+str(grp)+":"+len(db.get_all_group_ID(grp))

    bot.send_message(ID,text)
    send_welcome(message)
@bot.message_handler(regexp=back_btn)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    ID = message.from_user.id
    if not db.user_exists(ID) and not db.isteacher(ID):
        bot.send_message(ID,
                         "السلام عليكم😀👋, مرحبا بيك انا بوت الكلية 🤖, انا حنحاول اني نساعدك في كل شي تسحتقه في قرايتك📚, ننبهك كان عندك واجب📝, نستلمه منك📭, ونصلحهولك☑️!, حننبهك لو غاب الأستاذ🏃 او لو كان فيه ظرف في الكلية😟, حنبعتلك شن خديت بعد ماتروح الحوش من الكلية باش تراجعه كملخص, ونقدر نوريك مراجع تقرا منها وتابع بيها💻. بإختصار انا حنحاول انني نكون مساعد ذكي شاطر ونخليك شاطر معاي😉!",
                         reply_markup=types.ReplyKeyboardRemove(selective=False))
        bot.send_message(ID, "نبي ناخد منك معلومات بسيطة باش نسجلك عندي🏁")
        show_menu(message, person_type_student_btn, person_type_teacher_btn, text="اول حاجة انت طالب او استاذ مادة؟🤔")
        bot.register_next_step_handler(message, process_person_type)

        return
    show_main_menu(message)
    bot.register_next_step_handler(message, main_menu_handler)


def process_person_type(message):
    ID = message.from_user.id
    if message.text == person_type_student_btn:
        bot.send_message(ID, "شن هو رقم قيدك؟ #️⃣", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_regid)
    elif message.text == person_type_teacher_btn:
        bot.send_message(ID, "شن هو الرقم السري؟ 🔑", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, verify_teacher_password)


def verify_teacher_password(message):
    ID = message.from_user.id
    password = message.text
    if password == PASSWORD:
        markup = types.ReplyKeyboardMarkup()
        markup.add(*list(subjects_en.values()))
        bot.send_message(ID, "شني هي المادة يلي تعطي فاها؟🤔", reply_markup=markup)
        bot.register_next_step_handler(message, process_registering_teacher)
    else:
        bot.send_message(ID, "رقم سري غلط 🤐")
        send_welcome(message)


def process_registering_teacher(message):
    ID = message.from_user.id
    subject = get_dictkey(subjects_en, message.text)
    bot.send_message(ID, "شن اسمك؟", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_teacher_name, [subject, ])


def get_teacher_name(message, data):
    if len(data) == 1:
        subject = data[0]
        added = []
        name = message.text
        name = re.sub("أ|إ|آ",'ا',name)
        name = name.replace("ى","ي")
        name = name.replace("ذ","د")

    else:
        subject = data[0]
        added = data[1]
        name = data[2]
    ID = message.from_user.id
    if db.isteachernameexist(name):
        tname = name
        fname = tname.split()[0]
        db.update_teacher_ID(ID,tname)
        bot.send_message(ID,"تمام أستاذ {n} تم تسجيلك!".format(n=fname))
        send_welcome(message)
        return
    markup = types.ReplyKeyboardMarkup(row_width=3)
    if not added:
        added = []
    groups = []
    for i in range(1, 12):
        if i in added:
            continue
        groups.append(str(i))
    markup.add(*groups)

    markup.add('تم')
    bot.send_message(ID, "اختار المجموعات يلي تعطي فاها؟", reply_markup=markup)
    bot.register_next_step_handler(message, get_teacher_group, [subject, added, name])


def get_teacher_group(message, data):
    ID = message.from_user.id
    subject = data[0]
    added = data[1]
    name = data[2]
    num = message.text
    if num == "تم" and len(added) == 0:
        bot.send_message(ID, "ما إخترتش اي مجموعة!")
        get_teacher_name(message, [subject, added, name])
    elif num == "تم" and len(added) != 0:
        db.add_teacher(ID, name, subject, str(added))
        bot.send_message(ID,"تمام")
        send_welcome(message)
        return
    if num.isdigit():
        added.append(int(num))
    get_teacher_name(message, [subject, added, name])

@bot.message_handler(regexp=homework_btn)
def manage_homework_input(message):
    main_menu_handler(message)

# processes:
def main_menu_handler(message=None):
    ID = message.from_user.id
    if user_not_exist(message):
        return
    if db.isteacher(ID):
        teacher_menu_handler(message)
        return
    text = message.text
    if text == homework_btn:
        subjects = list(set(db.get_needed_homework(ID)))
        if len(subjects) == 0:
            bot.send_message(ID, "ماعندكش واجبات فرهد على روحك 😉")
            return
        show_hw_menu(message)
        bot.register_next_step_handler(message, homework_menu_handler)
    elif text == info_btn:
        handle_info_command(message)
    elif text == admin_btn:
        handle_admin_menu(message)
    elif text == weather_btn:
        send_today_weather(message)
    elif text == settings_btn:
        show_settings_menu(message)
        bot.register_next_step_handler(message,settings_menu)
    elif text == checkin_btn:
        process_checkin(message)
    elif text == study_btn:
        process_study_menu(message)
    else:
        handle_not_known(message)


def process_study_menu(message):
    ID = message.chat.id
    markup = types.ReplyKeyboardMarkup()
    markup.add(*list(subjects_en.values()))
    markup.add(back_btn)
    bot.send_message(ID,"اختار مادة: ⬅️",reply_markup=markup)
    bot.register_next_step_handler(message, get_subject_study)

study_en = {"exam" : "اسئلة امتحانات 💯",
"exercise" : "تمارين 🏋️",
"book" : "كتب 📚",
"explain" : "شروحات 👨‍🏫","course":"كورسات 📺",
"summary" : "ملخصات 📜"}

def get_subject_study(message):
    ID = message.chat.id
    text = message.text
    def give_error():
        bot.send_message(ID,"ادخال خاطىء حاول مرة تانية: ")
        bot.register_next_step_handler(message,get_subject_study)
    if text == back_btn:
        send_welcome(message)
        return
    if message.content_type != 'text':
        give_error()
        return
    if text not in subjects_en.values():
        give_error()
        return
    subject = get_dictkey(subjects_en,text)
    if not db.does_any_curriculum_exist(1,subject):
        bot.send_message(ID, "للأسف مافيش اي محتوى لحد توا 😅, حتنزل حاجات جديدة في اقرب وقت ممكن 😉")
        send_welcome(message)
        return
    markup = types.ReplyKeyboardMarkup()
    markup.add(*list(study_en.values()))
    markup.add(back_btn)
    bot.send_message(ID,"اختر واحد من الخيارات: ⬅️",reply_markup=markup)
    bot.register_next_step_handler(message,handle_study_menu,subject)
def handle_study_menu(message,subject):
    ID = message.chat.id
    cat = message.text
    if cat == back_btn:
        get_subject_study(message)
        return
    if cat not in study_en.values():
        bot.send_message(ID,"ادخال خاطئ")
        send_welcome(message)
        return
    cat = get_dictkey(study_en,cat)
    cur = db.get_curriculum(1,subject,cat)
    if not len(cur):
        bot.send_message(ID, "للأسف مافيش اي محتوى لحد توا 😅, حتنزل حاجات جديدة في اقرب وقت ممكن 😉")
        bot.send_message(ID,"اختار واحد من الخيارات: ⬅️")
        bot.register_next_step_handler(message,handle_study_menu,subject)
        return
    w = 3
    if cat == "explain":
        w = 1
    markup = types.ReplyKeyboardMarkup(row_width=w)
    j = []
    for c in cur:
        title = c[0]
        j.append(title)
    markup.add(*j)
    markup.add(back_btn)
    bot.send_message(ID,"اختار ملف",reply_markup=markup)
    bot.register_next_step_handler(message,process_which_file,cur)
def process_which_file(message,cur):
    ID = message.chat.id
    title = message.text
    if title == back_btn:
        send_welcome(message)
        return

    for c in cur:
        if c[0] == title:
            link = c[1]
            if './files' in link:
                if '.jpg' in link or '.jpeg' in link or '.png' in link:
                    file = open(link,'rb')
                    bot.send_photo(ID,file,caption=title)
                elif '.pdf' in link:
                    file = open(link,'rb')
                    bot.send_document(ID,file,caption=title)
            elif 'http' in link:
                if '.jpg' in link or '.jpeg' in link or '.png' in link:
                    bot.send_photo(ID,link,caption=title)
                elif '.pdf' in link:
                    bot.send_document(ID,link,caption=title)
                else:
                    bot.send_message(ID,link)
    send_welcome(message)
def process_checkin(message):
    ID = message.chat.id
    if user_not_exist(message):
        return
    day = get_weekday(0)
    day_num = get_weekday(0,1)
    if db.isteacher(ID):
        sched = eval(db.get_info("schedule",ID,table='teachers'))[day_num]
    else:
        group = db.get_info("grp",ID)
        sched = db.get_day_schedule(group, day)
    if len(sched) == 0:
        bot.send_message(ID, "ماعندكش اي محاضرات توا😍", disable_notification=True)
        send_welcome(message)
        return
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton("ايه",request_location=True)
    btn2 = types.KeyboardButton("لا",request_location=False)
    markup.add(btn1,btn2)
    bot.send_message(ID, "انت توا في الكلية؟",reply_markup=markup)
    bot.register_next_step_handler(message,process_checkin_2)
def process_checkin_2(message):
    ID = message.chat.id
    day = get_weekday(0)
    day_num = get_weekday(0,1)
    hour = datetime.now(tz).hour
    minute = datetime.now(tz).minute
    if db.isteacher(ID):
        group = 0
    else:
        group = db.get_info("grp",ID)

    if message.content_type=="location":
        if message.location:
            long = float(message.location.longitude)
            lat = float(message.location.latitude)
            if lat > 32.872946 and lat < 32.873824 and long > 13.208327 and long < 13.209326:
                if db.isteacher(ID):
                    sched = eval(db.get_info('schedule',ID,table='teachers'))[day_num]
                    for grp in sched:
                        start_time = sched[grp][0]
                        room = sched[grp][2]
                        if (hour == start_time and minute < 30) or (hour == start_time-1 and minute > 40):
                            bot.send_message(ID,"ارسل الكيو ار كود الخاص بالقاعة {} كصورة: ".format(room),reply_markup=types.ReplyKeyboardRemove())
                            sbj = db.get_info('subject',ID,table='teachers')
                            bot.register_next_step_handler(message,handle_qr_code,[room,sbj])
                            return
                    bot.send_message(ID,"للأسف مانقدرش نسجلك لانه فات عليك وقت المحاضرة 🤷‍♂️")
                    send_welcome(message)
                    return
                else:
                    sched = db.get_day_schedule(group, day)
                    for sbj in sched:
                        start_time = sched[sbj][0]
                        room = sched[sbj][2]
                        if (hour == start_time and minute < 30) or (hour == start_time-1 and minute > 40):
                            bot.send_message(ID,"ارسل الكيو ار كود الخاص بالقاعة {} كصورة: ".format(room),reply_markup=types.ReplyKeyboardRemove())
                            bot.register_next_step_handler(message,handle_qr_code,[room,sbj])
                            return
                    bot.send_message(ID,"للأسف مانقدرش نسجلك لانه فات عليك وقت المحاضرة 🤷‍♂️")
                    send_welcome(message)
                    return

            else:
                bot.send_message(ID,"يلزم تكون في الكلية باش تسجل حضورك 🤦‍♂️")
                send_welcome(message)
                return
    else:
        if message.text == "لا":
            bot.send_message(ID, 'لازم تكون في الكلية باش تسجل حضورك 🤦‍♂️')
            send_welcome(message)
            return
        elif message.content_type != "location":
            bot.send_message(ID,"لازم تبعت مكانك الحالي, حاول مرة ثانية:")
            process_checkin(message)
from pyzbar.pyzbar import decode
import urllib.request
from PIL import Image
import os
from os.path import isfile
def handle_qr_code(message,data):
    ID = message.chat.id
    room = data[0]
    sbj = data[1]
    if message.content_type != "photo":
        bot.send_message(ID,"يجب ارسال الكيو ار كود كصورة, حاول مرة ثانية: ")
        bot.register_next_step_handler(message,handle_qr_code,data)
        return
    fileid = message.photo[-1].file_id
    localpath = './files/qrcodes/users/'+fileid+'.jpg'
    if isfile(localpath):
        bot.send_message(ID,"الصورة هذه باعتهالي قبل 🤨, عاود ارسل صورة جديدة: ")
        bot.register_next_step_handler(message,handle_qr_code,data)
        return
    f = bot.get_file(fileid).file_path
    path = "https://api.telegram.org/file/bot"+TOKEN+"/"+str(f)
    urllib.request.urlretrieve(path,localpath)
    code = decode(Image.open(localpath))
    if code:
        data = code[0].data.decode('UTF-8')
        if str(room) == data:
            if db.isteacher(ID):
                name = db.get_info('name',ID,table='teachers')
            else:
                name = db.get_info('name',ID)
            date = datetime.now(tz).date().isoformat()
            time = datetime.now(tz).strftime("%H:%M:%S")
            db.register_attendance(ID,name,date,time,room,sbj)
            bot.send_message(ID,"تمام, تم تسجيل حضورك")
            delete_attendance_record()
            send_welcome(message)
            return
        else:
            bot.send_message(ID,"هذا مش كود القاعة رقم {}, حاول مرة ثانية: ".format(room))
            os.remove(localpath)
            bot.register_next_step_handler(message, handle_qr_code, room)
            return
    else:
        bot.send_message(ID,"ماقدرتش نقرا الصورة كويس 🤨, عاود ارسلها: ")
        os.remove(localpath)
        bot.register_next_step_handler(message,handle_qr_code,room)

@bot.message_handler(regexp=settings_btn)
def handle_settings_directly(message):
    show_settings_menu(message)
    bot.register_next_step_handler(message, settings_menu)
def settings_menu(message):
    ID = message.from_user.id
    t = message.text
    if t == settings_change_name_btn:
        bot.send_message(ID,"شن هو اسمك؟ 🤔",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,settings_change_name)
    elif t == settings_change_group_btn:
        groups = list(range(1,12))
        markup = types.ReplyKeyboardMarkup()
        markup.add(*list(map(str,groups)))
        markup.add(back_btn)
        bot.send_message(ID,"بتغير لأي مجموعة؟ 🤔",reply_markup=markup)
        bot.register_next_step_handler(message,settings_change_group)
    elif t == get_scores_btn:
        get_scores(message)
    elif t == get_feedback:
        bot.send_message(ID,"شن تبي تقول؟ 🤔",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,handle_feedback)
    else:
        send_welcome(message)
def handle_feedback(message):
    ID = message.chat.id
    feedback = message.text
    bot.send_message(ID,"تمام 👍")
    send_welcome(message)
    name = db.get_info('name',ID)
    text = "عندك فيدباك من "+name+":\n"+feedback
    bot.send_message(MID,text)
def get_scores(message):
    ID = message.chat.id
    subjects = list(subjects_en.keys())
    text = "نقاطك ⭐: \n"
    for subject in subjects:
        sbj = subjects_en[subject]
        score=db.get_info(subject,ID,table="scores")
        text += "\n {s} : {c} \n".format(s=sbj,c=score)
    bot.send_message(ID,text)
    send_welcome(message)
def settings_change_group(message):
    ID = message.from_user.id
    group = message.text
    if group == back_btn:
        send_welcome(message)
        return
    if (not group.isdigit()) or message.content_type != "text":
        bot.send_message(ID, "بالله اختار من القائمة")
        bot.register_next_step_handler(message, settings_change_group)
        return
    db.update_info('grp', group, ID)
    db.remove_needed_homework_by_id(ID)
    bot.send_message(ID,"{n}, هكي انت غير مجموعتك! واجباتك كلها امتسحت".format(n=db.get_firstname(ID)))
    send_welcome(message)
def settings_change_name(message):
    ID = message.from_user.id
    name = message.text
    if message.content_type != "text":
        bot.send_message(ID, "دخل اسمك قلنا 🙂, عاود ارسل اسمك:")
        bot.register_next_step_handler(message, settings_change_name)
        return
    elif not isarabic(name):
        bot.send_message(ID, "بالله عاود دخل اسمك الأول بس من غير ايموجيز وبالعربي!")
        bot.register_next_step_handler(message, settings_change_name)
        return
    db.update_info('name', name, ID)
    bot.send_message(ID,"تمام {n}, سجلت اسمك!".format(n=name))
    send_welcome(message)

t_absent = "مانقدرش نجي 😦"
t_hw = "اطلب واجب 📝"
t_review = "صلح الواجبات 🧐"
t_summary = "ارسل ملخص 📜"
t_message = "ارسل رسالة ✉️"
t_schedule = "مواقيت محاضراتي 🕑"
t_attendance = "سجل حضوري 🙋‍♂️"
t_get_attendance = "اعطيني الحضور 📅"
def teacher_menu_handler(message):
    t = message.text
    if t == t_absent:
        process_teacher_absent(message)
    elif t == t_hw:
        process_teacher_hw(message,chosen_groups=[])
    elif t == t_review:
        process_teacher_review(message)
    elif t == t_summary:
        process_teacher_summary(message,chosen_grp=[])
    elif t == t_message:
        process_teacher_message(message)
    elif t == t_schedule:
        process_teacher_schedule(message)
    elif t == t_attendance:
        process_checkin(message)
    elif t == t_get_attendance:
        ID = message.chat.id
        markup = types.ReplyKeyboardMarkup()
        markup.add(tomorrow_btn,today_btn)
        markup.add(back_btn)
        bot.send_message(message.chat.id,"حضور بتاع اي يوم؟",reply_markup=markup)
        bot.register_next_step_handler(message,process_get_attendance)
    elif t == weather_btn:
        send_today_weather(message)
from datetime import timedelta
def process_get_attendance(message):
    ID = message.chat.id
    if message.text == today_btn:
        d = 0
    elif message.text == tomorrow_btn:
        d = 1
    else:
        send_welcome(message)
        return
    date = datetime.now(tz).date() + timedelta(d)
    day = get_weekday(d,1)
    sched = eval(db.get_info('schedule',ID,table='teachers'))
    if not sched:
        send_welcome(message)
        return
    sched = sched[day]
    if len(sched) == 0:
        bot.send_message(ID,"ماعندكش محاضرات في هذا اليوم 😅")
        send_welcome(message)
        return
    groups = list(map(str,sched.keys()))
    markup = types.ReplyKeyboardMarkup()
    markup.add(*groups)
    markup.add(back_btn)
    bot.send_message(ID,"اي مجموعة تبي حضورها؟ 🤔",reply_markup=markup)
    bot.register_next_step_handler(message,get_group_for_attendance,date)
def get_group_for_attendance(message,date):
    ID = message.chat.id
    grp = message.text
    if message.content_type != "text":
        bot.send_message(ID,"ادخال خاطئ, حاول مرة تانية")
        bot.register_next_step_handler(message,get_group_for_attendance,date)
        return
    if not grp.isdigit():
        bot.send_message(ID,"ادخال خاطئ, حاول مرة تانية")
        bot.register_next_step_handler(message,get_group_for_attendance,date)
        return
    attendance = db.get_attendance_group(grp,date,db.get_info('subject',ID,table='teachers'))
    bot.send_message(ID,"حضور المجموعة {g} يوم {d}: ".format(g=grp,d=date))
    text = ""
    num = 0
    for i in attendance:
        regid = db.get_info('regid',i)
        name = attendance[i][0]
        time = attendance[i][1]
        room = attendance[i][2]
        text += "\n🛑 {r} | {n} | {t} \n".format(r=regid,n=name,t=time)
        num += 1
    text += "اجمالي عدد الحضور: "+str(num)
    bot.send_message(ID,text)
    send_welcome(message)


today_btn = 'اليوم ⬇️'
tomorrow_btn = 'غدوا ↖️'


@bot.message_handler(regexp=t_absent)
def process_teacher_absent(message):
    ID = message.from_user.id
    if not db.isteacher(ID):
        send_welcome(message)
        return
    markup = types.ReplyKeyboardMarkup()
    markup.add(today_btn)
    markup.add(tomorrow_btn)
    markup.add(back_btn)
    bot.send_message(ID, "امتى مش حاضر؟ 🤔", reply_markup=markup)
    bot.register_next_step_handler(message, process_teacher_absent_question)


def process_teacher_absent_question(message):
    ID = message.from_user.id
    text = message.text
    if text == today_btn:
        report_teacher_absent(message,0)
    elif text == tomorrow_btn:
        report_teacher_absent(message,1)
    else:
        send_welcome(message)
        return


def report_teacher_absent(message,day):
    ID=message.from_user.id
    ar_day = "اليوم" if day==0 else "غدوا"
    day = get_weekday(day,1)
    schedule=eval(db.get_info('schedule',ID,table='teachers'))
    if schedule == None:
        bot.send_message(ID,"للأسف قاعد ماعنديش جدولك!")
        return
    schedule = schedule[day]
    subject= db.get_info('subject',ID,table='teachers')
    subject=subjects_en[subject]

    if not len(schedule):
        bot.send_message(ID,'ماعندكش اي محاضرات {d} 😀'.format(d=ar_day))
        send_welcome(message)
        return

    for grp in schedule:
        ids = db.get_all_group_ID(grp)
        for i in ids:
            name = db.get_firstname(i)
            bot.send_message(i,"{n}, {d} استاذ ال{s} غايب 😋 استمتع بحياتك".format(n=name,d=ar_day,s=subject))
    bot.send_message(ID,"تمام, تم ابلاغ الطلاب يلي عندهم محاضرات انك مش حتقدر تجي {d} 👍".format(d=ar_day))
    send_welcome(message)


@bot.message_handler(regexp=t_hw)
def process_teacher_hw(message,chosen_groups=[]):
    ID = message.from_user.id
    if not db.isteacher(ID):
        bot.send_message(ID,"انت مش استاذ")
        send_welcome(message)
        return
    given_groups = eval(db.get_info('groups', ID,table='teachers'))
    markup = types.ReplyKeyboardMarkup()
    for grp in given_groups:
        if grp not in chosen_groups:
            markup.add(str(grp))
    markup.add("تم",back_btn)
    bot.send_message(ID,'اختر المجموعات يلي تبي تعطاها الواجب',reply_markup=markup)
    bot.register_next_step_handler(message,get_teacher_hw_groups,chosen_groups)


def get_teacher_hw_groups(message,chosen_groups):
    ID = message.from_user.id
    text = message.text
    if text == back_btn:
        send_welcome(message)
        return
    if text == "تم":
        if not len(chosen_groups):
            bot.send_message(ID,"ما أخترتش شي, حاول مرة تانية")
            process_teacher_hw(message,chosen_groups)
            return
        bot.send_message(ID,"تمام, شن ينص الواجب؟ 🤔",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,get_teacher_hw_info,chosen_groups)
        return
    else:
        if not text.isdigit():
            bot.send_message(ID,'ادخل خاطئ, حاول مرة تانية')
            process_teacher_hw(message,chosen_groups)
            return
        else:
            chosen_groups.append(int(text))
            process_teacher_hw(message,chosen_groups)


def get_teacher_hw_info(message,chosen_groups):
    ID = message.from_user.id
    info = message.text
    markup = types.ReplyKeyboardMarkup()
    markup.add("لا","ايه")
    bot.send_message(ID,"هل فيه امكانية انك ترسل صورة للواجب؟",reply_markup=markup)
    bot.register_next_step_handler(message,get_teacher_hw_photo_question,[chosen_groups,info,None])


def get_teacher_hw_photo_question(message,data):
    ID = message.from_user.id
    subject = db.get_info('subject',ID,table='teachers')
    text = message.text
    if text == "ايه":
        bot.send_message(ID,"اوكي ابعت الصورة: ",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,get_teacher_hw_photo,data)
        return
    else:
        markup=types.ReplyKeyboardMarkup()
        markup.add("لا","ايه")
        bot.send_message(ID,"هل تبي تمسح اي واجب قبل هذا؟",reply_markup=markup)
        bot.register_next_step_handler(message,want_to_delete_past_hws,data)
        return
def want_to_delete_past_hws(message,data):
    ID = message.chat.id
    text = message.text
    groups = data[0]
    info = data[1]
    fileid = data[2]
    subject = db.get_info('subject',ID,table='teachers')
    subject_ar = subjects_en[subject]

    if text == "ايه":
        for grp in groups:
            db.remove_givenhomework(grp,subject)
            db.remove_needed_homework_group(grp,subject)

    for grp in groups:
        ids = db.get_all_group_ID(int(grp))
        for i in ids:
            if fileid:
                bot.send_message(i, "عندك واجب {s}:".format(s=subject_ar))
                bot.send_photo(i, fileid, caption=info)
                db.add_homework_group(grp, subject, info, fileid)
            else:
                bot.send_message(i,"عندك واجب {s}, ينص: {i}".format(s=subject_ar,i=info))
                db.add_homework_group(grp, subject, info)
    bot.send_message(ID,"تمام, تم ارسال الواجب لكل الطلبة",reply_markup=types.ReplyKeyboardRemove())
    send_welcome(message)

def get_teacher_hw_photo(message,data):
    ID = message.from_user.id
    groups = data[0]
    info = data[1]
    subject = db.get_info('subject',ID,table='teachers')
    subject_ar = subjects_en[subject]
    if not (message.content_type == 'photo'):
        bot.reply_to(message, 'لازم ترسل صورة فقط, ابعت الصورة مرة تانية:')
        bot.register_next_step_handler(message, get_teacher_hw_photo, data)
        return
    fileid = message.photo[-1].file_id
    markup = types.ReplyKeyboardMarkup()
    markup.add("لا", "ايه")
    bot.send_message(ID, "هل تبي تمسح اي واجب قبل هذا؟", reply_markup=markup)
    data[2]=fileid
    bot.register_next_step_handler(message, want_to_delete_past_hws,data)

@bot.message_handler(regexp=t_review)
def process_teacher_review(message):
    ID = message.from_user.id
    given_groups = eval(db.get_info('groups',ID,table='teachers'))
    subject = db.get_info('subject',ID,table='teachers')
    subject_groups = db.get_given_homework_groups(subject)
    groups = []
    for grp in subject_groups:
        if grp in given_groups:
            groups.append(grp)

    if len(groups) == 0:
        bot.send_message(ID, 'مافيش اي واجبات تبي التصليح')
        send_welcome(message)
        return
    groups = list(set(groups))
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for grp in groups:
        markup.add(str(grp))
    markup.add(back_btn)
    bot.send_message(ID, 'اختر  المجموعة يلي تبي تصلحلها', reply_markup=markup)
    bot.register_next_step_handler(message, process_teacher_review_group)


def process_teacher_review_group(message):
    ID = message.from_user.id
    if message.text == back_btn:
        send_welcome(message)
        return
    grp = message.text
    subject = db.get_info('subject',ID,table='teachers')
    markup = types.ReplyKeyboardMarkup()
    markup.add(right_btn, wrong_btn)
    unis = db.get_givenhomework_uni(subject,grp)
    hws = []
    for uni in unis:
        hws.append(db.review_homework(uni,grp))
    d = {}
    for hw in hws:
        for h in hw:
            d[h[0]] = []
    for hw in hws:
        for h in hw:
            if not (h[2] in d[h[0]]):
                d[h[0]].append(h[2])
    for hw in hws:
        for h in hw:
            d[h[0]].append(types.InputMediaPhoto(h[1]))

    if len(d) != 0:
        data = d[list(d)[0]]
        fileid_array = data[1:]
        person_id = data[0]
        uni = get_dictkey(d, data)
        bot.send_media_group(ID, fileid_array)
        bot.send_message(ID, 'شن رايك؟', reply_markup=markup)
        bot.register_next_step_handler(message, right_wrong_homework_teacher, [person_id, subject, message])
        db.remove_given_homework(person_id, uni)
        return
    else:
        bot.send_message(ID, 'تم التصحيح')
        send_welcome(message)


def right_wrong_homework_teacher(message, data):
    ID = message.from_user.id
    person_id = data[0]
    subject = subjects_en[data[1]]
    msg = data[2]
    markup = types.ReplyKeyboardRemove(selective=False)
    if message.text == right_btn:
        score = int(db.get_info(data[1], person_id, table='scores')) + 1
        db.update_info(data[1], score, person_id, table='scores')
        bot.send_message(person_id, "واجبك ال{d} صح, حصلت نقطة ⭐".format(d=subject))
    if message.text == wrong_btn:
        bot.send_message(ID, 'علاش؟', reply_markup=markup)
        bot.register_next_step_handler(message, why_wrong_homework_teacher, [person_id, subject, msg])
    else:
        process_teacher_review_group(msg)


def why_wrong_homework_teacher(message, data):
    person_id = data[0]
    subject = data[1]
    msg = data[2]
    reason = message.text
    bot.send_message(person_id, 'واجبك ال{d} كان للأسف غلط, السبب {r}'.format(d=subject, r=reason))
    process_teacher_review_group(msg)


@bot.message_handler(regexp=t_summary)
def process_teacher_summary(message,chosen_grp=[]):
    ID = message.from_user.id
    if db.isteacher(ID):
        groups = eval(db.get_info("groups",ID,table='teachers'))
        markup = types.ReplyKeyboardMarkup()
        for grp in groups:
            if not(str(grp) in chosen_grp):
                markup.add(str(grp))
        markup.add(back_btn,'تم')
        bot.send_message(ID,"اختر المجموعات يلي تبي ترسلهم الملخص",reply_markup=markup)
        bot.register_next_step_handler(message,get_chosen_group_summary,chosen_grp)


def get_chosen_group_summary(message,chosen_grp):
    ID = message.from_user.id
    grp = message.text
    if grp == back_btn:
        send_welcome(message)
        return
    if grp == 'تم':
        if not len(chosen_grp):
            bot.send_message(ID,'ما أخترتش اي مجموعة')
            process_teacher_summary(message,chosen_grp)
            return
        else:
            bot.send_message(ID,"شن هو عنوان الملخص؟",reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message,get_info_summary,chosen_grp)
            return
    else:
        chosen_grp.append(grp)
        process_teacher_summary(message, chosen_grp)
def get_info_summary(message,chosen_grp):
    ID = message.from_user.id
    info = message.text
    bot.send_message(ID, "تمام ابعت الملخص كصورة (ابعت بالصورة لما تكمل اضغط تمام)",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, handle_summary, [chosen_grp,info,[]])
def handle_summary(message,data):
    ID = message.from_user.id
    if message.content_type != "photo":
        bot.send_message(ID,"يمكن انك تبعت صورة بس, حاول مرة تانية")
        process_teacher_summary(message)
        return
    fileid = message.photo[-1].file_id
    data[2].append(types.InputMediaPhoto(fileid))
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("مزال","تمام")
    bot.send_message(ID,"مزال ولا تمام؟",reply_markup=markup)
    bot.register_next_step_handler(message, still_or_not_summary,data)
def still_or_not_summary(message,data):
    ID = message.from_user.id
    groups = data[0]
    info = data[1]
    subject = subjects_en[db.get_info('subject',ID,table='teachers')]
    if message.text == "مزال":
        bot.send_message(ID,"ابعت تاني",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,handle_summary,data)
    else:
        for grp in groups:
            ids = db.get_all_group_ID(grp)
            for i in ids:
                bot.send_message(i,"ملخص مادة ال{s}: ".format(s=subject))
                bot.send_message(i,info)
                bot.send_media_group(i, data[2])

        bot.send_message(ID,"تمام")
        send_welcome(message)


@bot.message_handler(regexp=t_message)
def process_teacher_message(message):
    ID = message.from_user.id
    groups = eval(db.get_info('groups',ID,table='teachers'))
    markup = types.ReplyKeyboardMarkup()
    markup.add(*list(map(str,groups)))
    markup.add('كل المجموعات')
    markup.add(back_btn)
    bot.send_message(ID,"اختر المجموعة: ", reply_markup=markup)
    bot.register_next_step_handler(message,process_teacher_message_handler)
def process_teacher_message_handler(message):
    ID = message.from_user.id
    group = message.text
    if group == 'كل المجموعات':
        group = eval(db.get_info('groups',ID,table='teachers'))

    elif group == back_btn:
        send_welcome(message)
        return
    else:
        group=[group]
    bot.send_message(ID, 'شن هو نص الرسالة؟', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_teacher_message, group)

def get_teacher_message(message,groups):
    info = message.text
    ID = message.from_user.id
    subject=subjects_en[db.get_info('subject',ID,table='teachers')]
    for grp in groups:
        ids = db.get_all_group_ID(grp)
        for i in ids:
            bot.send_message(i,"عندك رسالة من استاذ ال{s}:".format(s=subject))
            bot.send_message(i,info)
    bot.send_message(ID,"تمام, تم ارسال الرسالة لكل الطلبة")
    send_welcome(message)

@bot.message_handler(regexp=t_schedule)
def process_teacher_schedule(message):
    ID = message.from_user.id
    schedule =db.get_info('schedule',ID,table='teachers')
    if not schedule:
        bot.send_message(ID, "للأسف جدول محاضراتك مش مسجل عندي")
        send_welcome(message)
        return
    markup = types.ReplyKeyboardMarkup()
    markup.add(tomorrow_btn,today_btn)
    markup.add(back_btn)
    bot.send_message(ID,"لاي يوم؟ 🤔",reply_markup=markup)
    bot.register_next_step_handler(message,which_day_teacher_schedule)
def which_day_teacher_schedule(message):
    text = message.text
    ID = message.from_user.id
    if text == today_btn:
        schedule=get_teacher_schedule(ID,get_weekday(0,1))
    elif text == tomorrow_btn:
        schedule=get_teacher_schedule(ID,get_weekday(1,1))
    else:
        send_welcome(message)
        return
    if not len(schedule):
        bot.send_message(ID,"ماعندكش اي محاضرات😄")
        send_welcome(message)
        return
    elif len(schedule)==1:
        report="عندك محاضرة وحدة, "
    elif len(schedule)==2:
        report="عندك محاضرتين, "
    else:
        report="عندك {n} محاضرات, ".format(n=len(schedule))
    times = list(schedule.values())
    times.sort()
    for t in times:
        grp = get_dictkey(schedule,t)
        report += "\n🛑 في المجموعة رقم {g} من الساعة {f} الى الساعة {t} في القاعة رقم {h}".format(g=grp,f=t[0],t=t[1],h=t[2])
    bot.send_message(ID,report)
    send_welcome(message)


def get_teacher_schedule(ID,day):
    try:
        schedule=eval(db.get_info('schedule', ID, table="teachers"))
        return schedule[day]
    except Exception as e:
            return []


sendhw_menu_btn = "ابعت واجب 📝"
alert_menu_btn = "ابعت رسالة للقروب 💬"
send_summary_menu_btn = "ابعت ملخص درس اليوم ⬇️"
admin_polling_menu_btn = "قائمة ترشيح المشرفين 🗳️"
start_polling_btn = 'ابدا في ترشيح المشرف 🏁'
start_voting_btn = 'ابدا في التصويت 🗳️'
stop_voting_btn = "اوقف التصويت ✋"

@bot.message_handler(regexp=admin_btn)
def handle_admin_menu(message):
    if user_not_exist(message):
        return
    ID = message.from_user.id
    if db.get_info('admin', ID) != 1:
        bot.send_message(ID, "للأسف انت مش مشرف!")
        send_welcome(message)
        return
    show_menu(message,sendhw_menu_btn, alert_menu_btn, send_summary_menu_btn, admin_polling_menu_btn, back_btn)
    bot.register_next_step_handler(message, process_admin_menu)


def process_admin_menu(message):
    ID = message.from_user.id
    text = message.text
    #if text == review_menu_btn:
    #   review_homework(message)
    if text == sendhw_menu_btn:
        markup = types.ReplyKeyboardMarkup()
        markup.add(*list(subjects_en.values()))
        bot.send_message(ID, "واجب شني؟", reply_markup=markup)
        bot.register_next_step_handler(message, process_which_hw)
    elif text == alert_menu_btn:
        bot.send_message(ID, "شن تبي تقول؟ لما تكتب عبود كأنك كتبت اسم الطالب نفسه",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_alert_info_menu)
    elif text == send_summary_menu_btn:
        markup = types.ReplyKeyboardMarkup()
        markup.add(*list(subjects_en.values()))
        markup.add(back_btn)
        bot.send_message(ID,"الملخص بتاع اي مادة؟",reply_markup=markup)
        bot.register_next_step_handler(message, process_summary_subject)
    elif text == admin_polling_menu_btn:
        show_menu(message,stop_voting_btn,start_voting_btn,start_polling_btn,back_btn)
        bot.register_next_step_handler(message, admin_polling_menu_handler)
    elif text == back_btn:
        send_welcome(message)
        return
def admin_polling_menu_handler(message):
    ID = message.chat.id
    text = message.text
    if text == start_polling_btn:
        start_polling(message)
        send_welcome(message)
    elif text==start_voting_btn:
        start_voting(message)
    elif text ==stop_voting_btn:
        stop_voting(message)
    elif text == back_btn:
        send_welcome(message)
def start_polling(message):
    ID = message.from_user.id
    grp = db.get_info('grp',ID)
    ids = db.get_all_group_ID(grp)
    btn1 = types.InlineKeyboardButton('ايه', callback_data="yes")
    btn2 = types.InlineKeyboardButton('لا', callback_data="no")
    markup = types.InlineKeyboardMarkup()
    markup.row(btn1, btn2)

    for i in ids:
        bot.send_message(i, "تبي تترشح كمشرف؟ 🤠",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def polling_callback(call):
    ID = call.from_user.id
    data = call.data
    msg_ID = call.message.message_id
    if data == "yes":
        name = db.get_info('name',ID)
        grp = db.get_info('grp', ID)
        photos = bot.get_user_profile_photos(ID).photos
        if len(photos) != 0:
            photo = photos[0][-1].file_id
        else:
            photo = None
        db.add_polling_member(ID, grp, name, photo)
        bot.send_message(ID, "تمام, هكي انت رشحت روحك 😉")
        send_welcome(call.message)
    bot.delete_message(ID,msg_ID)

def start_voting(message):
    ID = message.chat.id
    grp = db.get_info('grp',ID)
    ids = db.get_all_group_ID(grp)
    candidates =db.get_candidates(grp)
    if len(candidates) == 0:
        bot.send_message(ID,"ما حد رشح روحه!")
        send_welcome(message)
        return
    names = []
    for c in candidates:
        names.append(c[0])
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(*names)
    markup.add("منبيش نصوت")
    for i in ids:
        msg = bot.send_message(i, 'لمن تصوت كمشرف؟ 🤔🗳️',reply_markup=markup)
        bot.register_next_step_handler(msg, get_vote)
def get_vote(message):
    ID=message.chat.id
    candidate = message.text
    if candidate == "منبيش نصوت":
        bot.send_message(ID,"على راحتك")
        send_welcome(message)
        return
    grp = db.get_info('grp',ID)
    db.add_vote(candidate,grp)
    bot.send_message(ID,"تمام رشحت {n}".format(n=candidate))
    send_welcome(message)
def stop_voting(message):
    ID = message.chat.id
    grp = db.get_info('grp',ID)
    result = db.get_voting_result(grp)
    votes = []
    for i in result:
        votes.append(i[3])
    winning_vote=max (votes)
    winning_candidates=[]
    for i in result:
        if i[3] == winning_vote:
            winning_candidates.append(i)

    if len(winning_candidates) == 0:
        bot.send_message(ID,"ما في حد صوت! جرب بعدين")
        send_welcome(message)
        return
    if len(winning_candidates) > 1:
        bot.send_message(ID,"فيه تعادل بين المترشحين: ")
        for c in winning_candidates:
            bot.send_message(ID,c[1])
        bot.send_message(ID,"سيتم اعادة التصويت")
        db.remove_all_candidate(grp)
        for c in winning_candidates:
            db.add_polling_member(c[0],grp,c[1],c[2],c[3])
        start_voting(message)
    elif len(winning_candidates) == 1:
        winner = winning_candidates[0]
        ids = db.get_all_group_ID(grp)
        for i in ids:
            bot.send_photo(i,winner[2], "المشرف الجديد هو: "+winner[1]+" 🎉🎉")
        admins = db.get_admin_ID(grp)
        for admin in admins:
            db.update_info('admin',0,admin)
        db.update_info('admin',1,winner[0])
        bot.send_message(winner[0], "مبروك 🎉, تم تعينك كمشرف على مجموعتك!")
        db.remove_all_candidate(grp)
        send_welcome(message)

"""
@bot.message_handler(regexp="Ok")
def test(message):
    bot.register_next_step_handler(bot.send_message(message.chat.id,'Okok'),bkbk)
def bkbk(message):
    print(message.chat.id)
"""

def process_summary_subject(message,subject=None):
    ID = message.from_user.id
    if subject == None:
        subject = message.text
    else:
        subject = message.text
    if subject == back_btn:
        send_welcome(message)
        return
    bot.send_message(ID,"ابعت صور الملخص, بالصورة: ",reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_summary_photos,[subject,[]])
def process_summary_photos(message,data):
    ID = message.from_user.id
    subject = data[0]
    if not(message.content_type == 'photo'):
        bot.send_message(ID,"مابعتش صورة, عاود من جديد 😅")
        process_summary_subject(message,subject)
        return
    fileid = message.photo[-1].file_id
    data[1].append(types.InputMediaPhoto(fileid))
    markup = types.ReplyKeyboardMarkup()
    markup.add("تمام","مزال")
    bot.send_message(ID,"مزال ولا تمام؟",reply_markup=markup)
    bot.register_next_step_handler(message,keep_or_stop_summary,data)
def keep_or_stop_summary(message,data):
    ID = message.from_user.id
    subject = data[0]
    group = db.get_info('grp',ID)
    fileids = data[1]
    text = message.text

    if text == "مزال":
        bot.send_message(ID,"ارسل تاني: ",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,process_summary_photos,data)
    else:
        ids = db.get_all_group_ID(group)
        for i in ids:
            bot.send_message(i,"ملخص لمحاضرة ال{s} اليوم:".format(s=subject))
            bot.send_media_group(i,fileids)
        bot.send_message(ID,"تمام, هكي تم ارسال الملخص لكل طلبة مجموعتك 😊")
        send_welcome(message)
def process_alert_info_menu(message):
    ID = message.from_user.id
    info = message.text
    manage_alert(message, info)


def process_which_hw(message):
    ID = message.from_user.id
    subject = get_dictkey(subjects_en, message.text)
    bot.send_message(ID, "شني ينص الواجب؟", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_info_hw, subject)


def process_info_hw(message, subject):
    ID = message.from_user.id
    grp = db.get_info('grp', ID)
    if db.get_info('admin', ID) == 0:
        bot.send_message(ID, 'Unauthorized')
        return
    info = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("ايه")
    markup.add("لا")
    bot.send_message(ID, "فيه كيف ترسل صورة للواجب؟", reply_markup=markup)
    bot.register_next_step_handler(message, send_neededhw_photo, [grp, subject, info,None])

def homework_menu_handler(message):
    ID = message.from_user.id
    subjects = list(set(db.get_needed_homework(ID)))
    if message.text == back_btn:
        show_main_menu(message)
        return
    if len(subjects) == 0:
        return
    markup = types.ReplyKeyboardMarkup()
    markup.add('ايه')
    markup.add('لا')
    subject = get_dictkey(subjects_en, message.text)
    inf = db.get_needed_homework_info(ID, subject)[0]
    uni = inf[0]
    info = inf[1]
    fileid = inf[2]

    if fileid:
        bot.send_photo(ID, fileid, caption=info)
    else:
        bot.send_message(ID, info)

    bot.send_message(ID, "تبي تسلم واجبك توا؟", reply_markup=markup)
    bot.register_next_step_handler(message, when_to_submit_hw, [subject, uni])


def when_to_submit_hw(message, data):
    ID = message.from_user.id
    text = message.text
    if text == "ايه":
        bot.send_message(message.from_user.id,
                         "ارسل الواجب بالصورة, لما تكمل ارسل تمام , كان لقيت اسمك مكتوب على الورقة حيمشي الواجب غلط",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, homework_handler, data)
    elif text == "لا":
        bot.send_message(ID, "تمام, لما تحله ابعتهولي")
        send_welcome(message)
        return


def homework_handler(message, data):
    if message.text == back_btn or message.text == "/start":
        send_welcome(message)
        return
    if not (message.content_type == 'photo' or message.content_type == 'document'):
        bot.reply_to(message, 'لازم ترسل ملف او صورة فقط -_-')
        bot.register_next_step_handler(message, homework_handler)
        return
    ID = message.from_user.id
    group = db.get_info('grp', ID)
    fileid = message.photo[-1].file_id
    subject = data[0]
    uni = data[1]
    db.submit_homework(uni, ID, fileid, group, subject)
    markup = types.ReplyKeyboardMarkup()
    markup.add('تمام', 'مزال')
    bot.send_message(ID, 'ارسل بالوحدة, اضغط تمام لما تكمل', reply_markup=markup)
    bot.register_next_step_handler(message, wait_next_homework, data)


def wait_next_homework(message, data):
    ID = message.from_user.id
    if message.text == 'مزال':
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(ID, 'ارسل تاني:', reply_markup=markup)
        bot.register_next_step_handler(message, homework_handler, data)
    if message.text == 'تمام':
        bot.send_message(ID, 'تمام, سلمت واجبك هكي!')
        show_main_menu(message)


def get_weekday(day,isnum=False):
    today = datetime.now(tz).weekday()
    d = today + day
    if d > 6:
        d -= 7
    if isnum:
        return d
    return ['mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun'][d]


def translate_weekday(day):
    return {'mon': 'الاثنين', 'tue': "الثلاث", 'wed': "الاربعاء", 'thur': "الخميس", 'fri': "الجمعة", 'sat': "السبت",
            'sun': "الاحد"}[day]


@bot.message_handler(regexp=info_btn)
def handle_info_command(message):
    if user_not_exist(message):
        return
    show_info_menu(message)
    bot.register_next_step_handler(message, handle_info_menu)


def handle_info_menu(message):
    t = message.text
    if t == info_today_btn:
        get_day_info(message, 0)
    if t == info_tomorrow_btn:
        get_day_info(message, 1)
    if t == info_timetable_btn:
        send_timetable(message)
    if t == info_hw:
        get_hw(message)
    if t == info_exams_table:
        send_exams_table(message)
    if message.text == back_btn:
        send_welcome(message)

def send_exams_table(message):
    ID = message.chat.id
    photo = open('./files/photos/examtables/2018.jpg', 'rb')
    bot.send_photo(ID,photo,"مواعيد الامتحانات 🤓")
    send_welcome(message)

def get_hw(message):
    ID = message.from_user.id
    subjects = db.get_needed_homework(ID)
    subjects = list(set(subjects))
    if len(subjects)==0:
        bot.send_message(ID,"ماعندكش اي واجب 😊")
    for sbj in subjects:
        text = "🛑 عندك "
        info=db.get_needed_homework_info(ID,sbj)
        ar = subjects_en[sbj]
        if len(info)==1:
            text += "واجب {s} ".format(s=ar)
        elif len(info)==2:
            text += "واجبين {s} ".format(s=ar)
        else:
            text += "{l} واجبات {s} ".format(l=len(info),s=ar)
        bot.send_message(ID,text)
        for inf in info:
            des = inf[1]
            fileid = inf[2]
            if fileid:
                bot.send_photo(ID,fileid,des)
            else:
                bot.send_message(ID,des)
    send_welcome(message)
def send_today_weather(message):
    ID = message.from_user.id
    w = get_weather()
    tmp = get_now_temp(w)
    status = get_now_status(w)
    text = "الجو اليوم " + status + " ودرجة الحرارة توا " + tmp
    bot.send_message(ID, text)
    send_welcome(message)


def send_timetable(message):
    ID = message.from_user.id
    group = db.get_info('grp', ID)
    try:
        photo = open('./files/photos/timetables/' + str(group), 'rb')
        bot.send_photo(ID, photo, caption="جدول محاضرات المجموعة رقم " + str(group))
        send_welcome(message)
    except Exception as e:
        bot.send_message(ID,"للأسف جدول المحاضرات مش متوفر حاليا")
        send_welcome(message)

def convert_time_to_readable(t):
    if t > 12:
        return t - 12
    else:
        return t

def get_day_info(message, rank,sID=None):
    if not message:
        ID = sID
    else:
        ID = message.from_user.id
    group = db.get_info('grp', ID)
    day = get_weekday(rank)
    day_word = "اليوم" if rank == 0 else "غدوا"
    schedule = db.get_day_schedule(group, day)
    if len(schedule) == 0:
        bot.send_message(ID, "ماعندكش {dd} اي محاضرات😍".format(dd=day_word),disable_notification=True)
        if message:
            send_welcome(message)
        return

    if len(schedule) == 1:
        w = "محاضرة"
    elif len(schedule) == 2:
        w = "محاضرتين:"
    else:
        w = str(len(schedule)) + " محاضرات:"

    text = "عندك {dd} {ww} ".format(ww=w,dd=day_word)
    wa = "🛑 و"
    schedule_list = list(schedule)
    for i in range(len(schedule_list)):
        sb = subjects_en[schedule_list[i]]
        frm = convert_time_to_readable(schedule[schedule_list[i]][0])
        to = convert_time_to_readable(schedule[schedule_list[i]][1])
        room = schedule[schedule_list[i]][2]
        text += "{s} من {f} الى {t} في القاعة {r} ".format(s=sb, f=frm, t=to,r=room)

        if len(schedule_list) > 1 and i != (len(schedule_list) - 1):
            text = text + wa
    bot.send_message(ID, text,disable_notification=True)
    if message:
        send_welcome(message)


@bot.message_handler(commands=['review', ])
def review_homework(message):
    ID = message.from_user.id
    if db.get_info('admin', ID) == 0:
        bot.send_message(ID, 'Unauthorized')
        return
    group = db.get_info('grp', ID)
    subjects = db.get_given_homework_group(group)
    if len(subjects) == 0:
        bot.send_message(ID, 'مافيش اي واجبات تبي التصليح')
        send_welcome(message)
        return
    subjects = list(set(subjects))
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for subject in subjects:
        markup.add(subjects_en[subject])
    bot.send_message(ID, 'اختر المادة يلي تبي تصلحها', reply_markup=markup)
    bot.register_next_step_handler(message, review_homework_handler)


def review_homework_handler(message):
    if not (message.text in subjects_en.values()):
        send_welcome(message)
        return
    subject = get_dictkey(subjects_en, message.text)
    ID = message.from_user.id
    grp = db.get_info('grp',ID)
    markup = types.ReplyKeyboardMarkup()
    markup.add(right_btn, wrong_btn)
    unis = db.get_givenhomework_uni(subject,grp)
    hws = []
    for uni in unis:
        hws.append(db.review_homework(uni,grp))
    d = {}
    for hw in hws:
        for h in hw:
            d[h[0]] = []
    for hw in hws:
        for h in hw:
            if not (h[2] in d[h[0]]):
                d[h[0]].append(h[2])
    for hw in hws:
        for h in hw:
            d[h[0]].append(types.InputMediaPhoto(h[1]))

    if len(d) != 0:
        data = d[list(d)[0]]
        fileid_array = data[1:]
        person_id = data[0]
        uni = get_dictkey(d, data)
        bot.send_media_group(ID, fileid_array)
        bot.send_message(ID, 'شن رايك؟', reply_markup=markup)
        bot.register_next_step_handler(message, right_wrong_homework, [person_id, subject, message])
        db.remove_given_homework(person_id, uni)
        return
    else:
        bot.send_message(ID, 'تم التصحيح')
        send_welcome(message)


def right_wrong_homework(message, data):
    ID = message.from_user.id
    person_id = data[0]
    subject = subjects_en[data[1]]
    msg = data[2]
    markup = types.ReplyKeyboardRemove(selective=False)
    if message.text == right_btn:
        score = int(db.get_info(data[1], person_id, table='scores')) + 1
        db.update_info(data[1], score, person_id, table='scores')
        bot.send_message(person_id, "واجبك ال{d} صح, زدناك سكور".format(d=subject))
    if message.text == wrong_btn:
        bot.send_message(ID, 'علاش؟', reply_markup=markup)
        bot.register_next_step_handler(message, why_wrong_homework, [person_id, subject, msg])
    else:
        review_homework_handler(msg)


def why_wrong_homework(message, data):
    person_id = data[0]
    subject = data[1]
    msg = data[2]
    reason = message.text
    bot.send_message(person_id, 'واجبك ال{d} كان للأسف غلط, السبب {r}'.format(d=subject, r=reason))
    review_homework_handler(msg)


@bot.message_handler(commands=['sendhw', ])
def send_homework_group(message):
    ID = message.from_user.id
    grp = db.get_info('grp', ID)
    if db.get_info('admin', ID) == 0:
        bot.send_message(ID, 'Unauthorized')
        return
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(ID, 'Wrong Syntax, it is /sendhw subject description')
        return
    subject = args[1]
    info = ' '.join(args[2:len(args)])
    if subject.isdigit():
        bot.send_message(ID, 'Wrong Syntax, it is /sendhw subject group[number]')
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("ايه")
    markup.add("لا")
    bot.send_message(ID, "فيه كيف ترسل صورة للواجب؟", reply_markup=markup)
    bot.register_next_step_handler(message, send_neededhw_photo, [grp, subject, info,None])


def send_neededhw_photo(message, data):
    ID = message.from_user.id
    text = message.text
    if text == "ايه":
        bot.send_message(ID, "اوكي ارسلها")
        bot.register_next_step_handler(message, handle_send_neededhw, data)
        return
    if text == "لا":
        markup=types.ReplyKeyboardMarkup()
        markup.add("لا","ايه")
        bot.send_message(ID,"هل تبي تمسح اي واجب قبل هذا؟",reply_markup=markup)
        bot.register_next_step_handler(message,want_to_delete_past_hws_admin,data)
        return
        db.add_homework_group(grp, subject, info)
        ids = db.get_all_group_ID(grp)
        for i in ids:
            bot.send_message(i, "عندك واجب {s}:".format(s=subjects_en[subject]))
            bot.send_message(i, info)
        send_welcome(message)

def want_to_delete_past_hws_admin(message,data):
    ID = message.chat.id
    text = message.text
    grp = data[0]
    subject = data[1]
    info = data[2]
    fileid = data[3]
    subject_ar = subjects_en[subject]

    if text == "ايه":
        db.remove_givenhomework(grp,subject)
        db.remove_needed_homework_group(grp,subject)

    ids = db.get_all_group_ID(int(grp))
    for i in ids:
        if fileid:
            bot.send_message(i, "عندك واجب {s}:".format(s=subject_ar))
            bot.send_photo(i, fileid, caption=info)
            db.add_homework_group(grp, subject, info, fileid)
        else:
            bot.send_message(i,"عندك واجب {s}, ينص: {i}".format(s=subject_ar,i=info))
            db.add_homework_group(grp, subject, info)
    bot.send_message(ID,"تمام, تم ارسال الواجب لكل الطلبة",reply_markup=types.ReplyKeyboardRemove())
    send_welcome(message)


def handle_send_neededhw(message, data):
    ID = message.from_user.id
    if not (message.content_type == 'photo'):
        bot.reply_to(message, 'لازم ترسل صورة فقط -_-')
        bot.register_next_step_handler(message, handle_send_neededhw, data)
        return
    fileid = message.photo[-1].file_id
    data[3]=fileid
    markup = types.ReplyKeyboardMarkup()
    markup.add("لا", "ايه")
    bot.send_message(ID, "هل تبي تمسح اي واجب قبل هذا؟", reply_markup=markup)
    bot.register_next_step_handler(message, want_to_delete_past_hws_admin, data)
    return



def convert_numbers(numbers):
    dic = {'۰': 0, '١': 1, '٢': 2, '۳': 3, '٤': 4, '٥': 5, '٦': 6, '٧': 7, '٨': 8, '٩': 9}
    if not numbers.isdigit():
        return numbers
    result = ""
    for n in list(str(numbers)):
        if n.isdigit():
            if n in dic:
                result += str(dic[n])
            else:
                result += n
    return result


def process_regid(message):
    ID = message.from_user.id
    regid = message.text
    if message.content_type != "text":
        bot.send_message(ID, "دخل رقم قيدك قلنا, حاول تاني🙂")
        bot.register_next_step_handler(message, process_regid)
        return
    if not regid.isdigit():
        bot.send_message(ID, 'لازم يكون رقم قيدك متكون من ارقام 🙂, اكتبه تاني:')
        bot.register_next_step_handler(message, process_regid)
        return
    if len(regid) != 6:
        bot.send_message(ID,"رقم قيد خطأ🙂, اكتبه ثاني:")
        bot.register_next_step_handler(message, process_regid)
        return
    regid = convert_numbers(regid)
    pw = db.get_info('pw',regid=regid)
    if pw:
        bot.send_message(ID,"هذا المستخدم مسجل من قبل, ادخل الرقم السري: ")
        bot.register_next_step_handler(message,check_password,regid)
        return
    bot.send_message(ID, "اختار رقم سري خاص بيك 🔑:")
    bot.register_next_step_handler(message, handle_user_password,regid)


def check_password(message,regid):
    ID = message.chat.id
    pw = message.text
    upw = db.get_info('pw',regid=regid)
    if pw == upw:
        pID = db.get_info('ID',regid=regid)
        db.update_info('ID',ID,regid=regid)
        bot.send_message(ID,"تمام, تم تسجيل الدخول")
        send_welcome(message)
        markup = types.ReplyKeyboardMarkup()
        markup.add(back_btn)
        bot.send_message(pID,"تم تسجيل خروجك",reply_markup=markup)
        return
    bot.send_message(ID,"رقم سري خاطئ")
    send_welcome(message)
def handle_user_password(message,regid):
    ID = message.chat.id
    password = message.text
    if db.is_registed(regid):
        name = db.get_info('name',regid=regid,table='peoplelist')
        grp = db.get_info('grp',regid=regid,table='peoplelist')
        db.add_person(ID,regid,name,grp,admin=0,pw=password)
        fname = db.get_firstname(ID)
        bot.reply_to(message, "تمام {n} 😄,لقيتك مسجل عندي 😊 رقم قيدك هو {r}, ومجموعتك هي {g}, لو فيه خطأ راجع مع المشرفين 🤠, ان شاء الله نكون مساعد كويس, وبالتوفيق🎓".format(n=fname,r=regid,g=grp))
        send_welcome(message)
        return
    bot.reply_to(message, "شن اسمك الرباعي؟ 👀")
    bot.register_next_step_handler(message, process_name,[regid,password])

def isarabic(t):
    alphabet = ("ابتثجحخدذرزسشصضطظعغفقكلمنهويﻷأإئءؤأإﻷئؤرﻻةىوظزعاشوركمالطلالظزوةئﻻرؤﻻىجدحخعهخحهضغعقفغذ ")
    letters = list(t)
    for l in letters:
        if not (l in alphabet):
            return False
    return True


def process_name(message,data):
    name = None
    ID = message.from_user.id
    try:
        name = message.text
        if message.content_type != "text":
            bot.send_message(ID, "دخل اسمك قلنا!!:")
            bot.register_next_step_handler(message, process_name,data)
            return

        if len(name.split()) != 4:
            bot.send_message(ID, "اسمك الرباعي قلنا 🙂, ابعت اسمك مرة ثانية!")
            bot.register_next_step_handler(message, process_name,data)
            return
        if not isarabic(name):
            bot.send_message(ID, "بالله عاود دخل اسمك بس من غير ايموجيز وبالعربي!")
            bot.register_next_step_handler(message, process_name,data)
            return
        #db.update_info('name', name, ID)
        data.append(name)
        group_keyboard = types.ReplyKeyboardMarkup()
        group_keyboard.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11')
        msg = bot.send_message(ID, "اوكي {n}, اخر حاجة اعطيني في اي مجموعة انت؟:♎".format(n=db.get_firstname(ID)),
                               reply_markup=group_keyboard)
        bot.register_next_step_handler(msg, process_group,data)
    except Exception as e:
        bot.reply_to(message, e)


def process_group(message,data):
    group = None
    ID = message.from_user.id
    try:
        group = message.text
        if (not group.isdigit()) or message.content_type != "text":
            bot.send_message(ID, "بالله اختار من القائمة")
            bot.register_next_step_handler(message, process_group,data)
            return
        #db.update_info('grp', group, ID)
        regid = data[0]
        password = data[1]
        name = data[2]
        group = data[2]
        db.add_person(ID,regid,name,group,admin=0,pw=password)
        bot.reply_to(message, "تو هكي انت تمام التمام 😄 ان شاء الله نكون مساعد كويس, وبالتوفيق🎓")
        send_welcome(message)
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=['alert', ])
def manage_alert(message, text=None):
    if not text:
        text = message.text.replace('/alert ', '')

    ID = message.from_user.id
    admin = db.get_info('admin', ID)
    if admin < 1:
        bot.send_message(ID, 'Unauthorized')
        return
    elif admin == 1:
        group = db.get_info('grp', ID)
        ids = db.get_all_group_ID(group)
        bot.send_message(ID, "تم!")
        for i in ids:
            if i == ID:
                continue
            name = db.get_firstname(i)
            text = text.replace('عبود', name)
            bot.send_message(i, text)
        send_welcome(message)


@bot.message_handler(commands=['setadmin', ])
def set_admin(message):
    try:
        text = message.text
        regid = text.split()[1]
        password = text.split()[2]
        if password == PASSWORD:
            db.update_info('admin', 1, regid=regid)
            person_id = db.get_info('ID', regid=regid)
            bot.reply_to(message, 'تمام')
            send_welcome(message)
            bot.send_message(person_id, "تم تعينك كمشرف على مجموعتك")
        else:
            bot.reply_to(message, 'الرقم السري خطأ')
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=['insertgroupregid'])
def insert_group_regid(message):
    ID = message.chat.id
    markup = types.ReplyKeyboardMarkup()
    markup.add("تم")
    bot.send_message(ID,"ابعت بالطالب, اكتب رقم قيده الاول بعدين اسمه الكامل, تأكد من صحة المعلومات ومن انك تدير مسافة بين رقم القيد والأسم, لما تكمل اضغط 'تم'",reply_markup=markup)
    bot.register_next_step_handler(message,get_insert_group_regid)
def get_insert_group_regid(message):
    ID = message.chat.id
    grp = db.get_info('grp',ID)
    text = message.text
    def send_error():
        bot.send_message(ID,"خطأ في الإدخل حاول مرة ثانية")
        bot.register_next_step_handler(message,get_insert_group_regid)
    if text == "تم":
        bot.send_message(ID,"تمامات")
        send_welcome(message)
        return
    if text != None and message.content_type == "text":
        text = text.split()
        if len(text) < 5:
            send_error()
            return
        if not text[0].isdigit() and len(text[0])==6:
            send_error()
            return
        regid = text[0]
        name = ' '.join(text[1:])
        db.register_a_student_in_list(grp,regid,name)
    else:
        send_error()
        return

bot.enable_save_next_step_handlers(delay=5)
bot.load_next_step_handlers()


def translate_weather_code(code):
    def gcode(frm, to):
        return list(range(frm, int(to) + 1))

    w = 'طبيعي'
    code = int(code)
    if code in gcode(0, 6) or code in gcode(37, 39) or code in [41, 42, 43, 45, 46, 47]:
        w = "عاصفي"
    elif code in gcode(7, 18) or code == 40:
        w = "تبشبش"
    elif code in gcode(19, 23):
        w = "مضبب"
    if code == 24:
        w = "رياحي"
    elif code == 25:
        w = "صقع"
    elif code == 26:
        w = "مسحب"
    elif code in [27, 28]:
        w = "شبه بالكامل مسحب"
    elif code in [29, 30, 44]:
        w = "نص مسحب نص لا"
    elif code == 31:
        w = "صافي"
    elif code == 32:
        w = "شميسة"
    elif code in [33, 34]:
        w = "معدل"
    elif code == 35:
        w = "مطر وتبروري"
    elif code == 36:
        w = "سخون"
    return w


def get_weather():
    weather = Weather(unit=Unit.CELSIUS)
    location = weather.lookup_by_location('tripoli')
    return location


def get_now_status(weather):
    return translate_weather_code(weather.condition.code)


def get_now_temp(weather):
    return "["+str(weather.condition.temp)+"]"


def get_tomorrow_status(weather):
    return translate_weather_code(weather.forecast[1].code)


def get_tomorrow_temp(weather):
    return [weather.forecast[1].low, weather.forecast[1].high]

def give_info():
    hour = datetime.now(tz).hour
    day=get_weekday(0)
    groups = db.get_availiabe_groups()
    for grp in groups:
        sched = db.get_day_schedule(grp,day)
        print(sched)
        if sched:
            for sbj in sched:
                start = sched[sbj][0]
                room = sched[sbj][2]
                subject = subjects_en[sbj]
                if start == hour+1:
                    if start > 12:
                        start -= 12
                    ids = db.get_all_group_ID(grp)
                    for i in ids:
                        name = db.get_firstname(i)
                        bot.send_message(i,"{n} استعد لمحاضرة ال{s} الساعة {t} في القاعة {r} 🙃".format(n=name,s=subject,t=start,r=room))
    day = get_weekday(0,1)
    ids = db.get_all_teachers_id()
    for i in ids:
        sched = db.get_info("schedule",i,table='teachers')
        if sched:
            sched = eval(sched)[day]
            if sched != {}:
                for grp in sched:
                    start = int(sched[grp][0])
                    room = sched[grp][2]
                    if start == hour+1:
                        if start > 12:
                            start -= 12
                        bot.send_message(i,"عندك محاضرة الساعة {t} للمجموعة {g} في القاعة {r} 😊".format(g=grp,t=start,r=room))

morning_list =["صباح الخير","صباح النور","صباح الفل","صباح الياسمين","صباح النشاط","صباح التفاؤل"]
morning_list_emojis="🌅🌄🌞☀️🌻😃😊😊🥀🌼💐🌹🌸🌷"

from random import choice

def give_morning_weather():
    ids = db.get_all_students_id()
    ids2 = db.get_all_teachers_id()
    if ids2:
        for idd in ids2:
            if idd:
                ids.append(idd)
    text = choice(morning_list)+" {n} "+choice(morning_list_emojis)
    w = get_weather()
    tmp = get_now_temp(w)
    status = get_now_status(w)
    text2 = "الجو اليوم " + status + " ودرجة الحرارة توا " + tmp
    for i in ids:
        if i != "" and i != None:
            bot.send_message(i,text.format(n=db.get_firstname(i)),disable_notification=True)
            bot.send_message(i, text2,disable_notification=True)
            get_day_info(None,0,i)

@bot.message_handler(regexp=".*")
def handle_any_text(message):
    main_menu_handler(message)
def handle_not_known(message):
    if message.text != "/start" and message.text != back_btn:
        send_welcome(message)
def delete_attendance_record():
    folder = './files/qrcodes/users/'
    filelist = [f for f in os.listdir(folder)]
    if len(filelist) > 2000:
        for file in filelist:
            os.remove(folder+file)
schedule.every().hour.at('05:00').do(give_info)
schedule.every().day.at('04:58').do(give_morning_weather)
bot.threaded=False
while True:
    try:
        schedule.run_continuously()
        bot.polling(none_stop=True,interval=1)
    except Exception as e:
        bot.send_message(MID,e)
        time.sleep(5)