flectra.define('point_of_sale.PosContext',function(require){
    'usestrict';

    const{Context}=owl;

    //Createglobalcontextobjects
    //e.g.component.env.device=newContext({isMobile:false});
    return{
        orderManagement:newContext({searchString:'',selectedOrder:null}),
        chrome:newContext({showOrderSelector:true}),
    };
});
