// product page

const product_price = document.querySelector('#product-price-att').getAttribute('data-product-price');
let product_currency = document.querySelector('#product-currency-att').getAttribute('data-product-currency');

product_currency = product_currency.replace('GBP', '£')
product_currency = product_currency.replace('EUR', '€')
product_currency = product_currency.replace('USD', '$')

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
        if('{{user.payment_methods.paypal_delivery}}' == 'False'){
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