# 💊 PharmaFlow: Advanced Pharmacy POS & Inventory System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge&logo=htmx&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

**PharmaFlow** is a comprehensive, high-performance Point of Sale (POS) and Inventory Management system built with Django. Designed specifically for retail pharmacy operations, it handles the complexities of batch-specific inventory, real-time POS billing, customer retention, and business analytics.

## ✨ Key Features

### 🛒 1. HTMX-Powered POS Terminal
* **Real-Time Batch Selection:** Live search functionality displays medicine name, batch number, expiry date, and stock count instantly without full page reloads.
* **Smart Recommendations:** Automatically highlights the "BEST" batch to sell based on the closest expiry date to minimize inventory wastage.
* **Atomic Transactions:** Simultaneous stock deduction and invoice generation using Django's atomic transactions to ensure data integrity.

### 📦 2. Advanced Inventory Logic
* **Batch-Specific Tracking:** Moves beyond simple FIFO models to track individual batches and exact expiration dates for every medical item.
* **Critical Alerts:** Automated warnings for low-stock items and soon-to-expire batches on the operational dashboard.

### 👥 3. Customer CRM & Loyalty
* **Patient History Tracking:** Maintains detailed profiles for customers, tracking their order history for refill reminders.
* **Loyalty Program:** Calculates lifetime value and automatically assigns loyalty points for customer retention.

### 📊 4. Business Analytics Dashboard
* **Financial Overviews:** Tracks gross revenue, tax liabilities, and average order value.
* **AI-Driven Insights:** Logic that suggests inventory adjustments based on category sales trends (e.g., "Antibiotics trending up 20%").

## 📸 System Previews


| Operational Dashboard | Business Analytics |
|:---:|:---:|
| <img src="docs/Screenshot 2026-02-03 121418.png" width="400"> | <img src="docs/Screenshot 2026-02-03 121352.png" width="400"> |

| POS Billing Terminal | Invoice Generation |
|:---:|:---:|
| <img src="docs/Screenshot 2026-02-03 121251.png" width="400"> | <img src="docs/Screenshot 2026-02-03 121303.png" width="400"> |

| Customer CRM | Inventory Management |
|:---:|:---:|
| <img src="docs/Screenshot 2026-02-03 121337.png" width="400"> | <img src="docs/Screenshot 2026-02-03 121322.png" width="400"> |

## 🛠️ System Architecture

* **Backend:** Python, Django (Django Models, Forms, ORM, Views)
* **Frontend:** HTML5, HTMX (for dynamic UI updates), Tailwind CSS (responsive design)
* **Database:** SQLite (Development) / PostgreSQL (Production)

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/PharmaFlow.git](https://github.com/your-username/PharmaFlow.git)
   cd PharmaFlow

```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Run database migrations:**
```bash
python manage.py migrate

```


5. **Create a superuser for the admin panel:**
```bash
python manage.py createsuperuser

```


6. **Start the development server:**
```bash
python manage.py runserver

```


*Access the application at `http://127.0.0.1:8000/*`

---

## 👨‍💻 Author

**Ananthu Krishnan** *Backend Developer | Django & Python Specialist*

* **LinkedIn:** [https://www.linkedin.com/in/ananthu-krishnan-5713a6252/]
* **GitHub:** [https://github.com/aanthuu]
