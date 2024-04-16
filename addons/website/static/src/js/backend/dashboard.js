flectra.define('website.backend.dashboard',function(require){
'usestrict';

varAbstractAction=require('web.AbstractAction');
varajax=require('web.ajax');
varcore=require('web.core');
varDialog=require('web.Dialog');
varfield_utils=require('web.field_utils');
varpyUtils=require('web.py_utils');
varsession=require('web.session');
vartime=require('web.time');
varweb_client=require('web.web_client');

var_t=core._t;
varQWeb=core.qweb;

varCOLORS=["#1f77b4","#aec7e8"];
varFORMAT_OPTIONS={
    //allowtodecideifutils.human_numbershouldbeused
    humanReadable:function(value){
        returnMath.abs(value)>=1000;
    },
    //withthechoicesbelow,1236isrepresentedby1.24k
    minDigits:1,
    decimals:2,
    //avoidcommaseparatorsforthousandsinnumberswhenhuman_numberisused
    formatterCallback:function(str){
        returnstr;
    },
};

varDashboard=AbstractAction.extend({
    hasControlPanel:true,
    contentTemplate:'website.WebsiteDashboardMain',
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],
    events:{
        'click.js_link_analytics_settings':'on_link_analytics_settings',
        'click.o_dashboard_action':'on_dashboard_action',
        'click.o_dashboard_action_form':'on_dashboard_action_form',
    },

    init:function(parent,context){
        this._super(parent,context);

        this.DATE_FORMAT=time.getLangDateFormat();
        this.date_range='week'; //possiblevalues:'week','month',year'
        this.date_from=moment.utc().subtract(1,'week');
        this.date_to=moment.utc();

        this.dashboards_templates=['website.dashboard_header','website.dashboard_content'];
        this.graphs=[];
        this.chartIds={};
    },

    willStart:function(){
        varself=this;
        returnPromise.all([ajax.loadLibs(this),this._super()]).then(function(){
            returnself.fetch_data();
        }).then(function(){
            varwebsite=_.findWhere(self.websites,{selected:true});
            self.website_id=website?website.id:false;
        });
    },

    start:function(){
        varself=this;
        this._computeControlPanelProps();
        returnthis._super().then(function(){
            self.render_graphs();
        });
    },

    on_attach_callback:function(){
        this._isInDom=true;
        this.render_graphs();
        this._super.apply(this,arguments);
    },
    on_detach_callback:function(){
        this._isInDom=false;
        this._super.apply(this,arguments);
    },
    /**
     *Fetchesdashboarddata
     */
    fetch_data:function(){
        varself=this;
        varprom=this._rpc({
            route:'/website/fetch_dashboard_data',
            params:{
                website_id:this.website_id||false,
                date_from:this.date_from.year()+'-'+(this.date_from.month()+1)+'-'+this.date_from.date(),
                date_to:this.date_to.year()+'-'+(this.date_to.month()+1)+'-'+this.date_to.date(),
            },
        });
        prom.then(function(result){
            self.data=result;
            self.dashboards_data=result.dashboards;
            self.currency_id=result.currency_id;
            self.groups=result.groups;
            self.websites=result.websites;
        });
        returnprom;
    },

    on_link_analytics_settings:function(ev){
        ev.preventDefault();

        varself=this;
        vardialog=newDialog(this,{
            size:'medium',
            title:_t('ConnectGoogleAnalytics'),
            $content:QWeb.render('website.ga_dialog_content',{
                ga_key:this.dashboards_data.visits.ga_client_id,
                ga_analytics_key:this.dashboards_data.visits.ga_analytics_key,
            }),
            buttons:[
                {
                    text:_t("Save"),
                    classes:'btn-primary',
                    close:true,
                    click:function(){
                        varga_client_id=dialog.$el.find('input[name="ga_client_id"]').val();
                        varga_analytics_key=dialog.$el.find('input[name="ga_analytics_key"]').val();
                        self.on_save_ga_client_id(ga_client_id,ga_analytics_key);
                    },
                },
                {
                    text:_t("Cancel"),
                    close:true,
                },
            ],
        }).open();
    },

    on_go_to_website:function(ev){
        ev.preventDefault();
        varwebsite=_.findWhere(this.websites,{selected:true});
        window.location.href=`/website/force/${website.id}`;
    },

    on_save_ga_client_id:function(ga_client_id,ga_analytics_key){
        varself=this;
        returnthis._rpc({
            route:'/website/dashboard/set_ga_data',
            params:{
                'website_id':self.website_id,
                'ga_client_id':ga_client_id,
                'ga_analytics_key':ga_analytics_key,
            },
        }).then(function(result){
            if(result.error){
                self.do_warn(result.error.title,result.error.message);
                return;
            }
            self.on_date_range_button('week');
        });
    },

    render_dashboards:function(){
        varself=this;
        _.each(this.dashboards_templates,function(template){
            self.$('.o_website_dashboard').append(QWeb.render(template,{widget:self}));
        });
    },

    render_graph:function(div_to_display,chart_values,chart_id){
        varself=this;

        this.$(div_to_display).empty();
        var$canvasContainer=$('<div/>',{class:'o_graph_canvas_container'});
        this.$canvas=$('<canvas/>').attr('id',chart_id);
        $canvasContainer.append(this.$canvas);
        this.$(div_to_display).append($canvasContainer);

        varlabels=chart_values[0].values.map(function(date){
            returnmoment(date[0],"YYYY-MM-DD",'en');
        });

        vardatasets=chart_values.map(function(group,index){
            return{
                label:group.key,
                data:group.values.map(function(value){
                    returnvalue[1];
                }),
                dates:group.values.map(function(value){
                    returnvalue[0];
                }),
                fill:false,
                borderColor:COLORS[index],
            };
        });

        varctx=this.$canvas[0];
        this.chart=newChart(ctx,{
            type:'line',
            data:{
                labels:labels,
                datasets:datasets,
            },
            options:{
                legend:{
                    display:false,
                },
                maintainAspectRatio:false,
                scales:{
                    yAxes:[{
                        type:'linear',
                        ticks:{
                            beginAtZero:true,
                            callback:this.formatValue.bind(this),
                        },
                    }],
                    xAxes:[{
                        ticks:{
                            callback:function(moment){
                                returnmoment.format(self.DATE_FORMAT);
                            },
                        }
                    }],
                },
                tooltips:{
                    mode:'index',
                    intersect:false,
                    bodyFontColor:'rgba(0,0,0,1)',
                    titleFontSize:13,
                    titleFontColor:'rgba(0,0,0,1)',
                    backgroundColor:'rgba(255,255,255,0.6)',
                    borderColor:'rgba(0,0,0,0.2)',
                    borderWidth:2,
                    callbacks:{
                        title:function(tooltipItems,data){
                            returndata.datasets[0].label;
                        },
                        label:function(tooltipItem,data){
                            varmoment=data.labels[tooltipItem.index];
                            vardate=tooltipItem.datasetIndex===0?
                                        moment:
                                        moment.subtract(1,self.date_range);
                            returndate.format(self.DATE_FORMAT)+':'+self.formatValue(tooltipItem.yLabel);
                        },
                        labelColor:function(tooltipItem,chart){
                            vardataset=chart.data.datasets[tooltipItem.datasetIndex];
                            return{
                                borderColor:dataset.borderColor,
                                backgroundColor:dataset.borderColor,
                            };
                        },
                    }
                }
            }
        });
    },

    render_graphs:function(){
        varself=this;
        if(this._isInDom){
            _.each(this.graphs,function(e){
                varrenderGraph=self.groups[e.group]&&
                                    self.dashboards_data[e.name].summary.order_count;
                if(!self.chartIds[e.name]){
                    self.chartIds[e.name]=_.uniqueId('chart_'+e.name);
                }
                varchart_id=self.chartIds[e.name];
                if(renderGraph){
                    self.render_graph('.o_graph_'+e.name,self.dashboards_data[e.name].graph,chart_id);
                }
            });
            this.render_graph_analytics(this.dashboards_data.visits.ga_client_id);
        }
    },

    render_graph_analytics:function(client_id){
        if(!this.dashboards_data.visits||!this.dashboards_data.visits.ga_client_id){
          return;
        }

        this.load_analytics_api();

        var$analytics_components=this.$('.js_analytics_components');
        this.addLoader($analytics_components);

        varself=this;
        gapi.analytics.ready(function(){

            $analytics_components.empty();
            //1.Authorizecomponent
            var$analytics_auth=$('<div>').addClass('col-lg-12');
            window.onOriginError=function(){
                $analytics_components.find('.js_unauthorized_message').remove();
                self.display_unauthorized_message($analytics_components,'not_initialized');
            };
            gapi.analytics.auth.authorize({
                container:$analytics_auth[0],
                clientid:client_id
            });

            $analytics_auth.appendTo($analytics_components);

            self.handle_analytics_auth($analytics_components);
            gapi.analytics.auth.on('signIn',function(){
                deletewindow.onOriginError;
                self.handle_analytics_auth($analytics_components);
            });

        });
    },

    on_date_range_button:function(date_range){
        if(date_range==='week'){
            this.date_range='week';
            this.date_from=moment.utc().subtract(1,'weeks');
        }elseif(date_range==='month'){
            this.date_range='month';
            this.date_from=moment.utc().subtract(1,'months');
        }elseif(date_range==='year'){
            this.date_range='year';
            this.date_from=moment.utc().subtract(1,'years');
        }else{
            console.log('Unknowndaterange.Choosebetween[week,month,year]');
            return;
        }

        varself=this;
        Promise.resolve(this.fetch_data()).then(function(){
            self.$('.o_website_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });

    },

    on_website_button:function(website_id){
        varself=this;
        this.website_id=website_id;
        Promise.resolve(this.fetch_data()).then(function(){
            self.$('.o_website_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });
    },

    on_reverse_breadcrumb:function(){
        varself=this;
        web_client.do_push_state({});
        this.fetch_data().then(function(){
            self.$('.o_website_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });
    },

    on_dashboard_action:function(ev){
        ev.preventDefault();
        varself=this
        var$action=$(ev.currentTarget);
        varadditional_context={};
        if(this.date_range==='week'){
            additional_context={search_default_week:true};
        }elseif(this.date_range==='month'){
            additional_context={search_default_month:true};
        }elseif(this.date_range==='year'){
            additional_context={search_default_year:true};
        }
        this._rpc({
            route:'/web/action/load',
            params:{
                'action_id':$action.attr('name'),
            },
        })
        .then(function(action){
            action.domain=pyUtils.assembleDomains([action.domain,`[('website_id','=',${self.website_id})]`]);
            returnself.do_action(action,{
                'additional_context':additional_context,
                'on_reverse_breadcrumb':self.on_reverse_breadcrumb
            });
        });
    },

    on_dashboard_action_form:function(ev){
        ev.preventDefault();
        var$action=$(ev.currentTarget);
        this.do_action({
            name:$action.attr('name'),
            res_model:$action.data('res_model'),
            res_id:$action.data('res_id'),
            views:[[false,'form']],
            type:'ir.actions.act_window',
        },{
            on_reverse_breadcrumb:this.on_reverse_breadcrumb
        });
    },

    /**
     *@private
     */
    _computeControlPanelProps(){
        const$searchview=$(QWeb.render("website.DateRangeButtons",{
            widget:this,
        }));
        $searchview.find('button.js_date_range').click((ev)=>{
            $searchview.find('button.js_date_range.active').removeClass('active');
            $(ev.target).addClass('active');
            this.on_date_range_button($(ev.target).data('date'));
        });
        $searchview.find('button.js_website').click((ev)=>{
            $searchview.find('button.js_website.active').removeClass('active');
            $(ev.target).addClass('active');
            this.on_website_button($(ev.target).data('website-id'));
        });

        const$buttons=$(QWeb.render("website.GoToButtons"));
        $buttons.on('click',this.on_go_to_website.bind(this));

        this.controlPanelProps.cp_content={$searchview,$buttons};
    },

    //LoadsAnalyticsAPI
    load_analytics_api:function(){
        varself=this;
        if(!("gapi"inwindow)){
            (function(w,d,s,g,js,fjs){
                g=w.gapi||(w.gapi={});g.analytics={q:[],ready:function(cb){this.q.push(cb);}};
                js=d.createElement(s);fjs=d.getElementsByTagName(s)[0];
                js.src='https://apis.google.com/js/platform.js';
                fjs.parentNode.insertBefore(js,fjs);js.onload=function(){g.load('analytics');};
            }(window,document,'script'));
            gapi.analytics.ready(function(){
                self.analytics_create_components();
            });
        }
    },

    handle_analytics_auth:function($analytics_components){
        $analytics_components.find('.js_unauthorized_message').remove();

        //CheckiftheuserisauthenticatedandhastherighttomakeAPIcalls
        if(!gapi.analytics.auth.getAuthResponse()){
            this.display_unauthorized_message($analytics_components,'not_connected');
        }elseif(gapi.analytics.auth.getAuthResponse()&&gapi.analytics.auth.getAuthResponse().scope.indexOf('https://www.googleapis.com/auth/analytics')===-1){
            this.display_unauthorized_message($analytics_components,'no_right');
        }else{
            this.make_analytics_calls($analytics_components);
        }
    },

    display_unauthorized_message:function($analytics_components,reason){
        $analytics_components.prepend($(QWeb.render('website.unauthorized_analytics',{reason:reason})));
    },

    make_analytics_calls:function($analytics_components){
        //2.ActiveUserscomponent
        var$analytics_users=$('<div>');
        varactiveUsers=newgapi.analytics.ext.ActiveUsers({
            container:$analytics_users[0],
            pollingInterval:10,
        });
        $analytics_users.appendTo($analytics_components);

        //3.ViewSelector
        var$analytics_view_selector=$('<div>').addClass('col-lg-12o_properties_selection');
        varviewSelector=newgapi.analytics.ViewSelector({
            container:$analytics_view_selector[0],
        });
        viewSelector.execute();
        $analytics_view_selector.appendTo($analytics_components);

        //4.Chartgraph
        varstart_date='7daysAgo';
        if(this.date_range==='month'){
            start_date='30daysAgo';
        }elseif(this.date_range==='year'){
            start_date='365daysAgo';
        }
        var$analytics_chart_2=$('<div>').addClass('col-lg-6col-12');
        varbreakdownChart=newgapi.analytics.googleCharts.DataChart({
            query:{
                'dimensions':'ga:date',
                'metrics':'ga:sessions',
                'start-date':start_date,
                'end-date':'yesterday'
            },
            chart:{
                type:'LINE',
                container:$analytics_chart_2[0],
                options:{
                    title:'All',
                    width:'100%',
                    tooltip:{isHtml:true},
                }
            }
        });
        $analytics_chart_2.appendTo($analytics_components);

        //5.Charttable
        var$analytics_chart_1=$('<div>').addClass('col-lg-6col-12');
        varmainChart=newgapi.analytics.googleCharts.DataChart({
            query:{
                'dimensions':'ga:medium',
                'metrics':'ga:sessions',
                'sort':'-ga:sessions',
                'max-results':'6'
            },
            chart:{
                type:'TABLE',
                container:$analytics_chart_1[0],
                options:{
                    width:'100%'
                }
            }
        });
        $analytics_chart_1.appendTo($analytics_components);

        //Eventshandling&animations

        vartable_row_listener;

        viewSelector.on('change',function(ids){
            varoptions={query:{ids:ids}};
            activeUsers.set({ids:ids}).execute();
            mainChart.set(options).execute();
            breakdownChart.set(options).execute();

            if(table_row_listener){google.visualization.events.removeListener(table_row_listener);}
        });

        mainChart.on('success',function(response){
            varchart=response.chart;
            vardataTable=response.dataTable;

            table_row_listener=google.visualization.events.addListener(chart,'select',function(){
                varoptions;
                if(chart.getSelection().length){
                    varrow= chart.getSelection()[0].row;
                    varmedium= dataTable.getValue(row,0);
                    options={
                        query:{
                            filters:'ga:medium=='+medium,
                        },
                        chart:{
                            options:{
                                title:medium,
                            }
                        }
                    };
                }else{
                    options={
                        chart:{
                            options:{
                                title:'All',
                            }
                        }
                    };
                    deletebreakdownChart.get().query.filters;
                }
                breakdownChart.set(options).execute();
            });
        });

        //AddCSSanimationtovisuallyshowthewhenuserscomeandgo.
        activeUsers.once('success',function(){
            varelement=this.container.firstChild;
            vartimeout;

            this.on('change',function(data){
                element=this.container.firstChild;
                varanimationClass=data.delta>0?'is-increasing':'is-decreasing';
                element.className+=(''+animationClass);

                clearTimeout(timeout);
                timeout=setTimeout(function(){
                    element.className=element.className.replace(/is-(increasing|decreasing)/g,'');
                },3000);
            });
        });
    },

    /*
     *Creditstohttps://github.com/googleanalytics/ga-dev-tools
     *ThisistheActiveUserscomponentthatpolls
     *thenumberofactiveusersonAnalyticseach5secs
     */
    analytics_create_components:function(){

        gapi.analytics.createComponent('ActiveUsers',{

            initialize:function(){
                this.activeUsers=0;
                gapi.analytics.auth.once('signOut',this.handleSignOut_.bind(this));
            },

            execute:function(){
                //Stopanypollingcurrentlygoingon.
                if(this.polling_){
                    this.stop();
                }

                this.render_();

                //Waituntiltheuserisauthorized.
                if(gapi.analytics.auth.isAuthorized()){
                    this.pollActiveUsers_();
                }else{
                    gapi.analytics.auth.once('signIn',this.pollActiveUsers_.bind(this));
                }
            },

            stop:function(){
                clearTimeout(this.timeout_);
                this.polling_=false;
                this.emit('stop',{activeUsers:this.activeUsers});
            },

            render_:function(){
                varopts=this.get();

                //Renderthecomponentinsidethecontainer.
                this.container=typeofopts.container==='string'?
                    document.getElementById(opts.container):opts.container;

                this.container.innerHTML=opts.template||this.template;
                this.container.querySelector('b').innerHTML=this.activeUsers;
            },

            pollActiveUsers_:function(){
                varoptions=this.get();
                varpollingInterval=(options.pollingInterval||5)*1000;

                if(isNaN(pollingInterval)||pollingInterval<5000){
                    thrownewError('Frequencymustbe5secondsormore.');
                }

                this.polling_=true;
                gapi.client.analytics.data.realtime
                    .get({ids:options.ids,metrics:'rt:activeUsers'})
                    .then(function(response){
                        varresult=response.result;
                        varnewValue=result.totalResults?+result.rows[0][0]:0;
                        varoldValue=this.activeUsers;

                        this.emit('success',{activeUsers:this.activeUsers});

                        if(newValue!==oldValue){
                            this.activeUsers=newValue;
                            this.onChange_(newValue-oldValue);
                        }

                        if(this.polling_){
                            this.timeout_=setTimeout(this.pollActiveUsers_.bind(this),pollingInterval);
                        }
                    }.bind(this));
            },

            onChange_:function(delta){
                varvalueContainer=this.container.querySelector('b');
                if(valueContainer){valueContainer.innerHTML=this.activeUsers;}

                this.emit('change',{activeUsers:this.activeUsers,delta:delta});
                if(delta>0){
                    this.emit('increase',{activeUsers:this.activeUsers,delta:delta});
                }else{
                    this.emit('decrease',{activeUsers:this.activeUsers,delta:delta});
                }
            },

            handleSignOut_:function(){
                this.stop();
                gapi.analytics.auth.once('signIn',this.handleSignIn_.bind(this));
            },

            handleSignIn_:function(){
                this.pollActiveUsers_();
                gapi.analytics.auth.once('signOut',this.handleSignOut_.bind(this));
            },

            template:
                '<divclass="ActiveUsers">'+
                    'ActiveUsers:<bclass="ActiveUsers-value"></b>'+
                '</div>'

        });
    },

    //Utilityfunctions
    addLoader:function(selector){
        varloader='<spanclass="fafa-3xfa-spinfa-spinnerfa-pulse"/>';
        selector.html("<divclass='o_loader'>"+loader+"</div>");
    },
    getValue:function(d){returnd[1];},
    format_number:function(value,type,digits,symbol){
        if(type==='currency'){
            returnthis.render_monetary_field(value,this.currency_id);
        }else{
            returnfield_utils.format[type](value||0,{digits:digits})+''+symbol;
        }
    },
    formatValue:function(value){
        varformatter=field_utils.format.float;
        varformatedValue=formatter(value,undefined,FORMAT_OPTIONS);
        returnformatedValue;
    },
    render_monetary_field:function(value,currency_id){
        varcurrency=session.get_currency(currency_id);
        varformatted_value=field_utils.format.float(value||0,{digits:currency&&currency.digits});
        if(currency){
            if(currency.position==="after"){
                formatted_value+=currency.symbol;
            }else{
                formatted_value=currency.symbol+formatted_value;
            }
        }
        returnformatted_value;
    },

});

core.action_registry.add('backend_dashboard',Dashboard);

returnDashboard;
});
