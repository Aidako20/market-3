flectra.define('portal.signature_form',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');
varNameAndSignature=require('web.name_and_signature').NameAndSignature;
varqweb=core.qweb;

var_t=core._t;

/**
 *Thiswidgetisasignaturerequestform.Ituses
 *@seeNameAndSignaturefortheinputfields,addsasubmit
 *button,andhandlestheRPCtosavetheresult.
 */
varSignatureForm=publicWidget.Widget.extend({
    template:'portal.portal_signature',
    xmlDependencies:['/portal/static/src/xml/portal_signature.xml'],
    events:{
        'click.o_portal_sign_submit':'async_onClickSignSubmit',
    },
    custom_events:{
        'signature_changed':'_onChangeSignature',
    },

    /**
     *Overriddentoallowoptions.
     *
     *@constructor
     *@param{Widget}parent
     *@param{Object}options
     *@param{string}options.callUrl-makeRPCtothisurl
     *@param{string}[options.sendLabel='Accept&Sign']-labelofthe
     * sendbutton
     *@param{Object}[options.rpcParams={}]-paramsfortheRPC
     *@param{Object}[options.nameAndSignatureOptions={}]-optionsfor
     * @seeNameAndSignature.init()
     */
    init:function(parent,options){
        this._super.apply(this,arguments);

        this.csrf_token=flectra.csrf_token;

        this.callUrl=options.callUrl||'';
        this.rpcParams=options.rpcParams||{};
        this.sendLabel=options.sendLabel||_t("Accept&Sign");

        this.nameAndSignature=newNameAndSignature(this,
            options.nameAndSignatureOptions||{});
    },
    /**
     *OverriddentogettheDOMelements
     *andtoinsertthenameandsignature.
     *
     *@override
     */
    start:function(){
        varself=this;
        this.$confirm_btn=this.$('.o_portal_sign_submit');
        this.$controls=this.$('.o_portal_sign_controls');
        varsubWidgetStart=this.nameAndSignature.replace(this.$('.o_web_sign_name_and_signature'));
        returnPromise.all([subWidgetStart,this._super.apply(this,arguments)]).then(function(){
            self.nameAndSignature.resetSignature();
        });
    },

    //----------------------------------------------------------------------
    //Public
    //----------------------------------------------------------------------

    /**
     *Focusesthename.
     *
     *@seeNameAndSignature.focusName();
     */
    focusName:function(){
        this.nameAndSignature.focusName();
    },
    /**
     *Resetsthesignature.
     *
     *@seeNameAndSignature.resetSignature();
     */
    resetSignature:function(){
        returnthis.nameAndSignature.resetSignature();
    },

    //----------------------------------------------------------------------
    //Handlers
    //----------------------------------------------------------------------

    /**
     *Handlesclickonthesubmitbutton.
     *
     *Thiswillgetthecurrentnameandsignatureandvalidatethem.
     *Iftheyarevalid,theyaresenttotheserver,andthereponseis
     *handled.Iftheyareinvalid,itwilldisplaytheerrorstotheuser.
     *
     *@private
     *@param{Event}ev
     *@returns{Deferred}
     */
    _onClickSignSubmit:function(ev){
        varself=this;
        ev.preventDefault();

        if(!this.nameAndSignature.validateSignature()){
            return;
        }

        varname=this.nameAndSignature.getName();
        varsignature=this.nameAndSignature.getSignatureImage()[1];

        returnthis._rpc({
            route:this.callUrl,
            params:_.extend(this.rpcParams,{
                'name':name,
                'signature':signature,
            }),
        }).then(function(data){
            if(data.error){
                self.$('.o_portal_sign_error_msg').remove();
                self.$controls.prepend(qweb.render('portal.portal_signature_error',{widget:data}));
            }elseif(data.success){
                var$success=qweb.render('portal.portal_signature_success',{widget:data});
                self.$el.empty().append($success);
            }
            if(data.force_refresh){
                if(data.redirect_url){
                    window.location=data.redirect_url;
                }else{
                    window.location.reload();
                }
                //noresolveifwereloadthepage
                returnnewPromise(function(){});
            }
        });
    },
    /**
     *Togglesthesubmitbuttondependingonthesignaturestate.
     *
     *@private
     */
    _onChangeSignature:function(){
        varisEmpty=this.nameAndSignature.isSignatureEmpty();
        this.$confirm_btn.prop('disabled',isEmpty);
    },
});

publicWidget.registry.SignatureForm=publicWidget.Widget.extend({
    selector:'.o_portal_signature_form',

    /**
     *@private
     */
    start:function(){
        varhasBeenReset=false;

        varcallUrl=this.$el.data('call-url');
        varnameAndSignatureOptions={
            defaultName:this.$el.data('default-name'),
            mode:this.$el.data('mode'),
            displaySignatureRatio:this.$el.data('signature-ratio'),
            signatureType:this.$el.data('signature-type'),
            fontColor:this.$el.data('font-color') ||'black',
        };
        varsendLabel=this.$el.data('send-label');

        varform=newSignatureForm(this,{
            callUrl:callUrl,
            nameAndSignatureOptions:nameAndSignatureOptions,
            sendLabel:sendLabel,
        });

        //Correctlysetupthesignatureareaifitisinsideamodal
        this.$el.closest('.modal').on('shown.bs.modal',function(ev){
            if(!hasBeenReset){
                //Resetitonlythefirsttimeitisopentogetcorrect
                //size.Afterwewanttokeepitscontentonreopen.
                hasBeenReset=true;
                form.resetSignature();
            }else{
                form.focusName();
            }
        });

        returnPromise.all([
            this._super.apply(this,arguments),
            form.appendTo(this.$el)
        ]);
    },
});

return{
    SignatureForm:SignatureForm,
};
});
