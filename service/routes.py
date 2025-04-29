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
Customer Service with Swagger

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, Api
from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customer Demo REST API Swagger Service",
    description="This is a Customer server.",
    default="customers",
    default_label="Customer service operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return {"message": "Healthy"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Customer",
    {
        "name": fields.String(
            required=True,
            description="The name of the customer.",
            example="Albert",
        ),
        "email": fields.String(
            required=True,
            description="The email of of the customer.",
            example="albert@nyu.edu",
        ),
        "address": fields.String(
            required=True,
            description="The address of of the customer.",
            example="nyu101",
        ),
        "phonenumber": fields.Integer(
            required=True,
            description="The phonenumber of the customer",
            example="9999999999",
        ),
    },
)

# Define the API model for Customer
customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.Integer(
            description="A unique identifier for the customer, generated automatically.",
            readOnly=True,
        ),
    },
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "customer_id",
    type=int,
    location="args",
    required=False,
    help="List Customers by customer id",
)
customer_args.add_argument(
    "name", type=str, location="args", required=False, help="List Customers by name"
)
customer_args.add_argument(
    "address",
    type=str,
    location="args",
    required=False,
    help="List Customers by address",
)
customer_args.add_argument(
    "email", type=str, location="args", required=False, help="List Customers by email"
)
customer_args.add_argument(
    "phonenumber",
    type=str,
    location="args",
    required=False,
    help="List Customers by phonenumber",
)


######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route("/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer{id} - Returns a Customer with the id
    PUT /customer{id} - Update a Customer with the id
    DELETE /customer{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on it's id
        """
        app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to Update a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        customer.deserialize(data)
        customer.id = customer_id
        customer.update()
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """
        Delete a Customer

        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to Delete a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()
            app.logger.info("Customer with id [%s] was deleted", customer_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers"""
        app.logger.info("Request to list Customers...")
        customers = []
        args = customer_args.parse_args()

        if args["customer_id"]:
            app.logger.info("Filtering by customer id: %s", args["customer_id"])
            customers = Customer.find(args["customer_id"])
        elif args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            customers = Customer.find_by_name(args["name"])
        elif args["address"]:
            app.logger.info("Filtering by address: %s", args["address"])
            customers = Customer.find_by_address(args["address"])
        elif args["email"]:
            app.logger.info("Filtering by email: %s", args["email"])
            customers = Customer.find_by_email(args["email"])
        elif args["phonenumber"]:
            app.logger.info("Filtering by phonenumber: %s", args["phonenumber"])
            customers = Customer.find_by_phonenumber(args["phonenumber"])
        else:
            app.logger.info("Returning unfiltered list.")
            customers = Customer.all()

        app.logger.info("[%s] Customers returned", len(customers))
        results = [customer.serialize() for customer in customers]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(customer_model)
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
        app.logger.info("Customer with new id [%s] created!", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/{id}/suspend
######################################################################
@api.route("/customers/<customer_id>/action")
@api.param("customer_id", "The Customer identifier")
class SuspendResource(Resource):
    """Suspend action on a Customer"""

    @api.doc("suspend_customers")
    @api.response(404, "Customer not found")
    def put(self, customer_id):
        """
        Suspend a Customer

        This endpoint will suspend a Customer and make it unavailable
        """
        app.logger.info("Request to Suspend a Customer")
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id [{customer_id}] was not found.",
            )

        data = api.payload
        action = data.get("action", "").lower() if data else ""

        if action == "suspend":
            app.logger.info("Suspending customer with id [%s]", customer_id)
            result = customer.serialize()
            result["action"] = "suspended"
            return result, status.HTTP_200_OK

        api.abort(status.HTTP_400_BAD_REQUEST, f"Action '{action}' is not supported.")


######################################################################
# U T I L I T Y     F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
