flectra.define('sms.fields',function(require){
"usestrict";

varbasic_fields=require('web.basic_fields');
varcore=require('web.core');
varsession=require('web.session');

var_t=core._t;

/**
 *OverrideofFieldPhonetoaddabuttoncallingSMScomposerifoptionactivated(default)
 */

varPhone=basic_fields.FieldPhone;
Phone.include({
    /**
     *Bydefault,enable_smsisactivated
     *
     *@override
     */
    init(){
        this._super.apply(this,arguments);
        this.enableSMS='enable_sms'inthis.attrs.options?this.attrs.options.enable_sms:true;
        //reinjectinnodeOptions(andthusinthis.attrs)tosignaltheproperty
        this.attrs.options.enable_sms=this.enableSMS;
    },
    /**
     *WhenthesendSMSbuttonisdisplayed,$elbecomesadivwrapping
     *theoriginallinks.
     *Thismethodmakessurewealwaysfocusthephonenumber
     *
     *@override
     */
    getFocusableElement(){
        if(this.enableSMS&&this.mode==='readonly'){
            returnthis.$el.filter('.'+this.className);
        }
        returnthis._super.apply(this,arguments);
    },
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *OpenSMScomposerwizard
     *
     *@private
     */
    _onClickSMS:function(ev){
        ev.preventDefault();
        ev.stopPropagation();

        varcontext=session.user_context;
        context=_.extend({},context,{
            default_res_model:this.model,
            default_res_id:parseInt(this.res_id),
            default_number_field_name:this.name,
            default_composition_mode:'comment',
        });
        varself=this;
        returnthis.do_action({
            title:_t('SendSMSTextMessage'),
            type:'ir.actions.act_window',
            res_model:'sms.composer',
            target:'new',
            views:[[false,'form']],
            context:context,
        },{
        on_close:function(){
            self.trigger_up('reload');
        }});
    },

    /**
     *Addabuttontocallthecomposerwizard
     *
     *@override
     *@private
     */
    _renderReadonly:function(){
        vardef=this._super.apply(this,arguments);
        if(this.enableSMS&&this.value){
            var$composerButton=$('<a>',{
                title:_t('SendSMSTextMessage'),
                href:'',
                class:'ml-3d-inline-flexalign-items-centero_field_phone_sms',
                html:$('<small>',{class:'font-weight-boldml-1',html:'SMS'}),
            });
            $composerButton.prepend($('<i>',{class:'fafa-mobile'}));
            $composerButton.on('click',this._onClickSMS.bind(this));
            this.$el=this.$el.add($composerButton);
        }

        returndef;
    },
});

returnPhone;

});
