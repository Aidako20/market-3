flectra.define('sale.product_discount',function(require){
    "usestrict";

    constBasicFields=require('web.basic_fields');
    constFieldsRegistry=require('web.field_registry');

    /**
     *Thesale.product_discountwidgetisasimplewidgetextendingFieldFloat
     *
     *
     *!!!WARNING!!!
     *
     *Thiswidgetisonlydesignedforsale_order_linecreation/updates.
     *!!!Itshouldonlybeusedonadiscountfield!!!
     */
    constProductDiscountWidget=BasicFields.FieldFloat.extend({

        /**
         *Overridechangesatadiscount.
         *
         *@override
         *@param{FlectraEvent}ev
         *
         */
        asyncreset(record,ev){
            if(ev&&ev.data.changes&&ev.data.changes.discount>=0){
               this.trigger_up('open_discount_wizard');
            }
            this._super(...arguments);
        },
    });

    FieldsRegistry.add('product_discount',ProductDiscountWidget);

    returnProductDiscountWidget;

});
