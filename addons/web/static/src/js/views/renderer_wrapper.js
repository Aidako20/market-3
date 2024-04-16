flectra.define('web.RendererWrapper',function(require){
    "usestrict";

    const{ComponentWrapper}=require('web.OwlCompatibility');

    classRendererWrapperextendsComponentWrapper{
        getLocalState(){}
        setLocalState(){}
        giveFocus(){}
        resetLocalState(){}
    }

    returnRendererWrapper;

});
