

## Project Overview

This is a team ERP project built with a **plugin architecture** — each team member owns one self-contained Django app (plugin). The system covers customer order placement, admin validation, production management, and warehouse reporting gooods.

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ERP_Mini_project
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (Required for local Django admin access)
Note: Each team member must run this locally to view and manage models in the browser.

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`

---


## Git Workflow

Each member works on their own branch and **never edits another member's plugin folder**.

```bash
# create your branch
git checkout -b feature/your-plugin-name

# work on your plugin only
git push origin feature/your-plugin-name

# open a pull request to merge into main
```

**Shared files** (`config/settings.py`, `config/urls.py`, `core/`) should only be edited by agreement with the whole team.

---

## Adding a New Migration

After changing your plugin's `models.py`:

```bash
python manage.py makemigrations your_plugin_name
python manage.py migrate
```

Always commit your migration files — teammates need them to keep their local database in sync.

---

## Running Tests

```bash
# run all tests
python manage.py test

# run tests for one plugin only
python manage.py test plugins.orders_plugin
```



## Functional Requirements Summary

## Customer

1. Can create an account by registering on the platform.
2. Can place an order and select their customer grade (1st grade, 2nd grade, or 3rd grade).

## Admin

3. Can view all orders placed by customers and validate them.
4. Can detect and validate urgent orders. An order is considered urgent when the quantity ordered does not match the customer's grade for example, a 3rd grade customer ordering a 1st grade quantity.
6. Can set discounts for premium customers. A customer becomes premium after placing at least 7 orders with a total cumulated value of 3,000,000 XAF or more, and receives a 4% discount on subsequent orders.
7. Can view the warehouse contents and browse each product in stock.
8. Can generate reports covering orders, production activity, and supplier information.

Product Manager

9. Can initiate a production order with a priority level: Low, Urgent, or Out-of-stock.
10. Can initiate a delivery with a status of either In-Stock or Urgent.
11. Can view the stock status of any product or raw material, including whether it is out of stock.
12. Can track the exact quantity of materials required to produce a given product.
13. Can update product information such as quantities produced.

## All Users

14. Can log in to the platform using their credentials

---

## Team Module Assignments

1. **User management + Final integration**: Gloria (`users_plugin`)
2. **Inventory management**: Paho Tchaptchet (`inventory_plugin`)
3. **Order management**: Mbiangoupii Ngoba Reine (`orders_plugin`)
4. **Notification management**: Joky Diane (`notifications_plugin`)
5. **MRP module + Production module**: Tankeu Ndosse Franck (`mrp_production_plugin`)