# TODO

## Admin Dashboard
- [x] Add ability for admin to delete user. 
- [x] Add ability for admin to approve service professionals and also view their docs
- [x] View Profile of Service Professionals individually (use a modal to populate professional's info, and put a view profile button next to edit and delete buttons in user management only for the professionals)
- [x] Add ability to search all users (except admins) in User Management modal
- [x] Add ability to view docs when professional profile is being viewed from user management modal
## Customer
- [x] Build Customer Dashboard with search bar showing all the services available
- [x] Create or delete service request.
- [x] Edit an existing service **request** - e.g. date_of_request
- [x] Post reviews
- [ ] Add fade effect to the flash
- [x] Add live search functionality to search for services by name
- [x] Add live search functionality to search for services by pincode
- [x] Fix live search bug where card.innerHTML is not being recongnized by the dom but is showing
- [x] Once a service request to a specific professional has been made, that professional cannot be booked again until the current service request to him temrinates.
## Service Professional
- [x] Add Card for Service Requests on Service Professional Dashboard.
- [x] Add Backend support for service request creation by customer and acceptance by professional.
- [x] Handle rejection from Admin and ability to reapply for the role

## Other
- [ ] Check the validity of a pin number using some python package or javascript
- [ ] what if two users sign up with the same phone number? that cannot be possible. Therefore, we need to verify during signup process whether entered phone number already exists in User Table or not.
- [ ] Add the ability to check whether all the professionals who has a certain preferred service is unavailable. If so, make that service inactive.


# Improvements that should be added later on
- [x] Add description field if the user signing up is a service professional
- [x] Add Block user functionality in the backend (users.py)
- [ ] Add aesthetics using CSS