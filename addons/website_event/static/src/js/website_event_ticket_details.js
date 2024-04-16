flectra.define('website_event.ticket_details',function(require){
    varpublicWidget=require('web.public.widget');

    publicWidget.registry.ticketDetailsWidget=publicWidget.Widget.extend({
        selector:'.o_wevent_js_ticket_details',
        events:{
            'click.o_wevent_registration_btn':'_onTicketDetailsClick',
            'change.custom-select':'_onTicketQuantityChange'
        },
        start:function(){
            this.foldedByDefault=this.$el.data('foldedByDefault')===1;
            returnthis._super.apply(this,arguments);
        },

        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *@private
         */
        _getTotalTicketCount:function(){
            varticketCount=0;
            this.$('.custom-select').each(function(){
                ticketCount+=parseInt($(this).val());
            });
            returnticketCount;
        },

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *@private
         *@param{*}ev
         */
        _onTicketDetailsClick:function(ev){
            ev.preventDefault();
            if(this.foldedByDefault){
                $(ev.currentTarget).toggleClass('btn-primarytext-leftpl-0');
                $(ev.currentTarget).siblings().toggleClass('d-none');
                this.$('.close').toggleClass('d-none');
            }
        },
        /**
         *@private
         */
        _onTicketQuantityChange:function(){
            this.$('button.btn-primary').attr('disabled',this._getTotalTicketCount()===0);
        }
    });

returnpublicWidget.registry.ticketDetailsWidget;
});
