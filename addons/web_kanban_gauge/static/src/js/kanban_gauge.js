flectra.define('web_kanban_gauge.widget',function(require){
"usestrict";

varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varfield_registry=require('web.field_registry');
varutils=require('web.utils');

var_t=core._t;

/**
 *options
 *
 *-max_value:maximumvalueofthegauge[default:100]
 *-max_field:getthemax_valuefromthefieldthatmustbepresentinthe
 *  view;takesovermax_value
 *-gauge_value_field:ifset,thevaluedisplayedbelowthegaugeistaken
 *  fromthisfieldinsteadofthebasefieldusedfor
 *  thegauge.Thisallowstodisplayanumberdifferent
 *  fromthegauge.
 *-label:lableofthegauge,displayedbelowthegaugevalue
 *-label_field:getthelabelfromthefieldthatmustbepresentinthe
 *  view;takesoverlabel
 *-title:titleofthegauge,displayedontopofthegauge
 *-style:customstyle
 */

varGaugeWidget=AbstractField.extend({
    className:"oe_gauge",
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        //currentvalue
        varval=this.value;
        if(_.isArray(JSON.parse(val))){
            val=JSON.parse(val);
        }
        vargauge_value=_.isArray(val)&&val.length?val[val.length-1].value:val;
        if(this.nodeOptions.gauge_value_field){
            gauge_value=this.recordData[this.nodeOptions.gauge_value_field];
        }

        //max_value
        varmax_value=this.nodeOptions.max_value||100;
        if(this.nodeOptions.max_field){
            max_value=this.recordData[this.nodeOptions.max_field];
        }
        max_value=Math.max(gauge_value,max_value);

        //label
        varlabel=this.nodeOptions.label||"";
        if(this.nodeOptions.label_field){
            label=this.recordData[this.nodeOptions.label_field];
        }

        //title
        vartitle=this.nodeOptions.title||this.field.string;

        varmaxLabel=max_value;
        if(gauge_value===0&&max_value===0){
            max_value=1;
            maxLabel=0;
        }
		varconfig={
			type:'doughnut',
			data:{
				datasets:[{
					data:[
                        gauge_value,
                        max_value-gauge_value
					],
					backgroundColor:[
                        "#1f77b4","#dddddd"
					],
					label:title
				}],
			},
			options:{
				circumference:Math.PI,
				rotation:-Math.PI,
				responsive:true,
                tooltips:{
                    displayColors:false,
                    callbacks:{
                        label:function(tooltipItems){
                            if(tooltipItems.index===0){
                                return_t('Value:')+gauge_value;
                            }
                            return_t('Max:')+maxLabel;
                        },
                    },
                },
				title:{
					display:true,
					text:title,
                    padding:4,
				},
                layout:{
                    padding:{
                        bottom:5
                    }
                },
                maintainAspectRatio:false,
                cutoutPercentage:70,
            }
		};
        this.$canvas=$('<canvas/>');
        this.$el.empty();
        this.$el.append(this.$canvas);
        this.$el.attr('style',this.nodeOptions.style);
        this.$el.css({position:'relative'});
        varcontext=this.$canvas[0].getContext('2d');
        this.chart=newChart(context,config);

        varhumanValue=utils.human_number(gauge_value,1);
        var$value=$('<spanclass="o_gauge_value">').text(humanValue);
        $value.css({'text-align':'center',position:'absolute',left:0,right:0,bottom:'6px','font-weight':'bold'});
        this.$el.append($value);
    },
});

field_registry.add("gauge",GaugeWidget);

returnGaugeWidget;

});
