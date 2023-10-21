# WeedX 


**Link to live version - [WeedX](https://www.weedx.io)**

WeedX is a e-commerce web Websitelication that allows users to search for products stored in database, add them to shopping cart and then make payment using Stripe. Website has login system functionality. The guest user is able to browse, search and add product to cart only. Checkout and payment option is available for registerd users.


## Features

The Website can be accessible with or without user registration, but in that case some features will be available after registration only (checkout,wishlist).
Anyone is able to perform search, view results, all details about selected product, add product to cart, view and modify product on cart page.

#### Existing Features

- search bar - allows user to search product by keyword. Return all products where search keywords Websiteears
- login/register system - allows user access full Website functionality
- logout
- back to top arrow - scrolling to top of page
- flash messages Websiteerars after user login/registration, add/update/delete and purchase product (disWebsiteears after 5s)
- after adding product to cart small badge with product quantity Websiteears on menubar beside cart icon
- short product info cards on homepage
- function preventing access restricted page(checkout) without registration/login


## Technologies used

- **[GitHub](https://github.com/)** - provides hosting for software development version control using Git.
- **[Git](https://git-scm.com/)** - version-control system for tracking changes in source code during software development.
- **[Python](https://www.python.org/)** - programming language.
- **[HTML5](https://en.wikipedia.org/wiki/HTML5)** - standard markup language for creating Web pages.
- **[CSS3](https://en.wikipedia.org/wiki/Cascading_Style_Sheets#CSS_3)** - used to define styles for Web pages, including the design, layout and variations in display for different devices and screen sizes.
- **[VS Code](https://code.visualstudio.com/)** - code editor redefined and optimized for building and debugging modern web and cloud Websitelications.
- **[Bootstrap 4](https://getbootstrap.com/)** - free and open-source CSS framework directed at responsive, mobile-first front-end web development.
- **[AWS S3](https://aws.amazon.com/)** - service offered by Amazon Web Services that provides object storage through a web service interface.
- **[Django](https://docs.djangoproject.com/en/1.11/)** - a Python-based free and open-source web framework, which follows the model-template-view architectural pattern.
- **[Django REST framework](https://www.django-rest-framework.org/)** - Django REST framework is a powerful and flexible toolkit for building Web APIs.
- **[AWS ec2](https://aws.amazon.com/)** - service offered by Amazon Web Services that provides secure, resizable compute capacity in the cloud.

### Manual testing

Manual testing was performed by clicking every element on page which can be clicked.

1) Search form

   - Available all the time on menubar
   - Try to submit empty form and verify that an error message about required fields Websiteear - form doesn't have required attribute. After submiting returning page with all available products.
   - Try to submit the form with valid input and verify that a success message Websiteears (after entering keyword user is redirected to results page and the product matches searching criteria are displayed)

2) Login form page

   - Go to Homepage page
   - Click Log in link on navigation bar (user is redirected to login page)
   - Try to submit empty form and verify that an error message about required fields Websiteear(required field message Websiteears)
   - Try to submit the form with valid input and verify that a success message Websiteears (user is redirected to homepage with successful login message)
   - Try to submit the form with invalid input and verify that a error message Websiteears (_Your username or password is incorrect_ message Websiteears)

3) Registration form page

   - Go to Homepage page
   - Click Log in link on navigation bar (user is redirected to registration page)
   - Click _Create account_ button below the login form
   - Try to submit empty form and verify that an error message about required fields Websiteear (required field message Websiteears)
   - Try to submit the form with valid input and verify that a success message Websiteears (user is redirected to homepage with success message)
   - Try to submit the form with invalid input and verify that a error message Websiteears (_Unable to register your account_ message Websiteears)
   - Click _Sign In_ under _Create account_ button (user is redirected to login page with success message)

4) Add to cart form

   - Go to Product details page
   - Try to submit empty form and verify that an error message about required fields Websiteear (required message Websiteears)
   - Try to submit the form with valid input and verify that a success message Websiteears (_Item added to your cart. View cart_ message Websiteears)
   - Try to submit the form with invalid input and verify that a error message Websiteears.(field has html5 type _number_ attribute and initial default value 1 preventing entering invalid input)

5) Cart form

   - Go to the Cart page
   - Try to submit empty form and verify that an error message about required fields Websiteear (required message Websiteears)
   - Try to submit the form with valid input and verify that a success message Websiteears (_Cart updated_ message Websiteears)
   - Try to submit the form with invalid input and verify that a error message Websiteears (field has html5 type _number_ attribute preventing entering invalid input and also has initial value number of the specific item, which was selected on _add to cart_ page)
   - Click _Trash_ icon - item is deleted from cart (message Websiteears)
   - Click _Shoppig_ button (user is redirected to products page (homepage))
   - Click _Checkout_ button (user is redirected to checkout page)



6) Scrolling up and down all the pages

   - Project was manually tested in all the major browsers including Google Chrome, Safari and Internet Explorer to confirm compatibility. The tests were conducted in virtual mode using the google developer tools and also physical mobile phones such us: Samsung Galaxy Note 9, Htc One S, Samsung A20. Website looks consistent and works well on different browsers and screen sizes.


## Deployment

The project was developed, committed to git and pushed to GitHub using Visual Studio Code IDE.

##### Clone in GitHub

1. Open the [e-commerce](https://github.com/AnshumanSelnox/BackwoodAroma.git) repository.
2. Click the _Clone or download_ button.
3. In the _clone with HTTPs_ pop-up, click the _copy icon_.
4. Open git bash in your IDE.
5. Change the current working directory to where you want the cloned directory to be made.
6. Type _git clone_ and paste the URL copied earlier.
7. Press enter.
8. Repository is copied.

##### IDE Development Setup

1. Create a virtual environment for your Python project.
2. Create a env.py file in the root project folder.
3. Add the following variables to the env.py file:

   os.environ.setdefault['SECRET_KEY']

   os.environ.setdefault['STRIPE_PUBLISHABLE']

   os.environ.setdefault['STRIPE_SECRET']

   os.environ.setdefault['AWS_ACCESS_KEY_ID']

   os.environ.setdefault['AWS_SECRET_ACCESS_KEY']

   os.environ.setdefault['DATABASE_URL']

4. Use _pip install -r requirements.txt_ to install Python required modules.

For security reason the environment variables were set in a separate file env.py and are referenced by os.environ.get("KEY", "name"). Stripe account need to be set up to obtain testing keys. AWS S3 account is used for hosting media and static files.



#### Acknowledgements

- I received inspiration for this project through internet research. I visited websites such as [Weedmaps](https://weedmaps.com/), [Sweede](https://sweede.io/), [leafly](https://www.leafly.com/) and watched youtube tutorials, which helped me to put all the pieces together.
