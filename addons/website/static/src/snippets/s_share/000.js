flectra.define('website.s_share',function(require){
'usestrict';

constpublicWidget=require('web.public.widget');

constShareWidget=publicWidget.Widget.extend({
    selector:'.s_share,.oe_share',//oe_shareforcompatibility

    /**
     *@override
     */
    start:function(){
        consturlRegex=/(\?(?:|.*&)(?:u|url|body)=)(.*?)(&|#|$)/;
        consttitleRegex=/(\?(?:|.*&)(?:title|text|subject|description)=)(.*?)(&|#|$)/;
        constmediaRegex=/(\?(?:|.*&)(?:media)=)(.*?)(&|#|$)/;
        consturl=encodeURIComponent(window.location.href);
        consttitle=encodeURIComponent($('title').text());
        constmedia=encodeURIComponent($('meta[property="og:image"]').attr('content'));

        this.$('a').each((index,element)=>{
            const$a=$(element);
            $a.attr('href',(i,href)=>{
                returnhref.replace(urlRegex,(match,a,b,c)=>{
                    returna+url+c;
                }).replace(titleRegex,function(match,a,b,c){
                    if($a.hasClass('s_share_whatsapp')){
                        //WhatsAppdoesnotsupportthe"url"GETparameter.
                        //Insteadweneedtoincludetheurlwithinthepassed"text"parameter,mergingeverythingtogether.
                        //e.gofoutput:
                        //https://wa.me/?text=%20OpenWood%20Collection%20Online%20Reveal%20%7C%20My%20Website%20http%3A%2F%2Flocalhost%3A8888%2Fevent%2Fopenwood-collection-online-reveal-2021-06-21-2021-06-23-8%2Fregister
                        //seehttps://faq.whatsapp.com/general/chats/how-to-use-click-to-chat/formoredetails
                        returna+title+url+c;
                    }
                    returna+title+c;
                }).replace(mediaRegex,(match,a,b,c)=>{
                    returna+media+c;
                });
            });
            if($a.attr('target')&&$a.attr('target').match(/_blank/i)&&!$a.closest('.o_editable').length){
                $a.on('click',function(){
                    window.open(this.href,'','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=550,width=600');
                    returnfalse;
                });
            }
        });

        returnthis._super.apply(this,arguments);
    },
});

publicWidget.registry.share=ShareWidget;

returnShareWidget;
});
