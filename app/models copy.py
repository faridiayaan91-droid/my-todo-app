from app import db
class Task(db.Model):
    id = db.column(db.Integar,primary_key = True)
    title = db.column(db.String(100),nullable= False)
    status= db.column(db.String(20),defoult = "pending")
    