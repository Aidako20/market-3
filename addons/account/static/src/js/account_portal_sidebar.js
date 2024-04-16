flectra.define('account.AccountPortalSidebar',function(require){
'usestrict';

constdom=require('web.dom');
varpublicWidget=require('web.public.widget');
varPortalSidebar=require('portal.PortalSidebar');
varutils=require('web.utils');

publicWidget.registry.AccountPortalSidebar=PortalSidebar.extend({
    selector:'.o_portal_invoice_sidebar',
    events:{
        'click.o_portal_invoice_print':'_onPrintInvoice',
    },

    /**
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);

        var$invoiceHtml=this.$el.find('iframe#invoice_html');
        varupdateIframeSize=this._updateIframeSize.bind(this,$invoiceHtml);

        $(window).on('resize',updateIframeSize);

        variframeDoc=$invoiceHtml[0].contentDocument||$invoiceHtml[0].contentWindow.document;
        if(iframeDoc.readyState==='complete'){
            updateIframeSize();
        }else{
            $invoiceHtml.on('load',updateIframeSize);
        }

        returndef;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhentheiframeisloadedorthewindowisresizedoncustomerportal.
     *Thegoalistoexpandtheiframeheighttodisplaythefullreportwithoutscrollbar.
     *
     *@private
     *@param{object}$el:theiframe
     */
    _updateIframeSize:function($el){
        var$wrapwrap=$el.contents().find('div#wrapwrap');
        //Setitto0firsttohandlethecasewherescrollHeightistoobigforitscontent.
        $el.height(0);
        $el.height($wrapwrap[0].scrollHeight);

        //scrolltotherightplaceafteriframeresize
        if(!utils.isValidAnchor(window.location.hash)){
            return;
        }
        var$target=$(window.location.hash);
        if(!$target.length){
            return;
        }
        dom.scrollTo($target[0],{duration:0});
    },
    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onPrintInvoice:function(ev){
        ev.preventDefault();
        varhref=$(ev.currentTarget).attr('href');
        this._printIframeContent(href);
    },
});
});
