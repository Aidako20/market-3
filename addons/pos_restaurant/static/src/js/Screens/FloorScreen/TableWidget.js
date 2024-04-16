flectra.define('pos_restaurant.TableWidget',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classTableWidgetextendsPosComponent{
        mounted(){
            consttable=this.props.table;
            functionunit(val){
                return`${val}px`;
            }
            conststyle={
                width:unit(table.width),
                height:unit(table.height),
                'line-height':unit(table.height),
                top:unit(table.position_v),
                left:unit(table.position_h),
                'border-radius':table.shape==='round'?unit(1000):'3px',
            };
            if(table.color){
                style.background=table.color;
            }
            if(table.height>=150&&table.width>=150){
                style['font-size']='32px';
            }
            Object.assign(this.el.style,style);

            consttableCover=this.el.querySelector('.table-cover');
            Object.assign(tableCover.style,{height:`${Math.ceil(this.fill*100)}%`});
        }
        getfill(){
            constcustomerCount=this.env.pos.get_customer_count(this.props.table);
            returnMath.min(1,Math.max(0,customerCount/this.props.table.seats));
        }
        getorderCount(){
            consttable=this.props.table;
            returntable.order_count!==undefined
                ?table.order_count
                :this.env.pos
                      .get_table_orders(table)
                      .filter(o=>o.orderlines.length!==0||o.paymentlines.length!==0).length;
        }
        getorderCountClass(){
            constnotifications=this._getNotifications();
            return{
                'order-count':true,
                'notify-printing':notifications.printing,
                'notify-skipped':notifications.skipped,
            };
        }
        _getNotifications(){
            constorders=this.env.pos.get_table_orders(this.props.table);

            lethasChangesCount=0;
            lethasSkippedCount=0;
            for(leti=0;i<orders.length;i++){
                if(orders[i].hasChangesToPrint()){
                    hasChangesCount++;
                }elseif(orders[i].hasSkippedChanges()){
                    hasSkippedCount++;
                }
            }

            returnhasChangesCount?{printing:true}:hasSkippedCount?{skipped:true}:{};
        }
    }
    TableWidget.template='TableWidget';

    Registries.Component.add(TableWidget);

    returnTableWidget;
});
