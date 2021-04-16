// product page
let product_price = ''
let product_currency = ''
let email_delivery = ''

if(document.querySelector('#product-price-att')){
    product_price = document.querySelector('#product-price-att').getAttribute('data-product-price');
    product_currency = document.querySelector('#product-currency-att').getAttribute('data-product-currency');
    email_delivery = document.querySelector('#product-email-delivery').getAttribute('data-email-delivery');

    if(document.querySelector('#product-stock').getAttribute('data-product-stock') == '0'){
        document.querySelector('.buy-block-form').innerHTML = 'Out of Stock';
    }

    product_currency = product_currency.replace('GBP', '£')
    product_currency = product_currency.replace('EUR', '€')
    product_currency = product_currency.replace('USD', '$')
}

function updateCost(){
    const per_item = parseFloat(product_price);
    const quantity = parseInt(document.querySelector('#quantity').value)


    if(quantity == 0){
        document.querySelector('#quantity').value = '1';
        document.querySelector('#total-price').innerHTML = `${product_currency}<span id="product-price">${per_item}</span>`;
    }
    else{
        document.querySelector('#total-price').innerHTML = `${product_currency}<span id="product-price">${per_item*quantity}</span>`;
    }
    if(document.querySelector('#coupon_set').value == 'y'){
        checkCoupon();
    }
}

async function checkCoupon(){
    const coupon = document.querySelector('#coupon_code').value
    if(coupon == ''){
        return;
    }
    let form = new FormData();
    form.append('product_id', document.querySelector('#product_id').value);
    form.append('coupon_code', coupon);

    response = await fetch('/product/coupon/check', {
        method: "POST",
        body: form
    });

    if(response.status == 200){
        document.querySelector('.invalid-coupon').style.display = 'none';
        document.querySelector('.valid-coupon').style.display = 'block';
        document.querySelector('.btn-remove-coupon').style.display = 'flex';

        result = await response.json();
        current_price = parseFloat(product_price) * parseInt(document.querySelector('#quantity').value);
        console.log(current_price)
        discount = parseFloat(result['Discount']) * current_price;
        document.querySelector('.valid-coupon').innerHTML = `Coupon Applied. You've saved ${product_currency}${discount.toFixed(2)}`
        document.querySelector('#product-price').innerHTML = (current_price - discount).toFixed(2);
        document.querySelector('#coupon_set').value = 'y';
    }
    else{
        document.querySelector('#total-price').innerHTML = `${product_currency}<span id="product-price">${product_price}</span>`;
        document.querySelector('.valid-coupon').style.display = 'none';
        document.querySelector('.invalid-coupon').style.display = 'block';
        document.querySelector('.btn-remove-coupon').style.display = 'none';
        document.querySelector('#coupon_code').value = '';
        document.querySelector('#coupon_set').value = ''
    }
}

function removeCoupon(){
    document.querySelector('#product-price').innerHTML = product_price;
    document.querySelector('.valid-coupon').style.display = 'none';
    document.querySelector('.btn-remove-coupon').style.display = 'none';
    document.querySelector('#coupon_code').value = '';
}

function showPaymentBlocks(){
    document.querySelector('.buy-block-quantity').style.display = 'none';
    document.querySelector('.payment-block-options').style.display = 'flex';
}

function returnToPrice(){
    document.querySelector('.buy-block-quantity').style.display = 'block';
    document.querySelector('.payment-block-options').style.display = 'none';
}

function setPaymentMethod(payment){
    document.querySelector('#payment_method').value = payment;

    var elems = document.querySelectorAll(".btn-payment-active");

    [].forEach.call(elems, function(el) {
        el.classList.remove("btn-payment-active");
    });
    document.querySelector(`.btn-payment-${payment}`).classList.remove('btn-payment-inactive');
    document.querySelector(`.btn-payment-${payment}`).classList.add('btn-payment-active');
}

function continueWithOrder(){
    if(document.querySelector('#payment_method').value == 'paypal'){
        if(email_delivery == 'False'){
            document.querySelector('.payment-block-options').style.display = 'none';
            document.querySelector('.payment-delivery-block').style.display = 'block';
            document.querySelector('#email').setAttribute('required', 'true');
            // create order on back-end
            return;
        }
        else {
            document.querySelector('#create-order-form').submit();
        }
    }
    else if(document.querySelector('#payment_method').value == ''){
        return;
    }
    else{
        document.querySelector('.payment-block-options').style.display = 'none';
        document.querySelector('.payment-delivery-block').style.display = 'block';
        document.querySelector('#email').setAttribute('required', 'true');
    }
}

function returnToPaymentMethods(){
    document.querySelector('.payment-block-options').style.display = 'flex';
    document.querySelector('.payment-delivery-block').style.display = 'none';
}

if(document.querySelector('.rating-wrapper')){
    document.querySelector('.rating-wrapper').addEventListener('click', updateStarRating, false);
}

function updateStarRating(evt){
    for(i=0; i < parseInt(evt.target.id); i++){
        const stars = document.querySelectorAll('.rating-wrapper img');
        for(s=0; s < 5; s++){
            stars[s].classList.remove('rating-checked');
        }
        for(j=0; j < parseInt(evt.target.id); j++){
            stars[j].classList.add('rating-checked');
        }
    }
    document.querySelector('#rating').value = evt.target.id;
}

// donation

function donationsStatus(){
    if(document.querySelector('#donations_enabled').getAttribute('data_donations_enabled') === 'None'){
        document.querySelector('.not-accepting-donations').style.display = 'block';
        document.querySelectorAll('input, button').forEach(elem => {
            elem.disabled = true;
        });
        document.querySelector('.donate-page-block').style.opacity = '0.6';
    }
}

function showDonationMessageContent(){
    if(document.querySelector('#leave_message').checked){
        document.querySelector('#leave_message').value = 'y';
        document.querySelector('.leave-message-content').style.display = 'flex';
        document.querySelector('#message').setAttribute('required', 'true')
    }
    else{
        document.querySelector('#leave_message').value = 'n';
        document.querySelector('.leave-message-content').style.display = 'none';
        document.querySelector('#message').removeAttribute('required')
    }
}

function setDonationAmount(button){
    const amount = document.querySelector(`${button}`).getAttribute('data-amount');
    
    document.querySelector('#amount').value = parseFloat(amount).toFixed(2);
    var elems = document.querySelectorAll(".btn-user-donation.btn-primary");

    [].forEach.call(elems, function(el) {
        el.classList.remove("btn-primary");
    });
    document.querySelector(button).classList.add('btn-primary');
}

function checkDonationAmount(){
    
    let amount = document.querySelector('#amount');
    const min = amount.getAttribute('data-min');
    
    if(parseFloat(amount.value) < parseFloat(min)){
        amount.value = parseFloat(min).toFixed(2);
        return;
    }
    amount.value = parseFloat(amount.value).toFixed(2);
}

function continueWithDonation(){
    const username = document.querySelector('.btn-donation-continue').getAttribute('data-username');
    const currency = document.querySelector('.btn-donation-continue').getAttribute('data-currency');
    
    if(document.querySelector('#leave_message').checked && document.querySelector('#message').value == ''){
        document.querySelector('#donation-message-required').style.display = 'block';
        return;
    }
    else{
        document.querySelector('.donate-main-content').style.display = 'none';
        document.querySelector('.payment-block-options').style.display = 'flex';
    }
    const value = document.querySelector('#amount').value;
    document.querySelector('#donation-amount-header').innerHTML = `You are making a donation of ${currency}${parseFloat(value).toFixed(2)} to ${username}`
    document.querySelector('#donation-amount-header').style.display = 'flex';
}

function returnToDonation(){
    document.querySelector('.donate-main-content').style.display = 'block';
    document.querySelector('.payment-block-options').style.display = 'none';
    document.querySelector('#make-payment-text').style.display = 'block';
    document.querySelector('.donation-loading-spinner').style.display = 'none';
    document.querySelector('#payment-block-continue').removeAttribute('disabled');
    document.querySelector('#donation-amount-header').style.display = 'none';
}

function setPaymentMethod(payment){
    document.querySelector('#payment_method').value = payment;

    var elems = document.querySelectorAll(".btn-payment-active");

    [].forEach.call(elems, function(el) {
        el.classList.remove("btn-payment-active");
    });
    document.querySelector(`.btn-payment-${payment}`).classList.remove('btn-payment-inactive');
    document.querySelector(`.btn-payment-${payment}`).classList.add('btn-payment-active');
}

function makeDonation(){
    if(document.querySelector('#payment_method').value == ''){
        return;
    }
    document.querySelector('#make-payment-text').style.display = 'none';
    document.querySelector('.donation-loading-spinner').style.display = 'flex';
    document.querySelector('#payment-block-continue').setAttribute('disabled', 'true');
    createDonation();
}

async function createDonation(){
    
    let form = new FormData();
    form.append('amount', document.querySelector('#amount').value)
    if(document.querySelector('#leave_message').checked){
        form.append('name', document.querySelector('#name').value);
        form.append('message', document.querySelector('#message').value);
    }
    form.append('payment_method', document.querySelector('#payment_method').value)
    form.append('csrf_token', document.querySelector('#csrf_token').value)
    form.append('uuid', document.querySelector('#uuid').value)

    const request = await fetch('/donation/create/payment',{
            method: "POST",
            body: form
    })
    const json = await request.json()

    if(request.status !== 200){
        document.querySelector('.flashed-error-donation').style.display = 'block';
        if(json['error'] == 'The CSRF token is invalid.'){
            console.log(1)
            document.querySelector('.flashed-error-donation').innerHTML = 'Something went wrong. Please refresh and try again';
        }
        else{
            console.log(2)
            document.querySelector('.flashed-error-donation').innerHTML = json['error'];
        }
        
        document.querySelector('#make-payment-text').style.display = 'block';
        document.querySelector('.donation-loading-spinner').style.display = 'none';
    }
    else{
        donationTimeout(60 * 15 - 1, json['donation_id']);
        document.querySelector('.awaiting-payment').style.display = 'flex';
        document.querySelector('.payment-block-options').style.display = 'none';
        document.querySelector('.donation-loading-spinner').style.display = 'none';
        localStorage.setItem('donation_id', json['donation_id'])
        if(json['Payment'] == 'paypal'){
            window.location.replace(json['address']);
        }
        else if(json['Payment'] == 'stripe'){
            createStripeElement(json['address'], json['donation_id'])
        }
        else {
            document.querySelector('.pay-donation-crypto').style.display = 'block';
            document.querySelector('#crypto-pay-amount').innerHTML = `Please send <b>${json['amount']} ${json['Payment']}</b> to ${json['address']}`
            document.querySelector('.btn-back').style.display = 'flex';
            document.querySelector('.crypto-donation-amount-tracker').style.display = 'block';
            document.querySelector('#total-crypto-amount').innerHTML = `${json['amount']} ${json['Payment']}`
            const payment_method = json['Payment'].replace('BTC', 'bitcoin').replace('ETH', 'ethereum').replace('LTC', 'litecoin');
            new QRCode(document.querySelector(".crypto-pay-qr"), `${payment_method}:${json['address']}?amount=${json['amount']}?label=Sellit%20Donation`);

            checkCryptoPayment(json['donation_id']);
        }
    }
}

function cancelDonation(){
    const donation_id = localStorage.getItem('donation_id')
    localStorage.clear();
    window.location = `/donation/cancel/${donation_id}`;
}

function createStripeElement(id, donation){
    
    document.querySelector('.pay-donation-stripe').style.display = 'block';
    document.querySelector('#make-payment-text').style.display = 'block';
    
    var stripe = Stripe("pk_test_51IUdJSIec92qezfoBm6qkEq8ZA88oElR7sttP66FZINxqJz8C3Jmba5d4MkC6uazliPdouP9FUBAff7M1tAAPnsd0039W08k5V");

    var elements = stripe.elements();

    var style = {
        base: {
          color: "#32325d",
          fontFamily: 'Arial, sans-serif',
          fontSmoothing: "antialiased",
          fontSize: "16px",
          "::placeholder": {
            color: "#32325d"
          }
        },
        invalid: {
          fontFamily: 'Arial, sans-serif',
          color: "#fa755a",
          iconColor: "#fa755a"
        }
    };

    var card = elements.create("card", { style: style });
    // Stripe injects an iframe into the DOM
    card.mount("#card-element");

    card.on("change", function (event) {
        // Disable the Pay button if there are no card details in the Element
        document.querySelector("button").disabled = event.empty;
        document.querySelector("#card-error").textContent = event.error ? event.error.message : "";
    });

    var form = document.getElementById("payment-form");
    form.addEventListener("submit", function(event) {
        localStorage.clear();
        event.preventDefault();
        document.querySelector('#stripe-submit').setAttribute('disabled', 'true');
        document.querySelector('#pay-now-text').style.display = 'none';
        document.querySelector('#stripe-processing-payment').style.display = 'flex';
        payWithCard(stripe, card, id);
    });

    var payWithCard = function(stripe, card, id) {
        stripe
          .confirmCardPayment(id, {
            payment_method: {
              card: card
            }
          })
          .then(function(result) {
            if (result.error) {
                document.querySelector('#stripe-processing-payment').style.display = 'none';
                document.querySelector('#pay-now-text').style.display = 'block';
                const stripeError = document.querySelector('#card-error');
                stripeError.style.display = 'block';
                stripeError.innerHTML = result.error.message
                document.querySelector('#stripe-submit').removeAttribute('disabled');
            } else {
                window.location.href = `/donation/check/${donation}?intent=${result.paymentIntent.id}`
            }
          });
      };
}

async function checkCryptoPayment(donation_id){
    const request = await fetch(`/donation/check/${donation_id}`);
    try {
        json = await request.json();
        if(json['amount_received'] != '0.00000000'){
            document.querySelector('#received-crypto-amount').innerHTML = json['amount_received']
        }
        setTimeout(() => checkCryptoPayment(donation_id), 20000)
    }
    catch {
        window.location = `/donation/check/${donation_id}`;
        return;
    }
};

function donationTimeout(duration, donation_id){
    document.querySelector('#awaiting-payment-timer').innerHTML = '14:59'
    var timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10)
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        document.querySelector('#awaiting-payment-timer').innerHTML = minutes + ":" + seconds;

        if (--timer < 0) {
            window.location = `/donation/check/${donation_id}?payment_timeout=true`;
        }
    }, 1000);
    }