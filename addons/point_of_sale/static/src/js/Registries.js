flectra.define('point_of_sale.Registries',function(require){
    'usestrict';

    /**
     *ThisdefinitioncontainsalltheinstancesofClassRegistry.
     */

    constComponentRegistry=require('point_of_sale.ComponentRegistry');

    return{Component:newComponentRegistry()};
});
