flectra.define('point_of_sale.SaleDetailsButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classSaleDetailsButtonextendsPosComponent{
        asynconClick(){
            //IMPROVEMENT:Perhapsputthislogicinaparentcomponent
            //sothatforunittesting,wecancheckifthissimple
            //componentcorrectlytriggersanevent.
            constsaleDetails=awaitthis.rpc({
                model:'report.point_of_sale.report_saledetails',
                method:'get_sale_details',
                args:[false,false,false,[this.env.pos.pos_session.id]],
            });
            constreport=this.env.qweb.renderToString(
                'SaleDetailsReport',
                Object.assign({},saleDetails,{
                    date:newDate().toLocaleString(),
                    pos:this.env.pos,
                })
            );
            constprintResult=awaitthis.env.pos.proxy.printer.print_receipt(report);
            if(!printResult.successful){
                awaitthis.showPopup('ErrorPopup',{
                    title:printResult.message.title,
                    body:printResult.message.body,
                });
            }
        }
    }
    SaleDetailsButton.template='SaleDetailsButton';

    Registries.Component.add(SaleDetailsButton);

    returnSaleDetailsButton;
});
