// Event Listeners
if(document.querySelector('.items-textarea')){
    document.querySelector('.items-textarea').addEventListener("keyup", itemLineCount);
}
window.addEventListener('load', (event) => {
    if(document.querySelector('#imagename')){
        if(document.querySelector('#imagename').value == 'default.png'){
            removeProductImage();
        }
    }    
});
window.addEventListener('resize', checkMobileMenuDisplay);

// Nav menu 

function showMobileMenu(){
    document.querySelector('.mobile-menu').style.display = 'block';
    document.querySelector('.dashboard-main-content').style.opacity = '0.2';
    document.querySelector('body').style.overflow = 'hidden';
}

function hideMobileMenu(){
    document.querySelector('.mobile-menu').style.display = 'none';
    document.querySelector('.dashboard-main-content').style.opacity = '1';
    document.querySelector('body').style.overflow = 'scroll';
}

function checkMobileMenuDisplay(){
    if(window.matchMedia("(max-width: 500px)")){
        document.querySelector('.mobile-menu').style.display = 'none';
        document.querySelector('.dashboard-main-content').style.opacity = '1';
        document.querySelector('body').style.overflow = 'scroll';
    }
}

// create product page

function itemButtonClicked(){
    document.querySelector('#product-attachments').style.display = 'none';
    document.querySelector('#product-items').style.display = 'block';
    document.querySelector('#product_type').value = 'item';
    document.querySelector('.btn-item').classList.remove('btn-not-active');
    document.querySelector('.btn-file').classList.add('btn-not-active');
    document.querySelector('#product-attachments').style.display = 'none';
    document.querySelector('#attachment_file').removeAttribute('required')
    document.querySelector('.items-textarea').setAttribute('required', 'True');
}

function fileButtonClicked(){
    document.querySelector('#product_type').value = 'file';
    document.querySelector('.btn-item').classList.add('btn-not-active');
    document.querySelector('.btn-file').classList.remove('btn-not-active');
    document.querySelector('#product-attachments').style.display = 'block';
    document.querySelector('#product-items').style.display = 'none';
    document.querySelector('#attachment_file').setAttribute('required', 'True')
    document.querySelector('.items-textarea').removeAttribute('required');
}

function updateProductType(item){
    if(item == 'item'){
        itemButtonClicked();
    }
    else{
        fileButtonClicked()
    }
}

function createTextEditor(id, content = false){
    tinymce.init({
        selector: `#${id}`,
        height: 400,
        block_formats: 'Paragraph=p; Header 1=h1; Header 2=h2; Header 3=h3',
        plugins: 'advlist autolink lists link image charmap print preview hr anchor pagebreak codesample code spellchecker code',
        toolbar_mode: 'floating',
        toolbar: 'h1 h2 h3 p a advlist autolink lists link image hr preview pagebreak blockquote',
        menubar: false,

        // Detect input changes
        setup: function(editor) {
            editor.on('Paste Change input Undo Redo', function () {
                document.querySelector('#description_value').value = tinymce.activeEditor.getContent();
            });
            if(!(content === false)){
                editor.on('init', function (e) {
                    editor.setContent(content);
                });
            }
        }


     });
}

function productImageUpload(){
    const filename = document.querySelector('#product_image').value;
    if(filename.includes('.')){
        imageUploadSuccess(filename);
    }
}

function imageUploadSuccess(filename){
    document.querySelector('.uploaded-image-details').removeAttribute('id', 'remove');
    document.querySelector('.product-image-section').removeAttribute('id', 'resize-image-container')
    document.querySelector('.new-product-image-block').setAttribute('id', 'image-uploaded')
    document.querySelector('.image-upload-icon-text').style.display = 'none';
    document.querySelector('.new-product-image-block').style.display = 'flex';
    document.querySelector('.uploaded-image-name').innerHTML = filename;
    document.querySelector('.image-uploaded-text').style.display = 'flex';
    document.querySelector('.product-image-section').classList.add('image-area-small-transition');
    document.querySelector('.product-image-input').style.display = 'none';
    document.querySelector('.uploaded-image-details').style.display = 'flex';
}

function removeProductImage(){
    document.querySelector('#product_image').value = '';
    document.querySelector('.product-image-section').setAttribute('id', 'resize-image-container')
    document.querySelector('.image-upload-icon-text').style.display = 'flex';
    document.querySelector('.new-product-image-block').setAttribute('id', 'image-removed')
    document.querySelector('.product-image-input').style.display = 'block';
    document.querySelector('.uploaded-image-details').setAttribute('id', 'remove');
    document.querySelector('.image-uploaded-text').style.display = 'none';
    document.querySelector('#image-changed').value = 'y';
}

function itemLineCount(){
    document.querySelector('.total-stock-items').innerHTML = `Stock: ${document.querySelector('.items-textarea').value.split("\n").length}`;
    if(document.querySelector('.items-textarea').value == ''){
        document.querySelector('.total-stock-items').innerHTML = 'Stock: 0';
    }
}

function removeDuplicates(){
    const items = document.querySelector('.items-textarea');
    const replaced_items = Array.from(new Set(items.value.split('\n')));
    let new_items = '';
    for(i=0; i < replaced_items.length; i++){
        if(i +1 == replaced_items.length){
            new_items = new_items + replaced_items[i]
        }
        else{
            new_items = new_items + replaced_items[i] + '\n'
        }
        
    }
    items.innerHTML = new_items;
    items.value = new_items;
    itemLineCount();
}

// edit product
function editProduct(){
    if(document.querySelector('#product_type_hidden').value == 'file'){
        fileButtonClicked();
    }
    else{
        itemLineCount();
    }
    if(document.querySelector('#imagename').value.includes('.')){
        imageUploadSuccess(document.querySelector('#imagename').value);
    }
    itemLineCount();
}

function replaceProductImage(){
    removeProductImage();
}

// category page 

function editCategory(cat){
    document.querySelector('.modal').style.display = 'block';
    document.querySelector(`.categories-container`).style.opacity = '0.3';
    document.querySelector('#category-name-input').value = cat;
    document.querySelector('#category-header').innerHTML = 'Edit Category';

    const linked_products = document.querySelectorAll('.linked-product-data');
    console.log(linked_products);
}

// modals
function openModal(id, edit=false){
    document.querySelector('.modal').style.display = 'block';
    document.querySelector(`.${id}-container`).style.opacity = '0.3';
}

function closeModal(type){
    document.querySelector('.modal').style.display = 'none';
    document.querySelector(`.${type}-container`).style.opacity = '1';
}

// in progress animation

function inProgress(){
    document.querySelector('.inprogress-animation').style.display = 'block';
}

// coupon page
function generateCoupon(){
    document.querySelector('.coupon-code-input').value = Math.random().toString(36).substr(2, 9)
}

function setStartDate(){
    document.querySelector('#start_date').setAttribute('min', new Date().toISOString().split("T")[0])
    document.querySelector('#end_date').setAttribute('min', new Date().toISOString().split("T")[0])
}

function updateEndDate(){
    document.querySelector('#end_date').setAttribute('min', document.querySelector('#start_date').value);
}

function couponRestricted(){
    if(document.querySelector('#coupon_restricted').checked){
        document.querySelector('.coupon-product-list').style.display = 'flex';
        document.querySelector('#coupon_restricted').value = 'y'
        document.querySelector('#product_list').setAttribute('required', 'true')
    }
    else{
        document.querySelector('#coupon_restricted').value = 'n'
        document.querySelector('.coupon-product-list').style.display = 'none';
        document.querySelector('#product_list').removeAttribute('required')
    }
}


// attachment page

function uploadAttachment(){
    const m = document.querySelector('#membership-status').getAttribute('data-membership');
    const upload = document.querySelector('#attachment_upload').files[0].size;
    let upload_error = document.querySelector('#attachment-error');
    
    if(upload.value != ''){
        if(m === 'Free' & upload > 2097152){
            upload_error.innerHTML = 'File too big. Max file size is 2MB';
            return;
        }
        if(m === 'Pro' & upload > 5242880){
            upload_error.innerHTML = 'File too big. Max file size is 5MB';
            return;
        }
        if(m === 'Business' & upload > 10485760){
            upload_error.innerHTML = 'File too big. Max file size is 10MB';
            return;
        }
        
        inProgress();
        document.querySelector('#submit-attachment').click();
    }
}

// settings page

function preloadSettings(avatar){
    if(avatar != 'default'){
        document.querySelector('.avatar-block').style.backgroundImage = `url(https://sellit-avatars.s3.eu-west-2.amazonaws.com/${avatar})`;
        document.querySelector('.btn-remove-avatar').style.display = 'block';
        document.querySelector('#default-avatar-img').style.display = 'none';
    }
}

function uploadAvatar(){
    document.querySelector('#image-changed').value = 'y';
    
    if(document.querySelector('#avatar-upload').value != ''){
        document.querySelector('.btn-remove-avatar').style.display = 'block';
        document.querySelector('.avatar-block').style.backgroundImage = "url("+URL.createObjectURL(document.querySelector('#avatar-upload').files[0])+")";
        document.querySelector('#default-avatar-img').style.display = 'none';
    }
    else{
        document.querySelector('.btn-remove-avatar').style.display = 'none';
        document.querySelector('.avatar-block').style.backgroundImage = '';
        document.querySelector('#default-avatar-img').style.display = 'block';
    }
}

function removeAvatar(){
    document.querySelector('#avatar-upload').value = '';
    document.querySelector('.avatar-block').style.backgroundImage = '';
    document.querySelector('#default-avatar-img').style.display = 'block';
    document.querySelector('.btn-remove-avatar').style.display = 'none';
    document.querySelector('#image-changed').value = 'y';
}
