flectra.define('mail/static/src/js/core/translation.js',function(require){
'usestrict';

const{TranslationDataBase}=require('web.translation');

const{Component}=owl;

TranslationDataBase.include({
    /**
     *@override
     */
    set_bundle(){
        constres=this._super(...arguments);
        if(Component.env.messaging){
            //Updatemessaginglocalewheneverthetranslationbundlechanges.
            //Inparticularifmessagingiscreatedbeforetheendofthe
            //`load_translations`RPC,thedefaultvalueshavetobe
            //updatedbythereceivedones.
            Component.env.messaging.locale.update({
                language:this.parameters.code,
                textDirection:this.parameters.direction,
            });
        }
        returnres;
    },
});

});
