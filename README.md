
---

## 🚀 Getting Started

Set up and run this project locally in a few steps.

### ✅ Prerequisites

- Python 3.10+
- pip
- Git
- virtualenv (recommended)
- PostgreSQL

---

```bash
git clone https://github.com/sardor-an/Auth-system-practice-1.git
cd ./Auth-system-practice-1
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Now open your browser: http://127.0.0.1:8000/
