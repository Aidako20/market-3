flectra.define('web.SystrayMenu',function(require){
"usestrict";

vardom=require('web.dom');
varWidget=require('web.Widget');

/**
 *TheSystrayMenuistheclassthatmanagethelistoficonsinthetopright
 *ofthemenubar.
 */
varSystrayMenu=Widget.extend({
    /**
     *Thiswidgetrendersthesystraymenu.Itcreatesandrenderswidgets
     *pushedininstance.web.SystrayItems.
     */
    init:function(parent){
        this._super(parent);
        this.items=[];
        this.widgets=[];
    },
    /**
     *Instanciatetheitemsandaddthemintoatemporaryfragmenet
     *@override
     */
    willStart:function(){
        varself=this;
        varproms=[];
        SystrayMenu.Items=_.sortBy(SystrayMenu.Items,function(item){
            return!_.isUndefined(item.prototype.sequence)?item.prototype.sequence:50;
        });

        SystrayMenu.Items.forEach(function(WidgetClass){
            varcur_systray_item=newWidgetClass(self);
            self.widgets.push(cur_systray_item);
            proms.push(cur_systray_item.appendTo($('<div>')));
        });

        returnthis._super.apply(this,arguments).then(function(){
            returnPromise.all(proms);
        });
    },
    on_attach_callback(){
        this.widgets
            .filter(widget=>widget.on_attach_callback)
            .forEach(widget=>widget.on_attach_callback());
    },
    /**
     *Addtheinstanciateditems,usingtheobjectlocatedinthis.wisgets
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.widgets.forEach(function(widget){
                dom.prepend(self.$el,widget.$el);
            });
        });
    },
});

SystrayMenu.Items=[];

returnSystrayMenu;

});

