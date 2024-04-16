flectra.define('im_livechat.ImLivechatChannelFormController',function(require){
'usestrict';

constFormController=require('web.FormController');

constImLivechatChannelFormController=FormController.extend({
    events:Object.assign({},FormController.prototype.events,{
        'click.o_im_livechat_channel_form_button_colors_reset_button':'_onClickLivechatButtonColorsResetButton',
        'click.o_im_livechat_channel_form_chat_window_colors_reset_button':'_onClickLivechatChatWindowColorsResetButton',
    }),

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}colorValues
     */
    async_updateColors(colorValues){
        for(constnameincolorValues){
            this.$(`[name="${name}"].o_field_color`).css('background-color',colorValues[name]);
        }
        constresult=awaitthis.model.notifyChanges(this.handle,colorValues);
        this._updateRendererState(this.model.get(this.handle),{fieldNames:result});
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    async_onClickLivechatButtonColorsResetButton(){
        awaitthis._updateColors({
            button_background_color:"#878787",
            button_text_color:"#FFFFFF",
        });
    },
    /**
     *@private
     */
    async_onClickLivechatChatWindowColorsResetButton(){
        awaitthis._updateColors({
            header_background_color:"#009EFB",
            title_color:"#FFFFFF",
        });
    },
});

returnImLivechatChannelFormController;

});
