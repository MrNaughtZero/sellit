function openMobileMenu(){
    document.querySelector('.mobile-menu').style.display = 'block';
    document.querySelector('main').style.opacity = '0.3';
    document.querySelector('body').style.overflow = 'hidden';
    document.querySelector('#hamburger-icon').onclick = closeMobileMenu;
    document.querySelector('#hamburger-icon').style.transform = 'rotate(90deg)';
}

function closeMobileMenu(){
    document.querySelector('.mobile-menu').style.display = 'none';
    document.querySelector('main').style.opacity = '1';
    document.querySelector('body').style.overflow = 'visible';
    document.querySelector('#hamburger-icon').onclick = openMobileMenu;
    document.querySelector('#hamburger-icon').style.transform = 'rotate(0deg)';
}