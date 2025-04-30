"""
API Steps for Customers

Steps file for api_customer.feature that uses Flask test client.
"""

from behave import given, when, then
from service.models import Customer, db


@given('the following customers')
def step_impl(context):
    """Clear existing customers and add new ones"""
    with context.flask_app.app_context():
        db.session.query(Customer).delete()
        db.session.commit()

    for row in context.table:
        payload = {
            "name": row["name"],
            "address": row["address"],
            "email": row["email"],
            "phonenumber": row["phonenumber"],
        }
        context.response = context.app.post("/customers", json=payload)
        assert context.response.status_code == 201


@when('I create a customer with name "{name}" and email "{email}"')
def step_impl(context, name, email):
    """Send POST request to create a customer"""
    payload = {
        "name": name,
        "email": email,
        "address": "Default Address",
        "phonenumber": "000-000-0000"
    }
    context.response = context.app.post("/customers", json=payload)
    assert context.response.status_code == 201
    context.created_customer = context.response.get_json()


@then("the customer should be saved in the database")
def step_impl(context):
    """Confirm that customer exists in the database"""
    customer_id = context.created_customer["id"]
    context.response = context.app.get(f"/customers/{customer_id}")
    assert context.response.status_code == 200
    data = context.response.get_json()
    assert data["name"] == context.created_customer["name"]
    assert data["email"] == context.created_customer["email"]


@when("I request all customers")
def step_impl(context):
    """Send GET request to list all customers"""
    context.response = context.app.get("/customers")
    assert context.response.status_code == 200


@then("the response should contain {count:d} customers")
def step_impl(context, count):
    """Check the number of customers returned"""
    customers = context.response.get_json()
    assert isinstance(customers, list)
    assert len(customers) == count


@given('I have a customer named "{name}"')
def step_impl(context, name):
    """Find a customer by name and save ID"""
    context.response = context.app.get("/customers")
    customers = context.response.get_json()
    for customer in customers:
        if customer["name"] == name:
            context.customer_to_delete = customer
            return
    assert False, f"Customer with name {name} not found"


@when("I delete that customer")
def step_impl(context):
    """Send DELETE request to delete a customer"""
    customer_id = context.customer_to_delete["id"]
    context.response = context.app.delete(f"/customers/{customer_id}")
    assert context.response.status_code == 204


@then("the customer should no longer exist")
def step_impl(context):
    """Verify the customer is gone"""
    customer_id = context.customer_to_delete["id"]
    context.response = context.app.get(f"/customers/{customer_id}")
    assert context.response.status_code == 404
