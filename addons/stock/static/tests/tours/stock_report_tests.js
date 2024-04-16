flectra.define('stock.reports.setup.tour',function(require){
    "usestrict";

    consttour=require('web_tour.tour');

    tour.register('test_stock_route_diagram_report',{
        test:true,
    },[
    {
        trigger:'.o_kanban_record',
        extra_trigger:'.breadcrumb',
    },
    {
        trigger:'.nav-item>a:contains("Inventory")',
    },
    {
        trigger:'.btn[id="stock.view_diagram_button"]',
    },
    {
        trigger:'iframe.o_report_stock_rule',
    },
    ]);
});
