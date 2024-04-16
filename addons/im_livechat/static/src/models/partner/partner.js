flectra.define('im_livechat/static/src/models/partner/partner.js',function(require){
'usestrict';

const{
    registerClassPatchModel,
    registerFieldPatchModel,
}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');

letnextPublicId=-1;

registerClassPatchModel('mail.partner','im_livechat/static/src/models/partner/partner.js',{

    //----------------------------------------------------------------------
    //Public
    //----------------------------------------------------------------------

    convertData(data){
        constdata2=this._super(data);
        if('livechat_username'indata){
            //fluxspecific,iflivechatusernameispresentitmeans`name`,
            //`email`and`im_status`contain`false`eventhoughtheirvalue
            //mightactuallyexist.Removethemfromdata2toavoidoverwriting
            //existingvalue(thatcouldbeknownthroughothermeans).
            deletedata2.name;
            deletedata2.email;
            deletedata2.im_status;
            data2.livechat_username=data.livechat_username;
        }
        returndata2;
    },
    getNextPublicId(){
        constid=nextPublicId;
        nextPublicId-=1;
        returnid;
    },
});

registerFieldPatchModel('mail.partner','im_livechat/static/src/models/partner/partner.js',{
    /**
     *Statesthespecificnameofthispartnerinthecontextoflivechat.
     *Eitherastringorundefined.
     */
    livechat_username:attr(),
});

});
