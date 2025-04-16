Feature: The customer service back-end
    As a online shop owner
    I need a RESTful catalog service
    So that I can keep track of all my customer

Background:
    Given the following customers
        | name       | address         | email                | phonenumber     |
        | Albert     | 4000 Penn Ave   | albert@gmail.com     | 212-123-4567    |
        | Ben        | 44 West 4th St  | ben@outlook.com      | 212-309-3131    |
        | Carol      | 1 Wall Street   | Carol@stern.nyu.edu  | 601-932-2222    |
        | Shmoo Moo  | 611 5th Ave     | Dillan@nyu.edu       | 714-888-8888    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Eileen"
    And I set the "Address" to "50 Broadway St"
    And I set the "Email" to "eileen@gmail.com"
    And I set the "Phonenumber" to "999-888-7777"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Address" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"    
    And I should see "Eileen" in the "Name" field
    And I should see "50 Broadway St" in the "Address" field
    And I should see "eileen@gmail.com" in the "Email" field
    And I should see "999-888-7777" in the "Phonenumber" field

Scenario: Query a Customer by Name
    When I visit the "Home Page"
    And I set the "Name" to "Albert"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Albert" in the "Name" field
    And I should see "4000 Penn Ave" in the "Address" field
    And I should not see "Ben" in the results

Scenario: Query a Customer by Email
    When I visit the "Home Page"
    And I set the "email" to "ben@outlook.com "
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Ben" in the "Name" field
    And I should see "44 West 4th St" in the "Address" field
    And I should not see "Albert" in the results

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Albert"
    And I press the "Search" button
    Then I should see "Albert" in the "Name" field

    When I change the "Address" to "500 Broadway St"
    And I press the "Update" button
    Then I should see the message "Success"
    And I should see "500 Broadway St" in the "Address" field