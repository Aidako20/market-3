flectra.define('website_links.charts',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

var_t=core._t;

varBarChart=publicWidget.Widget.extend({
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],
    /**
     *@constructor
     *@param{Object}parent
     *@param{Object}beginDate
     *@param{Object}endDate
     *@param{Object}dates
     */
    init:function(parent,beginDate,endDate,dates){
        this._super.apply(this,arguments);
        this.beginDate=beginDate.locale("en");
        this.endDate=endDate;
        this.number_of_days=this.endDate.diff(this.beginDate,'days')+2;
        this.dates=dates;
    },
    /**
     *@override
     */
    start:function(){
        //Filldataforeachday(with0clickfordayswithoutdata)
        varclicksArray=[];
        varbeginDateCopy=this.beginDate;
        for(vari=0;i<this.number_of_days;i++){
            vardateKey=beginDateCopy.format('YYYY-MM-DD');
            clicksArray.push([dateKey,(dateKeyinthis.dates)?this.dates[dateKey]:0]);
            beginDateCopy.add(1,'days');
        }

        varnbClicks=0;
        vardata=[];
        varlabels=[];
        clicksArray.forEach(function(pt){
            labels.push(pt[0]);
            nbClicks+=pt[1];
            data.push(pt[1]);
        });

        this.$('.title').html(nbClicks+_t('clicks'));

        varconfig={
            type:'line',
            data:{
                labels:labels,
                datasets:[{
                    data:data,
                    fill:'start',
                    label:_t('#ofclicks'),
                    backgroundColor:'#ebf2f7',
                    borderColor:'#6aa1ca',

                }],
            },
        };
        varcanvas=this.$('canvas')[0];
        varcontext=canvas.getContext('2d');
        newChart(context,config);
    },
});

varPieChart=publicWidget.Widget.extend({
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],
    /**
     *@override
     *@param{Object}parent
     *@param{Object}data
     */
    init:function(parent,data){
        this._super.apply(this,arguments);
        this.data=data;
    },
    /**
     *@override
     */
    start:function(){

        //ProcesscountrydatatofitintotheChartJSscheme
        varlabels=[];
        vardata=[];
        for(vari=0;i<this.data.length;i++){
            varcountryName=this.data[i]['country_id']?this.data[i]['country_id'][1]:_t('Undefined');
            labels.push(countryName+'('+this.data[i]['country_id_count']+')');
            data.push(this.data[i]['country_id_count']);
        }

        //Settitle
        this.$('.title').html(this.data.length+_t('countries'));

        varconfig={
            type:'pie',
            data:{
                labels:labels,
                datasets:[{
                    data:data,
                    label:this.data.length>0?this.data[0].key:_t('Nodata'),
                }]
            },
        };

        varcanvas=this.$('canvas')[0];
        varcontext=canvas.getContext('2d');
        newChart(context,config);
    },
});

publicWidget.registry.websiteLinksCharts=publicWidget.Widget.extend({
    selector:'.o_website_links_chart',
    events:{
        'click.graph-tabslia':'_onGraphTabClick',
        'click.copy-to-clipboard':'_onCopyToClipboardClick',
    },

    /**
     *@override
     */
    start:function(){
        varself=this;
        this.charts={};

        //Getthecodeofthelink
        varlinkID=parseInt($('#link_id').val());
        this.links_domain=['link_id','=',linkID];

        vardefs=[];
        defs.push(this._totalClicks());
        defs.push(this._clicksByDay());
        defs.push(this._clicksByCountry());
        defs.push(this._lastWeekClicksByCountry());
        defs.push(this._lastMonthClicksByCountry());
        defs.push(this._super.apply(this,arguments));

        newClipboardJS($('.copy-to-clipboard')[0]);

        this.animating_copy=false;

        returnPromise.all(defs).then(function(results){
            var_totalClicks=results[0];
            var_clicksByDay=results[1];
            var_clicksByCountry=results[2];
            var_lastWeekClicksByCountry=results[3];
            var_lastMonthClicksByCountry=results[4];

            if(!_totalClicks){
                $('#all_time_charts').prepend(_t("Thereisnodatatoshow"));
                $('#last_month_charts').prepend(_t("Thereisnodatatoshow"));
                $('#last_week_charts').prepend(_t("Thereisnodatatoshow"));
                return;
            }

            varformattedClicksByDay={};
            varbeginDate;
            for(vari=0;i<_clicksByDay.length;i++){
                //Thisisatricktogetthedatewithoutthelocalformatting.
                //Wecan'tsimplydo.locale("en")becausesomeFlectralanguages
                //arenotsupportedbymoment.js(eg:ArabicSyria).
                constdate=moment(
                    _clicksByDay[i]["__domain"].find((el)=>el.length&&el.includes(">="))[2]
                        .split("")[0],"YYYYMMDD"
                );
                if(i===0){
                    beginDate=date;
                }
                formattedClicksByDay[date.locale("en").format("YYYY-MM-DD")]=
                    _clicksByDay[i]["create_date_count"];
            }

            //Processalltimelinechartdata
            varnow=moment();
            self.charts.all_time_bar=newBarChart(self,beginDate,now,formattedClicksByDay);
            self.charts.all_time_bar.attachTo($('#all_time_clicks_chart'));

            //Processmonthlinechartdata
            beginDate=moment().subtract(30,'days');
            self.charts.last_month_bar=newBarChart(self,beginDate,now,formattedClicksByDay);
            self.charts.last_month_bar.attachTo($('#last_month_clicks_chart'));

            //Processweeklinechartdata
            beginDate=moment().subtract(7,'days');
            self.charts.last_week_bar=newBarChart(self,beginDate,now,formattedClicksByDay);
            self.charts.last_week_bar.attachTo($('#last_week_clicks_chart'));

            //Processpiecharts
            self.charts.all_time_pie=newPieChart(self,_clicksByCountry);
            self.charts.all_time_pie.attachTo($('#all_time_countries_charts'));

            self.charts.last_month_pie=newPieChart(self,_lastMonthClicksByCountry);
            self.charts.last_month_pie.attachTo($('#last_month_countries_charts'));

            self.charts.last_week_pie=newPieChart(self,_lastWeekClicksByCountry);
            self.charts.last_week_pie.attachTo($('#last_week_countries_charts'));

            varrowWidth=$('#all_time_countries_charts').parent().width();
            var$chartCanvas=$('#all_time_countries_charts,last_month_countries_charts,last_week_countries_charts').find('canvas');
            $chartCanvas.height(Math.max(_clicksByCountry.length*(rowWidth>750?1:2),20)+'em');

        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _totalClicks:function(){
        returnthis._rpc({
            model:'link.tracker.click',
            method:'search_count',
            args:[[this.links_domain]],
        });
    },
    /**
     *@private
     */
    _clicksByDay:function(){
        returnthis._rpc({
            model:'link.tracker.click',
            method:'read_group',
            args:[[this.links_domain],['create_date']],
            kwargs:{groupby:'create_date:day'},
        });
    },
    /**
     *@private
     */
    _clicksByCountry:function(){
        returnthis._rpc({
            model:'link.tracker.click',
            method:'read_group',
            args:[[this.links_domain],['country_id']],
            kwargs:{groupby:'country_id'},
        });
    },
    /**
     *@private
     */
    _lastWeekClicksByCountry:function(){
        //7days*24hours*60minutes*60seconds*1000milliseconds.
        constaWeekAgoDate=newDate(Date.now()-7*24*60*60*1000);
        //getthedateintheformatYYYY-MM-DD.
        constaWeekAgoString=aWeekAgoDate.toISOString().split("T")[0];
        returnthis._rpc({
            model:'link.tracker.click',
            method:'read_group',
            args:[[this.links_domain,["create_date",">",aWeekAgoString]],["country_id"]],
            kwargs:{groupby:'country_id'},
        });
    },
    /**
     *@private
     */
    _lastMonthClicksByCountry:function(){
        //30days*24hours*60minutes*60seconds*1000milliseconds.
        constaMonthAgoDate=newDate(Date.now()-30*24*60*60*1000);
        //getthedateintheformatYYYY-MM-DD.
        constaMonthAgoString=aMonthAgoDate.toISOString().split("T")[0];
        returnthis._rpc({
            model:'link.tracker.click',
            method:'read_group',
            args:[[this.links_domain,["create_date",">",aMonthAgoString]],["country_id"]],
            kwargs:{groupby:'country_id'},
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onGraphTabClick:function(ev){
        ev.preventDefault();
        $('.graph-tabslia').tab('show');
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onCopyToClipboardClick:function(ev){
        ev.preventDefault();

        if(this.animating_copy){
            return;
        }

        this.animating_copy=true;

        $('.o_website_links_short_url').clone()
            .css('position','absolute')
            .css('left','15px')
            .css('bottom','10px')
            .css('z-index',2)
            .removeClass('.o_website_links_short_url')
            .addClass('animated-link')
            .appendTo($('.o_website_links_short_url'))
            .animate({
                opacity:0,
                bottom:'+=20',
            },500,function(){
                $('.animated-link').remove();
                this.animating_copy=false;
            });
    },
});

return{
    BarChart:BarChart,
    PieChart:PieChart,
};
});
