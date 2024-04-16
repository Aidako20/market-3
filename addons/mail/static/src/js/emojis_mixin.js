flectra.define('mail.emoji_mixin',function(require){
"usestrict";

varemojis=require('mail.emojis');

/**
 *Thismixingathersafewmethodsthatareusedtohandleemojis.
 *
 *It'susedto:
 *
 *-handletheclickonanemojifromadropdownpanelandaddittotherelatedtextarea/input
 *-formattextandwraptheemojisaround<spanclass="o_mail_emoji">tomakethemlooknicer
 *
 *Methodsarebasedonthecollectionsofemojisavailableinmail.emojis
 *
 */
return{
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Thismethodshouldbeboundtoaclickeventonanemoji.
     *(usedintextelement'semojisdropdownlist)
     *
     *Itassumesthata``_getTargetTextElement``methodisdefinedthatwillreturntherelated
     *textarea/inputelementinwhichtheemojiwillbeinserted.
     *
     *@param{MouseEvent}ev
     */
    _onEmojiClick:function(ev){
        varunicode=ev.currentTarget.textContent.trim();
        vartextInput=this._getTargetTextElement($(ev.currentTarget))[0];
        varselectionStart=textInput.selectionStart;

        textInput.value=textInput.value.slice(0,selectionStart)+unicode+textInput.value.slice(selectionStart);
        textInput.focus();
        textInput.setSelectionRange(selectionStart+unicode.length,selectionStart+unicode.length);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Thismethodisusedtowrapemojisinatextmessagewith<spanclass="o_mail_emoji">
     *Asthisreturnshtmltobeusedina't-raw'argument,itfirstmakessurethatthe
     *passedtextmessageishtmlescapedforsafetyreasons.
     *
     *@param{String}messageatextmessagetoformat
     */
    _formatText:function(message){
        message=this._htmlEscape(message);
        message=this._wrapEmojis(message);
        message=message.replace(/(?:\r\n|\r|\n)/g,'<br>');

        returnmessage;
    },

    /**
     *Adaptedfromqweb2.js#html_escapetoavoidformatting'&'
     *
     *@param{String}s
     *@private
     */
    _htmlEscape:function(s){
        if(s==null){
            return'';
        }
        returnString(s).replace(/</g,'&lt;').replace(/>/g,'&gt;');
    },

    /**
     *Willusethemail.emojislibrarytowrapemojisunicodearoundaspanwithaspecialfont
     *thatwillmakethemlooknicer(colored,...).
     *
     *@param{String}message
     */
    _wrapEmojis:function(message){
        emojis.forEach(function(emoji){
            message=message.replace(
                newRegExp(emoji.unicode.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'g'),
                '<spanclass="o_mail_emoji">'+emoji.unicode+'</span>'
            );
        });

        returnmessage;
    }
};

});
