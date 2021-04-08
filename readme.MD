# Sellit

Sell It is an all-in-one payment processing and e-commerce solution. Accept payments, sell digital products from your own and more, do it all with a single platform. Sellit is currently in development. Some functions may not work or be created yet.

## Setup

To setup Sellit, first you will need to clone this repository. Once cloned, you need to set the following environmental variables:

* ENVIROMENT - Set to DEV if testing locally. PRODUCTION if you plan to host Sellit online
* SITE_URL - Set your localpath or domain. This is required so subdomains work.
* BRAND_NAME - Set the name you want to call the website. Sellit for example.
* DB_PATH - The full path to your mySQL database. Example: mysql://root:password@localhost/sellit
* SMTP_EMAIL - Google Email address
* SMTP_PASSWORD - Google password
* S3_ACCESS - Amazon AWS access key
* S3_KEY - Amazon key
* PP_CLIENT - PayPal client token
* PP_secret - PayPal secret key
* BROKER_URL - The url for your redis server. Example: redis://localhost:6379/0
* STRIPE_PUB_KEY - Stripe public Key
* STRIPE_SECRET - Stripe secret key
* CP_PUBLIC - CoinPayments public key
* CP_PRIVATE - CoinPayments secret key
* AWS_PRODUCT_IMAGES - AWS bucket name for product images
* AWS_PROFILE_AVATARS - AWS bucket name for profile avatars
* AWS_ATTACHMENTS - AWS bucket name for product attachments
* AWS_SOLD_ATTACHMENTS - AWS bucket name for product attachments sold
* AUTHORISED_IP - IP authorised to access auth/dash if you deploy the app

Next, you need to change your public key for stripe inside app/static/scripts/main.js : Line 278

## How to file a bug

1. Go to our [Issue Tracker](https://github.com/MrNaughtZero/sellit/issues) on GitHub
2. Search for existing issues using the search field at the top of the page
3. File a new issue including as many details as much, including how to reproduce the bug.