const validation_error = document.querySelector('#validation-error');

function validateEmail(){
    const re = /\S+@\S+\.\S+/;
    const email = document.querySelector('#email').value;
    return re.test(String(email).toLowerCase());
}

function validateUsername(){
    return document.querySelector('#username').value.length < 3 ? false:true
}

function validateTerms(){
    return document.querySelector('#terms').checked ? true:false
}

function confirmPasswords(){
    const password = document.querySelector('#password').value
    const confirm_password = document.querySelector('#confirm_password').value

    return password != confirm_password ? false:true;
}

function validatePasswordLength(){
    const password = document.querySelector('#password').value;
    return password.length < 8 ? false:true
}

function validateDateOfBirth(){
    const d = new Date;
    const month = d.getMonth().toString().padStart(2, '0');
    const day = d.getDay().toString().padStart(2, '0');

    const current_date = d.getFullYear() + month + day;
    const user_date = document.querySelector('#date_of_birth').value.replaceAll('-', '');
    
    if(user_date === ''){
        return false;
    }

    const age = current_date - user_date.toString().slice(0, -4);
    
    return parseInt(age) < 13 ? false:true
}

function validateRegistration(){
    if(!(validateEmail())){
        validation_error.innerHTML = 'Please enter a valid email';
        validation_error.style.display = 'flex';
        return;    
    }

    if(!(validateUsername())){
        validation_error.innerHTML = 'Username must be at least 3 characters';
        validation_error.style.display = 'flex';
        return; 
    }

    if(!(confirmPasswords())){
        validation_error.innerHTML = 'Passwords do not match.';
        validation_error.style.display = 'flex';
        return; 
    }

    if(!(validatePasswordLength())){
        validation_error.innerHTML = 'Password must be at least 8 characters';
        validation_error.style.display = 'flex';
        return; 
    }

    if(!(validateDateOfBirth())){
        validation_error.innerHTML = 'You must be at least 13 years old to use this service';
        validation_error.style.display = 'flex';
        return; 
    }

    if(!(validateTerms())){
        validation_error.innerHTML = 'You must accept the Terms and Conditions';
        validation_error.style.display = 'flex';
        return; 
    }

    document.querySelector('#auth-form').submit();
}

function validateLogin(){
    if(!(validateEmail())){
        validation_error.innerHTML = 'Please enter a valid email';
        validation_error.style.display = 'flex';
        return;
    }

    document.querySelector('#auth-form').submit();
}