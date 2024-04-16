flectra.define('mail.field_emojis_common',function(require){
"usestrict";

varbasicFields=require('web.basic_fields');
varcore=require('web.core');
varemojis=require('mail.emojis');
varMailEmojisMixin=require('mail.emoji_mixin');
var_onEmojiClickMixin=MailEmojisMixin._onEmojiClick;
varQWeb=core.qweb;

/*
 *CommoncodeforFieldTextEmojisandFieldCharEmojis
 */
varFieldEmojiCommon={
    /**
     *@override
     *@private
     */
    init:function(){
        this._super.apply(this,arguments);
        this._triggerOnchange=_.throttle(this._triggerOnchange,1000,{leading:false});
        this.emojis=emojis;
    },

    /**
     *@override
     */
    on_attach_callback:function(){
        this._attachEmojisDropdown();
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        this._super.apply(this,arguments);

        if(this.mode!=='edit'){
            this.$el.html(this._formatText(this.$el.text()));
        }
    },

    /**
     *OverriddenbecauseweneedtoaddtheEmojitotheinputANDtrigger
     *the'change'eventtorefreshthevalue.
     *
     *@override
     *@private
     */
    _onEmojiClick:function(){
        _onEmojiClickMixin.apply(this,arguments);
        this._isDirty=true;
        this.$input.trigger('change');
    },

    /**
     *
     *Bydefault,the'change'eventisonlytriggeredwhenthetextelementisblurred.
     *
     *Weoverridethismethodbecausewewanttoupdatethevaluewhile
     *theuseristypinghismessage(andnotonlyonblur).
     *
     *@override
     *@private
     */
    _onKeydown:function(){
        this._super.apply(this,arguments);
        if(this.nodeOptions.onchange_on_keydown){
            this._triggerOnchange();
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *UsedbyMailEmojisMixin,checkitsdocumentformoreinfo.
     *
     *@private
     */
    _getTargetTextElement(){
        returnthis.$el;
    },

    /**
     *Triggersthe'change'eventtorefreshthevalue.
     *Thismethodisthrottledtorunatmostonceeverysecond.
     *(toavoidspammingtheserverwhiletheuseristypinghismessage)
     *
     *@private
     */
    _triggerOnchange:function(){
        this.$input.trigger('change');
    },

    /**
     *Thiswilladdanemojibuttonthatshowstheemojisselectiondropdown.
     *
     *Shouldbeusedinside'on_attach_callback'becauseweneedtheelementtobeattachedtotheformfirst.
     *That'sbecausethe$emojisIconelementneedstoberenderedoutsideofthis$el
     *(whichisantextelement,thatcan't'contain'anyotherelements).
     *
     *@private
     */
    _attachEmojisDropdown:function(){
        if(!this.$emojisIcon){
            this.$emojisIcon=$(QWeb.render('mail.EmojisDropdown',{widget:this}));
            this.$emojisIcon.find('.o_mail_emoji').on('click',this._onEmojiClick.bind(this));

            if(this.$el.filter('span.o_field_translate').length){
                //multi-languagesactivated,placethebuttonontheleftofthetranslationbutton
                this.$emojisIcon.addClass('o_mail_emojis_dropdown_translation');
            }
            if(this.$el.filter('textarea').length){
                this.$emojisIcon.addClass('o_mail_emojis_dropdown_textarea');
            }
            this.$el.last().after(this.$emojisIcon);
        }

        if(this.mode==='edit'){
            this.$emojisIcon.show();
        }else{
            this.$emojisIcon.hide();
        }
    }
};

returnFieldEmojiCommon;

});
