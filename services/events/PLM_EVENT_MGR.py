import mysql.connector

def PLM_EVENT_ADD(event):

    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="LightEos27.6",
        database="tension_cosmos"
    )

    cursor = db.cursor()
    sql = "INSERT INTO events (`severity`,`application`,`module`,`name`,`message`) VALUES (%s, %s, %s, %s, %s)"
    values = (event["severity"], event["application"], event["module"], event["name"], event["message"])
    cursor.execute(sql,values)
    db.commit()




