flectra.define('hr_holidays/static/src/components/thread_view/thread_view.js',function(require){
'usestrict';

constcomponents={
    ThreadView:require('mail/static/src/components/thread_view/thread_view.js'),
};

const{patch}=require('web.utils');

patch(components.ThreadView,'hr_holidays/static/src/components/thread_view/thread_view.js',{
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _useStoreSelector(props){
        constres=this._super(...arguments);
        constthread=res.thread;
        constcorrespondent=thread&&thread.correspondent;
        returnObject.assign({},res,{
            correspondentOutOfOfficeText:correspondent&&correspondent.outOfOfficeText,
        });
    },
});

});
