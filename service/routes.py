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

import secrets
from functools import wraps
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Customer
from service.common import status  # HTTP Status Codes


# Document the type of authorization required
authorizations = {"apiKey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}}

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customer Demo REST API Service",
    description="This is a sample Customer REST API Service.",
    default="customers",
    default_label="Customer Operations",
    doc="/apidocs",
    authorizations=authorizations,
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


# Define models for documentation with Flask-RestX
create_model = api.model(
    "Customers",
    {
        "id": fields.Integer(
            readonly=True, description="The unique identifier for the customer"
        ),
        "name": fields.String(
            required=True,
            description="The name of the customer",
            example="John Smith",
        ),
        "address": fields.String(
            required=True,
            description="The address associated with customer",
            example="145 Lafayette",
        ),
        "email": fields.String(
            required=True,
            description="The email of the customer",
            example="johnsmith@gmail.com",
        ),
        "phonenumber": fields.Integer(
            required=True,
            description="The phone number of the customer",
            example=7479264929,
        ),
        "blocked": fields.Integer(
            required=True,
            description="The active status of the customer (New, Used, Opened, Refurbished)",
            enum=[
                "True",
                "False",
            ],
            example="True",
        ),
    },
)

customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "name", type=str, required=False, help="List Customers by name"
)
customer_args.add_argument(
    "address", type=str, required=False, help="List Customers by address"
)
customer_args.add_argument(
    "email", type=str, required=False, help="List Customers by email"
)
customer_args.add_argument(
    "phonenumber", type=str, required=False, help="List Customers by phone number"
)
customer_args.add_argument(
    "blocked", type=str, required=False, help="List Customers by status"
)


######################################################################
# Authorization Decorator
######################################################################
def token_required(func):
    """Decorator to require a token for this endpoint"""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if "X-Api-Key" in request.headers:
            token = request.headers["X-Api-Key"]

        if app.config.get("API_KEY") and app.config["API_KEY"] == token:
            return func(*args, **kwargs)

        return {"message": "Invalid or missing token"}, 401

    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route("/customer/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer{id} - Returns a Customer with the id
    PUT /customer{id} - Update a Customer with the id
    DELETE /customer{id} -  Deletes a Customer with the id
    """

    ######################################################################
    # UPDATE AN EXISTING CUSTOMER
    ######################################################################
    # @app.route("/customers/<int:customer_id>", methods=["PUT"])
    @api.doc("update_customers", security="apikey")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def update_customers(self, customer_id):
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
        data = api.payload
        app.logger.info("Processing: %s", data)
        customer.deserialize(data)

        # Save the updates to the database
        customer.update()

        app.logger.info("Customer with ID: %d updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    ######################################################################
    # READ A Customer
    ######################################################################
    # @app.route("/customers/<int:customer_id>", methods=["GET"])
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get_customers(self, customer_id):
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
        return customer.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A CUSTOMER
    ######################################################################
    # @app.route("/customers/<int:customer_id>", methods=["DELETE"])
    @api.doc("delete_customers", security="apikey")
    @api.response(204, "Customer deleted")
    def delete_customers(self, customer_id):
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
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    ######################################################################
    # LIST ALL CUSTOMERS
    ######################################################################

    @api.doc("list_customers")
    @api.expect(customer_args, validate=False)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers unless a query parameter is specified"""
        app.logger.info("Request to list Customers...")
        customers = []
        args = customer_args.parse_args()
        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            customers = Customer.find_by_name(args["name"])
        elif args["address"]:
            app.logger.info("Filtering by address: %s", args["address"])
            customers = Customer.find_by_address(args["address"])
        elif args["email"] is not None:
            app.logger.info("Filtering by email: %s", args["email"])
            customers = Customer.find_by_email(args["email"])
        elif args["phonenumber"] is not None:
            app.logger.info("Filtering by phone number: %s", args["phonenumber"])
            customers = Customer.find_by_phonenumber(args["phonenumber"])
        else:
            app.logger.info("Returning unfiltered list.")
            customers = Customer.all()

        app.logger.info("[%s] Pets returned", len(customers))
        results = [customer.serialize() for customer in customers]
        return results, status.HTTP_200_OK

    ######################################################################
    # CREATE A NEW customer
    ######################################################################
    @api.doc("create_customers", security="apikey")
    @api.expect(create_model)
    @api.response(400, "The posted data was not valid")
    @api.response(201, "Customer created successfully")
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer")
        customer = Customer()
        app.logger.debug("Payload = %s", api.payload)
        customer.deserialize(api.payload)
        customer.create()
        app.logger.info("Customer with new id [%s] saved!", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# ACTION ENDPOINT: PERFORM AN ACTION ON A CUSTOMER
######################################################################


@api.route("/customers/<int:customer_id>/suspend", methods=["POST"])
@api.param("customer_id", "The Customer identifier")
def action_customer(customer_id):
    """
    Perform an action on a customer record.
    Supported action: suspend

    Example Request JSON:
    {
      "action": "suspend"
    }
    """
    app.logger.info("Performing action on customer with id [%s]", customer_id)
    check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND, f"Customer with id '{customer_id}' not found.")

    data = request.get_json()
    action = data.get("action", "").lower() if data else ""

    if action == "suspend":
        app.logger.info("Suspending customer with id [%s]", customer_id)
        result = customer.serialize()
        result["action"] = "suspended"
        return result, status.HTTP_200_OK
    abort(status.HTTP_400_BAD_REQUEST, f"Action '{action}' is not supported.")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


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
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK
