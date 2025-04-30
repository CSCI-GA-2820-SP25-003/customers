Feature: Customer Service API
  As a developer
  I want to test the customer REST API
  So that I can validate core functionality works without the UI

  Background:
    Given the following customers
      | name   | address       | email               | phonenumber   |
      | Alice  | 10 Park Ave   | alice@mail.com      | 123-456-7890  |
      | Bob    | 20 5th Ave    | bob@gmail.com       | 222-333-4444  |

  Scenario: Create a new customer via API
    When I create a customer with name "Eve" and email "eve@openai.com"
    Then the customer should be saved in the database

  Scenario: Retrieve all customers via API
    When I request all customers
    Then the response should contain 2 customers

  Scenario: Delete a customer via API
    Given I have a customer named "Alice"
    When I delete that customer
    Then the customer should no longer exist
