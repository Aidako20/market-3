flectra.define('sms.sms_widget',function(require){
"usestrict";

varcore=require('web.core');
varfieldRegistry=require('web.field_registry');
varFieldTextEmojis=require('mail.field_text_emojis');

var_t=core._t;
/**
 *SmsWidgetisawidgettodisplayatextarea(thebody)andatextrepresenting
 *thenumberofSMSandthenumberofcharacters.Thistextiscomputedevery
 *timetheuserchangesthebody.
 */
varSmsWidget=FieldTextEmojis.extend({
    className:'o_field_text',
    enableEmojis:false,
    /**
     *@constructor
     */
    init:function(){
        this._super.apply(this,arguments);
        this.nbrChar=0;
        this.nbrSMS=0;
        this.encoding='GSM7';
        this.enableEmojis=!!this.nodeOptions.enable_emojis;
    },
    
    /**
     *@override
     *"Thiswilladdtheemojidropdowntoatargetfield(controlledbythe"enableEmojis"attribute)
     */
    on_attach_callback:function(){
        if(this.enableEmojis){
            this._super.apply(this,arguments);
        }
    },

    //--------------------------------------------------------------------------
    //Private:overridewidget
    //--------------------------------------------------------------------------

    /**
     *@private
     *@override
     */
    _renderEdit:function(){
        vardef=this._super.apply(this,arguments);

        this._compute();
        $('.o_sms_container').remove();
        var$sms_container=$('<divclass="o_sms_container"/>');
        $sms_container.append(this._renderSMSInfo());
        $sms_container.append(this._renderIAPButton());
        this.$el=this.$el.add($sms_container);

        returndef;
    },

    //--------------------------------------------------------------------------
    //Private:SMS
    //--------------------------------------------------------------------------

    /**
     *Computethenumberofcharactersandsms
     *@private
     */
    _compute:function(){
        varcontent=this._getValue();
        this.encoding=this._extractEncoding(content);
        this.nbrChar=content.length;
        this.nbrChar+=(content.match(/\n/g)||[]).length;
        this.nbrSMS=this._countSMS(this.nbrChar,this.encoding);
    },

    /**
     *CountthenumberofSMSofthecontent
     *@private
     *@returns{integer}NumberofSMS
     */
    _countSMS:function(){
        if(this.nbrChar===0){
            return0;
        }
        if(this.encoding==='UNICODE'){
            if(this.nbrChar<=70){
                return1;
            }
            returnMath.ceil(this.nbrChar/67);
        }
        if(this.nbrChar<=160){
            return1;
        }
        returnMath.ceil(this.nbrChar/153);
    },

    /**
     *Extracttheencodingdependingonthecharactersinthecontent
     *@private
     *@param{String}contentContentoftheSMS
     *@returns{String}Encodingofthecontent(GSM7orUNICODE)
     */
    _extractEncoding:function(content){
        if(String(content).match(RegExp("^[@£$¥èéùìòÇ\\nØø\\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ!\\\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà]*$"))){
            return'GSM7';
        }
        return'UNICODE';
    },

    /**
     *RendertheIAPbuttontoredirecttoIAPpricing
     *@private
     */
    _renderIAPButton:function(){
        return$('<a>',{
            'href':'https://iap-services.flectrahq.com/iap/sms/pricing',
            'target':'_blank',
            'title':_t('SMSPricing'),
            'aria-label':_t('SMSPricing'),
            'class':'fafa-lgfa-info-circle',
        });
    },

    /**
     *Renderthenumberofcharacters,smsandtheencoding.
     *@private
     */
    _renderSMSInfo:function(){
        varstring=_.str.sprintf(_t('%scharacters,fitsin%sSMS(%s)'),this.nbrChar,this.nbrSMS,this.encoding);
        var$span=$('<span>',{
            'class':'text-mutedo_sms_count',
        });
        $span.text(string);
        return$span;
    },

    /**
     *UpdatewidgetSMSinformationwithre-computedinfoaboutlength,...
     *@private
     */
    _updateSMSInfo:function() {
        this._compute();
        varstring=_.str.sprintf(_t('%scharacters,fitsin%sSMS(%s)'),this.nbrChar,this.nbrSMS,this.encoding);
        this.$('.o_sms_count').text(string);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _onBlur:function(){
        varcontent=this._getValue();
        if(!content.trim().length&&content.length>0){
            this.do_warn(_t("YourSMSTextMessagemustincludeatleastonenon-whitespacecharacter"));
            this.$input.val(content.trim());
            this._updateSMSInfo();
        }
    },

    /**
     *@override
     *@private
     */
    _onChange:function(){
        this._super.apply(this,arguments);
        this._updateSMSInfo();
    },

    /**
     *@override
     *@private
     */
    _onInput:function(){
        this._super.apply(this,arguments);
        this._updateSMSInfo();
    },
});

fieldRegistry.add('sms_widget',SmsWidget);

returnSmsWidget;
});
