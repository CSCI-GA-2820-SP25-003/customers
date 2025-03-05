"""
Models for Customer

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    address = db.Column(db.String(256))
    email = db.Column(db.String(50))
    phonenumber = db.Column(db.String(25))

    # Todo: Place the rest of your schema here...

    def __repr__(self):
        return f"<Customer {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Saving %s", self.name)
        if self.id is None:
            raise DataValidationError("Cannot update a customer with no ID")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "phonenumber": self.phonenumber,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if not isinstance(data["name"], str):
                raise DataValidationError(
                    "Invalid type for [name]: " + str(type(data["name"]))
                )
            self.name = data["name"]

            if not isinstance(data["address"], str):
                raise DataValidationError(
                    "Invalid type for [address]: " + str(type(data["address"]))
                )
            self.address = data["address"]

            if not isinstance(data["email"], str):
                raise DataValidationError(
                    "Invalid type for [email]: " + str(type(data["email"]))
                )
            self.email = data["email"]

            if not isinstance(data["phonenumber"], str):
                raise DataValidationError(
                    "Invalid type for [phonenumber]: " + str(type(data["phonenumber"]))
                )
            self.phonenumber = data["phonenumber"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_address(cls, address):
        """Returns all Customers with the given address

        Args:
            address (string): the address of the Customers you want to match
        """
        logger.info("Processing address query for %s ...", address)
        return cls.query.filter(cls.address == address)

    @classmethod
    def find_by_email(cls, email):
        """Returns all Customers with the given email

        Args:
            email (string): the email of the Customers you want to match
        """
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_phonenumber(cls, phonenumber):
        """Returns all Customers with the given phonenumber

        Args:
            phonenumber (string): the phonenumber of the Customers you want to match
        """
        logger.info("Processing phonenumber query for %s ...", phonenumber)
        return cls.query.filter(cls.phonenumber == phonenumber)
