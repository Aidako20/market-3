flectra.define('website_links.code_editor',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

var_t=core._t;

publicWidget.registry.websiteLinksCodeEditor=publicWidget.Widget.extend({
    selector:'#wrapwrap:has(.o_website_links_edit_code)',
    events:{
        'click.o_website_links_edit_code':'_onEditCodeClick',
        'click.o_website_links_cancel_edit':'_onCancelEditClick',
        'submit#edit-code-form':'_onEditCodeFormSubmit',
        'click.o_website_links_ok_edit':'_onEditCodeFormSubmit',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{String}newCode
     */
    _showNewCode:function(newCode){
        $('.o_website_links_code_error').html('');
        $('.o_website_links_code_error').hide();

        $('#o_website_links_codeform').remove();

        //Shownewcode
        varhost=$('#short-url-host').html();
        $('#o_website_links_code').html(newCode);

        //Updatebuttoncopytoclipboard
        $('.copy-to-clipboard').attr('data-clipboard-text',host+newCode);

        //Showactionagain
        $('.o_website_links_edit_code').show();
        $('.copy-to-clipboard').show();
        $('.o_website_links_edit_tools').hide();
    },
    /**
     *@private
     *@returns{Promise}
     */
    _submitCode:function(){
        varinitCode=$('#edit-code-form#init_code').val();
        varnewCode=$('#edit-code-form#new_code').val();
        varself=this;

        if(newCode===''){
            self.$('.o_website_links_code_error').html(_t("Thecodecannotbeleftempty"));
            self.$('.o_website_links_code_error').show();
            return;
        }

        this._showNewCode(newCode);

        if(initCode===newCode){
            this._showNewCode(newCode);
        }else{
            returnthis._rpc({
                route:'/website_links/add_code',
                params:{
                    init_code:initCode,
                    new_code:newCode,
                },
            }).then(function(result){
                self._showNewCode(result[0].code);
            },function(){
                $('.o_website_links_code_error').show();
                $('.o_website_links_code_error').html(_t("Thiscodeisalreadytaken"));
            });
        }

        returnPromise.resolve();
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onEditCodeClick:function(){
        varinitCode=$('#o_website_links_code').html();
        $('#o_website_links_code').html('<formstyle="display:inline;"id="edit-code-form"><inputtype="hidden"id="init_code"value="'+initCode+'"/><inputtype="text"id="new_code"value="'+initCode+'"/></form>');
        $('.o_website_links_edit_code').hide();
        $('.copy-to-clipboard').hide();
        $('.o_website_links_edit_tools').show();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onCancelEditClick:function(ev){
        ev.preventDefault();
        $('.o_website_links_edit_code').show();
        $('.copy-to-clipboard').show();
        $('.o_website_links_edit_tools').hide();
        $('.o_website_links_code_error').hide();

        varoldCode=$('#edit-code-form#init_code').val();
        $('#o_website_links_code').html(oldCode);

        $('#code-error').remove();
        $('#o_website_links_codeform').remove();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onEditCodeFormSubmit:function(ev){
        ev.preventDefault();
        this._submitCode();
    },
});
});
