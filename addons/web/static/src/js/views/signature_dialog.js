flectra.define('web.signature_dialog',function(require){
"usestrict";

varcore=require('web.core');
varDialog=require('web.Dialog');
varNameAndSignature=require('web.name_and_signature').NameAndSignature;

var_t=core._t;

//Thegoalofthisdialogistoasktheuserasignaturerequest.
//Ituses@seeSignNameAndSignatureforthenameandsignaturefields.
varSignatureDialog=Dialog.extend({
    template:'web.signature_dialog',
    xmlDependencies:Dialog.prototype.xmlDependencies.concat(
        ['/web/static/src/xml/name_and_signature.xml']
    ),
    custom_events:{
        'signature_changed':'_onChangeSignature',
    },

    /**
     *@constructor
     *@param{Widget}parent
     *@param{Object}options
     *@param{string}[options.title='AdoptYourSignature']-modaltitle
     *@param{string}[options.size='medium']-modalsize
     *@param{Object}[options.nameAndSignatureOptions={}]-optionsfor
     * @seeNameAndSignature.init()
     */
    init:function(parent,options){
        varself=this;
        options=options||{};

        options.title=options.title||_t("AdoptYourSignature");
        options.size=options.size||'medium';
        options.technical=false;

        if(!options.buttons){
            options.buttons=[];
            options.buttons.push({text:_t("AdoptandSign"),classes:"btn-primary",disabled:true,click:function(e){
                self._onConfirm();
            }});
            options.buttons.push({text:_t("Cancel"),close:true});
        }

        this._super(parent,options);

        this.nameAndSignature=newNameAndSignature(this,options.nameAndSignatureOptions);
    },
    /**
     *StartthenameAndSignaturewidgetandwaitforit.
     *
     *@override
     */
    willStart:function(){
        returnPromise.all([
            this.nameAndSignature.appendTo($('<div>')),
            this._super.apply(this,arguments)
        ]);
    },
    /**
     *Initializethenameandsignaturewidgetwhenthemodalisopened.
     *
     *@override
     */
    start:function(){
        varself=this;
        this.$primaryButton=this.$footer.find('.btn-primary');

        this.opened().then(function(){
            self.$('.o_web_sign_name_and_signature').replaceWith(self.nameAndSignature.$el);
            //initializethesignaturearea
            self.nameAndSignature.resetSignature();
        });

        returnthis._super.apply(this,arguments);
    },

    //----------------------------------------------------------------------
    //Public
    //----------------------------------------------------------------------

    /**
     *Returnswhetherthedrawingareaiscurrentlyempty.
     *
     *@seeNameAndSignature.isSignatureEmpty()
     *@returns{boolean}Whetherthedrawingareaiscurrentlyempty.
     */
    isSignatureEmpty:function(){
        returnthis.nameAndSignature.isSignatureEmpty();
    },

    //----------------------------------------------------------------------
    //Handlers
    //----------------------------------------------------------------------

    /**
     *Togglesthesubmitbuttondependingonthesignaturestate.
     *
     *@private
     */
    _onChangeSignature:function(){
        varisEmpty=this.nameAndSignature.isSignatureEmpty();
        this.$primaryButton.prop('disabled',isEmpty);
    },
    /**
     *Uploadthesignatureimagewhenconfirm.
     *
     *@private
     */
    _onConfirm:function(fct){
        this.trigger_up('upload_signature',{
            name:this.nameAndSignature.getName(),
            signatureImage:this.nameAndSignature.getSignatureImage(),
        });
    },
});

returnSignatureDialog;

});
