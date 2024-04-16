flectra.define('website_livechat/static/src/models/thread/thread.js',function(require){
'usestrict';

const{
    registerClassPatchModel,
    registerFieldPatchModel,
}=require('mail/static/src/model/model_core.js');
const{many2one}=require('mail/static/src/model/model_field.js');

registerClassPatchModel('mail.thread','website_livechat/static/src/models/thread/thread.js',{

    //----------------------------------------------------------------------
    //Public
    //----------------------------------------------------------------------

    /**
     *@override
     */
    convertData(data){
        constdata2=this._super(data);
        if('visitor'indata){
            if(data.visitor){
                data2.visitor=[[
                    'insert',
                    this.env.models['website_livechat.visitor'].convertData(data.visitor)
                ]];
            }else{
                data2.visitor=[['unlink']];
            }
        }
        returndata2;
    },

});

registerFieldPatchModel('mail.thread','website_livechat/static/src/models/thread/thread.js',{
    /**
     *Visitorconnectedtothelivechat.
     */
    visitor:many2one('website_livechat.visitor',{
        inverse:'threads',
    }),
});

});
