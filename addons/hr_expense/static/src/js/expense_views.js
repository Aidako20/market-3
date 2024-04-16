flectra.define('hr_expense.expenses.tree',function(require){
"usestrict";
    varDocumentUploadMixin=require('hr_expense.documents.upload.mixin');
    varKanbanController=require('web.KanbanController');
    varKanbanView=require('web.KanbanView');
    varPivotView=require('web.PivotView');
    varListController=require('web.ListController');
    varListView=require('web.ListView');
    varviewRegistry=require('web.view_registry');
    varcore=require('web.core');
    varListRenderer=require('web.ListRenderer');
    varKanbanRenderer=require('web.KanbanRenderer');
    varPivotRenderer=require('web.PivotRenderer');
    varsession=require('web.session');
    constconfig=require('web.config');

    varQWeb=core.qweb;

    varExpensesListController=ListController.extend(DocumentUploadMixin,{
        buttons_template:'ExpensesListView.buttons',
        events:_.extend({},ListController.prototype.events,{
            'click.o_button_upload_expense':'_onUpload',
            'change.o_expense_documents_upload.o_form_binary_form':'_onAddAttachment',
        }),
    });

    constExpenseQRCodeMixin={
        async_renderView(){
            constself=this;
            awaitthis._super(...arguments);
            constgoogle_url="https://play.google.com/store/apps/details?id=com.flectra.mobile";
            constapple_url="https://apps.apple.com/be/app/flectra/id1272543640";
            constaction_desktop={
                name:'DownloadourApp',
                type:'ir.actions.client',
                tag:'expense_qr_code_modal',
                params:{'url':"https://apps.apple.com/be/app/flectra/id1272543640"},
                target:'new',
            };
            this.$el.find('img.o_expense_apple_store').on('click',function(event){
                event.preventDefault();
                if(!config.device.isMobileDevice){
                    self.do_action(_.extend(action_desktop,{params:{'url':apple_url}}));
                }else{
                    self.do_action({type:'ir.actions.act_url',url:apple_url});
                }
            });
            this.$el.find('img.o_expense_google_store').on('click',function(event){
                event.preventDefault();
                if(!config.device.isMobileDevice){
                    self.do_action(_.extend(action_desktop,{params:{'url':google_url}}));
                }else{
                    self.do_action({type:'ir.actions.act_url',url:google_url});
                }
            });
        },
    };

    constExpenseDashboardMixin={
        _render:asyncfunction(){
            varself=this;
            awaitthis._super(...arguments);
            constresult=awaitthis._rpc({
                model:'hr.expense',
                method:'get_expense_dashboard',
                context:this.context,
            });

            self.$el.parent().find('.o_expense_container').remove();
            constelem=QWeb.render('hr_expense.dashboard_list_header',{
                expenses:result,
                render_monetary_field:self.render_monetary_field,
            });
            self.$el.before(elem);
        },
        render_monetary_field:function(value,currency_id){
            value=value.toFixed(2);
            varcurrency=session.get_currency(currency_id);
            if(currency){
                if(currency.position==="after"){
                    value+=currency.symbol;
                }else{
                    value=currency.symbol+value;
                }
            }
            returnvalue;
        }
    };

    //ExpenseListRenderer
    varExpenseListRenderer=ListRenderer.extend(ExpenseQRCodeMixin);

    //ExpenseListRendererwiththeHeader
    //Usedin"MyExpensestoReport","AllMyExpenses"&"MyReports"
    varExpenseListRendererHeader=ExpenseListRenderer.extend(ExpenseDashboardMixin);

    varExpensesListViewDashboardUpload=ListView.extend({
        config:_.extend({},ListView.prototype.config,{
            Renderer:ExpenseListRenderer,
            Controller:ExpensesListController,
        }),
    });

    //Usedin"MyExpensestoReport"&"AllMyExpenses"
    varExpensesListViewDashboardUploadHeader=ExpensesListViewDashboardUpload.extend({
        config:_.extend({},ExpensesListViewDashboardUpload.prototype.config,{
            Renderer:ExpenseListRendererHeader,
        }),
    });

    //Thedashboardviewoftheexpensemodule
    varExpensesListViewDashboard=ListView.extend({
        config:_.extend({},ListView.prototype.config,{
            Renderer:ExpenseListRenderer,
            Controller:ExpensesListController,
        }),
    });

    //Thedashboardviewoftheexpensemodulewithanheader
    //Usedin"MyExpenses"
    varExpensesListViewDashboardHeader=ExpensesListViewDashboard.extend({
        config:_.extend({},ExpensesListViewDashboard.prototype.config,{
            Renderer:ExpenseListRendererHeader,
        })
    });

    varExpensesKanbanController=KanbanController.extend(DocumentUploadMixin,{
        buttons_template:'ExpensesKanbanView.buttons',
        events:_.extend({},KanbanController.prototype.events,{
            'click.o_button_upload_expense':'_onUpload',
            'change.o_expense_documents_upload.o_form_binary_form':'_onAddAttachment',
        }),
    });

    varExpenseKanbanRenderer=KanbanRenderer.extend(ExpenseQRCodeMixin);

    varExpenseKanbanRendererHeader=ExpenseKanbanRenderer.extend(ExpenseDashboardMixin);

    //Thekanbanview
    varExpensesKanbanView=KanbanView.extend({
        config:_.extend({},KanbanView.prototype.config,{
            Controller:ExpensesKanbanController,
            Renderer:ExpenseKanbanRenderer,
        }),
    });

    //ThekanbanviewwiththeHeader
    //Usedin"MyExpensestoReport","AllMyExpenses"&"MyRepo
    varExpensesKanbanViewHeader=ExpensesKanbanView.extend({
        config:_.extend({},ExpensesKanbanView.prototype.config,{
            Renderer:ExpenseKanbanRendererHeader,
        })
    });

    viewRegistry.add('hr_expense_tree_dashboard_upload',ExpensesListViewDashboardUpload);
    //Treeviewwiththeheader.
    //Usedin"MyExpensestoReport"&"AllMyExpenses"
    viewRegistry.add('hr_expense_tree_dashboard_upload_header',ExpensesListViewDashboardUploadHeader);
    viewRegistry.add('hr_expense_tree_dashboard',ExpensesListViewDashboard);
    //Treeviewwiththeheader.
    //Usedin"MyReports"
    viewRegistry.add('hr_expense_tree_dashboard_header',ExpensesListViewDashboardHeader);
    viewRegistry.add('hr_expense_kanban',ExpensesKanbanView);
    //Kanbanviewwiththeheader.
    //Usedin"MyExpensestoReport","AllMyExpenses"&"MyReports"
    viewRegistry.add('hr_expense_kanban_header',ExpensesKanbanViewHeader);
});
