flectra.define('mail.CustomFilterItem',function(require){
    "usestrict";

    constCustomFilterItem=require('web.CustomFilterItem');

    CustomFilterItem.patch('mail.CustomFilterItem',T=>classextendsT{

        /**
         *Withthe`mail`moduleinstalled,wewanttofilteroutsomeofthe
         *availablefieldsin'Addcustomfilter'menu(@seeCustomFilterItem).
         *@override
         */
        _validateField(field){
            returnsuper._validateField(...arguments)&&
                field.relation!=='mail.message'&&
                field.name!=='message_ids';
        }
    });

    returnCustomFilterItem;
});
