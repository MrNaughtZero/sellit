# TODO LIST

1. set fore checks
2. ~~Make sure user is at least 13 years~~
3. ~~Create 404 / method not allows pages etc~~
4. ~~Check all emails are asynced~~
5. ~~Add total lines to items~~
6. ~~Add option to remove duplicates when user enters their product items~~
7. ~~Make queries on coupons case sensitive~~
8. Reconstruct DB - normalize
9. Reconstruct vars inside DB to max lengths
10. Setup risk level for stripe based on users settings
11. ~~Create notification settings inside user settings~~
12. ~~Validate email/ip on blacklist~~
13. Create global blacklist of known fraudulent emails -> advanced fraud shield
14. ~~Change keywords on add_donation to price~~
15. ~~Allow expiration of download file~~
16. Change PayPal create order to HTTPS // only when in Production
17. ~~Add max file size to attachment dependent on the member role~~
18. ~~When user is a leaving feedback create a tracking hash and store as cookie. If user visits link, and no hash exists -> regenerate -> send email for them to click; else return 404~~
19. When user is accessing their ticket, create tracking hash and compare to DB. Return 404 if not
20. Create notification system
21. Create WAF system : maybe use 3rd party
22. Load tickets and recent orders on dashboard
23. Check all pages are displaying the correct flashed messages
24. Load tinymce locally; remove CDN
25. Fix download file attachment issue; attachment_name needs renaming
26. Fix start_date on edit coupon page
27. Show orders on order page
28. Create order details page
29. Create analytics page - chart.js or highcharts maybe
30. Show reviews in review page
31. Fix avatar_name on settings page
32. Find API for BTC, ETH, LTC - avoid bitpay: maybe self hosted solution????
33. Check http methods. Some post can be changed to put
34. Make sure malicious users can’t abuse any get methods; checking coupon code on the product page for example. More than likely will have to change this
35. Allow Pro/Business users to enable cart. So instead of the buyer purchasing one product at once, they can purchase multiple
36. Create feature to allow Business users make a request to have their negative feedback reviewed; proof will have to be submitted.
37. Create membership types and start restricting what each member can do; custom login_decorator for each member rank
38. Create admin panel
39. Allow users to edit the css/js on their shop page
40. Allow users to download PDF of their sales
41. Creating ranking system to show the seller what rank they are out of all sellers on the platform
42. Create seller verification system; blue tick
43. Create live chat system; for Pro/Business users : try and figure out if google translate api can be used to automatically translate messages for foreign users
44. Figure out how to allow sellers to link their custom domain
45. Restrict donations to Pro/Business users
46. Integrate cash app for Business users // try find other payments methods too
47. Allow users to set a custom message. So when a buyer goes to their shop, a small block appears with the sellers message
48. Create api
49. Create docs for api
50. Try break the site
51. Create python scripts to replicate what the user does. Try to bypass any restrictions
52. Add rate limiting
53. Temp block IP’s that are caught for 24 hours
54. Redesign front and back. Maybe use a 3rd party css processor. Currently there is thousands of lines of CSS. A lot of repetition like buttons, forms, inputs etc
55. Refactor all code. There is a lot that can be removed/changed. TO BE DONE LAST