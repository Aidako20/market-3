flectra.define('pos_mercury.OrderReceipt',function(require){
    'usestrict';

    constOrderReceipt=require('point_of_sale.OrderReceipt');
    constRegistries=require('point_of_sale.Registries');

    constPosMercuryOrderReceipt=OrderReceipt=>
        classextendsOrderReceipt{
            /**
             *Thereceipthassignatureifoneofthepaymentlines
             *ispaidwithmercury.
             */
            gethasPosMercurySignature(){
                for(letlineofthis.paymentlines){
                    if(line.mercury_data)returntrue;
                }
                returnfalse;
            }
        };

    Registries.Component.extend(OrderReceipt,PosMercuryOrderReceipt);

    returnOrderReceipt;
});
