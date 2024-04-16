(function(){
'usestrict';

/**
 *Thisfilemakessuretextareaelementswithaspecificeditorclassare
 *tweakedassoonastheDOMisreadysothattheyappeartobeloading.
 *
 *TheymustthenbeloadedusingstandardFlectramodulessystem.Inparticular,
 *@seeweb_editor.loader
 */

document.addEventListener('DOMContentLoaded',()=>{
    //Standardloopforbetterbrowsersupport
    vartextareaEls=document.querySelectorAll('textarea.o_wysiwyg_loader');
    for(vari=0;i<textareaEls.length;i++){
        vartextarea=textareaEls[i];
        varwrapper=document.createElement('div');
        wrapper.classList.add('position-relative','o_wysiwyg_wrapper');

        varloadingElement=document.createElement('div');
        loadingElement.classList.add('o_wysiwyg_loading');
        varloadingIcon=document.createElement('i');
        loadingIcon.classList.add('text-600','text-center',
            'fa','fa-circle-o-notch','fa-spin','fa-2x');
        loadingElement.appendChild(loadingIcon);
        wrapper.appendChild(loadingElement);

        textarea.parentNode.insertBefore(wrapper,textarea);
        wrapper.insertBefore(textarea,loadingElement);
    }
});

})();
