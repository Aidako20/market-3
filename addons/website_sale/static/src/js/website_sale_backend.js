flectra.define('website_sale.backend',function(require){
"usestrict";

varWebsiteBackend=require('website.backend.dashboard');
varCOLORS=['#009EFB','#21b799','#E4A900','#D5653E','#5B899E','#E46F78','#8F8F8F'];

WebsiteBackend.include({
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],

    events:_.defaults({
        'clicktr.o_product_template':'on_product_template',
        'click.js_utm_selector':'_onClickUtmButton',
    },WebsiteBackend.prototype.events),

    init:function(parent,context){
        this._super(parent,context);

        this.graphs.push({'name':'sales','group':'sale_salesman'});
    },

    /**
     *@overridemethodfromwebsitebackendDashboard
     *@private
     */
    render_graphs:function(){
        this._super();
        this.utmGraphData=this.dashboards_data.sales.utm_graph;
        this.utmGraphData&&this._renderUtmGraph();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *MethodusedtogeneratePiechart,dependingonuserselectedUTMoption(campaign,medium,source)
     *
     *@private
     */
    _renderUtmGraph:function(){
        varself=this;
        this.$(".utm_button_name").html(this.btnName);//changedrop-downbuttonname
        varutmDataType=this.utmType||'campaign_id';
        vargraphData=this.utmGraphData[utmDataType];
        if(graphData.length){
            this.$(".o_utm_no_data_img").hide();
            this.$(".o_utm_data_graph").empty().show();
            var$canvas=$('<canvas/>');
            this.$(".o_utm_data_graph").append($canvas);
            varcontext=$canvas[0].getContext('2d');
            console.log(graphData);

            vardata=[];
            varlabels=[];
            graphData.forEach(function(pt){
                data.push(pt.amount_total);
                labels.push(pt.utm_type);
            });
            varconfig={
                type:'pie',
                data:{
                    labels:labels,
                    datasets:[{
                        data:data,
                        backgroundColor:COLORS,
                    }]
                },
                options:{
                    tooltips:{
                        callbacks:{
                            label:function(tooltipItem,data){
                                varlabel=data.labels[tooltipItem.index]||'';
                                if(label){
                                    label+=':';
                                }
                                varamount=data.datasets[0].data[tooltipItem.index];
                                amount=self.render_monetary_field(amount,self.data.currency);
                                label+=amount;
                                returnlabel;
                            }
                        }
                    },
                    legend:{display:false}
                }
            };
            newChart(context,config);
        }else{
            this.$(".o_utm_no_data_img").show();
            this.$(".o_utm_data_graph").hide();
        }
    },

    //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *OnchangeonUTMdropdownbutton,thismethodiscalled.
         *
         *@private
         */
    _onClickUtmButton:function(ev){
        this.utmType=$(ev.currentTarget).attr('name');
        this.btnName=$(ev.currentTarget).text();
        this._renderUtmGraph();
    },

    on_product_template:function(ev){
        ev.preventDefault();

        varproduct_tmpl_id=$(ev.currentTarget).data('productId');
        this.do_action({
            type:'ir.actions.act_window',
            res_model:'product.template',
            res_id:product_tmpl_id,
            views:[[false,'form']],
            target:'current',
        },{
            on_reverse_breadcrumb:this.on_reverse_breadcrumb,
        });
    },
});
returnWebsiteBackend;

});
