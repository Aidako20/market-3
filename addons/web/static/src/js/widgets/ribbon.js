flectra.define('web.ribbon',function(require){
    'usestrict';

    /**
     *Thiswidgetaddsaribbononthetoprightsideoftheform
     *
     *     -Youcanspecifythetextwiththetitleattribute.
     *     -Youcanspecifythetooltipwiththetooltipattribute.
     *     -Youcanspecifyabackgroundcolorfortheribbonwiththebg_colorattribute
     *       usingbootstrapclasses:
     *       (bg-primary,bg-secondary,bg-success,bg-danger,bg-warning,bg-info,
     *       bg-light,bg-dark,bg-white)
     *
     *       Ifyoudon'tspecifythebg_colorattributethebg-successclasswillbeused
     *       bydefault.
     */

    varwidgetRegistry=require('web.widget_registry');
    varWidget=require('web.Widget');

    varRibbonWidget=Widget.extend({
        template:'web.ribbon',
        xmlDependencies:['/web/static/src/xml/ribbon.xml'],

        /**
         *@param{Object}options
         *@param{string}options.attrs.title
         *@param{string}options.attrs.textsameastitle
         *@param{string}options.attrs.tooltip
         *@param{string}options.attrs.bg_color
         */
        init:function(parent,data,options){
            this._super.apply(this,arguments);
            this.text=options.attrs.title||options.attrs.text;
            this.tooltip=options.attrs.tooltip;
            this.className=options.attrs.bg_color?options.attrs.bg_color:'bg-success';
            if(this.text.length>15){
                this.className+='o_small';
            }elseif(this.text.length>10){
                this.className+='o_medium';
            }
        },
    });

    widgetRegistry.add('web_ribbon',RibbonWidget);

    returnRibbonWidget;
});
