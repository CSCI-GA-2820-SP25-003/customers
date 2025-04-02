######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Customer REST API Service",
            version="1.0",
            paths=url_for("list_customers", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW customer
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Create a Customer
    This endpoint will create a customer based the data in the body that is posted
    """
    app.logger.info("Request to Create a customer...")
    check_content_type("application/json")

    customer = Customer()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    # Save the new customer to the database
    customer.create()
    app.logger.info("customer with new id [%s] saved!", customer.id)

    location_url = url_for("get_customers", customer_id=customer.id, _external=True)
    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# LIST ALL CUSTOMERS
######################################################################


@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""
    app.logger.info("Request for customer list")

    customers = []

    # Parse any arguments from the query string
    customer_id = request.args.get("id")
    name = request.args.get("name")
    address = request.args.get("address")
    email = request.args.get("email")
    phonenumber = request.args.get("phonenumber")

    if customer_id:
        app.logger.info("Find by id: %s", customer_id)
        customers = Customer.find(customer_id)
    elif name:
        app.logger.info("Find by name: %s", name)
        customers = Customer.find_by_name(name)
    elif address:
        app.logger.info("Find by address: %s", address)
        # create bool from string
        customers = Customer.find_by_address(address)
    elif email:
        app.logger.info("Find by email: %s", email)
        # create enum from string
        customers = Customer.find_by_email(email)
    elif phonenumber:
        app.logger.info("Find by phonenumber: %s", phonenumber)
        # create enum from string
        customers = Customer.find_by_phonenumber(phonenumber)
    else:
        app.logger.info("Find all")
        customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer

    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to Update a customer with id [%s]", customer_id)
    check_content_type("application/json")

    # Attempt to find the Customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    # Update the Customer with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    # Save the updates to the database
    customer.update()

    app.logger.info("Customer with ID: %d updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# READ A Customer
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

    # Attempt to find the Customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info("Returning customer: %s", customer.name)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to Delete a customer with id [%s]", customer_id)

    # Delete the Customer if it exists
    customer = Customer.find(customer_id)
    if customer:
        app.logger.info("Customer with ID: %d found.", customer.id)
        customer.delete()

    app.logger.info("Customer with ID: %d delete complete.", customer_id)
    return {}, status.HTTP_204_NO_CONTENT

######################################################################
# ACTION ENDPOINT: PERFORM AN ACTION ON A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/action", methods=["POST"])
def action_customer(customer_id):
    """
    Perform an action on a customer record.
    Supported actions: suspend

    Example Request JSON:
    {
      "action": "suspend"
    }
    """
    app.logger.info("Request to perform an action on customer with id [%s]", customer_id)
    # Ensure the request has the correct content type
    check_content_type("application/json")
    
    # Lookup the customer
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found."
        )
    
    # Get the action from the JSON body
    data = request.get_json()
    action = data.get("action", "").lower() if data else ""
    
    # Process the supported action(s)
    if action == "suspend":
        app.logger.info("Suspending customer with id [%s]", customer_id)
        # Here you would update a status flag in the database
        # e.g., customer.status = "suspended" followed by customer.update()
        # For now we simulate the action by returning the customer data with an action key.
        result = customer.serialize()
        result["action"] = "suspended"
        return jsonify(result), status.HTTP_200_OK
    else:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Action '{action}' is not supported."
        )

