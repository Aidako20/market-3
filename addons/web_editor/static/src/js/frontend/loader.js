flectra.define('web_editor.loader',function(require){
'usestrict';

varWysiwyg=require('web_editor.wysiwyg.root');

functionload(parent,textarea,options){
    varloading=textarea.nextElementSibling;
    if(loading&&!loading.classList.contains('o_wysiwyg_loading')){
        loading=null;
    }

    if(!textarea.value.match(/\S/)){
        textarea.value='<p><br/></p>';
    }

    varwysiwyg=newWysiwyg(parent,options);
    returnwysiwyg.attachTo(textarea).then(()=>{
        if(loading){
            loading.parentNode.removeChild(loading);
        }
        returnwysiwyg;
    });
}

return{
    load:load,
};
});
