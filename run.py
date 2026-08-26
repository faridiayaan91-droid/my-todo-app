from app import create_app, db
from app.models import User, Task

application = create_app()
with app.app_context():
    db.create_all()
    # Default admin auto-create
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='1234')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
